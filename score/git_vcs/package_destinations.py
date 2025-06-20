import configparser
import json
import logging
import os
import re
from typing import Iterable, Optional, Tuple

import tomli
from git import Repo

log = logging.getLogger(__name__)


def pypi_normalize(name):
    if not name:
        return None

    return re.sub(r"[-_.]+", "-", name).lower()


def checkout_suffix(repo: Repo, suffix: str):

    all_files_output: str = repo.git.ls_tree("-r", "--name-only", "--full-name", "HEAD")
    all_filespaths = [f.strip() for f in all_files_output.split("\n")]
    filepaths = [f for f in all_filespaths if f == suffix or f.endswith(f"/{suffix}")]
    log.info(f"Found {len(filepaths)} files with suffix {suffix}")
    if not filepaths:
        return []

    filepaths.sort(key=len)

    return [os.path.join(repo.working_dir, f) for f in filepaths]


def get_pyproject_tomls(repo: Repo):
    return checkout_suffix(repo, "pyproject.toml")


def get_setup_configs(repo: Repo):
    return checkout_suffix(repo, "setup.cfg")


def get_setup_pys(repo: Repo):
    return checkout_suffix(repo, "setup.py")


def get_npm_package_json(repo: Repo):
    return checkout_suffix(repo, "package.json")


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

    if not isinstance(data, dict):
        log.error("Invalid json format")
        return None, None
    if not data.get("name"):
        log.error("Invalid package.json no key 'name'")
        return None, None
    return data["name"], full_path.replace(str(repo.working_dir), "")


def get_npm_pypackage_names(repo: Repo):
    full_paths = get_npm_package_json(repo)
    log.info(f"Found {len(full_paths)} package.json files")
    for full_path in full_paths:
        name, source_file = read_npm_package_json(repo, full_path)
        if name and source_file:
            yield f"npm/{name}", source_file


def python_typeshed_special_case(repo: Repo):
    for full_path in checkout_suffix(repo, "METADATA.toml"):
        stub_path = full_path.replace(str(repo.working_dir), "")
        if not stub_path.startswith("/stubs"):
            continue
        name = stub_path[7:-14]
        yield f"pypi/types-{name}", stub_path
    return


def get_pypi_pypackage_names(repo: Repo):
    full_paths = get_pyproject_tomls(repo)
    found_names = False
    log.info(f"Found {len(full_paths)} pyproject.toml files")
    for full_path in full_paths:
        name, source_file = read_pypi_toml(repo, full_path)
        if name and source_file:
            found_names = True
            yield f"pypi/{name}", source_file

            if name == "typeshed":
                yield from python_typeshed_special_case(repo)

    full_paths = get_setup_configs(repo)
    log.info(f"Found {len(full_paths)} setup.cfg files")
    for full_path in full_paths:
        name, source_file = read_setup_cfg(repo, full_path)
        if name and source_file:
            found_names = True
            yield f"pypi/{name}", source_file

    if found_names:
        return

    full_paths = get_setup_pys(repo)
    log.info(f"Found {len(full_paths)} setup.py files")
    for full_path in full_paths:
        name, source_file = read_setup_py(repo, full_path)
        if name and source_file:
            found_names = True
            yield f"pypi/{name}", source_file

    return


def get_all_pypackage_names(repo: Repo) -> Iterable[Tuple[str, str]]:
    yield from get_pypi_pypackage_names(repo)
    yield from get_npm_pypackage_names(repo)
