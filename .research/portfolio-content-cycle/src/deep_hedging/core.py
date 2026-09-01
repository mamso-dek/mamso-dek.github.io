"""Simulation, stratégies classiques et mesures de risque."""

from __future__ import annotations

from dataclasses import dataclass
import math

import torch
from torch import Tensor


@dataclass(frozen=True)
class MarketConfig:
    s0: float = 100.0
    strike: float = 100.0
    maturity: float = 30 / 252
    rate: float = 0.0
    sigma: float = 0.20
    n_steps: int = 30

    @property
    def dt(self) -> float:
        return self.maturity / self.n_steps


@dataclass(frozen=True)
class HestonConfig:
    """Paramètres du scénario de volatilité stochastique."""

    s0: float = 100.0
    maturity: float = 30 / 252
    rate: float = 0.0
    v0: float = 0.04
    kappa: float = 3.0
    theta: float = 0.04
    vol_of_vol: float = 0.35
    rho: float = -0.70
    n_steps: int = 30
    substeps_per_step: int = 8

    @property
    def fine_steps(self) -> int:
        return self.n_steps * self.substeps_per_step

    @property
    def fine_dt(self) -> float:
        return self.maturity / self.fine_steps

    @property
    def feller_margin(self) -> float:
        return 2.0 * self.kappa * self.theta - self.vol_of_vol**2


def simulate_gbm(
    n_paths: int,
    config: MarketConfig,
    seed: int,
    *,
    device: str | torch.device = "cpu",
    dtype: torch.dtype = torch.float32,
) -> Tensor:
    """Simule des trajectoires GBM exactes sur la grille du protocole.

    Les chocs sont générés sur CPU avec un générateur local. Cette convention
    évite de faire dépendre la séparation train/test du générateur global ou du
    backend MPS, puis les trajectoires sont déplacées vers le périphérique visé.
    """

    if n_paths <= 0:
        raise ValueError("n_paths doit être strictement positif")
    if config.n_steps <= 0 or config.maturity <= 0 or config.sigma <= 0:
        raise ValueError("grille, maturité et volatilité doivent être positives")

    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed)
    shocks = torch.randn(
        (n_paths, config.n_steps), generator=generator, dtype=dtype, device="cpu"
    )
    drift = (config.rate - 0.5 * config.sigma**2) * config.dt
    diffusion = config.sigma * math.sqrt(config.dt) * shocks
    log_paths = torch.cumsum(drift + diffusion, dim=1)
    initial = torch.full((n_paths, 1), config.s0, dtype=dtype, device="cpu")
    paths = torch.cat((initial, config.s0 * torch.exp(log_paths)), dim=1)
    return paths.to(device)


