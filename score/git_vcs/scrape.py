import logging
import os
import tempfile
import time
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, timedelta
from glob import glob
from typing import Iterator

import pandas as pd
from git import Repo
from git.cmd import Git
from git.exc import GitCommandError, UnsafeProtocolError

from score.models import License, Source
from score.notes import Note

from .check_url import get_source_from_url
from .license_detection import identify_license
from .package_destinations import get_all_pypackage_names

one_year_ago = datetime.now() - timedelta(days=365)

log = logging.getLogger(__name__)


MAX_CLONE_TIME = 30

LICENSE_PATTERNS = [
    "**/LICEN[CS]E",
    "**/LICEN[CS]E.*",
    "**/licen[cs]e",
    "**/licen[cs]e.*",
    "**/COPYING",
    "**/copying",
    "**/COPYING.*",
    "**/copying.*",
]

sparse_checkout = """
**/package.json
**/pyproject.toml
**/setup.cfg
**/setup.py
**/requirements.txt
**/LICEN?E*
**/licen?e*
**/COPYING*
**/copying*
"""


@contextmanager
def clone_repo(url: str):
    log.info(f"Cloning {url}")
    source = Source(package_destinations=[], source_url=url)

    with tempfile.TemporaryDirectory(
        prefix="score", suffix=".git", ignore_cleanup_errors=True
    ) as tmpdir:
        try:
            s = time.time()
            mygit = Git(os.getcwd())
            mygit.clone(
                Git.polish_url(url),
                tmpdir,
                single_branch=True,
                no_checkout=True,
                sparse=True,
                filter="tree:0",
                # depth=1,
                # https://github.com/gitpython-developers/GitPython/issues/892
                # See issue for why we cant use clone_from
                kill_after_timeout=MAX_CLONE_TIME,
            )
            repo = Repo(tmpdir)
            log.info(f"Cloned to {tmpdir} in {time.time() - s:.2f} seconds")

            repo.git.execute(["git", "sparse-checkout", "init", "--no-cone"])

            with open(f"{repo.git_dir}/info/sparse-checkout", "w") as fp:
                fp.write(sparse_checkout)

            s = time.time()
            repo.git.checkout("HEAD")
            log.info(f"Checked out in {time.time() - s:.2f} seconds")
            yield repo, source

        except UnsafeProtocolError:
            source.error = Note.NO_SOURCE_UNSAFE_GIT_PROTOCOL
            yield None, source
        except GitCommandError as err:
            if err.status == 128 and "not found" in err.stderr.lower():
                source.error = Note.NO_SOURCE_REPO_NOT_FOUND
                yield None, source
            elif err.status == -9 and "timeout:" in err.stderr.lower():
                source.error = Note.NO_SOURCE_GIT_TIMEOUT
                yield None, source

            else:
                log.error(f"{url}: {err.stderr}")
                source.error = Note.NO_SOURCE_OTHER_GIT_ERROR
                yield None, source
        return


def create_git_metadata(url: str) -> Source:
    source = get_source_from_url(url)
    if source.error is not None:
        return source

    with clone_repo(url) as (repo, metadata):
        if repo is None:
            return metadata
        metadata = replace(metadata, **get_commit_metadata(repo, url))
        metadata.licenses = list(get_license_type(repo, url))
        metadata.package_destinations.extend(get_all_pypackage_names(repo))

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
    print(commits[commits.when > one_year_ago].email.unique())

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


def get_license_type(repo: Repo, url: str) -> Iterator[License]:

    license_file_paths = [
        path
        for pattern in LICENSE_PATTERNS
        for path in glob(os.path.join(repo.working_dir, pattern), recursive=True)
    ]

    for license_file_path in license_file_paths:
        log.info(f"Found license file: {license_file_path}")
        try:
            with open(
                license_file_path, encoding="utf8", errors="ignore"
            ) as license_file:
                license_content = license_file.read().strip()
        except IsADirectoryError:
            continue

        yield identify_license(
            url, license_content, license_file_path[len(str(repo.working_dir)) + 1 :]
        )
