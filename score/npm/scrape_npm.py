import logging
from datetime import datetime
from typing import List

import pandas as pd
from tqdm import tqdm

from ..utils.request_session import get_session

log = logging.getLogger(__name__)

current_date = datetime.now().strftime("%Y-%m-%d")

NPM_PACKAGE_TEMPLATE_URL = "https://registry.npmjs.org/{package_name}"
NPM_PACKAGE_DOWNLOAD_URL = (
    "https://api.npmjs.org/downloads/range/2000-01-01:{current_date}/{package_name}"
)


def get_npm_package_downloads(package_name: str) -> int:
    s = get_session()
    downloads_url = NPM_PACKAGE_DOWNLOAD_URL.format(
        current_date=current_date, package_name=package_name
    )
    downloads_res = s.get(downloads_url)
    if downloads_res.status_code == 404:
        log.debug(
            f"Skipping download data package not found for package {package_name}"
        )
        return 0
    downloads_res.raise_for_status()
    downloads_data = downloads_res.json()
    total_downloads = sum(day["downloads"] for day in downloads_data["downloads"])
    ndownloads = total_downloads if total_downloads else 0
    return ndownloads


def scrape_npm(package_names: List[str]) -> pd.DataFrame:
    s = get_session()
    all_packages = []
    for package in tqdm(package_names, disable=None):
        url = NPM_PACKAGE_TEMPLATE_URL.format(package_name=package)
        res = s.get(url)
        if res.status_code == 404:
            log.debug(f"Skipping package not found for package {package}")
            return {}
        res.raise_for_status()
        package_data = res.json()

        ndownloads = get_npm_package_downloads(package)
        maintainers_count = (
            len(package_data.get("maintainers", [])) if package_data else 0
        )
        repository = package_data.get("repository", None)
        source_url = repository.get("url") if isinstance(repository, dict) else None

        all_packages.append(
            {
                "name": package,
                "full_name": package_data.get("name"),
                "source_url": source_url,
                "latest_version": package_data.get("dist-tags", {}).get("latest"),
                "ndownloads": ndownloads,
                "maintainers_count": maintainers_count,
            }
        )

    return pd.DataFrame(all_packages)
