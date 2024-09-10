import pandas as pd
import pyarrow as pa
import toml
from typing import Optional
from git import Repo
from git.exc import GitCommandError, UnsafeProtocolError
from git.cmd import Git
from tqdm import tqdm
import tempfile
from datetime import datetime, timedelta
import logging
import os
from contextlib import contextmanager
from ..utils.map import do_map
from .license_detection import identify_license
from .check_url import check_url
from ..notes import Note

one_year_ago = datetime.now() - timedelta(days=365)

log = logging.getLogger(__name__)


MAX_CLONE_TIME = 30


@contextmanager
def clone_repo(url):
    with tempfile.TemporaryDirectory(
        prefix="score", suffix=".git", ignore_cleanup_errors=True
    ) as tmpdir:
        try:
            mygit = Git(os.getcwd())
            mygit.clone(
                Git.polish_url(url),
                tmpdir,
                single_branch=True,
                no_checkout=True,
                filter="tree:0",
                # https://github.com/gitpython-developers/GitPython/issues/892
                # See issue for why we cant use clone_from
                kill_after_timeout=MAX_CLONE_TIME,
            )
            repo = Repo(tmpdir)
            # repo = Repo.clone_from(
            #     url, tmpdir, single_branch=True, no_checkout=True, filter="tree:0"
            # )
            yield repo, {"source_url": url}
        except UnsafeProtocolError:
            yield None, {
                "error": Note.UNSAFE_GIT_PROTOCOL.value,
                "source_url": url,
            }
        except GitCommandError as err:
            if err.status == 128 and "not found" in err.stderr.lower():
                yield None, {"error": Note.REPO_NOT_FOUND.value, "source_url": url}
            elif err.status == -9 and "timeout:" in err.stderr.lower():
                yield None, {
                    "error": Note.GIT_TIMEOUT.value,
                    "source_url": url,
                }

            else:
                log.error(f"{url}: {err.stderr}")
                yield None, {"error": Note.OTHER_GIT_ERROR.value, "source_url": url}

        return


git_schema = pa.schema(
    [
        ("partition", pa.int32()),
        ("insert_ts", pa.timestamp("ns")),
        ("source_url", pa.string()),
        ("error", pa.int32()),
        ("recent_authors_count", pa.int32()),
        ("max_monthly_authors_count", pa.float32()),
        ("first_commit", pa.timestamp("ns")),
        ("latest_commit", pa.timestamp("ns")),
        ("py_package", pa.string()),
        (
            "license",
            pa.struct(
                [
                    ("best_match", pa.string()),
                    ("error", pa.int32()),
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

    all_data = list(
        tqdm(do_map(create_git_metadata, urls), total=len(urls), disable=None)
    )

    df = pd.DataFrame(all_data)
    return df


def create_git_metadata(url: str) -> dict:
    is_valid, metadata = check_url(url)
    if not is_valid:
        return metadata

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
        return {"error": Note.REPO_EMPTY.value}

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
        return {"error": Note.LICENSE_CHECKOUT_ERROR.value}

    # Check if LICENSE or LICENSE.txt exists in the root directory
    paths = ["LICENSE", "LICENSE.txt", "LICENSE.md"]
    license_file_path = None
    for path in paths:
        full_path = os.path.join(repo.working_dir, path)
        if os.path.isfile(full_path):
            license_file_path = full_path
            break

    if not license_file_path:
        return {"error": Note.NO_LICENSE.value}

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
    name = data.get("project", {}).get("name")

    if not name:
        return None

    return name.lower().replace("_", "-")
