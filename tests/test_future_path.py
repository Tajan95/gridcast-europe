import pytest

from gridcast.future_path import (
    FUTURE_PATH_BASE_YEAR,
    FUTURE_PATH_END_YEAR,
    interpolate_future_path,
)


def test_future_path_starts_at_the_unmodified_2020_reference():
    assumptions = interpolate_future_path(FUTURE_PATH_BASE_YEAR)

    assert assumptions.year == 2020
    assert assumptions.progress == 0.0
    assert assumptions.temperature_delta_c == 0.0
    assert assumptions.demand_change_pct == 0
    assert assumptions.data_centre_mw == 0
    assert assumptions.direct_radiation_pct == 100
    assert assumptions.diffuse_radiation_pct == 100


def test_future_path_reaches_the_documented_2050_endpoints():
    assumptions = interpolate_future_path(FUTURE_PATH_END_YEAR)

    assert assumptions.year == 2050
    assert assumptions.progress == 1.0
    assert assumptions.temperature_delta_c == 1.5
    assert assumptions.demand_change_pct == 35
    assert assumptions.data_centre_mw == 2_000
    assert assumptions.direct_radiation_pct == 102
    assert assumptions.diffuse_radiation_pct == 102


def test_future_path_interpolates_and_rounds_to_widget_steps():
    assumptions = interpolate_future_path(2030)

    assert assumptions.temperature_delta_c == 0.5
    assert assumptions.demand_change_pct == 12
    assert assumptions.data_centre_mw == 700
    assert assumptions.direct_radiation_pct == 101
    assert assumptions.diffuse_radiation_pct == 101


@pytest.mark.parametrize("year", [2019, 2051, 2030.5])
def test_future_path_rejects_invalid_years(year):
    with pytest.raises(ValueError):
        interpolate_future_path(year)


def test_future_path_rejects_boolean_year():
    with pytest.raises(TypeError):
        interpolate_future_path(True)
