import requests
from typing import List
import pandas as pd
from tqdm import tqdm
import logging
import os
import re

from ..utils.common import get_all_package_names


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
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    if response.status_code == 404:
        log.debug(f"Skipping package not found for package {package_name}")
        return None
    response.raise_for_status()  # Raise an error for bad status codes
    package_data = response.json()  # Parse the JSON response

    # Extract the 'info' section
    info = package_data.get("info", {})

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
        "source_url": extract_github_repo(info.get("project_urls", {})),
    }

    return filtered_data


def extract_github_repo(project_urls):
    """
    Extracts the GitHub repository URL from the project_urls dictionary.

    Args:
        project_urls (dict): The project URLs dictionary.

    Returns:
        str: The GitHub repository URL if found, otherwise None.
    """
    if not project_urls:
        return None
    for url in project_urls.values():
        if url and GITHUB_REPO_PATTERN.match(url):
            return url
    return None


def scrape_json(output_dir: str, letters: List[str]):
    """
    Initiates the scraping process using the JSON API based on the given configuration.

    Args:
        config (dict): Configuration dictionary containing scraping parameters.
    """
    # Get all package names from the PyPI Simple API
    package_names = get_all_package_names()

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for letter in letters:
        process_packages_by_letter(letter, package_names, output_dir)


def process_packages_by_letter(letter, package_names, output_dir):
    """
    Processes packages by their first letter and saves the data to the specified output format.

    Args:
        letter (str): The starting letter of the packages to process.
        package_names (list): List of all package names.
        output_dir (str): Directory to save the output files.
    """
    # Filter package names that start with the specified letter
    letter_package_names = [name for name in package_names if name[0].lower() == letter]

    all_package_data = []
    for package_name in tqdm(
        letter_package_names, desc=f"Processing partition column {letter!r}"
    ):
        package_data = get_package_data(package_name)
        if package_data:
            all_package_data.append(package_data)

    df = pd.DataFrame(all_package_data)
    df.to_parquet(output_dir, partition_cols=["first_letter"])
