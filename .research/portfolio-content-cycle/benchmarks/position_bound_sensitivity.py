"""Sensibilité à la borne maximale de la position de couverture."""

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
from deep_hedging.statistics import (  # noqa: E402
    paired_cvar_improvement_bootstrap,
    paired_mean_improvement_bootstrap,
)
from deep_hedging.train import (  # noqa: E402
    TrainConfig,
    initial_premium,
    train_policy,
)


OUTPUT = Path(__file__).with_name("position-bound-sensitivity.json")
HISTORIES = Path(__file__).with_name("position-bound-histories")
CHECKPOINTS = ROOT / "checkpoints"
CENTRAL_CHECKPOINT = CHECKPOINTS / "convergence-2000.pt"
CENTRAL_RESULT = Path(__file__).with_name("convergence-2000.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--bootstrap", type=int, default=1_000)
    return parser.parse_args()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def specifications() -> list[dict[str, object]]:
    return [
        {
            "name": "bound_1_25_central",
            "max_position": 1.25,
            "role": "référence centrale",
        },
        {
            "name": "bound_1_00",
            "max_position": 1.00,
            "role": "borne resserrée",
        },
        {
            "name": "bound_1_50",
            "max_position": 1.50,
            "role": "borne élargie",
        },
    ]


def make_policy(specification: dict[str, object]) -> HedgingPolicy:
    return HedgingPolicy(
        hidden_size=32,
        max_position=float(specification["max_position"]),
        include_inventory=True,
    )


def variant_paths(name: str) -> tuple[Path, Path]:
    return (
        CHECKPOINTS / f"position-{name}.pt",
        HISTORIES / f"{name}.json",
    )


def load_policy(path: Path, specification: dict[str, object]) -> HedgingPolicy:
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    policy = make_policy(specification)
    policy.load_state_dict(checkpoint["policy_state_dict"])
    policy.eval()
    return policy


def load_or_train(
    specification: dict[str, object],
    market: MarketConfig,
    training: TrainConfig,
    resume: bool,
) -> tuple[HedgingPolicy, dict[str, float], float, float, str, str]:
    name = str(specification["name"])
    if name == "bound_1_25_central":
        policy = load_policy(CENTRAL_CHECKPOINT, specification)
        previous = json.loads(CENTRAL_RESULT.read_text(encoding="utf-8"))
        return (
            policy,
            previous["best_validation"],
            float(previous["best_eta"]),
            0.0,
            "checkpoint central validé à 2 000 époques",
            str(CENTRAL_RESULT.relative_to(ROOT)),
        )

    checkpoint_path, history_path = variant_paths(name)
    if resume and checkpoint_path.exists() and history_path.exists():
        policy = load_policy(checkpoint_path, specification)
        previous = json.loads(history_path.read_text(encoding="utf-8"))
        best_validation = min(
            previous["history"], key=lambda row: row["cvar_loss_95"]
        )
        return (
            policy,
            best_validation,
            float(previous["best_eta"]),
            0.0,
            str(previous["training_provenance"]),
            str(history_path.relative_to(ROOT)),
        )

    started = time.perf_counter()
    policy, history, best_eta = train_policy(
        market,
        training,
        device="cpu",
        policy_factory=lambda: make_policy(specification),
    )
    elapsed = time.perf_counter() - started
    best_validation = min(history, key=lambda row: row["cvar_loss_95"])
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "policy_state_dict": policy.state_dict(),
            "market": market.__dict__,
            "training": training.__dict__,
            "model_specification": specification,
            "best_epoch": int(best_validation["epoch"]),
            "best_eta": best_eta,
        },
        checkpoint_path,
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
            "model_specification": specification,
            "parameter_count": sum(
                parameter.numel() for parameter in policy.parameters()
            ),
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
        best_validation,
        best_eta,
        elapsed,
        "réentraînement complet de 2 000 époques",
        str(history_path.relative_to(ROOT)),
    )


def position_distribution(
    positions: torch.Tensor,
    max_position: float,
) -> dict[str, float]:
    flattened = positions.flatten()
    probabilities = torch.tensor(
        [0.001, 0.01, 0.50, 0.99, 0.999], dtype=positions.dtype
    )
    quantiles = torch.quantile(flattened, probabilities)
    return {
        "minimum": float(torch.min(flattened)),
        "q001": float(quantiles[0]),
        "q010": float(quantiles[1]),
        "q500": float(quantiles[2]),
        "q990": float(quantiles[3]),
        "q999": float(quantiles[4]),
        "maximum": float(torch.max(flattened)),
        "share_below_one_percent_of_bound": float(
            torch.mean((flattened <= 0.01 * max_position).to(positions.dtype))
        ),
        "share_above_ninety_nine_percent_of_bound": float(
            torch.mean((flattened >= 0.99 * max_position).to(positions.dtype))
        ),
        "share_above_one": float(
            torch.mean((flattened > 1.0).to(positions.dtype))
        ),
    }


