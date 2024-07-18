import requests
import re
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from data_storage.csv_storage import save_to_csv
from data_storage.parquet_storage import save_to_parquet
from logger import setup_logger

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
        response.raise_for_status()
        package_data = response.json()

        filtered_data = {
            "info.bugtrack_url": package_data.get("info", {}).get("bugtrack_url", None),
            "info.docs_url": package_data.get("info", {}).get("docs_url", None),
            "info.home_page": package_data.get("info", {}).get("home_page", None),
            "info.maintainer": package_data.get("info", {}).get("maintainer", None),
            "info.maintainer_email": package_data.get("info", {}).get(
                "maintainer_email", None
            ),
            "info.project_urls": package_data.get("info", {}).get("project_urls", None),
            "info.release_url": package_data.get("info", {}).get("release_url", None),
            "info.requires_dist": package_data.get("info", {}).get(
                "requires_dist", None
            ),
            "info.version": package_data.get("info", {}).get("version", None),
            "info.yanked_reason": package_data.get("info", {}).get(
                "yanked_reason", None
            ),
        }

        return filtered_data
    except requests.RequestException as e:
        logger.error(f"Failed to retrieve data for package {package_name}: {e}")
        return None


def get_all_package_names():
    """
    Fetches the list of all package names from the PyPI Simple API.

    Returns:
        list: A list of all package names.
    """
    url = "https://pypi.org/simple/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        package_names = re.findall(r'<a href="/simple/([^/]+)/">', response.text)
        return package_names
    except requests.RequestException as e:
        print(f"Failed to retrieve the list of all packages: {e}")
        return []


def scrape_json(config):
    """
    Initiates the scraping process using the JSON API based on the given configuration.

    Args:
        config (dict): Configuration dictionary containing scraping parameters.
    """
    package_names = get_all_package_names()
    letters = config["letters"]

    with ThreadPoolExecutor(max_workers=26) as executor:
        futures = [
            executor.submit(process_packages_by_letter, letter, package_names, config)
            for letter in letters
        ]

        for future in as_completed(futures):
            future.result()


def process_packages_by_letter(letter, package_names, config):
    """
    Processes and saves package data for packages starting with a specific letter.

    Args:
        letter (str): The letter to filter package names by.
        package_names (list): List of all package names.
        config (dict): Configuration dictionary containing output parameters.
    """
    letter_package_names = [name for name in package_names if name[0].lower() == letter]

    for package_name in tqdm(letter_package_names, desc=f"Processing letter {letter}"):
        package_data = get_package_data(package_name)
        if package_data:
            df = pd.json_normalize(package_data)
            if config["output_format"] in [1, 3]:
                save_to_csv(df, letter)
            if config["output_format"] in [2, 3]:
                save_to_parquet(df, letter, config["entries_per_parquet"])
