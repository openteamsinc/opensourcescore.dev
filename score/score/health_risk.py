import pandas as pd
from typing import List
from dataclasses import dataclass, field

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
    notes: List[str] = field(default_factory=list)

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
        score.notes.append(
            f"Only {mma_count:.0f} author{'s have' if mma_count > 1 else ' has'} "
            "contributed to this repository in a single month"
        )

    if recent_count < 1:
        score.limit(CAUTION_NEEDED)
        score.notes.append("No one has contributed to this repository in the last year")
    elif recent_count < 2:
        score.limit(CAUTION_NEEDED)
        score.notes.append(
            "Only one author has contributed to this repository in the last year"
        )

    if latest_commit < FIVE_YEARS_AGO:
        score.limit(HIGH_RISK)
        score.notes.append("The last commit to source control was over 5 years ago")


def score_license(git_info, score: Score):
    license_kind = git_info.license.get("kind")
    modified = git_info.license.get("modified")

    if git_info.license.get("error"):
        score.limit(MODERATE_RISK)
        note = git_info.license.get("error", "Could not retrieve licence information")
        score.notes.append(note)

    elif not license_kind or license_kind == "Unknown":
        score.limit(MODERATE_RISK)
        note = git_info.license.get("error", "Could not detect open source license")
        score.notes.append(note)

    if license_kind in LESS_PERMISSIVE_LICENSES:
        score.limit(CAUTION_NEEDED)
        score.notes.append(
            "License may have usage restrictions. Review terms before implementation"
        )

    if modified:
        score.limit(CAUTION_NEEDED)
        score.notes.append("License may have been modified from the original")


def score_python(git_info, score: Score):

    packages = git_info.pypi_packages
    expected_name = git_info.py_package

    if len(packages) == 0:
        return

    if not expected_name:
        score.limit(CAUTION_NEEDED)
        score.notes.append(
            "Could not determine the Python package name from pyproject.toml in the source code"
        )

    have_package_names = [p["name"].lower() for p in packages]
    if expected_name.lower() not in have_package_names:
        score.limit(CAUTION_NEEDED)
        score.notes.append(
            f"The Python package '{expected_name}' from pyproject.toml is not listed on PyPI"
        )

    return


def build_health_risk_score(git_info) -> Score:
    score = Score()

    if git_info.error:
        score.value = "Unknown"
        score.notes.append(git_info.error)
        return score

    if git_info.first_commit == "NaT":
        score.value = "Placeholder"
        score.notes.append("There are no human commits in this repository")
        return score

    score_license(git_info, score)
    score_contributors(git_info, score)
    score_python(git_info, score)

    return score
