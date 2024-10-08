#!/usr/bin/env python


def region_dict(x_low: int, y_low: int, x_high: int, y_high: int) -> dict[str, int]:
    return {"x_low": x_low, "y_low": y_low, "x_high": x_high, "y_high": y_high}
