# Registre des affirmations et preuves

| Affirmation envisagée | Statut | Preuve ou source exigée |
| --- | --- | --- |
| Les coûts de transaction empêchent d’assimiler la réplication continue réelle au cadre sans friction. | Sourcée | Leland (1985), DOI 10.1111/j.1540-6261.1985.tb02383.x. |
| Une stratégie neuronale peut représenter une politique de couverture sous mesure convexe du risque. | Sourcée | Buehler et al. (2019), DOI 10.1080/14697688.2019.1571683. |
| La CVaR empirique peut être optimisée avec la représentation de Rockafellar–Uryasev. | Sourcée | Rockafellar & Uryasev (2000), DOI 10.21314/JOR.2000.038. |
| La couverture delta réduit fortement la dispersion et la CVaR face à l’absence de couverture dans le pilote sans coûts. | Pilote validé, non final | `pilot/results.json` et `pilot/validation.txt`. À confirmer par l’étude principale et la convergence en nombre de pas. |
| L’ajustement de Leland réduit la CVaR par rapport à la delta non ajustée dans les scénarios internes à 10, 25 et 50 points de base. | Résultat interne provisoire | `benchmarks/classical-baselines.json`, 100 000 trajectoires communes. À confirmer par intervalles et sensibilités. |
| Le réseau négocie moins que la delta et Leland à 25 points de base. | Résultat interne multigraine | Turnover moyen sur cinq graines : 232,31, contre 273,78 pour la delta et 262,54 pour Leland. À vérifier aux autres niveaux de coût. |
| Le réseau réduit la CVaR par rapport à la delta ou à Leland. | Indice positif multigraine, non final | Après 1 000 époques : CVaR moyenne 1,5921 (écart-type entre graines 0,0080), contre 1,9174 pour la delta et 1,7185 pour Leland ; les cinq graines battent Leland. Il reste à quantifier l’incertitude Monte-Carlo appariée et la robustesse. |
| La stratégie reste robuste sous volatilité différente ou Heston. | Non établie | Expérience hors distribution dédiée. |

Une affirmation marquée « non établie » ne doit pas apparaître comme un résultat sur le portfolio.
