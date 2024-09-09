import os
import click
import duckdb

from .conda.get_conda_package_names import get_conda_package_names
from .conda.scrape_conda import scrape_conda
from .pypi.json_scraper import scrape_json
from .pypi.pypi_downloads import get_bulk_download_counts
from .logger import setup_logger
from .pypi.get_pypi_package_list import get_pypi_package_names
from .vulnerabilities.scrape_vulnerabilities import scrape_vulnerabilities
from .git_vcs.get_git_urls import get_git_urls
from .git_vcs.scrape import scrape_git, git_schema
from .score.score import create_scores, score_schema
from . import notes

OUTPUT_ROOT = os.environ.get("OUTPUT_ROOT", "./output")

PREP_PYPI_DIR = os.path.join(OUTPUT_ROOT, "pre/pypi")
PREP_CONDA_DIR = os.path.join(OUTPUT_ROOT, "pre/conda")
PREP_GIT_DIR = os.path.join(OUTPUT_ROOT, "pre/git")

PYPI_DIR = os.path.join(OUTPUT_ROOT, "pypi")
CONDA_DIR = os.path.join(OUTPUT_ROOT, "conda")
GIT_DIR = os.path.join(OUTPUT_ROOT, "git")

VULNERABILITIES_DIR = os.path.join(OUTPUT_ROOT, "vulnerabilities")
PYPI_DOWNLOADS_PATH = os.path.join(OUTPUT_ROOT, "pypi-downloads.parquet")

NOTES_PATH = os.path.join(OUTPUT_ROOT, "notes.parquet")
SCORE_PATH = os.path.join(OUTPUT_ROOT, "score.parquet")
SOURCE_URLS_PATH = os.path.join(OUTPUT_ROOT, "source-urls.parquet")

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
    os.environ.setdefault("GIT_TERMINAL_PROMPT", "0")


