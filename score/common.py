import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup


def requests_get(url: str, headers: dict = {}) -> requests.models.Response:
    """
    Fetch the URL and return the response object

    Args:
        url (str): URL to fetch the data
        headers (dict): Headers to send with the request

    Returns:
        response / None (requests.models.Response): Response object
    """
    response = requests.get(url, headers)
    if response.status_code == 200:
        return response
    else:
        logging.error(
            f"Failed to fetch URL: {url} with status code: {response.status_code} | {response.text}"
        )
        return None


def get_requests_soup(url: str, headers: dict = {}) -> BeautifulSoup:
    """
    Fetch the URL and return the BeautifulSoup object

    Args:
        url (str): URL to fetch the data
        headers (dict): Headers to send with the request

    Returns:
        BeautifulSoup / None: BeautifulSoup object
    """
    response = requests_get(url, headers)
    if response:
        return BeautifulSoup(response.text, "html.parser")
    else:
        return None


def json_to_parquet(json_data: dict, parquet_file_path: str) -> None:
    """
    Convert the JSON data to Parquet file

    Args:
        json_data (dict): JSON data to save
        parquet_file_path (str): Path to save the Parquet file

    Returns:
        None
    """
    df = pd.DataFrame(json_data)
    df.to_parquet(parquet_file_path)
    logging.info(f"Data saved to Parquet file: {parquet_file_path}")
