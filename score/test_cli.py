from .cli import cli
from click.testing import CliRunner


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    print(result)