def main() -> None:
    args = parse_args()
    if args.bootstrap <= 1:
        raise ValueError("bootstrap doit être supérieur à un")
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
    premium = initial_premium(market)
    development_seed = 20263000
    paths = simulate_gbm(100_000, market, development_seed, device="cpu")
    leland_sigma = leland_volatility(market, training.one_way_cost)
    leland_positions = black_scholes_delta_paths(
        paths, market, volatility=leland_sigma
    )
    leland = strategy_pnl(
        paths,
        leland_positions,
        premium,
        training.one_way_cost,
        market.strike,
    )

    result: dict[str, object] = {
        "status": "sensibilité à la borne sur développement — non finale",
        "device": "cpu",
        "torch_version": torch.__version__,
        "market": market.__dict__,
        "training": training.__dict__,
        "development_seed": development_seed,
        "development_size": int(paths.shape[0]),
        "leland_adjusted_volatility": leland_sigma,
        "leland_development_metrics": summarize_pnl(*leland),
        "same_training_stream_across_variants": True,
        "bootstrap_replicates": args.bootstrap,
        "final_test_used": False,
        "variants": [],
        "reserved_final_test": {
            "seed": 20269000,
            "size": 250_000,
            "status": "préenregistré et non exécuté",
        },
    }
    rows = result["variants"]
    assert isinstance(rows, list)
    losses: dict[str, torch.Tensor] = {}
    turnovers: dict[str, torch.Tensor] = {}

    for index, specification in enumerate(specifications()):
        (
            policy,
            best_validation,
            best_eta,
            elapsed,
            provenance,
            history_file,
        ) = load_or_train(specification, market, training, args.resume)
        name = str(specification["name"])
        max_position = float(specification["max_position"])
        with torch.no_grad():
            positions = policy(paths, market)
            pnl = strategy_pnl(
                paths,
                positions,
                premium,
                training.one_way_cost,
                market.strike,
            )
        losses[name] = -pnl[0].detach()
        turnovers[name] = pnl[2].detach()
        metrics = summarize_pnl(*pnl)
        rows.append(
            {
                "name": name,
                "role": specification["role"],
                "max_position": max_position,
                "parameter_count": sum(
                    parameter.numel() for parameter in policy.parameters()
                ),
                "training_provenance": provenance,
                "elapsed_seconds_this_run": elapsed,
                "best_epoch": int(best_validation["epoch"]),
                "best_eta": best_eta,
                "best_validation": best_validation,
                "development_metrics": metrics,
                "position_distribution": position_distribution(
                    positions, max_position
                ),
                "paired_bootstrap_versus_leland": (
                    paired_cvar_improvement_bootstrap(
                        (-leland[0]).numpy(),
                        losses[name].numpy(),
                        n_bootstrap=args.bootstrap,
                        seed=20264100 + index,
                    )
                ),
                "history_file": history_file,
            }
        )
        write_json(OUTPUT, result)
        print(
            f"{name}: époque={int(best_validation['epoch'])} "
            f"CVaR={metrics['cvar_loss_95']:.6f} "
            f"turnover={metrics['mean_turnover_notional']:.3f} "
            f"max={torch.max(positions):.4f}",
            flush=True,
        )

    central_name = "bound_1_25_central"
    for index, row in enumerate(rows):
        name = str(row["name"])
        if name == central_name:
            row["central_improvement_over_variant"] = None
            row["central_turnover_reduction_over_variant"] = None
            continue
        row["central_improvement_over_variant"] = (
            paired_cvar_improvement_bootstrap(
                losses[name].numpy(),
                losses[central_name].numpy(),
                n_bootstrap=args.bootstrap,
                seed=20264200 + index,
            )
        )
        row["central_turnover_reduction_over_variant"] = (
            paired_mean_improvement_bootstrap(
                turnovers[name].numpy(),
                turnovers[central_name].numpy(),
                n_bootstrap=args.bootstrap,
                seed=20264300 + index,
            )
        )
    write_json(OUTPUT, result)


if __name__ == "__main__":
    main()
