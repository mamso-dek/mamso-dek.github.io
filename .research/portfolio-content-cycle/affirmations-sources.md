# Registre des affirmations et preuves

| Affirmation envisagée | Statut | Preuve ou source exigée |
| --- | --- | --- |
| Les coûts de transaction empêchent d’assimiler la réplication continue réelle au cadre sans friction. | Sourcée | Leland (1985), DOI 10.1111/j.1540-6261.1985.tb02383.x. |
| Une stratégie neuronale peut représenter une politique de couverture sous mesure convexe du risque. | Sourcée | Buehler et al. (2019), DOI 10.1080/14697688.2019.1571683. |
| La CVaR empirique peut être optimisée avec la représentation de Rockafellar–Uryasev. | Sourcée | Rockafellar & Uryasev (2000), DOI 10.21314/JOR.2000.038. |
| La couverture delta réduit fortement la dispersion et la CVaR face à l’absence de couverture dans le pilote sans coûts. | Pilote validé, non final | `pilot/results.json` et `pilot/validation.txt`. À confirmer par l’étude principale et la convergence en nombre de pas. |
| Le réseau négocie moins que la delta lorsque les coûts augmentent. | Non établie | Mesures hors échantillon sur plusieurs graines. |
| Le réseau réduit la CVaR par rapport à la delta. | Non établie | Test final indépendant, intervalle bootstrap et sensibilité aux graines. |
| La stratégie reste robuste sous volatilité différente ou Heston. | Non établie | Expérience hors distribution dédiée. |

Une affirmation marquée « non établie » ne doit pas apparaître comme un résultat sur le portfolio.
