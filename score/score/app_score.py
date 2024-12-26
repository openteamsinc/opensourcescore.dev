from datetime import timedelta

from .score import safe_date_diff
from .maturity import build_maturity_score
from .health_risk import (
    build_health_risk_score,
    Score,
    CAUTION_NEEDED,
    HIGH_RISK,
    MODERATE_RISK,
)
from ..notes import Note


def score_python(package_data: dict, source_data: dict, score: Score):

    if not package_data:
        return

    expected_name = source_data.get("py_package")
    actual_name = package_data.get("name")

    if not expected_name:
        score.limit(CAUTION_NEEDED)
        score.notes.append(Note.NO_PROJECT_NAME.value)
        return

    if expected_name != actual_name:
        score.limit(HIGH_RISK)
        score.notes.append(Note.PACKAGE_NAME_MISMATCH.value)

    one_year = timedelta(days=365)
    skew = safe_date_diff(
        source_data.get("latest_commit"), package_data.get("release_date")
    )
    if skew and skew > one_year:
        score.limit(MODERATE_RISK)
        score.notes.append(Note.PACKGE_SKEW_NOT_UPDATED.value)

    if skew and skew < -one_year:
        score.limit(MODERATE_RISK)
        score.notes.append(Note.PACKGE_SKEW_NOT_RELEASED.value)

    return


def build_score(source_url, source_data, package_data):
    if source_data is None:
        return None
    score: dict = {
        "source_url": source_url,
        "packages": [],
        "ecosystem_destination": {
            "pypi": source_data.get("py_package"),
            "npm": None,
            "conda": None,
        },
    }

    score["maturity"] = build_maturity_score(source_url, source_data)
    sc = build_health_risk_score(source_data)
    score_python(package_data, source_data, sc)
    score["health_risk"] = sc.dict_string_notes()
    score["last_updated"] = source_data["latest_commit"]

    license = source_data.get("license")
    if license:
        score["license"] = license["license"]
        score["license_kind"] = license["kind"]
        score["license_modified"] = license["modified"]

    return score
