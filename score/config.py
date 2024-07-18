import yaml
import os

CONFIG_FILE = "config.yaml"
OUTPUT_DIR = "output"


def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        config = {}
    return config


def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        yaml.safe_dump(config, file)


def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
