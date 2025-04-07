import tomli
import json
import configparser
from typing import Optional, Tuple
from git import Repo
from git.exc import GitCommandError
import logging

import re
import glob

log = logging.getLogger(__name__)


def pypi_normalize(name):
    if not name:
        return None

    return re.sub(r"[-_.]+", "-", name).lower()


def checkout_and_read_file(repo: Repo, suffix: str):
    try:
        repo.git.checkout(repo.active_branch, "--", suffix)
    except GitCommandError:
        try:
            repo.git.checkout(repo.active_branch, "--", f"**/{suffix}")
        except GitCommandError:
            pass

    possible_paths = glob.glob(f"{repo.working_dir}/**/{suffix}", recursive=True)
    if not possible_paths:
        return []

    # Shortest path first
    possible_paths = sorted(possible_paths, key=lambda x: len(x))
    return possible_paths


def get_pyproject_tomls(repo: Repo):
    return checkout_and_read_file(repo, "pyproject.toml")


def get_setup_configs(repo: Repo):
    return checkout_and_read_file(repo, "setup.cfg")


def get_setup_pys(repo: Repo):
    return checkout_and_read_file(repo, "setup.py")


def get_npm_package_json(repo: Repo):
    return checkout_and_read_file(repo, "package.json")


def read_pypi_toml(repo: Repo, full_path: str) -> Tuple[Optional[str], Optional[str]]:
    def get_name(data):
        name = data.get("project", {}).get("name")
        if name:
            return name
        return data.get("tool", {}).get("poetry", {}).get("name")

    try:
        # Read and return the license type
        with open(full_path, "rb") as fd:
            data = tomli.load(fd)
    except FileNotFoundError:
        return None, None
    except (tomli.TOMLDecodeError, IndexError, IOError) as err:
        log.error(f"Error reading pyproject.toml: {err}")
        return None, None
    name = get_name(data)

    if not name:
        return None, None

    return pypi_normalize(name), full_path.replace(str(repo.working_dir), "")


def read_setup_cfg(repo: Repo, full_path: str) -> Tuple[Optional[str], Optional[str]]:
    config = configparser.ConfigParser()
    try:
        # Read and return the license type
        with open(full_path, encoding="utf8", errors="ignore") as fd:
            config.read_file(fd)
    except FileNotFoundError:
        return None, None
    except (configparser.Error, IndexError, IOError) as err:
        log.error(f"Error reading setup.cfg: {err}")
        return None, None

    if not config.has_option("metadata", "name"):
        return None, None

    name = config.get("metadata", "name")

    return pypi_normalize(name), full_path.replace(str(repo.working_dir), "")


def read_setup_py(repo: Repo, full_path: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        # Read and return the license type
        with open(full_path, encoding="utf8", errors="ignore") as fd:
            setup_code = fd.read()
    except FileNotFoundError:
        return None, None

    pattern = r"setup\(.*?name\s*=\s*(['\"])(.*?)\1"

    match = re.search(pattern, setup_code, re.DOTALL)
    if not match:
        return None, None

    name = match.group(2)
    return pypi_normalize(name), full_path.replace(str(repo.working_dir), "")


def read_npm_package_json(
    repo: Repo, full_path: str
) -> Tuple[Optional[str], Optional[str]]:
    try:
        # Read and return the license type
        with open(full_path, encoding="utf8", errors="ignore") as fd:
            data = json.load(fd)
    except FileNotFoundError:
        return None, None
    except Exception:
        log.error("Could not read json")
        return None, None

    if not data.get("name"):
        return None, None
    return data["name"], full_path.replace(str(repo.working_dir), "")


def get_npm_pypackage_names(repo: Repo):
    full_paths = get_npm_package_json(repo)
    log.info(f"Found {len(full_paths)} package.json files")
    for full_path in full_paths:
        name, source_file = read_npm_package_json(repo, full_path)
        if name:
            yield f"npm/{name}", source_file


def get_pypi_pypackage_names(repo: Repo):
    full_paths = get_pyproject_tomls(repo)
    found_names = False
    log.info(f"Found {len(full_paths)} pyproject.toml files")
    for full_path in full_paths:
        name, source_file = read_pypi_toml(repo, full_path)
        if name:
            found_names = True
            yield f"pypi/{name}", source_file

    full_paths = get_setup_configs(repo)
    log.info(f"Found {len(full_paths)} setup.cfg files")
    for full_path in full_paths:
        name, source_file = read_setup_cfg(repo, full_path)
        if name:
            found_names = True
            yield f"pypi/{name}", source_file

    if found_names:
        return

    full_paths = get_setup_pys(repo)
    log.info(f"Found {len(full_paths)} setup.py files")
    for full_path in full_paths:
        name, source_file = read_setup_py(repo, full_path)
        if name:
            found_names = True
            yield f"pypi/{name}", source_file

    return


def get_all_pypackage_names(repo: Repo):
    yield from get_pypi_pypackage_names(repo)
    yield from get_npm_pypackage_names(repo)
