from __future__ import annotations

import unittest

import numpy as np

from deep_hedging.statistics import (
    empirical_cvar,
    paired_cvar_improvement_bootstrap,
    paired_mean_improvement_bootstrap,
)


class StatisticsTests(unittest.TestCase):
    def test_empirical_cvar_uses_largest_tail(self) -> None:
        losses = np.arange(1.0, 101.0)
        self.assertAlmostEqual(empirical_cvar(losses, 0.95), 98.0)

    def test_empirical_cvar_uses_exact_five_percent_on_large_sample(self) -> None:
        losses = np.arange(1.0, 100_001.0)
        expected = float(np.mean(losses[-5_000:]))
        self.assertAlmostEqual(empirical_cvar(losses, 0.95), expected)

    def test_paired_bootstrap_is_zero_for_identical_losses(self) -> None:
        losses = np.linspace(-1.0, 3.0, 200)
        result = paired_cvar_improvement_bootstrap(
            losses,
            losses.copy(),
            n_bootstrap=50,
            seed=7,
        )
        self.assertEqual(result["point_improvement"], 0.0)
        self.assertEqual(result["ci_lower"], 0.0)
        self.assertEqual(result["ci_upper"], 0.0)

    def test_paired_bootstrap_detects_uniform_improvement(self) -> None:
        reference = np.linspace(-1.0, 3.0, 500)
        candidate = reference - 0.25
        result = paired_cvar_improvement_bootstrap(
            reference,
            candidate,
            n_bootstrap=100,
            seed=8,
        )
        self.assertAlmostEqual(float(result["point_improvement"]), 0.25)
        self.assertGreater(float(result["ci_lower"]), 0.24)

    def test_paired_mean_bootstrap_detects_uniform_improvement(self) -> None:
        reference = np.linspace(0.0, 10.0, 500)
        candidate = reference - 2.0
        result = paired_mean_improvement_bootstrap(
            reference,
            candidate,
            n_bootstrap=100,
            seed=9,
        )
        self.assertAlmostEqual(float(result["point_improvement"]), 2.0)
        self.assertAlmostEqual(float(result["ci_lower"]), 2.0)
        self.assertAlmostEqual(float(result["ci_upper"]), 2.0)


if __name__ == "__main__":
    unittest.main()
