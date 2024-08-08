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
        if vulns_list:
            required_vuln = list()
            for vuln in vulns_list:
                if (
                    datetime.now()
                    - datetime.strptime(vuln.get("published"), "%Y-%m-%dT%H:%M:%SZ")
                ) <= timedelta(days=365):
                    print(vuln.get("published"))
                    affected = vuln.get("affected")[0]
                    required_vuln.append(
                        {
                            "id": vuln.get("id"),
                            "source": affected.get("database_specific", None).get(
                                "source", None
                            ),
                            "aliases": vuln.get("aliases", None),
                            "details": vuln.get("details", None),
                            "published": vuln.get("published"),
                            "severity": vuln.get("severity", None),
                            "versions": affected.get("versions", None),
                            "references": vuln.get("references", None),
                            "ranges": affected.get("ranges", None),
                        }
                    )

            all_packages.append(
                {
                    "name": package,
                    "ecosystem": ecosystem,
                    "num_vulnerabilities": len(required_vuln),
                    "vulnerabilities": required_vuln,
                }
            )

    return pd.DataFrame(all_packages)
