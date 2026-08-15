---
title: Modélisation et simulation de prix d’options
summary: Étudier la valorisation de produits dérivés en reliant hypothèses de modèle, incertitude et simulation numérique.
date: 2024-01-01
order: 2
featured: true
domain: Mathématiques financières
project_type: Modélisation numérique
methods: Valorisation, simulation, analyse de sensibilité
methods_label: SIMULATION NUMÉRIQUE · PRODUITS DÉRIVÉS · INCERTITUDE
objective: Construire une démarche de valorisation reproductible et rendre visibles les effets des hypothèses du modèle.
visual: options
search_terms: option simulation valorisation produits dérivés finance mathématiques incertitude
contact_subject: Projet simulation prix options
comment_term: projet-modelisation-simulation-prix-options
steps:
  - title: Formaliser
    description: Définir le produit étudié, les variables utiles et les hypothèses de valorisation.
  - title: Simuler
    description: Générer des scénarios numériques pour représenter plusieurs évolutions possibles du sous-jacent.
  - title: Comparer
    description: Analyser la sensibilité du prix aux paramètres et discuter les limites des résultats obtenus.
---
## Question étudiée

Le prix d’une option dépend d’hypothèses sur l’évolution du sous-jacent, le risque et le temps. Ce projet étudie comment formaliser ces hypothèses, simuler des trajectoires possibles et interpréter le prix obtenu sans dissocier le résultat des choix de modélisation.

## Modèle de diffusion

Dans le modèle de Black-Scholes, le prix \\(S_t\\) du sous-jacent suit un mouvement brownien géométrique :

$$
dS_t = \mu S_t\,dt + \sigma S_t\,dW_t.
$$

Sous la probabilité risque-neutre, \\(\mu\\) est remplacé par le taux sans risque \\(r\\). Pour une option d’achat européenne de strike \\(K\\), le payoff à maturité est :

$$
H(S_T) = \max(S_T-K,0),
$$

et son estimateur de Monte Carlo s’écrit :

$$
\widehat{C}_0 =
e^{-rT}\frac{1}{N}\sum_{i=1}^{N}\max\!\left(S_T^{(i)}-K,0\right).
$$

## Simulation en Python

```python
import numpy as np

rng = np.random.default_rng(42)
z = rng.standard_normal(size=(n_scenarios, n_steps))

increments = (
    (r - 0.5 * sigma**2) * dt
    + sigma * np.sqrt(dt) * z
)
paths = s0 * np.exp(np.cumsum(increments, axis=1))

payoff = np.maximum(paths[:, -1] - strike, 0.0)
price = np.exp(-r * maturity) * payoff.mean()
standard_error = np.exp(-r * maturity) * payoff.std(ddof=1) / np.sqrt(n_scenarios)
```

## Trajectoires simulées

![Trajectoires simulées du prix d’un actif](/assets/projets/simulation-prix-options/trajectoires-simulees.svg)

*Données simulées : les courbes grises représentent plusieurs scénarios et la courbe rouge leur trajectoire moyenne.*
{: .figure-caption}

Le prix estimé doit toujours être accompagné de son erreur de Monte Carlo. Une analyse de sensibilité permet ensuite d’étudier l’effet de \\(\sigma\\), \\(T\\), \\(K\\) et \\(r\\) sur la valorisation.

## Extensions possibles

- réduction de variance par variables antithétiques ;
- comparaison avec la formule fermée de Black-Scholes ;
- estimation des sensibilités Delta, Gamma et Vega ;
- prise en compte d’une volatilité locale ou stochastique.
