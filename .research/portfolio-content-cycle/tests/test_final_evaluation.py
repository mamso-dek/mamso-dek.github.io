from __future__ import annotations

from pathlib import Path
import sys
import unittest

import torch


BENCHMARKS = Path(__file__).resolve().parents[1] / "benchmarks"
sys.path.insert(0, str(BENCHMARKS))

from final_evaluation import (  # noqa: E402
    CONFIRMATION_PHRASE,
    loss_quantiles,
    validate_authorization,
)


class FinalEvaluationTests(unittest.TestCase):
    def test_opening_requires_flag_and_exact_phrase(self) -> None:
        validate_authorization(False, "")
        with self.assertRaises(ValueError):
            validate_authorization(False, CONFIRMATION_PHRASE)
        with self.assertRaises(ValueError):
            validate_authorization(True, "incorrect")
        validate_authorization(True, CONFIRMATION_PHRASE)

    def test_loss_quantiles_are_named_and_ordered(self) -> None:
        pnl = -torch.arange(1.0, 101.0)
        quantiles = loss_quantiles(pnl)
        self.assertEqual(
            list(quantiles), ["q01", "q05", "q50", "q95", "q99", "q995"]
        )
        self.assertEqual(list(quantiles.values()), sorted(quantiles.values()))


if __name__ == "__main__":
    unittest.main()
