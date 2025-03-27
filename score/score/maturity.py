import pandas as pd
from ..notes import Note

ONE_YEAR_AGO = pd.Timestamp.now() - pd.DateOffset(years=1)
FIVE_YEARS_AGO = pd.Timestamp.now() - pd.DateOffset(years=5)


def build_maturity_score(source_url: str, git_info: dict):

    if git_info.get("error") and not pd.isna(git_info["error"]):
        note = git_info["error"]
        yield note
        return

    if not git_info.get("first_commit") or pd.isnull(git_info["first_commit"]):
        yield Note.NO_COMMITS
        return

    latest_commit = git_info["latest_commit"]
    first_commit = git_info["first_commit"]

    if latest_commit < ONE_YEAR_AGO:
        if latest_commit < FIVE_YEARS_AGO:
            yield Note.LAST_COMMIT_OVER_5_YEARS
            return

        yield Note.LAST_COMMIT_OVER_A_YEAR
        return

    if first_commit > ONE_YEAR_AGO:
        yield Note.FIRST_COMMIT_THIS_YEAR

    return
