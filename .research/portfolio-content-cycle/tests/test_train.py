from __future__ import annotations

import math
import unittest

from deep_hedging.core import MarketConfig
from deep_hedging.model import HedgingPolicy
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

    def test_training_accepts_custom_policy_factory(self) -> None:
        market = MarketConfig(maturity=3 / 252, n_steps=3)
        training = TrainConfig(
            epochs=2,
            batch_size=128,
            validation_size=256,
            model_seed=4101,
            train_seed=4201,
            validation_seed=4301,
        )
        policy, history, _ = train_policy(
            market,
            training,
            device="cpu",
            policy_factory=lambda: HedgingPolicy(
                hidden_size=8, include_inventory=False
            ),
        )
        self.assertFalse(policy.include_inventory)
        self.assertEqual(policy.network[0].in_features, 2)
        self.assertEqual(len(history), 2)


if __name__ == "__main__":
    unittest.main()
