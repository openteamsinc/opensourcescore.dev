import os
import string
from pathlib import Path

import click

from .conda import scrape_conda
from .data_retrieval.json_scraper import scrape_json
from .data_retrieval.web_scraper import scrape_web
from .logger import setup_logger

# from .data_retrieval.github_scraper import scrape_github_data

OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "."))


def validate_input(ctx, param, value):
    if not (
        value.isdigit() or (len(value) == 1 and value.isalpha() and value.islower())
    ):
        raise click.BadParameter(
            f"{value} is not a valid input. Please enter a single letter (a-z) or number (0-9)."
        )
    return value


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
    return list(all_chars[start : end + 1])


@click.group()
def cli():
    setup_logger()


@cli.command()
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


@cli.command()
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

    scrape_web(output, letters_to_scrape)
    click.echo("Scraping completed.")


@cli.command()
@click.option(
    "--output",
    default=OUTPUT_ROOT / "output" / "conda-json",
    help="The output directory to save the scraped data in hive partition",
)
@click.option(
    "--letter_to_scrape",
    "-l",
    required=True,
    help="Enter the starting letter or number to scrape (e.g., 'a' or '0').",
)
def conda(output, letter_to_scrape):
    click.echo(
        f"Will process all packages starting with characters {letter_to_scrape}."
    )
    scrape_conda(output, letter_to_scrape)
    click.echo("Scraping completed.")


if __name__ == "__main__":
    cli()
