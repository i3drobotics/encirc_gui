#!/usr/bin/env python

import matplotlib.pyplot as plt


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
