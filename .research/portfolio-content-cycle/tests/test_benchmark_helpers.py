from __future__ import annotations

from pathlib import Path
import sys
import unittest


BENCHMARKS = Path(__file__).resolve().parents[1] / "benchmarks"
sys.path.insert(0, str(BENCHMARKS))

from extreme_cost_multiseed import aggregate_runs  # noqa: E402


def make_run(cvar: float, improvement: float) -> dict[str, object]:
    return {
        "development_metrics": {
            "neural": {
                "cvar_loss_95": cvar,
                "std_pnl": 0.5,
                "mean_transaction_cost": 0.2,
                "mean_turnover_notional": 200.0,
            }
        },
        "paired_bootstrap_versus_leland": {
            "point_improvement": improvement,
            "ci_lower": improvement - 0.01,
        },
    }


class BenchmarkHelperTests(unittest.TestCase):
    def test_aggregate_accepts_incremental_single_run(self) -> None:
        first = aggregate_runs([make_run(1.0, 0.1)])
        self.assertIsNone(first["cvar_loss_95"]["sample_std"])
        self.assertIsNone(
            first["cvar_improvement_versus_leland"]["sample_std"]
        )

        complete = aggregate_runs(
            [make_run(1.0, 0.1), make_run(1.2, 0.2)]
        )
        self.assertAlmostEqual(complete["cvar_loss_95"]["mean"], 1.1)
        self.assertGreater(complete["cvar_loss_95"]["sample_std"], 0)


if __name__ == "__main__":
    unittest.main()
