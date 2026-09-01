"""Construit le notebook narratif du projet depuis des cellules versionnées."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(__file__).with_name("deep-hedging-couts-transaction.ipynb")


def markdown(source: str):
    return nbf.v4.new_markdown_cell(source.strip())


def code(source: str):
    return nbf.v4.new_code_cell(source.strip())


def build_cells() -> list:
    return [
        markdown(
            r"""
# Deep hedging sous coûts de transaction

**Compromis entre risque de queue et intensité de négociation**

Étude computationnelle reproductible · Massavo Salako · septembre 2026

> Ce notebook est un rapport d'analyse. Il relit des artefacts figés et ne simule pas le test final.
"""
        ),
        markdown(
            r"""
## TL;DR

Sur le test final préenregistré de **250 000 trajectoires GBM**, avec 30 rééquilibrages et un coût aller simple de 25 points de base :

- la politique neuronale atteint une CVaR à 95 % de **1,5586**, contre **1,7202** pour la delta de Leland ;
- l'amélioration appariée est de **0,1615**, IC bootstrap à 95 % **[0,1565 ; 0,1664]** ;
- son turnover est inférieur de **28,79**, soit **10,96 %** ;
- son écart-type de P&L est cependant **14,00 % plus élevé** que celui de Leland.

Le réseau améliore donc le risque de queue visé et réduit les transactions dans le scénario central, mais il ne domine pas toutes les mesures de dispersion et son avantage n'est pas robuste à tous les changements de volatilité ou de modèle.
"""
        ),
        markdown(
            r"""
## 1. Portée et règle de sécurité

Le notebook répond à une question scientifique précise : une politique neuronale compacte, optimisée selon la CVaR, peut-elle améliorer une couverture discrète classique lorsqu'il existe des coûts proportionnels ?

Toutes les conclusions sont conditionnelles au cadre simulé. Les cellules ci-dessous chargent uniquement des fichiers JSON et des figures déjà conservés. Le test final, ouvert une seule fois, ne doit jamais être régénéré depuis ce document.
"""
        ),
        code(
            """
from pathlib import Path
import hashlib
import json
import platform
import sys

import numpy as np
import pandas as pd
from IPython.display import Image, Markdown, display

pd.set_option("display.max_columns", 20)
pd.set_option("display.width", 140)


def locate_project_root() -> Path:
    candidates = [Path.cwd(), *Path.cwd().parents]
    for candidate in candidates:
        expected = candidate / "benchmarks" / "final-test-results.json"
        if expected.exists():
            return candidate
    raise FileNotFoundError("Dossier .research/portfolio-content-cycle introuvable")


ROOT = locate_project_root()
BENCHMARKS = ROOT / "benchmarks"
FIGURES = ROOT / "figures" / "generated"
print("Racine scientifique localisée : .research/portfolio-content-cycle")
"""
        ),
        markdown(
            """
### 1.1 Vérifier les sources avant lecture

Le manifeste relie chaque figure à son artefact numérique. Le contrôle suivant vérifie les cinq sources, le fichier final et le marqueur d'ouverture avant de calculer la moindre synthèse.
"""
        ),
        code(
            """
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


source_paths = {
    "final": BENCHMARKS / "final-test-results.json",
    "cost": BENCHMARKS / "cost-sensitivity.json",
    "volatility": BENCHMARKS / "frequency-volatility.json",
    "heston": BENCHMARKS / "heston-parameter-sensitivity.json",
    "ablations": BENCHMARKS / "model-ablations.json",
}
manifest = json.loads((FIGURES / "manifest.json").read_text(encoding="utf-8"))
figure_alt = {
    Path(item["file"]).name: item["alt_text"]
    for item in manifest["figures"]
    if item["file"].endswith(".png")
}
source_audit = []
for name, path in source_paths.items():
    observed = sha256(path)
    expected = manifest["source_hashes"][name]
    source_audit.append(
        {"source": name, "fichier": path.name, "empreinte": observed[:12], "conforme": observed == expected}
    )

