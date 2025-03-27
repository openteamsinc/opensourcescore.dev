import pandas as pd

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


def remove_copyright_lines(content: str):
    return "".join([line for line in content.splitlines() if not copyright_line(line)])


def identify_license(license_content: str) -> dict:

    license_content_without_copyright = remove_copyright_lines(license_content)

    all_licenses = get_all_licenses()
    sd = SorensenDice()
    similarities = []
    for license_name, ref_license in all_licenses.items():
        similarities.append(
            {
                "name": license_name,
                "similarity": sd.similarity(
                    license_content_without_copyright.strip(),
                    remove_copyright_lines(ref_license).strip(),
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
    copyright = b"copyright" if isinstance(line, bytes) else "copyright"
    if line.strip().lower().startswith(copyright):
        return True
    return False


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
