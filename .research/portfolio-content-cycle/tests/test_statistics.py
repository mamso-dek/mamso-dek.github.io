from __future__ import annotations

import unittest

import numpy as np

from deep_hedging.statistics import (
    empirical_cvar,
    paired_cvar_improvement_bootstrap,
)


class StatisticsTests(unittest.TestCase):
    def test_empirical_cvar_uses_largest_tail(self) -> None:
        losses = np.arange(1.0, 101.0)
        self.assertAlmostEqual(empirical_cvar(losses, 0.95), 98.0)

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


if __name__ == "__main__":
    unittest.main()
