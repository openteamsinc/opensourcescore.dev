import click
import os
import duckdb
from .logger import setup_logger
from .data_retrieval.json_scraper import scrape_json
from .data_retrieval.web_scraper import scrape_web
from .utils.github_aggregator import aggregate
from .data_retrieval.github_scraper import scrape_github_data
from .utils.get_pypi_package_list import get_pypi_package_names
from .conda.get_conda_package_names import get_conda_package_names
from .conda.scrape_conda import scrape_conda

OUTPUT_ROOT = os.environ.get("OUTPUT_ROOT", "./output")


partition_option = click.option(
    "-p",
    "--partition",
    default=lambda: os.environ.get("SCORE_PARTITION"),
    required=True,
    type=int,
    help="The partition number to process.",
)

num_partitions_option = click.option(
    "-n",
    "--num-partitions",
    required=True,
    default=lambda: os.environ.get("SCORE_NUM_PARTITIONS"),
    type=int,
    help="The number of partitions in total.",
)


@click.group()
def cli():
    setup_logger()


@cli.command()
@click.option(
    "--output",
    default=os.path.join(OUTPUT_ROOT, "pypi-json"),
    help="The output directory to save the scraped data in hive partition",
)
@partition_option
@num_partitions_option
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
    default=os.path.join(OUTPUT_ROOT, "pypi-web"),
    help="The output directory to save the scraped data in hive partition",
)
@partition_option
@num_partitions_option
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
    "-o" "--output",
    default=OUTPUT_ROOT / "output" / "github-urls",
    help="The output directory to save the aggregated data",
)
@click.option(
    "-i" "--input",
    default=OUTPUT_ROOT / "output" / "pypi-json",
    help="The input directory to read the data from",
)
@click.option(
    "-p",
    "--partition",
    required=True,
    type=int,
    help="The partition number to scrape.",
)
def github_aggregate(partition, input, output):
    click.echo(f"Aggregating data for partition {partition}.")

    aggregate(input, output, partition)
    click.echo("Aggregation completed.")


@cli.command()
@click.option(
    "-p",
    "--partition",
    required=True,
    type=int,
    help="The partition number to scrape.",
)
@click.option(
    "-o",
    "--output",
    default=OUTPUT_ROOT / "output" / "github-details",
    help="The output directory to save the detailed GitHub data",
)
def scrape_github(partition, output):
    click.echo(f"Scraping GitHub data for partition {partition}.")

    input_dir = OUTPUT_ROOT / "output" / "github-urls"

    df = scrape_github_data(input_dir, partition)
    df["partition"] = partition

    click.echo(f"Saving data to {output}")
    df.to_parquet(output, partition_cols=["partition"])


@cli.command()
@click.option(
    "--output",
    default=os.path.join(OUTPUT_ROOT, "conda"),
    help="The output directory to save the scraped data in hive partition",
)
@click.option(
    "-c",
    "--channel",
    default="conda-forge",
    help="The conda channel to scrape packages from",
)
@partition_option
@num_partitions_option
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
