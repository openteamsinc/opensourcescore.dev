import logging

import requests
from common import json_to_parquet

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("conda")
logger.addHandler(logging.FileHandler("conda.log"))


def get_all_package_names(letter) -> list:
    """
    Fetches all the package names from the conda-forge feedstock-outputs.json file.

    Args:
        letter (str): The starting letter to filter the package names.

    Returns:
        packages_name_list (list): A list of package names.

    """
    packages_name_list = list()
    packages_name_url = "https://raw.githubusercontent.com/conda-forge/feedstock-outputs/single-file/feedstock-outputs.json"

    try:
        logger.info("Fetching all packages from URL: %s", packages_name_url)
        response = requests.get(packages_name_url)
        if response.status_code == 200:
            packages_name_list = response.json().keys()
            logger.info("Total Packages : %s", len(packages_name_list))
        else:
            logger.error(
                f"Failed to fetch URL: {packages_name_url} | status code: {response.status_code} | {response.text}"
            )
            packages_name_list = []
    except Exception as e:
        logger.error("Error fetching package names: %s", e)

    if letter:
        packages_name_list = {
            i for i in packages_name_list if str(i).startswith(letter)
        }
        logger.info(
            "Total Packages with letter %s : %s", letter, len(packages_name_list)
        )
    return packages_name_list


def get_required_json_data(package_data_response: dict, package_url: str) -> dict:
    """
    Extracts the required data from the package data response.

    Args:
        package_data_response (dict): The package data response.
        package_url (str): The package URL.

    Returns:
        required_json_data (dict): The required JSON data.
    """
    required_json_data = dict()
    required_json_data["name"] = package_data_response.get("name")
    required_json_data["initial_letter"] = package_data_response.get("name")[0]
    required_json_data["full_name"] = package_data_response.get("full_name", None)
    required_json_data["home_page"] = package_data_response.get("home", None)
    required_json_data["api_url"] = package_data_response.get("api_url", None)
    required_json_data["html_url"] = package_data_response.get("html_url", None)
    required_json_data["created_at"] = package_data_response.get("created_at", None)
    required_json_data["modified_at"] = package_data_response.get("modified_at", None)
    required_json_data["public"] = package_data_response.get("public", None)
    required_json_data["owner"] = package_data_response.get("owner", {}).get(
        "name", None
    )
    required_json_data["versions"] = package_data_response.get("versions", [])
    required_json_data["latest_version"] = package_data_response.get(
        "latest_version", None
    )
    required_json_data["revision"] = package_data_response.get("revision", None)
    required_json_data["license"] = package_data_response.get("license", None)
    required_json_data["license_url"] = package_data_response.get("license_url", None)
    required_json_data["dev_url"] = package_data_response.get("dev_url", None)
    required_json_data["doc_url"] = package_data_response.get("doc_url", None)
    required_json_data["source_git_url"] = package_data_response.get(
        "source_git_url", None
    )
    required_json_data["source_git_tag"] = package_data_response.get(
        "source_git_tag", None
    )
    required_json_data["watchers"] = package_data_response.get("watchers", None)
    required_json_data["upvoted"] = package_data_response.get("upvoted", None)
    required_json_data["downloads"] = sum(
        [i.get("ndownloads", 0) for i in package_data_response.get("files", [])]
    )
    required_json_data["package_url"] = package_url
    return required_json_data


def get_package_data(package_name: str) -> dict:
    """
    Fetches the package data for the given package name.

    Args:
        package_name (str): The package name.

    Returns:
        required_json_data (dict): The required JSON data.
    """
    logger.info("Package Name : %s", package_name)
    package_url = f"https://api.anaconda.org/package/conda-forge/{package_name}"
    response = requests.get(package_url)
    if response.status_code == 200:
        package_data_response = response.json()
        required_json_data = get_required_json_data(package_data_response, package_url)
        return required_json_data
    else:
        logger.error(
            f"Failed to fetch URL: {package_url} with status code: {response.status_code} | {response.text}"
        )
        return None


def scrape_conda_packages(letter_to_scrape: str) -> None:
    """
    Scrapes all the conda packages data for the given letter
    and saves the data in a parquet file.

    Args:
        letter_to_scrape (str): The letter to scrape.

    Returns:
        None
    """
    package_data_list = list()
    packages_name_list = get_all_package_names(letter_to_scrape)
    for package_name in list(packages_name_list):
        package_data = get_package_data(package_name)
        if package_data:
            package_data_list.append(package_data)
    if package_data_list:
        json_to_parquet(package_data_list, f"conda_package_data_{letter_to_scrape}")
        logger.info("Data saved for package : %s", len(package_data_list))
    else:
        logger.error("Failed to save data for package letter : %s", letter_to_scrape)