final_result = json.loads(source_paths["final"].read_text(encoding="utf-8"))
opening_marker = json.loads((BENCHMARKS / "final-test-opening.json").read_text(encoding="utf-8"))
assert all(row["conforme"] for row in source_audit)
assert final_result["final_test_used"] is True
assert opening_marker["status"] == "completed"
assert opening_marker["output_sha256"] == sha256(source_paths["final"])
assert sha256(source_paths["final"]) == "966e7ddaf7e546d60e95ae4fbf4d5adc7c1f4ad6978f1ba06d7e35fdf7cabcc3"

display(pd.DataFrame(source_audit))
print("Test final : fermé, artefact intact et ouverture unique documentée.")
"""
        ),
        markdown(
            r"""
## 2. Contexte et méthode

### 2.1 Position couverte et convention de P&L

On considère un vendeur de call européen. À chaque date \(t\), il détient \(h_t\) unités du sous-jacent jusqu'à la date suivante. Le P&L terminal est

\[
\Pi_T
=
\pi_0
+ \sum_{t=0}^{N-1} h_t(S_{t+1}-S_t)
- c\!\left(
S_0|h_0|
+ \sum_{t=1}^{N-1}S_t|h_t-h_{t-1}|
+ S_T|h_{N-1}|
\right)
- (S_T-K)^+.
\]

Le coût \(c\) est un coût **aller simple**. L'ouverture, les rééquilibrages et la liquidation terminale sont tous facturés. Une même prime Black--Scholes est utilisée pour les stratégies d'une comparaison afin d'isoler l'effet de la couverture.
"""
        ),
        markdown(
            r"""
### 2.2 Pourquoi optimiser la CVaR ?

La perte est \(L=-\Pi_T\). Pour \(\alpha=95\%\), la formulation de Rockafellar--Uryasev est

\[
\operatorname{CVaR}_{\alpha}(L)
=
\min_{\eta}
\left\{
\eta + \frac{1}{1-\alpha}\,\mathbb{E}\left[(L-\eta)_+\right]
\right\}.
\]

Cette fonction pénalise directement la moyenne des pertes les plus graves. Elle ne minimise pas la variance ; un modèle peut donc réduire la queue tout en acceptant davantage de dispersion ailleurs. Cette distinction sera vérifiée dans les résultats.
"""
        ),
        markdown(
            r"""
### 2.3 Stratégies comparées

1. **Sans couverture**, comme contrôle minimal.
2. **Delta Black--Scholes** recalculée aux 30 dates.
3. **Delta de Leland**, qui augmente la volatilité utilisée par la delta pour tenir compte des coûts :

\[
\sigma_L
=
\sigma\sqrt{1+\sqrt{\frac{8}{\pi}}\frac{c}{\sigma\sqrt{\Delta t}}}.
\]

4. **Politique neuronale** partagée dans le temps : deux couches cachées de 32 neurones SiLU, 1 217 paramètres, état composé de la log-moneyness, du temps restant et de l'inventaire précédent, sortie bornée dans \([0;1{,}25]\).
"""
        ),
        markdown(
            r"""
### 2.4 Hypothèses clés

- mouvement brownien géométrique sous la mesure risque-neutre ;
- volatilité constante de 20 % dans le scénario central ;
- call à la monnaie, \(S_0=K=100\), échéance \(30/252\) année ;
- taux sans risque nul ;
- coûts proportionnels sans impact de marché, spread variable ni contrainte de liquidité ;
- trajectoires simulées, et non observations de marché.

Ces hypothèses rendent l'expérience contrôlable et reproductible, mais limitent directement la portée économique des conclusions.
"""
        ),
        code(
            """
market = final_result["market"]
evaluation = final_result["evaluation"]
protocol_table = pd.DataFrame(
    [
        ("Spot initial", market["s0"]),
        ("Strike", market["strike"]),
        ("Échéance", f"{market['maturity']:.6f} an"),
        ("Volatilité", f"{100 * market['sigma']:.0f} %"),
        ("Rééquilibrages", market["n_steps"]),
        ("Coût aller simple", f"{10_000 * evaluation['one_way_cost']:.0f} pb"),
        ("Niveau de CVaR", f"{100 * evaluation['alpha']:.0f} %"),
        ("Trajectoires finales", f"{evaluation['size']:,}".replace(",", " ")),
        ("Réplications bootstrap", f"{evaluation['bootstrap_replicates']:,}".replace(",", " ")),
    ],
    columns=["Paramètre", "Valeur"],
)
display(protocol_table)
"""
        ),
        markdown(
            """
