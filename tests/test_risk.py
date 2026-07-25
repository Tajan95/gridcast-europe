from pathlib import Path
import sys

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from gridcast.risk import (
    brier_score,
    empirical_extreme_probabilities,
    extreme_day_probability,
    historical_quantile,
)


def test_historical_quantile_and_hourly_probabilities():
    assert historical_quantile([0, 10, 20, 30, 40], 0.95) == 38.0
    probabilities = empirical_extreme_probabilities(
        [80.0, 100.0],
        [-10.0, 0.0, 10.0],
        100.0,
    )
    assert np.allclose(probabilities, [0.0, 1 / 3])


def test_extreme_day_probability_preserves_residual_paths():
    probability = extreme_day_probability(
        [90.0, 90.0],
        [[0.0, 0.0], [20.0, -20.0]],
        100.0,
    )
    assert probability == 0.5


def test_brier_score():
    assert np.isclose(brier_score([0, 1], [0.2, 0.8]), 0.04)
