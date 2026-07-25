from datetime import date

import numpy as np
import pandas as pd

from gridcast.modeling import (
    CalendarBaseline,
    CountryMeanBaseline,
    add_modeling_features,
    national_holidays,
    regression_metrics,
)


def test_national_holidays_cover_fixed_and_movable_dates():
    german_2018 = national_holidays("DE", 2018)
    polish_2018 = national_holidays("PL", 2018)

    assert date(2018, 1, 1) in german_2018
    assert date(2018, 3, 30) in german_2018  # Karfreitag
    assert date(2018, 5, 31) in polish_2018  # Fronleichnam
    assert date(2018, 2, 1) not in german_2018


def test_modeling_features_prioritize_holiday_over_weekend():
    frame = pd.DataFrame(
        {
            "country": ["DE", "FR"],
            "local_date": ["2018-01-01", "2018-01-06"],
            "local_hour": [12, 12],
            "local_month": [1, 1],
            "is_weekend": [0, 1],
        }
    )

    result = add_modeling_features(frame)

    assert result.loc[0, "day_type"] == "holiday"
    assert result.loc[1, "day_type"] == "weekend"
    assert all(
        key.startswith(country)
        for key, country in zip(result["calendar_key"], result["country"])
    )


def test_baselines_predict_all_rows_with_fallbacks():
    X_train = pd.DataFrame(
        {
            "country": ["DE"] * 6,
            "local_month": [1] * 6,
            "day_type": ["weekday"] * 6,
            "is_weekend": [0] * 6,
            "local_hour": [8, 8, 8, 9, 9, 9],
        }
    )
    y_train = np.array([10, 12, 14, 20, 22, 24], dtype=float)
    X_validation = pd.DataFrame(
        {
            "country": ["DE", "DE"],
            "local_month": [1, 2],
            "day_type": ["weekday", "holiday"],
            "is_weekend": [0, 0],
            "local_hour": [8, 9],
        }
    )

    mean_model = CountryMeanBaseline().fit(X_train, y_train)
    calendar_model = CalendarBaseline(min_group_size=3).fit(X_train, y_train)
    calendar_prediction, levels = calendar_model.predict_with_levels(X_validation)

    assert np.allclose(mean_model.predict(X_validation), 17.0)
    assert np.allclose(calendar_prediction, [12.0, 22.0])
    assert levels[0] == "Land × Monat × Tagtyp × Stunde"
    assert levels[1] == "Land × Wochenendklasse × Stunde"


def test_macro_nmae_weights_countries_equally():
    actual = np.array([100.0, 100.0, 1000.0, 1000.0])
    predicted = np.array([90.0, 90.0, 900.0, 900.0])
    countries = np.array(["A", "A", "B", "B"])

    summary, by_country = regression_metrics(actual, predicted, countries)

    assert np.isclose(summary["macro_nMAE"], 0.1)
    assert np.allclose(by_country["nMAE"], 0.1)
