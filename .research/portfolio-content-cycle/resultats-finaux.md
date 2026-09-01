# Résultats du test final préenregistré

**Ouverture unique :** 1er septembre 2026

**Statut :** résultat confirmatoire obtenu ; aucune nouvelle sélection de modèle autorisée

## Cadre de lecture

Le test final utilise 250 000 trajectoires indépendantes d'un mouvement brownien géométrique, avec \(S_0=K=100\), \(T=30/252\), \(\sigma=20\%\), 30 rééquilibrages et un coût proportionnel aller simple de 25 points de base. La politique neuronale et le protocole ont été gelés avant la génération de ces trajectoires.

Le critère confirmatoire est

\[
\Delta_{\mathrm{CVaR}}
=
\operatorname{CVaR}_{95\%}(L_{\mathrm{Leland}})
-
\operatorname{CVaR}_{95\%}(L_{\mathrm{réseau}}).
\]

Le critère est favorable lorsque la borne inférieure de son intervalle bootstrap bilatéral à 95 % est strictement positive.

## Résultat principal

La CVaR à 95 % vaut 1,7202 pour la delta de Leland et 1,5586 pour la politique neuronale. L'amélioration appariée est de **0,1615**, avec un intervalle bootstrap à 95 % de **[0,1565 ; 0,1664]**. Le critère confirmatoire préenregistré est donc satisfait dans ce scénario simulé.

La réduction relative de CVaR face à Leland est de 9,39 %. Elle ne constitue ni une garantie de performance de marché ni une démonstration de supériorité sous d'autres modèles de prix.

## Comparaison des stratégies

| Stratégie | P&L moyen | Écart-type du P&L | Probabilité de perte | VaR 95 % | CVaR 95 % | Coût moyen | Turnover |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sans couverture | -0,0101 | 4,2038 | 33,53 % | 9,0454 | 12,3126 | 0 | 0 |
| Delta Black--Scholes | -0,6846 | 0,4980 | 94,16 % | 1,5786 | 1,9230 | 0,6850 | 274,01 |
| Delta de Leland | -0,6563 | 0,4771 | 92,09 % | 1,4345 | 1,7202 | 0,6569 | 262,75 |
| Politique neuronale | -0,5840 | 0,5439 | 85,16 % | 1,3584 | 1,5586 | 0,5849 | 233,96 |

Face à la delta Black--Scholes, l'amélioration de CVaR vaut 0,3644, IC 95 % [0,3577 ; 0,3710], soit une réduction relative de 18,95 %.

## Coûts et activité de couverture

Par rapport à Leland, la politique neuronale réduit :

- le coût moyen de 0,0720, IC 95 % [0,0718 ; 0,0722], soit 10,96 % ;
- le turnover notionnel de 28,79, IC 95 % [28,70 ; 28,88], soit 10,96 % ;
- la probabilité de perte de 6,93 points de pourcentage.

Face à la delta Black--Scholes, les réductions de coût et de turnover atteignent 14,62 %, et la probabilité de perte diminue de 9,00 points.

## Compromis entre variance et risque de queue

La politique neuronale n'est pas supérieure selon toutes les mesures. Son écart-type de P&L, 0,5439, dépasse celui de Leland, 0,4771, de 14,00 %. Elle accepte donc davantage de dispersion globale tout en réduisant les pertes de queue qui correspondent à son objectif d'apprentissage.

Les quantiles élevés de perte confirment ce déplacement de risque :

| Stratégie | Quantile 95 % | Quantile 99 % | Quantile 99,5 % |
| --- | ---: | ---: | ---: |
| Delta Black--Scholes | 1,5786 | 2,1285 | 2,3567 |
| Delta de Leland | 1,4345 | 1,8908 | 2,0873 |
| Politique neuronale | 1,3584 | 1,6794 | 1,8168 |

Ce résultat est cohérent avec une optimisation ciblée de la CVaR, mais il interdit de présenter la politique comme minimisant la variance.

## Cohérence avec le développement

La CVaR neuronale finale, 1,55863, est pratiquement identique à la valeur de développement 1,55861. L'amélioration finale face à Leland, 0,16154, est également proche de l'amélioration de développement 0,15987. Cette proximité est rassurante, sans remplacer les limites du cadre de simulation.

## Limites

- Le résultat est conditionnel au GBM, à une volatilité connue et constante, à un call à la monnaie, à une échéance courte et à un coût proportionnel fixe.
- Le bootstrap mesure l'incertitude Monte-Carlo sur les trajectoires pour une politique gelée ; il ne couvre pas toute l'incertitude liée à l'apprentissage neuronal.
- La politique centrale provient d'une seule graine d'entraînement. Les réplications réalisées sur le développement soutiennent certains résultats, mais ne transforment pas ce test en étude exhaustive des initialisations.
- Les tests Heston de développement ont montré que l'avantage dépend du scénario et de l'information accordée à la stratégie de référence. Aucune robustesse générale hors modèle n'est revendiquée.
- Les P&L sont simulés sous des hypothèses idéalisées ; ils ne représentent ni rendement réalisable ni recommandation financière.

## Traçabilité

- Commit évalué : `9ea3efe94a9d0b1abe34f8ca35303bd848c9f90a`.
- Checkpoint SHA-256 : `d47f58cf3df225148688c74349cee8988e2750c7067be4f4d7dd9f3d4b6ccd8a`.
- Script SHA-256 : `51f40c1d8abb183a1f46d0798cc018f712a5b39cf19033e20d408d1b10017b87`.
- Résultat SHA-256 : `966e7ddaf7e546d60e95ae4fbf4d5adc7c1f4ad6978f1ba06d7e35fdf7cabcc3`.
- Fichier brut : `benchmarks/final-test-results.json`.
- Marqueur d'ouverture : `benchmarks/final-test-opening.json`.

Le test final a été exécuté une fois. Toute analyse supplémentaire devra réutiliser ce fichier sans régénérer les trajectoires finales.
