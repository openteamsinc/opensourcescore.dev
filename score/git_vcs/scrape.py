import pandas as pd
from git import Repo
from git.exc import GitCommandError, UnsafeProtocolError
import tempfile
from tqdm import tqdm
from datetime import datetime, timedelta
import logging
import os
from .license_detection import identify_license

one_year_ago = datetime.now() - timedelta(days=365)

log = logging.getLogger(__name__)


def scrape_git(urls: list) -> pd.DataFrame:
    all_data = []
    for url in tqdm(urls, disable=None):
        metadata = get_commit_metadata(url)
        if "error" in metadata:
            # Skip the license check if commit metadata retrieval failed
            metadata["license_type"] = "Skipped due to commit metadata error"
        else:
            license_type = get_license_type(url)
            metadata["license_type"] = license_type
        metadata["source_url"] = url
        all_data.append(metadata)
    return pd.DataFrame(all_data)


def get_commit_metadata(url) -> dict:
    one_year_ago = datetime.now() - timedelta(days=365)

    with tempfile.TemporaryDirectory(
        prefix="score", suffix=".git", ignore_cleanup_errors=True
    ) as tmpdir:
        try:
            repo = Repo.clone_from(url, tmpdir, no_checkout=True, filter="tree:0")
        except UnsafeProtocolError:
            return {"error": "Unsafe Git Protocol: protocol looks suspicious"}
        except GitCommandError as err:
            if err.status == 128 and "not found" in err.stderr.lower():
                return {"error": "Repo not found"}
            log.error(f"{url}: {err.stderr}")
            return {"error": "Could not clone repo"}

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


def get_license_type(url) -> str:
    with tempfile.TemporaryDirectory(
        prefix="score", suffix=".git", ignore_cleanup_errors=True
    ) as tmpdir:
        try:
            # Perform a shallow clone with depth=1 to fetch the LICENSE file
            repo = Repo.clone_from(url, tmpdir, depth=1)
        except UnsafeProtocolError:
            log.error(f"{url}: Unsafe Git Protocol: protocol looks suspicious")
            return "No License Found"
        except GitCommandError as err:
            if err.status == 128 and "not found" in err.stderr.lower():
                log.error(f"{url}: Repo not found")
                return "No License Found"
            log.error(f"{url}: {err.stderr}")
            return "No License Found"

        try:
            # Check out the LICENSE file(s)
            repo.git.checkout(repo.active_branch, "--", "LICENSE*")

            # Check if LICENSE or LICENSE.txt exists in the root directory
            license_file_path = None
            if os.path.exists(os.path.join(tmpdir, "LICENSE")):
                license_file_path = os.path.join(tmpdir, "LICENSE")
            elif os.path.exists(os.path.join(tmpdir, "LICENSE.txt")):
                license_file_path = os.path.join(tmpdir, "LICENSE.txt")

            if not license_file_path:
                return "No License Found"

            # Read and return the license type
            with open(license_file_path, "r", encoding="utf-8") as license_file:
                license_content = license_file.read()
                return identify_license(license_content)

        except Exception as e:
            log.error(f"{url}: Error accessing the repository files: {str(e)}")
            return "No License Found"
