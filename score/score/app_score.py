from typing import Optional
from datetime import timedelta
from hashlib import md5
import re
from score.utils.normalize_license_content import normalize_license_content
from score.models import Package, Source, Score as ScoreType
from .score_type import ScoreBuilder
from .score import safe_date_diff
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


def check_package_license(pkg: Package, source_data: Source):

    if not pkg.license:
        yield Note.PACKAGE_NO_LICENSE
        return

    if not source_data.license:
        return

    source_license_kind = source_data.license.kind
    source_license_md5 = source_data.license.md5

    if not source_license_kind:
        return

    if source_license_kind.lower() == "unknown":
        return

    if pkg.license == source_license_kind:
        return

    package_license_md5 = md5(
        normalize_license_content(pkg.license).encode("utf-8")
    ).hexdigest()

    if package_license_md5 == source_license_md5:
        # The package license is the exact same as the source file contents
        return

    yield Note.PACKAGE_LICENSE_MISMATCH


def score_python(package_data: Package, source_data: Source):

    if not package_data:
        return
    if source_data.error:
        return

    ecosystem = package_data.ecosystem
    published_name = package_normalize_name(ecosystem, package_data.name)

    package_destinations_names = [
        name[len(ecosystem) + 1 :]
        for name, _ in source_data.package_destinations
        if name.startswith(f"{ecosystem}/")
    ]

    if len(package_destinations_names) == 0:
        yield Note.NO_PROJECT_NAME
    elif published_name not in package_destinations_names:
        yield Note.PACKAGE_NAME_MISMATCH

    one_year = timedelta(days=365)
    skew = safe_date_diff(source_data.latest_commit, package_data.release_date)
    if skew and skew > one_year:
        yield Note.PACKAGE_SKEW_NOT_UPDATED

    if skew and skew < -one_year:
        yield Note.PACKAGE_SKEW_NOT_RELEASED

    yield from check_package_license(package_data, source_data)

    return


def build_notes(source_url, source_data: Source, package_data: Package) -> list[Note]:
    notes = []
    notes.extend(build_maturity_score(source_url, source_data))

    notes.extend(build_health_risk_score(source_data))

    notes.extend(build_legal_score(source_data))

    # -- Distribution + Language specific
    notes.extend(score_python(package_data, source_data))
    return notes


def build_score(
    source_url, source_data: Optional[Source], package_data: Package
) -> ScoreType:

    if source_data is None:
        notes = [Note.NO_SOURCE_URL]
    else:
        notes = build_notes(source_url, source_data, package_data)

    return ScoreType(
        notes=sorted(notes, key=lambda x: x.name),
        legal=ScoreBuilder.legal(notes).asmodel(),
        health_risk=ScoreBuilder.health_risk(notes).asmodel(),
        maturity=ScoreBuilder.maturity(notes).asmodel(),
    )
