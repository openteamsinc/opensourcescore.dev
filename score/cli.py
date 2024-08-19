import os
import pandas as pd
import click
import duckdb

from .conda.get_conda_package_names import get_conda_package_names
from .conda.scrape_conda import scrape_conda
from .data_retrieval.json_scraper import scrape_json
from .data_retrieval.pypi_downloads import get_bulk_download_counts
from .logger import setup_logger
from .utils.get_pypi_package_list import get_pypi_package_names
from .vulnerabilities.scrape_vulnerabilities import scrape_vulnerabilities
from .git_vcs.get_git_urls import get_git_urls
from .git_vcs.scrape import scrape_git
from .score.maturity import build_maturity_score
from .score.health_risk import build_health_risk_score
from .score.packages import get_pypi_packages, get_conda_packages

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
    default=os.path.join(OUTPUT_ROOT, "pypi-downloads"),
    help="The output directory to save the download data in hive partition",
)
@num_partitions_option
def scrape_pypi_downloads(num_partitions, output):
    click.echo(
        f"Fetching download data from BigQuery and partitioning into {num_partitions} partitions..."
    )

    # Fetch the download data
    df = get_bulk_download_counts()

    # Determine partition assignments
    df["partition"] = (df.index.to_series().rank(method="first") - 1) % num_partitions

    # Save the DataFrame to the specified output with partitioning
    click.echo(f"Saving data to {output}")
    df.to_parquet(output, partition_cols=["partition"])
    click.echo(
        f"Download data fetching and saving into {num_partitions} partitions completed."
    )


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
    "--output",
    default=os.path.join(OUTPUT_ROOT, "vulnerabilities"),
    help="The output directory to save the scraped data in hive partition",
)
@click.option(
    "-e",
    "--ecosystem",
    default=os.environ.get("SCORE_ECOSYSTEM", "PyPI"),
    help="The ecosystem to scrape vulnerabilities for",
)
@partition_option
@num_partitions_option
def vulnerabilities(num_partitions, partition, output, ecosystem):
    if ecosystem == "PyPI":
        packages = get_pypi_package_names(num_partitions, partition)
    else:
        raise ValueError(f"Unsupported ecosystem: {ecosystem}")

    click.echo(
        f"Will process {len(packages)} packages in partition {partition} of {num_partitions}"
    )

    df = scrape_vulnerabilities(ecosystem, packages)
    df["partition"] = partition
    df["ecosystem"] = ecosystem

    click.echo(f"Saving data to {output}")
    df.to_parquet(output, partition_cols=["ecosystem", "partition"])
    click.echo("Scraping completed.")


@cli.command()
@click.option(
    "-o",
    "--output",
    default=os.path.join(OUTPUT_ROOT, "source-urls.parquet"),
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
        WITH pypi_sources AS (
        SELECT source_url FROM read_parquet('{input}/pypi-json/*/*.parquet')
        ),
        conda_sources AS (
        SELECT source_url FROM read_parquet('{input}/conda/*/*/*.parquet')
        )
        SELECT DISTINCT source_url
        FROM (
            SELECT source_url FROM pypi_sources
            UNION ALL
            SELECT source_url FROM conda_sources
        );
    """
    ).df()
    df.to_parquet(output)
    click.echo("Aggregation completed.")


@cli.command()
@click.option(
    "--output",
    default=os.path.join(OUTPUT_ROOT, "git"),
    help="The output directory to save the scraped data in hive partition",
)
@click.option(
    "-i",
    "--input",
    default=os.path.join(OUTPUT_ROOT, "source-urls.parquet"),
    help="The output path to save the aggregated data",
)
@partition_option
@num_partitions_option
def git(input, num_partitions, partition, output):
    urls = get_git_urls(input, num_partitions, partition)
    click.echo(
        f"Will process {len(urls)} source urls in partition {partition} of {num_partitions}"
    )

    df = scrape_git(urls)
    df["partition"] = partition

    click.echo(f"Saving data to {output}")
    df.to_parquet(output, partition_cols=["partition"])
    click.echo("Scraping completed.")


@cli.command()
@click.option(
    "--git-input",
    default=os.path.join(OUTPUT_ROOT, "git"),
    help="The git input path to read the data from",
)
@click.option(
    "--pypi-input",
    default=os.path.join(OUTPUT_ROOT, "pypi-json"),
    help="The pypi input path to read the data from",
)
@click.option(
    "--conda-input",
    default=os.path.join(OUTPUT_ROOT, "conda"),
    help="The conda input path to read the data from",
)
@click.option(
    "-o",
    "--output",
    default=os.path.join(OUTPUT_ROOT, "score"),
    help="The output path to save the aggregated data",
)
@partition_option
@num_partitions_option
def score(git_input, pypi_input, conda_input, num_partitions, partition, output):

    db = duckdb.connect()
    db.execute("CREATE SECRET (TYPE GCS);")
    click.echo(f"Reading data from pypi {pypi_input} into memory")
    db.execute(
        f"""
    CREATE TABLE pypi AS
    SELECT * FROM read_parquet('{pypi_input}/*/*.parquet')
    """
    )
    click.echo(f"Reading data from conda {conda_input} into memory")
    db.execute(
        f"""
    CREATE TABLE conda AS
    SELECT * FROM read_parquet('{conda_input}/*/*/*.parquet')
    """
    )

    # This has better handling than panadas read_parquet
    click.echo(f"Reading data from git {git_input} into memory")
    df = db.query(
        f"""
    select * from read_parquet('{git_input}/*/*.parquet')
    where partition={partition}
    """
    ).df()

    df = df[~df.source_url.isna()]
    df.set_index("source_url", inplace=True)

    scores = []
    for source_url, row in df.iterrows():
        score: dict = {"source_url": source_url, "packages": []}
        scores.append(score)
        score["packages"].extend(get_pypi_packages(db, source_url))
        score["packages"].extend(get_conda_packages(db, source_url))

        score["maturity"] = build_maturity_score(source_url, row)
        score["health_risk"] = build_health_risk_score(source_url, row)

    df = pd.DataFrame(scores)
    df["partition"] = partition

    click.echo(f"Saving data to {output}")
    df.to_parquet(output, partition_cols=["partition"])
    click.echo("Scraping completed.")


if __name__ == "__main__":
    cli()
