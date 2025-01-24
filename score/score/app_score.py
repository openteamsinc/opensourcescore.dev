from datetime import timedelta

from .score import safe_date_diff
from .maturity import build_maturity_score
from .legal import build_legal_score
from .health_risk import (
    build_health_risk_score,
    Score,
)
from ..notes import Note


def score_python(package_data: dict, source_data: dict, score: Score):

    if not package_data:
        return

    expected_name = source_data.get("py_package")
    actual_name = package_data.get("name")

    if not expected_name:
        score.add_note(Note.NO_PROJECT_NAME)
        return

    if expected_name != actual_name:
        score.add_note(Note.PACKAGE_NAME_MISMATCH)

    one_year = timedelta(days=365)
    skew = safe_date_diff(
        source_data.get("latest_commit"), package_data.get("release_date")
    )
    if skew and skew > one_year:
        score.add_note(Note.PACKGE_SKEW_NOT_UPDATED)

    if skew and skew < -one_year:
        score.add_note(Note.PACKGE_SKEW_NOT_RELEASED)

    return


def build_score(source_url, source_data, package_data):

    score: dict = {
        "source_url": source_url,
        "packages": [],
        "ecosystem_destination": {
            "pypi": source_data and source_data.get("py_package"),
            "npm": None,
            "conda": None,
        },
    }

    score["maturity"] = build_maturity_score(source_url, source_data)

    health_score = build_health_risk_score(source_data)
    score_python(package_data, source_data, health_score)

    score["health_risk"] = health_score.dict_string_notes()
    score["last_updated"] = source_data.get("latest_commit")

    legal_score = build_legal_score(source_data)
    score["legal"] = legal_score.dict_string_notes()

    license = source_data.get("license")
    if license and not license.get("error"):
        score["license"] = license["license"]
        score["license_kind"] = license["kind"]
        score["license_modified"] = license["modified"]

    return score
