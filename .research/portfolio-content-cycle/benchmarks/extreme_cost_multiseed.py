"""Réplications multigraines aux coûts extrêmes de 0 et 50 pb."""

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
from deep_hedging.model import HedgingPolicy  # noqa: E402
from deep_hedging.statistics import paired_cvar_improvement_bootstrap  # noqa: E402
from deep_hedging.train import (  # noqa: E402
    TrainConfig,
    initial_premium,
    train_policy,
)


OUTPUT = Path(__file__).with_name("extreme-cost-multiseed.json")
HISTORIES = Path(__file__).with_name("extreme-cost-multiseed-histories")
CHECKPOINTS = ROOT / "checkpoints"
EXISTING_HISTORIES = Path(__file__).with_name("cost-sensitivity-histories")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--bootstrap", type=int, default=1_000)
    return parser.parse_args()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def load_policy(path: Path) -> HedgingPolicy:
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    policy = HedgingPolicy()
    policy.load_state_dict(checkpoint["policy_state_dict"])
    policy.eval()
    return policy


def save_checkpoint(
    path: Path,
    policy: HedgingPolicy,
    market: MarketConfig,
    training: TrainConfig,
    best_validation: dict[str, float],
    best_eta: float,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "policy_state_dict": policy.state_dict(),
            "market": market.__dict__,
            "training": training.__dict__,
            "best_epoch": int(best_validation["epoch"]),
            "best_eta": best_eta,
        },
        path,
    )


def seeds(run: int) -> tuple[int, int]:
    return 20260911 + run - 1, 20261000 + 10_000 * (run - 1)


def run_paths(basis_points: int, run: int) -> tuple[Path, Path]:
    if run == 1:
        return (
            CHECKPOINTS / f"cost-{basis_points:04d}bp.pt",
            EXISTING_HISTORIES / f"cost-{basis_points:04d}bp.json",
        )
    stem = f"cost-{basis_points:04d}bp-run-{run}"
    return CHECKPOINTS / f"extreme-{stem}.pt", HISTORIES / f"{stem}.json"


def load_or_train(
    market: MarketConfig,
    cost: float,
    basis_points: int,
    run: int,
    resume: bool,
) -> tuple[
    HedgingPolicy,
    list[dict[str, float]],
    dict[str, float],
    float,
    float,
    str,
    TrainConfig,
]:
    model_seed, train_seed = seeds(run)
    training = TrainConfig(
        epochs=2_000,
        batch_size=8_192,
        validation_size=50_000,
        model_seed=model_seed,
        train_seed=train_seed,
        validation_seed=20262000,
        one_way_cost=cost,
    )
    checkpoint_path, history_path = run_paths(basis_points, run)
    can_reuse = run == 1 or resume
    if can_reuse and checkpoint_path.exists() and history_path.exists():
        policy = load_policy(checkpoint_path)
        previous = json.loads(history_path.read_text(encoding="utf-8"))
        history = previous["history"]
        best_validation = min(
            history, key=lambda row: row["cvar_loss_95"]
        )
        best_eta = float(previous["best_eta"])
        elapsed = 0.0
        provenance = (
            "checkpoint existant de la sensibilité aux coûts"
            if run == 1
            else "checkpoint local repris après interruption"
        )
        return (
            policy,
            history,
            best_validation,
            best_eta,
            elapsed,
            provenance,
            training,
        )

    started = time.perf_counter()
    policy, history, best_eta = train_policy(market, training, device="cpu")
    elapsed = time.perf_counter() - started
    best_validation = min(history, key=lambda row: row["cvar_loss_95"])
    save_checkpoint(
        checkpoint_path,
        policy,
        market,
        training,
        best_validation,
        best_eta,
    )
    sampled_history = [
        row
        for row in history
        if int(row["epoch"]) == 1
        or int(row["epoch"]) % 50 == 0
        or int(row["epoch"]) == int(best_validation["epoch"])
    ]
    write_json(
        history_path,
        {
            "training": training.__dict__,
            "training_provenance": "réentraînement complet de 2 000 époques",
            "best_eta": best_eta,
            "history_sampling": (
                "époque 1, chaque 50 époques et meilleur état"
            ),
            "history": sampled_history,
        },
    )
    return (
        policy,
        history,
        best_validation,
        best_eta,
        elapsed,
        "réentraînement complet de 2 000 époques",
        training,
    )


