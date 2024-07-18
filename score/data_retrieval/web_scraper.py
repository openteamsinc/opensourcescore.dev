import requests
import pandas as pd
import re
import time
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from data_storage.csv_storage import save_to_csv
from data_storage.parquet_storage import save_to_parquet
from logger import setup_logger

logger = setup_logger()


def get_package_data(package_name):
    """
    Fetches package data by scraping the PyPI project page for a given package name.

    Args:
        package_name (str): The name of the package to fetch data for.

    Returns:
        dict: A dictionary containing filtered package data.
    """
    url = f"https://pypi.org/project/{package_name}/"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract the package summary
        summary_element = soup.find("p", class_="package-description__summary")
        summary = summary_element.text.strip() if summary_element else ""

        # Initialize package information dictionary
        package_info = {
            "name": package_name,
            "version": soup.find("h1").text.strip().split()[-1],
            "summary": summary,
            "author": "",
            "license": "",
            "maintainer": "",
            "maintainer_email": "",
            "requires": "",
            "dev_status": "",
            "first_release": "",
            "last_release": "",
            "releases": [],
            "monthly_downloads_pypi": "",
            "monthly_downloads_conda": "",
        }

        # Extract meta information from the sidebar section
        meta_section = None
        sidebar_sections = soup.find_all("div", class_="sidebar-section")
        for section in sidebar_sections:
            heading = section.find("h6")
            if heading and heading.text.strip().lower() == "meta":
                meta_section = section
                break

        if meta_section:
            for p in meta_section.find_all("p"):
                strong = p.find("strong")
                if strong:
                    label = strong.text.strip().lower()
                    if "license" in label:
                        package_info["license"] = p.text.replace(
                            strong.text, ""
                        ).strip()
                    elif "author" in label:
                        package_info["author"] = p.text.replace(strong.text, "").strip()
                    elif "maintainer" in label:
                        maintainer_info = p.text.replace(strong.text, "").strip()
                        package_info["maintainer"] = maintainer_info
                        email_link = p.find("a", href=True)
                        if email_link and "mailto:" in email_link["href"]:
                            package_info["maintainer_email"] = (
                                email_link["href"].replace("mailto:", "").strip()
                            )
                    elif "requires" in label:
                        package_info["requires"] = p.text.replace(
                            strong.text, ""
                        ).strip()

        # Extract classifiers (Development Status)
        classifiers_section = soup.find("ul", class_="sidebar-section__classifiers")
        if classifiers_section:
            for classifier in classifiers_section.find_all("li"):
                text = classifier.text.strip()
                if "Development Status" in text:
                    package_info["dev_status"] = text

        extract_release_history(url, soup, package_info)

        # Extract monthly downloads from image URLs based on alt text
        images = soup.find_all("img")
        for img in images:
            alt_text = img.get("alt", "")
            src = img.get("src", "")
            if "PyPI Downloads" in alt_text:
                package_info["monthly_downloads_pypi"] = extract_downloads_from_svg(src)
            elif "Conda Downloads" in alt_text:
                package_info["monthly_downloads_conda"] = extract_downloads_from_svg(
                    src
                )

        return package_info
    except requests.RequestException as e:
        logger.error(f"Failed to retrieve data for package {package_name}: {e}")
        return None


def get_all_package_names():
    """
    Fetches the list of all package names from the PyPI Simple API.

    Returns:
        list: A list of all package names.
    """
    url = "https://pypi.org/simple/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Extract package names from the HTML response
        package_names = re.findall(r'<a href="/simple/([^/]+)/">', response.text)
        return package_names
    except requests.RequestException as e:
        print(f"Failed to retrieve the list of all packages: {e}")
        return []


def scrape_web(config):
    """
    Initiates the scraping process by scraping the web pages based on the given configuration.

    Args:
        config (dict): Configuration dictionary containing scraping parameters.
    """
    package_names = get_all_package_names()
    letters = config["letters"]

    # Use a ThreadPoolExecutor to parallelize the scraping process by letters
    with ThreadPoolExecutor(max_workers=26) as executor:
        futures = [
            executor.submit(process_packages_by_letter, letter, package_names, config)
            for letter in letters
        ]

        for future in as_completed(futures):
            future.result()


