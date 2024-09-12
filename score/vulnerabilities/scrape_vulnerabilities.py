from typing import List
from dateutil.parser import parse as parse_date
import pandas as pd
from cvss import CVSS2, CVSS3, CVSS4
from tqdm import tqdm
from ..utils.request_session import get_session
from ..utils.map import do_map

OSV_API_URL = "https://api.osv.dev/v1/query"


def categorize_severity(score):
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
    if score >= 9.0:
        return "CRITICAL"
    elif score >= 7.0:
        return "HIGH"
    elif score >= 4.0:
        return "MODERATE"
    else:
        return "LOW"


def extract_severity(vuln):
    severity = vuln.get("severity", [])
    if severity:
        for sev in severity:
            cvss_vector = sev.get("score")
            cvss = None
            if sev.get("type") == "CVSS_V2":
                cvss = CVSS2(cvss_vector)
            elif sev.get("type") == "CVSS_V3":
                cvss = CVSS3(cvss_vector)
            elif sev.get("type") == "CVSS_V4":
                cvss = CVSS4(cvss_vector)

            if cvss:
                return categorize_severity(cvss.scores()[0])
    return None


def extract_affected_severity(vuln):
    affected = vuln.get("affected", [])
    if affected:
        for aff in affected:
            ecosystem_specific = aff.get("ecosystem_specific", {})
            return ecosystem_specific.get("severity")
    return None


def get_vulnerability_severity(vuln):
    severity = extract_severity(vuln)
    if severity:
        return severity
    return extract_affected_severity(vuln)


def scrape_vulnerability(ecosystem, package: str) -> list:
    session = get_session()
    payload = {"package": {"name": package, "ecosystem": ecosystem}}
    response = session.post(OSV_API_URL, json=payload)
    if response.status_code != 200:
        return []
    vulns_list = response.json().get("vulns")
    if not vulns_list:
        return []
    vulns = []
    for vuln in vulns_list:
        published = parse_date(vuln.get("published"))
        severity = get_vulnerability_severity(vuln)
        if severity is None:
            continue
        vulns.append(
            {
                "name": package,
                "ecosystem": ecosystem,
                "published": published,
                "id": vuln["id"],
                "severity": get_vulnerability_severity(vuln),
                "summary": vuln.get("summary"),
            }
        )
    return vulns


def scrape_vulnerabilities(ecosystem, package_names: List[str]) -> pd.DataFrame:

    # all_packages = []
    # for package in tqdm(package_names):
    #     vulns = scrape_vulnerability(ecosystem, package)
    #     all_packages.extend(vulns)

    mapped = do_map(lambda x: scrape_vulnerability(ecosystem, x), package_names)
    all_packages = [
        item for sublist in tqdm(mapped, total=len(package_names)) for item in sublist
    ]

    return pd.DataFrame(all_packages)
