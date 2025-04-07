from typing import Any

import numpy as np
from cachetools import cached, TTLCache
from .pypi.json_scraper import get_package_data as get_pypi_package_data
from .conda.scrape_conda import get_conda_package_data
from .npm.scrape_npm import get_npm_package_data
from .git_vcs.scrape import create_git_metadata_str
from .vulnerabilities.scrape_vulnerabilities import scrape_vulnerability

max_age = 60 * 60
get_pypi_package_data_cached = cached(cache=TTLCache(maxsize=2**18, ttl=max_age))(
    get_pypi_package_data
)

get_conda_package_data_cached = cached(cache=TTLCache(maxsize=2**18, ttl=max_age))(
    get_conda_package_data
)
get_npm_package_data_cached = cached(cache=TTLCache(maxsize=2**18, ttl=max_age))(
    get_npm_package_data
)

create_git_metadata_cached = cached(cache=TTLCache(maxsize=2**18, ttl=max_age))(
    create_git_metadata_str
)

get_vuln_data_cached = cached(cache=TTLCache(maxsize=2**18, ttl=max_age))(
    scrape_vulnerability
)


@cached(cache=TTLCache(maxsize=2**18, ttl=max_age))
def get_package_data_cached(ecosystem: str, *args):
    if ecosystem == "pypi":
        return get_pypi_package_data(*args)
    if ecosystem == "conda":
        return get_conda_package_data(*args)
    if ecosystem == "npm":
        return get_npm_package_data(*args)


get_conda_package_data_cached = cached(cache=TTLCache(maxsize=2**18, ttl=max_age))(
    get_conda_package_data
)
get_npm_package_data_cached = cached(cache=TTLCache(maxsize=2**18, ttl=max_age))(
    get_npm_package_data
)

create_git_metadata_cached = cached(cache=TTLCache(maxsize=2**18, ttl=max_age))(
    create_git_metadata_str
)


def convert_numpy_types(obj: Any) -> Any:
    # Handle numpy types
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()

    # Handle nested dictionaries
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}

    # Handle lists, tuples, and other iterables
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(convert_numpy_types(item) for item in obj)

    return obj
