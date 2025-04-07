from datetime import timedelta
from hashlib import md5
import re
from score.utils.normalize_license_content import normalize_license_content
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


def package_normalize_name(ecosystem: str, name: str) -> str:
    if ecosystem == "pypi":
        return pypi_normalize(name)
    return name


def check_package_license(package_data: dict, source_data: dict):
    package_license = package_data.get("license")
    if not package_license:
        yield Note.PACKAGE_NO_LICENSE
        return

    source_license_kind = source_data.get("license", {}).get("kind")
    source_license_md5 = source_data.get("license", {}).get("md5")

    if not source_license_kind:
        return

    if source_license_kind.lower() == "unknown":
        return

    if package_license == source_license_kind:
        return

    package_license_md5 = md5(
        normalize_license_content(package_license).encode("utf-8")
    ).hexdigest()

    if package_license_md5 == source_license_md5:
        # The package license is the exact same as the source file contents
        return

    yield Note.PACKAGE_LICENSE_MISMATCH


def score_python(package_data: dict, source_data: dict):

    if not package_data:
        return
    if source_data.get("error"):
        return
    ecosystem = package_data["ecosystem"]

    published_name = package_normalize_name(ecosystem, package_data.get("name"))

    package_destinations_names = [
        name[len(ecosystem) + 1 :]
        for name, _ in source_data.get("package_destinations", [])
        if name.startswith(f"{ecosystem}/")
    ]

    print("package_destinations_names", package_destinations_names)

    if len(package_destinations_names) == 0:
        yield Note.NO_PROJECT_NAME
    elif published_name not in package_destinations_names:
        yield Note.PACKAGE_NAME_MISMATCH

    one_year = timedelta(days=365)
    print(package_data)
    skew = safe_date_diff(
        source_data.get("latest_commit"), package_data.get("release_date")
    )
    if skew and skew > one_year:
        yield Note.PACKAGE_SKEW_NOT_UPDATED

    if skew and skew < -one_year:
        yield Note.PACKAGE_SKEW_NOT_RELEASED

    yield from check_package_license(package_data, source_data)

    return


def build_score(source_url, source_data, package_data):

    score: dict = {
        "source_url": source_url,
        "packages": [],
        "last_updated": source_data and source_data.get("latest_commit"),
    }
    if source_data is None:
        score["status"] = "not_found"
        score["notes"] = [Note.NO_SOURCE_URL.name]
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
