---
title: "Attribution des profits et pertes des portefeuilles d’options par réseaux de neurones"
summary: Un manuscrit de recherche sur la reconstruction du P&L observé d’un portefeuille d’options et son attribution aux facteurs de marché.
authors: "Mintodê Nicodème Atchadé · Massavo Emmanuel Abed-N. Salako"
year: 2026
date: 2026-07-27
venue: "Article issu du mémoire · Manuscrit finalisé, non publié"
status_note: "Version du 27 juillet 2026 · Manuscrit non publié"
publication_type: Manuscrit de recherche
search_terms: attribution P&L portefeuille options réseaux de neurones deep learning intelligence artificielle explicable SHAP finance quantitative risque facteurs de marché
comment_term: publication-attribution-pnl-reseaux-neurones
full_text_note: Le manuscrit est finalisé mais non publié. Son texte intégral n’est pas diffusé publiquement à ce stade.
links:
  - label: Voir le mémoire associé
    url: /projets/memoire-pnl-ia-explicable.html
---
## Résumé

Cette étude porte sur l’attribution du profit et de la perte d’un portefeuille de calls américains sur NVIDIA observé entre 2020 et 2022. L’objectif est de reconstruire directement le P&L quotidien observé et de le relier aux principaux facteurs de marché, notamment le sous-jacent, la volatilité, les taux et le temps.

## Problème étudié

Connaître le P&L total d’un portefeuille ne suffit pas à comprendre sa performance ou son risque. Il faut également déterminer les facteurs qui expliquent les variations observées. Les méthodes classiques d’attribution peuvent dépendre d’un modèle de valorisation et de l’ordre dans lequel les facteurs sont modifiés.

## Approche

Le travail compare des références analytiques, dont les méthodes de revalorisation et l’Average Sequential Updating, à plusieurs formulations neuronales. L’une des architectures étudiées structure le P&L comme une somme de contributions attribuées aux facteurs. Cette contrainte permet de produire à la fois une reconstruction du P&L et une lecture de sa composition.

## Résultats principaux

Les résultats montrent que l’ajout d’une mémoire séquentielle apporte un gain limité lorsque les mouvements observés à la date considérée sont fournis explicitement. L’architecture qui structure le P&L en contributions par facteurs offre, sans atteindre la précision d’une revalorisation Black–Scholes–Merton, un compromis entre reconstruction du P&L observé, attribution par facteurs et coût pratique.

L’importance relative des contributions dépend de la période et des caractéristiques des contrats. L’étude fournit ainsi un cadre de comparaison entre méthodes analytiques et méthodes neuronales pour des instruments dont la valeur dépend de plusieurs facteurs de manière non linéaire.

## Limites et prolongements

L’étude repose sur un univers limité de contrats et sur un seul sous-jacent. Elle ne permet donc pas de généraliser directement les résultats à tous les portefeuilles. Des travaux complémentaires pourraient porter sur plusieurs actifs, des portefeuilles plus diversifiés et une comparaison avec d’autres mesures de risque.
