# Matrice de littérature vérifiée

Vérification initiale : 1er septembre 2026. Les liens pointent vers l’éditeur, l’institution ou une prépublication identifiable.

| Référence | Résultat ou rôle retenu | Usage prévu | Lien vérifié |
| --- | --- | --- | --- |
| Black & Scholes (1973) | Dérivation d’un prix d’option par absence d’arbitrage dans un cadre idéal sans frictions. | Prix initial, delta de référence et contrôle sans coûts. | [DOI 10.1086/260062](https://doi.org/10.1086/260062) |
| Leland (1985) | Les coûts invalident la réplication continue sans friction ; proposition d’un ajustement dépendant du coût et du pas de rééquilibrage. | Référence classique sous coûts, après vérification de la convention exacte. | [DOI 10.1111/j.1540-6261.1985.tb02383.x](https://doi.org/10.1111/j.1540-6261.1985.tb02383.x) |
| Hutchinson, Lo & Poggio (1994) | Les réseaux d’apprentissage peuvent estimer des formules de prix et servir à la couverture hors échantillon. | Contexte historique de l’apprentissage neuronal pour les dérivés. | [DOI 10.1111/j.1540-6261.1994.tb00081.x](https://doi.org/10.1111/j.1540-6261.1994.tb00081.x) |
| Rockafellar & Uryasev (2000) | Formulation d’optimisation de la CVaR à partir d’une variable de seuil et de pertes excédentaires. | Fonction objectif neuronale et définition de la mesure de queue. | [DOI 10.21314/JOR.2000.038](https://doi.org/10.21314/JOR.2000.038) |
| Efron (1979) | Introduction du bootstrap comme méthode de rééchantillonnage pour approximer la distribution d’un estimateur. | Incertitude conditionnelle des écarts de CVaR sur les trajectoires de test indépendantes. | [DOI 10.1214/aos/1176344552](https://doi.org/10.1214/aos/1176344552) |
| Buehler, Gonon, Teichmann & Wood (2019) | Cadre de deep hedging sous frictions, contraintes et mesures convexes du risque ; illustration synthétique sous Heston. | Référence méthodologique principale et limites de la réplication. | [Article](https://doi.org/10.1080/14697688.2019.1571683), [arXiv:1802.03042](https://arxiv.org/abs/1802.03042) |
| Kolm & Ritter (2019) | Formulation de la réplication dynamique comme problème d’apprentissage par renforcement sous coûts non linéaires. | Comparaison conceptuelle avec une approche valeur-action ; non reproduite intégralement. | [DOI 10.3905/jfds.2019.1.1.159](https://doi.org/10.3905/jfds.2019.1.1.159) |
| Heston (1993) | Modèle de volatilité stochastique avec corrélation entre variance et rendement du sous-jacent. | Scénario optionnel de robustesse hors modèle. | [DOI 10.1093/rfs/6.2.327](https://doi.org/10.1093/rfs/6.2.327) |
| Engle & Manganelli (2004) | Modélisation autorégressive directe du quantile conditionnel et test dynamique de spécification. | Fondation du sujet candidat B ; non utilisée comme résultat du projet A. | [DOI 10.1198/073500104000000370](https://doi.org/10.1198/073500104000000370) |
| Markowitz (1952) | Formulation moyenne–variance de la sélection de portefeuille. | Fondation du sujet candidat C. | [DOI 10.1111/j.1540-6261.1952.tb01525.x](https://doi.org/10.1111/j.1540-6261.1952.tb01525.x) |
| Mohajerin Esfahani & Kuhn (2018) | Programmes robustes fondés sur des boules de Wasserstein et application à une allocation moyenne–risque. | Fondation du sujet candidat C. | [DOI 10.1007/s10107-017-1172-1](https://doi.org/10.1007/s10107-017-1172-1) |

## Ce que la littérature ne permet pas encore d’affirmer

- Aucune supériorité générale d’une politique neuronale ne sera supposée avant les expériences.
- Un résultat sous trajectoires simulées ne prouve pas une amélioration en marché réel.
- Une CVaR empirique plus faible sur une seule graine n’est pas une conclusion robuste.
- Le projet ne cherchera pas à reproduire toutes les architectures ni tous les théorèmes de Buehler et al.
