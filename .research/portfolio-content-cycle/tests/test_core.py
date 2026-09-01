from __future__ import annotations

import math
import unittest

import torch

from deep_hedging.core import (
    MarketConfig,
    black_scholes_call,
    black_scholes_delta_paths,
    leland_volatility,
    rockafellar_uryasev_cvar,
    simulate_gbm,
    strategy_pnl,
    summarize_pnl,
)
from deep_hedging.model import HedgingPolicy


class CoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = MarketConfig()

    def test_simulation_is_reproducible_and_positive(self) -> None:
        first = simulate_gbm(128, self.config, 1234, dtype=torch.float64)
        second = simulate_gbm(128, self.config, 1234, dtype=torch.float64)
        third = simulate_gbm(128, self.config, 1235, dtype=torch.float64)
        self.assertEqual(first.shape, (128, self.config.n_steps + 1))
        self.assertTrue(torch.equal(first, second))
        self.assertFalse(torch.equal(first, third))
        self.assertTrue(torch.all(first > 0))
        self.assertTrue(torch.all(first[:, 0] == self.config.s0))

    def test_risk_neutral_terminal_mean(self) -> None:
        paths = simulate_gbm(30_000, self.config, 5678, dtype=torch.float64)
        expected = self.config.s0 * math.exp(self.config.rate * self.config.maturity)
        self.assertLess(abs(float(paths[:, -1].mean()) - expected), 0.12)

    def test_black_scholes_price_matches_pilot(self) -> None:
        value = black_scholes_call(
            torch.tensor(self.config.s0, dtype=torch.float64),
            self.config.strike,
            torch.tensor(self.config.maturity, dtype=torch.float64),
            self.config.rate,
            self.config.sigma,
        )
        self.assertAlmostEqual(float(value), 2.7524171533585005, places=10)

    def test_delta_has_valid_shape_and_bounds(self) -> None:
        paths = simulate_gbm(64, self.config, 42)
        delta = black_scholes_delta_paths(paths, self.config)
        self.assertEqual(delta.shape, (64, self.config.n_steps))
        self.assertTrue(torch.all((delta >= 0) & (delta <= 1)))

    def test_leland_uses_round_trip_conversion(self) -> None:
        self.assertEqual(leland_volatility(self.config, 0.0), self.config.sigma)
        cost = 0.001
        expected = self.config.sigma * math.sqrt(
            1
            + math.sqrt(2 / math.pi)
            * (2 * cost)
            / (self.config.sigma * math.sqrt(self.config.dt))
        )
        adjusted = leland_volatility(self.config, cost)
        self.assertAlmostEqual(adjusted, expected, places=14)
        self.assertGreater(leland_volatility(self.config, 0.0025), adjusted)

    def test_zero_position_matches_unhedged_pnl(self) -> None:
        paths = torch.tensor([[100.0, 103.0, 106.0], [100.0, 98.0, 97.0]])
        positions = torch.zeros((2, 2))
        pnl, costs, turnover = strategy_pnl(paths, positions, 2.0, 0.005, 100.0)
        torch.testing.assert_close(pnl, torch.tensor([-4.0, 2.0]))
        torch.testing.assert_close(costs, torch.zeros(2))
        torch.testing.assert_close(turnover, torch.zeros(2))

    def test_transaction_cost_identity(self) -> None:
        paths = simulate_gbm(256, self.config, 99)
        positions = black_scholes_delta_paths(paths, self.config)
        _, costs, turnover = strategy_pnl(
            paths, positions, 2.75, 0.0025, self.config.strike
        )
        torch.testing.assert_close(costs, 0.0025 * turnover)

    def test_rockafellar_uryasev_objective(self) -> None:
        losses = torch.tensor([0.0, 1.0, 2.0, 3.0])
        eta = torch.tensor(1.0)
        value = rockafellar_uryasev_cvar(losses, eta, 0.5)
        self.assertAlmostEqual(float(value), 2.5)

    def test_delta_reduces_risk_without_costs(self) -> None:
        paths = simulate_gbm(10_000, self.config, 2026)
        premium = black_scholes_call(
            torch.tensor(self.config.s0),
            self.config.strike,
            torch.tensor(self.config.maturity),
            self.config.rate,
            self.config.sigma,
        )
        zeros = torch.zeros_like(paths[:, :-1])
        delta = black_scholes_delta_paths(paths, self.config)
        pnl_zero, costs_zero, turnover_zero = strategy_pnl(
            paths, zeros, premium, 0.0, self.config.strike
        )
        pnl_delta, costs_delta, turnover_delta = strategy_pnl(
            paths, delta, premium, 0.0, self.config.strike
        )
        unhedged = summarize_pnl(pnl_zero, costs_zero, turnover_zero)
        hedged = summarize_pnl(pnl_delta, costs_delta, turnover_delta)
        self.assertLess(hedged["std_pnl"], 0.2 * unhedged["std_pnl"])
        self.assertLess(hedged["cvar_loss_95"], 0.2 * unhedged["cvar_loss_95"])

    def test_policy_is_bounded_and_differentiable(self) -> None:
        torch.manual_seed(7)
        paths = simulate_gbm(128, self.config, 77)
        policy = HedgingPolicy(hidden_size=16)
        positions = policy(paths, self.config)
        self.assertEqual(positions.shape, (128, self.config.n_steps))
        self.assertTrue(torch.all((positions > 0) & (positions < 1.25)))
        premium = torch.tensor(2.75)
        pnl, _, _ = strategy_pnl(
            paths, positions, premium, 0.0025, self.config.strike
        )
        eta = torch.tensor(1.0, requires_grad=True)
        objective = rockafellar_uryasev_cvar(-pnl, eta, 0.95)
        objective.backward()
        gradients = [p.grad for p in policy.parameters() if p.grad is not None]
        self.assertTrue(gradients)
        self.assertTrue(all(torch.all(torch.isfinite(g)) for g in gradients))


if __name__ == "__main__":
    unittest.main()
