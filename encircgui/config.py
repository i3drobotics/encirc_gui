#!/usr/bin/env python

from pathlib import Path
import json

from utils import region_dict, get_config_path

SCRIPT_DIR = Path(__file__).parent.absolute()
DEFAULT_CONFIG_PATH = get_config_path()


def write_config(config: dict, path=None) -> None:
    """Writes config file. If path is not specified, "config.json" is used."""
    if path is None:
        path = DEFAULT_CONFIG_PATH
    with open(path, "w") as f:
        json.dump(config, f, indent=4)


def read_config(path=None) -> dict:
    """Reads config file. If path is not specified, "config.json" is used."""
    if path is None:
        path = DEFAULT_CONFIG_PATH
    with open(path, "r") as f:
        return json.load(f)


def write_default_config():
    # Write default config file
    region1 = region_dict(300, 120, 500, 320)
    region2 = region_dict(500, 120, 850, 320)
    region3 = region_dict(850, 120, 1200, 320)
    region4 = region_dict(1200, 120, 1600, 320)

    regions = [region1, region2, region3, region4]

    data = {}
    data["exposure"] = 0
    data["regions"] = regions
    write_config(data)


if __name__ == "__main__":
    write_default_config()
