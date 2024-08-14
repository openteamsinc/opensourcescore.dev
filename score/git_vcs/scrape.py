import pandas as pd
from git import Repo
from git.exc import GitCommandError, UnsafeProtocolError
import tempfile
from tqdm import tqdm
from datetime import datetime, timedelta
import logging

one_year_ago = datetime.now() - timedelta(days=365)

log = logging.getLogger(__name__)


def scrape_git(urls: list) -> pd.DataFrame:
    all_data = []
    for url in tqdm(urls, disable=None):
        info = get_info_from_git_repo(url)
        info["source_url"] = url
        all_data.append(info)

    return pd.DataFrame(all_data)


def get_info_from_git_repo(url) -> dict:
    with tempfile.TemporaryDirectory(
        prefix="score", suffix=".git", ignore_cleanup_errors=True
    ) as tmpdir:
        try:
            repo = Repo.clone_from(url, tmpdir, no_checkout=True, filter="tree:0")
        except UnsafeProtocolError:
            return {"error": "Unsafe Git Protocol: protocol looks suspicious"}
        except GitCommandError as err:
            if err.status == 128 and "not found" in err.stderr:
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
        commits = commits[~commits.email.str.endswith("github.com")]
        commits["when"] = pd.to_datetime(commits.when, unit="s")

        recent_authors_count = commits[commits.when > one_year_ago].email.nunique()

        # Sort commits by date and set 'when' as index
        commits_by_when = commits.sort_values("when").set_index("when")

        # Resample to daily frequency and count unique authors
        daily_authors = commits_by_when.resample("D")["email"].nunique()

        # Calculate the rolling 30-day sum of unique authors
        rolling_authors = daily_authors.rolling(window="30D").sum()

        # Find the maximum number of authors in any 30-day period
        max_monthly_authors_count = rolling_authors.max()

        return {
            "recent_authors_count": recent_authors_count,
            "max_monthly_authors_count": max_monthly_authors_count,
            "first_commit": commits.when.min(),
            "latest_commit": commits.when.max(),
        }
