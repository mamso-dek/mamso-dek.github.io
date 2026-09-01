from __future__ import annotations

import math
import unittest

from deep_hedging.core import MarketConfig
from deep_hedging.train import TrainConfig, train_policy


class TrainingTests(unittest.TestCase):
    def test_short_training_loop_returns_finite_history(self) -> None:
        market = MarketConfig(maturity=5 / 252, n_steps=5)
        training = TrainConfig(
            epochs=2,
            batch_size=256,
            validation_size=512,
            model_seed=3101,
            train_seed=3201,
            validation_seed=3301,
        )
        policy, history, best_eta = train_policy(market, training, device="cpu")
        self.assertEqual(len(history), 2)
        self.assertTrue(math.isfinite(best_eta))
        self.assertTrue(all(math.isfinite(row["train_objective"]) for row in history))
        self.assertTrue(all(math.isfinite(row["cvar_loss_95"]) for row in history))
        self.assertGreater(sum(parameter.numel() for parameter in policy.parameters()), 0)


if __name__ == "__main__":
    unittest.main()
