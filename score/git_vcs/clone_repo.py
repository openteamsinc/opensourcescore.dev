import logging
import os
import shutil
import tempfile
import time
from contextlib import contextmanager
from typing import Tuple

from git import Repo
from git.cmd import Git
from git.exc import GitCommandError, UnsafeProtocolError

from score.models import Source
from score.notes import Note

log = logging.getLogger(__name__)


MAX_CLONE_TIME = 30

NOT_A_LICENSE_FILE_EXT = [".json", ".csv", ".svg", ".jpg", ".jpeg"]
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


def git_command_error(
    url: str, err: GitCommandError, source: Source
) -> Tuple[None, Source]:
    if err.status == 128:
        if "not found" in err.stderr.lower():
            source.error = Note.NO_SOURCE_REPO_NOT_FOUND
            return None, source
        if "could not read username for" in err.stderr.lower():
            source.error = Note.NO_SOURCE_PRIVATE_REPO
            return None, source
        else:
            log.error(f"{url}: {err.status}: {repr(err.stderr)}")
            source.error = Note.NO_SOURCE_OTHER_GIT_ERROR
            return None, source

    if err.status == -9 and "timeout:" in err.stderr.lower():
        raise TimeoutError(f"Timeout while cloning {url}")

    log.error(f"{url}: {err.status}: {err.stderr}")
    source.error = Note.NO_SOURCE_OTHER_GIT_ERROR
    return None, source


def cleanup(repo: Repo | None, tmpdir: str | None):
    if repo is not None:
        try:
            repo.close()
        except Exception as e:
            log.error(f"Error closing repo: {e}")
    else:
        log.info("No repo to close")
    # Clean up the temporary directory
    if tmpdir is not None:
        try:
            shutil.rmtree(tmpdir)
        except OSError as e:
            log.error(f"Error removing temporary directory {tmpdir}: {e}")


@contextmanager
def clone_repo(url: str):
    log.info(f"Cloning {url}")
    source = Source(package_destinations=[], source_url=url)
    tmpdir = None
    repo = None

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

        except UnsafeProtocolError:
            source.error = Note.NO_SOURCE_UNSAFE_GIT_PROTOCOL
            repo = None
        except GitCommandError as err:
            repo, source = git_command_error(url, err, source)

        try:
            yield repo, source
        finally:
            cleanup(repo, tmpdir)
