import click
import os
from .logger import setup_logger
from .data_retrieval.json_scraper import scrape_json
from .data_retrieval.web_scraper import scrape_web
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
    default=os.path.join(OUTPUT_ROOT, "pypi-web"),
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
    "--output",
    default=os.path.join(OUTPUT_ROOT, "pypi-web"),
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


if __name__ == "__main__":
    cli()
