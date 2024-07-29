import requests
import pandas as pd
from tqdm import tqdm
from logger import setup_logger
from utils.common import get_all_package_names
import os

logger = setup_logger()


def get_package_data(package_name):
    """
    Fetches package data from the PyPI JSON API for a given package name and filters out specific fields.

    Args:
        package_name (str): The name of the package to fetch data for.

    Returns:
        dict: A dictionary containing filtered package data.
    """
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url)
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
            "project_urls": info.get("project_urls", None),
            "release_url": info.get("release_url", None),
            "requires_python": info.get("requires_python", None),
            "version": info.get("version", None),
            "yanked_reason": info.get("yanked_reason", None),
        }

        return filtered_data
    except requests.RequestException as e:
        logger.error(f"Failed to retrieve data for package {package_name}: {e}")
        return None


def scrape_json(config):
    """
    Initiates the scraping process using the JSON API based on the given configuration.

    Args:
        config (dict): Configuration dictionary containing scraping parameters.
    """
    # Get all package names from the PyPI Simple API
    package_names = get_all_package_names()
    letters = config["letters"]

    # Create the output directory if it doesn't exist
    output_dir = os.path.join("output", "json")
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
    for package_name in tqdm(letter_package_names, desc=f"Processing letter {letter}"):
        package_data = get_package_data(package_name)
        if package_data:
            all_package_data.append(package_data)

    df = pd.DataFrame(all_package_data)
    df.to_parquet(output_dir, partition_cols=["first_letter"])
