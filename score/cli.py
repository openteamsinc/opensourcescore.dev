import click


@click.group()
def main():
    pass


@main.command()
def scrape_pypi():
    pass


if __name__ == "__main__":
    main()
