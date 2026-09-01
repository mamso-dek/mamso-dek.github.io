"""Contrôle de convergence à 2 000 époques sur la première graine."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import time

import numpy as np
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
from deep_hedging.statistics import paired_cvar_improvement_bootstrap  # noqa: E402
from deep_hedging.train import (  # noqa: E402
    TrainConfig,
    initial_premium,
    train_policy,
)


OUTPUT = Path(__file__).with_name("convergence-2000.json")
CHECKPOINT = ROOT / "checkpoints" / "convergence-2000.pt"
PREVIOUS = Path(__file__).with_name("extended-diagnostics.json")


def block_minimum(
    history: list[dict[str, float]], start: int, end: int
) -> dict[str, float]:
    rows = [row for row in history if start <= int(row["epoch"]) <= end]
    if not rows:
        raise ValueError("bloc de convergence vide")
    return min(rows, key=lambda row: row["cvar_loss_95"])


def main() -> None:
    torch.use_deterministic_algorithms(True)
    market = MarketConfig()
    training = TrainConfig(
        epochs=2_000,
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

    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    previous_best = previous["best_validation"]
    previous_cvar = float(previous_best["cvar_loss_95"])
    current_cvar = float(best_validation["cvar_loss_95"])
    block_1501_1750 = block_minimum(history, 1_501, 1_750)
    block_1751_2000 = block_minimum(history, 1_751, 2_000)
    last_window = np.array(
        [
            row["cvar_loss_95"]
            for row in history
            if 1_751 <= int(row["epoch"]) <= 2_000
        ],
        dtype=np.float64,
    )
    slope = float(np.polyfit(np.arange(last_window.size), last_window, 1)[0])

    development_seed = 20263000
    development_paths = simulate_gbm(
        100_000, market, development_seed, device="cpu"
    )
    premium = initial_premium(market)
    leland_sigma = leland_volatility(market, training.one_way_cost)
    with torch.no_grad():
        neural_positions = policy(development_paths, market)
        delta_positions = black_scholes_delta_paths(development_paths, market)
        leland_positions = black_scholes_delta_paths(
            development_paths, market, volatility=leland_sigma
        )
        neural = strategy_pnl(
            development_paths,
            neural_positions,
            premium,
            training.one_way_cost,
            market.strike,
        )
        delta = strategy_pnl(
            development_paths,
            delta_positions,
            premium,
            training.one_way_cost,
            market.strike,
        )
        leland = strategy_pnl(
            development_paths,
            leland_positions,
            premium,
            training.one_way_cost,
            market.strike,
        )
    bootstrap = paired_cvar_improvement_bootstrap(
        (-leland[0]).numpy(),
        (-neural[0]).numpy(),
        n_bootstrap=2_000,
        seed=20264002,
    )

    sampled_history = [
        row
        for row in history
        if int(row["epoch"]) == 1
        or int(row["epoch"]) % 25 == 0
        or int(row["epoch"]) == best_epoch
    ]
    result: dict[str, object] = {
        "status": "contrôle de convergence sur test de développement — non final",
        "device": "cpu",
        "torch_version": torch.__version__,
        "elapsed_seconds": elapsed,
        "market": market.__dict__,
        "training": training.__dict__,
        "best_epoch": best_epoch,
        "best_eta": best_eta,
        "best_validation": best_validation,
        "convergence": {
            "previous_limit": 1_500,
            "previous_best_epoch": int(previous["best_epoch"]),
            "previous_best_validation_cvar": previous_cvar,
            "current_limit": 2_000,
            "current_best_validation_cvar": current_cvar,
            "absolute_improvement": previous_cvar - current_cvar,
            "relative_improvement": (previous_cvar - current_cvar) / previous_cvar,
            "best_1501_1750": block_1501_1750,
            "best_1751_2000": block_1751_2000,
            "last_250_epoch_ols_slope_per_epoch": slope,
        },
        "development_test": {
            "seed": development_seed,
            "size": int(development_paths.shape[0]),
            "reuse_warning": (
                "jeu réutilisé pour les diagnostics ; il ne constitue plus "
                "l'évaluation finale"
            ),
            "metrics": {
                "neural": summarize_pnl(*neural),
                "delta_black_scholes": summarize_pnl(*delta),
                "delta_leland": summarize_pnl(*leland),
            },
            "paired_bootstrap_versus_leland": bootstrap,
        },
        "reserved_final_test": {
            "seed": 20269000,
            "size": 250_000,
            "status": "préenregistré et non exécuté",
        },
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
                "best_validation": best_validation,
                "convergence": result["convergence"],
                "development_test": result["development_test"],
                "reserved_final_test": result["reserved_final_test"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
