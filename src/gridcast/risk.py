"""Empirical extreme-load indicators.

These functions estimate threshold exceedance probabilities. They do not
estimate blackout, outage, or physical grid-overload probabilities.
"""

from __future__ import annotations

from collections.abc import Sequence
import math


def _finite_values(values: Sequence[float], name: str) -> list[float]:
    result = [float(value) for value in values]
    if not result:
        raise ValueError(f"{name} must not be empty")
    if not all(math.isfinite(value) for value in result):
        raise ValueError(f"{name} must contain only finite values")
    return result


def historical_quantile(values: Sequence[float], quantile: float) -> float:
    """Return a linearly interpolated empirical quantile.

    The intended input is historical load from the training period of one
    country. Keeping threshold construction on training data avoids test
    leakage.
    """

    if not 0.0 <= quantile <= 1.0:
        raise ValueError("quantile must be between 0 and 1")

    ordered = sorted(_finite_values(values, "values"))
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def empirical_extreme_probabilities(
    point_forecast_mw: Sequence[float],
    validation_residuals_mw: Sequence[float],
    threshold_mw: float,
) -> list[float]:
    """Estimate an exceedance probability for every forecast hour.

    Residuals must be out-of-sample errors defined as actual minus forecast,
    preferably from the validation period of the same country.
    """

    forecasts = _finite_values(point_forecast_mw, "point_forecast_mw")
    residuals = _finite_values(validation_residuals_mw, "validation_residuals_mw")
    threshold = float(threshold_mw)
    if not math.isfinite(threshold):
        raise ValueError("threshold_mw must be finite")

    denominator = len(residuals)
    return [
        sum(forecast + residual > threshold for residual in residuals) / denominator
        for forecast in forecasts
    ]


def extreme_day_probability(
    point_forecast_mw: Sequence[float],
    validation_residual_paths_mw: Sequence[Sequence[float]],
    threshold_mw: float,
) -> float:
    """Estimate P(any forecast hour exceeds the threshold).

    Complete residual paths preserve within-day dependence better than
    independently sampled hourly residuals. Each path must have the same
    length as the point forecast (normally 24 hours).
    """

    forecasts = _finite_values(point_forecast_mw, "point_forecast_mw")
    paths = [
        _finite_values(path, f"validation_residual_paths_mw[{index}]")
        for index, path in enumerate(validation_residual_paths_mw)
    ]
    if not paths:
        raise ValueError("validation_residual_paths_mw must not be empty")
    if any(len(path) != len(forecasts) for path in paths):
        raise ValueError("each residual path must match the forecast length")

    threshold = float(threshold_mw)
    if not math.isfinite(threshold):
        raise ValueError("threshold_mw must be finite")

    exceedances = sum(
        any(forecast + residual > threshold for forecast, residual in zip(forecasts, path))
        for path in paths
    )
    return exceedances / len(paths)

