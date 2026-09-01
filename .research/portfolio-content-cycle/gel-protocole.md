# Gel du protocole avant test final

**Date du gel :** 1er septembre 2026

**Statut :** gelé après les diagnostics de développement, avant toute génération du test final

Ce document fixe le modèle, les données et les règles d'analyse qui seront utilisés lors de l'unique ouverture du test final. Les choix ci-dessous ne devront pas être modifiés après consultation des résultats finaux.

## Question confirmatoire

Sur 250 000 trajectoires GBM indépendantes, une politique neuronale entraînée pour minimiser la CVaR à 95 % réduit-elle la CVaR de la perte terminale d'un vendeur de call par rapport à la delta de Leland, lorsque les deux stratégies supportent le même coût proportionnel et partent de la même prime ?

L'amélioration appariée est définie par

\[
\Delta_{\mathrm{CVaR}}
=
\operatorname{CVaR}_{95\%}(L_{\mathrm{Leland}})
-
\operatorname{CVaR}_{95\%}(L_{\mathrm{réseau}}).
\]

Une valeur positive favorise le réseau. Le résultat confirmatoire sera considéré favorable uniquement si la borne inférieure de l'intervalle bootstrap bilatéral à 95 % de \(\Delta_{\mathrm{CVaR}}\) est strictement positive. La comparaison avec la delta Black--Scholes non ajustée sera secondaire.

## Scénario final immuable

| Élément | Valeur gelée |
| --- | ---: |
| Processus | mouvement brownien géométrique |
| \(S_0\) | 100 |
| Strike \(K\) | 100 |
| Échéance \(T\) | \(30/252\) année |
| Taux sans risque | 0 |
| Volatilité | 20 % |
| Rééquilibrages | 30 |
| Coût proportionnel aller simple | 25 points de base |
| Fermeture finale | incluse dans les coûts |
| Graine du test | 20269000 |
| Taille du test | 250 000 trajectoires |
| Niveau de CVaR | 95 % |

La prime commune demeure le prix Black--Scholes du call dans le scénario ci-dessus. Les stratégies seront évaluées sur exactement les mêmes trajectoires.

## Politique neuronale gelée

- réseau partagé entre les dates, avec deux couches cachées de 32 neurones et activations SiLU ;
- état : log-moneyness normalisé, temps restant normalisé et inventaire précédent normalisé ;
- sortie : `1.25 * sigmoid`, donc position dans \([0;1{,}25]\) ;
- nombre de paramètres : 1 217 ;
- entraînement : 2 000 époques, lots de 8 192 trajectoires renouvelées ;
- validation : 50 000 trajectoires indépendantes ;
- optimiseur : Adam, taux \(10^{-3}\) pour le réseau et \(5\times10^{-3}\) pour \(\eta\) ;
- écrêtage de la norme du gradient : 5 ;
- graines : modèle 20260911, entraînement à partir de 20261000, validation 20262000 ;
- meilleur état retenu : époque 2 000, uniquement selon la CVaR de validation ;
- checkpoint : `checkpoints/convergence-2000.pt` ;
- SHA-256 du checkpoint : `d47f58cf3df225148688c74349cee8988e2750c7067be4f4d7dd9f3d4b6ccd8a`.

La politique ne sera pas réentraînée pour le test final.

## Références et mesures

Les quatre stratégies seront calculées : absence de couverture, delta Black--Scholes discrète, delta de Leland et politique neuronale gelée.

Les mesures suivantes seront produites sans changer leur définition :

- moyenne et écart-type du P&L ;
- probabilité de perte ;
- VaR et CVaR de la perte à 95 % ;
- quantiles de perte 1 %, 5 %, 50 %, 95 %, 99 % et 99,5 % ;
- coût de transaction moyen ;
- turnover notionnel moyen.

Le bootstrap apparié utilisera 5 000 réplications. Les graines, fixées avant le test, sont 20269101 pour la CVaR face à Leland, 20269102 pour la CVaR face à la delta, puis 20269103 à 20269106 pour les coûts et turnovers face aux deux références. Il estimera en priorité l'écart de CVaR entre réseau et Leland, puis les écarts secondaires face à la delta et les écarts de coût et de turnover.

## Décision sur la borne de position

La sensibilité de développement compare les bornes 1,00, 1,25 et 1,50. La borne 1,00 est active sur 2,64 % des décisions et améliore la CVaR de développement de 0,00285 face à 1,25, tout en augmentant le turnover de 0,55. La borne 1,50 reste inactive ; son maximum observé vaut 1,139.

La borne 1,25 est conservée parce qu'elle appartient au modèle central préenregistré et qu'elle laisse une marge sans être atteinte. Choisir 1,00 après lecture du développement introduirait un ajustement rétrospectif pour un gain de CVaR d'environ 0,18 %, estimé sur une seule graine d'apprentissage. Le résultat favorable à 1,00 sera rapporté comme sensibilité, pas utilisé pour sélectionner le modèle final.

## Règles après ouverture

1. Le test final est généré une seule fois avec la graine et la taille fixées.
2. Tous les résultats prévus sont enregistrés, qu'ils soient favorables, nuls ou défavorables.
3. Aucun changement d'architecture, de checkpoint, de référence ou de métrique n'est autorisé après consultation des chiffres.
4. Une correction purement technique doit être documentée. Si des résultats ont déjà été lus, la nouvelle exécution ne pourra plus être qualifiée de test final intact.
5. Les sensibilités déjà conduites sur le développement restent exploratoires et ne sont pas mélangées au résultat confirmatoire.

## Contrôles requis juste avant ouverture

- vérifier l'empreinte du checkpoint ;
- exécuter tous les tests unitaires et `pip check` ;
- vérifier l'absence de la graine 20269000 dans les artefacts existants ;
- inspecter le script final sans l'exécuter ;
- enregistrer les versions logicielles, la durée et l'empreinte du fichier de résultats.

Le script `benchmarks/final_evaluation.py` fonctionne en audit seul par défaut. L'ouverture exige simultanément l'option `--open-final-test`, la phrase exacte consignée dans le script, un dépôt propre, le checkpoint attendu et l'absence de `final-test-opening.json` et `final-test-results.json`. Le marqueur est créé avant la simulation afin qu'une interruption ne puisse pas provoquer une seconde ouverture silencieuse.
