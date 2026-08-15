---
title: Modélisation de la volatilité avec GARCH
summary: Étudier la dynamique de la variance conditionnelle afin de mieux représenter les phases d’incertitude sur des données financières.
date: 2024-01-01
order: 3
featured: true
domain: Économétrie financière
project_type: Estimation statistique
methods: Variance conditionnelle, GARCH, diagnostic
methods_label: ÉCONOMÉTRIE · GARCH · DONNÉES FINANCIÈRES
objective: Construire une représentation statistique de la volatilité et vérifier si elle décrit correctement la dynamique observée.
visual: garch
search_terms: garch volatilité économétrie variance conditionnelle données financières diagnostic statistique
contact_subject: Projet modélisation volatilité GARCH
comment_term: projet-estimation-modeles-garch
steps:
  - title: Préparer
    description: Transformer et explorer les données financières pour caractériser leur variabilité.
  - title: Estimer
    description: Ajuster des spécifications GARCH afin de représenter la variance conditionnelle.
  - title: Diagnostiquer
    description: Analyser les résidus, comparer les modèles et interpréter la dynamique estimée.
---
## Question étudiée

Les données financières présentent souvent des périodes calmes suivies de phases plus agitées. Le projet étudie cette concentration de la volatilité dans le temps et utilise des modèles GARCH pour représenter l’évolution de la variance conditionnelle.

## Spécification GARCH

Un modèle GARCH(1,1) sépare le rendement \\(r_t\\) d’une innovation standardisée \\(z_t\\) :

$$
r_t = \mu + \varepsilon_t,
\qquad
\varepsilon_t = \sigma_t z_t,
$$

avec une variance conditionnelle définie par :

$$
\sigma_t^2 =
\omega
+ \alpha\,\varepsilon_{t-1}^{2}
+ \beta\,\sigma_{t-1}^{2}.
$$

Les contraintes \\(\omega>0\\), \\(\alpha\geq0\\) et \\(\beta\geq0\\) garantissent une variance positive. Lorsque \\(\alpha+\beta\\) est proche de 1, les chocs de volatilité disparaissent lentement.

## Estimation en Python

```python
from arch import arch_model

returns = 100 * prices.pct_change().dropna()

model = arch_model(
    returns,
    mean="Constant",
    vol="GARCH",
    p=1,
    q=1,
    dist="t",
)
result = model.fit(disp="off")

conditional_volatility = result.conditional_volatility
forecast = result.forecast(horizon=10, reindex=False)
```

## Volatilité conditionnelle

![Rendements simulés et volatilité conditionnelle GARCH](/assets/projets/modelisation-volatilite-garch/volatilite-conditionnelle.svg)

*Données simulées : les barres montrent les rendements et la courbe rouge l’écart-type conditionnel estimé.*
{: .figure-caption}

Le graphique met en évidence le regroupement de la volatilité : un choc important est généralement suivi d’une période où l’incertitude estimée reste élevée.

## Diagnostics nécessaires

| Diagnostic | Question examinée |
| --- | --- |
| Résidus standardisés | Reste-t-il une structure prévisible ? |
| Test ARCH-LM | Une hétéroscédasticité demeure-t-elle ? |
| QQ-plot | La distribution choisie représente-t-elle les queues ? |
| AIC / BIC | Une autre spécification est-elle plus parcimonieuse ? |
