---
title: Couverture neuronale sous coûts de transaction
summary: Étude computationnelle d’une politique de couverture optimisée selon la CVaR, comparée aux deltas de Black–Scholes et de Leland sur un test Monte-Carlo préenregistré.
date: 2026-09-01
order: 2
featured: true
domain: Modélisation financière et gestion des risques
project_type: Étude computationnelle reproductible
methods: CVaR, réseaux neuronaux, Monte-Carlo, Black–Scholes, Leland et Heston
methods_label: DEEP HEDGING · CVaR · MONTE-CARLO
objective: Évaluer si une politique neuronale peut réduire les pertes extrêmes et l’intensité de négociation d’une couverture d’option lorsque chaque rééquilibrage est coûteux.
hero_image: /assets/projets/couverture-neuronale-couts-transaction/comparaison-finale.png
hero_image_alt: Comparaison finale de la CVaR et du turnover des couvertures delta et neuronale
hero_image_caption: Test final · 250 000 trajectoires simulées · coût aller simple de 25 points de base
search_terms: couverture option deep hedging CVaR expected shortfall risque de queue coûts de transaction Black Scholes Leland Heston réseau neuronal Monte Carlo finance quantitative modélisation financière
contact_subject: Projet de couverture neuronale sous coûts de transaction
comment_term: couverture-neuronale-couts-transaction
comments: true
steps:
  - title: Formuler
    description: Fixer une convention unique de P&L, de coûts et de risque, puis construire des références analytiques comparables.
  - title: Apprendre
    description: Entraîner une politique neuronale compacte qui observe la moneyness, le temps restant et sa position précédente.
  - title: Tester
    description: Geler le protocole, ouvrir une seule fois le test final et conserver les sensibilités comme les résultats défavorables.
resources:
  - label: Rapport technique
    format: PDF
    file_size: 601 Ko
    new_tab: true
    url: /assets/projets/couverture-neuronale-couts-transaction/rapport-technique.pdf
  - label: Notebook de l’étude
    format: HTML
    file_size: 1,2 Mo
    new_tab: true
    url: /assets/projets/couverture-neuronale-couts-transaction/notebook.html
  - label: Code et reproductibilité
    format: GitHub
    external: true
    url: https://github.com/manusalako/manusalako.github.io/tree/main/.research/portfolio-content-cycle
pdf_url: /assets/projets/couverture-neuronale-couts-transaction/rapport-technique.pdf
pdf_title: Rapport technique — Couverture neuronale sous coûts de transaction
pdf_pages: 10
pdf_file_size: 601 Ko
pdf_language: Français
pdf_download: false
---
## Question étudiée

Une couverture delta réduit le risque d’une option en ajustant régulièrement la position détenue dans le sous-jacent. En présence de coûts de transaction, chaque correction devient pourtant un compromis : intervenir souvent rapproche la couverture de la delta théorique, mais multiplie les frais ; intervenir moins réduit les frais, mais laisse davantage de risque non couvert.

Ce projet étudie une question précise : pour une position courte sur un call européen, une politique apprise par réseau de neurones et optimisée selon la *Conditional Value-at-Risk* (CVaR) peut-elle réduire les pertes extrêmes hors échantillon par rapport à une couverture delta discrète, à coût donné ?

> Les données de cette étude sont entièrement simulées. Les résultats décrivent une expérience contrôlée ; ils ne constituent ni une stratégie de négociation, ni une recommandation financière, ni une preuve de performance sur un marché réel.

## Cadre et protocole

Le scénario principal simule un call européen à la monnaie dans un modèle de Black–Scholes : sous-jacent initial de 100, strike de 100, maturité d’un an, volatilité de 20 %, taux sans risque de 3 % et 30 dates de rééquilibrage. Le coût proportionnel aller simple vaut 25 points de base.

Quatre stratégies sont évaluées sur les mêmes trajectoires :

- aucune couverture, comme contrôle minimal ;
- la delta de Black–Scholes recalculée à chaque date ;
- la delta de Leland, qui ajuste la volatilité pour tenir compte des frictions ;
- une politique neuronale de 1 217 paramètres, avec la log-moneyness, le temps restant et la position précédente comme variables d’état.

Pour une position courte sur l’option, le P&L terminal est défini par

$$
\Pi_T = \pi_0
+ \sum_{t=0}^{N-1} h_t(S_{t+1}-S_t)
- c\left[S_0|h_0| + \sum_{t=1}^{N-1}S_t|h_t-h_{t-1}| + S_T|h_{N-1}|\right]
-(S_T-K)^+.
$$

La perte est \(L=-\Pi_T\). Le réseau minimise une approximation différentiable de la CVaR à 95 %, qui cible la moyenne des 5 % de pertes les plus sévères. Un jeu de développement sert aux choix méthodologiques. Le checkpoint, les métriques, le coût, les graines et la taille du test sont ensuite gelés avant l’unique évaluation finale sur 250 000 trajectoires.

