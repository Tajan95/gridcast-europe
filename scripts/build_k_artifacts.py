"""Erzeugt die kompakten Deployment-Artefakte der K-Phase.

Voraussetzungen:

1. ``01_data_import_merge_eda.ipynb`` wurde ausgeführt.
2. ``03_conclude_compare.ipynb`` hat das finale App-Modell erzeugt.

Das Skript verändert weder Modellfamilie noch Hyperparameter. Es reproduziert
den C-Backtest für die App, kalibriert den explorativen Extremzustandsindikator
mit 2018 und schreibt ausschließlich kompakte Deployment-Daten.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sys

import joblib
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from gridcast.modeling import (
    CalendarBaseline,
    CountryMeanBaseline,
    add_modeling_features,
    make_hgb_estimator,
    regression_metrics,
)
from gridcast.risk import brier_score, extreme_day_probability
from gridcast.scenario import predict_scenario_day, summarize_scenario


MODEL_DATA_PATH = (
    PROJECT_ROOT / "data" / "processed" / "opsd_model_data_2015_2019.csv.gz"
)
CLIMATOLOGY_SOURCE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "opsd_weather_climatology_1980_2019.csv.gz"
)
FINAL_MODEL_PATH = (
    PROJECT_ROOT / "models" / "gridcast_final_2015_2019.joblib"
)
SELECTION_PATH = PROJECT_ROOT / "reports" / "a3" / "a3_selection.json"
C_REPORT_PATH = PROJECT_ROOT / "reports" / "c" / "c_conclusion.json"

APP_DATA_DIR = PROJECT_ROOT / "data" / "app"
BACKTEST_PATH = APP_DATA_DIR / "backtest_2019.csv.gz"
CLIMATOLOGY_TARGET_PATH = APP_DATA_DIR / "weather_climatology_1980_2019.csv.gz"
RISK_PATH = APP_DATA_DIR / "risk_calibration_2018.npz"
K_REPORT_PATH = PROJECT_ROOT / "reports" / "k_deployment.json"


MODEL_COLUMNS = [
    "utc_timestamp",
    "country",
    "load_mw",
    "temperature_c",
    "radiation_direct_wm2",
    "radiation_diffuse_wm2",
    "local_date",
    "local_hour",
    "local_weekday",
    "local_month",
    "is_weekend",
    "season",
    "hour_sin",
    "hour_cos",
    "weekday_sin",
    "weekday_cos",
    "year_sin",
    "year_cos",
    "temperature_sq",
    "heating_degrees",
    "cooling_degrees",
    "split",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def selected_model(selection: dict):
    parameters = dict(selection["hyperparameters"])
    parameters.pop("early_stopping", None)
    return make_hgb_estimator(
        include_weather=True,
        include_holiday=True,
        **parameters,
    )


def complete_residual_paths(frame: pd.DataFrame) -> np.ndarray:
    """Liefert nur lokale Tage mit genau einer Beobachtung je Stunde 0–23."""

    paths = []
    for _, group in frame.groupby("local_date", sort=True):
        ordered = group.sort_values("local_hour")
        if (
            len(ordered) == 24
            and ordered["local_hour"].tolist() == list(range(24))
        ):
            paths.append(ordered["residual_mw"].to_numpy(dtype=float))
    if not paths:
        raise ValueError("Keine vollständigen 24-Stunden-Residualpfade gefunden.")
    return np.vstack(paths)


def evaluate_daily_risk(
    backtest: pd.DataFrame,
    residual_paths: np.ndarray,
    threshold: float,
) -> dict[str, float | int]:
    probabilities: list[float] = []
    events: list[int] = []
    for _, day in backtest.groupby("local_date", sort=True):
        day = day.sort_values("local_hour")
        if len(day) != 24 or day["local_hour"].tolist() != list(range(24)):
            continue
        probabilities.append(
            extreme_day_probability(
                day["hgb_prediction_mw"].to_numpy(dtype=float),
                residual_paths,
                threshold,
            )
        )
        events.append(int(day["actual_load_mw"].max() > threshold))
    return {
        "complete_test_days": len(events),
        "observed_event_rate": float(np.mean(events)),
        "mean_predicted_probability": float(np.mean(probabilities)),
        "brier_score": float(brier_score(events, probabilities)),
    }


def main() -> None:
    required = [
        MODEL_DATA_PATH,
        CLIMATOLOGY_SOURCE_PATH,
        FINAL_MODEL_PATH,
        SELECTION_PATH,
        C_REPORT_PATH,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Erforderliche Vorartefakte fehlen: {missing}")

    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    K_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    selection = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
    c_report = json.loads(C_REPORT_PATH.read_text(encoding="utf-8"))
    model_data = pd.read_csv(
        MODEL_DATA_PATH,
        usecols=MODEL_COLUMNS,
        parse_dates=["utc_timestamp"],
    )
    model_data = add_modeling_features(model_data)

    train = model_data.loc[model_data["split"].eq("train")].copy()
    validation = model_data.loc[model_data["split"].eq("validation")].copy()
    refit = model_data.loc[
        model_data["split"].isin(["train", "validation"])
    ].copy()
    test = model_data.loc[model_data["split"].eq("test")].copy()

    if not (
        train["utc_timestamp"].dt.year.max() == 2017
        and validation["utc_timestamp"].dt.year.eq(2018).all()
        and test["utc_timestamp"].dt.year.eq(2019).all()
    ):
        raise AssertionError("Der verbindliche chronologische Split wurde verletzt.")

    # Reproduktion des unveränderten C-Backtests für die interaktive App.
    c_model = selected_model(selection)
    calendar = CalendarBaseline(min_group_size=3)
    country_mean = CountryMeanBaseline()
    c_model.fit(refit, refit["load_mw"])
    calendar.fit(refit, refit["load_mw"])
    country_mean.fit(refit, refit["load_mw"])

    hgb_prediction = c_model.predict(test)
    calendar_prediction = calendar.predict(test)
    mean_prediction = country_mean.predict(test)
    c_summary, _ = regression_metrics(
        test["load_mw"],
        hgb_prediction,
        test["country"],
    )
    expected_nmae = c_report["test_metrics"]["macro_nMAE"]
    if not np.isclose(c_summary["macro_nMAE"], expected_nmae, atol=1e-12):
        raise AssertionError("Der reproduzierte C-Backtest weicht vom Abschlussreport ab.")

    backtest = test[
        [
            "utc_timestamp",
            "country",
            "local_date",
            "local_hour",
            "temperature_c",
        ]
    ].copy()
    backtest["actual_load_mw"] = test["load_mw"].to_numpy(dtype=float)
    backtest["hgb_prediction_mw"] = hgb_prediction
    backtest["calendar_prediction_mw"] = calendar_prediction
    backtest["mean_prediction_mw"] = mean_prediction
    backtest.sort_values(["country", "utc_timestamp"], inplace=True)
    backtest.to_csv(
        BACKTEST_PATH,
        index=False,
        compression={"method": "gzip", "compresslevel": 9, "mtime": 0},
    )

    # Kalibrierung ausschließlich mit Training/Validierung; 2019 dient zur
    # nachgelagerten Prüfung und verändert die Methode nicht.
    validation_model = selected_model(selection)
    validation_model.fit(train, train["load_mw"])
    validation_prediction = validation_model.predict(validation)
    validation_residuals = validation[
        ["country", "local_date", "local_hour"]
    ].copy()
    validation_residuals["residual_mw"] = (
        validation["load_mw"].to_numpy(dtype=float) - validation_prediction
    )

    risk_arrays: dict[str, np.ndarray] = {}
    risk_evaluation: dict[str, dict] = {}
    for country in selection["countries"]:
        train_country = train.loc[train["country"].eq(country), "load_mw"]
        residual_country = validation_residuals.loc[
            validation_residuals["country"].eq(country)
        ]
        paths = complete_residual_paths(residual_country)
        threshold_q95 = float(train_country.quantile(0.95))
        threshold_q99 = float(train_country.quantile(0.99))

        risk_arrays[f"threshold_q95_{country}"] = np.array(
            [threshold_q95], dtype=float
        )
        risk_arrays[f"threshold_q99_{country}"] = np.array(
            [threshold_q99], dtype=float
        )
        risk_arrays[f"residual_paths_{country}"] = paths
        country_backtest = backtest.loc[backtest["country"].eq(country)]
        risk_evaluation[country] = {
            "residual_days_2018": int(len(paths)),
            "threshold_q95_mw": threshold_q95,
            "threshold_q99_mw": threshold_q99,
            "q95_test_2019": evaluate_daily_risk(
                country_backtest,
                paths,
                threshold_q95,
            ),
        }
    np.savez_compressed(RISK_PATH, **risk_arrays)

    shutil.copyfile(CLIMATOLOGY_SOURCE_PATH, CLIMATOLOGY_TARGET_PATH)

    # Frischer Lade- und Inferenztest des finalen Deployment-Modells.
    final_model = joblib.load(FINAL_MODEL_PATH)
    climatology = pd.read_csv(CLIMATOLOGY_TARGET_PATH)
    scenario = predict_scenario_day(
        final_model,
        climatology,
        country="DE",
        target_date="2030-01-15",
        temperature_delta_c=2.0,
        demand_change_fraction=0.10,
        additional_data_centre_load_mw=500.0,
    )
    scenario_summary = summarize_scenario(scenario)
    if not (
        len(scenario) == 24
        and np.isfinite(scenario["scenario_prediction_mw"]).all()
        and scenario_summary["scenario_peak_mw"]
        > scenario_summary["base_peak_mw"]
    ):
        raise AssertionError("Der Deployment-Szenariotest ist fehlgeschlagen.")

    app_assets = {}
    for path, rows in [
        (BACKTEST_PATH, len(backtest)),
        (CLIMATOLOGY_TARGET_PATH, len(climatology)),
        (RISK_PATH, sum(len(value) for value in risk_arrays.values())),
    ]:
        app_assets[str(path.relative_to(PROJECT_ROOT))] = {
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
            "rows_or_arrays": int(rows),
        }

    report = {
        "project": "GridCast Europe",
        "phase": "K",
        "status": "deployment_ready",
        "created_on": "2026-07-25",
        "model": {
            "path": str(FINAL_MODEL_PATH.relative_to(PROJECT_ROOT)),
            "size_bytes": FINAL_MODEL_PATH.stat().st_size,
            "sha256": sha256(FINAL_MODEL_PATH),
            "training_period": "2015-01-01/2019-12-31",
            "independent_quality_source": "C-Backtest: Refit 2015–2018, Test 2019",
        },
        "backtest": {
            "rows": int(len(backtest)),
            "macro_nMAE": float(c_summary["macro_nMAE"]),
            "matches_c_report": True,
        },
        "risk_indicator": {
            "meaning": "historische Quantilsüberschreitung; keine Blackout-Wahrscheinlichkeit",
            "threshold_reference": "Training 2015–2017",
            "residual_reference": "Validierung 2018",
            "test_reference": "2019",
            "evaluation": risk_evaluation,
        },
        "scenario_smoke_test": {
            "country": "DE",
            "date": "2030-01-15",
            "temperature_delta_c": 2.0,
            "demand_change_pct": 10.0,
            "additional_data_centre_load_mw": 500.0,
            **scenario_summary,
        },
        "app_assets": app_assets,
        "verification": {
            "passed": [
                "C-Backtest exakt reproduziert",
                "finales Modell frisch geladen",
                "24 Szenariostunden vorhergesagt",
                "keine nicht-endlichen Prognosen",
                "Risiko-Residualpfade länderweise vollständig",
            ]
        },
    }
    K_REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Backtest: {BACKTEST_PATH} ({len(backtest):,} Zeilen)")
    print(f"Klimatologie: {CLIMATOLOGY_TARGET_PATH} ({len(climatology):,} Zeilen)")
    print(f"Risikokalibrierung: {RISK_PATH}")
    print(f"K-Report: {K_REPORT_PATH}")
    print(f"Modell SHA-256: {sha256(FINAL_MODEL_PATH)}")


if __name__ == "__main__":
    main()
