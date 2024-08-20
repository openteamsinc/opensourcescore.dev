import json
import logging
import multiprocessing
import os
from hashlib import sha256
from typing import List, Tuple

from ..utils.request_session import get_session

log = logging.getLogger(__name__)

NPM_PACKAGE_URL = "https://replicate.npmjs.com/_all_docs"

NPM_PACKAGE_NAMES_FILE = "npm_package_names.json"


def save_npm_package_names_to_file(all_packages: List[str]) -> None:
    with open(NPM_PACKAGE_NAMES_FILE, "w") as f:
        json.dump(all_packages, f)


def load_npm_package_names_from_file() -> List[str]:
    if not os.path.exists(NPM_PACKAGE_NAMES_FILE):
        with open(NPM_PACKAGE_NAMES_FILE, "w") as f:
            f.write("[]")
        print(f"Created file: {NPM_PACKAGE_NAMES_FILE}")
        return []

    with open(NPM_PACKAGE_NAMES_FILE, "r") as f:
        all_packages = json.load(f)
        return all_packages


def fetch_npm_package_names(limit: int, start_key: str = None) -> Tuple[List[str], str]:
    params = {"limit": limit, "include_docs": False}
    if start_key:
        params["startkey"] = json.dumps(start_key)
    s = get_session()
    res = s.get(NPM_PACKAGE_URL, params=params)
    res.raise_for_status()
    data = res.json()
    rows = data.get("rows", [])
    last_key = rows[-1]["id"] if rows else None
    return list({row["id"] for row in rows}), last_key


def get_all_npm_package_names() -> List[str]:
    all_package_names = []
    existing_packages = load_npm_package_names_from_file()
    start_key = existing_packages[-1] if existing_packages else None
    while True:
        package_names, start_key = fetch_npm_package_names(
            limit=100000, start_key=start_key
        )
        if not package_names:
            break
        all_package_names = list(set(existing_packages + package_names))
        save_npm_package_names_to_file(all_package_names)
        print(f"Found {len(all_package_names)} package names")
    return all_package_names


def run_process():
    # Create processes for fetching all npm package names
    fetch_process = multiprocessing.Process(target=get_all_npm_package_names)
    fetch_process.start()

    # load all packages from file whichever is available
    all_packages = load_npm_package_names_from_file()

    return all_packages


def get_npm_package_names(num_partitions: int, partition: int) -> List[str]:
    all_packages = run_process()

    def is_in_partition(name: str):
        package_hash = sha256(name.encode()).hexdigest()
        return (int(package_hash, base=16) % num_partitions) == partition

    return [p for p in all_packages if is_in_partition(p)]
