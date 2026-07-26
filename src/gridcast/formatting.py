"""Kompakte, deutsch formatierte Einheiten für die App-Darstellung."""

from __future__ import annotations

import math


def _format_decimal(value: float, digits: int) -> str:
    """Formatiert mit Dezimalkomma und ohne bedeutungslose Endnullen."""

    if not math.isfinite(value):
        raise ValueError("Anzeigewerte müssen endlich sein.")
    rounded = round(float(value), digits)
    if rounded == 0:
        rounded = 0.0
    text = f"{rounded:.{digits}f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")


def format_power_mw(value_mw: float) -> str:
    """Skaliert eine Leistung von MW über GW bis TW."""

    absolute = abs(float(value_mw))
    if absolute >= 1_000_000:
        return f"{_format_decimal(value_mw / 1_000_000, 3)} TW"
    if absolute >= 1_000:
        scaled = value_mw / 1_000
        digits = 3 if abs(scaled) >= 999.5 else 1
        return f"{_format_decimal(scaled, digits)} GW"
    return f"{_format_decimal(value_mw, 1)} MW"


def format_energy_mwh(value_mwh: float) -> str:
    """Skaliert eine Energie von MWh über GWh bis TWh."""

    absolute = abs(float(value_mwh))
    if absolute >= 1_000_000:
        return f"{_format_decimal(value_mwh / 1_000_000, 3)} TWh"
    if absolute >= 1_000:
        scaled = value_mwh / 1_000
        digits = 3 if abs(scaled) >= 999.5 else 1
        return f"{_format_decimal(scaled, digits)} GWh"
    return f"{_format_decimal(value_mwh, 1)} MWh"
