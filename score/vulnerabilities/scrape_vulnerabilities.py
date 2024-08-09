from datetime import datetime, timedelta
from typing import List

import pandas as pd
from tqdm import tqdm
from cvss import CVSS2, CVSS3, CVSS4

from ..utils.request_session import get_session

OSV_API_URL = "https://api.osv.dev/v1/query"


def categorize_severity(score):
    if score >= 7.0:
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


def scrape_vulnerabilities(ecosystem, package_names: List[str]) -> pd.DataFrame:
    session = get_session()
    all_packages = []
    for package in tqdm(package_names):
        payload = {"package": {"name": package, "ecosystem": ecosystem}}
        response = session.post(OSV_API_URL, json=payload)
        if response.status_code != 200:
            continue
        vulns_list = response.json().get("vulns")
        required_vuln = list()
        if vulns_list:
            for vuln in vulns_list:
                if (
                    datetime.now()
                    - datetime.strptime(vuln.get("published"), "%Y-%m-%dT%H:%M:%SZ")
                ) <= timedelta(days=365):
                    required_vuln.append(get_vulnerability_severity(vuln))

        all_packages.append(
            {
                "name": package,
                "ecosystem": ecosystem,
                "total_vuln": len(required_vuln),
                "count_high": len([v for v in required_vuln if v == "HIGH"]),
                "count_moderate": len([v for v in required_vuln if v == "MODERATE"]),
                "count_low": len([v for v in required_vuln if v == "LOW"]),
            }
        )

    return pd.DataFrame(all_packages)
