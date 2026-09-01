"""Références classiques sur un test Monte-Carlo commun."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import torch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from deep_hedging.core import (  # noqa: E402
    MarketConfig,
    black_scholes_delta_paths,
    leland_volatility,
    simulate_gbm,
    strategy_pnl,
    summarize_pnl,
)
from deep_hedging.train import initial_premium  # noqa: E402


def main() -> None:
    market = MarketConfig()
    n_paths = 100_000
    seed = 20263000
    paths = simulate_gbm(n_paths, market, seed, device="cpu")
    premium = initial_premium(market)
    zeros = torch.zeros_like(paths[:, :-1])
    ordinary_delta = black_scholes_delta_paths(paths, market)
    costs = (0.0, 0.0010, 0.0025, 0.0050)

    results: dict[str, object] = {
        "status": "références Monte-Carlo internes — non publiées",
        "n_paths": n_paths,
        "seed": seed,
        "market": market.__dict__,
        "premium": float(premium),
        "cost_convention": "coût aller simple, liquidation terminale incluse",
        "strategies": {},
    }
    strategies = results["strategies"]
    assert isinstance(strategies, dict)
    for cost in costs:
        leland_sigma = leland_volatility(market, cost)
        leland_delta = black_scholes_delta_paths(
            paths, market, volatility=leland_sigma
        )
        for name, positions in (
            ("sans_couverture", zeros),
            ("delta_black_scholes", ordinary_delta),
            ("delta_leland", leland_delta),
        ):
            pnl, transaction_cost, turnover = strategy_pnl(
                paths, positions, premium, cost, market.strike
            )
            row = summarize_pnl(pnl, transaction_cost, turnover)
            row["leland_sigma"] = leland_sigma if name == "delta_leland" else None
            strategies[f"{name}__{cost:.4f}"] = row

    output = Path(__file__).with_name("classical-baselines.json")
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    for cost in costs:
        print(f"\nCoût {cost * 10_000:.0f} pb")
        for name in ("sans_couverture", "delta_black_scholes", "delta_leland"):
            row = strategies[f"{name}__{cost:.4f}"]
            print(
                f"  {name:21s} CVaR={row['cvar_loss_95']:.4f} "
                f"P&L moyen={row['mean_pnl']:.4f} "
                f"coût={row['mean_transaction_cost']:.4f}"
            )


if __name__ == "__main__":
    main()
