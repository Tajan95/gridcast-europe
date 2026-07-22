"""Transparent post-model adjustments for scenario analysis."""

from __future__ import annotations

from collections.abc import Sequence
import math


def apply_structural_scenario(
    temperature_adjusted_forecast_mw: Sequence[float],
    demand_change_fraction: float = 0.0,
    additional_data_centre_load_mw: float | Sequence[float] = 0.0,
) -> list[float]:
    """Apply explicit structural assumptions to a rerun ML forecast.

    Temperature effects are not approximated here: the caller must first rerun
    the trained model with the modified temperature features. This function
    then applies the disclosed relative demand change and absolute data-centre
    load addition.
    """

    forecast = [float(value) for value in temperature_adjusted_forecast_mw]
    if not forecast or not all(math.isfinite(value) for value in forecast):
        raise ValueError("temperature_adjusted_forecast_mw must be finite and non-empty")

    demand_change = float(demand_change_fraction)
    if not math.isfinite(demand_change) or demand_change <= -1.0:
        raise ValueError("demand_change_fraction must be finite and greater than -1")

    if isinstance(additional_data_centre_load_mw, (int, float)):
        additions = [float(additional_data_centre_load_mw)] * len(forecast)
    else:
        additions = [float(value) for value in additional_data_centre_load_mw]
        if len(additions) != len(forecast):
            raise ValueError("data-centre load profile must match the forecast length")

    if not all(math.isfinite(value) for value in additions):
        raise ValueError("additional_data_centre_load_mw must be finite")

    return [
        base * (1.0 + demand_change) + addition
        for base, addition in zip(forecast, additions)
    ]

