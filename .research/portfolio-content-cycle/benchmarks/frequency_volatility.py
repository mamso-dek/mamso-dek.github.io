"""Sensibilités à la fréquence et à la volatilité hors entraînement."""

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


OUTPUT = Path(__file__).with_name("frequency-volatility.json")
HISTORIES = Path(__file__).with_name("frequency-histories")
CHECKPOINTS = ROOT / "checkpoints"
CENTRAL_CHECKPOINT = CHECKPOINTS / "convergence-2000.pt"
CENTRAL_RESULT = Path(__file__).with_name("convergence-2000.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reuse-central-checkpoint",
        action="store_true",
        help="réutilise la politique centrale à 30 pas",
    )
    parser.add_argument(
        "--reuse-frequency-checkpoints",
        action="store_true",
        help="réutilise les politiques locales à 10 et 20 pas",
    )
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


def load_central() -> tuple[
    HedgingPolicy, list[dict[str, float]], dict[str, float], float
]:
    policy = load_policy(CENTRAL_CHECKPOINT)
    previous = json.loads(CENTRAL_RESULT.read_text(encoding="utf-8"))
    return (
        policy,
        previous["history"],
        previous["best_validation"],
        float(previous["best_eta"]),
    )


def coupled_frequency_paths(
    n_paths: int,
    seed: int,
    n_steps: int,
) -> torch.Tensor:
    fine_steps = 60
    if fine_steps % n_steps != 0:
        raise ValueError("n_steps doit diviser la grille fine de 60 pas")
    fine_market = MarketConfig(n_steps=fine_steps)
    fine_paths = simulate_gbm(n_paths, fine_market, seed, device="cpu")
    stride = fine_steps // n_steps
    return fine_paths[:, ::stride]


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


