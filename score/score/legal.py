import pandas as pd
from ..notes import Note

LESS_PERMISSIVE_LICENSES = ["GPL", "AGPL", "LGPL", "Artistic", "CDDL", "MPL"]


def score_license(git_info: dict):
    license = git_info.get("license", {})
    license_kind = license.get("kind")
    modified = license.get("modified")

    if git_info.get("error") and not pd.isna(git_info["error"]):
        note = license[Note.NO_LICENSE_INFO]
        yield note

    elif not license_kind or license_kind == "Unknown":
        yield Note.NO_OS_LICENSE

    if license_kind in LESS_PERMISSIVE_LICENSES:
        yield Note.LESS_PERMISSIVE_LICENSE

    if modified:
        yield Note.LICENSE_MODIFIED


def build_legal_score(git_info: dict):

    if git_info.get("error") and not pd.isna(git_info["error"]):
        yield git_info["error"]

    yield from score_license(git_info)

    return
