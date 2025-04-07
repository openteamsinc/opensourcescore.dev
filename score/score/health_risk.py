import pandas as pd
import logging

from score.models import Source
from score.notes import Note, FEW_MAX_MONTHLY_AUTHORS_CONST


log = logging.getLogger(__name__)


ONE_YEAR_AGO = pd.Timestamp.now() - pd.DateOffset(years=1)
THREE_YEARS_AGO = pd.Timestamp.now() - pd.DateOffset(years=3)
FIVE_YEARS_AGO = pd.Timestamp.now() - pd.DateOffset(years=5)

LICENSE_LESS_PERMISSIVES = ["GPL", "AGPL", "LGPL", "Artistic", "CDDL", "MPL"]


def score_contributors(git_info: Source):
    mma_count = git_info.max_monthly_authors_count
    recent_count = git_info.recent_authors_count

    if mma_count is not None and mma_count < FEW_MAX_MONTHLY_AUTHORS_CONST:
        yield Note.FEW_MAX_MONTHLY_AUTHORS

    if recent_count is not None and recent_count < 2:
        yield Note.ONE_AUTHOR_THIS_YEAR


def build_health_risk_score(git_info: Source):

    if git_info.error:
        yield git_info.error
        return

    if not git_info.first_commit:
        yield Note.NO_COMMITS
        return

    yield from score_contributors(git_info)

    return
