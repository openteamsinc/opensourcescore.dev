import os
import pandas as pd
import requests
from tqdm import tqdm
import logging
from typing import List

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


def scrape_github_data(input_dir: str, output_dir: str, letters: List[str]):
    """
    Initiates the scraping process using the GitHub API based on the given configuration.

    Args:
        input_dir (str): Directory to read the input files from.
        output_dir (str): Directory to save the output files.
        letters (List[str]): List of letters to process.
    """
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for letter in letters:
        process_repos_by_letter(input_dir, output_dir, letter)


def process_repos_by_letter(input_dir: str, output_dir: str, letter: str):
    """
    Processes repositories by their first letter and saves the data to the specified output format.

    Args:
        input_dir (str): Directory to read the input files from.
        output_dir (str): Directory to save the output files.
        letter (str): The starting letter of the repositories to process.
    """
    input_path = os.path.join(input_dir, f"first_letter={letter}")
    if not os.path.exists(input_path):
        log.debug(f"No data for letter {letter}")
        return

    df = pd.read_parquet(input_path)
    all_repo_data = []

    for _, row in tqdm(
        df.iterrows(), total=len(df), desc=f"Processing letter {letter}"
    ):
        package_name = row["name"]
        source_url = row["source_url"]

        data = fetch_github_data(source_url)
        if data:
            data["first_letter"] = letter
            data["name"] = package_name
            all_repo_data.append(data)

    if all_repo_data:
        output_df = pd.DataFrame(all_repo_data)
        output_path = os.path.join(output_dir, f"first_letter={letter}")
        output_df.to_parquet(output_path, partition_cols=["first_letter"])
        log.info(f"Data saved for letter {letter} to {output_path}")
    else:
        log.info(f"No valid GitHub data found for letter {letter}")
