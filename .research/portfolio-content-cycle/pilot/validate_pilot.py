"""Contrôles déterministes des résultats exploratoires du pilote."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PAYLOAD = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
CONFIG = PAYLOAD["configuration"]
RESULTS = PAYLOAD["results"]


def result(strategy: str, cost: float) -> dict[str, float]:
    return RESULTS[f"{strategy}__{cost:.4f}"]


def main() -> None:
    checks: list[tuple[str, bool]] = []
    premium = CONFIG["premium"]
    checks.append(("prime Black–Scholes du scénario", abs(premium - 2.7524171534) < 1e-9))

    unhedged = result("sans_couverture", 0.0)
    delta = result("delta", 0.0)
    standard_error = unhedged["std_pnl"] / np.sqrt(CONFIG["n_paths"])
    checks.append(
        ("P&L moyen sans couverture compatible avec zéro à 3 erreurs-types", abs(unhedged["mean_pnl"]) < 3 * standard_error)
    )
    checks.append(
        ("P&L moyen delta compatible avec zéro à 3 erreurs-types", abs(delta["mean_pnl"]) < 3 * delta["std_pnl"] / np.sqrt(CONFIG["n_paths"]))
    )
    checks.append(("écart-type delta inférieur à 20 % du non-couvert", delta["std_pnl"] < 0.20 * unhedged["std_pnl"]))
    checks.append(("CVaR delta inférieure à 20 % du non-couvert", delta["cvar_loss_95"] < 0.20 * unhedged["cvar_loss_95"]))

    costs = (0.0, 0.0010, 0.0025, 0.0050)
    delta_cvars = [result("delta", cost)["cvar_loss_95"] for cost in costs]
    checks.append(("CVaR delta strictement croissante avec le coût", all(a < b for a, b in zip(delta_cvars, delta_cvars[1:]))))

    for cost in costs[1:]:
        row = result("delta", cost)
        checks.append(
            (
                f"identité coût-turnover à {cost * 10_000:.0f} pb",
                abs(row["mean_transaction_cost"] - cost * row["mean_turnover_notional"]) < 1e-12,
            )
        )
        checks.append(
            (
                f"non-couvert invariant à {cost * 10_000:.0f} pb",
                result("sans_couverture", cost) == unhedged,
            )
        )

    failed = [name for name, ok in checks if not ok]
    lines = [f"{'OK' if ok else 'ÉCHEC'} — {name}" for name, ok in checks]
    (HERE / "validation.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    if failed:
        raise SystemExit(f"{len(failed)} contrôle(s) en échec")


if __name__ == "__main__":
    main()
