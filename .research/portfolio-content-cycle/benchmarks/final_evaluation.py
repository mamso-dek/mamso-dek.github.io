"""Évaluation confirmatoire, volontairement verrouillée, du modèle gelé."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any

import numpy as np
import torch


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]
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
from deep_hedging.train import initial_premium  # noqa: E402


FINAL_SEED = 20269000
FINAL_SIZE = 250_000
BOOTSTRAP_REPLICATES = 5_000
CONFIRMATION_PHRASE = "OPEN-20269000-250000-FROZEN"
CHECKPOINT = ROOT / "checkpoints" / "convergence-2000.pt"
EXPECTED_CHECKPOINT_SHA256 = (
    "d47f58cf3df225148688c74349cee8988e2750c7067be4f4d7dd9f3d4b6ccd8a"
)
OUTPUT = Path(__file__).with_name("final-test-results.json")
OPENING_MARKER = Path(__file__).with_name("final-test-opening.json")
BOOTSTRAP_SEEDS = {
    "cvar_neural_versus_leland": 20269101,
    "cvar_neural_versus_delta": 20269102,
    "cost_neural_versus_leland": 20269103,
    "turnover_neural_versus_leland": 20269104,
    "cost_neural_versus_delta": 20269105,
    "turnover_neural_versus_delta": 20269106,
}
EXPECTED_MARKET = {
    "s0": 100.0,
    "strike": 100.0,
    "maturity": 30 / 252,
    "rate": 0.0,
    "sigma": 0.20,
    "n_steps": 30,
}
EXPECTED_TRAINING = {
    "epochs": 2_000,
    "batch_size": 8_192,
    "validation_size": 50_000,
    "learning_rate": 1e-3,
    "eta_learning_rate": 5e-3,
    "alpha": 0.95,
    "one_way_cost": 0.0025,
    "model_seed": 20260911,
    "train_seed": 20261000,
    "validation_seed": 20262000,
    "gradient_clip": 5.0,
}
EXPECTED_STATE_SHAPES = {
    "network.0.weight": (32, 3),
    "network.0.bias": (32,),
    "network.2.weight": (32, 32),
    "network.2.bias": (32,),
    "network.4.weight": (1, 32),
    "network.4.bias": (1,),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audite le protocole gelé par défaut. L'ouverture finale exige "
            "deux confirmations explicites."
        )
    )
    parser.add_argument("--open-final-test", action="store_true")
    parser.add_argument("--confirmation", default="")
    return parser.parse_args()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json_atomic(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def git_output(*arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPOSITORY), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def validate_authorization(open_final_test: bool, confirmation: str) -> None:
    if not open_final_test:
        if confirmation:
            raise ValueError(
                "une confirmation seule ne peut pas ouvrir le test final"
            )
        return
    if confirmation != CONFIRMATION_PHRASE:
        raise ValueError("phrase de confirmation finale incorrecte")


def checkpoint_audit() -> tuple[dict[str, Any] | None, list[str]]:
    issues: list[str] = []
    if not CHECKPOINT.exists():
        return None, [f"checkpoint absent : {CHECKPOINT}"]
    observed_hash = file_sha256(CHECKPOINT)
    if observed_hash != EXPECTED_CHECKPOINT_SHA256:
        issues.append("empreinte SHA-256 du checkpoint différente du gel")
    checkpoint = torch.load(CHECKPOINT, map_location="cpu", weights_only=True)
    if checkpoint.get("market") != EXPECTED_MARKET:
        issues.append("configuration de marché du checkpoint différente du gel")
    if checkpoint.get("training") != EXPECTED_TRAINING:
        issues.append("configuration d'entraînement différente du gel")
    if checkpoint.get("best_epoch") != 2_000:
        issues.append("le checkpoint ne correspond pas à l'époque gelée")
    state = checkpoint.get("policy_state_dict", {})
    shapes = {name: tuple(value.shape) for name, value in state.items()}
    if shapes != EXPECTED_STATE_SHAPES:
        issues.append("architecture du checkpoint différente du gel")
    return checkpoint, issues


def prior_final_use_issues() -> list[str]:
    issues: list[str] = []
    for path in sorted((ROOT / "benchmarks").glob("*.json")):
        if path in {OUTPUT, OPENING_MARKER}:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            issues.append(f"artefact JSON illisible : {path.name}")
            continue
        if isinstance(payload, dict) and payload.get("final_test_used") is True:
            issues.append(f"utilisation finale déjà déclarée : {path.name}")
    if OUTPUT.exists():
        issues.append(f"résultat final déjà présent : {OUTPUT.name}")
    if OPENING_MARKER.exists():
        issues.append(f"marqueur d'ouverture déjà présent : {OPENING_MARKER.name}")
    return issues


def audit() -> tuple[dict[str, Any] | None, dict[str, Any]]:
    checkpoint, issues = checkpoint_audit()
    issues.extend(prior_final_use_issues())
    try:
        commit = git_output("rev-parse", "HEAD")
        status = git_output("status", "--porcelain")
    except subprocess.CalledProcessError as error:
        commit = "indisponible"
        status = "indisponible"
        issues.append(f"audit Git impossible : {error}")
    if status:
        issues.append("le dépôt contient des changements non enregistrés")
    report = {
        "ready_for_single_opening": not issues,
        "issues": issues,
        "repository_commit": commit,
        "repository_clean": not bool(status),
        "checkpoint": str(CHECKPOINT.relative_to(ROOT)),
        "checkpoint_sha256_expected": EXPECTED_CHECKPOINT_SHA256,
        "checkpoint_sha256_observed": (
            file_sha256(CHECKPOINT) if CHECKPOINT.exists() else None
        ),
        "final_seed_reserved": FINAL_SEED,
        "final_size_reserved": FINAL_SIZE,
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "bootstrap_seeds": BOOTSTRAP_SEEDS,
        "output_absent": not OUTPUT.exists(),
        "opening_marker_absent": not OPENING_MARKER.exists(),
    }
    return checkpoint, report


def loss_quantiles(pnl: torch.Tensor) -> dict[str, float]:
    probabilities = torch.tensor(
        [0.01, 0.05, 0.50, 0.95, 0.99, 0.995], dtype=pnl.dtype
    )
    values = torch.quantile(-pnl, probabilities)
    names = ["q01", "q05", "q50", "q95", "q99", "q995"]
    return {name: float(value) for name, value in zip(names, values, strict=True)}


def strategy_summary(
    pnl: torch.Tensor, costs: torch.Tensor, turnover: torch.Tensor
) -> dict[str, Any]:
    return {
        **summarize_pnl(pnl, costs, turnover, alpha=0.95),
        "loss_quantiles": loss_quantiles(pnl),
    }


def evaluate_strategies(
    checkpoint: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, np.ndarray]]]:
    market = MarketConfig(**EXPECTED_MARKET)
    one_way_cost = float(EXPECTED_TRAINING["one_way_cost"])
    premium = initial_premium(market)
    paths = simulate_gbm(FINAL_SIZE, market, FINAL_SEED, device="cpu")
    policy = HedgingPolicy(
        hidden_size=32,
        max_position=1.25,
        include_inventory=True,
    )
    policy.load_state_dict(checkpoint["policy_state_dict"], strict=True)
    policy.eval()

    summaries: dict[str, dict[str, Any]] = {}
    arrays: dict[str, dict[str, np.ndarray]] = {}
    with torch.no_grad():
        position_builders = (
            ("unhedged", lambda: torch.zeros_like(paths[:, :-1])),
            (
                "black_scholes_delta",
                lambda: black_scholes_delta_paths(paths, market),
            ),
            (
                "leland_delta",
                lambda: black_scholes_delta_paths(
                    paths,
                    market,
                    volatility=leland_volatility(market, one_way_cost),
                ),
            ),
            ("neural_policy", lambda: policy(paths, market)),
        )
        for name, build_positions in position_builders:
            positions = build_positions()
            pnl, costs, turnover = strategy_pnl(
                paths,
                positions,
                premium,
                one_way_cost,
                market.strike,
            )
            summaries[name] = strategy_summary(pnl, costs, turnover)
            arrays[name] = {
                "losses": (-pnl).numpy(),
                "costs": costs.numpy(),
                "turnover": turnover.numpy(),
            }
            del positions, pnl, costs, turnover
    return summaries, arrays


def paired_comparisons(
    arrays: dict[str, dict[str, np.ndarray]],
) -> dict[str, dict[str, float | int]]:
    neural = arrays["neural_policy"]
    leland = arrays["leland_delta"]
    delta = arrays["black_scholes_delta"]
    return {
        "cvar_neural_versus_leland": paired_cvar_improvement_bootstrap(
            leland["losses"],
            neural["losses"],
            n_bootstrap=BOOTSTRAP_REPLICATES,
            seed=BOOTSTRAP_SEEDS["cvar_neural_versus_leland"],
        ),
        "cvar_neural_versus_delta": paired_cvar_improvement_bootstrap(
            delta["losses"],
            neural["losses"],
            n_bootstrap=BOOTSTRAP_REPLICATES,
            seed=BOOTSTRAP_SEEDS["cvar_neural_versus_delta"],
        ),
        "cost_neural_versus_leland": paired_mean_improvement_bootstrap(
            leland["costs"],
            neural["costs"],
            n_bootstrap=BOOTSTRAP_REPLICATES,
            seed=BOOTSTRAP_SEEDS["cost_neural_versus_leland"],
        ),
        "turnover_neural_versus_leland": paired_mean_improvement_bootstrap(
            leland["turnover"],
            neural["turnover"],
            n_bootstrap=BOOTSTRAP_REPLICATES,
            seed=BOOTSTRAP_SEEDS["turnover_neural_versus_leland"],
        ),
        "cost_neural_versus_delta": paired_mean_improvement_bootstrap(
            delta["costs"],
            neural["costs"],
            n_bootstrap=BOOTSTRAP_REPLICATES,
            seed=BOOTSTRAP_SEEDS["cost_neural_versus_delta"],
        ),
        "turnover_neural_versus_delta": paired_mean_improvement_bootstrap(
            delta["turnover"],
            neural["turnover"],
            n_bootstrap=BOOTSTRAP_REPLICATES,
            seed=BOOTSTRAP_SEEDS["turnover_neural_versus_delta"],
        ),
    }


def open_final_test(checkpoint: dict[str, Any], audit_report: dict[str, Any]) -> None:
    started = datetime.now(timezone.utc)
    opening = {
        "status": "started",
        "started_at_utc": started.isoformat(),
        "final_seed": FINAL_SEED,
        "final_size": FINAL_SIZE,
        "repository_commit": audit_report["repository_commit"],
        "checkpoint_sha256": EXPECTED_CHECKPOINT_SHA256,
    }
    with OPENING_MARKER.open("x", encoding="utf-8") as stream:
        json.dump(opening, stream, indent=2, ensure_ascii=False)
        stream.write("\n")

    start_clock = time.perf_counter()
    summaries, arrays = evaluate_strategies(checkpoint)
    comparisons = paired_comparisons(arrays)
    primary = comparisons["cvar_neural_versus_leland"]
    finished = datetime.now(timezone.utc)
    result = {
        "status": "final test executed once",
        "final_test_used": True,
        "started_at_utc": started.isoformat(),
        "finished_at_utc": finished.isoformat(),
        "elapsed_seconds": time.perf_counter() - start_clock,
        "repository_commit": audit_report["repository_commit"],
        "checkpoint_sha256": EXPECTED_CHECKPOINT_SHA256,
        "script_sha256": file_sha256(Path(__file__)),
        "software": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "torch": torch.__version__,
            "numpy": np.__version__,
            "device": "cpu",
        },
        "market": EXPECTED_MARKET,
        "evaluation": {
            "seed": FINAL_SEED,
            "size": FINAL_SIZE,
            "alpha": 0.95,
            "one_way_cost": EXPECTED_TRAINING["one_way_cost"],
            "bootstrap_replicates": BOOTSTRAP_REPLICATES,
            "bootstrap_seeds": BOOTSTRAP_SEEDS,
        },
        "strategy_metrics": summaries,
        "paired_comparisons": comparisons,
        "confirmatory_decision": {
            "criterion": (
                "borne inférieure de l'IC bootstrap bilatéral à 95 % de "
                "CVaR(Leland) - CVaR(réseau) strictement positive"
            ),
            "favorable": float(primary["ci_lower"]) > 0.0,
        },
    }
    write_json_atomic(OUTPUT, result)
    opening.update(
        {
            "status": "completed",
            "finished_at_utc": finished.isoformat(),
            "output": OUTPUT.name,
            "output_sha256": file_sha256(OUTPUT),
        }
    )
    write_json_atomic(OPENING_MARKER, opening)
    print(json.dumps(result["confirmatory_decision"], ensure_ascii=False))
    print(f"Résultats enregistrés dans {OUTPUT}")


def main() -> None:
    args = parse_args()
    validate_authorization(args.open_final_test, args.confirmation)
    torch.use_deterministic_algorithms(True)
    checkpoint, report = audit()
    if not args.open_final_test:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        raise SystemExit(0 if report["ready_for_single_opening"] else 1)
    if not report["ready_for_single_opening"] or checkpoint is None:
        raise RuntimeError(
            "audit final refusé : " + "; ".join(report["issues"])
        )
    open_final_test(checkpoint, report)


if __name__ == "__main__":
    main()
