import json
from hashlib import sha256
from typing import List, Tuple

from ..utils.request_session import get_session

NPM_PACKAGE_URL = "https://replicate.npmjs.com/_all_docs"


def fetch_npm_package_names(
    limit: int = 1000, start_key: str = None, end_key: str = None
) -> Tuple[List[str], str]:
    params = {"limit": limit, "include_docs": False}
    if start_key:
        params["startkey"] = json.dumps(start_key)
    if end_key:
        params["endkey"] = json.dumps(end_key)
    s = get_session()
    res = s.get(NPM_PACKAGE_URL, params=params)
    res.raise_for_status()
    data = res.json()
    rows = data.get("rows", [])
    last_key = rows[-1]["id"] if rows else None
    return list({row["id"] for row in rows}), last_key


def get_all_npm_package_names() -> List[str]:
    all_package_names = []
    start_key = None
    end_key = None
    while True:
        package_names, start_key = fetch_npm_package_names(
            limit=1000, start_key=start_key, end_key=end_key
        )
        if not package_names:
            break
        all_package_names.extend(package_names)
        print(f"\rFound {len(set(all_package_names))} package names", end="")
    return list(set(all_package_names))


def get_npm_package_names(num_partitions: int, partition: int) -> List[str]:
    all_packages = get_all_npm_package_names()

    def is_in_partition(name: str):
        package_hash = sha256(name.encode()).hexdigest()
        return (int(package_hash, base=16) % num_partitions) == partition

    return [p for p in all_packages if is_in_partition(p)]
