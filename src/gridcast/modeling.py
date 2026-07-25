"""Leakage-freie Baselines, Modellpipelines und Metriken für GridCast Europe."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    root_mean_squared_error,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.validation import check_is_fitted


TARGET_COLUMN = "load_mw"
COUNTRY_COLUMN = "country"

CYCLICAL_FEATURES: tuple[str, ...] = (
    "hour_sin",
    "hour_cos",
    "weekday_sin",
    "weekday_cos",
    "year_sin",
    "year_cos",
)
WEATHER_FEATURES: tuple[str, ...] = (
    "temperature_c",
    "temperature_sq",
    "heating_degrees",
    "cooling_degrees",
    "radiation_direct_wm2",
    "radiation_diffuse_wm2",
)
HGB_CALENDAR_FEATURES: tuple[str, ...] = (
    "local_hour",
    "local_weekday",
    "local_month",
    *CYCLICAL_FEATURES,
    "is_weekend",
)


def _require_columns(frame: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f"Erforderliche Modellspalten fehlen: {missing}")


def _gregorian_easter_sunday(year: int) -> date:
    """Berechnet den Ostersonntag nach dem gregorianischen Kalender."""

    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def national_holidays(country: str, year: int) -> set[date]:
    """Liefert die landesweit modellierten Feiertage für DE, FR und PL.

    Regionale Feiertage werden bewusst nicht abgebildet. Für Deutschland wird
    der einmalig bundesweite Reformationstag am 31.10.2017 berücksichtigt.
    """

    fixed_dates = {
        "DE": ((1, 1), (5, 1), (10, 3), (12, 25), (12, 26)),
        "FR": (
            (1, 1),
            (5, 1),
            (5, 8),
            (7, 14),
            (8, 15),
            (11, 1),
            (11, 11),
            (12, 25),
        ),
        "PL": (
            (1, 1),
            (1, 6),
            (5, 1),
            (5, 3),
            (8, 15),
            (11, 1),
            (11, 11),
            (12, 25),
            (12, 26),
        ),
    }
    easter_offsets = {
        "DE": (-2, 1, 39, 50),
        "FR": (1, 39, 50),
        "PL": (1, 60),
    }
    if country not in fixed_dates:
        raise KeyError(f"Keine Feiertagsregeln für Land {country!r} hinterlegt.")

    holidays = {date(year, month, day) for month, day in fixed_dates[country]}
    easter = _gregorian_easter_sunday(year)
    holidays.update(easter + timedelta(days=offset) for offset in easter_offsets[country])
    if country == "DE" and year == 2017:
        holidays.add(date(2017, 10, 31))
    return holidays


def add_modeling_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Ergänzt im Voraus bekannte Feiertags- und Gruppierungsmerkmale."""

    required = (
        COUNTRY_COLUMN,
        "local_date",
        "local_hour",
        "local_month",
        "is_weekend",
    )
    _require_columns(frame, required)
    result = frame.copy()
    local_dates = pd.to_datetime(result["local_date"], errors="raise").dt.date
    holiday_cache: dict[tuple[str, int], set[date]] = {}

    holiday_flags: list[int] = []
    for country, local_date in zip(result[COUNTRY_COLUMN], local_dates):
        key = (str(country), local_date.year)
        if key not in holiday_cache:
            holiday_cache[key] = national_holidays(*key)
        holiday_flags.append(int(local_date in holiday_cache[key]))

    result["is_holiday"] = np.asarray(holiday_flags, dtype=np.int8)
    result["day_type"] = np.select(
        [result["is_holiday"].eq(1), result["is_weekend"].eq(1)],
        ["holiday", "weekend"],
        default="weekday",
    )
    result["calendar_key"] = (
        result[COUNTRY_COLUMN].astype(str)
        + "|"
        + result["local_month"].astype(str)
        + "|"
        + result["day_type"].astype(str)
        + "|"
        + result["local_hour"].astype(str)
    )
    return result


class CountryMeanBaseline(BaseEstimator, RegressorMixin):
    """Konstante, länderspezifische Mittelwert-Baseline."""

    def fit(self, X: pd.DataFrame, y: Sequence[float]):
        _require_columns(X, (COUNTRY_COLUMN,))
        target = pd.Series(np.asarray(y, dtype=float), index=X.index)
        self.country_means_ = target.groupby(X[COUNTRY_COLUMN]).mean().to_dict()
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        check_is_fitted(self, "country_means_")
        mapped = X[COUNTRY_COLUMN].map(self.country_means_)
        if mapped.isna().any():
            unknown = sorted(X.loc[mapped.isna(), COUNTRY_COLUMN].unique())
            raise ValueError(f"Unbekannte Länder bei der Vorhersage: {unknown}")
        return mapped.to_numpy(dtype=float)