@cli.command()
@click.option(
    "--output",
    default=PREP_PYPI_DIR,
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
    click.echo("Pypi Scraping complete")


@cli.command()
@click.option(
    "-o",
    "--output",
    default=PYPI_DOWNLOADS_PATH,
    help="The output path",
)
def scrape_pypi_downloads(output):
    click.echo(f"Fetching download data from BigQuery and saving into {output}")

    # Fetch the download data
    df = get_bulk_download_counts()

    # Save the DataFrame to the specified output with partitioning
    click.echo(f"Saving data to {output}")
    df.to_parquet(output)
    click.echo("Download data fetching and saving completed.")


@cli.command()
@click.option(
    "--output",
    default=PREP_CONDA_DIR,
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
    click.echo("Conda Scraping complete")


@cli.command()
@click.option(
    "--output",
    default=VULNERABILITIES_DIR,
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
    click.echo("Vulnerabilities Scraping complete")


@cli.command()
@click.option(
    "-o",
    "--output",
    default=SOURCE_URLS_PATH,
    help="The output path to save the aggregated data",
)
@click.option(
    "--pypi-input",
    default=PREP_PYPI_DIR,
    help="The input directory to read the data from",
)
@click.option(
    "--conda-input",
    default=PREP_CONDA_DIR,
    help="The input directory to read the data from",
)
def agg_source_urls(pypi_input, conda_input, output):
    click.echo("Aggregating data")

    db = duckdb.connect()
    # Public dataset / empty secret
    db.execute("CREATE SECRET (TYPE GCS);")

    df = db.query(
        f"""
        WITH pypi_sources AS (
        SELECT source_url FROM read_parquet('{pypi_input}/*/*.parquet')
        ),
        conda_sources AS (
        SELECT source_url FROM read_parquet('{conda_input}/**/*.parquet')
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
    click.echo("Aggregation complete")


@cli.command()
@click.option(
    "--output",
    default=PREP_GIT_DIR,
    help="The output directory to save the scraped data in hive partition",
)
@click.option(
    "-i",
    "--input",
    default=SOURCE_URLS_PATH,
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

    df.to_parquet(output, partition_cols=["partition"], schema=git_schema)
    click.echo("Git Scraping complete")


@cli.command()
@click.option(
    "--git-input",
    default=PREP_GIT_DIR,
    help="The output directory to save the scraped data in hive partition",
)
@click.option(
    "--git-output",
    default=GIT_DIR,
    help="The output path to save the aggregated data",
)
@click.option(
    "--pypi-input",
    default=PREP_PYPI_DIR,
    help="The output directory to save the scraped data in hive partition",
)
@click.option(
    "--pypi-output",
    default=PYPI_DIR,
    help="The output path to save the aggregated data",
)
@click.option(
    "--conda-input",
    default=PREP_CONDA_DIR,
    help="The output directory to save the scraped data in hive partition",
)
@click.option(
    "--conda-output",
    default=CONDA_DIR,
    help="The output path to save the aggregated data",
)
@partition_option
@num_partitions_option
def coalesce(
    num_partitions,
    partition,
    git_input,
    git_output,
    pypi_input,
    pypi_output,
    conda_input,
    conda_output,
):
    """
    Step operation to reduce the number or partitions
    """
    db = duckdb.connect()
    db.execute("CREATE SECRET (TYPE GCS);")

    to_coalesce = [
        ("conda", conda_input, conda_output, None),
        ("pypi", pypi_input, pypi_output, None),
        ("git", git_input, git_output, git_schema),
    ]
    for name, input_path, output_path, schema in to_coalesce:
        click.echo(f"Reading data from {name} {input_path} into memory")
        git_df = db.execute(
            f"""
        select * from read_parquet('{input_path}/**/*.parquet')
        where (partition % {num_partitions}) = {partition}
        """
        ).df()

        click.echo(f"Saving data to {output_path}")

        git_df["partition"] = partition
        git_df.to_parquet(output_path, partition_cols=["partition"], schema=schema)
    click.echo("Coalesce complete")


@cli.command()
@click.option(
    "--git-input",
    default=GIT_DIR,
    help="The git input path to read the data from",
)
@click.option(
    "--pypi-input",
    default=PYPI_DIR,
    help="The pypi input path to read the data from",
)
@click.option(
    "--conda-input",
    default=CONDA_DIR,
    help="The conda input path to read the data from",
)
@click.option(
    "-o",
    "--output",
    default=SCORE_PATH,
    help="The output path to save the aggregated data",
)
@click.option(
    "--note-output",
    default=NOTES_PATH,
    help="path to save notes",
)
def score(git_input, pypi_input, conda_input, output, note_output):

    db = duckdb.connect()
    db.execute("CREATE SECRET (TYPE GCS);")
    click.echo(f"Reading data from pypi {pypi_input} into memory")
    db.execute(
        f"""
    CREATE TABLE pypi AS
    SELECT name, version, source_url FROM read_parquet('{pypi_input}/*/*.parquet')
    """
    )
    click.echo(f"Reading data from conda {conda_input} into memory")
    db.execute(
        f"""
    CREATE TABLE conda AS
    SELECT full_name, latest_version, source_url FROM read_parquet('{conda_input}/**/*.parquet')
    """
    )

    # This has better handling than panadas read_parquet
    click.echo(f"Reading data from git {git_input} into memory")
    db.execute(
        f"""
    CREATE TABLE git AS
    select * from read_parquet('{git_input}/*/*.parquet')
    """
    )

    click.echo("Processing score")
    print(db.query("select source_url, error from git").df())
    df = create_scores(db)
    click.echo(f"Saving data to {output}")
    df.to_parquet(output, schema=score_schema)

    note_df = notes.to_df()
    print("note_output", note_output)
    # note_df.to_parquet(note_output)
    click.echo("Score complete")


if __name__ == "__main__":
    cli()
