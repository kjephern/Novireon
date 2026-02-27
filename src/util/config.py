import os
import tomllib

from box import Box
from config.path_config import *


def get_config(name: str):
    config_file_name = f"{name}_config.toml"
    if config_file_name not in os.listdir(CONFIG_PATH):
        raise FileNotFoundError(f"Config {name} not found.")
    with open(CONFIG_PATH / config_file_name, "rb") as f:
        return Box(tomllib.load(f), box_dots=True)
