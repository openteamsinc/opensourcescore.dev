import pandas as pd
from ..notes import Note

one_year_ago = pd.Timestamp.now() - pd.DateOffset(years=1)


def build_maturity_score(source_url, git_info):
    score = {"value": "Mature", "notes": []}

    if git_info.error and not pd.isna(git_info.error):
        score["value"] = "Unknown"
        score["notes"].append(git_info.error)
        return score

    if git_info.first_commit == "NaT":
        score["value"] = "Placeholder"
        score["notes"].append(Note.NO_COMMITS.value)
        return score

    if git_info.latest_commit < one_year_ago:
        score["value"] = "Legacy"
        score["notes"].append(Note.LAST_COMMIT_OVER_A_YEAR.value)

    if git_info.first_commit > one_year_ago:
        score["value"] = "Experimental"
        score["notes"].append(Note.FIRST_COMMIT_THIS_YEAR.value)

    return score
