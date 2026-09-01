"""Robustesse hors modèle de la politique GBM sous un scénario Heston."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import torch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from deep_hedging.core import (  # noqa: E402
    HestonConfig,
    MarketConfig,
    black_scholes_delta_paths,
    black_scholes_delta_paths_local_volatility,
    leland_volatility,
    simulate_heston,
    strategy_pnl,
    summarize_pnl,
)
from deep_hedging.model import HedgingPolicy  # noqa: E402
from deep_hedging.statistics import paired_cvar_improvement_bootstrap  # noqa: E402
from deep_hedging.train import initial_premium  # noqa: E402


OUTPUT = Path(__file__).with_name("heston-robustness.json")
CHECKPOINT = ROOT / "checkpoints" / "convergence-2000.pt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--development-size", type=int, default=100_000)
    parser.add_argument("--diagnostic-size", type=int, default=50_000)
    parser.add_argument("--bootstrap", type=int, default=1_000)
    return parser.parse_args()


def load_policy() -> HedgingPolicy:
    checkpoint = torch.load(CHECKPOINT, map_location="cpu", weights_only=True)
    policy = HedgingPolicy()
    policy.load_state_dict(checkpoint["policy_state_dict"])
    policy.eval()
    return policy


def generate_shocks(
    n_paths: int,
    fine_steps: int,
    seed: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed)
    shape = (n_paths, fine_steps)
    return (
        torch.randn(shape, generator=generator),
        torch.randn(shape, generator=generator),
    )


def coarsen_shocks(
    shocks: torch.Tensor,
    n_steps: int,
    source_substeps: int,
    target_substeps: int,
) -> torch.Tensor:
    if source_substeps % target_substeps != 0:
        raise ValueError("la grille cible doit diviser la grille source")
    group = source_substeps // target_substeps
    reshaped = shocks.reshape(
        shocks.shape[0], n_steps, target_substeps, group
    )
    return (reshaped.sum(dim=-1) / math.sqrt(group)).reshape(
        shocks.shape[0], n_steps * target_substeps
    )


def moment_diagnostics(
    spots: torch.Tensor,
    variances: torch.Tensor,
    config: HestonConfig,
) -> dict[str, float]:
    terminal_spot = spots[:, -1].double()
    terminal_variance = variances[:, -1].double()
    log_return = torch.log(terminal_spot / config.s0)
    expected_spot = config.s0 * math.exp(config.rate * config.maturity)
    expected_variance = config.theta + (
        config.v0 - config.theta
    ) * math.exp(-config.kappa * config.maturity)
    spot_se = float(terminal_spot.std(correction=1) / math.sqrt(spots.shape[0]))
    variance_se = float(
        terminal_variance.std(correction=1) / math.sqrt(spots.shape[0])
    )
    centered_return = log_return - log_return.mean()
    return_std = log_return.std(correction=0)
    skewness = float(torch.mean(centered_return**3) / return_std**3)
    return {
        "expected_terminal_spot": expected_spot,
        "sample_terminal_spot_mean": float(terminal_spot.mean()),
        "terminal_spot_standard_error": spot_se,
        "terminal_spot_z_score": (
            float(terminal_spot.mean()) - expected_spot
        )
        / spot_se,
        "expected_terminal_variance": expected_variance,
        "sample_terminal_variance_mean": float(terminal_variance.mean()),
        "terminal_variance_standard_error": variance_se,
        "terminal_variance_z_score": (
            float(terminal_variance.mean()) - expected_variance
        )
        / variance_se,
        "terminal_log_return_skewness": skewness,
        "zero_variance_share_at_decision_dates": float(
            torch.mean((variances == 0).to(torch.float64))
        ),
    }


def build_positions(
    paths: torch.Tensor,
    variance_paths: torch.Tensor,
    market: MarketConfig,
    policy: HedgingPolicy,
    one_way_cost: float,
) -> dict[str, torch.Tensor]:
    fixed_delta = black_scholes_delta_paths(paths, market)
    fixed_leland_sigma = leland_volatility(market, one_way_cost)
    fixed_leland = black_scholes_delta_paths(
        paths, market, volatility=fixed_leland_sigma
    )
    local_sigma = torch.sqrt(torch.clamp(variance_paths[:, :-1], min=0.0))
    safe_local_sigma = torch.clamp(local_sigma, min=1e-4)
    informed_delta = black_scholes_delta_paths_local_volatility(
        paths, market, safe_local_sigma
    )
    informed_leland_sigma = safe_local_sigma * torch.sqrt(
        1.0
        + math.sqrt(8.0 / math.pi)
        * one_way_cost
        / (safe_local_sigma * math.sqrt(market.dt))
    )
    informed_leland = black_scholes_delta_paths_local_volatility(
        paths, market, informed_leland_sigma
    )
    with torch.no_grad():
        neural = policy(paths, market)
    return {
        "unhedged": torch.zeros_like(paths[:, :-1]),
        "neural_frozen_without_variance_state": neural,
        "delta_frozen_sigma_20": fixed_delta,
        "leland_frozen_sigma_20": fixed_leland,
        "delta_instantaneous_variance_proxy": informed_delta,
        "leland_instantaneous_variance_proxy": informed_leland,
    }


def evaluate_positions(
    paths: torch.Tensor,
    positions: dict[str, torch.Tensor],
    market: MarketConfig,
    premium: torch.Tensor,
    one_way_cost: float,
) -> tuple[dict[str, dict[str, float]], dict[str, torch.Tensor]]:
    metrics: dict[str, dict[str, float]] = {}
    losses: dict[str, torch.Tensor] = {}
    with torch.no_grad():
        for name, strategy_positions in positions.items():
            pnl = strategy_pnl(
                paths,
                strategy_positions,
                premium,
                one_way_cost,
                market.strike,
            )
            metrics[name] = summarize_pnl(*pnl)
            losses[name] = -pnl[0].detach()
    return metrics, losses


def loss_quantiles(losses: torch.Tensor) -> dict[str, float]:
    probabilities = torch.tensor(
        [0.50, 0.90, 0.95, 0.99, 0.995], dtype=losses.dtype
    )
    values = torch.quantile(losses, probabilities)
    return {
        label: float(value)
        for label, value in zip(
            ("q50", "q90", "q95", "q99", "q99_5"), values, strict=True
        )
    }


def main() -> None:
    args = parse_args()
    if args.development_size <= 0 or args.diagnostic_size <= 0:
        raise ValueError("les tailles doivent être strictement positives")
    if args.bootstrap <= 1:
        raise ValueError("bootstrap doit être supérieur à un")
    torch.use_deterministic_algorithms(True)

    heston = HestonConfig()
    market = MarketConfig(n_steps=heston.n_steps)
    one_way_cost = 0.0025
    premium = initial_premium(market)
    policy = load_policy()

    diagnostic_seed = 20263350
    source_substeps = 8
    source_steps = heston.n_steps * source_substeps
    fine_variance_shocks, fine_independent_shocks = generate_shocks(
        args.diagnostic_size, source_steps, diagnostic_seed
    )
    discretization_rows: list[dict[str, object]] = []
    for substeps in (2, 4, 8):
        scenario = HestonConfig(substeps_per_step=substeps)
        variance_shocks = coarsen_shocks(
            fine_variance_shocks,
            scenario.n_steps,
            source_substeps,
            substeps,
        )
        independent_shocks = coarsen_shocks(
            fine_independent_shocks,
            scenario.n_steps,
            source_substeps,
            substeps,
        )
        spots, variances = simulate_heston(
            args.diagnostic_size,
            scenario,
            diagnostic_seed,
            variance_shocks=variance_shocks,
            independent_shocks=independent_shocks,
        )
        positions = build_positions(
            spots, variances, market, policy, one_way_cost
        )
        metrics, _ = evaluate_positions(
            spots, positions, market, premium, one_way_cost
        )
        discretization_rows.append(
            {
                "substeps_per_hedging_step": substeps,
                "fine_time_steps": scenario.fine_steps,
                "moments": moment_diagnostics(spots, variances, scenario),
                "development_metrics": metrics,
            }
        )
        print(
            f"sous-pas={substeps} "
            f"E[S_T]={spots[:, -1].mean():.5f} "
            "CVaR réseau="
            f"{metrics['neural_frozen_without_variance_state']['cvar_loss_95']:.6f}",
            flush=True,
        )

    development_seed = 20263300
    paths, variances = simulate_heston(
        args.development_size, heston, development_seed
    )
    positions = build_positions(paths, variances, market, policy, one_way_cost)
    metrics, losses = evaluate_positions(
        paths, positions, market, premium, one_way_cost
    )
    neural_losses = losses["neural_frozen_without_variance_state"]
    comparisons = {}
    for index, reference in enumerate(
        (
            "leland_frozen_sigma_20",
            "leland_instantaneous_variance_proxy",
        )
    ):
        comparisons[f"neural_versus_{reference}"] = (
            paired_cvar_improvement_bootstrap(
                losses[reference].numpy(),
                neural_losses.numpy(),
                n_bootstrap=args.bootstrap,
                seed=20263400 + index,
            )
        )

    result = {
        "status": "robustesse Heston sur jeu de développement — non finale",
        "device": "cpu",
        "torch_version": torch.__version__,
        "final_test_used": False,
        "scenario_nature": (
            "paramétrage stylisé non calibré ; variance moyenne égale au "
            "modèle GBM d’entraînement"
        ),
        "simulation_scheme": {
            "variance": "Euler full truncation",
            "spot": "log-Euler",
            "reference": "Lord, Koekkoek et van Dijk (2010)",
            "doi": "10.1080/14697680802392496",
        },
        "heston_parameters": heston.__dict__,
        "feller_margin": heston.feller_margin,
        "feller_condition_satisfied": heston.feller_margin >= 0,
        "training_market": market.__dict__,
        "policy_receives_variance_state": False,
        "one_way_cost": one_way_cost,
        "premium_convention": {
            "value": float(premium),
            "definition": "prix Black–Scholes du modèle d’entraînement à 20 %",
            "comparison_effect": (
                "translation commune des pertes ; les écarts de CVaR entre "
                "stratégies d’un même scénario sont invariants"
            ),
        },
        "discretization_diagnostic": {
            "coupled_brownian_increments": True,
            "seed": diagnostic_seed,
            "size": args.diagnostic_size,
            "scenarios": discretization_rows,
        },
        "development_evaluation": {
            "seed": development_seed,
            "size": args.development_size,
            "substeps_per_hedging_step": heston.substeps_per_step,
            "moments": moment_diagnostics(paths, variances, heston),
            "metrics": metrics,
            "loss_quantiles": {
                name: loss_quantiles(strategy_losses)
                for name, strategy_losses in losses.items()
            },
            "paired_bootstrap": comparisons,
        },
        "baseline_warning": (
            "les proxys à variance instantanée utilisent une delta "
            "Black–Scholes locale ; ce ne sont pas des deltas analytiques "
            "optimales du modèle Heston"
        ),
        "reserved_final_test": {
            "seed": 20269000,
            "size": 250_000,
            "status": "préenregistré et non exécuté",
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
