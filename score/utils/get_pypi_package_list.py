import re
from hashlib import sha256

import requests

PYPI_URL = "https://pypi.org/simple/"


def get_all_pypi_package_names():
    """
    Fetches the list of all package names from the PyPI Simple API.

    Returns:
        list: A list of all package names.
    """

    response = requests.get(PYPI_URL, timeout=10)
    response.raise_for_status()  # Raise an error for bad status codes
    package_names = re.findall(
        r'<a href="/simple/([^/]+)/">', response.text
    )  # Extract package names
    return package_names


def get_pypi_package_names(num_partitions: int, partition: int):
    all_packages = get_all_pypi_package_names()

    def is_in_partition(name: str):
        package_hash = sha256(name.encode()).hexdigest()
        return (int(package_hash, base=16) % num_partitions) == partition

    return [p for p in all_packages if is_in_partition(p)]