def aggregate_runs(runs: list[dict[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {"n_runs": len(runs)}
    for metric in (
        "cvar_loss_95",
        "std_pnl",
        "mean_transaction_cost",
        "mean_turnover_notional",
    ):
        values = [
            float(run["development_metrics"]["neural"][metric])  # type: ignore[index]
            for run in runs
        ]
        result[metric] = {
            "mean": statistics.fmean(values),
            "sample_std": (
                statistics.stdev(values) if len(values) > 1 else None
            ),
            "min": min(values),
            "max": max(values),
        }
    improvements = [
        float(run["paired_bootstrap_versus_leland"]["point_improvement"])  # type: ignore[index]
        for run in runs
    ]
    result["cvar_improvement_versus_leland"] = {
        "mean": statistics.fmean(improvements),
        "sample_std": (
            statistics.stdev(improvements)
            if len(improvements) > 1
            else None
        ),
        "min": min(improvements),
        "max": max(improvements),
        "runs_with_positive_point_improvement": sum(x > 0 for x in improvements),
        "runs_with_strictly_positive_ci": sum(
            float(run["paired_bootstrap_versus_leland"]["ci_lower"]) > 0  # type: ignore[index]
            for run in runs
        ),
    }
    return result


def main() -> None:
    args = parse_args()
    if args.bootstrap <= 1:
        raise ValueError("bootstrap doit être supérieur à un")
    torch.use_deterministic_algorithms(True)
    market = MarketConfig()
    premium = initial_premium(market)
    development_seed = 20263000
    development_paths = simulate_gbm(
        100_000, market, development_seed, device="cpu"
    )

    result: dict[str, object] = {
        "status": "coûts extrêmes multigraines — développement non final",
        "device": "cpu",
        "torch_version": torch.__version__,
        "market": market.__dict__,
        "experiment": {
            "costs_one_way": [0.0, 0.0050],
            "runs_per_cost": 3,
            "epochs": 2_000,
            "batch_size": 8_192,
            "validation_size": 50_000,
            "validation_seed": 20262000,
            "development_seed": development_seed,
            "development_size": int(development_paths.shape[0]),
            "matched_training_seeds_across_costs": True,
            "bootstrap_replicates_per_run": args.bootstrap,
            "final_test_used": False,
        },
        "scenarios": [],
        "matched_cost_contrasts": [],
        "reserved_final_test": {
            "seed": 20269000,
            "size": 250_000,
            "status": "préenregistré et non exécuté",
        },
    }
    scenarios = result["scenarios"]
    assert isinstance(scenarios, list)

    for cost in (0.0, 0.0050):
        basis_points = int(round(cost * 10_000))
        leland_sigma = leland_volatility(market, cost)
        leland_positions = black_scholes_delta_paths(
            development_paths, market, volatility=leland_sigma
        )
        leland = strategy_pnl(
            development_paths,
            leland_positions,
            premium,
            cost,
            market.strike,
        )
        leland_metrics = summarize_pnl(*leland)
        scenario: dict[str, object] = {
            "one_way_cost": cost,
            "basis_points": basis_points,
            "leland_adjusted_volatility": leland_sigma,
            "leland_development_metrics": leland_metrics,
            "runs": [],
            "aggregate": {"n_runs": 0},
        }
        runs = scenario["runs"]
        assert isinstance(runs, list)
        scenarios.append(scenario)

        for run in (1, 2, 3):
            (
                policy,
                history,
                best_validation,
                best_eta,
                elapsed,
                provenance,
                training,
            ) = load_or_train(
                market, cost, basis_points, run, args.resume
            )
            with torch.no_grad():
                positions = policy(development_paths, market)
                neural = strategy_pnl(
                    development_paths,
                    positions,
                    premium,
                    cost,
                    market.strike,
                )
            neural_metrics = summarize_pnl(*neural)
            bootstrap = paired_cvar_improvement_bootstrap(
                (-leland[0]).numpy(),
                (-neural[0]).numpy(),
                n_bootstrap=args.bootstrap,
                seed=20263700 + basis_points + run,
            )
            _, history_path = run_paths(basis_points, run)
            runs.append(
                {
                    "run": run,
                    "model_seed": training.model_seed,
                    "train_seed": training.train_seed,
                    "training_provenance": provenance,
                    "elapsed_seconds_this_run": elapsed,
                    "best_epoch": int(best_validation["epoch"]),
                    "best_eta": best_eta,
                    "best_validation": best_validation,
                    "development_metrics": {"neural": neural_metrics},
                    "paired_bootstrap_versus_leland": bootstrap,
                    "history_file": str(history_path.relative_to(ROOT)),
                }
            )
            scenario["aggregate"] = aggregate_runs(runs)
            write_json(OUTPUT, result)
            print(
                f"coût={basis_points:02d} pb run={run} "
                f"époque={int(best_validation['epoch'])} "
                f"CVaR={neural_metrics['cvar_loss_95']:.6f} "
                f"Leland={leland_metrics['cvar_loss_95']:.6f}",
                flush=True,
            )

    zero_runs = scenarios[0]["runs"]  # type: ignore[index]
    high_runs = scenarios[1]["runs"]  # type: ignore[index]
    contrasts = result["matched_cost_contrasts"]
    assert isinstance(contrasts, list)
    for zero_run, high_run in zip(zero_runs, high_runs, strict=True):
        zero_metrics = zero_run["development_metrics"]["neural"]
        high_metrics = high_run["development_metrics"]["neural"]
        contrasts.append(
            {
                "run": zero_run["run"],
                "cvar_increase_50bp_minus_0bp": (
                    high_metrics["cvar_loss_95"]
                    - zero_metrics["cvar_loss_95"]
                ),
                "turnover_change_50bp_minus_0bp": (
                    high_metrics["mean_turnover_notional"]
                    - zero_metrics["mean_turnover_notional"]
                ),
            }
        )
    result["matched_cost_contrast_aggregate"] = {
        "cvar_increase_mean": statistics.fmean(
            row["cvar_increase_50bp_minus_0bp"] for row in contrasts
        ),
        "cvar_increase_sample_std": statistics.stdev(
            row["cvar_increase_50bp_minus_0bp"] for row in contrasts
        ),
        "turnover_change_mean": statistics.fmean(
            row["turnover_change_50bp_minus_0bp"] for row in contrasts
        ),
        "turnover_change_sample_std": statistics.stdev(
            row["turnover_change_50bp_minus_0bp"] for row in contrasts
        ),
    }
    write_json(OUTPUT, result)


if __name__ == "__main__":
    main()
