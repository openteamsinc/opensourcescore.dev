from datetime import datetime, timedelta
from typing import Iterator

from score.models import Source
from score.notes import Note

ONE_YEAR_AGO = datetime.now() - timedelta(days=365)
FIVE_YEARS_AGO = datetime.now() - timedelta(days=365 * 5)


def build_maturity_score(source_url: str, git_info: Source) -> Iterator[str]:

    if git_info.error:
        yield git_info.error
        return

    if not git_info.first_commit:
        yield Note.NO_COMMITS
        return
    if not git_info.latest_commit:
        yield Note.NO_COMMITS
        return

    if git_info.latest_commit < ONE_YEAR_AGO:
        if git_info.latest_commit < FIVE_YEARS_AGO:
            yield Note.LAST_COMMIT_OVER_5_YEARS
            return

        yield Note.LAST_COMMIT_OVER_A_YEAR
        return

    if git_info.first_commit > ONE_YEAR_AGO:
        yield Note.FIRST_COMMIT_THIS_YEAR

    return
