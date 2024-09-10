import pandas as pd
from typing import List
from dataclasses import dataclass, field
import logging

from ..notes import Note

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


@dataclass
class Score:
    value: str = HEALTHY
    notes: List[int] = field(default_factory=list)

    def limit(self, new_score: str):
        current_numeric_score = SCORE_ORDER.index(self.value)
        new_numeric_score = SCORE_ORDER.index(new_score)
        self.value = SCORE_ORDER[max(current_numeric_score, new_numeric_score)]

    def dict(self):
        return {"value": self.value, "notes": self.notes}


def score_contributors(git_info, score: Score):
    mma_count = git_info["max_monthly_authors_count"]
    recent_count = git_info["recent_authors_count"]
    latest_commit = git_info.latest_commit

    if mma_count < 3:
        score.limit(CAUTION_NEEDED)
        score.notes.append(Note.FEW_MAX_MONTHLY_AUTHORS.value)

    if recent_count < 1:
        score.limit(CAUTION_NEEDED)
        score.notes.append(Note.NO_AUTHORS_THIS_YEAR.value)
    elif recent_count < 2:
        score.limit(CAUTION_NEEDED)
        score.notes.append(Note.ONE_AUTHORS_THIS_YEAR.value)

    if latest_commit < FIVE_YEARS_AGO:
        score.limit(HIGH_RISK)
        score.notes.append(Note.LAST_COMMIT_5_YEARS.value)


def score_license(git_info, score: Score):
    license_kind = git_info.license.get("kind")
    modified = git_info.license.get("modified")

    if git_info.license.get("error"):
        score.limit(MODERATE_RISK)
        note = git_info.license.get("error", Note.NO_LICENSE_INFO.value)
        score.notes.append(note)

    elif not license_kind or license_kind == "Unknown":
        score.limit(MODERATE_RISK)
        note = git_info.license.get("error", Note.NO_OS_LICENSE.value)
        score.notes.append(note)

    if license_kind in LESS_PERMISSIVE_LICENSES:
        score.limit(CAUTION_NEEDED)
        score.notes.append(Note.LESS_PERMISSIVE_LICENSE.value)

    if modified:
        score.limit(CAUTION_NEEDED)
        score.notes.append(Note.LICENSE_MODIFIED.value)


def score_python(git_info, score: Score):

    packages = git_info.pypi_packages
    expected_name = git_info.py_package

    if len(packages) == 0:
        return

    if not expected_name:
        score.limit(CAUTION_NEEDED)
        score.notes.append(Note.NO_PROJECT_NAME.value)
        return

    have_package_names = [p["name"] for p in packages]

    if expected_name not in have_package_names:
        score.limit(CAUTION_NEEDED)
        score.notes.append(Note.PROJECT_NOT_PUBLISHED.value)

    return


def build_health_risk_score(git_info) -> Score:
    score = Score()

    if git_info.error and not pd.isna(git_info.error):
        score.value = "Unknown"
        score.notes.append(git_info.error)
        return score

    if (
        git_info.first_commit == "NaT"
        or pd.isna(git_info.first_commit)
        or not git_info.first_commit
    ):
        score.value = "Placeholder"
        score.notes.append(Note.NO_COMMITS.value)
        return score

    score_license(git_info, score)
    score_contributors(git_info, score)
    score_python(git_info, score)

    return score
