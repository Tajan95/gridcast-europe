"""Reproduzierbarer Import und Aufbau der GridCast-Modelldaten."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

from .config import CountrySpec


DEFAULT_LOAD_RELATIVE_PATH = Path(
    "data/raw/opsd/time_series_2020-10-06/time_series_60min_singleindex.csv"
)
DEFAULT_WEATHER_RELATIVE_PATH = Path(
    "data/raw/opsd/weather_data_2020-09-16/weather_data.csv"
)

MODEL_START = pd.Timestamp("2015-01-01T00:00:00Z")
MODEL_END_EXCLUSIVE = pd.Timestamp("2020-01-01T00:00:00Z")


def resolve_input_paths(
    project_root: Path,
    load_csv: str | Path | None = None,
    weather_csv: str | Path | None = None,
) -> tuple[Path, Path]:
    """Löst explizite, per Umgebungsvariable oder standardisierte Pfade auf."""

    load_path = Path(
        load_csv
        or os.getenv("GRIDCAST_LOAD_CSV")
        or project_root / DEFAULT_LOAD_RELATIVE_PATH
    ).expanduser()
    weather_path = Path(
        weather_csv
        or os.getenv("GRIDCAST_WEATHER_CSV")
        or project_root / DEFAULT_WEATHER_RELATIVE_PATH
    ).expanduser()

    missing = [path for path in (load_path, weather_path) if not path.is_file()]
    if missing:
        formatted = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(
            "Folgende OPSD-Rohdateien fehlen:\n"
            f"{formatted}\n"
            "Lege sie unter data/raw/ ab oder setze GRIDCAST_LOAD_CSV und "
            "GRIDCAST_WEATHER_CSV."
        )
    return load_path.resolve(), weather_path.resolve()


def _require_columns(frame: pd.DataFrame, required: list[str], label: str) -> None:
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"{label}: erforderliche Spalten fehlen: {missing}")


def load_opsd_sources(
    load_csv: Path,
    weather_csv: Path,
    specs: Mapping[str, CountrySpec],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lädt nur den für die freigegebenen Länder benötigten Spaltenausschnitt."""

    load_columns = ["utc_timestamp"] + [spec.load_column for spec in specs.values()]
    weather_columns = ["utc_timestamp"] + [
        column for spec in specs.values() for column in spec.weather_columns
    ]

    load = pd.read_csv(load_csv, usecols=load_columns, low_memory=False)
    weather = pd.read_csv(weather_csv, usecols=weather_columns, low_memory=False)
    _require_columns(load, load_columns, "Lastdaten")
    _require_columns(weather, weather_columns, "Wetterdaten")

    for frame in (load, weather):
        frame["utc_timestamp"] = pd.to_datetime(
            frame["utc_timestamp"], utc=True, errors="raise"
        )
        frame.sort_values("utc_timestamp", inplace=True)
        frame.reset_index(drop=True, inplace=True)

    return load, weather


def validate_hourly_axis(frame: pd.DataFrame, label: str) -> dict[str, object]:
    """Prüft Sortierung, Duplikate und fehlende UTC-Stunden einer Zeitachse."""

    timestamps = frame["utc_timestamp"]
    duplicates = int(timestamps.duplicated().sum())
    monotonic = bool(timestamps.is_monotonic_increasing)
    expected = pd.date_range(
        timestamps.min(), timestamps.max(), freq="h", tz="UTC"
    )
    missing_hours = int(len(expected.difference(pd.DatetimeIndex(timestamps))))

    return {
        "dataset": label,
        "rows": len(frame),
        "start_utc": timestamps.min(),
        "end_utc": timestamps.max(),
        "duplicate_timestamps": duplicates,
        "missing_index_hours": missing_hours,
        "monotonic_increasing": monotonic,
    }


def _weather_to_long(
    weather: pd.DataFrame,
    specs: Mapping[str, CountrySpec],
) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for code, spec in specs.items():
        part = weather[
            [
                "utc_timestamp",
                spec.temperature_column,
                spec.direct_radiation_column,
                spec.diffuse_radiation_column,
            ]
        ].copy()
        part.columns = [
            "utc_timestamp",
            "temperature_c",
            "radiation_direct_wm2",
            "radiation_diffuse_wm2",
        ]
        part.insert(1, "country", code)
        parts.append(part)
    return pd.concat(parts, ignore_index=True)


def _load_to_long(
    load: pd.DataFrame,
    specs: Mapping[str, CountrySpec],
) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for code, spec in specs.items():
        part = load[["utc_timestamp", spec.load_column]].copy()
        part.columns = ["utc_timestamp", "load_mw"]
        part.insert(1, "country", code)
        parts.append(part)
    return pd.concat(parts, ignore_index=True)


def _local_components(
    timestamps: pd.Series,
    timezone: str,
) -> pd.DataFrame:
    local = timestamps.dt.tz_convert(timezone)
    return pd.DataFrame(
        {
            "local_date": local.dt.strftime("%Y-%m-%d"),
            "local_hour": local.dt.hour.astype("int8"),
            "local_weekday": local.dt.weekday.astype("int8"),
            "local_month": local.dt.month.astype("int8"),
            "local_day_of_year": local.dt.dayofyear.astype("int16"),
            "utc_offset_hours": local.map(
                lambda value: value.utcoffset().total_seconds() / 3600
            ).astype("int8"),
        },
        index=timestamps.index,
    )


