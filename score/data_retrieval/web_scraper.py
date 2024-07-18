import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from data_storage.csv_storage import save_to_csv
from data_storage.parquet_storage import save_to_parquet
from logger import setup_logger

logger = setup_logger()

def get_package_data(package_name):
    url = f"https://pypi.org/project/{package_name}/"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        package_info = {
            'name': package_name,
            'version': soup.find('h1').text.strip().split()[-1],
            'summary': soup.find('p', class_='package-description__summary').text.strip() if soup.find('p', class_='package-description__summary') else '',
            'author': '',
            'license': '',
            'maintainer': '',
            'maintainer_email': '',
            'requires': '',
            'dev_status': '',
            'first_release': '',
            'last_release': '',
            'releases': [],
            'monthly_downloads_pypi': '',
            'monthly_downloads_conda': '',
            'github_stars': '',
            'github_forks': ''
        }

        # Extract other required fields...
        
        return package_info
    except requests.RequestException as e:
        logger.error(f"Failed to retrieve data for package {package_name}: {e}")
        return None

def get_all_package_names():
    url = "https://pypi.org/simple/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        package_names = re.findall(r'<a href="/simple/([^/]+)/">', response.text)
        return package_names
    except requests.RequestException as e:
        print(f"Failed to retrieve the list of all packages: {e}")
        return []

def scrape_web(config):
    package_names = get_all_package_names()
    letters = config['letters']

    with ThreadPoolExecutor(max_workers=26) as executor:
        futures = [executor.submit(process_packages_by_letter, letter, package_names, config) for letter in letters]

        for future in as_completed(futures):
            future.result()

def process_packages_by_letter(letter, package_names, config):
    letter_package_names = [name for name in package_names if name[0].lower() == letter]
    
    for package_name in tqdm(letter_package_names, desc=f"Processing letter {letter}"):
        package_data = get_package_data(package_name)
        if package_data:
            df = pd.DataFrame([package_data])
            if config['output_format'] in [1, 3]:
                save_to_csv(df, letter)
            if config['output_format'] in [2, 3]:
                save_to_parquet(df, letter, config['entries_per_parquet'])
