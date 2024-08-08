from datetime import datetime, timedelta
from typing import List

import pandas as pd
from tqdm import tqdm

from ..utils.request_session import get_session

OSV_API_URL = "https://api.osv.dev/v1/query"


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
        for vuln in vulns_list:
            published_date = datetime.strptime(
                vuln.get("published"), "%Y-%m-%dT%H:%M:%SZ"
            )
            current_date = datetime.now()
            if current_date - published_date <= timedelta(days=365):
                required_vuln.append(
                    {
                        "id": vuln.get("id"),
                        "source": vuln.get("database_specific").get("source"),
                        "aliases": vuln.get("aliases"),
                        "details": vuln.get("details"),
                        "published": published_date,
                        "severity": vuln.get("severity"),
                        "database_specific": vuln.get("database_specific"),
                        "versions": vuln.get("versions"),
                        "references": vuln.get("references"),
                        "ranges": vuln.get("affected").get("ranges"),
                    }
                )

        all_packages.append(
            {
                "name": "requests",
                "num_vulnerabilities": len(required_vuln),
                "vulnerabilities": required_vuln,
            }
        )

    return pd.DataFrame(all_packages)
