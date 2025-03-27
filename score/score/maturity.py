import pandas as pd
from ..notes import Note

one_year_ago = pd.Timestamp.now() - pd.DateOffset(years=1)


def build_maturity_score(source_url: str, git_info: dict):

    if git_info.get("error") and not pd.isna(git_info["error"]):
        note = git_info["error"]
        yield note.name
        return

    if not git_info.get("first_commit") or pd.isnull(git_info["first_commit"]):
        yield Note.NO_COMMITS
        return

    if git_info["latest_commit"] < one_year_ago:
        yield Note.LAST_COMMIT_OVER_A_YEAR
        return

    if git_info["first_commit"] > one_year_ago:
        yield Note.FIRST_COMMIT_THIS_YEAR

    return
