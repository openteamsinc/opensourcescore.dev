import click
import threading
from data_retrieval.json_scraper import scrape_json
from data_retrieval.web_scraper import scrape_web
from Score.score.data_retrieval.github_scraper import scrape_github_data
from logger import setup_logger


def get_letter_range(start, end):
    """
    Generates a list of characters from start to end inclusive, supporting both numbers and letters.

    Args:
        start (str): The starting character (letter or number).
        end (str): The ending character (letter or number).

    Returns:
        list: A list of characters from start to end.
    """
    all_chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    start_index = all_chars.index(start.lower())
    end_index = all_chars.index(end.lower()) + 1
    return list(all_chars[start_index:end_index])


@click.group()
def cli():
    pass


@cli.command()
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
def scrape_pypi(start, end):
    letters_to_scrape = get_letter_range(start, end)

    # Prepare the config
    config = {"letters": letters_to_scrape}

    setup_logger()
    scrape_json(config)
    click.echo("Scraping completed.")


@cli.command()
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
def scrape_pypi_web(start, end):
    letters_to_scrape = get_letter_range(start, end)

    # Prepare the config
    config = {"letters": letters_to_scrape}

    setup_logger()
    scrape_web(config)
    click.echo("Scraping completed.")


@cli.command()
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


@cli.command()
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
def scrape_github(start, end):
    letters_to_scrape = get_letter_range(start, end)

    # Prepare the config
    config = {"letters": letters_to_scrape}

    setup_logger()
    scrape_github_data(config)
    click.echo("Scraping completed.")


if __name__ == "__main__":
    cli()
