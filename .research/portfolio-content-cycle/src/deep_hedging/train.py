"""Boucle d'apprentissage avec validation indépendante."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import random

import numpy as np
import torch
from torch import Tensor

from .core import (
    MarketConfig,
    black_scholes_call,
    rockafellar_uryasev_cvar,
    simulate_gbm,
    strategy_pnl,
    summarize_pnl,
)
from .model import HedgingPolicy


@dataclass(frozen=True)
class TrainConfig:
    epochs: int = 30
    batch_size: int = 4_096
    validation_size: int = 20_000
    learning_rate: float = 1e-3
    eta_learning_rate: float = 5e-3
    alpha: float = 0.95
    one_way_cost: float = 0.0025
    model_seed: int = 20260911
    train_seed: int = 20261000
    validation_seed: int = 20262000
    gradient_clip: float = 5.0


def set_reproducible_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def initial_premium(config: MarketConfig, dtype: torch.dtype = torch.float32) -> Tensor:
    return black_scholes_call(
        torch.tensor(config.s0, dtype=dtype),
        config.strike,
        torch.tensor(config.maturity, dtype=dtype),
        config.rate,
        config.sigma,
    )


def evaluate_policy(
    policy: HedgingPolicy,
    paths: Tensor,
    config: MarketConfig,
    train_config: TrainConfig,
    premium: Tensor,
) -> dict[str, float]:
    policy.eval()
    with torch.no_grad():
        positions = policy(paths, config)
        pnl, costs, turnover = strategy_pnl(
            paths,
            positions,
            premium,
            train_config.one_way_cost,
            config.strike,
        )
    return summarize_pnl(pnl, costs, turnover, train_config.alpha)


def train_policy(
    config: MarketConfig,
    train_config: TrainConfig,
    *,
    device: str | torch.device = "cpu",
) -> tuple[HedgingPolicy, list[dict[str, float]], float]:
    set_reproducible_seed(train_config.model_seed)
    policy = HedgingPolicy().to(device)
    premium_cpu = initial_premium(config)
    premium = premium_cpu.to(device)
    calibration_paths = simulate_gbm(
        max(train_config.batch_size, 8_192),
        config,
        train_config.train_seed - 1,
        device=device,
    )
    with torch.no_grad():
        calibration_positions = policy(calibration_paths, config)
        calibration_pnl, _, _ = strategy_pnl(
            calibration_paths,
            calibration_positions,
            premium,
            train_config.one_way_cost,
            config.strike,
        )
        eta_start = torch.quantile(-calibration_pnl, train_config.alpha)
    eta = torch.nn.Parameter(eta_start.clone())
    optimizer = torch.optim.Adam(
        [
            {"params": policy.parameters(), "lr": train_config.learning_rate},
            {"params": [eta], "lr": train_config.eta_learning_rate},
        ]
    )
    validation_paths = simulate_gbm(
        train_config.validation_size,
        config,
        train_config.validation_seed,
        device=device,
    )

    history: list[dict[str, float]] = []
    best_cvar = float("inf")
    best_state: dict[str, Tensor] | None = None
    best_eta = float(eta.detach().cpu())

    for epoch in range(train_config.epochs):
        policy.train()
        paths = simulate_gbm(
            train_config.batch_size,
            config,
            train_config.train_seed + epoch,
            device=device,
        )
        positions = policy(paths, config)
        pnl, _, _ = strategy_pnl(
            paths,
            positions,
            premium,
            train_config.one_way_cost,
            config.strike,
        )
        objective = rockafellar_uryasev_cvar(-pnl, eta, train_config.alpha)
        if not torch.isfinite(objective):
            raise FloatingPointError("objectif d'apprentissage non fini")
        optimizer.zero_grad(set_to_none=True)
        objective.backward()
        torch.nn.utils.clip_grad_norm_(
            [*policy.parameters(), eta], train_config.gradient_clip
        )
        optimizer.step()

        metrics = evaluate_policy(
            policy, validation_paths, config, train_config, premium
        )
        record = {
            "epoch": float(epoch + 1),
            "train_objective": float(objective.detach().cpu()),
            "eta": float(eta.detach().cpu()),
            **metrics,
        }
        history.append(record)
        if metrics["cvar_loss_95"] < best_cvar:
            best_cvar = metrics["cvar_loss_95"]
            best_state = copy.deepcopy(policy.state_dict())
            best_eta = float(eta.detach().cpu())

    if best_state is None:
        raise RuntimeError("aucun état valide produit")
    policy.load_state_dict(best_state)
    return policy, history, best_eta
