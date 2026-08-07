---
title: "Décomposition du Profit & Loss (BRVM)"
summary: Comprendre les variations de performance en reliant le P&L aux facteurs de risque qui peuvent les expliquer.
date: 2025-01-01
order: 1
featured: true
domain: Finance quantitative
project_type: Étude de modélisation
methods: Risque, apprentissage automatique, explicabilité
methods_label: FINANCE QUANTITATIVE · ANALYSE DU RISQUE · MODÉLISATION
objective: Passer d’un résultat agrégé à une explication quantitative compréhensible et exploitable.
visual: pnl
search_terms: finance quantitative risque brvm pnl profit loss intelligence artificielle explicabilité modélisation
contact_subject: "Projet P&L BRVM"
comment_term: projet-decomposition-profit-loss-brvm
steps:
  - title: Structurer
    description: Identifier les variables de marché et préparer les données nécessaires à l’analyse.
  - title: Modéliser
    description: Étudier la relation entre facteurs de risque et variations du P&L à l’aide de modèles prédictifs.
  - title: Expliquer
    description: Mobiliser des outils d’IA explicable pour rendre les contributions du modèle plus lisibles.
---
## Question étudiée

Le Profit & Loss résume la variation de valeur d’un portefeuille, mais il n’explique pas à lui seul l’origine de cette variation. Le travail consiste à relier les mouvements observés aux facteurs de risque disponibles afin d’obtenir une lecture plus transparente de la performance.

## Formulation quantitative

Pour une date \(t\), la variation du portefeuille peut être représentée par une somme de contributions et un résidu :

$$
\Delta V_t = \sum_{j=1}^{p} \beta_j\,\Delta x_{j,t} + \varepsilon_t,
$$

où \(\Delta x_{j,t}\) désigne la variation du facteur de risque \(j\), \(\beta_j\) sa sensibilité estimée et \(\varepsilon_t\) la partie non expliquée. Avec un modèle non linéaire, la même logique peut être conservée grâce à des contributions locales \(\phi_j\) telles que :

$$
\widehat{\Delta V_t} = \phi_0 + \sum_{j=1}^{p}\phi_j.
$$

## Prototype Python

Le bloc suivant illustre un pipeline minimal d’estimation et de décomposition. Les noms de colonnes devront être adaptés aux données réelles.

```python
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import shap

features = ["taux", "change", "actions", "volatilite", "liquidite"]
X = data[features]
y = data["variation_pnl"]

model = RandomForestRegressor(
    n_estimators=400,
    min_samples_leaf=8,
    random_state=42,
)
model.fit(X, y)

explainer = shap.TreeExplainer(model)
contributions = explainer.shap_values(X)
decomposition = pd.DataFrame(contributions, columns=features)
```

## Lecture graphique

![Contributions simulées des facteurs de risque au Profit & Loss](/assets/projets/decomposition-pnl-brvm/contributions-simulees.svg)

*Illustration méthodologique sur données simulées : les barres représentent les contributions individuelles et la ligne leur cumul.*
{: .figure-caption}

L’intérêt de cette représentation est double : identifier les facteurs dominants et mesurer la part qui reste inexpliquée. Sur des données réelles, la stabilité des contributions doit être vérifiée dans le temps avant toute interprétation économique.

## Points de vigilance

- une contribution prédictive n’établit pas automatiquement une causalité ;
- les facteurs très corrélés peuvent se partager l’explication de manière instable ;
- le résidu doit être analysé pour détecter une variable absente ou une rupture ;
- la décomposition doit être comparée aux sensibilités financières usuelles.
