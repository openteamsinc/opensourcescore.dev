import requests
import re


def input_formatter(letters_str):
    """
    Formats an input string into a sorted set of letters and digits.
    Allows for the scraper to scrape specific ranges of letters.

    Args:
        letters_str (str): A string containing ranges or individual characters (e.g., "a-d,0-3").

    Returns:
        str: A sorted string of individual characters representing the input ranges.
    """
    letters = set()
    if not letters_str:
        letters_str = "0-9,a-z"  # Default range if no input is provided
    for part in letters_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            start, end = start.strip(), end.strip()
            if start.isdigit() and end.isdigit():
                # Add all digits in the specified range to the set
                letters.update(str(i) for i in range(int(start), int(end) + 1))
            elif start.isalpha() and end.isalpha():
                # Add all letters in the specified range to the set
                letters.update(chr(i) for i in range(ord(start), ord(end) + 1))
        else:
            # Add individual characters to the set
            letters.add(part)
    return "".join(sorted(letters))


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
