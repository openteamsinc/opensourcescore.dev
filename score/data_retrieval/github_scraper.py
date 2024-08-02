import os
import re
import pandas as pd
import requests
from pyarrow import parquet as pq
from tqdm import tqdm
from logger import setup_logger

logger = setup_logger()

# Constants
GITHUB_API_URL = "https://api.github.com/repos/"
AUTH_HEADER = {"Authorization": ""}
# AUTH_HEADER = {"Authorization": os.getenv("GITHUB_TOKEN", "")}  # Use an environment variable for the GitHub token

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
    if response.status_code == 200:
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
    else:
        logger.error(f"Failed to fetch data for {repo_url}: {response.status_code}")
        return None


def scrape_github_data(config):
    """
    Scrapes GitHub data for packages specified by the configuration.

    Args:
        config (dict): Configuration dictionary containing letters to scrape.
    """
    letters_to_scrape = config["letters"]
    all_data = []

    for letter in letters_to_scrape:
        directory = f"output/json/first_letter={letter}"
        if os.path.exists(directory):
            for file_name in os.listdir(directory):
                if file_name.endswith(".parquet"):
                    file_path = os.path.join(directory, file_name)
                    df = pq.read_table(file_path).to_pandas()

                    # Reconstruct project_urls from flattened columns
                    df["project_urls"] = df.filter(like="project_urls.").apply(
                        lambda row: {
                            col.split(".")[-1]: row[col]
                            for col in row.index
                            if pd.notna(row[col])
                        },
                        axis=1,
                    )

                    for _, row in tqdm(
                        df.iterrows(), total=len(df), desc=f"Processing letter {letter}"
                    ):
                        package_name = row.get("name")

                        # Get the GitHub URL from project_urls or home_page
                        source_url = row.get("project_urls", {}).get("Some_identifier")
                        if not source_url or "github.com" not in source_url:
                            source_url = row.get("home_page")

                        # Ensure the URL is in the correct format
                        if source_url and "github.com" in source_url:
                            repo_match = re.match(
                                r"https?://github\.com/[^/]+/[^/]+", source_url
                            )
                            if repo_match:
                                data = fetch_github_data(repo_match.group())
                                if data:
                                    data["first_letter"] = letter
                                    data["package_name"] = (
                                        package_name  # Add the package name
                                    )
                                    all_data.append(data)

    # Save the scraped data to a parquet file
    if all_data:
        output_df = pd.DataFrame(all_data)
        output_dir = "output/github"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, "github_data.parquet")
        output_df.to_parquet(output_file, partition_cols=["first_letter"])
        logger.info(
            "Scraping completed and data saved to output/github/github_data.parquet"
        )
    else:
        logger.info("No valid GitHub URLs found or failed to fetch data.")
