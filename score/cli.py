import click
import string
import os
from pathlib import Path
from .logger import setup_logger
from .data_retrieval.json_scraper import scrape_json
from .data_retrieval.web_scraper import scrape_web
from .utils.github_aggregator import aggregate
from .data_retrieval.github_scraper import scrape_github_data
from .utils.get_pypi_package_list import get_pypi_package_names

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
    "-n",
    "--num-partitions",
    required=True,
    type=int,
    help="The number of partitions in total.",
)
@click.option(
    "-p",
    "--partition",
    required=True,
    type=int,
    help="The partition number to process.",
)
def scrape_pypi(num_partitions, partition, output):
    packages = get_pypi_package_names(num_partitions, partition)
    click.echo(
        f"Will process {len(packages)} packages in partition {partition} of {num_partitions}"
    )

    df = scrape_json(packages)
    df["partition"] = partition

    click.echo(f"Saving data to {output}")
    df.to_parquet(output, partition_cols=["partition"])
    click.echo("Scraping completed.")


@cli.command()
@click.option(
    "--output",
    default=OUTPUT_ROOT / "output" / "pypi-web",
    help="The output directory to save the scraped data in hive partition",
)
@click.option(
    "-n",
    "--num-partitions",
    required=True,
    type=int,
    help="The number of partitions in total.",
)
@click.option(
    "-p",
    "--partition",
    required=True,
    type=int,
    help="The partition number to process.",
)
def scrape_pypi_web(num_partitions, partition, output):
    packages = get_pypi_package_names(num_partitions, partition)
    click.echo(
        f"Will process {len(packages)} packages in partition {partition} of {num_partitions}"
    )

    df = scrape_web(packages)
    df["partition"] = partition

    click.echo(f"Saving data to {output}")
    df.to_parquet(output, partition_cols=["partition"])
    click.echo("Scraping completed.")


@cli.command()
@click.option(
    "--output",
    default=OUTPUT_ROOT / "output" / "github-urls",
    help="The output directory to save the aggregated data",
)
@click.option(
    "--input",
    default=OUTPUT_ROOT / "output" / "pypi-json",
    help="The input directory to read the data from",
)
@click.option(
    "--start",
    required=True,
    type=str,
    callback=validate_input,
    help="Enter the starting letter or number to scrape (e.g., 'a' or '0').",
)
@click.option(
    "--end",
    required=True,
    type=str,
    callback=validate_input,
    help="Enter the ending letter or number to scrape (e.g., 'c' or '9').",
)
def github_aggregate(start, end, input, output):
    all_chars = string.digits + string.ascii_lowercase
    start_index = all_chars.index(start)
    end_index = all_chars.index(end)

    letters_to_scrape = get_letter_range(start_index, end_index)

    click.echo(f"Aggregating all data starting with characters {letters_to_scrape}.")

    aggregate(input, output, letters_to_scrape)
    click.echo("Aggregation completed.")


@cli.command()
@click.option(
    "--start",
    required=True,
    type=str,
    callback=validate_input,
    help="Enter the starting letter or number to scrape (e.g., 'a' or '0').",
)
@click.option(
    "--end",
    required=True,
    type=str,
    callback=validate_input,
    help="Enter the ending letter or number to scrape (e.g., 'c' or '9').",
)
@click.option(
    "--output",
    default=OUTPUT_ROOT / "output" / "github-detailed",
    help="The output directory to save the detailed GitHub data",
)
def scrape_github(start, end, output):
    all_chars = string.digits + string.ascii_lowercase
    start_index = all_chars.index(start)
    end_index = all_chars.index(end)

    letters_to_scrape = get_letter_range(start_index, end_index)

    click.echo(f"Scraping GitHub data for characters {letters_to_scrape}.")

    input_dir = OUTPUT_ROOT / "output" / "github-urls"
    scrape_github_data(input_dir, output, letters_to_scrape)

    click.echo("Scraping completed.")


if __name__ == "__main__":
    cli()
