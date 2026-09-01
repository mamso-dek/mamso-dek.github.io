"""Apprentissages longs répétés avec validation et test communs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
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
from deep_hedging.train import (  # noqa: E402
    TrainConfig,
    initial_premium,
    train_policy,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=1_000)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=8_192)
    parser.add_argument("--validation-size", type=int, default=50_000)
    parser.add_argument("--test-size", type=int, default=100_000)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("multiseed-results.json"),
    )
    return parser.parse_args()


def baseline_metrics(
    paths: torch.Tensor,
    market: MarketConfig,
    premium: torch.Tensor,
    cost: float,
) -> dict[str, dict[str, float]]:
    zeros = torch.zeros_like(paths[:, :-1])
    delta = black_scholes_delta_paths(paths, market)
    sigma_leland = leland_volatility(market, cost)
    leland = black_scholes_delta_paths(paths, market, volatility=sigma_leland)
    rows: dict[str, dict[str, float]] = {}
    for name, positions in (
        ("sans_couverture", zeros),
        ("delta_black_scholes", delta),
        ("delta_leland", leland),
    ):
        row = summarize_pnl(
            *strategy_pnl(paths, positions, premium, cost, market.strike)
        )
        if name == "delta_leland":
            row["adjusted_volatility"] = sigma_leland
        rows[name] = row
    return rows


def aggregate(runs: list[dict[str, object]], leland_cvar: float) -> dict[str, object]:
    metrics = ("cvar_loss_95", "mean_transaction_cost", "mean_turnover_notional")
    summary: dict[str, object] = {"n_runs": len(runs)}
    for metric in metrics:
        values = [float(run["test_neural"][metric]) for run in runs]  # type: ignore[index]
        summary[metric] = {
            "mean": statistics.fmean(values),
            "sample_std": statistics.stdev(values) if len(values) > 1 else None,
            "min": min(values),
            "max": max(values),
        }
    summary["runs_better_than_leland_cvar"] = sum(
        float(run["test_neural"]["cvar_loss_95"]) < leland_cvar  # type: ignore[index]
        for run in runs
    )
    return summary


def write_result(path: Path, result: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    if args.epochs <= 0 or args.runs <= 0:
        raise ValueError("epochs et runs doivent être strictement positifs")

    torch.use_deterministic_algorithms(True)
    market = MarketConfig()
    cost = 0.0025
    validation_seed = 20262000
    test_seed = 20263000
    test_paths = simulate_gbm(args.test_size, market, test_seed, device="cpu")
    premium = initial_premium(market)
    baselines = baseline_metrics(test_paths, market, premium, cost)
    leland_cvar = baselines["delta_leland"]["cvar_loss_95"]

    result: dict[str, object] = {
        "status": "expérience multigraine intermédiaire — non publiable seule",
        "torch_version": torch.__version__,
        "device": "cpu",
        "market": market.__dict__,
        "experiment": {
            "epochs": args.epochs,
            "requested_runs": args.runs,
            "batch_size": args.batch_size,
            "validation_size": args.validation_size,
            "test_size": args.test_size,
            "validation_seed": validation_seed,
            "test_seed": test_seed,
            "one_way_cost": cost,
            "alpha": 0.95,
        },
        "baselines": baselines,
        "runs": [],
        "aggregate": {"n_runs": 0},
    }
    histories_dir = args.output.with_name("multiseed-histories")

    runs = result["runs"]
    assert isinstance(runs, list)
    for run_index in range(args.runs):
        training = TrainConfig(
            epochs=args.epochs,
            batch_size=args.batch_size,
            validation_size=args.validation_size,
            model_seed=20260911 + run_index,
            train_seed=20261000 + 10_000 * run_index,
            validation_seed=validation_seed,
            one_way_cost=cost,
        )
        started = time.perf_counter()
        policy, history, best_eta = train_policy(market, training, device="cpu")
        elapsed = time.perf_counter() - started
        with torch.no_grad():
            positions = policy(test_paths, market)
            test_neural = summarize_pnl(
                *strategy_pnl(
                    test_paths, positions, premium, cost, market.strike
                )
            )
        best_validation = min(history, key=lambda row: row["cvar_loss_95"])
        best_epoch = int(best_validation["epoch"])
        sampled_history = [
            row
            for row in history
            if int(row["epoch"]) == 1
            or int(row["epoch"]) % 10 == 0
            or int(row["epoch"]) == best_epoch
        ]
        history_path = histories_dir / f"run-{run_index + 1}.json"
        write_result(
            history_path,
            {
                "training": training.__dict__,
                "best_eta": best_eta,
                "history_sampling": "époque 1, chaque dizaine et meilleur état de validation",
                "history": sampled_history,
            },
        )
        try:
            history_reference = str(history_path.relative_to(ROOT))
        except ValueError:
            history_reference = str(history_path)
        runs.append(
            {
                "run": run_index + 1,
                "model_seed": training.model_seed,
                "train_seed": training.train_seed,
                "elapsed_seconds": elapsed,
                "best_epoch": best_epoch,
                "best_eta": best_eta,
                "best_validation": best_validation,
                "test_neural": test_neural,
                "history_file": history_reference,
            }
        )
        result["aggregate"] = aggregate(runs, leland_cvar)
        write_result(args.output, result)
        print(
            f"run={run_index + 1} seed={training.model_seed} "
            f"epoch={int(best_validation['epoch'])} "
            f"test_cvar={test_neural['cvar_loss_95']:.6f} "
            f"leland={leland_cvar:.6f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
