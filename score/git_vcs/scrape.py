import pandas as pd
from git import Repo
from git.exc import GitCommandError, UnsafeProtocolError
import tempfile
from tqdm import tqdm
from datetime import datetime, timedelta
import logging
import os
from contextlib import contextmanager
from .license_detection import identify_license

one_year_ago = datetime.now() - timedelta(days=365)

log = logging.getLogger(__name__)


@contextmanager
def clone_repo(url):
    with tempfile.TemporaryDirectory(
        prefix="score", suffix=".git", ignore_cleanup_errors=True
    ) as tmpdir:
        os.chdir(tmpdir)

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


def scrape_git(urls: list) -> pd.DataFrame:
    all_data = []
    for url in tqdm(urls, disable=None):
        metadata = create_git_metadata(url)
        all_data.append(metadata)
    return pd.DataFrame(all_data)


def create_git_metadata(url: str) -> dict:
    with clone_repo(url) as (repo, metadata):
        if repo is None:
            return metadata
        metadata.update(get_commit_metadata(repo, url))
        license_data = get_license_type(repo, url)
        metadata["license"] = license_data

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
    except GitCommandError:
        return {"error": "Could not checkout license"}

    # Check if LICENSE or LICENSE.txt exists in the root directory
    paths = ["LICENSE", "LICENSE.txt", "LICENSE.md"]
    license_file_path = None
    for path in paths:
        if os.path.exists(path):
            license_file_path = path
            break

    if not license_file_path:
        return {"error": "No License Found"}

    # Read and return the license type
    with open(license_file_path) as license_file:
        license_content = license_file.read().strip()

    return identify_license(license_content)
