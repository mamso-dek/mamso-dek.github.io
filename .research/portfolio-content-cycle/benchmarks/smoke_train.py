"""Petit apprentissage de faisabilité, distinct des expériences finales."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

import torch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from deep_hedging.core import (  # noqa: E402
    MarketConfig,
    black_scholes_delta_paths,
    simulate_gbm,
    strategy_pnl,
    summarize_pnl,
)
from deep_hedging.train import (  # noqa: E402
    TrainConfig,
    initial_premium,
    train_policy,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", choices=("auto", "cpu", "mps"), default="auto")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=4_096)
    parser.add_argument("--validation-size", type=int, default=20_000)
    parser.add_argument("--test-size", type=int, default=30_000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    requested = args.device
    device = (
        "mps"
        if requested == "auto" and torch.backends.mps.is_available()
        else "cpu"
        if requested == "auto"
        else requested
    )
    if device == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("backend MPS indisponible")
    torch.use_deterministic_algorithms(True)
    market = MarketConfig()
    training = TrainConfig(
        epochs=args.epochs,
        batch_size=args.batch_size,
        validation_size=args.validation_size,
    )
    started = time.perf_counter()
    policy, history, best_eta = train_policy(market, training, device=device)
    elapsed = time.perf_counter() - started

    test_paths = simulate_gbm(args.test_size, market, 20263000, device=device)
    premium = initial_premium(market).to(device)
    with torch.no_grad():
        neural_positions = policy(test_paths, market)
        neural = strategy_pnl(
            test_paths,
            neural_positions,
            premium,
            training.one_way_cost,
            market.strike,
        )
        delta_positions = black_scholes_delta_paths(test_paths, market)
        delta = strategy_pnl(
            test_paths,
            delta_positions,
            premium,
            training.one_way_cost,
            market.strike,
        )

    result = {
        "status": "faisabilité uniquement — résultat non publiable",
        "device": device,
        "torch_version": torch.__version__,
        "elapsed_seconds": elapsed,
        "best_eta": best_eta,
        "training": training.__dict__,
        "market": market.__dict__,
        "first_validation": history[0],
        "best_validation_cvar": min(row["cvar_loss_95"] for row in history),
        "last_validation": history[-1],
        "test_neural": summarize_pnl(*neural, training.alpha),
        "test_delta": summarize_pnl(*delta, training.alpha),
        "history": history,
    }
    output = Path(__file__).with_name(
        f"smoke-results-{device}-{args.epochs}e.json"
    )
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "status", "device", "elapsed_seconds", "first_validation",
        "best_validation_cvar", "test_neural", "test_delta"
    )}, indent=2))


if __name__ == "__main__":
    main()
