import click
import subprocess


@click.group()
def main():
    pass


@main.command()
def scrape_pypi():
    pass


@main.command()
def conda():
    try:
        subprocess.run(["python", "score/conda.py"], check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error: {e}")


if __name__ == "__main__":
    main()
