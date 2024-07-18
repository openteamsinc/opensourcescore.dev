import argparse
from cli import run_cli


def main():
    parser = argparse.ArgumentParser(description="PyPI Scraper CLI Tool")
    parser.add_argument(
        "--config", type=str, help="Path to configuration file", default="config.yaml"
    )
    args = parser.parse_args()

    run_cli(args.config)


if __name__ == "__main__":
    main()