## 3. Données et séparation expérimentale

Les données sont entièrement simulées. L'entraînement renouvelle ses trajectoires à chaque époque ; la validation sélectionne le checkpoint ; un jeu de développement distinct sert aux diagnostics et sensibilités. Le test final de 250 000 trajectoires, graine 20269000, n'a été généré qu'après gel du modèle et du protocole.

Les intervalles bootstrap sont appariés : une même trajectoire fournit la perte du réseau et celle de la référence. Ils décrivent l'incertitude Monte-Carlo conditionnelle à la politique apprise, pas toute la variabilité de l'entraînement neuronal.
"""
        ),
        markdown("## 4. Résultats finaux"),
        code(
            """
strategy_labels = {
    "unhedged": "Sans couverture",
    "black_scholes_delta": "Delta Black-Scholes",
    "leland_delta": "Delta de Leland",
    "neural_policy": "Politique neuronale",
}
metric_rows = []
for key, label in strategy_labels.items():
    metrics = final_result["strategy_metrics"][key]
    metric_rows.append(
        {
            "Stratégie": label,
            "P&L moyen": metrics["mean_pnl"],
            "Écart-type": metrics["std_pnl"],
            "Probabilité de perte (%)": 100 * metrics["loss_probability"],
            "VaR 95 %": metrics["var_loss_95"],
            "CVaR 95 %": metrics["cvar_loss_95"],
            "Coût moyen": metrics["mean_transaction_cost"],
            "Turnover": metrics["mean_turnover_notional"],
        }
    )
metrics_table = pd.DataFrame(metric_rows).set_index("Stratégie")
display(metrics_table.round(4))
"""
        ),
        code(
            """
display(
    Image(
        filename=str(FIGURES / "final-strategy-comparison.png"),
        width=980,
        alt=figure_alt["final-strategy-comparison.png"],
    )
)
"""
        ),
        markdown(
            """
### 4.1 Test confirmatoire

Le critère gelé compare la CVaR de Leland à celle du réseau. Une amélioration positive favorise le réseau ; le résultat est déclaré favorable uniquement si la borne inférieure de l'intervalle à 95 % est strictement positive.
"""
        ),
        code(
            """
comparisons = final_result["paired_comparisons"]
comparison_labels = {
    "cvar_neural_versus_leland": "CVaR : réseau vs Leland",
    "cvar_neural_versus_delta": "CVaR : réseau vs delta",
    "cost_neural_versus_leland": "Coût : réseau vs Leland",
    "turnover_neural_versus_leland": "Turnover : réseau vs Leland",
}
comparison_rows = []
for key, label in comparison_labels.items():
    result = comparisons[key]
    comparison_rows.append(
        {
            "Comparaison": label,
            "Amélioration": result["point_improvement"],
            "IC 95 % bas": result["ci_lower"],
            "IC 95 % haut": result["ci_upper"],
        }
    )
comparison_table = pd.DataFrame(comparison_rows).set_index("Comparaison")
display(comparison_table.round(4))
assert comparisons["cvar_neural_versus_leland"]["ci_lower"] > 0
assert final_result["confirmatory_decision"]["favorable"] is True
"""
        ),
        markdown(
            r"""
La politique neuronale réduit la CVaR de **0,1615** face à Leland, IC 95 % **[0,1565 ; 0,1664]**, soit **9,39 %**. Son turnover baisse simultanément de **28,79** et son coût moyen de **0,0720**. Le résultat confirmatoire est favorable dans le scénario central.

Cette phrase doit rester complète : elle décrit une politique gelée, un modèle GBM et un coût précis. Elle ne signifie pas que le réseau domine toute couverture en marché réel.
"""
        ),
        markdown("### 4.2 Forme de la queue de perte"),
        code(
            """
display(
    Image(
        filename=str(FIGURES / "final-tail-quantiles.png"),
        width=920,
        alt=figure_alt["final-tail-quantiles.png"],
    )
)
"""
        ),
        code(
            """
