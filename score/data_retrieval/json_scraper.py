import requests
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from data_storage.parquet_storage import save_to_parquet
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

        # Extract and filter relevant fields from the JSON response
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

    # Use a ThreadPoolExecutor to process packages in parallel
    with ThreadPoolExecutor(max_workers=26) as executor:
        futures = [
            executor.submit(
                process_packages_by_letter, letter, package_names, config, output_dir
            )
            for letter in letters
        ]

        # Wait for all futures to complete
        for future in as_completed(futures):
            future.result()


def process_packages_by_letter(letter, package_names, config, output_dir):
    """
    Processes packages by their first letter and saves the data to the specified output format.

    Args:
        letter (str): The starting letter of the packages to process.
        package_names (list): List of all package names.
        config (dict): Configuration dictionary containing output parameters.
        output_dir (str): Directory to save the output files.
    """
    # Filter package names that start with the specified letter
    letter_package_names = [name for name in package_names if name[0].lower() == letter]

    # Process each package and save the data
    for package_name in tqdm(letter_package_names, desc=f"Processing letter {letter}"):
        package_data = get_package_data(package_name)
        if package_data:
            # Normalize JSON data to a flat table
            df = pd.json_normalize(package_data)
            save_to_parquet(df, letter, output_dir)
