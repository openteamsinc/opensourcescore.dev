import click
from typing import List, Optional, Dict, Tuple
from urllib.parse import urlparse
import pandas as pd
from tqdm import tqdm
import logging
import re

from ..utils.request_session import get_session


log = logging.getLogger(__name__)

GITHUB_REPO_PATTERN = re.compile(r"https://github\.com/[^/]+/[^/]+/?")


def get_package_data(package_name):
    """
    Fetches package data from the PyPI JSON API for a given package name and filters out specific fields.

    Args:
        package_name (str): The name of the package to fetch data for.

    Returns:
        dict: A dictionary containing filtered package data.
    """
    s = get_session()
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = s.get(url)
    if response.status_code == 404:
        log.debug(f"Skipping package not found for package {package_name}")
        return None
    response.raise_for_status()  # Raise an error for bad status codes
    package_data = response.json()  # Parse the JSON response

    # Extract the 'info' section
    info = package_data.get("info", {})

    source_url_key, source_url = extract_source_url(info.get("project_urls", {}))

    # Extract desired fields
    filtered_data = {
        "name": info.get("name", None),
        "first_letter": package_name[0],
        "bugtrack_url": info.get("bugtrack_url", None),
        "classifiers": info.get("classifiers", []),
        "docs_url": info.get("docs_url", None),
        "download_url": info.get("download_url", None),
        "home_page": info.get("home_page", None),
        "keywords": info.get("keywords", None),
        "maintainer": info.get("maintainer", None),
        "maintainer_email": info.get("maintainer_email", None),
        "release_url": info.get("release_url", None),
        "requires_python": info.get("requires_python", None),
        "version": info.get("version", None),
        "yanked_reason": info.get("yanked_reason", None),
        "source_url": source_url,
        "source_url_key": source_url_key,
    }

    return filtered_data


def normalize_source_url(url: str):
    URL = urlparse(url)
    if URL.hostname in ["github.com", "gitlab.com", "bitbucket.org"]:
        path_components = URL.path.strip("/").split("/")
        if len(path_components) < 2:
            # Invalid git*.com/ URL
            return None
        return f"https://{URL.hostname}/{path_components[0]}/{path_components[1]}"

    return url


def extract_source_url(
    project_urls: Dict[str, str]
) -> Tuple[Optional[str], Optional[str]]:
    if not project_urls:
        return None, None

    project_urls = {k.lower(): v for k, v in project_urls.items()}

    for key in ["code", "repository", "source", "homepage"]:
        if key not in project_urls:
            continue
        source_url = normalize_source_url(project_urls[key])
        if source_url:
            return key, source_url

    return None, None


def scrape_json(packages: List[str]) -> pd.DataFrame:
    """
    Initiates the scraping process using the JSON API based on the given configuration.

    Args:
        config (dict): Configuration dictionary containing scraping parameters.
    """
    all_package_data = []
    failed_count = 0
    for package_name in tqdm(packages, desc="Reading package data", disable=None):
        package_data = get_package_data(package_name)
        if package_data:
            all_package_data.append(package_data)
        else:
            failed_count += 1

    click.echo(
        f"OK, Failed to fetch data for {failed_count} of {len(packages)} packages."
    )

    return pd.DataFrame(all_package_data)
