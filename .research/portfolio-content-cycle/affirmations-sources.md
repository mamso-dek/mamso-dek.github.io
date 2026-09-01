# Registre des affirmations et preuves

| Affirmation envisagée | Statut | Preuve ou source exigée |
| --- | --- | --- |
| Les coûts de transaction empêchent d’assimiler la réplication continue réelle au cadre sans friction. | Sourcée | Leland (1985), DOI 10.1111/j.1540-6261.1985.tb02383.x. |
| Une stratégie neuronale peut représenter une politique de couverture sous mesure convexe du risque. | Sourcée | Buehler et al. (2019), DOI 10.1080/14697688.2019.1571683. |
| La CVaR empirique peut être optimisée avec la représentation de Rockafellar–Uryasev. | Sourcée | Rockafellar & Uryasev (2000), DOI 10.21314/JOR.2000.038. |
| La couverture delta réduit fortement la dispersion et la CVaR face à l’absence de couverture dans le pilote sans coûts. | Pilote validé, non final | `pilot/results.json` et `pilot/validation.txt`. À confirmer par l’étude principale et la convergence en nombre de pas. |
| L’ajustement de Leland réduit la CVaR par rapport à la delta non ajustée dans les scénarios internes à 10, 25 et 50 points de base. | Résultat interne provisoire | `benchmarks/classical-baselines.json`, 100 000 trajectoires communes. À confirmer par intervalles et sensibilités. |
| Le réseau négocie moins que la delta à 25 points de base. | Indice interne, non final | À 300 époques : turnover moyen 224,85 contre 273,78 pour la delta. À répéter sur plusieurs graines et niveaux de coût. |
| Le réseau réduit la CVaR par rapport à la delta ou à Leland. | Non établie ; première expérience contraire | À 300 époques et 25 points de base : CVaR 2,0938 contre 1,9174 pour la delta et 1,7185 pour Leland. Prolonger l’apprentissage et répéter les graines avant toute conclusion. |
| La stratégie reste robuste sous volatilité différente ou Heston. | Non établie | Expérience hors distribution dédiée. |

Une affirmation marquée « non établie » ne doit pas apparaître comme un résultat sur le portfolio.
