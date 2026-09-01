"""Sensibilité Heston à la corrélation et à la volatilité de la variance."""

from __future__ import annotations

import argparse
from dataclasses import replace
import gc
import json
from pathlib import Path
import sys

import torch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from deep_hedging.core import HestonConfig, MarketConfig, simulate_heston  # noqa: E402
from deep_hedging.statistics import paired_cvar_improvement_bootstrap  # noqa: E402
from deep_hedging.train import initial_premium  # noqa: E402
from heston_robustness import (  # noqa: E402
    build_positions,
    coarsen_shocks,
    evaluate_positions,
    generate_shocks,
    load_policy,
    loss_quantiles,
    moment_diagnostics,
)


OUTPUT = Path(__file__).with_name("heston-parameter-sensitivity.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--development-size", type=int, default=100_000)
    parser.add_argument("--diagnostic-size", type=int, default=50_000)
    parser.add_argument("--bootstrap", type=int, default=1_000)
    return parser.parse_args()


def scenario_grid() -> list[tuple[str, HestonConfig]]:
    central = HestonConfig()
    return [
        ("moderate_volvol_with_leverage", central),
        ("moderate_volvol_without_leverage", replace(central, rho=0.0)),
        (
            "high_volvol_with_leverage",
            replace(central, vol_of_vol=0.60),
        ),
        (
            "high_volvol_without_leverage",
            replace(central, vol_of_vol=0.60, rho=0.0),
        ),
    ]


def paired_comparisons(
    losses: dict[str, torch.Tensor],
    n_bootstrap: int,
    seed_offset: int,
) -> dict[str, dict[str, float | int]]:
    neural = losses["neural_frozen_without_variance_state"]
    result = {}
    for index, reference in enumerate(
        (
            "leland_frozen_sigma_20",
            "leland_instantaneous_variance_proxy",
        )
    ):
        result[f"neural_versus_{reference}"] = (
            paired_cvar_improvement_bootstrap(
                losses[reference].numpy(),
                neural.numpy(),
                n_bootstrap=n_bootstrap,
                seed=20263600 + seed_offset + index,
            )
        )
    return result


def stress_discretization(
    n_paths: int,
    policy: torch.nn.Module,
    market: MarketConfig,
    premium: torch.Tensor,
    one_way_cost: float,
) -> dict[str, object]:
    seed = 20263550
    fine_substeps = 8
    fine_config = HestonConfig(vol_of_vol=0.60, substeps_per_step=fine_substeps)
    variance_fine, independent_fine = generate_shocks(
        n_paths, fine_config.fine_steps, seed
    )
    scenario_groups = []
    for name, rho in (
        ("high_volvol_with_leverage", -0.70),
        ("high_volvol_without_leverage", 0.0),
    ):
        rows = []
        for substeps in (4, 8):
            scenario = replace(
                fine_config, rho=rho, substeps_per_step=substeps
            )
            variance_shocks = coarsen_shocks(
                variance_fine,
                scenario.n_steps,
                fine_substeps,
                substeps,
            )
            independent_shocks = coarsen_shocks(
                independent_fine,
                scenario.n_steps,
                fine_substeps,
                substeps,
            )
            paths, variances = simulate_heston(
                n_paths,
                scenario,
                seed,
                variance_shocks=variance_shocks,
                independent_shocks=independent_shocks,
            )
            positions = build_positions(
                paths, variances, market, policy, one_way_cost
            )
            metrics, _ = evaluate_positions(
                paths, positions, market, premium, one_way_cost
            )
            rows.append(
                {
                    "substeps_per_hedging_step": substeps,
                    "fine_time_steps": scenario.fine_steps,
                    "moments": moment_diagnostics(paths, variances, scenario),
                    "metrics": metrics,
                }
            )
        scenario_groups.append({"name": name, "scenarios": rows})
    return {
        "scenarios_checked": [
            "high_volvol_with_leverage",
            "high_volvol_without_leverage",
        ],
        "coupled_brownian_increments": True,
        "seed": seed,
        "size": n_paths,
        "scenario_groups": scenario_groups,
    }


def main() -> None:
    args = parse_args()
    if args.development_size <= 0 or args.diagnostic_size <= 0:
        raise ValueError("les tailles doivent être strictement positives")
    if args.bootstrap <= 1:
        raise ValueError("bootstrap doit être supérieur à un")
    torch.use_deterministic_algorithms(True)

    market = MarketConfig()
    policy = load_policy()
    premium = initial_premium(market)
    one_way_cost = 0.0025
    discretization = stress_discretization(
        args.diagnostic_size, policy, market, premium, one_way_cost
    )
    gc.collect()

    seed = 20263300
    central = HestonConfig()
    variance_shocks, independent_shocks = generate_shocks(
        args.development_size, central.fine_steps, seed
    )
    rows: list[dict[str, object]] = []
    for index, (name, scenario) in enumerate(scenario_grid()):
        paths, variances = simulate_heston(
            args.development_size,
            scenario,
            seed,
            variance_shocks=variance_shocks,
            independent_shocks=independent_shocks,
        )
        positions = build_positions(
            paths, variances, market, policy, one_way_cost
        )
        metrics, losses = evaluate_positions(
            paths, positions, market, premium, one_way_cost
        )
        comparisons = paired_comparisons(
            losses, args.bootstrap, seed_offset=10 * index
        )
        rows.append(
            {
                "name": name,
                "parameters": scenario.__dict__,
                "feller_margin": scenario.feller_margin,
                "feller_condition_satisfied": scenario.feller_margin >= 0,
                "moments": moment_diagnostics(paths, variances, scenario),
                "metrics": metrics,
                "loss_quantiles": {
                    strategy: loss_quantiles(strategy_losses)
                    for strategy, strategy_losses in losses.items()
                },
                "paired_bootstrap": comparisons,
            }
        )
        neural_cvar = metrics[
            "neural_frozen_without_variance_state"
        ]["cvar_loss_95"]
        proxy_cvar = metrics[
            "leland_instantaneous_variance_proxy"
        ]["cvar_loss_95"]
        print(
            f"{name}: CVaR réseau={neural_cvar:.6f}, "
            f"proxy Leland={proxy_cvar:.6f}",
            flush=True,
        )

    result = {
        "status": "sensibilité Heston sur jeux de développement — non finale",
        "device": "cpu",
        "torch_version": torch.__version__,
        "final_test_used": False,
        "design": {
            "factors": {
                "rho": [-0.70, 0.0],
                "vol_of_vol": [0.35, 0.60],
            },
            "fixed_parameters": {
                "s0": central.s0,
                "maturity": central.maturity,
                "rate": central.rate,
                "v0": central.v0,
                "kappa": central.kappa,
                "theta": central.theta,
                "n_steps": central.n_steps,
                "substeps_per_step": central.substeps_per_step,
            },
            "scenario_nature": "grille stylisée non calibrée sur un marché",
            "common_random_numbers": True,
        },
        "development_seed": seed,
        "development_size": args.development_size,
        "policy_receives_variance_state": False,
        "one_way_cost": one_way_cost,
        "premium_convention": {
            "value": float(premium),
            "definition": "prix Black–Scholes du modèle d’entraînement à 20 %",
            "comparison_effect": (
                "translation commune des pertes dans chaque scénario"
            ),
        },
        "scenarios": rows,
        "high_volvol_discretization_diagnostic": discretization,
        "baseline_warning": (
            "le proxy adaptatif emploie la variance instantanée dans une "
            "delta Black–Scholes locale ; il ne s’agit pas de la delta "
            "analytique de Heston"
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
