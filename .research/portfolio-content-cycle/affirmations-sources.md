# Registre des affirmations et preuves

| Affirmation envisagée | Statut | Preuve ou source exigée |
| --- | --- | --- |
| Les coûts de transaction empêchent d’assimiler la réplication continue réelle au cadre sans friction. | Sourcée | Leland (1985), DOI 10.1111/j.1540-6261.1985.tb02383.x. |
| Une stratégie neuronale peut représenter une politique de couverture sous mesure convexe du risque. | Sourcée | Buehler et al. (2019), DOI 10.1080/14697688.2019.1571683. |
| La CVaR empirique peut être optimisée avec la représentation de Rockafellar–Uryasev. | Sourcée | Rockafellar & Uryasev (2000), DOI 10.21314/JOR.2000.038. |
| La couverture delta réduit fortement la dispersion et la CVaR face à l’absence de couverture dans le pilote sans coûts. | Pilote validé, non final | `pilot/results.json` et `pilot/validation.txt`. À confirmer par l’étude principale et la convergence en nombre de pas. |
| L’ajustement de Leland réduit la CVaR par rapport à la delta non ajustée dans les scénarios internes à 10, 25 et 50 points de base. | Résultat interne provisoire | `benchmarks/classical-baselines.json`, 100 000 trajectoires communes. À confirmer par intervalles et sensibilités. |
| Le réseau réduit son turnover lorsque le coût augmente. | Résultat de développement, une graine par coût | Turnover neuronal : 258,20, 246,85, 233,78 et 216,93 pour 0, 10, 25 et 50 points de base ; valeurs inférieures à Leland dans chaque scénario. À répéter sur plusieurs graines aux extrêmes. |
| Le réseau réduit la CVaR par rapport à la delta ou à Leland. | Résultat de développement appuyé, non final | À 2 000 époques, amélioration face à Leland de 0,1068, 0,1171, 0,1599 et 0,2815 pour 0, 10, 25 et 50 points de base ; chaque intervalle bootstrap est strictement positif. Les sensibilités hors modèle et le test final restent à faire. |
| Optimiser la CVaR ne revient pas à minimiser la variance. | Résultat de développement | L’écart-type du P&L neuronal dépasse celui de Leland aux quatre coûts alors que sa CVaR est plus faible. Sans coûts, la médiane de perte est moins bonne mais les quantiles 99 % et 99,5 % sont meilleurs. |
| La politique apprise reste proche d’une delta tout en tenant compte de l’inventaire précédent. | Diagnostic interne | Corrélation des positions avec Leland : 0,9956 ; écart absolu moyen : 0,0286. La grille d’état montre une inertie mesurable autour de la delta, à confirmer par visualisation et ablation. |
| La stratégie reste robuste sous volatilité différente ou Heston. | Non établie | Expérience hors distribution dédiée. |

Une affirmation marquée « non établie » ne doit pas apparaître comme un résultat sur le portfolio.
