import json
from typing import List

import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

from ..utils.request_session import get_session

NPM_PACKAGE_TEMPLATE_URL = "https://www.npmjs.com/package/{package_name}"


def scrape_npm(package_names: List[str]) -> pd.DataFrame:
    s = get_session()
    all_packages = []
    for package in tqdm(package_names, disable=None):
        url = NPM_PACKAGE_TEMPLATE_URL.format(package_name=package)
        res = s.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, "html.parser")
        script_tag_data = soup.select_one("script")

        if script_tag_data.has_attr("integrity"):
            json_data = (
                str(script_tag_data.text).lstrip("window.__context__ = ").rstrip(";")
            )
            data = json.loads(json_data)

            context = data.get("context", {})
            package_data = context.get("packument", {})

            ndownloads = (
                sum([i.get("downloads") for i in context.get("downloads", {})])
                if context.get("downloads", {})
                else 0
            )
            maintainers_count = (
                len(package_data.get("maintainers", [])) if package_data else 0
            )

            all_packages.append(
                {
                    "name": package,
                    "full_name": context.get("package"),
                    "source_url": (
                        package_data.get("repository")
                        if package_data.get("repository")
                        else None
                    ),
                    "latest_version": package_data.get("version"),
                    "ndownloads": ndownloads,
                    "maintainers_count": maintainers_count,
                }
            )

    return pd.DataFrame(all_packages)
