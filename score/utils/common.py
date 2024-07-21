import os
import requests
import re
import pandas as pd


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


def input_formatter(letters_str):
    letters = set()
    if not letters_str:
        letters_str = "0-9,a-z"
    for part in letters_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            start, end = start.strip(), end.strip()
            if start.isdigit() and end.isdigit():
                letters.update(str(i) for i in range(int(start), int(end) + 1))
            elif start.isalpha() and end.isalpha():
                letters.update(chr(i) for i in range(ord(start), ord(end) + 1))
        else:
            letters.add(part)
    return "".join(sorted(letters))


def ensure_output_dir():
    if not os.path.exists("output"):
        os.makedirs("output")


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