def simulate_heston(
    n_paths: int,
    config: HestonConfig,
    seed: int,
    *,
    device: str | torch.device = "cpu",
    dtype: torch.dtype = torch.float32,
    variance_shocks: Tensor | None = None,
    independent_shocks: Tensor | None = None,
) -> tuple[Tensor, Tensor]:
    """Simule Heston par full truncation et log-Euler pour le spot.

    Les chocs optionnels permettent de coupler plusieurs discrétisations. Les
    variances retournées sont tronquées à zéro aux dates de couverture, tandis
    que l'état Euler brut est conservé entre deux sous-pas conformément au
    schéma de full truncation.
    """

    if n_paths <= 0:
        raise ValueError("n_paths doit être strictement positif")
    if (
        config.s0 <= 0
        or config.maturity <= 0
        or config.v0 < 0
        or config.kappa <= 0
        or config.theta < 0
        or config.vol_of_vol < 0
        or config.n_steps <= 0
        or config.substeps_per_step <= 0
        or not -1 <= config.rho <= 1
    ):
        raise ValueError("paramètres Heston invalides")

    expected_shape = (n_paths, config.fine_steps)
    if (variance_shocks is None) != (independent_shocks is None):
        raise ValueError("les deux matrices de chocs doivent être fournies")
    if variance_shocks is None:
        generator = torch.Generator(device="cpu")
        generator.manual_seed(seed)
        variance_shocks = torch.randn(
            expected_shape, generator=generator, dtype=dtype, device="cpu"
        )
        independent_shocks = torch.randn(
            expected_shape, generator=generator, dtype=dtype, device="cpu"
        )
    else:
        if (
            tuple(variance_shocks.shape) != expected_shape
            or tuple(independent_shocks.shape) != expected_shape
        ):
            raise ValueError("forme des chocs incompatible avec la grille fine")
        variance_shocks = variance_shocks.to(dtype=dtype, device="cpu")
        independent_shocks = independent_shocks.to(dtype=dtype, device="cpu")

    dt = config.fine_dt
    root_dt = math.sqrt(dt)
    orthogonal_weight = math.sqrt(max(0.0, 1.0 - config.rho**2))
    log_spot = torch.full(
        (n_paths,), math.log(config.s0), dtype=dtype, device="cpu"
    )
    variance = torch.full(
        (n_paths,), config.v0, dtype=dtype, device="cpu"
    )
    spot_paths = torch.empty(
        (n_paths, config.n_steps + 1), dtype=dtype, device="cpu"
    )
    variance_paths = torch.empty_like(spot_paths)
    spot_paths[:, 0] = config.s0
    variance_paths[:, 0] = config.v0

    decision_index = 1
    for fine_index in range(config.fine_steps):
        positive_variance = torch.clamp(variance, min=0.0)
        root_variance = torch.sqrt(positive_variance)
        variance_shock = variance_shocks[:, fine_index]
        spot_shock = (
            config.rho * variance_shock
            + orthogonal_weight * independent_shocks[:, fine_index]
        )
        log_spot = log_spot + (
            config.rate - 0.5 * positive_variance
        ) * dt + root_variance * root_dt * spot_shock
        variance = (
            variance
            + config.kappa * (config.theta - positive_variance) * dt
            + config.vol_of_vol * root_variance * root_dt * variance_shock
        )
        if (fine_index + 1) % config.substeps_per_step == 0:
            spot_paths[:, decision_index] = torch.exp(log_spot)
            variance_paths[:, decision_index] = torch.clamp(variance, min=0.0)
            decision_index += 1

    return spot_paths.to(device), variance_paths.to(device)


def black_scholes_call(
    spot: Tensor | float,
    strike: float,
    tau: Tensor | float,
    rate: float,
    sigma: float,
) -> Tensor:
    spot_tensor = torch.as_tensor(spot)
    tau_tensor = torch.as_tensor(tau, dtype=spot_tensor.dtype, device=spot_tensor.device)
    if torch.any(tau_tensor <= 0) or sigma <= 0 or strike <= 0:
        raise ValueError("tau, sigma et strike doivent être strictement positifs")
    root_tau = torch.sqrt(tau_tensor)
    d1 = (
        torch.log(spot_tensor / strike) + (rate + 0.5 * sigma**2) * tau_tensor
    ) / (sigma * root_tau)
    d2 = d1 - sigma * root_tau
    return spot_tensor * torch.special.ndtr(d1) - strike * torch.exp(
        -rate * tau_tensor
    ) * torch.special.ndtr(d2)


def black_scholes_delta_paths(
    paths: Tensor, config: MarketConfig, *, volatility: float | None = None
) -> Tensor:
    """Delta du call aux dates de décision, avant le dernier mouvement."""

    if paths.ndim != 2 or paths.shape[1] != config.n_steps + 1:
        raise ValueError("forme des trajectoires incompatible avec la grille")
    sigma = config.sigma if volatility is None else volatility
    if sigma <= 0:
        raise ValueError("la volatilité doit être positive")
    times = torch.arange(
        config.n_steps, dtype=paths.dtype, device=paths.device
    )
    tau = config.maturity - times * config.dt
    spots = paths[:, :-1]
    d1 = (
        torch.log(spots / config.strike)
        + (config.rate + 0.5 * sigma**2) * tau.unsqueeze(0)
    ) / (sigma * torch.sqrt(tau).unsqueeze(0))
    return torch.special.ndtr(d1)


