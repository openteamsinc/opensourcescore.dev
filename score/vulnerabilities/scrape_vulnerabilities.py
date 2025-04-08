from typing import Optional, Tuple
from cvss import CVSS2, CVSS3, CVSS4
import logging
from score.models import Vulnerabilities, Vulnerability
from score.utils.safe_time import try_parse_date
from score.utils.request_session import get_session
from score.notes import Note

log = logging.getLogger(__name__)

OSV_API_URL = "https://api.osv.dev/v1/query"


def categorize_severity(score: Optional[float]) -> str:
    """
    Categorize the severity based on the CVSS (Common Vulnerability Scoring System) score.

    CVSS Score Ranges:
    - LOW: 0.0 - 3.9
    - MODERATE: 4.0 - 6.9
    - HIGH: 7.0 - 8.9
    - CRITICAL: 9.0 - 10.0

    Reference :
        1. https://ossf.github.io/osv-schema/#severitytype-field
        2. https://www.first.org/cvss/specification-document (Look into 6. Qualitative Severity Rating Scale )
    """
    if score is None:
        return "UNKNOWN"

    if score >= 9.0:
        return "CRITICAL"
    elif score >= 7.0:
        return "HIGH"
    elif score >= 4.0:
        return "MODERATE"
    else:
        return "LOW"


def extract_severity_number(vuln) -> Optional[float]:
    severity = vuln.get("severity", [])
    if not severity:
        return None

    for sev in sorted(severity, key=lambda sev: sev.get("type"), reverse=True):
        cvss_vector = sev.get("score")

        if sev.get("type") == "CVSS_V4":
            return CVSS4(cvss_vector).scores()[0]
        if sev.get("type") == "CVSS_V3":
            return CVSS3(cvss_vector).scores()[0]
        if sev.get("type") == "CVSS_V2":
            return CVSS2(cvss_vector).scores()[0]

    return None


def extract_severity(vuln) -> Tuple[Optional[float], str]:
    num = extract_severity_number(vuln)
    return num, categorize_severity(num)


ecosystems = {"pypi": "PyPI", "npm": "npm"}


def scrape_vulnerability(package_ecosystem: str, package: str) -> Vulnerabilities:

    if package_ecosystem.lower() not in ecosystems:
        return Vulnerabilities(error=Note.VULNERABILITIES_CHECK_FAILED)

    v_ecosystem = ecosystems[package_ecosystem.lower()]
    session = get_session()
    payload = {"package": {"name": package, "ecosystem": v_ecosystem}}
    res = session.post(OSV_API_URL, json=payload)

    if res.status_code != 200:
        return Vulnerabilities(error=Note.VULNERABILITIES_CHECK_FAILED)

    vulns_list = res.json().get("vulns")
    vulns = Vulnerabilities()
    if not vulns_list:
        return vulns

    seen: set[str] = set()
    for vuln in vulns_list:

        known_ids = set([vuln["id"]])
        known_ids.update(vuln["aliases"])

        have_seen = len(seen.intersection(known_ids)) > 0
        seen.update(known_ids)

        if have_seen:
            continue

        severity_num, severity = extract_severity(vuln)
        published = try_parse_date(vuln.get("published"))

        if published is None:
            log.error(vuln)
            log.error(vuln.get("published"))
            raise ValueError(
                f"Published date is missing vulnerability payload {payload}"
            )

        modified = try_parse_date(vuln.get("modified"))

        days_to_fix = (
            int((modified - published).total_seconds() / (60 * 60 * 24))
            if modified is not None
            else None
        )
        vulns.vulns.append(
            Vulnerability(
                id=vuln["id"],
                severity=severity,
                severity_num=severity_num,
                published_on=published,
                fixed_on=modified,
                days_to_fix=days_to_fix,
            )
        )
    return vulns


def main():

    import argparse

    parser = argparse.ArgumentParser(
        description="Scrape vulnerabilities for a list of packages."
    )
    parser.add_argument(
        "--ecosystem",
        type=str,
        required=True,
        help="Ecosystem to scrape vulnerabilities for (e.g., pypi, npm).",
    )
    parser.add_argument(
        "--package",
        type=str,
        required=True,
        help="Single package",
    )

    args = parser.parse_args()
    ecosystem = args.ecosystem
    package = args.package
    vulns = scrape_vulnerability(ecosystem, package)
    print(f"Vulnerabilities for {ecosystem}/{package}:")
    for vuln in vulns.vulns:
        print(f"ID: {vuln.id}")
        print(f"  Published: {vuln.published_on}")
        print(f"  Modified: {vuln.fixed_on}")
        print(f"  Severity: {vuln.severity}")
        print(f"  Days to fix: {vuln.days_to_fix}")
        print()


if __name__ == "__main__":
    main()
