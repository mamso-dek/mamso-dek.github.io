"""Politique neuronale compacte et partagée dans le temps."""

from __future__ import annotations

import math

import torch
from torch import Tensor, nn

from .core import MarketConfig


class HedgingPolicy(nn.Module):
    """Politique markovienne avec inventaire précédent configurable.

    Le même réseau est appliqué à toutes les dates. La sortie est bornée entre
    zéro et ``max_position`` : le vendeur du call ne peut donc pas transformer
    l'optimisation de couverture en prise de position directionnelle extrême.
    """

    def __init__(
        self,
        hidden_size: int = 32,
        max_position: float = 1.25,
        initial_position: float = 0.50,
        include_inventory: bool = True,
    ) -> None:
        super().__init__()
        if hidden_size <= 0 or not 0 < initial_position < max_position:
            raise ValueError("taille cachée et bornes de position invalides")
        self.max_position = float(max_position)
        self.include_inventory = bool(include_inventory)
        input_size = 3 if self.include_inventory else 2
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.SiLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.SiLU(),
            nn.Linear(hidden_size, 1),
        )
        final_layer = self.network[-1]
        assert isinstance(final_layer, nn.Linear)
        nn.init.zeros_(final_layer.weight)
        ratio = initial_position / max_position
        nn.init.constant_(final_layer.bias, math.log(ratio / (1.0 - ratio)))

    def action(self, state: Tensor) -> Tensor:
        return self.max_position * torch.sigmoid(self.network(state)).squeeze(-1)

    def forward(self, paths: Tensor, config: MarketConfig) -> Tensor:
        if paths.ndim != 2 or paths.shape[1] != config.n_steps + 1:
            raise ValueError("forme des trajectoires incompatible avec la grille")
        previous = torch.zeros(paths.shape[0], dtype=paths.dtype, device=paths.device)
        positions: list[Tensor] = []
        scale = config.sigma * math.sqrt(config.maturity)
        for step in range(config.n_steps):
            tau = config.maturity - step * config.dt
            log_moneyness = torch.log(paths[:, step] / config.strike) / scale
            time_remaining = torch.full_like(log_moneyness, tau / config.maturity)
            if self.include_inventory:
                inventory = previous / self.max_position
                state = torch.stack(
                    (log_moneyness, time_remaining, inventory), dim=1
                )
            else:
                state = torch.stack((log_moneyness, time_remaining), dim=1)
            previous = self.action(state)
            positions.append(previous)
        return torch.stack(positions, dim=1)
