import pandas as pd
from typing import Union
from pathlib import Path
from functools import lru_cache
from strsimpy import SorensenDice
from difflib import unified_diff

KIND_MAP = {
    "AAL": "AAL",
    "AFL-3.0": "AFL",
    "AGPL-3.0": "AGPL",
    "APL-1.0": "APL",
    "APSL-2.0": "APSL",
    "Apache-1.1": "Apache",
    "Apache-2.0": "Apache",
    "Artistic-1.0": "Artistic",
    "Artistic-2.0": "Artistic",
    "0BSD": "BSD",
    "BSD-1-Clause": "BSD",
    "BSD-2": "BSD",
    "BSD-3": "BSD",
    "BSD-3-Clause-LBNL": "BSD",
    "BSDplusPatent": "BSD",
    "BSL-1.0": "BSL",
    "CAL-1.0": "CAL",
    "CATOSL-1.1": "CATOSL",
    "CDDL-1.0": "CDDL",
    "CECILL-2.1": "CECILL",
    "CNRI-Python": "CNRI-Python",
    "CPAL-1.0": "CPAL",
    "CPL-1.0": "CPL",
    "CUA-OPL-1.0": "CUA-OPL",
    "CVW": "CVW",
    "ECL-1.0": "ECL",
    "ECL-2.0": "ECL",
    "EFL-1.0": "EFL",
    "EFL-2.0": "EFL",
    "EPL-1.0": "EPL",
    "EPL-2.0": "EPL",
    "EUDatagrid": "EUDatagrid",
    "EUPL-1.1": "EUPL",
    "EUPL-1.2": "EUPL",
    "Entessa": "Entessa",
    "Fair": "Fair",
    "Frameworx-1.0": "Frameworx",
    "GFDL-1.2": "GFDL",
    "GFDL-1.3": "GFDL",
    "GPL-1.0": "GPL",
    "GPL-2.0": "GPL",
    "GPL-3.0": "GPL",
    "HPND": "HPND",
    "IPA": "IPA",
    "IPL-1.0": "IPL",
    "ISC": "ISC",
    "Intel": "Intel",
    "LGPL-2.0": "LGPL",
    "LGPL-2.1": "LGPL",
    "LGPL-3.0": "LGPL",
    "LPL-1.0": "LPL",
    "LPL-1.02": "LPL",
    "LPPL-1.3c": "LPPL",
    "LiLiQ-P-1.1": "LiLi",
    "LiLiQ-R+": "LiLi",
    "LiLiQ-R-1.1": "LiLi",
    "MIT": "MIT",
    "MIT-0": "MIT",
    "MPL-1.0": "MPL",
    "MPL-1.1": "MPL",
    "MPL-2.0": "MPL",
    "MS-PL": "MS-PL",
    "MS-RL": "MS-RL",
    "MirOS": "MirOS",
    "Motosoto": "Motosoto",
    "Multics": "Multics",
    "NASA-1.3": "NASA",
    "NCSA": "NCSA",
    "NGPL": "NGPL",
    "NPOSL-3.0": "NPOSL",
    "NTP": "NTP",
    "Naumen": "Naumen",
    "Nokia": "Nokia",
    "OCLC-2.0": "OCLC",
    "OFL-1.1": "OFL",
    "OGTSL": "OGTSL",
    "OLDAP-2.8": "OLDAP",
    "OPL-2.1": "OPL",
    "OSL-1.0": "OSL",
    "OSL-2.1": "OSL",
    "OSL-3.0": "OSL",
    "PHP-3.0": "PHP",
    "PHP-3.01": "PHP",
    "PostgreSQL": "PostgreSQL",
    "Python-2.0": "Python",
    "QPL-1.0": "QPL",
    "RPL-1.1": "RPL",
    "RPL-1.5": "RPL",
    "RPSL-1.0": "RPSL",
    "RSCPL": "RSCPL",
    "SISSL": "SISSL",
    "SPL-1.0": "SPL",
    "Simple-2.0": "Simple",
    "Sleepycat": "Sleepycat",
    "UPL": "UPL",
    "VSL-1.0": "VSL",
    "W3C": "W3C",
    "WXwindows": "WXwindows",
    "Watcom-1.0": "Watcom",
    "Xnet": "Xnet",
    "ZPL-2.0": "ZPL",
    "Zlib": "Zlib",
    "jabberpl": "jabberpl",
}

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
        # print("----")
        # print(license_content)
        # print("----")
        print("best_match", best_match)
        # print(all_licenses[best_match])
        print("----")
        diff = "".join(
            unified_diff(
                license_content.splitlines(),
                all_licenses[best_match].splitlines(),
                fromfile="Project Licence",
                tofile="Open Source License",
            )
        )
        print("diff")
        print(diff)
        print("diff")

    return {
        "license": best_match,
        "kind": kind,
        "similarity": similarity,
        "modified": modified,
        "diff": diff,
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
