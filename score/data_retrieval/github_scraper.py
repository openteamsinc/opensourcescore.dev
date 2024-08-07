import os
import pandas as pd
import requests
from tqdm import tqdm
import logging

log = logging.getLogger(__name__)

# Constants
GITHUB_API_URL = "https://api.github.com/repos/"
AUTH_HEADER = {"Authorization": f"token {os.getenv('GITHUB_TOKEN', '')}"}

# Fields to extract from the GitHub API response
FIELDS_TO_EXTRACT = {
    "created_at": "created_at",
    "updated_at": "updated_at",
    "pushed_at": "pushed_at",
    "stargazers_count": "stargazers_count",
    "forks_count": "forks_count",
    "open_issues_count": "open_issues_count",
    "subscribers_count": "subscribers_count",
    "watchers_count": "watchers_count",
    "releases_url": "releases_url",
    "commits_url": "commits_url",
    "collaborators_url": "collaborators_url",
    "contributors_url": "contributors_url",
    "license.name": "license",
}


def fetch_github_data(repo_url):
    """
    Fetches data from the GitHub API for a given repository URL and extracts specified fields.

    Args:
        repo_url (str): The GitHub repository URL.

    Returns:
        dict: A dictionary containing the extracted data fields.
    """
    repo_name = "/".join(repo_url.split("/")[-2:])
    response = requests.get(GITHUB_API_URL + repo_name, headers=AUTH_HEADER)
    if response.status_code == 404:
        log.debug(f"Skipping repository not found for URL {repo_url}")
        return None
    response.raise_for_status()  # Raise an error for bad status codes
    data = response.json()

    extracted_data = {}
    for key, field in FIELDS_TO_EXTRACT.items():
        if "." in key:
            top_level_key, nested_key = key.split(".")
            top_level_data = data.get(top_level_key, {})
            if isinstance(top_level_data, dict):
                extracted_data[field] = top_level_data.get(nested_key, None)
            else:
                extracted_data[field] = None
        else:
            extracted_data[field] = data.get(key, None)
    return extracted_data


def scrape_github_data(input_dir: str, partition: int):
    """
    Initiates the scraping process using the GitHub API based on the given partition.

    Args:
        input_dir (str): Directory to read the input files from.
        partition (int): The partition number to process.

    Returns:
        pd.DataFrame: A DataFrame containing the scraped data.
    """

    input_path = os.path.join(input_dir, f"partition={partition}.parquet")
    if not os.path.exists(input_path):
        log.debug(f"No data for partition {partition}")
        return pd.DataFrame()

    df = pd.read_parquet(input_path)
    all_repo_data = []

    for _, row in tqdm(
        df.iterrows(), total=len(df), desc=f"Processing partition {partition}"
    ):
        package_name = row["name"]
        source_url = row["source_url"]

        data = fetch_github_data(source_url)
        if data:
            data["partition"] = partition
            data["name"] = package_name
            all_repo_data.append(data)

    return pd.DataFrame(all_repo_data)
