"""Construit les figures du rapport depuis les artefacts JSON figés."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = ROOT / "benchmarks"
OUTPUT = Path(__file__).with_name("generated")

INK = "#191a21"
MUTED = "#5d616b"
FAINT = "#8a8e97"
GRID = "#dedfe3"
ACCENT = "#a83246"
ACCENT_LIGHT = "#ead1d7"
BLUE = "#416b85"
BLUE_LIGHT = "#d5e2ea"
WHITE = "#ffffff"

SOURCE_FILES = {
    "final": BENCHMARKS / "final-test-results.json",
    "cost": BENCHMARKS / "cost-sensitivity.json",
    "volatility": BENCHMARKS / "frequency-volatility.json",
    "heston": BENCHMARKS / "heston-parameter-sensitivity.json",
    "ablations": BENCHMARKS / "model-ablations.json",
}

ALT_TEXTS = {
    "final-strategy-comparison": (
        "Deux barres comparatives montrent que la politique neuronale a la "
        "CVaR et le turnover les plus faibles parmi les trois couvertures."
    ),
    "final-tail-quantiles": (
        "Graphique à points des quantiles 95, 99 et 99,5 pour cent : les "
        "pertes de queue de la politique neuronale restent sous celles des "
        "deltas Black-Scholes et Leland."
    ),
    "development-cost-sensitivity": (
        "Deux courbes de développement selon le coût de transaction montrent "
        "une CVaR croissante mais un turnover décroissant, avec des valeurs "
        "neuronales inférieures à Leland aux quatre coûts."
    ),
    "development-robustness": (
        "Intervalles de confiance des améliorations de CVaR : l'avantage "
        "neuronal change de signe selon la volatilité GBM et devient négatif "
        "dans un scénario Heston à forte volatilité de variance sans levier."
    ),
    "development-ablations": (
        "Intervalles de confiance des effets d'ablation : retirer l'inventaire "
        "dégrade CVaR et turnover, tandis qu'un réseau plus grand apporte un "
        "petit gain de CVaR au modèle alternatif."
    ),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_svg(path: Path) -> None:
    """Retire les espaces de fin de ligne ajoutés par le backend SVG."""

    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text(
        "\n".join(line.rstrip() for line in lines) + "\n",
        encoding="utf-8",
    )


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "axes.edgecolor": GRID,
            "axes.labelcolor": MUTED,
            "axes.facecolor": WHITE,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "figure.facecolor": WHITE,
            "text.color": INK,
            "legend.frameon": False,
            "savefig.facecolor": WHITE,
            "svg.hashsalt": "portfolio-deep-hedging-v1",
        }
    )


def finish_axis(axis: Axes, *, grid_axis: str = "x") -> None:
    axis.grid(axis=grid_axis, color=GRID, linewidth=0.7, alpha=0.75)
    axis.set_axisbelow(True)
    axis.spines["left"].set_color(GRID)
    axis.spines["bottom"].set_color(GRID)


def panel_label(axis: Axes, label: str) -> None:
    axis.text(
        -0.08,
        1.08,
        label,
        transform=axis.transAxes,
        fontsize=11,
        fontweight="bold",
        color=INK,
    )


def save_figure(figure: Figure, name: str) -> list[Path]:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    figure.subplots_adjust(bottom=0.19, top=0.78, left=0.10, right=0.97, wspace=0.35)
    figure.text(
        0.01,
        0.02,
        "Source : simulations internes documentées ; le test final n'est pas recalculé.",
        fontsize=8,
        color=FAINT,
    )
    paths = [OUTPUT / f"{name}.png", OUTPUT / f"{name}.svg"]
    figure.savefig(
        paths[0],
        dpi=200,
        bbox_inches="tight",
        metadata={"Software": "Matplotlib", "Description": ALT_TEXTS[name]},
    )
    figure.savefig(
        paths[1],
        bbox_inches="tight",
        metadata={"Creator": "Matplotlib", "Date": None, "Description": ALT_TEXTS[name]},
    )
    normalize_svg(paths[1])
    plt.close(figure)
    return paths


def final_strategy_comparison(data: dict[str, Any]) -> list[Path]:
    names = ["black_scholes_delta", "leland_delta", "neural_policy"]
    labels = ["Delta Black-Scholes", "Delta de Leland", "Politique neuronale"]
    colors = [FAINT, BLUE, ACCENT]
    metrics = data["strategy_metrics"]
    cvars = [metrics[name]["cvar_loss_95"] for name in names]
    turnovers = [metrics[name]["mean_turnover_notional"] for name in names]
    figure, axes = plt.subplots(1, 2, figsize=(11.8, 5.2))
    figure.suptitle("Comparaison finale des stratégies de couverture", x=0.10, ha="left", fontsize=17, fontweight="bold")
    figure.text(
        0.10,
        0.88,
        "250 000 trajectoires GBM communes · coût aller simple 25 pb · test final unique",
        color=MUTED,
        fontsize=10,
    )
    for axis, values, title, xlabel, maximum in (
        (axes[0], cvars, "Risque de queue", "CVaR de la perte à 95 %", 2.10),
        (axes[1], turnovers, "Activité de couverture", "Turnover notionnel moyen", 300.0),
    ):
        y = np.arange(len(labels))
        bars = axis.barh(y, values, color=colors, height=0.58)
        axis.set_yticks(y, labels)
        axis.invert_yaxis()
        axis.set_xlim(0, maximum)
        axis.set_xlabel(xlabel)
        axis.set_title(title, loc="left")
        finish_axis(axis)
        for index, (bar, value) in enumerate(zip(bars, values, strict=True)):
            axis.text(
                value - maximum * 0.018,
                bar.get_y() + bar.get_height() / 2,
                f"{value:.2f}" if maximum > 10 else f"{value:.3f}",
                va="center",
                ha="right",
                fontsize=9,
                color=WHITE,
                fontweight="bold" if index == 2 else "normal",
            )
    panel_label(axes[0], "A")
    panel_label(axes[1], "B")
    axes[0].text(
        0.0,
        -0.25,
        "Sans couverture : CVaR = 12,31 (hors échelle).",
        transform=axes[0].transAxes,
        fontsize=8.5,
        color=MUTED,
    )
    return save_figure(figure, "final-strategy-comparison")


def final_tail_quantiles(data: dict[str, Any]) -> list[Path]:
    metrics = data["strategy_metrics"]
    strategies = (
        ("black_scholes_delta", "Delta Black-Scholes", FAINT, "s"),
        ("leland_delta", "Delta de Leland", BLUE, "^"),
        ("neural_policy", "Politique neuronale", ACCENT, "o"),
    )
    quantiles = ("q95", "q99", "q995")
    labels = ("95 %", "99 %", "99,5 %")
    offsets = (0.18, 0.0, -0.18)
    figure, axis = plt.subplots(figsize=(10.8, 5.5))
    figure.suptitle("Quantiles élevés de la perte finale", x=0.10, ha="left", fontsize=17, fontweight="bold")
    figure.text(
        0.10,
        0.88,
        "Axe horizontal focalisé · une valeur plus faible indique une queue de perte plus courte",
        color=MUTED,
        fontsize=10,
    )
    y = np.arange(len(quantiles))
    for (name, label, color, marker), offset in zip(strategies, offsets, strict=True):
        values = [metrics[name]["loss_quantiles"][quantile] for quantile in quantiles]
        axis.scatter(
            values,
            y + offset,
            s=66,
            marker=marker,
            color=color if name != "leland_delta" else WHITE,
            edgecolor=color,
            linewidth=1.5,
            label=label,
            zorder=3,
        )
        for value, vertical in zip(values, y + offset, strict=True):
            axis.text(value + 0.025, vertical, f"{value:.2f}", va="center", fontsize=8, color=color)
    axis.set_yticks(y, labels)
    axis.invert_yaxis()
    axis.set_xlim(1.25, 2.50)
    axis.set_xlabel("Quantile de la perte")
    axis.set_ylabel("Niveau du quantile")
    axis.legend(ncol=3, loc="upper left", bbox_to_anchor=(0.0, 1.16))
    finish_axis(axis)
    figure.subplots_adjust(bottom=0.17, top=0.74, left=0.12, right=0.97)
    figure.text(
        0.01,
        0.02,
        "Source : test final préenregistré, 250 000 trajectoires communes.",
        fontsize=8,
        color=FAINT,
    )
    paths = [OUTPUT / "final-tail-quantiles.png", OUTPUT / "final-tail-quantiles.svg"]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    figure.savefig(paths[0], dpi=200, bbox_inches="tight", metadata={"Description": ALT_TEXTS["final-tail-quantiles"]})
    figure.savefig(paths[1], bbox_inches="tight", metadata={"Creator": "Matplotlib", "Date": None, "Description": ALT_TEXTS["final-tail-quantiles"]})
    normalize_svg(paths[1])
    plt.close(figure)
    return paths


def development_cost_sensitivity(data: dict[str, Any]) -> list[Path]:
    scenarios = data["scenarios"]
    costs = [scenario["basis_points"] for scenario in scenarios]
    neural_cvar = [scenario["development_metrics"]["neural"]["cvar_loss_95"] for scenario in scenarios]
    leland_cvar = [scenario["development_metrics"]["delta_leland"]["cvar_loss_95"] for scenario in scenarios]
    neural_turnover = [scenario["development_metrics"]["neural"]["mean_turnover_notional"] for scenario in scenarios]
    leland_turnover = [scenario["development_metrics"]["delta_leland"]["mean_turnover_notional"] for scenario in scenarios]
    figure, axes = plt.subplots(1, 2, figsize=(11.8, 5.2))
    figure.suptitle("Sensibilité au coût de transaction", x=0.10, ha="left", fontsize=17, fontweight="bold")
    figure.text(
        0.10,
        0.88,
        "Développement · 100 000 trajectoires communes par coût · axes verticaux focalisés",
        color=MUTED,
        fontsize=10,
    )
    for axis, neural, leland, title, ylabel in (
        (axes[0], neural_cvar, leland_cvar, "Risque de queue", "CVaR de la perte à 95 %"),
        (axes[1], neural_turnover, leland_turnover, "Activité de couverture", "Turnover notionnel moyen"),
    ):
        axis.plot(costs, leland, color=BLUE, marker="^", markerfacecolor=WHITE, linewidth=1.8, label="Delta de Leland")
        axis.plot(costs, neural, color=ACCENT, marker="o", linewidth=2.2, label="Politique neuronale")
        axis.set_xticks(costs)
        axis.set_xlabel("Coût aller simple (points de base)")
        axis.set_ylabel(ylabel)
        axis.set_title(title, loc="left")
        finish_axis(axis, grid_axis="y")
    axes[0].legend(loc="upper left")
    panel_label(axes[0], "A")
    panel_label(axes[1], "B")
    return save_figure(figure, "development-cost-sensitivity")


def interval_panel(
    axis: Axes,
    labels: list[str],
    points: list[float],
    lowers: list[float],
    uppers: list[float],
    title: str,
) -> None:
    y = np.arange(len(labels))
    axis.axvline(0, color=INK, linewidth=1.0)
    for index, (point, lower, upper) in enumerate(zip(points, lowers, uppers, strict=True)):
        crosses_zero = lower <= 0 <= upper
        color = ACCENT if point >= 0 else BLUE
        axis.errorbar(
            point,
            index,
            xerr=np.array([[point - lower], [upper - point]]),
            fmt="o",
            color=color,
            markerfacecolor=WHITE if crosses_zero else color,
            markeredgewidth=1.5,
            capsize=3,
            linewidth=1.4,
            zorder=3,
        )
    axis.set_yticks(y, labels)
    axis.invert_yaxis()
    axis.set_title(title, loc="left")
    axis.set_xlabel("Amélioration de CVaR face à la référence")
    axis.margins(x=0.12)
    finish_axis(axis)


def development_robustness(volatility: dict[str, Any], heston: dict[str, Any]) -> list[Path]:
    volatility_scenarios = volatility["volatility_experiment"]["scenarios"]
    vol_labels = [f"σ = {100 * scenario['scenario_sigma']:.0f} %" for scenario in volatility_scenarios]
    vol_bootstrap = [scenario["paired_bootstrap_neural_versus_informed_leland"] for scenario in volatility_scenarios]
    heston_labels = [
        f"ξ = {scenario['parameters']['vol_of_vol']:.2f}, ρ = {scenario['parameters']['rho']:.2f}"
        for scenario in heston["scenarios"]
    ]
    heston_bootstrap = [
        scenario["paired_bootstrap"]["neural_versus_leland_instantaneous_variance_proxy"]
        for scenario in heston["scenarios"]
    ]
    figure, axes = plt.subplots(1, 2, figsize=(12.8, 5.8))
    figure.suptitle("Robustesse de la politique gelée", x=0.08, ha="left", fontsize=17, fontweight="bold")
    figure.text(
        0.08,
        0.88,
        "Développement · point et IC bootstrap à 95 % · positif = avantage neuronal",
        color=MUTED,
        fontsize=10,
    )
    interval_panel(
        axes[0],
        vol_labels,
        [item["point_improvement"] for item in vol_bootstrap],
        [item["ci_lower"] for item in vol_bootstrap],
        [item["ci_upper"] for item in vol_bootstrap],
        "GBM : Leland informé de σ",
    )
    interval_panel(
        axes[1],
        heston_labels,
        [item["point_improvement"] for item in heston_bootstrap],
        [item["ci_lower"] for item in heston_bootstrap],
        [item["ci_upper"] for item in heston_bootstrap],
        "Heston : proxy informé de la variance",
    )
    panel_label(axes[0], "A")
    panel_label(axes[1], "B")
    return save_figure(figure, "development-robustness")


def development_ablations(data: dict[str, Any]) -> list[Path]:
    variants = [variant for variant in data["variants"] if variant["name"] != "central_inventory_h32"]
    labels = ["Sans inventaire, h=32", "Inventaire, h=16", "Inventaire, h=64"]
    cvar = [variant["central_improvement_over_variant"] for variant in variants]
    turnover = [variant["central_turnover_reduction_over_variant"] for variant in variants]
    figure, axes = plt.subplots(1, 2, figsize=(12.2, 5.4))
    figure.suptitle("Effets des ablations du réseau", x=0.09, ha="left", fontsize=17, fontweight="bold")
    figure.text(
        0.09,
        0.88,
        "Développement · point et IC bootstrap à 95 % · positif = avantage du modèle central",
        color=MUTED,
        fontsize=10,
    )
    interval_panel(
        axes[0],
        labels,
        [item["point_improvement"] for item in cvar],
        [item["ci_lower"] for item in cvar],
        [item["ci_upper"] for item in cvar],
        "Amélioration de CVaR du modèle central",
    )
    interval_panel(
        axes[1],
        labels,
        [item["point_improvement"] for item in turnover],
        [item["ci_lower"] for item in turnover],
        [item["ci_upper"] for item in turnover],
        "Réduction de turnover du modèle central",
    )
    axes[1].set_xlabel("Réduction moyenne de turnover")
    for axis, intervals, decimals in ((axes[0], cvar, 3), (axes[1], turnover, 2)):
        for index, interval in enumerate(intervals):
            point = interval["point_improvement"]
            positive = point >= 0
            anchor = interval["ci_upper"] if positive else interval["ci_lower"]
            axis.annotate(
                f"{point:+.{decimals}f}",
                (anchor, index),
                xytext=(7 if positive else -7, 0),
                textcoords="offset points",
                ha="left" if positive else "right",
                va="center",
                fontsize=8,
                color=MUTED,
            )
    panel_label(axes[0], "A")
    panel_label(axes[1], "B")
    return save_figure(figure, "development-ablations")


def write_manifest(outputs: list[Path]) -> None:
    manifest = {
        "status": "figures generated from preserved JSON artifacts",
        "source_hashes": {name: sha256(path) for name, path in SOURCE_FILES.items()},
        "figures": [
            {
                "file": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
                "alt_text": ALT_TEXTS[path.stem],
            }
            for path in outputs
        ],
    }
    (OUTPUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    configure_style()
    data = {name: load_json(path) for name, path in SOURCE_FILES.items()}
    if data["final"].get("final_test_used") is not True:
        raise RuntimeError("le résultat final conservé n'est pas marqué comme exécuté")
    outputs: list[Path] = []
    outputs.extend(final_strategy_comparison(data["final"]))
    outputs.extend(final_tail_quantiles(data["final"]))
    outputs.extend(development_cost_sensitivity(data["cost"]))
    outputs.extend(development_robustness(data["volatility"], data["heston"]))
    outputs.extend(development_ablations(data["ablations"]))
    write_manifest(outputs)
    print(f"{len(outputs) // 2} figures exportées dans {OUTPUT}")


if __name__ == "__main__":
    main()
