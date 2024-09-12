from typing import List
import pandas as pd
import pyarrow as pa
from tqdm import tqdm
from dateutil.parser import parse as parsedate
from ..utils.request_session import get_session

CONDA_PACKAGE_URL_TEMPLATE = "https://api.anaconda.org/package/{channel}/{package}"


conda_schema = pa.schema(
    [
        ("partition", pa.int32()),
        ("insert_ts", pa.timestamp("ns")),
        ("name", pa.string()),
        ("channel", pa.string()),
        ("full_name", pa.string()),
        ("source_url", pa.string()),
        ("latest_version", pa.string()),
        ("ndownloads", pa.int64()),
        ("release_date", pa.timestamp("ns")),
    ]
)


def scrape_conda(channel, package_names: List[str]) -> pd.DataFrame:
    """
    Scrapes metadata for a list of Conda packages from the Anaconda API and returns the data as a DataFrame.

    Args:
        channel (str): The Anaconda channel from which to retrieve the package data.
        package_names (List[str]): A list of package names to scrape data for.

    Returns:
        pd.DataFrame: A DataFrame containing metadata for each package. The DataFrame includes the following fields:

        - `name` (str): The name of the package.
        - `full_name` (str): The full name of the package, typically including the channel and package name.
        - `source_url` (Optional[str]): The URL to the source code repository, if available.
                This is taken from either `dev_url` or `source_git_url`.
        - `latest_version` (str): The latest version of the package available on the specified Anaconda channel.
        - `ndownloads` (int): The total number of downloads for all versions of the package.
    """
    s = get_session()
    all_packages = []
    for package in tqdm(package_names, disable=None):
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
                "release_date": parsedate(package_data["modified_at"]),
            }
        )

    return pd.DataFrame(all_packages)