class CalendarBaseline(BaseEstimator, RegressorMixin):
    """Kalenderdurchschnitt mit dokumentierter Rückfallhierarchie."""

    def __init__(self, min_group_size: int = 3):
        self.min_group_size = min_group_size

    @property
    def hierarchy(self) -> tuple[tuple[str, tuple[str, ...]], ...]:
        return (
            (
                "Land × Monat × Tagtyp × Stunde",
                (COUNTRY_COLUMN, "local_month", "day_type", "local_hour"),
            ),
            (
                "Land × Monat × Wochenendklasse × Stunde",
                (COUNTRY_COLUMN, "local_month", "is_weekend", "local_hour"),
            ),
            (
                "Land × Wochenendklasse × Stunde",
                (COUNTRY_COLUMN, "is_weekend", "local_hour"),
            ),
            ("Land × Stunde", (COUNTRY_COLUMN, "local_hour")),
        )

    def fit(self, X: pd.DataFrame, y: Sequence[float]):
        required = {column for _, columns in self.hierarchy for column in columns}
        _require_columns(X, required)
        target = pd.Series(np.asarray(y, dtype=float), index=X.index, name="_target")
        data = X.copy()
        data["_target"] = target
        self.lookups_: list[tuple[str, tuple[str, ...], pd.Series]] = []

        for level_index, (label, columns) in enumerate(self.hierarchy):
            grouped = data.groupby(list(columns), observed=True)["_target"].agg(
                ["mean", "size"]
            )
            means = grouped["mean"]
            if level_index == 0:
                means = means.where(grouped["size"].ge(self.min_group_size)).dropna()
            self.lookups_.append((label, columns, means))

        self.country_means_ = data.groupby(COUNTRY_COLUMN, observed=True)[
            "_target"
        ].mean()
        return self

    def predict_with_levels(self, X: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        check_is_fitted(self, ("lookups_", "country_means_"))
        predictions = np.full(len(X), np.nan, dtype=float)
        levels = np.full(len(X), "", dtype=object)

        for label, columns, lookup in self.lookups_:
            keys = pd.MultiIndex.from_frame(X.loc[:, list(columns)])
            candidates = lookup.reindex(keys).to_numpy(dtype=float)
            mask = np.isnan(predictions) & ~np.isnan(candidates)
            predictions[mask] = candidates[mask]
            levels[mask] = label

        country_fallback = X[COUNTRY_COLUMN].map(self.country_means_).to_numpy(dtype=float)
        mask = np.isnan(predictions)
        predictions[mask] = country_fallback[mask]
        levels[mask] = "Ländermittelwert"

        if np.isnan(predictions).any():
            raise ValueError("Kalender-Baseline konnte nicht alle Zeilen vorhersagen.")
        return predictions, levels

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.predict_with_levels(X)[0]


class CountryScaledRegressor(BaseEstimator, RegressorMixin):
    """Trainiert ein gemeinsames Modell auf länderweise skalierten Zielwerten."""

    def __init__(self, regressor, feature_columns: Sequence[str]):
        self.regressor = regressor
        self.feature_columns = feature_columns

    def fit(self, X: pd.DataFrame, y: Sequence[float]):
        _require_columns(X, (COUNTRY_COLUMN, *self.feature_columns))
        target = pd.Series(np.asarray(y, dtype=float), index=X.index)
        self.country_scales_ = target.groupby(X[COUNTRY_COLUMN]).mean().to_dict()
        row_scales = X[COUNTRY_COLUMN].map(self.country_scales_).to_numpy(dtype=float)
        if np.any(row_scales <= 0):
            raise ValueError("Länderskalen müssen positiv sein.")

        self.regressor_ = clone(self.regressor)
        self.regressor_.fit(X.loc[:, list(self.feature_columns)], target / row_scales)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        check_is_fitted(self, ("country_scales_", "regressor_"))
        _require_columns(X, (COUNTRY_COLUMN, *self.feature_columns))
        row_scales = X[COUNTRY_COLUMN].map(self.country_scales_)
        if row_scales.isna().any():
            unknown = sorted(X.loc[row_scales.isna(), COUNTRY_COLUMN].unique())
            raise ValueError(f"Unbekannte Länder bei der Vorhersage: {unknown}")
        scaled = self.regressor_.predict(X.loc[:, list(self.feature_columns)])
        return np.maximum(np.asarray(scaled, dtype=float), 0.0) * row_scales.to_numpy()


def make_ridge_estimator(
    *,
    alpha: float,
    include_weather: bool,
    include_holiday: bool = True,
) -> CountryScaledRegressor:
    """Erzeugt eine vollständige Ridge-Inferenzpipeline."""

    numeric_features = list(CYCLICAL_FEATURES)
    if include_holiday:
        numeric_features.append("is_holiday")
    if include_weather:
        numeric_features.extend(WEATHER_FEATURES)

    feature_columns = ("calendar_key", *numeric_features)
    preprocessing = ColumnTransformer(
        [
            (
                "calendar",
                OneHotEncoder(handle_unknown="ignore"),
                ["calendar_key"],
            ),
            ("numeric", StandardScaler(), numeric_features),
        ]
    )
    pipeline = Pipeline(
        [
            ("preprocessing", preprocessing),
            ("regressor", Ridge(alpha=alpha)),
        ]
    )
    return CountryScaledRegressor(pipeline, feature_columns)


def make_hgb_estimator(
    *,
    include_weather: bool,
    include_holiday: bool = True,
    learning_rate: float = 0.1,
    max_leaf_nodes: int = 31,
    max_iter: int = 300,
    min_samples_leaf: int = 40,
    l2_regularization: float = 1.0,
    loss: str = "absolute_error",
    random_state: int = 42,
) -> CountryScaledRegressor:
    """Erzeugt eine vollständige Histogram-Gradient-Boosting-Pipeline."""

    numeric_features = list(HGB_CALENDAR_FEATURES)
    if include_holiday:
        numeric_features.append("is_holiday")
    if include_weather:
        numeric_features.extend(WEATHER_FEATURES)
    feature_columns = (COUNTRY_COLUMN, *numeric_features)

    preprocessing = ColumnTransformer(
        [
            (
                "country",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                [COUNTRY_COLUMN],
            ),
            ("numeric", "passthrough", numeric_features),
        ],
        sparse_threshold=0,
    )
    regressor = HistGradientBoostingRegressor(
        loss=loss,
        learning_rate=learning_rate,
        max_leaf_nodes=max_leaf_nodes,
        max_iter=max_iter,
        min_samples_leaf=min_samples_leaf,
        l2_regularization=l2_regularization,
        early_stopping=False,
        random_state=random_state,
    )
    pipeline = Pipeline(
        [
            ("preprocessing", preprocessing),
            ("regressor", regressor),
        ]
    )
    return CountryScaledRegressor(pipeline, feature_columns)


def smape(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    """Symmetrischer mittlerer absoluter prozentualer Fehler in Prozent."""

    actual = np.asarray(y_true, dtype=float)
    predicted = np.asarray(y_pred, dtype=float)
    denominator = np.abs(actual) + np.abs(predicted)
    terms = np.divide(
        2.0 * np.abs(actual - predicted),
        denominator,
        out=np.zeros_like(denominator, dtype=float),
        where=denominator > 0,
    )
    return float(100.0 * np.mean(terms))


def regression_metrics_by_country(
    y_true: Sequence[float],
    y_pred: Sequence[float],
    countries: Sequence[str],
) -> pd.DataFrame:
    """Berechnet Pflichtmetriken je Land."""

    data = pd.DataFrame(
        {
            "country": np.asarray(countries),
            "actual": np.asarray(y_true, dtype=float),
            "prediction": np.asarray(y_pred, dtype=float),
        }
    )
    rows: list[dict[str, float | str | int]] = []
    for country, group in data.groupby("country", observed=True):
        mae = mean_absolute_error(group["actual"], group["prediction"])
        denominator = float(group["actual"].abs().mean())
        rows.append(
            {
                "country": country,
                "n": len(group),
                "MAE_MW": mae,
                "RMSE_MW": root_mean_squared_error(
                    group["actual"], group["prediction"]
                ),
                "nMAE": mae / denominator,
                "sMAPE_pct": smape(group["actual"], group["prediction"]),
                "R2": r2_score(group["actual"], group["prediction"]),
            }
        )
    return pd.DataFrame(rows).sort_values("country").reset_index(drop=True)


def regression_metrics(
    y_true: Sequence[float],
    y_pred: Sequence[float],
    countries: Sequence[str],
) -> tuple[dict[str, float | int], pd.DataFrame]:
    """Berechnet gepoolte Kennzahlen und den primären Makro-nMAE."""

    actual = np.asarray(y_true, dtype=float)
    predicted = np.asarray(y_pred, dtype=float)
    by_country = regression_metrics_by_country(actual, predicted, countries)
    summary: dict[str, float | int] = {
        "n": len(actual),
        "MAE_MW": mean_absolute_error(actual, predicted),
        "RMSE_MW": root_mean_squared_error(actual, predicted),
        "macro_nMAE": float(by_country["nMAE"].mean()),
        "sMAPE_pct": smape(actual, predicted),
        "R2": r2_score(actual, predicted),
    }
    return summary, by_country


def relative_improvement(candidate: float, reference: float) -> float:
    """Relative Fehlerreduktion eines Kandidaten gegenüber einer Referenz in Prozent."""

    if reference <= 0:
        raise ValueError("Der Referenzfehler muss positiv sein.")
    return float(100.0 * (1.0 - candidate / reference))
