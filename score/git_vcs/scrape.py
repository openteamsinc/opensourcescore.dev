import logging
import os
from dataclasses import replace
from datetime import datetime, timedelta
from glob import glob
from typing import Iterator

import pandas as pd
from git import Repo

from score.models import License, Source
from score.notes import Note

from .check_url import get_source_from_url
from .clone_repo import LICENSE_PATTERNS, clone_repo
from .license_detection import identify_license
from .package_destinations import get_all_pypackage_names

one_year_ago = datetime.now() - timedelta(days=365)

log = logging.getLogger(__name__)


MAX_CLONE_TIME = 30

NOT_A_LICENSE_FILE_EXT = [".json", ".csv", ".svg", ".jpg", ".jpeg"]


def create_git_metadata(url: str) -> Source:
    source = get_source_from_url(url)
    if source.error is not None:
        return source

    with clone_repo(url) as (repo, metadata):
        if repo is None:
            return metadata
        metadata = replace(metadata, **get_commit_metadata(repo, url))
        metadata.licenses = list(get_license_type(repo, url))
        log.info(f"Found {len(metadata.licenses)} licenses in {repo.working_dir}")
        metadata.package_destinations.extend(get_all_pypackage_names(repo))
        log.info(
            f"Found {len(metadata.package_destinations)} package destinations in {repo.working_dir}"
        )

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
        return {"error": Note.REPO_EMPTY}

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
        "recent_authors_count": int(recent_authors_count),
        "max_monthly_authors_count": int(max_monthly_authors_count),
        "first_commit": commits.when.min(),
        "latest_commit": commits.when.max(),
    }


def is_valid_license_filename(path: str) -> bool:
    _, ext = os.path.splitext(path)
    if ext in NOT_A_LICENSE_FILE_EXT:
        return False
    return True


def is_valid_license(path: str, content: str) -> bool:
    path = path.lower()
    if path.startswith("docs"):
        # This is documentation including a license file
        if path.endswith("license.rst") and (
            ".. literalinclude::" in content or ".. include::" in content
        ):
            log.info(f"Skipping {path} due to literalinclude directive")
            return False
        if path.endswith("license.md") and ("{include} ../LICENSE" in content):
            log.info(f"Skipping {path} due to literalinclude directive")
            return False
    return True


MAX_FILES = 2500


def get_license_type(repo: Repo, url: str) -> Iterator[License]:

    license_file_paths = sorted(
        [
            path
            for pattern in LICENSE_PATTERNS
            for path in glob(os.path.join(repo.working_dir, pattern), recursive=True)
            if is_valid_license_filename(path)
        ],
        key=lambda x: (len(x), x),
    )

    if len(license_file_paths) > MAX_FILES:
        log.warning(
            f"Found {len(license_file_paths)} license files in {repo.working_dir}. "
            "This is more than the expected number of license files. "
            "Please check if this is correct."
        )
    log.info(f"Extracting {len(license_file_paths[:MAX_FILES])} license files")
    for license_file_path in license_file_paths[:MAX_FILES]:
        log.debug(f"Found license file: {license_file_path}")
        try:
            with open(
                license_file_path, encoding="utf8", errors="ignore"
            ) as license_file:
                license_content = license_file.read().strip()
        except IsADirectoryError:
            continue

        rel_path = license_file_path[len(str(repo.working_dir)) + 1 :]

        if not is_valid_license(rel_path, license_content):
            continue

        yield identify_license(url, license_content, rel_path)