def process_packages_by_letter(letter, package_names, config):
    """
    Processes and saves package data for packages starting with a specific letter.

    Args:
        letter (str): The letter to filter package names by.
        package_names (list): List of all package names.
        config (dict): Configuration dictionary containing output parameters.
    """
    # Filter package names that start with the specified letter
    letter_package_names = [name for name in package_names if name[0].lower() == letter]

    for package_name in tqdm(letter_package_names, desc=f"Processing letter {letter}"):
        # Fetch and process package data
        package_data = get_package_data(package_name)
        if package_data:
            df = pd.DataFrame([package_data])
            # Save data to CSV if specified in the config
            if config["output_format"] in [1, 3]:
                save_to_csv(df, letter)
            # Save data to Parquet if specified in the config
            if config["output_format"] in [2, 3]:
                save_to_parquet(df, letter, config["entries_per_parquet"])


def extract_downloads_from_svg(svg_url, retries=3, delay=2):
    """
    Extracts download numbers from an SVG image by parsing the SVG content.

    Args:
        svg_url (str): The URL of the SVG image.
        retries (int): The number of retry attempts if the request fails.
        delay (int): The delay between retry attempts.

    Returns:
        str: The extracted download number.
    """
    attempt = 0
    while attempt < retries:
        try:
            print(f"Attempt {attempt + 1} to retrieve SVG from {svg_url}")
            response = requests.get(svg_url, timeout=5)
            response.raise_for_status()
            svg_content = response.text
            match = re.search(
                r"(\d[\d,]*[KM]?\s*/\s*month|\d[\d,]*[KM]?|\d+)\s*</text>", svg_content
            )
            if match:
                print(f"Match found: {match.group(1)}")
                return match.group(1).replace(",", "").replace("/month", "")
            else:
                print("No match found in SVG content.")
        except requests.RequestException as e:
            print(f"Failed to retrieve SVG from {svg_url}: {e}")
        attempt += 1
        if attempt < retries:
            print(f"Retrying... ({attempt}/{retries})")
            time.sleep(delay)
        else:
            print(f"Exceeded maximum retries ({retries}) for {svg_url}")
            return ""
    return ""


def extract_release_history(current_url, soup, package_info):
    """
    Extracts the release history for a given package from its PyPI project page.

    Args:
        current_url (str): The URL of the current package's project page.
        soup (BeautifulSoup): The BeautifulSoup object containing the parsed HTML of the project page.
        package_info (dict): The dictionary to store the extracted release history information.

    Returns:
        None
    """
    try:
        # Find the link to the history section
        history_link = soup.find("a", id="history-tab")
        if not history_link:
            return

        # Construct the full URL to the history section
        history_url = (
            f"{current_url.rstrip('/')}/{history_link.get('href').lstrip('/')}"
        )

        # Fetch the history page
        response = requests.get(history_url, timeout=10)
        response.raise_for_status()
        history_soup = BeautifulSoup(response.text, "html.parser")

        # Find the history section in the fetched HTML
        releases_section = history_soup.find("div", {"id": "history"})
        if not releases_section:
            return

        # Find all release cards within the history section
        release_cards = releases_section.find_all("a", class_="card release__card")

        # Initialize a list to hold the release history information
        release_history = []
        for card in release_cards:
            # Extract the release version and release date elements
            release_version_element = card.find("p", class_="release__version")
            release_date_element = card.find("p", class_="release__version-date")

            if release_version_element and release_date_element:
                # Extract the datetime element within the release date element
                release_date_time_element = release_date_element.find("time")
                if release_date_time_element:
                    release_version = release_version_element.text.strip()
                    release_date = release_date_time_element["datetime"]
                    release_info = {"version": release_version, "date": release_date}
                    release_history.append(release_info)

        # Update the package_info dictionary with the release history
        package_info["releases"] = release_history
        if release_history:
            # Set the first and last release dates in the package_info dictionary
            package_info["first_release"] = release_history[-1]["date"]
            package_info["last_release"] = release_history[0]["date"]

    except Exception as e:
        print(f"Failed to extract release history: {e}")
