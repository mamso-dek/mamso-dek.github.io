"""Pilote de cohérence pour la couverture delta sous coûts proportionnels.

Ce script ne produit pas de résultat publiable. Il fixe une convention de P&L,
teste le simulateur Black–Scholes et quantifie l'ordre de grandeur du problème.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import norm


SEED = 20260901
N_PATHS = 50_000
N_STEPS = 30
S0 = 100.0
K = 100.0
T = 30 / 252
R = 0.0
SIGMA = 0.20
ALPHA = 0.95
COST_RATES = (0.0, 0.0010, 0.0025, 0.0050)


def black_scholes_call(spot: float, strike: float, tau: float) -> float:
    d1 = (np.log(spot / strike) + (R + 0.5 * SIGMA**2) * tau) / (
        SIGMA * np.sqrt(tau)
    )
    d2 = d1 - SIGMA * np.sqrt(tau)
    return float(spot * norm.cdf(d1) - strike * np.exp(-R * tau) * norm.cdf(d2))


def black_scholes_delta(spot: np.ndarray, tau: float) -> np.ndarray:
    d1 = (np.log(spot / K) + (R + 0.5 * SIGMA**2) * tau) / (
        SIGMA * np.sqrt(tau)
    )
    return norm.cdf(d1)


def simulate_paths() -> np.ndarray:
    rng = np.random.default_rng(SEED)
    dt = T / N_STEPS
    shocks = rng.standard_normal((N_PATHS, N_STEPS))
    log_returns = (R - 0.5 * SIGMA**2) * dt + SIGMA * np.sqrt(dt) * shocks
    log_spots = np.cumsum(log_returns, axis=1)
    paths = np.empty((N_PATHS, N_STEPS + 1), dtype=np.float64)
    paths[:, 0] = S0
    paths[:, 1:] = S0 * np.exp(log_spots)
    return paths


def delta_positions(paths: np.ndarray) -> np.ndarray:
    positions = np.empty((N_PATHS, N_STEPS), dtype=np.float64)
    dt = T / N_STEPS
    for step in range(N_STEPS):
        tau = T - step * dt
        positions[:, step] = black_scholes_delta(paths[:, step], tau)
    return positions


def strategy_pnl(
    paths: np.ndarray, positions: np.ndarray, premium: float, cost_rate: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    price_moves = np.diff(paths, axis=1)
    trading_gain = np.sum(positions * price_moves, axis=1)

    previous = np.column_stack(
        (np.zeros(N_PATHS, dtype=np.float64), positions[:, :-1])
    )
    trades = positions - previous
    entry_and_rehedge = np.sum(np.abs(trades) * paths[:, :-1], axis=1)
    liquidation = np.abs(positions[:, -1]) * paths[:, -1]
    turnover_notional = entry_and_rehedge + liquidation
    transaction_cost = cost_rate * turnover_notional

    payoff = np.maximum(paths[:, -1] - K, 0.0)
    pnl = premium + trading_gain - transaction_cost - payoff
    return pnl, transaction_cost, turnover_notional


def summarize(
    pnl: np.ndarray, transaction_cost: np.ndarray, turnover_notional: np.ndarray
) -> dict[str, float]:
    loss = -pnl
    var = float(np.quantile(loss, ALPHA))
    tail = loss[loss >= var]
    return {
        "mean_pnl": float(np.mean(pnl)),
        "std_pnl": float(np.std(pnl, ddof=1)),
        "loss_probability": float(np.mean(pnl < 0)),
        "var_loss_95": var,
        "cvar_loss_95": float(np.mean(tail)),
        "pnl_q01": float(np.quantile(pnl, 0.01)),
        "pnl_q05": float(np.quantile(pnl, 0.05)),
        "pnl_median": float(np.median(pnl)),
        "mean_transaction_cost": float(np.mean(transaction_cost)),
        "mean_turnover_notional": float(np.mean(turnover_notional)),
    }


def markdown_table(results: dict[str, dict[str, float]]) -> str:
    rows = [
        "# Résultats du pilote",
        "",
        "Simulation Black–Scholes, 50 000 trajectoires indépendantes, "
        "30 rééquilibrages et prime Black–Scholes initiale. Les nombres "
        "sont exploratoires et ne doivent pas être publiés.",
        "",
        "| Stratégie | Coût | P&L moyen | Écart-type | CVaR perte 95 % | "
        "Coût moyen |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key, values in results.items():
        strategy, rate = key.split("__")
        rows.append(
            f"| {strategy} | {10000 * float(rate):.0f} pb | "
            f"{values['mean_pnl']:.4f} | {values['std_pnl']:.4f} | "
            f"{values['cvar_loss_95']:.4f} | "
            f"{values['mean_transaction_cost']:.4f} |"
        )
    return "\n".join(rows) + "\n"


def main() -> None:
    paths = simulate_paths()
    premium = black_scholes_call(S0, K, T)
    delta = delta_positions(paths)
    no_hedge = np.zeros_like(delta)

    results: dict[str, dict[str, float]] = {}
    for cost_rate in COST_RATES:
        for name, positions in (("sans_couverture", no_hedge), ("delta", delta)):
            pnl, costs, turnover = strategy_pnl(
                paths, positions, premium, cost_rate
            )
            results[f"{name}__{cost_rate:.4f}"] = summarize(pnl, costs, turnover)

    output_dir = Path(__file__).resolve().parent
    payload = {
        "configuration": {
            "seed": SEED,
            "n_paths": N_PATHS,
            "n_steps": N_STEPS,
            "s0": S0,
            "strike": K,
            "maturity_years": T,
            "sigma": SIGMA,
            "risk_free_rate": R,
            "premium": premium,
            "cvar_alpha": ALPHA,
        },
        "results": results,
    }
    (output_dir / "results.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (output_dir / "results.md").write_text(
        markdown_table(results), encoding="utf-8"
    )
    print(markdown_table(results))


if __name__ == "__main__":
    main()
