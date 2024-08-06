import os
import string
import subprocess
import threading
from pathlib import Path

import click

from .conda import scrape_conda_packages
from .data_retrieval.json_scraper import scrape_json
from .data_retrieval.web_scraper import scrape_web
from .logger import setup_logger

OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "."))


def get_letter_range(start: int, end: int):
    """
    Generates a list of characters from start to end inclusive, supporting both numbers and letters.

    Args:
        start (str): The starting character (letter or number).
        end (str): The ending character (letter or number).

    Returns:
        list: A list of characters from start to end.
    """
    all_chars = string.digits + string.ascii_lowercase
    return list(all_chars[start:end])


@click.group()
def main():
    pass


@main.command()
@click.option(
    "--output",
    default=OUTPUT_ROOT / "output" / "pypi-json",
    help="The output directory to save the scraped data in hive partition",
)
@click.option(
    "--start",
    required=True,
    type=int,
    help="Enter the starting letter or number to scrape (e.g., 'a' or '0').",
)
@click.option(
    "--end",
    required=True,
    type=int,
    help="Enter the ending letter or number to scrape (e.g., 'c' or '9').",
)
def scrape_pypi(start, end, output):
    letters_to_scrape = get_letter_range(start, end)
    click.echo(
        f"Will process all packages starting with characters {letters_to_scrape}."
    )
    scrape_json(output, letters_to_scrape)
    click.echo("Scraping completed.")


@main.command()
@click.option(
    "--output",
    default=OUTPUT_ROOT / "output" / "pypi-web",
    help="The output directory to save the scraped data in hive partition",
)
@click.option(
    "--start",
    required=True,
    type=int,
    help="Enter the starting letter or number to scrape (e.g., 'a' or '0').",
)
@click.option(
    "--end",
    required=True,
    type=int,
    help="Enter the ending letter or number to scrape (e.g., 'c' or '9').",
)
def scrape_pypi_web(start, end, output):
    letters_to_scrape = get_letter_range(start, end)
    click.echo(
        f"Will process all packages starting with characters {letters_to_scrape}."
    )

    # Prepare the config
    config = {"letters": letters_to_scrape}

    setup_logger()
    scrape_web(config)
    click.echo("Scraping completed.")


@main.command()
@click.option(
    "--start",
    required=True,
    help="Enter the starting letter or number to scrape (e.g., 'a' or '0').",
)
@click.option(
    "--end",
    required=True,
    help="Enter the ending letter or number to scrape (e.g., 'c' or '9').",
)
def scrape_pypi_both(start, end):
    letters_to_scrape = get_letter_range(start, end)

    # Prepare the config
    config = {"letters": letters_to_scrape}

    setup_logger()
    json_thread = threading.Thread(target=scrape_json, args=(config,))
    web_thread = threading.Thread(target=scrape_web, args=(config,))
    json_thread.start()
    web_thread.start()
    json_thread.join()
    web_thread.join()

    click.echo("Scraping completed.")


@main.command()
@click.option(
    "--letter_to_scrape",
    "-l",
    required=True,
    help="Enter the starting letter or number to scrape (e.g., 'a' or '0').",
)
def conda(letter_to_scrape):
    try:
        subprocess.run(["python", "score/conda.py"], check=True)
        scrape_conda_packages(letter_to_scrape)
        click.echo("Scraping completed.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error: {e}")


if __name__ == "__main__":
    main()
