from typing import List

import pandas as pd
from tqdm import tqdm

from ..utils.request_session import get_session

OSV_API_URL = "https://api.osv.dev/v1/query"


def scrape_vulnerabilities(ecosystem, package_names: List[str]) -> pd.DataFrame:
    session = get_session()
    all_packages = []
    for package in tqdm(package_names):
        print(f"Scraping vulnerabilities for {package}")
        payload = {"package": {"name": package, "ecosystem": ecosystem}}
        response = session.get(OSV_API_URL, json=payload)
        if response.status_code != 200:
            print(f"Failed to scrape vulnerabilities for {package}")
            continue
        package_data = response.json()["vulns"]

        all_packages.append(
            {
                "name": package,
                "id": package_data.get("id"),
                "details": package_data.get("details"),
                "published": package_data.get("published"),
                "modified": package_data.get("modified"),
                "source": package_data.get("database_specific").get("source"),
                "severity": package_data.get("ecosystem_specific").get("severity"),
                "references": package_data.get("references"),
                "versions": package_data.get("affected").get("versions"),
            }
        )

    return pd.DataFrame(all_packages)
