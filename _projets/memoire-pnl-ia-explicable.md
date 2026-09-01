---
title: Attribution des profits et pertes d’un portefeuille par réseaux de neurones profonds et intelligence artificielle explicable
summary: Mémoire de fin d’études consacré à la prévision et à l’attribution du P&L d’un portefeuille d’options américaines sur NVIDIA par LSTM, SHAP et méthodes analytiques.
date: 2025-10-30
order: 1
featured: true
domain: Finance quantitative
project_type: Mémoire de recherche appliquée
methods: LSTM, GradientSHAP, PLA, OAT, SU et ASU
methods_label: LSTM · SHAP · ATTRIBUTION DU P&L
objective: Reproduire le P&L journalier d’un portefeuille d’options et attribuer ses variations aux facteurs de risque de manière transparente.
hero_image: /assets/projets/memoire-pnl-ia-explicable/contributions-shap.png
hero_image_alt: Contributions SHAP signées du portefeuille, dominées par le facteur delta
hero_image_caption: Figure 3.4 du mémoire · Somme des contributions SHAP signées en 2022
search_terms: mémoire P&L portefeuille options LSTM SHAP deep learning intelligence artificielle explicable FRTB risque de marché finance quantitative
contact_subject: Mémoire sur l’attribution du P&L
comment_term: memoire-attribution-pnl-ia-explicable
comments: true
steps:
  - title: Construire
    description: Préparer les chaînes d’options NVIDIA et définir les P&L de marché et théorique utilisés dans le test PLA.
  - title: Prévoir
    description: Comparer LSTM, GRU et XGBoost, puis retenir la configuration la plus précise sur l’année 2022.
  - title: Attribuer
    description: Décomposer les prédictions avec GradientSHAP et confronter les contributions aux méthodes OAT, SU et ASU.
resources:
  - label: Mémoire de fin d’études
    format: PDF
    file_size: 1,1 Mo
    new_tab: true
    url: /assets/projets/memoire-pnl-ia-explicable/memoire_salako_pnl_ia_explicable.pdf
pdf_url: /assets/projets/memoire-pnl-ia-explicable/memoire_salako_pnl_ia_explicable.pdf
pdf_title: Mémoire de fin d’études
pdf_pages: 51
pdf_file_size: 1,1 Mo
pdf_language: Français
pdf_download: true
---
## Sujet étudié

Le Profit and Loss (P&L) mesure la variation de valeur d’un portefeuille, mais il ne précise pas quels facteurs de marché ont produit le gain ou la perte. Pour un portefeuille d’options, cette attribution est particulièrement délicate : le prix dépend simultanément du sous-jacent, de la volatilité implicite, du temps restant jusqu’à l’échéance, du taux d’intérêt et de relations non linéaires entre ces facteurs.

Le mémoire étudie comment combiner un modèle prédictif profond et une méthode d’intelligence artificielle explicable pour reproduire le P&L journalier, puis attribuer chaque prédiction à des facteurs de risque interprétables dans le cadre du *P&L Attribution Test* du FRTB.

## Données et protocole

L’étude utilise les chaînes quotidiennes de calls américains sur l’action NVIDIA entre 2020 et 2022. Après filtrage et alignement sur le calendrier du NYSE, la base finale comprend environ 977 000 observations. Le P&L hypothétique de marché sert de référence, tandis que les modèles apprennent le *Risk Theoretical P&L*.

Trois familles prédictives sont comparées : LSTM, GRU et XGBoost. La configuration retenue est un LSTM utilisant six pas temporels et les variables DRISK_core+, qui intègrent explicitement les produits entre chocs de marché et sensibilités. Les données de 2022 constituent l’échantillon d’évaluation.

Les prédictions du modèle retenu sont ensuite expliquées avec GradientSHAP. Les contributions sont regroupées en familles économiques : direction du sous-jacent \\(\Delta\\), volatilité \\(\nu\\), temps \\(\theta\\), taux \\(\rho\\) et autres variables d’état. Elles sont enfin comparées aux décompositions analytiques OAT, SU et ASU calculées sous Black-Scholes, avec un contrôle complémentaire sous un arbre binomial CRR.

## Résultats prédictifs

Le LSTM retenu obtient les performances suivantes sur l’année 2022 :

| Indicateur | Valeur |
| --- | ---: |
| RMSE | 0,768 |
| MAE | 0,391 |
| \\(R^2\\) | 0,972 |
| Corrélation quotidienne | 0,996 |
| Statistique KS | 0,064 |

La configuration passe le test PLA et reproduit étroitement la dynamique du P&L de marché. Les erreurs augmentent toutefois pour les options très dans la monnaie, proches de l’échéance ou observées dans les régimes de volatilité implicite les plus élevés. Sur le 1 % d’erreurs les plus extrêmes, la détection des pertes conserve une précision de 0,90 et un rappel de 0,91.

## Résultats d’attribution

La somme des contributions SHAP, valeur de base comprise, reconstitue pratiquement toute la prédiction du modèle : le ratio médian de complétude vaut 1,000. La répartition absolue met en évidence une exposition principalement directionnelle :

| Famille de facteurs | Part absolue |
| --- | ---: |
| Delta | 82 % |
| Vega | 6 % |
| Theta | 2 % |
| Rho | 0,2 % |
| Autres variables | 10 % |

La comparaison avec ASU est très forte pour les facteurs économiquement dominants. Pour le delta, les corrélations de Pearson et de Spearman atteignent respectivement 0,9957 et 0,9970 ; pour la volatilité, elles atteignent 0,9848 et 0,9615. Les concordances sont plus faibles pour le temps et les taux, dont le poids quotidien dans le P&L est nettement moindre.

## Portée et limites

Le travail porte sur un seul sous-jacent, une famille homogène de calls américains et une fréquence quotidienne. Les résultats ne peuvent donc pas être généralisés sans validation à des portefeuilles multi-actifs ou à d’autres régimes de marché. Les prolongements proposés concernent des données plus fines, des architectures attentionnelles ou probabilistes et l’intégration de mesures comme la Value-at-Risk et l’Expected Shortfall.
