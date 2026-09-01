# Protocole initial

## Titre de travail

**Deep hedging sous coûts de transaction : compromis entre risque terminal et intensité de négociation**

## Question principale

Pour une position courte sur un call européen, une politique de couverture apprise par réseau de neurones et optimisée selon la CVaR à 95 % réduit-elle la perte extrême hors échantillon par rapport à une couverture delta discrète, à coût de transaction donné ?

## Contribution attendue

Le projet ne revendiquera pas un nouvel algorithme. Il cherchera à fournir une étude reproductible et critique de trois mécanismes :

1. l’effet des coûts proportionnels sur la couverture delta ;
2. l’arbitrage appris entre réduction du risque et réduction du turnover ;
3. la robustesse d’une politique apprise lorsque la volatilité ou le modèle générateur diffèrent de l’entraînement.

## Cadre mathématique

- Sous-jacent initial : \(S_0=100\).
- Option : call européen à la monnaie, \(K=100\).
- Échéance principale : \(T=30/252\) année.
- Taux sans risque principal : \(r=0\) afin d’isoler l’effet de couverture.
- Modèle d’entraînement : mouvement brownien géométrique avec volatilité \(\sigma=20\%\).
- Rééquilibrages principaux : 30 pas.
- Coût proportionnel symétrique : \(c\,S_t|h_t-h_{t-1}|\).
- Fermeture finale de la position incluse dans les coûts.
- Perte terminale de la position courte : opposé du P&L net de prime, gains de couverture et coûts.
- Objectif principal : CVaR empirique à 95 %, formulée via Rockafellar–Uryasev.

La prime initiale sera fixée au prix Black–Scholes du scénario d’entraînement. Cette convention sera identique pour toutes les stratégies d’une même expérience. Les résultats sépareront la moyenne du P&L, sa dispersion et les mesures de queue afin de ne pas masquer un biais moyen par une seule métrique de risque.

## Stratégies comparées

1. **Sans couverture** : référence minimale.
2. **Delta Black–Scholes discrète** : référence théorique classique.
3. **Delta ajustée aux coûts** : stratégie de Leland avec coût aller-retour \(C=2c\), donc \(\sigma_L=\sigma\sqrt{1+\sqrt{8/\pi}\,c/(\sigma\sqrt{\Delta t})}\) pour le call convexe. La prime reste commune aux stratégies dans la comparaison principale.
4. **Politique neuronale** : petit réseau partagé dans le temps recevant au minimum le log-moneyness, le temps restant et la position précédente. La sortie sera bornée pour éviter des positions irréalistes.

## Séparation des données simulées

- Génération d’entraînement avec graines documentées et renouvellement des trajectoires pendant l’optimisation.
- Ensemble de validation indépendant pour l’arrêt et le choix des hyperparamètres.
- Ensemble de développement indépendant de l’entraînement et de la validation, graine 20263000, utilisé pour les diagnostics de méthode.
- Ensemble de test final préenregistré, graine 20269000 et 250 000 trajectoires, qui ne sera généré qu’après gel de la durée, de l’architecture et des expériences principales.
- Les graines, paramètres et versions de dépendances seront enregistrés.
- La durée de référence est fixée à 2 000 époques comme budget expérimental commun. Le meilleur état est choisi uniquement sur la validation ; cette limite ne sera pas présentée comme une preuve de convergence vers l’optimum.

## Expériences principales

### E1 — contrôle sans coûts

Vérifier que la couverture delta discrète réduit fortement le risque face à l’absence de couverture lorsque \(c=0\). Cette expérience sert de test de cohérence du simulateur.

### E2 — coûts de transaction

Comparer les stratégies pour \(c\in\{0,10,25,50\}\) points de base. Mesurer la CVaR, la VaR, l’écart-type du P&L, la perte moyenne, la probabilité de perte, le coût moyen et le turnover.

### E3 — fréquence de rééquilibrage

Comparer 10, 20 et 30 pas. Tester si une fréquence plus élevée cesse d’être avantageuse lorsque les coûts augmentent.

### E4 — robustesse hors distribution

Évaluer une politique entraînée à \(20\%\) sous \(15\%\), \(25\%\) et \(30\%\) de volatilité. Si l’implémentation est stable avant la fin du jour 3, ajouter un scénario Heston clairement identifié comme test de changement de modèle.

### E5 — ablations

Retirer la position précédente de l’état, modifier la borne de position et comparer au moins deux niveaux de capacité du réseau. Rapporter les résultats négatifs.

## Métriques et incertitude

- moyenne et écart-type du P&L ;
- quantiles 1 %, 5 %, 50 %, 95 % et 99 % ;
- VaR et CVaR de la perte à 95 % ;
- probabilité d’une perte nette ;
- coût de transaction moyen ;
- turnover notionnel moyen ;
- intervalles bootstrap pour les écarts de CVaR et de coût entre stratégies ;
- temps d’entraînement et d’inférence.

## Critères de validité

- Aucun chevauchement de graines entre apprentissage, validation et test.
- Même ensemble de test pour toutes les stratégies d’une comparaison.
- Vérification analytique du prix et de la delta Black–Scholes.
- Test de convergence quand le nombre de pas augmente sans coûts.
- Réplication sur plusieurs graines d’apprentissage.
- Conclusions limitées au cadre simulé ; aucune affirmation sur une performance de marché réelle.

## Risques méthodologiques

- Instabilité de l’optimisation de la CVaR sur peu d’observations de queue.
- Comparaison injuste si la stratégie neuronale exploite une prime ou une information différente.
- Surapprentissage au modèle Black–Scholes.
- Définition ambiguë du coût aller-retour et de la liquidation terminale.
- Coût de calcul trop élevé sur CPU.
- Résultat apparemment favorable dû à une graine unique.

## Plan de réduction des risques

- Commencer par un pilote vectorisé de couverture delta.
- Fixer une convention de P&L unique avant l’apprentissage.
- Employer des lots assez grands pour la CVaR et répéter les entraînements.
- Initialiser le seuil auxiliaire \(\eta\) sur le quantile d’un lot d’entraînement indépendant de la validation, puis l’optimiser avec son propre taux d’apprentissage.
- Conserver un modèle neuronal compact.
- Prioriser les expériences E1 à E4 ; l’ablation complète est secondaire.
