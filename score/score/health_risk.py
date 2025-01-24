import pandas as pd
import logging

from ..notes import Note
from .score_type import Score

log = logging.getLogger(__name__)

HEALTHY = "Healthy"
CAUTION_NEEDED = "Caution Needed"
MODERATE_RISK = "Moderate Risk"
HIGH_RISK = "High Risk"
SCORE_ORDER = [HEALTHY, CAUTION_NEEDED, MODERATE_RISK, HIGH_RISK]


ONE_YEAR_AGO = pd.Timestamp.now() - pd.DateOffset(years=1)
THREE_YEARS_AGO = pd.Timestamp.now() - pd.DateOffset(years=3)
FIVE_YEARS_AGO = pd.Timestamp.now() - pd.DateOffset(years=5)

LESS_PERMISSIVE_LICENSES = ["GPL", "AGPL", "LGPL", "Artistic", "CDDL", "MPL"]


def score_contributors(git_info: dict, score: Score):
    mma_count = git_info["max_monthly_authors_count"]
    recent_count = git_info["recent_authors_count"]
    latest_commit = git_info["latest_commit"]

    if mma_count < 3:
        score.add_note(Note.FEW_MAX_MONTHLY_AUTHORS)

    if recent_count < 1:
        score.add_note(Note.NO_AUTHORS_THIS_YEAR)
    elif recent_count < 2:
        score.add_note(Note.ONE_AUTHORS_THIS_YEAR)

    if latest_commit < FIVE_YEARS_AGO:
        score.add_note(Note.LAST_COMMIT_5_YEARS)


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


def build_health_risk_score(git_info: dict) -> Score:
    score = Score()

    if git_info.get("error") and not pd.isna(git_info["error"]):

        score.add_note(git_info["error"])
        return score

    if not git_info.get("first_commit") or pd.isnull(git_info["first_commit"]):
        score.add_note(Note.NO_COMMITS)
        return score

    score_contributors(git_info, score)
    # score_python(git_info, score)

    return score
