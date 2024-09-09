from .cli import cli
from click.testing import CliRunner
from unittest.mock import patch
import pandas as pd
import logging
import sys


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    print(result)


@patch("score.conda.get_conda_package_names.get_all_conda_package_names")
@patch("score.pypi.get_pypi_package_list.get_all_pypi_package_names")
def test_pipeline(get_all_pypi_package_names, get_all_conda_package_names, tmp_path):
    print("tmp_path", tmp_path)
    get_all_pypi_package_names.return_value = ["flask", "meta"]
    get_all_conda_package_names.return_value = ["flask"]

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    runner = CliRunner()
    result = runner.invoke(
        cli, ["scrape-pypi", f"--output={tmp_path}/pypi", "-p", "0", "-n", "1"]
    )
    print(result.output)
    print("result", result)
    assert result.exit_code == 0

    # -----
    # -----

    result = runner.invoke(
        cli, ["conda", f"--output={tmp_path}/conda", "-p", "0", "-n", "1"]
    )
    print(result.output)
    print("result", result)
    assert result.exit_code == 0

    # -----
    # -----

    print("running agg-source-urls")
    result = runner.invoke(
        cli,
        [
            "agg-source-urls",
            f"--output={tmp_path}/source-urls.parquet",
            f"--pypi-input={tmp_path}/pypi",
            f"--conda-input={tmp_path}/conda",
        ],
    )
    print(result.output)
    print("result", result)
    assert result.exit_code == 0

    # -----
    # -----
    print("running git ...")
    result = runner.invoke(
        cli,
        [
            "git",
            f"--input={tmp_path}/source-urls.parquet",
            f"--output={tmp_path}/git",
            "-p",
            "0",
            "-n",
            "1",
        ],
    )
    print(result.output)
    print("result", result)
    assert result.exit_code == 0

    # -----
    # -----
    print("running score ...")
    result = runner.invoke(
        cli,
        [
            "score",
            f"--git-input={tmp_path}/git",
            f"--pypi-input={tmp_path}/pypi",
            f"--conda-input={tmp_path}/conda",
            f"--output={tmp_path}/score.parquet",
            f"--note-output={tmp_path}/notes.parquet",
        ],
    )
    print(result.output)
    print("result", result)
    assert result.exit_code == 0

    df = pd.read_parquet(f"{tmp_path}/score.parquet").set_index("source_url")
    assert df.index.size == 2

    flask = df.loc["https://github.com/pallets/flask"]
    assert len(flask.packages) == 2
    assert flask.maturity["value"] == "Mature"
    assert flask.health_risk["value"] == "Healthy"

    meta = df.loc["http://srossross.github.com/Meta"]
    assert len(meta.packages) == 1
    print(df.iloc[0])
    print(df.iloc[1])
    # assert False
