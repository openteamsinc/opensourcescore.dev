import re
from datetime import timedelta
from hashlib import md5
from typing import Collection, Iterator, Optional

from score.models import Package
from score.models import Score as ScoreType
from score.models import Source, Vulnerabilities
from score.utils.normalize_license_content import normalize_license_content

from ..notes import Note
from .health_risk import build_health_risk_score
from .legal import build_legal_score
from .maturity import build_maturity_score
from .score import safe_date_diff
from .score_type import ScoreBuilder
from .security import score_security


def pypi_normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def package_normalize_name(ecosystem: str, name: str) -> str:
    if ecosystem == "pypi":
        return pypi_normalize(name)
    return name


def check_package_license(pkg: Package, source_data: Source) -> Iterator[str]:

    if not pkg.license:
        yield Note.PACKAGE_NO_LICENSE
        return

    # if not source_data.license:
    #     return
    for license in source_data.licenses:

        source_license_kind = license.kind
        source_license_md5 = license.md5

        if not source_license_kind:
            # check next
            continue

        if source_license_kind.lower() == "unknown":
            # check next
            continue

        if pkg.license == source_license_kind:
            # No mismatch
            return

        package_license_md5 = md5(
            normalize_license_content(pkg.license).encode("utf-8")
        ).hexdigest()

        if package_license_md5 == source_license_md5:
            # The package license is the exact same as the source file contents
            return

    if len(pkg.license) > 100:
        yield Note.PACKAGE_LICENSE_NOT_SPDX_ID
    else:
        yield Note.PACKAGE_LICENSE_MISMATCH


def score_python(package_data: Package, source_data: Source) -> Iterator[str]:

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


def build_notes(
    source_url,
    source_data: Source,
    package_data: Package,
    vuln_data: Vulnerabilities,
) -> list[str]:
    notes: list[str] = []
    notes.extend(build_maturity_score(source_url, source_data))

    notes.extend(build_health_risk_score(source_data))

    notes.extend(build_legal_score(source_data))

    # -- Distribution + Language specific
    notes.extend(score_python(package_data, source_data))

    notes.extend(score_security(vuln_data))
    return notes


def build_score(
    source_url,
    source_data: Optional[Source],
    package_data: Package,
    vuln_data: Vulnerabilities,
) -> ScoreType:

    notes: Collection[str]
    if source_data is None:
        if package_data.status == "not_found":
            notes = [Note.NOT_OPEN_SOURCE]
        else:
            notes = [Note.NO_SOURCE_REPO_NOT_FOUND]

    else:
        notes = build_notes(source_url, source_data, package_data, vuln_data)

    notes = set(notes)
    return ScoreType(
        notes=sorted(notes),
        legal=ScoreBuilder.legal(notes).asmodel(),
        health_risk=ScoreBuilder.health_risk(notes).asmodel(),
        maturity=ScoreBuilder.maturity(notes).asmodel(),
        security=ScoreBuilder.security(notes).asmodel(),
    )
