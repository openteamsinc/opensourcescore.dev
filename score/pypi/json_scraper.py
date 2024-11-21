import click
from typing import List, Optional, Dict, Tuple
from urllib.parse import urlparse
import pandas as pd
import pyarrow as pa
from tqdm import tqdm
import logging
from dateutil.parser import parse as parsedate
from ..utils.request_session import get_session
from ..utils.map import do_map

log = logging.getLogger(__name__)

pypi_schema = pa.schema(
    [
        ("partition", pa.int32()),
        ("insert_ts", pa.timestamp("ns")),
        ("name", pa.string()),
        ("version", pa.string()),
        ("source_url", pa.string()),
        ("source_url_key", pa.string()),
        ("release_date", pa.timestamp("ns")),
    ]
)


def get_package_data(package_name: str):
    """
    Fetches package data from the PyPI JSON API for a given package name and filters out specific fields.
    Additionally fetches download counts from the PyPI Stats API.

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

    version = info.get("version", None)
    release_date = None
    release_info = package_data.get("releases", {}).get(version, [])

    if version and release_info:
        upload_dates = [
            parsedate(i.get("upload_time"))
            for i in release_info
            if i.get("upload_time")
        ]
        first_upload_date = min(upload_dates)
        release_date = first_upload_date

    filtered_data = {
        "name": package_name,
        "version": version,
        "source_url": source_url,
        "source_url_key": source_url_key,
        "release_date": release_date,
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

    for key in ["code", "repository", "source", "source code", "github", "homepage"]:
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
        packages (List[str]): List of package names to scrape data for.

    Returns:
        pd.DataFrame: A DataFrame containing the scraped data. The DataFrame includes the following fields:

        - `name` (str): The name of the package.
        - `first_letter` (str): The first letter of the package name. (Used for partitioning)
        - `bugtrack_url` (Optional[str]): URL for the package's bug tracker, if available.
        - `classifiers` (List[str]): A list of classifiers associated with the package,
                typically indicating its license, supported operating systems, and programming languages.
        - `docs_url` (Optional[str]): URL for the package's documentation, if available.
        - `download_url` (Optional[str]): URL where the package can be downloaded, if available.
        - `home_page` (Optional[str]): The home page URL for the package, if available.
        - `keywords` (Optional[str]): A comma-separated string of keywords related to the package.
        - `maintainer` (Optional[str]): The name of the maintainer of the package.
        - `maintainer_email` (Optional[str]): The email address of the maintainer of the package.
        - `release_url` (Optional[str]): URL of the release page for the package on PyPI.
        - `requires_python` (Optional[str]): The Python version requirements for the package.
        - `version` (Optional[str]): The current version of the package.
        - `yanked_reason` (Optional[str]): The reason why the package version was yanked, if applicable.
        - `source_url` (Optional[str]): The normalized URL for the source code repository, if identified.
        - `source_url_key` (Optional[str]): The key from the `project_urls` dictionary that was
            identified as the source URL (e.g., "code", "repository", "source", "homepage").
    """
    all_package_data = list(
        tqdm(do_map(get_package_data, packages), total=len(packages), disable=None)
    )
    failed_count = len([x for x in all_package_data if x is None])
    all_package_data = [x for x in all_package_data if x is not None]

    click.echo(
        f"OK, Failed to fetch data for {failed_count} of {len(packages)} packages."
    )
    return pd.DataFrame(all_package_data)
