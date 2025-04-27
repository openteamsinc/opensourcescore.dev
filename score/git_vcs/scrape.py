import pandas as pd
import time
from git import Repo
from git.exc import GitCommandError, UnsafeProtocolError
from git.cmd import Git

import tempfile
from datetime import datetime, timedelta
import logging
import os
from contextlib import contextmanager
from dataclasses import replace
from score.models import Source, License
from score.notes import Note
from .license_detection import identify_license
from .check_url import get_source_from_url
from .package_destinations import get_all_pypackage_names

one_year_ago = datetime.now() - timedelta(days=365)

log = logging.getLogger(__name__)


MAX_CLONE_TIME = 30

sparse_checkout = """
**/package.json
**/pyproject.toml
**/setup.cfg
**/setup.py
**/requirements.txt
**/LICENSE
**/LICENSE.txt
**/LICENSE.md
**/LICENSE.rst
**/COPYING
**/LICENCE
**/LICENCE.txt
**/LICENCE.md
**/LICENCE.rst

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


def create_git_metadata_str(url: str) -> Source:
    source = get_source_from_url(url)
    if source.error is not None:
        return source

    with clone_repo(url) as (repo, metadata):
        if repo is None:
            return metadata
        metadata = replace(metadata, **get_commit_metadata(repo, url))
        metadata.license = get_license_type(repo, url)
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
        "recent_authors_count": int(recent_authors_count),
        "max_monthly_authors_count": int(max_monthly_authors_count),
        "first_commit": commits.when.min(),
        "latest_commit": commits.when.max(),
    }


def get_license_type(repo: Repo, url: str) -> License:

    # Check if LICENSE or LICENSE.txt exists in the root directory
    paths = [
        "LICENSE",
        "LICENSE.txt",
        "LICENSE.md",
        "LICENSE.rst",
        "COPYING",
        "LICENCE",
        "LICENCE.txt",
        "LICENCE.md",
        "LICENCE.rst",
    ]
    license_file_path = None
    for path in paths:
        full_path = os.path.join(repo.working_dir, path)
        if os.path.isfile(full_path):
            license_file_path = full_path
            break

    if not license_file_path:
        return License(error=Note.NO_LICENSE)

    # Read and return the license type
    with open(license_file_path, encoding="utf8", errors="ignore") as license_file:
        license_content = license_file.read().strip()

    return identify_license(url, license_content)
