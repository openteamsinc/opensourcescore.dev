import pandas as pd

from .score_type import Score

from ..notes import Note

LESS_PERMISSIVE_LICENSES = ["GPL", "AGPL", "LGPL", "Artistic", "CDDL", "MPL"]


def score_license(git_info: dict, score: Score):
    license = git_info.get("license", {})
    license_kind = license.get("kind")
    modified = license.get("modified")

    if license.get("error"):
        # score.limit(MODERATE_RISK)
        note = license.get("error", Note.NO_LICENSE_INFO)
        # score.notes.append(note)
        score.add_note(note)

    elif not license_kind or license_kind == "Unknown":
        score.add_note(Note.NO_OS_LICENSE)

    if license_kind in LESS_PERMISSIVE_LICENSES:
        score.add_note(Note.LESS_PERMISSIVE_LICENSE)
        # score.limit(CAUTION_NEEDED)
        # score.notes.append(Note.LESS_PERMISSIVE_LICENSE.value)

    if modified:
        score.add_note(Note.LICENSE_MODIFIED)
        # score.limit(CAUTION_NEEDED)
        # score.notes.append(Note.LICENSE_MODIFIED.value)


def build_legal_score(git_info: dict) -> Score:
    score = Score()

    if git_info.get("error") and not pd.isna(git_info["error"]):
        score.add_note(git_info["error"])
        return score

    score_license(git_info, score)

    return score
