import pandas as pd

import re
from typing import Union
from pathlib import Path
from functools import lru_cache
from strsimpy import SorensenDice
from difflib import unified_diff
from score.utils.license_name_to_kind import KIND_MAP
from score.utils.normalize_license_content import normalize_license_content
from hashlib import md5

CLOSE_ENOUGH = 0.95
PROBABLY_NOT = 0.9


def normalize(content: str):
    content = "\n".join(
        [line for line in content.splitlines() if not copyright_line(line)]
    )

    # Normalize bullet points (replace *, -, 1., 2., etc. with a standard marker)
    content = re.sub(
        r"^\s*(\d+[\.\):]|\([a-z0-9]+\)|[ivxIVX]+[\.\)])\s+",
        " * ",
        content,
        flags=re.MULTILINE,
    )

    content = re.sub(r"[\s]+", " ", content)

    return content.lower().strip()


def identify_license(license_content: str) -> dict:

    normalized_license_content = normalize(license_content)
    print(repr(normalized_license_content))
    all_licenses = get_all_licenses()
    sd = SorensenDice()
    similarities = []
    for license_name, ref_license in all_licenses.items():
        similarities.append(
            {
                "name": license_name,
                "similarity": sd.similarity(
                    normalized_license_content,
                    normalize(ref_license),
                ),
            }
        )
    similarities = pd.DataFrame(similarities).set_index("name")
    best_match = similarities.idxmax().item()
    similarity = similarities.loc[best_match, "similarity"]
    if similarity < PROBABLY_NOT:  # type: ignore
        return {
            "license": "Unknown",
            "kind": "Unknown",
            "similarity": similarity,
            "best_match": best_match,
            "modified": False,
        }

    kind = KIND_MAP.get(best_match, best_match)

    modified = similarity < CLOSE_ENOUGH  # type: ignore
    print(repr(normalize(all_licenses[best_match])))
    diff = None
    if modified:
        diff = "\n".join(
            unified_diff(
                license_content.splitlines(),
                all_licenses[best_match].splitlines(),
                fromfile="Project Licence",
                tofile="Open Source License",
            )
        )

    md5hash = md5(
        normalize_license_content(license_content).encode("utf-8")
    ).hexdigest()

    return {
        "license": best_match,
        "kind": kind,
        "similarity": similarity,
        "modified": modified,
        "diff": diff,
        "md5": md5hash,
    }


license_dir = Path(__file__).parent / "licenses"


def copyright_line(line: Union[bytes | str]):

    if isinstance(line, bytes):
        line = line.decode("utf-8", errors="ignore")

    # Pattern matches:
    # - Optional leading characters like '-', '*', '•' and whitespace
    # - "copyright" (case insensitive)
    # - Optional "(c)" or "©" symbol
    pattern = r"(?i)^[-\s*•]*copyright(\s+\([cC]\)|\s+©)?"

    return bool(re.search(pattern, line.strip()))


@lru_cache
def get_all_licenses():
    licenses = {}
    for license_file in license_dir.glob("*"):
        with open(license_file, "rb") as f:
            lines = f.readlines()
            lines = [line for line in lines if not copyright_line(line)]
            data = b"".join(lines)

        data = data.decode(errors="ignore")
        licenses[license_file.name] = data.strip()
    return licenses
