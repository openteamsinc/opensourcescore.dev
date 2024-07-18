import yaml


def load_config(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def save_config(config, file_path):
    with open(file_path, "w") as file:
        yaml.safe_dump(config, file)
