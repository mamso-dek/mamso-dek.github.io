---
title: "Attribution des profits et pertes des portefeuilles d’options par réseaux de neurones"
summary: Comparaison de méthodes analytiques et neuronales pour reconstruire le P&L observé d’un portefeuille d’options et l’attribuer aux facteurs de marché.
authors: "Mintodê Nicodème Atchadé · Massavo Emmanuel Abed-N. Salako"
year: 2026
date: 2026-07-27
publication_type: Manuscrit de recherche
search_terms: attribution P&L portefeuille options réseaux de neurones deep learning intelligence artificielle explicable SHAP finance quantitative risque facteurs de marché
comment_term: publication-attribution-pnl-reseaux-neurones
full_text_note: Le texte intégral n’est pas proposé sur le site. Cette fiche en présente le résumé, la méthode et les principaux résultats.
links:
  - label: Voir le mémoire associé
    url: /projets/memoire-pnl-ia-explicable.html
---
## Résumé

Cette étude porte sur l’attribution du profit et de la perte (P&L) pour des instruments complexes dont la valeur dépend de plusieurs facteurs de marché de manière non linéaire et dont l’analyse repose souvent sur une revalorisation préalable des positions. L’analyse empirique s’appuie sur un portefeuille de calls américains sur NVIDIA observé entre 2020 et 2022. L’enjeu est de reconstituer directement le P&L observé à partir des mouvements des principales variables de marché et du temps, puis d’en fournir une attribution cohérente.

Pour cela, l’étude compare des références analytiques et plusieurs formulations neuronales sur la même base empirique. Les résultats montrent que l’ajout d’une mémoire séquentielle apporte peu lorsque les mouvements observés à la date considérée sont fournis explicitement. Parmi les approches étudiées, celle qui structure le P&L comme une somme de contributions attribuées aux facteurs offre, sans atteindre la précision d’une revalorisation Black-Scholes-Merton, le meilleur compromis entre reconstitution du P&L observé, attribution par facteurs et coût pratique.

## Question et contribution

Connaître le P&L total ne permet pas de savoir quelle part provient du sous-jacent, de la volatilité implicite, des taux ou du passage du temps. Les approches classiques commencent généralement par revaloriser les positions, puis attribuent l’écart obtenu. L’étude explore une autre voie : apprendre directement le P&L observé tout en imposant au modèle une sortie additive,

$$
\widehat{\mathrm{P\&L}}_t =
\widehat{\phi}_{S,t}
+ \widehat{\phi}_{\sigma,t}
+ \widehat{\phi}_{r,t}
+ \widehat{\phi}_{\tau,t},
$$

où chaque terme représente la contribution d’un facteur de marché. Cette contrainte rend l’attribution disponible par construction et garantit que la somme des contributions restitue la prédiction journalière.

## Données et méthode

La base contient 928 343 observations relatives à 19 177 contrats distincts, cotés quotidiennement entre le 2 janvier 2020 et le 30 décembre 2022. Après appariement des observations successives d’un même contrat, l’analyse retient 907 832 transitions exploitables sur 756 journées, avec une médiane de 1 226,5 contrats actifs par jour.

Les méthodes comparées comprennent l’approximation de Taylor d’ordre 2, la revalorisation Black-Scholes-Merton, les attributions OAT, SU et ASU, des sous-réseaux avec ou sans mémoire GRU/LSTM, un réseau additif à contributions par facteur, une variante avec interactions et un réseau global expliqué par valeurs de Shapley. Le découpage est strictement chronologique : entraînement jusqu’au 30 juin 2021, validation au second semestre 2021 et test sur l’année 2022.

## Résultats clés

Sur l’échantillon test 2022, les principales performances journalières agrégées sont les suivantes :

| Méthode | \\(R^2\\) | RMSE |
| --- | ---: | ---: |
| Taylor d’ordre 2 en sous-jacent | 0,9916 | 407,6 |
| Revalorisation BSM et attribution ASU | 0,9973 | 233,0 |
| Réseau à contributions par facteur | 0,9954 | 302,6 |
| Réseau avec interactions | 0,9922 | 392,5 |
| Réseau global et valeurs de Shapley | 0,9306 | 1 172,5 |

Le réseau à contributions par facteur est la meilleure solution neuronale considérée. Il améliore nettement la référence locale de Taylor, produit une décomposition additive à une erreur moyenne de l’ordre de \\(10^{-6}\\), mais reste moins précis que la revalorisation BSM au niveau agrégé. Dans l’implémentation testée, son évaluation moyenne par journée est environ 14,5 fois moins coûteuse que l’ASU tout en fournissant directement l’attribution.

La mémoire séquentielle n’apporte qu’un gain marginal : le modèle sans mémoire atteint un \\(R^2\\) de 0,9936, contre 0,9938 pour la GRU et 0,9934 pour la LSTM. Dans le modèle retenu, le sous-jacent représente 88,9 % de l’intensité absolue moyenne des contributions, devant la volatilité implicite (5,9 %), le temps (2,6 %) et les taux (2,6 %). L’alignement avec l’ASU est satisfaisant pour les deux facteurs dominants, mais reste plus fragile pour le temps et les taux.

## Portée et limites

L’objectif n’est pas de remplacer un moteur général de valorisation d’options américaines. Les résultats portent sur un portefeuille technique de calls NVIDIA, à fréquence quotidienne, avec une convention BSM à dividende continu nul utilisée comme base de comparaison. Ils doivent être confirmés sur des portefeuilles plus hétérogènes, d’autres instruments et d’autres fréquences. Les prolongements concernent également une granularité plus fine des facteurs et l’intégration de l’attribution à des usages de couverture et de pilotage du risque.