def add_calendar_features(
    frame: pd.DataFrame,
    specs: Mapping[str, CountrySpec],
) -> pd.DataFrame:
    """Erzeugt kalender- und zyklusbasierte Features aus korrekter Lokalzeit."""

    result = frame.copy()
    result["local_date"] = ""
    for column in (
        "local_hour",
        "local_weekday",
        "local_month",
        "local_day_of_year",
        "utc_offset_hours",
    ):
        result[column] = np.int16(0)

    for code, spec in specs.items():
        mask = result["country"].eq(code)
        local = _local_components(result.loc[mask, "utc_timestamp"], spec.timezone)
        for column in local.columns:
            result.loc[mask, column] = local[column]

    integer_columns = [
        "local_hour",
        "local_weekday",
        "local_month",
        "local_day_of_year",
        "utc_offset_hours",
    ]
    result[integer_columns] = result[integer_columns].astype("int16")
    result["is_weekend"] = result["local_weekday"].ge(5).astype("int8")

    season_map = {
        12: "Winter",
        1: "Winter",
        2: "Winter",
        3: "Frühling",
        4: "Frühling",
        5: "Frühling",
        6: "Sommer",
        7: "Sommer",
        8: "Sommer",
        9: "Herbst",
        10: "Herbst",
        11: "Herbst",
    }
    result["season"] = result["local_month"].map(season_map)

    result["hour_sin"] = np.sin(2 * np.pi * result["local_hour"] / 24)
    result["hour_cos"] = np.cos(2 * np.pi * result["local_hour"] / 24)
    result["weekday_sin"] = np.sin(2 * np.pi * result["local_weekday"] / 7)
    result["weekday_cos"] = np.cos(2 * np.pi * result["local_weekday"] / 7)
    result["year_sin"] = np.sin(
        2 * np.pi * (result["local_day_of_year"] - 1) / 365.2425
    )
    result["year_cos"] = np.cos(
        2 * np.pi * (result["local_day_of_year"] - 1) / 365.2425
    )

    # Transparente nichtlineare Temperaturmerkmale.
    result["temperature_sq"] = result["temperature_c"] ** 2
    result["heating_degrees"] = (15.0 - result["temperature_c"]).clip(lower=0)
    result["cooling_degrees"] = (result["temperature_c"] - 22.0).clip(lower=0)

    return result


def assign_split(frame: pd.DataFrame) -> pd.DataFrame:
    """Weist den verbindlichen chronologischen Split zu."""

    result = frame.copy()
    year = result["utc_timestamp"].dt.year
    result["split"] = np.select(
        [year.between(2015, 2017), year.eq(2018), year.eq(2019)],
        ["train", "validation", "test"],
        default="outside_scope",
    )
    return result


def build_model_table(
    load: pd.DataFrame,
    weather: pd.DataFrame,
    specs: Mapping[str, CountrySpec],
    start: pd.Timestamp = MODEL_START,
    end_exclusive: pd.Timestamp = MODEL_END_EXCLUSIVE,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Baut die vollständige und die zielvariablenbereinigte Modelldatentabelle."""

    load_window = load.loc[
        load["utc_timestamp"].ge(start)
        & load["utc_timestamp"].lt(end_exclusive)
    ]
    weather_window = weather.loc[
        weather["utc_timestamp"].ge(start)
        & weather["utc_timestamp"].lt(end_exclusive)
    ]

    load_long = _load_to_long(load_window, specs)
    weather_long = _weather_to_long(weather_window, specs)
    merged = load_long.merge(
        weather_long,
        on=["country", "utc_timestamp"],
        how="left",
        validate="one_to_one",
    )
    merged.sort_values(["utc_timestamp", "country"], inplace=True)
    merged.reset_index(drop=True, inplace=True)

    with_features = assign_split(add_calendar_features(merged, specs))
    cleaned = with_features.dropna(subset=["load_mw"]).copy()
    cleaned.reset_index(drop=True, inplace=True)
    return with_features, cleaned


def quality_by_country(frame_before_target_drop: pd.DataFrame) -> pd.DataFrame:
    """Verdichtet Vollständigkeit und grobe Plausibilitätsgrenzen je Land."""

    grouped = frame_before_target_drop.groupby("country", observed=True)
    summary = grouped.agg(
        expected_hours=("utc_timestamp", "size"),
        missing_load=("load_mw", lambda values: int(values.isna().sum())),
        missing_temperature=(
            "temperature_c",
            lambda values: int(values.isna().sum()),
        ),
        missing_direct_radiation=(
            "radiation_direct_wm2",
            lambda values: int(values.isna().sum()),
        ),
        missing_diffuse_radiation=(
            "radiation_diffuse_wm2",
            lambda values: int(values.isna().sum()),
        ),
        min_load_mw=("load_mw", "min"),
        median_load_mw=("load_mw", "median"),
        max_load_mw=("load_mw", "max"),
    )
    summary["complete_load_hours"] = (
        summary["expected_hours"] - summary["missing_load"]
    )
    summary["load_completeness_pct"] = (
        100 * summary["complete_load_hours"] / summary["expected_hours"]
    )
    return summary.reset_index()


def build_climatology(
    weather: pd.DataFrame,
    specs: Mapping[str, CountrySpec],
) -> pd.DataFrame:
    """Erzeugt typische Monats-Stunden-Profile aus der gesamten Wetterhistorie."""

    weather_long = _weather_to_long(weather, specs)
    weather_long = add_calendar_features(weather_long, specs)
    value_columns = [
        "temperature_c",
        "radiation_direct_wm2",
        "radiation_diffuse_wm2",
    ]
    profile = (
        weather_long.groupby(
            ["country", "local_month", "local_hour"], observed=True
        )[value_columns]
        .median()
        .add_suffix("_median")
        .reset_index()
    )
    profile["climatology_start_utc"] = weather["utc_timestamp"].min()
    profile["climatology_end_utc"] = weather["utc_timestamp"].max()
    return profile
