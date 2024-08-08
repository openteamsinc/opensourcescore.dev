from typing import List
import pandas as pd
from tqdm import tqdm

from ..utils.request_session import get_session

CONDA_PACKAGE_URL_TEMPLATE = "https://api.anaconda.org/package/{channel}/{package}"


def scrape_conda(channel, package_names: List[str]) -> pd.DataFrame:
    s = get_session()
    all_packages = []
    for package in tqdm(package_names):
        url = CONDA_PACKAGE_URL_TEMPLATE.format(channel=channel, package=package)
        res = s.get(url)
        res.raise_for_status()
        package_data = res.json()

        ndownloads = 0
        for f in package_data["files"]:
            ndownloads += f["ndownloads"]
        source_url = package_data.get("dev_url") or package_data.get("source_git_url")
        all_packages.append(
            {
                "name": package_data["name"],
                "full_name": package_data["full_name"],
                "source_url": source_url,
                "latest_version": package_data["latest_version"],
                "ndownloads": ndownloads,
            }
        )

    return pd.DataFrame(all_packages)
