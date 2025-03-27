from datetime import timedelta
import re
from .score import safe_date_diff, Score
from .maturity import build_maturity_score
from .legal import build_legal_score
from .health_risk import (
    build_health_risk_score,
)

from ..notes import Note


def pypi_normalize(name):
    if not name:
        return None

    return re.sub(r"[-_.]+", "-", name).lower()


def score_python(package_data: dict, source_data: dict):

    if not package_data:
        return

    published_name = pypi_normalize(package_data.get("name"))
    # expected_name = pypi_normalize(source_data.get("py_package"))
    package_destinations_names = [
        name[5:]
        for name, _ in source_data["package_destinations"]
        if name.startswith("pypi/")
    ]

    if len(package_destinations_names) == 0:
        yield Note.NO_PROJECT_NAME
    elif published_name not in package_destinations_names:
        yield Note.PACKAGE_NAME_MISMATCH

    one_year = timedelta(days=365)
    skew = safe_date_diff(
        source_data.get("latest_commit"), package_data.get("release_date")
    )
    if skew and skew > one_year:
        yield Note.PACKAGE_SKEW_NOT_UPDATED

    if skew and skew < -one_year:
        yield Note.PACKAGE_SKEW_NOT_RELEASED

    package_license = package_data.get("license")
    if not package_license:
        yield Note.PACKAGE_NO_LICENSE
    else:
        print(package_license, source_data.get("license", {}).get("kind"))
        if package_license != source_data.get("license", {}).get("kind"):

            yield Note.PACKAGE_LICENSE_MISMATCH

    return


def build_score(source_url, source_data, package_data):

    score: dict = {
        "source_url": source_url,
        "packages": [],
        "last_updated": source_data and source_data.get("latest_commit"),
        "ecosystem_destination": {
            "pypi": source_data and source_data.get("py_package"),
            "npm": None,
            "conda": None,
        },
    }
    if source_data is None:
        score["status"] = "not_found"
        score["notes"] = [Note.PACKAGE_SOURCE_NOT_FOUND.name]
        return score

    license = source_data.get("license")
    if license and not license.get("error"):
        score["license"] = license["license"]
        score["license_kind"] = license["kind"]
        score["license_modified"] = license["modified"]

    notes = []
    notes.extend(build_maturity_score(source_url, source_data))

    notes.extend(build_health_risk_score(source_data))

    notes.extend(build_legal_score(source_data))

    # -- Distribution + Language specific
    notes.extend(score_python(package_data, source_data))

    score["notes"] = sorted({note.name for note in notes})

    score["legal"] = Score.legal(notes).dict_string_notes()
    score["health_risk"] = Score.health_risk(notes).dict_string_notes()
    score["maturity"] = Score.maturity(notes).dict_string_notes()

    return score
