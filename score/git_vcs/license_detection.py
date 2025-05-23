import pandas as pd

import re
from typing import Union
from pathlib import Path
from functools import lru_cache
from strsimpy import SorensenDice
from difflib import unified_diff
from score.models import License
from score.utils.license_name_to_kind import KIND_MAP
from score.utils.normalize_license_content import normalize_license_content
from hashlib import md5

CLOSE_ENOUGH = 0.95
PROBABLY_NOT = 0.9


def normalize(content: str) -> str:
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


def identify_license(source_url: str, license_content: str) -> License:

    normalized_license_content = normalize(license_content)
    all_licenses = get_all_licenses()
    sd = SorensenDice()
    similarities_lst = []
    for license_name, ref_license in all_licenses.items():
        similarities_lst.append(
            {
                "name": license_name,
                "similarity": sd.similarity(
                    normalized_license_content,
                    normalize(ref_license),
                ),
            }
        )
    similarities = pd.DataFrame(similarities_lst).set_index("name")
    best_match = similarities.idxmax().item()
    similarity: float = similarities.loc[best_match, "similarity"].item()  # type: ignore
    if similarity < PROBABLY_NOT:
        return License(
            license="Unknown",
            kind="Unknown",
            similarity=similarity,
            best_match=best_match,
            modified=False,
        )

    kind = KIND_MAP.get(best_match, best_match)

    modified = bool(similarity < CLOSE_ENOUGH)
    diff = None
    if modified:
        diff = "\n".join(
            unified_diff(
                all_licenses[best_match].splitlines(),
                license_content.splitlines(),
                fromfile=f"https://opensource.org/license/{best_match}",
                tofile=f"{source_url}",
            )
        )

    md5hash = md5(
        normalize_license_content(license_content).encode("utf-8")
    ).hexdigest()

    return License(
        license=best_match,
        kind=kind,
        similarity=similarity,
        modified=modified,
        diff=diff,
        md5=md5hash,
    )


license_dir = Path(__file__).parent / "licenses"


def copyright_line(line: Union[bytes, str]):

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
