import pandas as pd
import pyarrow as pa
import toml
from typing import Optional
from git import Repo
from git.exc import GitCommandError, UnsafeProtocolError
from tqdm import tqdm
import tempfile
from datetime import datetime, timedelta
import logging
import os
from contextlib import contextmanager
from .license_detection import identify_license
from concurrent.futures import ThreadPoolExecutor

one_year_ago = datetime.now() - timedelta(days=365)

log = logging.getLogger(__name__)

# Default values
LICENSE_DEFAULTS = {
    "best_match": None,
    "error": None,
    "kind": None,
    "license": None,
    "similarity": 0.0,
    "modified": None,
}


@contextmanager
def clone_repo(url):
    with tempfile.TemporaryDirectory(
        prefix="score", suffix=".git", ignore_cleanup_errors=True
    ) as tmpdir:
        try:
            repo = Repo.clone_from(
                url, tmpdir, single_branch=True, no_checkout=True, filter="tree:0"
            )
            yield repo, {"source_url": url}
        except UnsafeProtocolError:
            yield None, {
                "error": "Unsafe Git Protocol: protocol looks suspicious",
                "source_url": url,
            }
        except GitCommandError as err:
            if err.status == 128 and "not found" in err.stderr.lower():
                yield None, {"error": "Repo not found", "source_url": url}
            else:
                log.error(f"{url}: {err.stderr}")
                yield None, {"error": "Could not clone repo", "source_url": url}

        return


git_schema = pa.schema(
    [
        ("partition", pa.int32()),
        ("source_url", pa.string()),
        ("error", pa.string()),
        ("recent_authors_count", pa.int32()),
        ("max_monthly_authors_count", pa.float32()),
        ("first_commit", pa.timestamp("ns")),
        ("latest_commit", pa.timestamp("ns")),
        (
            "license",
            pa.struct(
                [
                    ("best_match", pa.string()),
                    ("error", pa.string()),
                    ("kind", pa.string()),
                    ("license", pa.string()),
                    ("similarity", pa.float32()),
                    ("modified", pa.bool_()),
                ]
            ),
        ),
    ]
)


def scrape_git(urls: list) -> pd.DataFrame:
    """
    Clones a list of Git repositories, collects metadata about their commits and license types,
    and returns the data as a DataFrame.

    Args:
        urls (list): A list of Git repository URLs to scrape.

    Returns:
        pd.DataFrame: A DataFrame containing metadata for each repository. The DataFrame includes the following fields:

        - `source_url` (str): The URL of the repository.
        - `error` (Optional[str]): An error message if the repository could not be cloned or processed.
        - `recent_authors_count` (Optional[int]): The number of unique authors who have made commits in the last year.
        - `max_monthly_authors_count` (Optional[float]): The maximum number of unique authors
            contributing in any rolling 30-day window over the history of the repository.
        - `first_commit` (Optional[pd.Timestamp]): The timestamp of the first commit in the repository.
        - `latest_commit` (Optional[pd.Timestamp]): The timestamp of the most recent commit in the repository.
        - `license` (Optional[dict]): A dictionary containing the detected license information
            or an error message if the license could not be determined.

            The `license` field includes:
            - `best_match` (Optional[str]): The best license match identified, if available.
            - `error` (Optional[str]): An error message if the license detection process encountered an issue.
            - `kind` (Optional[str]): The kind of license detected (e.g., MIT, GPL).
            - `license` (Optional[str]): The specific license name detected.
            - `similarity` (Optional[float]): A similarity score indicating
                how closely the detected license matches the best-known license text (value between 0 and 1).
    """

    exec = ThreadPoolExecutor(16)
    all_data = list(
        tqdm(exec.map(create_git_metadata, urls), total=len(urls), disable=None)
    )

    df = pd.DataFrame(all_data)
    return df


def create_git_metadata(url: str) -> dict:
    with clone_repo(url) as (repo, metadata):
        if repo is None:
            return metadata
        metadata.update(get_commit_metadata(repo, url))
        license_data = get_license_type(repo, url)
        metadata["license"] = license_data
        metadata["py_package"] = get_pypackage_name(repo)

        return metadata


def get_commit_metadata(repo: Repo, url: str) -> dict:
    one_year_ago = datetime.now() - timedelta(days=365)

    try:
        commits = pd.DataFrame(
            [
                {"email": c.author.email, "when": c.authored_date}
                for c in repo.iter_commits()
            ]
        )
    except ValueError as err:
        log.error(f"{url}: {err}")
        return {"error": "Repository is empty"}

    # Filter out commits from GitHub's email domain
    commits = commits[~commits.email.str.endswith("github.com")]
    commits["when"] = pd.to_datetime(commits.when, unit="s")

    # Calculate recent authors count
    recent_authors_count = commits[commits.when > one_year_ago].email.nunique()

    # Calculate max monthly authors count
    commits_by_when = commits.sort_values("when").set_index("when")
    daily_authors = commits_by_when.resample("D")["email"].nunique()
    rolling_authors = daily_authors.rolling(window="30D").sum()
    max_monthly_authors_count = rolling_authors.max()

    # Return the required metadata
    return {
        "recent_authors_count": recent_authors_count,
        "max_monthly_authors_count": max_monthly_authors_count,
        "first_commit": commits.when.min(),
        "latest_commit": commits.when.max(),
    }


def get_license_type(repo: Repo, url: str) -> dict:
    try:
        # Check out the LICENSE file(s)
        repo.git.checkout(repo.active_branch, "--", "LICENSE*")
    except GitCommandError as e:
        log.error(f"{url}: Could not checkout license file: {e.stderr}")
        return {"error": "Could not checkout license"}

    # Check if LICENSE or LICENSE.txt exists in the root directory
    paths = ["LICENSE", "LICENSE.txt", "LICENSE.md"]
    license_file_path = None
    for path in paths:
        full_path = os.path.join(repo.working_dir, path)
        if os.path.isfile(full_path):
            license_file_path = full_path
            break

    if not license_file_path:
        return {"error": "No License Found"}

    # Read and return the license type
    with open(license_file_path, encoding="utf8", errors="ignore") as license_file:
        license_content = license_file.read().strip()

    return identify_license(license_content)


def get_pypackage_name(repo: Repo) -> Optional[str]:
    try:
        # Check out the LICENSE file(s)
        repo.git.checkout(repo.active_branch, "--", "pyproject.toml")
    except GitCommandError:
        return None

    full_path = os.path.join(repo.working_dir, "pyproject.toml")
    try:
        # Read and return the license type
        with open(full_path, encoding="utf8", errors="ignore") as fd:
            data = toml.load(fd)
    except FileNotFoundError:
        return None
    except (toml.TomlDecodeError, IndexError, IOError) as err:
        log.error(f"Error reading pyproject.toml: {err}")
        return None

    return data.get("project", {}).get("name")
