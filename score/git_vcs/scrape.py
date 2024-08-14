import pandas as pd
from git import Repo
from git.exc import GitCommandError, UnsafeProtocolError
import tempfile
from tqdm import tqdm
from datetime import datetime, timedelta
import logging
from .license_detection import identify_license

one_year_ago = datetime.now() - timedelta(days=365)

log = logging.getLogger(__name__)


def scrape_git(urls: list) -> pd.DataFrame:
    all_data = []
    for url in tqdm(urls, disable=None):
        metadata = get_commit_metadata(url)
        license_type = get_license_type(url)
        metadata["license_type"] = license_type
        metadata["source_url"] = url
        all_data.append(metadata)
    return pd.DataFrame(all_data)


def get_commit_metadata(url) -> dict:
    with tempfile.TemporaryDirectory(
        prefix="score", suffix=".git", ignore_cleanup_errors=True
    ) as tmpdir:
        try:
            repo = Repo.clone_from(url, tmpdir, no_checkout=True, filter="tree:0")
        except (UnsafeProtocolError, GitCommandError) as err:
            log.error(f"{url}: {err}")
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

        commits = commits[~commits.email.str.endswith("github.com")]
        commits["when"] = pd.to_datetime(commits.when, unit="s")

        recent_authors_count = commits[commits.when > one_year_ago].email.nunique()
        commits_by_when = commits.sort_values("when").set_index("when")
        daily_authors = commits_by_when.resample("D")["email"].nunique()
        rolling_authors = daily_authors.rolling(window="30D").sum()
        max_monthly_authors_count = rolling_authors.max()

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
        except (UnsafeProtocolError, GitCommandError) as err:
            log.error(f"{url}: {err}")
            return "No License Found"

        # Check for a LICENSE file in the root directory
        license_content = None
        root_files = repo.tree().blobs  # List blobs (files) in the repository root
        for blob in root_files:
            if "LICENSE" in blob.name.upper():
                try:
                    license_content = blob.data_stream.read().decode("utf-8")
                    break
                except Exception as e:
                    log.error(f"Error reading license file {blob.name}: {str(e)}")

        return (
            "No License Found"
            if not license_content
            else identify_license(license_content)
        )
