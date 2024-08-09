import os
import pandas as pd
import requests
from tqdm import tqdm
import logging
import duckdb

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
    Additionally fetches details from 'collaborators_url' and 'contributors_url'.

    Args:
        repo_url (str): The GitHub repository URL.

    Returns:
        dict: A dictionary containing the extracted data fields and additional details.
    """
    repo_name = "/".join(repo_url.split("/")[-2:])
    response = requests.get(GITHUB_API_URL + repo_name, headers=AUTH_HEADER)

    # Handle non-existent repositories gracefully
    if response.status_code == 404:
        log.debug(f"Skipping repository not found for URL {repo_url}")
        return None

    response.raise_for_status()  # Raise an error for bad status codes
    data = response.json()

    # Extract required fields from the GitHub API response
    extracted_data = {}
    for key, field in FIELDS_TO_EXTRACT.items():
        if "." in key:
            top_level_key, nested_key = key.split(".")
            top_level_data = data.get(top_level_key, {})
            extracted_data[field] = (
                top_level_data.get(nested_key)
                if isinstance(top_level_data, dict)
                else None
            )
        else:
            extracted_data[field] = data.get(key)

    # Fetch additional details for contributors
    if contributors_url := data.get("contributors_url"):
        contributors_response = requests.get(contributors_url, headers=AUTH_HEADER)
        if contributors_response.status_code == 200:
            extracted_data["contributors"] = (
                contributors_response.json()
            )
            extracted_data["contributors_count"] = (
                len(contributors_response.json())
            )
        else:
            log.debug(f"Failed to fetch contributors for URL {repo_url}")

    return extracted_data


def scrape_github_data(input_file: str):
    """
    Initiates the scraping process using the GitHub API for a given input file.

    Args:
        input_file (str): Path to the input file (github-urls.parquet).

    Returns:
        pd.DataFrame: A DataFrame containing the scraped data.
    """

    query = f"""
        SELECT *
        FROM read_parquet('{input_file}')
        WHERE source_url IS NOT NULL
        AND source_url LIKE '%github.com%'
    """
    df = duckdb.query(query).to_df()

    if df.empty:
        log.debug("No valid GitHub URLs found in the input file")
        return pd.DataFrame()

    all_repo_data = []

    # Iterate over the DataFrame rows and fetch data from GitHub API
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing GitHub URLs"):
        source_url = row["source_url"]
        data = fetch_github_data(source_url)
        if data:
            data["source_url"] = source_url  # Use source_url as the unique key
            all_repo_data.append(data)

    return pd.DataFrame(all_repo_data)