tail_rows = []
for key in ("black_scholes_delta", "leland_delta", "neural_policy"):
    quantiles = final_result["strategy_metrics"][key]["loss_quantiles"]
    tail_rows.append(
        {
            "Stratégie": strategy_labels[key],
            "Q95": quantiles["q95"],
            "Q99": quantiles["q99"],
            "Q99,5": quantiles["q995"],
        }
    )
display(pd.DataFrame(tail_rows).set_index("Stratégie").round(4))
"""
        ),
        markdown(
            """
Les trois quantiles élevés sont plus faibles pour le réseau. En revanche, son écart-type de P&L vaut 0,5439 contre 0,4771 pour Leland, soit 14,00 % de plus. L'apprentissage a donc déplacé le compromis vers la queue ciblée, sans réduire toute la dispersion.
"""
        ),
        markdown("## 5. Sensibilités de développement"),
        markdown(
            """
### 5.1 Coûts de transaction

Une politique distincte a été entraînée pendant 2 000 époques pour chaque coût. Ces résultats servent à comprendre le mécanisme ; ils ne remplacent pas le test final central.
"""
        ),
        code(
            """
display(
    Image(
        filename=str(FIGURES / "development-cost-sensitivity.png"),
        width=980,
        alt=figure_alt["development-cost-sensitivity.png"],
    )
)
"""
        ),
        code(
            """
cost_data = json.loads(source_paths["cost"].read_text(encoding="utf-8"))
cost_rows = []
for scenario in cost_data["scenarios"]:
    neural = scenario["development_metrics"]["neural"]
    leland = scenario["development_metrics"]["delta_leland"]
    cost_rows.append(
        {
            "Coût (pb)": scenario["basis_points"],
            "CVaR réseau": neural["cvar_loss_95"],
            "CVaR Leland": leland["cvar_loss_95"],
            "Gain CVaR": scenario["paired_bootstrap_versus_leland"]["point_improvement"],
            "Turnover réseau": neural["mean_turnover_notional"],
            "Turnover Leland": leland["mean_turnover_notional"],
        }
    )
display(pd.DataFrame(cost_rows).set_index("Coût (pb)").round(4))
"""
        ),
        markdown(
            """
Quand le coût passe de 0 à 50 points de base, le turnover neuronal diminue de 258,20 à 216,93. La CVaR augmente néanmoins, car réduire les transactions ne peut annuler la friction. Le réseau reste meilleur que Leland aux quatre coûts de la grille, mais cette courbe ne démontre rien hors de cet intervalle.
"""
        ),
        markdown(
            """
### 5.2 Robustesse hors modèle d'entraînement

Le signe présenté ci-dessous est CVaR(référence informée) moins CVaR(réseau gelé). Une valeur négative signifie que la référence fait mieux. Les points ouverts signalent un intervalle contenant zéro.
"""
        ),
        code(
            """
display(
    Image(
        filename=str(FIGURES / "development-robustness.png"),
        width=1020,
        alt=figure_alt["development-robustness.png"],
    )
)
"""
        ),
        code(
            """
volatility_data = json.loads(source_paths["volatility"].read_text(encoding="utf-8"))
heston_data = json.loads(source_paths["heston"].read_text(encoding="utf-8"))


def classify_interval(lower: float, upper: float) -> str:
    if lower > 0:
        return "avantage réseau"
    if upper < 0:
        return "avantage référence"
    return "indistinct à 95 %"


robustness_rows = []
for scenario in volatility_data["volatility_experiment"]["scenarios"]:
    result = scenario["paired_bootstrap_neural_versus_informed_leland"]
    robustness_rows.append(
        {
            "Cadre": "GBM",
            "Scénario": f"sigma={100 * scenario['scenario_sigma']:.0f}%",
            "Amélioration": result["point_improvement"],
            "IC bas": result["ci_lower"],
            "IC haut": result["ci_upper"],
            "Lecture": classify_interval(result["ci_lower"], result["ci_upper"]),
        }
    )
