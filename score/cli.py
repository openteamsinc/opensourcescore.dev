import click
import threading
from config import load_config, save_config, ensure_output_dir
from data_retrieval.json_scraper import scrape_json
from data_retrieval.web_scraper import scrape_web
from logger import setup_logger


def parse_letters(letters_str):
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


@click.command()
def run_cli():
    # Ask for scraping method
    method = click.prompt(
        "Choose scraping method:\n1. JSON API\n2. Web Scraper\n3. Both",
        type=int,
        default=3,
    )

    # Ask for output format
    output_format = click.prompt(
        "Choose output format:\n1. CSV\n2. Parquet\n3. Both", type=int, default=3
    )

    # If Parquet or Both is chosen, ask for entries per Parquet file
    entries_per_parquet = None
    if output_format in [2, 3]:
        entries_per_parquet = click.prompt(
            "Enter the number of entries per Parquet file", type=int, default=1000
        )

    # Ask for letters to scrape
    letters = click.prompt(
        "Enter letters to scrape (e.g., 'a-c' or 'a,b,c,0-9'). Leave empty for all letters",
        type=str,
        default="0-9,a-z",
    )
    parsed_letters = parse_letters(letters)

    # Save config
    config = load_config()
    config["method"] = method
    config["output_format"] = output_format
    config["entries_per_parquet"] = entries_per_parquet
    config["letters"] = parsed_letters
    save_config(config)

    ensure_output_dir()
    setup_logger()

    if method == 1:
        scrape_json(config)
    elif method == 2:
        scrape_web(config)
    elif method == 3:
        # Run both scrapers simultaneously using threading
        json_thread = threading.Thread(target=scrape_json, args=(config,))
        web_thread = threading.Thread(target=scrape_web, args=(config,))
        json_thread.start()
        web_thread.start()
        json_thread.join()
        web_thread.join()

    click.echo("Scraping completed.")


if __name__ == "__main__":
    run_cli()
