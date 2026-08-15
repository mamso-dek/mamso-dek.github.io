---
title: Attribution des profits et pertes d’un portefeuille par réseaux de neurones profonds et intelligence artificielle explicable
summary: Mémoire de fin d’études consacré à l’explication du P&L d’un portefeuille d’options par une approche hybride mêlant apprentissage profond, IA explicable et méthodes analytiques.
date: 2025-10-30
order: 1
featured: true
domain: Finance quantitative
project_type: Mémoire de recherche appliquée
methods: LSTM, SHAP, attribution du P&L, méthodes analytiques
methods_label: FINANCE QUANTITATIVE · DEEP LEARNING · IA EXPLICABLE
objective: Concilier la capacité prédictive des réseaux de neurones avec une attribution lisible et cohérente des profits et pertes.
visual: pnl
search_terms: mémoire P&L portefeuille options LSTM SHAP deep learning intelligence artificielle explicable FRTB risque de marché finance quantitative
contact_subject: Mémoire sur l’attribution du P&L
comment_term: memoire-attribution-pnl-ia-explicable
comments: true
steps:
  - title: Formaliser
    description: Définir le problème d’attribution du P&L dans le cadre du Fundamental Review of the Trading Book.
  - title: Modéliser
    description: Construire un réseau LSTM à partir de variables de risque pour reproduire les variations quotidiennes du portefeuille.
  - title: Expliquer
    description: Utiliser SHAP et comparer les contributions obtenues avec les décompositions analytiques OAT, SU et ASU.
resources:
  - label: Mémoire de fin d’études
    type: Rapport de recherche
    format: PDF
    description: Version finale du mémoire soutenu à l’UNSTIM d’Abomey le 30 octobre 2025.
    action: Télécharger
    download: true
    file_size: 1,1 Mo
    url: /assets/projets/memoire-pnl-ia-explicable/memoire_salako_pnl_ia_explicable.pdf
pdf_url: /assets/projets/memoire-pnl-ia-explicable/memoire_salako_pnl_ia_explicable.pdf
pdf_title: Mémoire de fin d’études
pdf_pages: 51
pdf_file_size: 1,1 Mo
pdf_language: Français
pdf_download: true
---
## Sujet étudié

Le Profit and Loss (P&L) indique la variation de valeur d’un portefeuille, mais ne permet pas à lui seul de comprendre les facteurs à l’origine de cette variation. Cette question devient particulièrement délicate pour un portefeuille d’options, dont la valeur dépend de plusieurs facteurs de marché et de relations non linéaires.

Le mémoire étudie donc la question suivante : comment combiner les réseaux de neurones profonds et l’intelligence artificielle explicable pour attribuer les profits et pertes d’un portefeuille financier de manière précise et interprétable ?

## Approche retenue

L’étude porte sur un portefeuille d’options américaines sur l’action NVIDIA, à partir de données de marché quotidiennes. Un réseau de neurones récurrent de type LSTM est utilisé pour modéliser les variations du Risk Theoretical P&L. Les prédictions sont ensuite interprétées avec la méthode SHAP afin d’estimer la contribution des principaux facteurs de risque, notamment le mouvement du sous-jacent, la volatilité, le passage du temps et les taux d’intérêt.

Les attributions obtenues sont comparées à des décompositions analytiques fondées sur les méthodes OAT, SU et ASU, implémentées dans un cadre Black-Scholes.

## Principaux résultats

Les résultats montrent que le modèle explicable reproduit la dynamique quotidienne du P&L et que ses contributions présentent une forte concordance avec celles des méthodes analytiques de référence. L’étude met également en évidence le rôle dominant du facteur directionnel, suivi des effets de volatilité et du passage du temps.

L’intérêt du travail est de rapprocher la capacité de modélisation des réseaux neuronaux de la lisibilité attendue dans l’analyse et la validation des risques de marché.

## Limites et prolongements

L’étude repose sur un seul actif et une famille homogène d’options. Les résultats devront donc être vérifiés sur des portefeuilles multi-actifs, d’autres classes d’instruments et des périodes de marché différentes. Une extension vers des approches probabilistes et des mesures comme la Value-at-Risk ou l’Expected Shortfall pourrait également approfondir le lien entre apprentissage automatique et gestion des risques.
