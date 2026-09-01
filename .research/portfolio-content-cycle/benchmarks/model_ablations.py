"""Ablations de l'inventaire précédent et de la capacité du réseau."""

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


OUTPUT = Path(__file__).with_name("model-ablations.json")
HISTORIES = Path(__file__).with_name("model-ablation-histories")
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


def parameter_count(policy: HedgingPolicy) -> int:
    return sum(parameter.numel() for parameter in policy.parameters())


def variants() -> list[dict[str, object]]:
    return [
        {
            "name": "central_inventory_h32",
            "hidden_size": 32,
            "include_inventory": True,
            "role": "référence centrale",
        },
        {
            "name": "without_inventory_h32",
            "hidden_size": 32,
            "include_inventory": False,
            "role": "ablation de l’état",
        },
        {
            "name": "inventory_h16",
            "hidden_size": 16,
            "include_inventory": True,
            "role": "capacité réduite",
        },
        {
            "name": "inventory_h64",
            "hidden_size": 64,
            "include_inventory": True,
            "role": "capacité augmentée",
        },
    ]


def make_policy(specification: dict[str, object]) -> HedgingPolicy:
    return HedgingPolicy(
        hidden_size=int(specification["hidden_size"]),
        include_inventory=bool(specification["include_inventory"]),
    )


def variant_paths(name: str) -> tuple[Path, Path]:
    return (
        CHECKPOINTS / f"ablation-{name}.pt",
        HISTORIES / f"{name}.json",
    )


def load_policy(path: Path, specification: dict[str, object]) -> HedgingPolicy:
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    policy = make_policy(specification)
    policy.load_state_dict(checkpoint["policy_state_dict"])
    policy.eval()
    return policy


def save_checkpoint(
    path: Path,
    policy: HedgingPolicy,
    market: MarketConfig,
    training: TrainConfig,
    specification: dict[str, object],
    best_validation: dict[str, float],
    best_eta: float,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "policy_state_dict": policy.state_dict(),
            "market": market.__dict__,
            "training": training.__dict__,
            "model_specification": specification,
            "best_epoch": int(best_validation["epoch"]),
            "best_eta": best_eta,
        },
        path,
    )


def load_or_train(
    specification: dict[str, object],
    market: MarketConfig,
    training: TrainConfig,
    resume: bool,
) -> tuple[
    HedgingPolicy,
    list[dict[str, float]],
    dict[str, float],
    float,
    float,
    str,
    str,
]:
    name = str(specification["name"])
    if name == "central_inventory_h32":
        policy = load_policy(CENTRAL_CHECKPOINT, specification)
        previous = json.loads(CENTRAL_RESULT.read_text(encoding="utf-8"))
        return (
            policy,
            previous["history"],
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
        history = previous["history"]
        best_validation = min(
            history, key=lambda row: row["cvar_loss_95"]
        )
        return (
            policy,
            history,
            best_validation,
            float(previous["best_eta"]),
            0.0,
            str(
                previous.get(
                    "training_provenance",
                    "checkpoint local repris après interruption",
                )
            ),
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
    save_checkpoint(
        checkpoint_path,
        policy,
        market,
        training,
        specification,
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
            "model_specification": specification,
            "parameter_count": parameter_count(policy),
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
        str(history_path.relative_to(ROOT)),
    )


def position_diagnostics(
    positions: torch.Tensor,
    central_positions: torch.Tensor,
) -> dict[str, float]:
    previous = torch.cat(
        (torch.zeros_like(positions[:, :1]), positions[:, :-1]), dim=1
    )
    flattened = positions.flatten()
    central_flattened = central_positions.flatten()
    correlation = torch.corrcoef(
        torch.stack((flattened, central_flattened))
    )[0, 1]
    return {
        "mean_position": float(torch.mean(positions)),
        "mean_absolute_trade_units": float(
            torch.mean(torch.abs(positions - previous))
        ),
        "mean_absolute_position_gap_to_central": float(
            torch.mean(torch.abs(positions - central_positions))
        ),
        "position_correlation_with_central": float(correlation),
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
    leland_metrics = summarize_pnl(*leland)

    result: dict[str, object] = {
        "status": "ablations du modèle sur développement — non finales",
        "device": "cpu",
        "torch_version": torch.__version__,
        "market": market.__dict__,
        "training": training.__dict__,
        "development_seed": development_seed,
        "development_size": int(paths.shape[0]),
        "one_way_cost": training.one_way_cost,
        "leland_adjusted_volatility": leland_sigma,
        "leland_development_metrics": leland_metrics,
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
    policies: dict[str, HedgingPolicy] = {}
    positions_by_name: dict[str, torch.Tensor] = {}
    losses_by_name: dict[str, torch.Tensor] = {}
    turnover_by_name: dict[str, torch.Tensor] = {}

    for index, specification in enumerate(variants()):
        (
            policy,
            history,
            best_validation,
            best_eta,
            elapsed,
            provenance,
            history_file,
        ) = load_or_train(specification, market, training, args.resume)
        name = str(specification["name"])
        policies[name] = policy
        with torch.no_grad():
            variant_positions = policy(paths, market)
            pnl = strategy_pnl(
                paths,
                variant_positions,
                premium,
                training.one_way_cost,
                market.strike,
            )
        positions_by_name[name] = variant_positions
        losses_by_name[name] = -pnl[0].detach()
        turnover_by_name[name] = pnl[2].detach()
        metrics = summarize_pnl(*pnl)
        versus_leland = paired_cvar_improvement_bootstrap(
            (-leland[0]).numpy(),
            losses_by_name[name].numpy(),
            n_bootstrap=args.bootstrap,
            seed=20263800 + index,
        )
        rows.append(
            {
                "name": name,
                "role": specification["role"],
                "hidden_size": specification["hidden_size"],
                "include_inventory": specification["include_inventory"],
                "parameter_count": parameter_count(policy),
                "training_provenance": provenance,
                "elapsed_seconds_this_run": elapsed,
                "best_epoch": int(best_validation["epoch"]),
                "best_eta": best_eta,
                "best_validation": best_validation,
                "development_metrics": metrics,
                "paired_bootstrap_versus_leland": versus_leland,
                "history_file": history_file,
            }
        )
        write_json(OUTPUT, result)
        print(
            f"{name}: paramètres={parameter_count(policy)} "
            f"époque={int(best_validation['epoch'])} "
            f"CVaR={metrics['cvar_loss_95']:.6f} "
            f"turnover={metrics['mean_turnover_notional']:.3f}",
            flush=True,
        )

    central_name = "central_inventory_h32"
    central_positions = positions_by_name[central_name]
    central_losses = losses_by_name[central_name]
    for index, row in enumerate(rows):
        name = str(row["name"])
        row["position_diagnostics"] = position_diagnostics(
            positions_by_name[name], central_positions
        )
        if name == central_name:
            row["central_improvement_over_variant"] = None
            row["central_turnover_reduction_over_variant"] = None
            continue
        row["central_improvement_over_variant"] = (
            paired_cvar_improvement_bootstrap(
                losses_by_name[name].numpy(),
                central_losses.numpy(),
                n_bootstrap=args.bootstrap,
                seed=20263900 + index,
            )
        )
        row["central_turnover_reduction_over_variant"] = (
            paired_mean_improvement_bootstrap(
                turnover_by_name[name].numpy(),
                turnover_by_name[central_name].numpy(),
                n_bootstrap=args.bootstrap,
                seed=20264000 + index,
            )
        )
    write_json(OUTPUT, result)


if __name__ == "__main__":
    main()
