import click
import threading
from data_retrieval.json_scraper import scrape_json
from data_retrieval.web_scraper import scrape_web
from logger import setup_logger


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
