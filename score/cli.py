import click
import string
import os
import duckdb
from pathlib import Path
from .logger import setup_logger
from .data_retrieval.json_scraper import scrape_json
from .data_retrieval.web_scraper import scrape_web
from .utils.get_pypi_package_list import get_pypi_package_names
from .conda.get_conda_package_names import get_conda_package_names
from .conda.scrape_conda import scrape_conda

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
    default=OUTPUT_ROOT / "output" / "conda",
    help="The output directory to save the scraped data in hive partition",
)
@click.option(
    "-c",
    "--channel",
    default="conda-forge",
    help="The conda channel to scrape packages from",
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
def conda(num_partitions, partition, output, channel):
    packages = get_conda_package_names(num_partitions, partition, channel)
    click.echo(
        f"Will process {len(packages)} packages in partition {partition} of {num_partitions}"
    )

    df = scrape_conda(channel, packages)
    df["partition"] = partition
    df["channel"] = channel

    click.echo(f"Saving data to {output}")
    df.to_parquet(output, partition_cols=["channel", "partition"])
    click.echo("Scraping completed.")


@cli.command()
@click.option(
    "-o",
    "--output",
    default=os.path.join(OUTPUT_ROOT, "github-urls.parquet"),
    help="The output path to save the aggregated data",
)
@click.option(
    "-i",
    "--input",
    default=OUTPUT_ROOT,
    help="The input directory to read the data from",
)
def agg_source_urls(input, output):
    click.echo("Aggregating data")

    db = duckdb.connect()
    # Public dataset / empty secret
    db.execute("CREATE SECRET (TYPE GCS);")

    df = db.query(
        f"""
    select distinct source_url from read_parquet('{input}/pypi-json/*/*.parquet');
    """
    ).df()
    df.to_parquet(output)
    click.echo("Aggregation completed.")


if __name__ == "__main__":
    cli()
