import pandas as pd
from ..notes import Note

one_year_ago = pd.Timestamp.now() - pd.DateOffset(years=1)


def build_maturity_score(source_url: str, git_info: dict):
    score = {"value": "Mature", "notes": []}

    # if git_info is None:
    #     score["value"] = "Unknown"
    #     score["notes"].append(git_info["error"])
    #     return score

    if git_info.get("error") and not pd.isna(git_info["error"]):
        note = git_info["error"]
        score["value"] = note.category
        score["notes"].append(note.name)
        return score

    if not git_info.get("first_commit") or pd.isnull(git_info["first_commit"]):
        note = Note.NO_COMMITS
        score["value"] = note.category
        score["notes"].append(note.name)

        return score

    if git_info["latest_commit"] < one_year_ago:
        note = Note.LAST_COMMIT_OVER_A_YEAR
        score["value"] = note.category
        score["notes"].append(note.name)

    if git_info["first_commit"] > one_year_ago:
        note = Note.FIRST_COMMIT_THIS_YEAR
        score["value"] = note.category
        score["notes"].append(note.name)

    return score