def black_scholes_delta_paths_local_volatility(
    paths: Tensor,
    config: MarketConfig,
    volatility_paths: Tensor,
    *,
    volatility_floor: float = 1e-4,
) -> Tensor:
    """Proxy de delta Black–Scholes alimentée par une volatilité locale.

    Cette règle n'est pas la delta analytique de Heston. Elle sert de référence
    adaptative lorsque la variance instantanée simulée est observable.
    """

    expected_shape = paths[:, :-1].shape
    if paths.ndim != 2 or paths.shape[1] != config.n_steps + 1:
        raise ValueError("forme des trajectoires incompatible avec la grille")
    if volatility_paths.shape != expected_shape:
        raise ValueError("forme des volatilités incompatible avec la grille")
    if volatility_floor <= 0 or torch.any(volatility_paths < 0):
        raise ValueError("les volatilités et leur plancher doivent être positifs")
    sigma = torch.clamp(volatility_paths, min=volatility_floor)
    times = torch.arange(
        config.n_steps, dtype=paths.dtype, device=paths.device
    )
    tau = config.maturity - times * config.dt
    spots = paths[:, :-1]
    d1 = (
        torch.log(spots / config.strike)
        + (config.rate + 0.5 * sigma**2) * tau.unsqueeze(0)
    ) / (sigma * torch.sqrt(tau).unsqueeze(0))
    return torch.special.ndtr(d1)


def leland_volatility(config: MarketConfig, one_way_cost: float) -> float:
    """Volatilité de Leland sous la convention coût aller simple du projet."""

    if one_way_cost < 0:
        raise ValueError("le coût ne peut pas être négatif")
    round_trip_cost = 2.0 * one_way_cost
    leland_number = (
        math.sqrt(2.0 / math.pi)
        * round_trip_cost
        / (config.sigma * math.sqrt(config.dt))
    )
    return config.sigma * math.sqrt(1.0 + leland_number)


def strategy_pnl(
    paths: Tensor,
    positions: Tensor,
    premium: Tensor | float,
    one_way_cost: float,
    strike: float,
) -> tuple[Tensor, Tensor, Tensor]:
    """P&L terminal d'un vendeur de call et coûts par trajectoire.

    La position est détenue sur chaque intervalle. L'ouverture, les
    rééquilibrages et la liquidation terminale sont facturés.
    """

    if positions.shape != paths[:, :-1].shape:
        raise ValueError("positions et trajectoires ont des formes incompatibles")
    if one_way_cost < 0:
        raise ValueError("le coût ne peut pas être négatif")

    gains = torch.sum(positions * torch.diff(paths, dim=1), dim=1)
    previous = torch.cat((torch.zeros_like(positions[:, :1]), positions[:, :-1]), dim=1)
    trades = positions - previous
    entry_and_rehedge = torch.sum(torch.abs(trades) * paths[:, :-1], dim=1)
    liquidation = torch.abs(positions[:, -1]) * paths[:, -1]
    turnover = entry_and_rehedge + liquidation
    costs = one_way_cost * turnover
    payoff = torch.clamp(paths[:, -1] - strike, min=0.0)
    pnl = torch.as_tensor(premium, dtype=paths.dtype, device=paths.device) + gains - costs - payoff
    return pnl, costs, turnover


def rockafellar_uryasev_cvar(losses: Tensor, eta: Tensor, alpha: float) -> Tensor:
    """Objectif convexe de Rockafellar–Uryasev pour un seuil eta donné."""

    if not 0 < alpha < 1:
        raise ValueError("alpha doit appartenir à ]0, 1[")
    return eta + torch.mean(torch.relu(losses - eta)) / (1.0 - alpha)


def summarize_pnl(pnl: Tensor, costs: Tensor, turnover: Tensor, alpha: float = 0.95) -> dict[str, float]:
    """Métriques hors gradient utilisées pour les comparaisons."""

    with torch.no_grad():
        loss = -pnl
        var = torch.quantile(loss, alpha)
        tail = loss[loss >= var]
        return {
            "mean_pnl": float(torch.mean(pnl).cpu()),
            "std_pnl": float(torch.std(pnl, correction=1).cpu()),
            "loss_probability": float(torch.mean((pnl < 0).to(pnl.dtype)).cpu()),
            "var_loss_95": float(var.cpu()),
            "cvar_loss_95": float(torch.mean(tail).cpu()),
            "mean_transaction_cost": float(torch.mean(costs).cpu()),
            "mean_turnover_notional": float(torch.mean(turnover).cpu()),
        }