def main() -> None:
    args = parse_args()
    torch.use_deterministic_algorithms(True)
    cost = 0.0025
    frequency_seed = 20263100
    frequency_losses: dict[int, torch.Tensor] = {}
    frequency_rows: list[dict[str, object]] = []

    for n_steps in (10, 20, 30):
        market = MarketConfig(n_steps=n_steps)
        training = TrainConfig(
            epochs=2_000,
            batch_size=8_192,
            validation_size=50_000,
            model_seed=20260911,
            train_seed=20261000,
            validation_seed=20262000,
            one_way_cost=cost,
        )
        history_path = HISTORIES / f"frequency-{n_steps:02d}.json"
        local_checkpoint = CHECKPOINTS / f"frequency-{n_steps:02d}-steps.pt"
        if n_steps == 30 and args.reuse_central_checkpoint:
            policy, history, best_validation, best_eta = load_central()
            elapsed = 0.0
            policy_source = "checkpoint central à 30 pas"
            training_provenance = (
                "réentraînement central complet de 2 000 époques "
                "(exécution 5)"
            )
        elif (
            n_steps in (10, 20)
            and args.reuse_frequency_checkpoints
            and local_checkpoint.exists()
            and history_path.exists()
        ):
            policy = load_policy(local_checkpoint)
            previous = json.loads(history_path.read_text(encoding="utf-8"))
            history = previous["history"]
            best_validation = min(
                history, key=lambda row: row["cvar_loss_95"]
            )
            best_eta = float(previous["best_eta"])
            elapsed = 0.0
            policy_source = f"checkpoint local à {n_steps} pas"
            training_provenance = (
                "réentraînement complet de 2 000 époques lors de la "
                "première exécution de ce benchmark"
            )
        else:
            started = time.perf_counter()
            policy, history, best_eta = train_policy(
                market, training, device="cpu"
            )
            elapsed = time.perf_counter() - started
            best_validation = min(
                history, key=lambda row: row["cvar_loss_95"]
            )
            policy_source = "politique produite pendant cette exécution"
            training_provenance = "réentraînement complet de 2 000 époques"
            save_checkpoint(
                local_checkpoint,
                policy,
                market,
                training,
                best_validation,
                best_eta,
            )

        paths = coupled_frequency_paths(100_000, frequency_seed, n_steps)
        premium = initial_premium(market)
        delta_positions = black_scholes_delta_paths(paths, market)
        leland_sigma = leland_volatility(market, cost)
        leland_positions = black_scholes_delta_paths(
            paths, market, volatility=leland_sigma
        )
        with torch.no_grad():
            neural = strategy_pnl(
                paths,
                policy(paths, market),
                premium,
                cost,
                market.strike,
            )
            delta = strategy_pnl(
                paths,
                delta_positions,
                premium,
                cost,
                market.strike,
            )
            leland = strategy_pnl(
                paths,
                leland_positions,
                premium,
                cost,
                market.strike,
            )
        neural_metrics = summarize_pnl(*neural)
        leland_metrics = summarize_pnl(*leland)
        frequency_losses[n_steps] = -neural[0].detach()
        best_epoch = int(best_validation["epoch"])
        sampled_history = [
            row
            for row in history
            if int(row["epoch"]) == 1
            or int(row["epoch"]) % 50 == 0
            or int(row["epoch"]) == best_epoch
        ]
        write_json(
            history_path,
            {
                "market": market.__dict__,
                "training": training.__dict__,
                "training_provenance": training_provenance,
                "evaluation_policy_source": policy_source,
                "best_eta": best_eta,
                "history_sampling": (
                    "époque 1, chaque 50 époques et meilleur état"
                ),
                "history": sampled_history,
            },
        )
        frequency_rows.append(
            {
                "n_steps": n_steps,
                "training_provenance": training_provenance,
                "evaluation_policy_source": policy_source,
                "elapsed_seconds_this_run": elapsed,
                "best_epoch": best_epoch,
                "best_eta": best_eta,
                "best_validation": best_validation,
                "leland_adjusted_volatility": leland_sigma,
                "development_metrics": {
                    "neural": neural_metrics,
                    "delta_black_scholes": summarize_pnl(*delta),
                    "delta_leland": leland_metrics,
                },
                "paired_bootstrap_neural_versus_leland": (
                    paired_cvar_improvement_bootstrap(
                        (-leland[0]).numpy(),
                        (-neural[0]).numpy(),
                        n_bootstrap=1_000,
                        seed=20266000 + n_steps,
                    )
                ),
                "history_file": str(history_path.relative_to(ROOT)),
            }
        )
        print(
            f"fréquence={n_steps:02d} "
            f"CVaR réseau={neural_metrics['cvar_loss_95']:.6f} "
            f"Leland={leland_metrics['cvar_loss_95']:.6f}",
            flush=True,
        )

    frequency_comparisons = {
        "20_versus_10": paired_cvar_improvement_bootstrap(
            frequency_losses[10].numpy(),
            frequency_losses[20].numpy(),
            n_bootstrap=1_000,
            seed=20266120,
        ),
        "30_versus_20": paired_cvar_improvement_bootstrap(
            frequency_losses[20].numpy(),
            frequency_losses[30].numpy(),
            n_bootstrap=1_000,
            seed=20266230,
        ),
    }

    training_market = MarketConfig()
    central_policy = load_policy(CENTRAL_CHECKPOINT)
    training_premium = initial_premium(training_market)
    volatility_seed = 20263200
    volatility_rows: list[dict[str, object]] = []
    for sigma in (0.15, 0.20, 0.25, 0.30):
        scenario_market = MarketConfig(sigma=sigma)
        paths = simulate_gbm(
            100_000, scenario_market, volatility_seed, device="cpu"
        )
        informed_delta = black_scholes_delta_paths(paths, scenario_market)
        informed_leland_sigma = leland_volatility(scenario_market, cost)
        informed_leland = black_scholes_delta_paths(
            paths,
            scenario_market,
            volatility=informed_leland_sigma,
        )
        frozen_delta = black_scholes_delta_paths(paths, training_market)
        frozen_leland_sigma = leland_volatility(training_market, cost)
        frozen_leland = black_scholes_delta_paths(
            paths,
            training_market,
            volatility=frozen_leland_sigma,
        )
        with torch.no_grad():
            neural = strategy_pnl(
                paths,
                central_policy(paths, training_market),
                training_premium,
                cost,
                training_market.strike,
            )
            informed_delta_pnl = strategy_pnl(
                paths,
                informed_delta,
                training_premium,
                cost,
                training_market.strike,
            )
            informed_leland_pnl = strategy_pnl(
                paths,
                informed_leland,
                training_premium,
                cost,
                training_market.strike,
            )
            frozen_delta_pnl = strategy_pnl(
                paths,
                frozen_delta,
                training_premium,
                cost,
                training_market.strike,
            )
            frozen_leland_pnl = strategy_pnl(
                paths,
                frozen_leland,
                training_premium,
                cost,
                training_market.strike,
            )
        neural_metrics = summarize_pnl(*neural)
        informed_leland_metrics = summarize_pnl(*informed_leland_pnl)
        volatility_rows.append(
            {
                "scenario_sigma": sigma,
                "policy_training_sigma": training_market.sigma,
                "policy_receives_scenario_sigma": False,
                "common_training_premium": float(training_premium),
                "informed_leland_adjusted_volatility": informed_leland_sigma,
                "development_metrics": {
                    "neural_frozen": neural_metrics,
                    "delta_informed_by_scenario_sigma": summarize_pnl(
                        *informed_delta_pnl
                    ),
                    "leland_informed_by_scenario_sigma": (
                        informed_leland_metrics
                    ),
                    "delta_frozen_sigma_20": summarize_pnl(*frozen_delta_pnl),
                    "leland_frozen_sigma_20": summarize_pnl(*frozen_leland_pnl),
                },
                "paired_bootstrap_neural_versus_informed_leland": (
                    paired_cvar_improvement_bootstrap(
                        (-informed_leland_pnl[0]).numpy(),
                        (-neural[0]).numpy(),
                        n_bootstrap=1_000,
                        seed=20267000 + int(round(sigma * 100)),
                    )
                ),
                "paired_bootstrap_neural_versus_frozen_leland": (
                    paired_cvar_improvement_bootstrap(
                        (-frozen_leland_pnl[0]).numpy(),
                        (-neural[0]).numpy(),
                        n_bootstrap=1_000,
                        seed=20268000 + int(round(sigma * 100)),
                    )
                ),
            }
        )
        print(
            f"volatilité={sigma:.0%} "
            f"CVaR réseau={neural_metrics['cvar_loss_95']:.6f} "
            f"Leland informé={informed_leland_metrics['cvar_loss_95']:.6f}",
            flush=True,
        )

    result = {
        "status": "sensibilités sur jeux de développement — non finales",
        "device": "cpu",
        "torch_version": torch.__version__,
        "final_test_used": False,
        "frequency_experiment": {
            "one_way_cost": cost,
            "n_steps": [10, 20, 30],
            "fine_grid_steps": 60,
            "coupled_development_paths": True,
            "development_seed": frequency_seed,
            "development_size": 100_000,
            "training_budget_epochs": 2_000,
            "scenarios": frequency_rows,
            "paired_frequency_comparisons": frequency_comparisons,
        },
        "volatility_experiment": {
            "one_way_cost": cost,
            "training_sigma": training_market.sigma,
            "scenario_sigmas": [0.15, 0.20, 0.25, 0.30],
            "development_seed": volatility_seed,
            "development_size": 100_000,
            "common_standard_normal_shocks": True,
            "premium_fixed_at_training_model": True,
            "scenarios": volatility_rows,
        },
        "reserved_final_test": {
            "seed": 20269000,
            "size": 250_000,
            "status": "préenregistré et non exécuté",
        },
    }
    write_json(OUTPUT, result)


if __name__ == "__main__":
    main()
