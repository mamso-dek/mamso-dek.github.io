"""Sensibilité au coût avec une politique réentraînée par scénario."""

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


OUTPUT = Path(__file__).with_name("cost-sensitivity.json")
HISTORIES = Path(__file__).with_name("cost-sensitivity-histories")
CHECKPOINTS = ROOT / "checkpoints"
CENTRAL_CHECKPOINT = CHECKPOINTS / "convergence-2000.pt"
CENTRAL_RESULT = Path(__file__).with_name("convergence-2000.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reuse-central-checkpoint",
        action="store_true",
        help="réutilise le réseau déjà validé à 25 points de base",
    )
    return parser.parse_args()


def load_central_policy() -> tuple[
    HedgingPolicy, list[dict[str, float]], dict[str, float], float
]:
    checkpoint = torch.load(
        CENTRAL_CHECKPOINT,
        map_location="cpu",
        weights_only=True,
    )
    policy = HedgingPolicy()
    policy.load_state_dict(checkpoint["policy_state_dict"])
    policy.eval()
    previous = json.loads(CENTRAL_RESULT.read_text(encoding="utf-8"))
    return (
        policy,
        previous["history"],
        previous["best_validation"],
        float(previous["best_eta"]),
    )


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def loss_quantiles(pnl: torch.Tensor) -> dict[str, float]:
    losses = -pnl
    return {
        f"q{int(probability * 1_000):03d}": float(
            torch.quantile(losses, probability)
        )
        for probability in (0.50, 0.90, 0.95, 0.99, 0.995)
    }


def main() -> None:
    args = parse_args()
    torch.use_deterministic_algorithms(True)
    market = MarketConfig()
    premium = initial_premium(market)
    development_seed = 20263000
    development_paths = simulate_gbm(
        100_000, market, development_seed, device="cpu"
    )
    delta_positions = black_scholes_delta_paths(development_paths, market)
    zero_positions = torch.zeros_like(delta_positions)
    costs = (0.0, 0.0010, 0.0025, 0.0050)

    result: dict[str, object] = {
        "status": "sensibilité aux coûts sur jeu de développement — non finale",
        "device": "cpu",
        "torch_version": torch.__version__,
        "market": market.__dict__,
        "experiment": {
            "costs_one_way": costs,
            "epochs_per_cost": 2_000,
            "batch_size": 8_192,
            "validation_size": 50_000,
            "model_seed": 20260911,
            "train_seed": 20261000,
            "validation_seed": 20262000,
            "development_seed": development_seed,
            "development_size": int(development_paths.shape[0]),
            "common_random_numbers": True,
            "bootstrap_replicates": 1_000,
            "final_test_used": False,
        },
        "scenarios": [],
    }
    scenarios = result["scenarios"]
    assert isinstance(scenarios, list)

    for cost in costs:
        basis_points = int(round(cost * 10_000))
        training = TrainConfig(
            epochs=2_000,
            batch_size=8_192,
            validation_size=50_000,
            model_seed=20260911,
            train_seed=20261000,
            validation_seed=20262000,
            one_way_cost=cost,
        )
        if cost == 0.0025 and args.reuse_central_checkpoint:
            policy, history, best_validation, best_eta = load_central_policy()
            elapsed = 0.0
            training_source = "checkpoint central à 2 000 époques"
        else:
            started = time.perf_counter()
            policy, history, best_eta = train_policy(
                market, training, device="cpu"
            )
            elapsed = time.perf_counter() - started
            best_validation = min(
                history, key=lambda row: row["cvar_loss_95"]
            )
            training_source = "réentraînement complet"
            checkpoint_path = CHECKPOINTS / f"cost-{basis_points:04d}bp.pt"
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(
                {
                    "policy_state_dict": policy.state_dict(),
                    "market": market.__dict__,
                    "training": training.__dict__,
                    "best_epoch": int(best_validation["epoch"]),
                    "best_eta": best_eta,
                },
                checkpoint_path,
            )

        leland_sigma = leland_volatility(market, cost)
        leland_positions = black_scholes_delta_paths(
            development_paths, market, volatility=leland_sigma
        )
        with torch.no_grad():
            neural_positions = policy(development_paths, market)
            neural = strategy_pnl(
                development_paths,
                neural_positions,
                premium,
                cost,
                market.strike,
            )
            delta = strategy_pnl(
                development_paths,
                delta_positions,
                premium,
                cost,
                market.strike,
            )
            leland = strategy_pnl(
                development_paths,
                leland_positions,
                premium,
                cost,
                market.strike,
            )
            unhedged = strategy_pnl(
                development_paths,
                zero_positions,
                premium,
                cost,
                market.strike,
            )
        neural_metrics = summarize_pnl(*neural)
        delta_metrics = summarize_pnl(*delta)
        leland_metrics = summarize_pnl(*leland)
        bootstrap = paired_cvar_improvement_bootstrap(
            (-leland[0]).numpy(),
            (-neural[0]).numpy(),
            n_bootstrap=1_000,
            seed=20265000 + basis_points,
        )
        best_epoch = int(best_validation["epoch"])
        sampled_history = [
            row
            for row in history
            if int(row["epoch"]) == 1
            or int(row["epoch"]) % 50 == 0
            or int(row["epoch"]) == best_epoch
        ]
        history_path = HISTORIES / f"cost-{basis_points:04d}bp.json"
        write_json(
            history_path,
            {
                "training": training.__dict__,
                "training_source": training_source,
                "best_eta": best_eta,
                "history_sampling": (
                    "époque 1, chaque 50 époques et meilleur état"
                ),
                "history": sampled_history,
            },
        )
        scenarios.append(
            {
                "one_way_cost": cost,
                "basis_points": basis_points,
                "training_source": training_source,
                "elapsed_seconds": elapsed,
                "best_epoch": best_epoch,
                "best_eta": best_eta,
                "best_validation": best_validation,
                "leland_adjusted_volatility": leland_sigma,
                "development_metrics": {
                    "neural": neural_metrics,
                    "delta_black_scholes": delta_metrics,
                    "delta_leland": leland_metrics,
                    "unhedged": summarize_pnl(*unhedged),
                },
                "loss_quantiles": {
                    "neural": loss_quantiles(neural[0]),
                    "delta_black_scholes": loss_quantiles(delta[0]),
                    "delta_leland": loss_quantiles(leland[0]),
                },
                "neural_minus_leland": {
                    "cvar_improvement": (
                        leland_metrics["cvar_loss_95"]
                        - neural_metrics["cvar_loss_95"]
                    ),
                    "relative_cvar_improvement": (
                        leland_metrics["cvar_loss_95"]
                        - neural_metrics["cvar_loss_95"]
                    )
                    / leland_metrics["cvar_loss_95"],
                    "transaction_cost_reduction": (
                        leland_metrics["mean_transaction_cost"]
                        - neural_metrics["mean_transaction_cost"]
                    ),
                    "turnover_reduction": (
                        leland_metrics["mean_turnover_notional"]
                        - neural_metrics["mean_turnover_notional"]
                    ),
                },
                "paired_bootstrap_versus_leland": bootstrap,
                "history_file": str(history_path.relative_to(ROOT)),
            }
        )
        write_json(OUTPUT, result)
        print(
            f"coût={basis_points:02d} pb "
            f"époque={best_epoch} "
            f"CVaR réseau={neural_metrics['cvar_loss_95']:.6f} "
            f"Leland={leland_metrics['cvar_loss_95']:.6f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
