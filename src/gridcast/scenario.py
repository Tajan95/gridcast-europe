"""Szenario-Features und transparente Post-Model-Anpassungen.

Die Funktionen in diesem Modul trennen zwei Ebenen:

1. Das trainierte ML-Modell reagiert auf Kalender und Wetter.
2. Strukturelle Nachfrage- und Rechenzentrumsannahmen werden danach sichtbar
   und deterministisch auf die Modellprognose angewendet.

Die resultierenden Kurven sind konditionale Was-wäre-wenn-Rechnungen und keine
autonomen Langfrist- oder Wetterprognosen.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
import math

import numpy as np
import pandas as pd

from .config import COUNTRY_REGISTRY
from .modeling import add_modeling_features


CLIMATOLOGY_COLUMNS: tuple[str, ...] = (
    "country",
    "local_month",
    "local_hour",
    "temperature_c_median",
    "radiation_direct_wm2_median",
    "radiation_diffuse_wm2_median",
)


def _coerce_date(value: date | datetime | str | pd.Timestamp) -> date:
    """Normalisiert eine Datumseingabe ohne stillschweigende Zeitzonenumrechnung."""

    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return pd.Timestamp(value).date()


def build_scenario_features(
    climatology: pd.DataFrame,
    *,
    country: str,
    target_date: date | datetime | str | pd.Timestamp,
    temperature_delta_c: float = 0.0,
    direct_radiation_factor: float = 1.0,
    diffuse_radiation_factor: float = 1.0,
) -> pd.DataFrame:
    """Erzeugt ein nominales 24-Stunden-Featureprofil für ein Szenario.

    Das Wetter stammt aus dem historischen Medianprofil
    ``Land × Monat × lokale Stunde``. ``temperature_delta_c`` verschiebt die
    Temperatur, während ``direct_radiation_factor`` und
    ``diffuse_radiation_factor`` die beiden nicht-negativen
    Strahlungsprofile skalieren. Das Profil besitzt bewusst die lokalen
    Uhrstunden 0 bis 23. An Tagen mit Sommerzeitwechsel ist es daher eine
    standardisierte Szenariodarstellung und kein behaupteter
    UTC-Prognosehorizont.
    """

    missing = sorted(set(CLIMATOLOGY_COLUMNS) - set(climatology.columns))
    if missing:
        raise ValueError(f"Erforderliche Klimatologiespalten fehlen: {missing}")
    if country not in COUNTRY_REGISTRY:
        raise KeyError(f"Nicht unterstütztes Land: {country!r}")

    scenario_date = _coerce_date(target_date)
    delta = float(temperature_delta_c)
    if not math.isfinite(delta):
        raise ValueError("temperature_delta_c muss endlich sein.")
    direct_factor = float(direct_radiation_factor)
    diffuse_factor = float(diffuse_radiation_factor)
    if not math.isfinite(direct_factor) or direct_factor < 0:
        raise ValueError(
            "direct_radiation_factor muss endlich und nicht-negativ sein."
        )
    if not math.isfinite(diffuse_factor) or diffuse_factor < 0:
        raise ValueError(
            "diffuse_radiation_factor muss endlich und nicht-negativ sein."
        )

    profile = climatology.loc[
        climatology["country"].eq(country)
        & climatology["local_month"].eq(scenario_date.month),
        list(CLIMATOLOGY_COLUMNS),
    ].copy()
    profile.sort_values("local_hour", inplace=True)
    profile.reset_index(drop=True, inplace=True)

    expected_hours = list(range(24))
    actual_hours = profile["local_hour"].astype(int).tolist()
    if actual_hours != expected_hours:
        raise ValueError(
            "Das Klimatologieprofil muss genau die lokalen Stunden 0 bis 23 "
            f"enthalten; erhalten: {actual_hours}"
        )

    result = pd.DataFrame(
        {
            "country": country,
            "local_date": scenario_date.isoformat(),
            "local_hour": profile["local_hour"].astype("int8"),
            "local_weekday": scenario_date.weekday(),
            "local_month": scenario_date.month,
            "local_day_of_year": scenario_date.timetuple().tm_yday,
            "is_weekend": int(scenario_date.weekday() >= 5),
            "temperature_c": (
                profile["temperature_c_median"].astype(float) + delta
            ),
            "radiation_direct_wm2": (
                profile["radiation_direct_wm2_median"].astype(float)
                * direct_factor
            ),
            "radiation_diffuse_wm2": (
                profile["radiation_diffuse_wm2_median"].astype(float)
                * diffuse_factor
            ),
        }
    )

    result["hour_sin"] = np.sin(2 * np.pi * result["local_hour"] / 24)
    result["hour_cos"] = np.cos(2 * np.pi * result["local_hour"] / 24)
    result["weekday_sin"] = np.sin(
        2 * np.pi * result["local_weekday"] / 7
    )
    result["weekday_cos"] = np.cos(
        2 * np.pi * result["local_weekday"] / 7
    )
    result["year_sin"] = np.sin(
        2 * np.pi * (result["local_day_of_year"] - 1) / 365.2425
    )
    result["year_cos"] = np.cos(
        2 * np.pi * (result["local_day_of_year"] - 1) / 365.2425
    )
    result["temperature_sq"] = result["temperature_c"] ** 2
    result["heating_degrees"] = (15.0 - result["temperature_c"]).clip(lower=0)
    result["cooling_degrees"] = (result["temperature_c"] - 22.0).clip(lower=0)
    return add_modeling_features(result)


def apply_structural_scenario(
    weather_adjusted_forecast_mw: Sequence[float],
    demand_change_fraction: float = 0.0,
    additional_data_centre_load_mw: float | Sequence[float] = 0.0,
) -> list[float]:
    """Apply explicit structural assumptions to a rerun ML forecast."""

    forecast = [float(value) for value in weather_adjusted_forecast_mw]
    if not forecast or not all(math.isfinite(value) for value in forecast):
        raise ValueError(
            "weather_adjusted_forecast_mw must be finite and non-empty"
        )
    demand_change = float(demand_change_fraction)
    if not math.isfinite(demand_change) or demand_change <= -1.0:
        raise ValueError(
            "demand_change_fraction must be finite and greater than -1"
        )
    if isinstance(additional_data_centre_load_mw, (int, float)):
        additions = [float(additional_data_centre_load_mw)] * len(forecast)
    else:
        additions = [float(value) for value in additional_data_centre_load_mw]
        if len(additions) != len(forecast):
            raise ValueError(
                "data-centre load profile must match the forecast length"
            )
    if not all(math.isfinite(value) for value in additions):
        raise ValueError("additional_data_centre_load_mw must be finite")
    return [
        base * (1.0 + demand_change) + addition
        for base, addition in zip(forecast, additions)
    ]


def predict_scenario_day(
    model,
    climatology: pd.DataFrame,
    *,
    country: str,
    target_date: date | datetime | str | pd.Timestamp,
    temperature_delta_c: float = 0.0,
    direct_radiation_factor: float = 1.0,
    diffuse_radiation_factor: float = 1.0,
    demand_change_fraction: float = 0.0,
    additional_data_centre_load_mw: float | Sequence[float] = 0.0,
) -> pd.DataFrame:
    """Berechnet Basis-, Wetter- und Gesamtszenario für einen Kalendertag."""

    base_features = build_scenario_features(
        climatology,
        country=country,
        target_date=target_date,
        temperature_delta_c=0.0,
    )
    weather_features = build_scenario_features(
        climatology,
        country=country,
        target_date=target_date,
        temperature_delta_c=temperature_delta_c,
        direct_radiation_factor=direct_radiation_factor,
        diffuse_radiation_factor=diffuse_radiation_factor,
    )

    base_prediction = np.asarray(model.predict(base_features), dtype=float)
    weather_prediction = np.asarray(model.predict(weather_features), dtype=float)
    scenario_prediction = np.asarray(
        apply_structural_scenario(
            weather_prediction,
            demand_change_fraction=demand_change_fraction,
            additional_data_centre_load_mw=additional_data_centre_load_mw,
        ),
        dtype=float,
    )

    if not (
        np.isfinite(base_prediction).all()
        and np.isfinite(weather_prediction).all()
        and np.isfinite(scenario_prediction).all()
    ):
        raise ValueError("Das Modell hat nicht-endliche Szenariowerte erzeugt.")
    if (scenario_prediction < 0).any():
        raise ValueError("Das Gesamtszenario darf keine negative Last enthalten.")

    return pd.DataFrame(
        {
            "country": country,
            "local_date": base_features["local_date"],
            "local_hour": base_features["local_hour"],
            "typical_temperature_c": base_features["temperature_c"],
            "scenario_temperature_c": weather_features["temperature_c"],
            "typical_direct_radiation_wm2": base_features[
                "radiation_direct_wm2"
            ],
            "scenario_direct_radiation_wm2": weather_features[
                "radiation_direct_wm2"
            ],
            "typical_diffuse_radiation_wm2": base_features[
                "radiation_diffuse_wm2"
            ],
            "scenario_diffuse_radiation_wm2": weather_features[
                "radiation_diffuse_wm2"
            ],
            "base_prediction_mw": base_prediction,
            "weather_prediction_mw": weather_prediction,
            "scenario_prediction_mw": scenario_prediction,
        }
    )


def summarize_scenario(scenario: pd.DataFrame) -> dict[str, float]:
    """Fasst Spitzenlast und Tagesenergie eines Szenariovergleichs zusammen."""

    required = {"base_prediction_mw", "scenario_prediction_mw"}
    missing = sorted(required - set(scenario.columns))
    if missing:
        raise ValueError(f"Erforderliche Szenariospalten fehlen: {missing}")
    if scenario.empty:
        raise ValueError("scenario darf nicht leer sein.")

    base_peak = float(scenario["base_prediction_mw"].max())
    scenario_peak = float(scenario["scenario_prediction_mw"].max())
    peak_delta = scenario_peak - base_peak
    return {
        "base_peak_mw": base_peak,
        "scenario_peak_mw": scenario_peak,
        "peak_delta_mw": peak_delta,
        "peak_delta_pct": 100.0 * peak_delta / base_peak,
        "base_energy_mwh": float(scenario["base_prediction_mw"].sum()),
        "scenario_energy_mwh": float(scenario["scenario_prediction_mw"].sum()),
    }
