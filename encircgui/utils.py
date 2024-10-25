#!/usr/bin/env python

import matplotlib.pyplot as plt
from pathlib import Path
import sys


def region_dict(x_low: int, y_low: int, x_high: int, y_high: int) -> dict[str, int]:
    return {"x_low": x_low, "y_low": y_low, "x_high": x_high, "y_high": y_high}


def set_qdarkstyle_plot_theme():
    plt.rcParams["axes.facecolor"] = "#19232D"
    plt.rcParams["savefig.facecolor"] = "#19232D"
    plt.rcParams["figure.facecolor"] = "#19232D"
    plt.rcParams["axes.edgecolor"] = "#FFFFFF"
    plt.rcParams["axes.labelcolor"] = "#FFFFFF"
    plt.rcParams["xtick.color"] = "#FFFFFF"
    plt.rcParams["ytick.color"] = "#FFFFFF"
    plt.rcParams["axes.titlecolor"] = "#FFFFFF"
    plt.rcParams["text.color"] = "#FFFFFF"
    plt.rcParams["axes.grid"] = False
    plt.rcParams["grid.linestyle"] = "dashed"


def get_main_script_path() -> Path:
    return Path(sys.argv[0]).absolute()


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_config_path(config_name: str = "config.json") -> Path:
    return get_main_script_path().parent / config_name
