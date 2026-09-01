"""Convergence prolongée, bootstrap apparié et diagnostics de politique."""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys
import time

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
from deep_hedging.model import HedgingPolicy  # noqa: E402
from deep_hedging.statistics import paired_cvar_improvement_bootstrap  # noqa: E402
from deep_hedging.train import (  # noqa: E402
    TrainConfig,
    initial_premium,
    train_policy,
)


OUTPUT = Path(__file__).with_name("extended-diagnostics.json")
CHECKPOINT = ROOT / "checkpoints" / "extended-run-1.pt"


def policy_grid(
    policy: HedgingPolicy,
    market: MarketConfig,
    one_way_cost: float,
) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    scale = market.sigma * math.sqrt(market.maturity)
    leland_sigma = leland_volatility(market, one_way_cost)
    for time_fraction in (1.0, 0.5, 0.1):
        tau = market.maturity * time_fraction
        for spot in (80.0, 90.0, 100.0, 110.0, 120.0):
            d1 = (
                math.log(spot / market.strike)
                + (market.rate + 0.5 * market.sigma**2) * tau
            ) / (market.sigma * math.sqrt(tau))
            d1_leland = (
                math.log(spot / market.strike)
                + (market.rate + 0.5 * leland_sigma**2) * tau
            ) / (leland_sigma * math.sqrt(tau))
            for previous in (0.25, 0.50, 0.75):
                state = torch.tensor(
                    [[
                        math.log(spot / market.strike) / scale,
                        time_fraction,
                        previous / policy.max_position,
                    ]],
                    dtype=torch.float32,
                )
                with torch.no_grad():
                    neural_position = float(policy.action(state))
                rows.append(
                    {
                        "spot": spot,
                        "time_fraction": time_fraction,
                        "previous_position": previous,
                        "neural_position": neural_position,
                        "black_scholes_delta": 0.5
                        * (1.0 + math.erf(d1 / math.sqrt(2.0))),
                        "leland_delta": 0.5
                        * (1.0 + math.erf(d1_leland / math.sqrt(2.0))),
                    }
                )
    return rows


def path_diagnostics(
    positions: torch.Tensor,
    paths: torch.Tensor,
    leland_positions: torch.Tensor,
) -> dict[str, object]:
    previous = torch.cat(
        (torch.zeros_like(positions[:, :1]), positions[:, :-1]), dim=1
    )
    trade_notional = torch.abs(positions - previous) * paths[:, :-1]
    selected_steps = (0, 5, 10, 15, 20, 25, 29)
    position_rows: list[dict[str, float | int]] = []
    for step in selected_steps:
        values = positions[:, step]
        position_rows.append(
            {
                "step": step,
                "mean": float(torch.mean(values)),
                "q05": float(torch.quantile(values, 0.05)),
                "median": float(torch.quantile(values, 0.50)),
                "q95": float(torch.quantile(values, 0.95)),
                "mean_leland_delta": float(torch.mean(leland_positions[:, step])),
                "mean_trade_notional": float(torch.mean(trade_notional[:, step])),
            }
        )
    return {
        "mean_absolute_position_gap_to_leland": float(
            torch.mean(torch.abs(positions - leland_positions))
        ),
        "position_correlation_with_leland": float(
            torch.corrcoef(
                torch.stack((positions.flatten(), leland_positions.flatten()))
            )[0, 1]
        ),
        "selected_steps": position_rows,
        "mean_terminal_liquidation_notional": float(
            torch.mean(torch.abs(positions[:, -1]) * paths[:, -1])
        ),
    }


def main() -> None:
    torch.use_deterministic_algorithms(True)
    market = MarketConfig()
    training = TrainConfig(
        epochs=1_500,
        batch_size=8_192,
        validation_size=50_000,
        model_seed=20260911,
        train_seed=20261000,
        validation_seed=20262000,
        one_way_cost=0.0025,
    )
    started = time.perf_counter()
    policy, history, best_eta = train_policy(market, training, device="cpu")
    elapsed = time.perf_counter() - started
    best_validation = min(history, key=lambda row: row["cvar_loss_95"])
    best_epoch = int(best_validation["epoch"])

    test_seed = 20263000
    test_paths = simulate_gbm(100_000, market, test_seed, device="cpu")
    premium = initial_premium(market)
    leland_sigma = leland_volatility(market, training.one_way_cost)
    with torch.no_grad():
        neural_positions = policy(test_paths, market)
        delta_positions = black_scholes_delta_paths(test_paths, market)
        leland_positions = black_scholes_delta_paths(
            test_paths, market, volatility=leland_sigma
        )
        neural = strategy_pnl(
            test_paths,
            neural_positions,
            premium,
            training.one_way_cost,
            market.strike,
        )
        delta = strategy_pnl(
            test_paths,
            delta_positions,
            premium,
            training.one_way_cost,
            market.strike,
        )
        leland = strategy_pnl(
            test_paths,
            leland_positions,
            premium,
            training.one_way_cost,
            market.strike,
        )

    neural_losses = (-neural[0]).numpy()
    delta_losses = (-delta[0]).numpy()
    leland_losses = (-leland[0]).numpy()
    bootstrap = {
        "versus_leland": paired_cvar_improvement_bootstrap(
            leland_losses, neural_losses, seed=20264000
        ),
        "versus_delta": paired_cvar_improvement_bootstrap(
            delta_losses, neural_losses, seed=20264001
        ),
    }
    sampled_history = [
        row
        for row in history
        if int(row["epoch"]) == 1
        or int(row["epoch"]) % 25 == 0
        or int(row["epoch"]) == best_epoch
    ]
    result: dict[str, object] = {
        "status": "diagnostic interne — non publiable seul",
        "device": "cpu",
        "torch_version": torch.__version__,
        "elapsed_seconds": elapsed,
        "market": market.__dict__,
        "training": training.__dict__,
        "test_seed": test_seed,
        "test_size": int(test_paths.shape[0]),
        "best_epoch": best_epoch,
        "best_eta": best_eta,
        "best_validation": best_validation,
        "test_metrics": {
            "neural": summarize_pnl(*neural),
            "delta_black_scholes": summarize_pnl(*delta),
            "delta_leland": summarize_pnl(*leland),
        },
        "paired_bootstrap": bootstrap,
        "bootstrap_method": {
            "method": "bootstrap non paramétrique apparié, intervalle percentile",
            "unit": "trajectoire Monte-Carlo indépendante",
            "interpretation": "incertitude de test conditionnelle au modèle entraîné",
        },
        "policy_grid": policy_grid(policy, market, training.one_way_cost),
        "path_diagnostics": path_diagnostics(
            neural_positions, test_paths, leland_positions
        ),
        "history_sampling": "époque 1, chaque 25 époques et meilleur état",
        "history": sampled_history,
    }
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "policy_state_dict": policy.state_dict(),
            "market": market.__dict__,
            "training": training.__dict__,
            "best_epoch": best_epoch,
            "best_eta": best_eta,
        },
        CHECKPOINT,
    )
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "elapsed_seconds": elapsed,
                "best_epoch": best_epoch,
                "test_metrics": result["test_metrics"],
                "paired_bootstrap": bootstrap,
                "path_diagnostics": result["path_diagnostics"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
