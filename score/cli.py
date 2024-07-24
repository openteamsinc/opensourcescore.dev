import click
import threading
from utils.common import input_formatter
from data_retrieval.json_scraper import scrape_json
from data_retrieval.web_scraper import scrape_web
from logger import setup_logger


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--letters",
    default="0-9,a-z",
    help="Enter letters to scrape (e.g., 'a-c' or 'a,b,c,0-9'). Leave empty for all letters",
)
def scrape_pypi(letters):
    letters_to_scrape = input_formatter(letters)

    # Prepare the config
    config = {"letters": letters_to_scrape}

    setup_logger()
    scrape_json(config)
    click.echo("Scraping completed.")


@cli.command()
@click.option(
    "--letters",
    default="0-9,a-z",
    help="Enter letters to scrape (e.g., 'a-c' or 'a,b,c,0-9'). Leave empty for all letters",
)
def scrape_pypi_web(letters):
    letters_to_scrape = input_formatter(letters)

    # Prepare the config
    config = {"letters": letters_to_scrape}

    setup_logger()
    scrape_web(config)
    click.echo("Scraping completed.")


@cli.command()
@click.option(
    "--letters",
    default="0-9,a-z",
    help="Enter letters to scrape (e.g., 'a-c' or 'a,b,c,0-9'). Leave empty for all letters",
)
def scrape_pypi_both(letters):
    letters_to_scrape = input_formatter(letters)

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


if __name__ == "__main__":
    cli()