## Résultat confirmatoire

| Stratégie | CVaR 95 % | Écart-type du P&L | Coût moyen | Turnover |
| --- | ---: | ---: | ---: | ---: |
| Delta Black–Scholes | 1,9230 | 0,4980 | 0,6850 | 274,01 |
| Delta de Leland | 1,7202 | 0,4771 | 0,6569 | 262,75 |
| Politique neuronale | **1,5586** | 0,5439 | **0,5849** | **233,96** |

Face à Leland, la réduction appariée de CVaR vaut **0,1615**, avec un intervalle bootstrap à 95 % de **[0,1565 ; 0,1664]**. Le turnover diminue de **28,79**, soit 10,96 %. Le critère confirmatoire fixé avant le test est donc satisfait.

![Deux barres comparatives montrent que la politique neuronale obtient la CVaR et le turnover les plus faibles parmi les trois couvertures.](/assets/projets/couverture-neuronale-couts-transaction/comparaison-finale.png)

*Comparaison finale sur 250 000 trajectoires communes. Source : simulations internes documentées ; le test final n’a été ouvert qu’une fois.*
{: .figure-caption}

Ce résultat ne signifie pas que le réseau domine selon toutes les mesures. Son écart-type de P&L est supérieur de 14,00 % à celui de Leland. La politique déplace donc le compromis vers la queue de perte ciblée par l’entraînement, sans réduire toute la dispersion.

## Ce que la politique apprend

Quand le coût passe de 0 à 50 points de base sur le jeu de développement, le turnover neuronal diminue de 258,20 à 216,93. La politique apprend ainsi à rendre sa couverture plus inerte lorsque chaque ordre devient plus cher. Sa CVaR augmente néanmoins avec le coût : négocier moins limite la friction, mais ne la supprime pas.

![Deux courbes montrent une CVaR croissante et un turnover décroissant lorsque le coût de transaction augmente ; les valeurs neuronales restent inférieures à celles de Leland.](/assets/projets/couverture-neuronale-couts-transaction/sensibilite-couts.png)

*Sensibilité sur 100 000 trajectoires de développement communes par niveau de coût. Ces courbes ne réutilisent pas le test final.*
{: .figure-caption}

Une ablation confirme aussi le rôle de l’inventaire : retirer la position précédente de l’état dégrade la CVaR de 0,0160 et augmente le turnover de 13,08. L’information sur la position courante permet au réseau d’estimer le coût marginal d’un changement de couverture.

## Robustesse et résultats défavorables

La politique n’est pas robuste à tout changement de modèle. Lorsqu’une delta de Leland connaît la volatilité réellement utilisée dans la simulation, elle dépasse le réseau sous certains scénarios Black–Scholes à 15 % et 30 % de volatilité. À 25 %, l’intervalle de différence contient zéro.

Dans une grille Heston stylisée, le réseau reste meilleur dans deux scénarios à volatilité de variance modérée, devient statistiquement indistinct dans un troisième et perd son avantage dans le scénario \(\xi=0{,}60,\rho=0\). Ce résultat défavorable est conservé parce qu’il montre qu’une information d’état absente du réseau peut annuler son avantage.

![Intervalles de confiance des différences de CVaR : l’avantage neuronal change de signe selon la volatilité Black–Scholes et devient négatif dans un scénario Heston.](/assets/projets/couverture-neuronale-couts-transaction/robustesse.png)

*Analyses de robustesse sur les jeux de développement. Un point positif indique une CVaR plus faible pour le réseau ; un point négatif favorise la référence informée.*
{: .figure-caption}

## Portée et limites

L’expérience porte sur une seule option, une échéance, une fréquence de rééquilibrage et un coût linéaire constant. Le scénario confirmatoire repose sur un modèle Black–Scholes à volatilité connue, tandis que la grille Heston reste stylisée. Le réseau central provient d’une seule graine d’apprentissage ; les intervalles bootstrap mesurent l’incertitude Monte-Carlo conditionnelle aux stratégies entraînées, pas la variabilité entre entraînements.

Une extension crédible devrait traiter plusieurs strikes et maturités, des coûts non linéaires, une volatilité latente estimée, plusieurs graines d’apprentissage et une calibration temporelle sur données réelles avec un nouveau test indépendant.

## Reproductibilité

Le noyau scientifique comporte 27 tests unitaires. Le notebook et le rapport relisent les résultats JSON existants et vérifient leurs empreintes avant d’afficher les tableaux. Le test final est définitivement fermé : son empreinte SHA-256 commence par `966e7ddaf7e546d…` ; la valeur intégrale reste consignée dans le rapport et le manifeste, et le fichier ne doit pas être régénéré.