for scenario in heston_data["scenarios"]:
    result = scenario["paired_bootstrap"]["neural_versus_leland_instantaneous_variance_proxy"]
    parameters = scenario["parameters"]
    robustness_rows.append(
        {
            "Cadre": "Heston",
            "Scénario": f"xi={parameters['vol_of_vol']:.2f}, rho={parameters['rho']:.2f}",
            "Amélioration": result["point_improvement"],
            "IC bas": result["ci_lower"],
            "IC haut": result["ci_upper"],
            "Lecture": classify_interval(result["ci_lower"], result["ci_upper"]),
        }
    )
display(pd.DataFrame(robustness_rows).round(4))
"""
        ),
        markdown(
            """
La robustesse n'est pas générale. À 15 % et 30 % de volatilité GBM, Leland informé du vrai sigma fait mieux ; à 25 %, l'intervalle contient zéro. Sous Heston, le réseau reste meilleur dans deux scénarios modérés, devient statistiquement comparable dans le scénario à forte vol-of-vol avec levier, puis inférieur au proxy informé lorsque la vol-of-vol vaut 0,60 et rho vaut 0.

Le proxy Heston n'est pas une delta analytique exacte. Il observe toutefois la variance instantanée que le réseau ne reçoit pas, ce qui rend la comparaison informative sur la valeur de l'information d'état.
"""
        ),
        markdown("### 5.3 Ablations de l'état et de la capacité"),
        code(
            """
display(
    Image(
        filename=str(FIGURES / "development-ablations.png"),
        width=1000,
        alt=figure_alt["development-ablations.png"],
    )
)
"""
        ),
        code(
            """
ablation_data = json.loads(source_paths["ablations"].read_text(encoding="utf-8"))
ablation_rows = []
for variant in ablation_data["variants"]:
    if variant["name"] == "central_inventory_h32":
        continue
    ablation_rows.append(
        {
            "Variante": variant["name"],
            "Paramètres": variant["parameter_count"],
            "CVaR": variant["development_metrics"]["cvar_loss_95"],
            "Avantage CVaR central": variant["central_improvement_over_variant"]["point_improvement"],
            "Réduction turnover centrale": variant["central_turnover_reduction_over_variant"]["point_improvement"],
        }
    )
display(pd.DataFrame(ablation_rows).set_index("Variante").round(4))
"""
        ),
        markdown(
            """
Retirer l'inventaire précédent augmente la CVaR de 0,0160 et le turnover de 13,08 : cet état fournit bien l'inertie utile sous coûts. Réduire la largeur à 16 dégrade la CVaR de 0,0195. L'augmenter à 64 améliore la CVaR de seulement 0,0029 pour 4 481 paramètres contre 1 217 ; le modèle central reste retenu par parcimonie.
"""
        ),
        markdown("## 6. Contrôle de cohérence développement–test"),
        code(
            """
central_development = next(
    scenario for scenario in cost_data["scenarios"] if scenario["basis_points"] == 25
)
consistency = pd.DataFrame(
    [
        {
            "Mesure": "CVaR réseau",
            "Développement": central_development["development_metrics"]["neural"]["cvar_loss_95"],
            "Test final": final_result["strategy_metrics"]["neural_policy"]["cvar_loss_95"],
        },
        {
            "Mesure": "CVaR Leland",
            "Développement": central_development["development_metrics"]["delta_leland"]["cvar_loss_95"],
            "Test final": final_result["strategy_metrics"]["leland_delta"]["cvar_loss_95"],
        },
        {
            "Mesure": "Amélioration réseau",
            "Développement": central_development["paired_bootstrap_versus_leland"]["point_improvement"],
            "Test final": comparisons["cvar_neural_versus_leland"]["point_improvement"],
        },
    ]
)
consistency["Écart absolu"] = (consistency["Test final"] - consistency["Développement"]).abs()
display(consistency.set_index("Mesure").round(6))
"""
        ),
        markdown(
            """
La CVaR neuronale finale diffère de moins de 0,0001 de sa valeur de développement. L'amélioration face à Leland passe de 0,1599 à 0,1615. Cette proximité soutient la stabilité Monte-Carlo du scénario central ; elle ne valide pas les hypothèses du GBM sur des données réelles.
"""
        ),
        markdown(
            r"""
## 7. Conclusions

