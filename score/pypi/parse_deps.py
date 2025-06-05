import logging
import re
from typing import List, Optional

from score.models import Dependency

log = logging.getLogger(__name__)


def parse_dep(dep_string: str) -> Dependency:
    # Split on semicolon to separate main requirement from conditions
    parts = dep_string.split(";", 1)
    main_part = parts[0].strip()
    environment_marker = parts[1].strip() if len(parts) > 1 else None

    # Parse name and extras
    # Match name followed by optional extras in brackets
    match = re.match(r"^([a-zA-Z_][a-zA-Z0-9._-]*)\s*(?:\[([^\]]+)\])?\s*(.*)", main_part)
    if not match:
        raise ValueError(f"Invalid dependency string: {dep_string}")

    name = match.group(1)
    extras_str = match.group(2)
    spec_part = match.group(3).strip()

    # Parse extras
    extras: List[str] = []
    if extras_str:
        extras = [extra.strip() for extra in extras_str.split(",") if extra.strip()]

    # Handle URL specifications (@ http://...)
    if spec_part.startswith("@"):
        # For URL dependencies, we don't parse version specifiers
        specifiers = []
    else:
        # Extract version specifiers
        specifiers = []
        if spec_part:
            # Find all version specifiers (>=, ==, !=, <, >, ~=, etc.)
            spec_matches = re.findall(r"[><=!~]+[^,;\s]+", spec_part)
            specifiers = [spec.strip() for spec in spec_matches]

    # Extract extra_marker from environment_marker if present
    extra_marker = None
    if environment_marker:
        # Look for patterns like: extra == "value" or extra == 'value'
        extra_match = re.search(r'extra\s*==\s*["\']([^"\']+)["\']', environment_marker)
        if extra_match:
            extra_marker = extra_match.group(1)

    return Dependency(
        name=name,
        specifiers=specifiers,
        extras=extras,
        environment_marker=environment_marker,
        extra_marker=extra_marker,
    )


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
