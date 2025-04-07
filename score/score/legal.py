import pandas as pd
from ..notes import Note

LICENSE_LESS_PERMISSIVES = ["GPL", "AGPL", "LGPL", "Artistic", "CDDL", "MPL"]


def score_license(git_info: dict):
    license = git_info.get("license", {})
    license_kind = license.get("kind")
    modified = license.get("modified")
    if git_info.get("error") and not pd.isna(git_info["error"]):
        note = git_info["error"]
        yield note
        return

    if license.get("error") and not pd.isna(license["error"]):
        note = license["error"]
        yield note
        return

    if not license_kind or license_kind == "Unknown":
        yield Note.LICENSE_NOT_OSS

    if license_kind in LICENSE_LESS_PERMISSIVES:
        yield Note.LICENSE_LESS_PERMISSIVE

    if modified:
        yield Note.LICENSE_MODIFIED


def build_legal_score(git_info: dict):

    if git_info.get("error") and not pd.isna(git_info["error"]):
        yield git_info["error"]

    yield from score_license(git_info)

    return