1. **Résultat confirmatoire.** Dans le scénario central préenregistré, le réseau réduit la CVaR de 9,39 % face à Leland avec un intervalle apparié strictement positif.
2. **Mécanisme économique.** La politique négocie moins : coût et turnover baissent de 10,96 % face à Leland.
3. **Objectif ciblé.** La variance du P&L augmente de 14,00 %. Le gain concerne la queue de perte, pas toutes les formes de risque.
4. **Rôle de l'état.** L'inventaire précédent réduit à la fois CVaR et turnover dans l'ablation.
5. **Robustesse limitée.** Une référence informée peut égaler ou dépasser le réseau lorsque la volatilité ou le modèle générateur change.

La contribution du projet n'est pas un nouvel algorithme. Elle réside dans un protocole reproductible, une comparaison appariée, la conservation des résultats négatifs et une séparation stricte entre développement et test final.
"""
        ),
        markdown(
            """
## 8. Limites

- Une seule option, une échéance courte et une grille principale de 30 dates.
- Coût linéaire, sans spread stochastique, impact de marché ni contrainte de liquidité.
- Volatilité connue et constante dans le test confirmatoire.
- Politique centrale issue d'une seule graine d'entraînement ; le bootstrap ne couvre pas cette incertitude d'optimisation.
- Tests Heston limités à une grille stylisée et à un proxy de delta informé, non à une couverture Heston analytique exacte.
- Aucune calibration sur des données de marché et aucune affirmation de rendement réalisable.

Une extension crédible étudierait plusieurs maturités et strikes, des coûts non linéaires, une volatilité latente estimée et un protocole de calibration temporelle sur données réelles, avec un nouveau jeu de test indépendant.
"""
        ),
        markdown(
            """
## 9. Références principales

- Black, F. & Scholes, M. (1973), *The Pricing of Options and Corporate Liabilities*, DOI [10.1086/260062](https://doi.org/10.1086/260062).
- Leland, H. E. (1985), *Option Pricing and Replication with Transactions Costs*, DOI [10.1111/j.1540-6261.1985.tb02383.x](https://doi.org/10.1111/j.1540-6261.1985.tb02383.x).
- Rockafellar, R. T. & Uryasev, S. (2000), *Optimization of Conditional Value-at-Risk*, DOI [10.21314/JOR.2000.038](https://doi.org/10.21314/JOR.2000.038).
- Heston, S. L. (1993), *A Closed-Form Solution for Options with Stochastic Volatility*, DOI [10.1093/rfs/6.2.327](https://doi.org/10.1093/rfs/6.2.327).
- Buehler, H., Gonon, L., Teichmann, J. & Wood, B. (2019), *Deep Hedging*, DOI [10.1080/14697688.2019.1571683](https://doi.org/10.1080/14697688.2019.1571683).
"""
        ),
        markdown(
            """
## 10. Reproductibilité

Le notebook est reconstruit par `notebooks/build_notebook.py`, puis exécuté dans l'environnement verrouillé. Il ne dépend d'aucun accès réseau. Les calculs relisent les JSON suivis par Git et contrôlent leurs SHA-256 avant affichage.

Commande d'exécution depuis la racine scientifique :

```bash
python -m jupyter nbconvert --execute --to notebook --inplace notebooks/deep-hedging-couts-transaction.ipynb
```
"""
        ),
        code(
            """
environment = pd.Series(
    {
        "Python": platform.python_version(),
        "Environnement": f"{Path(sys.executable).name} dans .lock-venv",
        "NumPy": np.__version__,
        "pandas": pd.__version__,
        "Commit évalué": final_result["repository_commit"],
        "SHA-256 résultat": sha256(source_paths["final"]),
        "Exports graphiques contrôlés": len(manifest["figures"]),
    },
    name="Valeur",
)
display(environment.to_frame())
print("Notebook terminé : toutes les assertions d'intégrité ont réussi.")
"""
        ),
    ]


def main() -> None:
    notebook = nbf.v4.new_notebook(
        cells=build_cells(),
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.12"},
        },
    )
    nbf.validate(notebook)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, OUTPUT)
    print(f"Notebook construit : {OUTPUT}")


if __name__ == "__main__":
    main()
