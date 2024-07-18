import os
import pandas as pd
import requests
import re


def get_next_parquet_filename(base_name, extension=".parquet"):
    index = 1
    dir_name = os.path.dirname(base_name)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    filename = os.path.join(
        dir_name, f"{os.path.basename(base_name)}_{index}{extension}"
    )
    while os.path.exists(filename):
        index += 1
        filename = os.path.join(
            dir_name, f"{os.path.basename(base_name)}_{index}{extension}"
        )
    return filename


def get_parquet_record_count(file_path):
    if os.path.exists(file_path):
        df = pd.read_parquet(file_path)
        return len(df)
    return 0


def get_all_package_names():
    """
    Fetches the list of all package names from the PyPI Simple API.

    Returns:
        list: A list of all package names.
    """
    url = "https://pypi.org/simple/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        package_names = re.findall(
            r'<a href="/simple/([^/]+)/">', response.text
        )  # Extract package names
        return package_names
    except requests.RequestException as e:
        print(f"Failed to retrieve the list of all packages: {e}")
        return []
