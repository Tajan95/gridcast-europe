"""Transparente Annahmen für den gekoppelten Zukunftspfad der App.

Der Pfad ist keine Prognose. Er interpoliert wenige, offen dokumentierte
europäische Stressannahmen zwischen dem ersten Jahr nach dem Modellfenster und
2050. Die gerundeten Werte entsprechen den Schrittweiten der Streamlit-Regler.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Real


FUTURE_PATH_BASE_YEAR = 2020
FUTURE_PATH_END_YEAR = 2050

# Transparente, europaweit einheitliche Endpunkte für einen vergleichbaren
# Szenariopfad in DE, FR und PL. Die fachliche Herleitung wird im App-Tooltip
# offengelegt; es handelt sich ausdrücklich nicht um länderscharfe Prognosen.
FUTURE_PATH_2050_TEMPERATURE_DELTA_C = 1.5
FUTURE_PATH_2050_DEMAND_CHANGE_PCT = 35
FUTURE_PATH_2050_DATA_CENTRE_MW = 2_000
FUTURE_PATH_2050_RADIATION_PCT = 102


@dataclass(frozen=True)
class FuturePathAssumptions:
    """Gerundete Einzelannahmen eines gekoppelten Zukunftsjahres."""

    year: int
    progress: float
    temperature_delta_c: float
    demand_change_pct: int
    data_centre_mw: int
    direct_radiation_pct: int
    diffuse_radiation_pct: int


def _validated_year(year: Real) -> int:
    if isinstance(year, bool) or not isinstance(year, Real):
        raise TypeError("year muss eine ganze Jahreszahl sein.")
    numeric_year = float(year)
    if not math.isfinite(numeric_year) or not numeric_year.is_integer():
        raise ValueError("year muss eine endliche ganze Jahreszahl sein.")
    result = int(numeric_year)
    if not FUTURE_PATH_BASE_YEAR <= result <= FUTURE_PATH_END_YEAR:
        raise ValueError(
            f"year muss zwischen {FUTURE_PATH_BASE_YEAR} und "
            f"{FUTURE_PATH_END_YEAR} liegen."
        )
    return result


def _round_half_up(value: float) -> int:
    """Rundet positive Pfadwerte deterministisch statt nach Banker's Rounding."""

    return int(math.floor(value + 0.5))


def interpolate_future_path(year: Real) -> FuturePathAssumptions:
    """Interpoliert den europäischen Stresspfad linear von 2020 bis 2050."""

    target_year = _validated_year(year)
    progress = (target_year - FUTURE_PATH_BASE_YEAR) / (
        FUTURE_PATH_END_YEAR - FUTURE_PATH_BASE_YEAR
    )
    temperature_delta = (
        FUTURE_PATH_2050_TEMPERATURE_DELTA_C * progress
    )
    demand_change = _round_half_up(
        FUTURE_PATH_2050_DEMAND_CHANGE_PCT * progress
    )
    data_centre_load = 100 * _round_half_up(
        FUTURE_PATH_2050_DATA_CENTRE_MW * progress / 100
    )
    radiation_pct = 100 + _round_half_up(
        (FUTURE_PATH_2050_RADIATION_PCT - 100) * progress
    )

    return FuturePathAssumptions(
        year=target_year,
        progress=progress,
        temperature_delta_c=round(temperature_delta, 1),
        demand_change_pct=demand_change,
        data_centre_mw=data_centre_load,
        direct_radiation_pct=radiation_pct,
        diffuse_radiation_pct=radiation_pct,
    )
