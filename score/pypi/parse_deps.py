import logging
import re
from typing import List, Optional

from score.models import Dependency

log = logging.getLogger(__name__)


def parse_dep(dep_string: str) -> Dependency:
    # Split on semicolon to separate main requirement from conditions
    parts = dep_string.split(";", 1)
    main_part = parts[0].strip()
    include_check = parts[1].strip() if len(parts) > 1 else None

    # Parse name and version specifiers
    # Match name - must start with letter/underscore
    match = re.match(r"^([a-zA-Z_][a-zA-Z0-9._-]*)", main_part)
    if not match:
        raise ValueError(f"Invalid dependency string: {dep_string}")

    name = match.group(1)
    spec_part = main_part[len(name) :].strip()

    # Extract version specifiers
    specifiers = []
    if spec_part:
        # Find all version specifiers (>=, ==, !=, <, >, ~=, etc.)
        spec_matches = re.findall(r"[><=!~]+[^,;\s]+", spec_part)
        specifiers = [spec.strip() for spec in spec_matches]

    return Dependency(name=name, specifiers=specifiers, include_check=include_check)


def parse_deps(requires_dist: Optional[List[str]]) -> List[Dependency]:
    if not requires_dist:
        return []

    result = []
    for line in requires_dist:
        try:
            dep = parse_dep(line)
            result.append(dep)
        except ValueError as err:
            log.warning(f"Failed to parse dependency '{line}': {err}")
            continue

    return result
