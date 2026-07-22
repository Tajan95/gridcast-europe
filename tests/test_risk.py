import unittest

from gridcast.risk import (
    empirical_extreme_probabilities,
    extreme_day_probability,
    historical_quantile,
)
from gridcast.scenario import apply_structural_scenario


class RiskTests(unittest.TestCase):
    def test_historical_quantile_interpolates(self):
        self.assertEqual(historical_quantile(range(101), 0.95), 95.0)

    def test_hourly_extreme_probability(self):
        probabilities = empirical_extreme_probabilities(
            point_forecast_mw=[100.0],
            validation_residuals_mw=[-10.0, 0.0, 10.0],
            threshold_mw=105.0,
        )
        self.assertAlmostEqual(probabilities[0], 1 / 3)

    def test_daily_probability_uses_complete_paths(self):
        probability = extreme_day_probability(
            point_forecast_mw=[100.0, 100.0],
            validation_residual_paths_mw=[
                [0.0, 0.0],
                [10.0, 0.0],
                [-1.0, 11.0],
            ],
            threshold_mw=105.0,
        )
        self.assertAlmostEqual(probability, 2 / 3)

    def test_residual_path_length_must_match(self):
        with self.assertRaises(ValueError):
            extreme_day_probability([100.0, 101.0], [[0.0]], 105.0)


class ScenarioTests(unittest.TestCase):
    def test_structural_adjustments_are_explicit(self):
        scenario = apply_structural_scenario(
            temperature_adjusted_forecast_mw=[100.0, 200.0],
            demand_change_fraction=0.10,
            additional_data_centre_load_mw=5.0,
        )
        self.assertAlmostEqual(scenario[0], 115.0)
        self.assertAlmostEqual(scenario[1], 225.0)


if __name__ == "__main__":
    unittest.main()
