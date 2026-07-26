from pathlib import Path
import sys

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from gridcast.formatting import format_energy_mwh, format_power_mw


@pytest.mark.parametrize(
    ("value_mw", "expected"),
    [
        (999.5, "999,5 MW"),
        (1_000, "1 GW"),
        (88_300, "88,3 GW"),
        (999_999, "999,999 GW"),
        (1_000_000, "1 TW"),
        (-1_250_000, "-1,25 TW"),
    ],
)
def test_power_units_scale_at_thousand_steps(value_mw, expected):
    assert format_power_mw(value_mw) == expected


@pytest.mark.parametrize(
    ("value_mwh", "expected"),
    [
        (999.5, "999,5 MWh"),
        (1_000, "1 GWh"),
        (288_000, "288 GWh"),
        (999_999, "999,999 GWh"),
        (1_000_000, "1 TWh"),
        (1_882_151, "1,882 TWh"),
    ],
)
def test_energy_units_scale_at_thousand_steps(value_mwh, expected):
    assert format_energy_mwh(value_mwh) == expected


@pytest.mark.parametrize("formatter", [format_power_mw, format_energy_mwh])
def test_unit_formatters_reject_non_finite_values(formatter):
    with pytest.raises(ValueError):
        formatter(float("inf"))
