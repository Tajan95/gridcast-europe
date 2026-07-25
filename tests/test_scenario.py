from datetime import date
from pathlib import Path
import sys

import joblib
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from gridcast.scenario import (
    apply_structural_scenario,
    build_scenario_features,
    predict_scenario_day,
    summarize_scenario,
)


def _climatology() -> pd.DataFrame:
    hours = np.arange(24)
    return pd.DataFrame(
        {
            "country": "DE",
            "local_month": 1,
            "local_hour": hours,
            "temperature_c_median": np.linspace(-2, 4, 24),
            "radiation_direct_wm2_median": np.maximum(
                0, 300 * np.sin(np.pi * (hours - 6) / 12)
            ),
            "radiation_diffuse_wm2_median": np.maximum(
                0, 80 * np.sin(np.pi * (hours - 6) / 12)
            ),
        }
    )


def test_build_scenario_features_has_complete_model_schema():
    frame = build_scenario_features(
        _climatology(),
        country="DE",
        target_date=date(2030, 1, 15),
        temperature_delta_c=2.0,
    )
    assert len(frame) == 24
    assert frame["local_hour"].tolist() == list(range(24))
    assert frame["temperature_c"].iloc[0] == 0.0
    assert {
        "is_holiday",
        "temperature_sq",
        "heating_degrees",
        "cooling_degrees",
        "year_sin",
        "year_cos",
    }.issubset(frame.columns)


def test_structural_scenario_is_explicit_and_monotonic():
    result = apply_structural_scenario(
        [100.0, 200.0],
        demand_change_fraction=0.10,
        additional_data_centre_load_mw=50.0,
    )
    assert np.allclose(result, [160.0, 270.0])


def test_final_model_predicts_complete_scenario():
    model_path = PROJECT_ROOT / "models" / "gridcast_final_2015_2019.joblib"
    climate_path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "opsd_weather_climatology_1980_2019.csv.gz"
    )
    if not (model_path.is_file() and climate_path.is_file()):
        return
    model = joblib.load(model_path)
    climate = pd.read_csv(climate_path)
    scenario = predict_scenario_day(
        model,
        climate,
        country="DE",
        target_date=date(2030, 1, 15),
        temperature_delta_c=2.0,
        demand_change_fraction=0.1,
        additional_data_centre_load_mw=500.0,
    )
    summary = summarize_scenario(scenario)
    assert len(scenario) == 24
    assert np.isfinite(scenario["scenario_prediction_mw"]).all()
    assert summary["scenario_peak_mw"] > summary["base_peak_mw"]
