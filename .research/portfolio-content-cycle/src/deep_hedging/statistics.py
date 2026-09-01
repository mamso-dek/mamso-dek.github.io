"""Outils d'incertitude pour les comparaisons de risque hors échantillon."""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray


def _tail_size(sample_size: int, alpha: float) -> int:
    raw_size = (1.0 - alpha) * sample_size
    nearest_integer = round(raw_size)
    if math.isclose(raw_size, nearest_integer, rel_tol=0.0, abs_tol=1e-9):
        return max(1, int(nearest_integer))
    return max(1, math.ceil(raw_size))


def empirical_cvar(losses: NDArray[np.floating], alpha: float = 0.95) -> float:
    """Moyenne des plus grandes pertes dans la masse de queue 1 - alpha."""

    values = np.asarray(losses, dtype=np.float64)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("losses doit être un vecteur non vide")
    if not np.all(np.isfinite(values)):
        raise ValueError("losses contient une valeur non finie")
    if not 0 < alpha < 1:
        raise ValueError("alpha doit appartenir à ]0, 1[")
    tail_size = _tail_size(values.size, alpha)
    tail = np.partition(values, values.size - tail_size)[-tail_size:]
    return float(np.mean(tail))


def paired_cvar_improvement_bootstrap(
    reference_losses: NDArray[np.floating],
    candidate_losses: NDArray[np.floating],
    *,
    alpha: float = 0.95,
    n_bootstrap: int = 2_000,
    confidence: float = 0.95,
    seed: int = 20264000,
) -> dict[str, float | int]:
    """Bootstrap apparié de CVaR(référence) moins CVaR(candidate).

    Les mêmes indices sont utilisés pour les deux stratégies à chaque tirage.
    Une amélioration positive favorise donc la stratégie candidate.
    """

    reference = np.asarray(reference_losses, dtype=np.float64)
    candidate = np.asarray(candidate_losses, dtype=np.float64)
    if (
        reference.ndim != 1
        or candidate.ndim != 1
        or reference.shape != candidate.shape
        or reference.size == 0
    ):
        raise ValueError("les pertes doivent être deux vecteurs de même taille")
    if not np.all(np.isfinite(reference)) or not np.all(np.isfinite(candidate)):
        raise ValueError("les pertes contiennent une valeur non finie")
    if n_bootstrap <= 1:
        raise ValueError("n_bootstrap doit être supérieur à un")
    if not 0 < confidence < 1:
        raise ValueError("confidence doit appartenir à ]0, 1[")

    point = empirical_cvar(reference, alpha) - empirical_cvar(candidate, alpha)
    rng = np.random.default_rng(seed)
    improvements = np.empty(n_bootstrap, dtype=np.float64)
    for replicate in range(n_bootstrap):
        indices = rng.integers(0, reference.size, size=reference.size)
        improvements[replicate] = empirical_cvar(
            reference[indices], alpha
        ) - empirical_cvar(candidate[indices], alpha)

    lower_probability = (1.0 - confidence) / 2.0
    lower, upper = np.quantile(
        improvements, [lower_probability, 1.0 - lower_probability]
    )
    return {
        "point_improvement": point,
        "reference_cvar": empirical_cvar(reference, alpha),
        "candidate_cvar": empirical_cvar(candidate, alpha),
        "bootstrap_mean": float(np.mean(improvements)),
        "bootstrap_standard_error": float(np.std(improvements, ddof=1)),
        "confidence": confidence,
        "ci_lower": float(lower),
        "ci_upper": float(upper),
        "probability_improvement_positive": float(np.mean(improvements > 0)),
        "n_bootstrap": n_bootstrap,
        "bootstrap_seed": seed,
        "sample_size": int(reference.size),
        "tail_size": _tail_size(reference.size, alpha),
        "alpha": alpha,
    }
