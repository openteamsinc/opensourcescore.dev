import pandas as pd
import logging

from ..notes import Note, FEW_MAX_MONTHLY_AUTHORS_CONST
from .score_type import Score

log = logging.getLogger(__name__)


ONE_YEAR_AGO = pd.Timestamp.now() - pd.DateOffset(years=1)
THREE_YEARS_AGO = pd.Timestamp.now() - pd.DateOffset(years=3)
FIVE_YEARS_AGO = pd.Timestamp.now() - pd.DateOffset(years=5)

LICENSE_LESS_PERMISSIVES = ["GPL", "AGPL", "LGPL", "Artistic", "CDDL", "MPL"]


def score_contributors(git_info: dict):
    mma_count = git_info["max_monthly_authors_count"]
    recent_count = git_info["recent_authors_count"]

    if mma_count < FEW_MAX_MONTHLY_AUTHORS_CONST:
        yield Note.FEW_MAX_MONTHLY_AUTHORS

    if recent_count < 2:
        yield Note.ONE_AUTHOR_THIS_YEAR


def score_python(git_info: dict, score: Score):

    packages = git_info.pypi_packages
    expected_name = git_info.py_package

    if len(packages) == 0:
        return

    if not expected_name:
        score.add_note(Note.NO_PROJECT_NAME)
        return

    have_package_names = [p["name"] for p in packages]

    if expected_name not in have_package_names:
        score.add_note(Note.PROJECT_NOT_PUBLISHED)

    return


def build_health_risk_score(git_info: dict):

    if git_info.get("error") and not pd.isna(git_info["error"]):

        yield git_info["error"]
        return

    if not git_info.get("first_commit") or pd.isnull(git_info["first_commit"]):
        yield Note.NO_COMMITS
        return

    yield from score_contributors(git_info)

    return
