# Journal d’exécution

## 2026-09-01 — Exécution 1

### Travail réalisé

- Inspection du dépôt, de son historique et des contenus réels.
- Constat : le dépôt local est propre mais possède un commit non publié consacré à la note sur l’exponentielle.
- Inventaire : un projet réel sur l’attribution du P&L, deux manuscrits associés et une note pédagogique.
- Comparaison pondérée de trois sujets candidats.
- Sélection d’un projet de deep hedging sous coûts de transaction.
- Vérification initiale de dix références originales ou institutionnelles.
- Définition de la question, des baselines, des métriques, de la séparation des simulations et des contrôles de robustesse.
- Vérification de l’environnement : NumPy, SciPy, pandas et scikit-learn sont disponibles dans le runtime scientifique ; PyTorch et les outils Jupyter n’y sont pas encore disponibles.

### Décisions

- Utiliser des données simulées et les identifier explicitement comme telles.
- Ne pas revendiquer de contribution algorithmique originale.
- Prioriser une politique compacte et une étude robuste plutôt qu’une architecture spectaculaire.
- Garder le projet non publié jusqu’à la validation finale du jour 5.
- Ne pas pousser le commit de la note sur l’exponentielle sans autorisation explicite séparée.

### Problèmes ouverts

- Installer un environnement local reproductible avec PyTorch et nbformat.
- Vérifier la convention et la formule exactes de la stratégie de Leland avant implémentation.
- Fixer la taille des simulations après mesure du coût CPU.

### Prochain jalon

Exécuter et valider le pilote de couverture delta, écrire les tests de cohérence, puis préparer l’environnement de deep learning.

### Résultat du pilote classique

Le pilote a été exécuté sur 50 000 trajectoires Black–Scholes indépendantes, 30 pas et une échéance de 30 jours ouvrés.

- Sans coûts, la delta fait passer l’écart-type du P&L de 4,2267 à 0,4294 et la CVaR de la perte à 95 % de 12,3742 à 0,9926.
- La moyenne du P&L delta sans coûts est de -0,0005, cohérente avec zéro à la précision Monte-Carlo du pilote.
- Les coûts moyens de la delta sont de 0,2738, 0,6845 et 1,3689 pour 10, 25 et 50 points de base.
- La CVaR de la delta augmente de 0,9926 sans coûts à 2,8755 à 50 points de base. Le problème d’optimisation n’est donc pas artificiel : réduire les échanges peut avoir une valeur mesurable.
- Ces valeurs sont exploratoires. Elles valident la convention de P&L et l’ordre de grandeur, pas la supériorité d’une stratégie neuronale.

Les contrôles automatisés vérifient la cohérence de la prime, la neutralité Monte-Carlo approximative, la réduction du risque sans coûts, l’identité coût = taux × turnover et la monotonie de la CVaR delta avec le coût. Le dossier `.research` a aussi été confirmé absent du site Jekyll généré.

### Prochain jalon révisé

Préparer un environnement PyTorch reproductible, confirmer la formule de Leland dans la convention adoptée et écrire les tests unitaires du simulateur avant tout apprentissage.

## 2026-09-01 — Exécution 2

### Travail réalisé

- Création d’un environnement PyTorch reproductible sur Python 3.12.13 et génération d’un verrou complet dans un environnement propre, sans dépendance locale héritée.
- Vérification de PyTorch 2.13.0 sur CPU et MPS, du fonctionnement des tenseurs MPS et de la cohérence des dépendances.
- Fixation de la convention de coût : le projet utilise un coût aller simple \(cS|\Delta h|\), liquidation finale incluse ; le coût aller-retour de Leland est donc \(C=2c\).
- Implémentation du simulateur Black–Scholes, du prix et de la delta analytiques, de la volatilité de Leland, du P&L différentiable et de l’objectif CVaR de Rockafellar–Uryasev.
- Implémentation d’une politique neuronale compacte partagée dans le temps, conditionnée par le log-moneyness, le temps restant et la position précédente.
- Initialisation du seuil auxiliaire de CVaR sur un lot d’entraînement indépendant, afin de ne pas utiliser la validation pour calibrer l’optimisation.
- Ajout et validation de 11 tests couvrant la simulation, les identités de coût, les références analytiques, la CVaR, la différentiabilité et une boucle courte d’apprentissage.
- Comparaison d’exécution CPU/MPS et construction des références classiques sur 100 000 trajectoires de test communes.

### Résultats intermédiaires

Sur 20 époques, le CPU est légèrement plus rapide que MPS (0,764 s contre 0,869 s) et l’écart maximal entre métriques neuronales est de \(7,63\times10^{-6}\). Le CPU devient donc le périphérique de référence.

À 25 points de base de coût aller simple, sur 100 000 trajectoires indépendantes :

- delta Black–Scholes : CVaR 95 % de 1,9174, coût moyen de 0,6845 et turnover notionnel de 273,78 ;
- delta de Leland : CVaR 95 % de 1,7185, coût moyen de 0,6564 et turnover de 262,54 ;
- réseau après 300 époques : CVaR 95 % de 2,0938, coût moyen de 0,5621 et turnover de 224,85.

Le résultat neuronal est donc mitigé et non publiable en l’état. Le réseau apprend une politique moins coûteuse, mais il ne compense pas encore cette économie par une réduction suffisante du risque de queue. La validation continue de s’améliorer à l’époque 300 et le seuil appris η reste supérieur à la VaR empirique, ce qui indique que l’optimisation n’a pas convergé.

Les références classiques montrent aussi que Leland améliore la CVaR de la delta non ajustée aux coûts testés : 10, 25 et 50 points de base. Cette observation reste interne tant que les incertitudes et sensibilités ne sont pas calculées.

### Décisions

- Conserver le CPU comme plateforme de référence et MPS comme contrôle secondaire.
- Ne formuler aucune affirmation de supériorité du deep hedging.
- Prolonger l’apprentissage plutôt que modifier le jeu de test ou sélectionner une comparaison avantageuse.
- Garder l’intégralité de ce travail hors du site public jusqu’aux contrôles finaux.

### Prochain jalon

Lancer des apprentissages de 600 à 1 000 époques sur plusieurs graines, vérifier la convergence de η, comparer systématiquement au benchmark de Leland et examiner la forme de la politique ainsi que le turnover. Les expériences de robustesse ne commenceront qu’après stabilisation de l’apprentissage principal.

## 2026-09-01 — Exécution 3

### Travail réalisé

- Réexécution complète du premier apprentissage sur 1 000 époques, au lieu du pilote de 300 époques, dans la configuration centrale à 25 points de base.
- Création d’un protocole multigraine reproductible : cinq initialisations du réseau et cinq flux d’entraînement distincts, avec validation commune de 50 000 trajectoires et test commun indépendant de 100 000 trajectoires.
- Conservation séparée des graines, du meilleur état de validation, de η, des métriques de test et d’un historique échantillonné de convergence.
- Comparaison systématique au même prix initial et sur les mêmes trajectoires avec la delta Black–Scholes et la delta ajustée de Leland.

### Résultats intermédiaires

Les CVaR à 95 % hors échantillon des cinq réseaux sont 1,5910, 1,5930, 1,5977, 1,5792 et 1,5995. Leur moyenne est de 1,5921 et leur écart-type entre graines de 0,0080. Les cinq réplications font mieux que Leland, dont la CVaR vaut 1,7185 sur ce test, ainsi que la delta classique à 1,9174.

L’amélioration moyenne de CVaR par rapport à Leland est de 0,1264, soit 7,36 % dans ce scénario. Le coût de transaction moyen des réseaux est de 0,5808 contre 0,6564 pour Leland, et leur turnover notionnel moyen de 232,31 contre 262,54. Le gain ne provient donc pas d’une multiplication des échanges.

Les meilleurs états apparaissent entre les époques 992 et 999. Le seuil η est désormais proche de la VaR de validation : l’écart absolu moyen est de 0,0032. Cela corrige le diagnostic de l’exécution précédente, où η n’avait pas convergé. La proximité du meilleur état avec la limite de 1 000 époques impose toutefois un contrôle plus long avant de considérer la convergence comme acquise.

### Interprétation prudente

La stabilité entre graines montre que le résultat n’est pas lié à une initialisation heureuse. Elle ne mesure toutefois pas l’incertitude Monte-Carlo, car toutes les stratégies sont comparées sur le même jeu de test. Elle ne démontre pas non plus une robustesse à d’autres coûts, maturités, volatilités ou dynamiques de marché.

### Décisions

- Remplacer le constat négatif à 300 époques par un résultat positif mais explicitement provisoire à 1 000 époques.
- Ne rien intégrer au portfolio public à ce stade.
- Conserver les comparaisons appariées sur des trajectoires communes.
- Échantillonner les historiques enregistrés afin de garder les points de convergence utiles sans stocker 5 000 lignes redondantes.

### Prochain jalon

Produire les P&L trajectoire par trajectoire pour une analyse bootstrap appariée, prolonger au moins une réplication au-delà de 1 000 époques et construire des diagnostics de politique. Ensuite seulement, lancer les sensibilités au coût et aux paramètres de marché.

## 2026-09-01 — Exécution 4

### Travail réalisé

- Ajout d’une estimation de CVaR indépendante de PyTorch et d’un bootstrap non paramétrique apparié ; trois nouveaux tests portent le total à 14 tests validés.
- Réentraînement déterministe de la première graine pendant 1 500 époques, avec validation sur 50 000 trajectoires et évaluation sur les 100 000 trajectoires de test déjà fixées.
- Conservation locale du meilleur état du réseau et enregistrement des paramètres, graines, métriques, historiques échantillonnés et diagnostics.
- Calcul de 2 000 réplications bootstrap, en réutilisant les mêmes indices de trajectoires pour le réseau et chaque référence.
- Construction d’une grille de politique selon le spot, le temps restant et l’inventaire précédent, puis comparaison trajectoire par trajectoire à Leland.

### Résultats de convergence

Le meilleur état de validation apparaît à l’époque 1 500. Sa CVaR de validation est de 1,5765 et η vaut 1,3649, proche de la VaR de validation à 1,3685. Sur le test indépendant :

- réseau : CVaR 1,5682, coût moyen 0,5838 et turnover 233,52 ;
- Leland : CVaR 1,7185, coût moyen 0,6564 et turnover 262,54 ;
- delta Black–Scholes : CVaR 1,9174, coût moyen 0,6845 et turnover 273,78.

La réduction ponctuelle de CVaR face à Leland est donc de 0,1503, soit environ 8,74 %, avec environ 11 % de turnover en moins.

### Incertitude appariée

L’intervalle percentile à 95 % de l’amélioration de CVaR face à Leland est [0,1425 ; 0,1578], avec une erreur-type bootstrap de 0,0039. Les 2 000 réplications donnent une amélioration positive. Face à la delta classique, l’amélioration est de 0,3492 et son intervalle à 95 % de [0,3388 ; 0,3607].

Cette inférence quantifie uniquement l’incertitude due aux trajectoires de test, conditionnellement au réseau entraîné et au modèle Black–Scholes simulé. Elle n’inclut ni l’incertitude de spécification ni un changement de régime de marché. La stabilité d’optimisation est traitée séparément par les cinq graines de l’exécution précédente.

### Diagnostic de la politique

Les positions neuronales ont une corrélation de 0,9956 avec la delta de Leland et un écart absolu moyen de 0,0286. La politique n’est donc pas une règle opaque sans rapport avec la théorie : elle reste globalement delta-like.

L’inventaire précédent modifie néanmoins l’ajustement. Par exemple, à la monnaie avec 10 % du temps restant, la position cible vaut 0,4701 lorsque l’inventaire précédent est 0,25 et 0,5827 lorsqu’il est 0,75, alors que la delta de Leland vaut 0,5050 dans les deux cas. Le réseau rapproche la position de la delta sans effacer immédiatement l’inventaire, mécanisme cohérent avec une réduction des transactions.

### Limite encore ouverte

Le meilleur état se trouvant exactement à l’époque 1 500, le plateau n’est pas formellement confirmé. L’amélioration ralentit mais reste visible : la CVaR de validation passe de 1,6004 à l’époque 1 000 à 1,5765 à l’époque 1 500. Il serait prématuré de fixer 1 500 comme durée définitive sans un contrôle supplémentaire.

### Prochain jalon

Prolonger une réplication jusqu’à 2 000 époques pour confirmer le plateau, puis figer la durée d’apprentissage. Lancer ensuite l’expérience de sensibilité aux coûts, en réentraînant les politiques plutôt qu’en appliquant le même réseau à des coûts qu’il n’a pas appris.

## 2026-09-01 — Exécution 5

### Travail réalisé

- Réentraînement déterministe de la première graine pendant 2 000 époques, sans modifier l’architecture, les graines, la validation ni le scénario central.
- Comparaison des minima de validation sur les blocs 1 501–1 750 et 1 751–2 000, et estimation de la pente sur les 250 dernières époques.
- Nouveau bootstrap apparié de 2 000 réplications sur le jeu de développement.
- Correction d’un effet d’arrondi flottant qui sélectionnait 5 001 pertes au lieu des 5 000 constituant exactement 5 % de 100 000 trajectoires. Les diagnostics à 1 500 et 2 000 époques ont été recalculés ; les conclusions et les valeurs arrondies à quatre décimales ne changent pas.
- Ajout d’un test de régression sur 100 000 observations ; les 15 tests passent après correction.
- Séparation explicite entre le jeu de développement déjà consulté et un test final préenregistré mais non exécuté.

### Convergence observée

Le meilleur état apparaît de nouveau à la borne, à l’époque 2 000. La CVaR de validation passe de 1,5765 à la limite de 1 500 époques à 1,5640 à 2 000 époques, soit une amélioration absolue de 0,0125 et relative de 0,79 %. La pente estimée sur les 250 dernières époques reste négative à \(-1,83\times10^{-5}\) par époque.

L’apprentissage continue donc à progresser faiblement ; un plateau mathématique n’est pas démontré. En revanche, le gain marginal a nettement ralenti par rapport aux premières phases. Pour éviter de consacrer le cycle à une prolongation indéfinie d’un seul réseau, 2 000 époques devient le budget commun des expériences suivantes. Ce choix est un compromis expérimental, pas une affirmation d’optimalité.

### Résultat sur le jeu de développement

À 2 000 époques :

- réseau : CVaR 1,5586, coût moyen 0,5844 et turnover 233,78 ;
- Leland : CVaR 1,7185, coût moyen 0,6564 et turnover 262,54 ;
- delta Black–Scholes : CVaR 1,9174.

L’amélioration appariée face à Leland vaut 0,1599. Son intervalle bootstrap à 95 % est [0,1521 ; 0,1677], avec une erreur-type de 0,0039. Toutes les réplications bootstrap sont positives. Ce résultat reste un diagnostic de développement, non l’évaluation finale.

### Protection du test final

La graine 20263000 a été consultée à plusieurs étapes pour diagnostiquer la méthode. Elle reste indépendante de l’entraînement et de la validation, mais ne doit plus être qualifiée de test final. Elle est désormais explicitement désignée comme jeu de développement.

Le test final est préenregistré avec la graine 20269000 et 250 000 trajectoires. Il ne sera généré qu’après gel de la durée, de l’architecture et du plan de sensibilité. Cette séparation limite le risque de sélectionner implicitement la méthode en fonction de son résultat final.

### Prochain jalon

Exécuter la sensibilité aux coûts aller simple de 0, 10, 25 et 50 points de base. Chaque politique doit être réentraînée avec son propre coût sous le budget commun de 2 000 époques. Les comparaisons utiliseront le jeu de développement ; le test final restera fermé.

## 2026-09-01 — Exécution 6

### Travail réalisé

- Réentraînement complet de politiques distinctes pour 0, 10 et 50 points de base, avec 2 000 époques chacune ; réutilisation exacte du checkpoint central à 25 points de base.
- Utilisation de nombres aléatoires communs entre scénarios : mêmes graines d’initialisation, d’entraînement, de validation et de développement.
- Comparaison à la delta Black–Scholes, à Leland et à l’absence de couverture sur 100 000 trajectoires de développement.
- Calcul de 1 000 réplications bootstrap appariées par coût.
- Ajout des quantiles de perte 50 %, 90 %, 95 %, 99 % et 99,5 % afin de ne pas interpréter la CVaR sans examiner la forme de la distribution.
- Conservation des historiques échantillonnés et des checkpoints privés ; le test final n’a pas été ouvert.

### Résultats par coût

| Coût aller simple | CVaR réseau | CVaR Leland | Amélioration | IC bootstrap 95 % | Turnover réseau | Turnover Leland |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 pb | 0,8946 | 1,0014 | 0,1068 | [0,0997 ; 0,1143] | 258,20 | 273,78 |
| 10 pb | 1,1696 | 1,2867 | 0,1171 | [0,1103 ; 0,1246] | 246,85 | 268,90 |
| 25 pb | 1,5586 | 1,7185 | 0,1599 | [0,1528 ; 0,1672] | 233,78 | 262,54 |
| 50 pb | 2,1628 | 2,4443 | 0,2815 | [0,2729 ; 0,2903] | 216,93 | 253,85 |

Les quatre intervalles sont strictement positifs sur le jeu de développement. L’avantage absolu de CVaR augmente avec le coût, surtout entre 25 et 50 points de base. En parallèle, le turnover neuronal diminue régulièrement lorsque le coût appris augmente. La politique utilise donc bien l’inventaire précédent pour négocier moins lorsque les frictions deviennent plus pénalisantes.

### Forme de la distribution

Le réseau ne domine pas Leland selon toutes les mesures. Son écart-type de P&L est plus élevé dans les quatre scénarios : par exemple 0,4921 contre 0,4302 sans coûts, et 0,5989 contre 0,5460 à 50 points de base. C’est cohérent avec l’objectif retenu, qui cible la queue gauche du P&L et non la variance globale.

Sans coûts, la perte médiane du réseau vaut 0,0597 contre -0,0063 pour la delta, mais le quantile de perte à 99 % baisse de 1,1678 à 1,0091. À 50 points de base, le réseau améliore à la fois la médiane de perte, 1,1561 contre 1,2587 pour Leland, et le quantile 99 %, 2,2872 contre 2,6196. L’intérêt de la politique devient donc plus général lorsque les coûts sont élevés.

### Limites

La courbe de coût repose sur une seule graine d’apprentissage par scénario, sauf le scénario central dont la stabilité multigraine a déjà été vérifiée à 1 000 époques. Les minima de validation restent proches de la limite de calcul, entre les époques 1 972 et 2 000. Les résultats montrent une structure cohérente, mais les scénarios extrêmes devront être répétés avant la conclusion finale.

### Prochain jalon

Tester 10, 20 et 30 dates de rééquilibrage avec réentraînement au coût central, puis évaluer la politique centrale sous des volatilités de 15 %, 25 % et 30 %. Conserver la graine finale 20269000 fermée. Répliquer ensuite les coûts 0 et 50 points de base sur des graines supplémentaires si la structure se maintient.

## 2026-09-01 — Exécution 7

### Travail réalisé

- Réentraînement complet de politiques à 10 et 20 dates de rééquilibrage sous un coût aller simple de 25 points de base, avec le budget commun de 2 000 époques ; réutilisation du checkpoint central à 30 pas.
- Construction de 100 000 trajectoires de développement couplées sur une grille fine commune de 60 pas, puis sous-échantillonnage exact aux fréquences 10, 20 et 30. Les écarts de CVaR entre fréquences sont ainsi appariés trajectoire par trajectoire.
- Évaluation de la politique centrale figée, entraînée à 20 % de volatilité, dans quatre scénarios à 15 %, 20 %, 25 % et 30 %, sans lui transmettre la volatilité réelle du scénario.
- Comparaison avec deux familles de références classiques : des deltas figées à 20 % et des deltas informées de la volatilité du scénario. Le terme « oracle » a été écarté, car connaître la volatilité ne rend pas la règle de Leland optimale pour la CVaR.
- Conservation d’une prime commune calculée à 20 % dans chaque comparaison hors distribution. Ce décalage commun modifie le niveau absolu des pertes entre scénarios, mais pas l’écart de CVaR entre stratégies au sein d’un scénario.
- Calcul de 1 000 réplications bootstrap appariées par comparaison. Le test final préenregistré n’a pas été généré.

### Fréquence de rééquilibrage

| Nombre de pas | CVaR réseau | CVaR Leland | Amélioration face à Leland | IC bootstrap 95 % | Turnover réseau | Turnover Leland |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 2,0602 | 2,2441 | 0,1839 | [0,1728 ; 0,1950] | 178,24 | 192,74 |
| 20 | 1,6973 | 1,8667 | 0,1694 | [0,1611 ; 0,1781] | 211,97 | 233,28 |
| 30 | 1,5597 | 1,7176 | 0,1578 | [0,1504 ; 0,1648] | 233,82 | 262,59 |

Passer de 10 à 20 pas réduit la CVaR neuronale de 0,3629, avec un intervalle à 95 % de [0,3527 ; 0,3741]. Passer de 20 à 30 pas apporte encore 0,1376, avec un intervalle de [0,1296 ; 0,1454]. Au coût central, la fréquence accrue reste donc avantageuse sur la plage étudiée, contrairement à l’hypothèse d’un retournement précoce. Le gain marginal diminue cependant, tandis que le turnover augmente. Une fréquence supérieure à 30 pas pourrait encore révéler un optimum intérieur et n’a pas été testée.

Chaque politique neuronale fait mieux que Leland à sa propre fréquence. L’amélioration absolue face à Leland diminue néanmoins avec la fréquence, de 0,1839 à 10 pas à 0,1578 à 30 pas. Cette expérience repose sur une seule graine d’apprentissage par fréquence ; les intervalles mesurent l’incertitude des trajectoires conditionnellement aux réseaux entraînés, pas l’instabilité d’optimisation.

### Volatilité hors entraînement

| Volatilité réelle | CVaR réseau figé | Leland informé | Leland figé à 20 % | Écart informé - réseau | IC 95 % |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 15 % | 0,8184 | 0,7833 | 0,7188 | -0,0351 | [-0,0436 ; -0,0268] |
| 20 % | 1,5650 | 1,7254 | 1,7254 | 0,1604 | [0,1528 ; 0,1685] |
| 25 % | 2,6608 | 2,6673 | 3,0436 | 0,0065 | [-0,0003 ; 0,0139] |
| 30 % | 3,9584 | 3,6090 | 4,5065 | -0,3494 | [-0,3591 ; -0,3403] |

Une valeur positive de la cinquième colonne favorise le réseau. À 20 %, il conserve l’avantage central. À 25 %, l’écart avec Leland informé est petit et l’intervalle contient zéro : aucune domination n’est établie. À 15 % et 30 %, Leland informé fait significativement mieux.

La comparaison avec Leland figé donne une lecture complémentaire. Le réseau est inférieur à 15 %, mais il réduit la CVaR de 0,3828 à 25 % et de 0,5480 à 30 %, avec des intervalles entièrement positifs. Il transfère donc mieux qu’une règle classique mal calibrée lorsque la volatilité augmente, sans égaler une règle qui reçoit la volatilité réelle à 30 %. Ce résultat ne justifie pas une affirmation générale de robustesse ; il montre précisément où le transfert fonctionne et où il échoue.

### Décisions

- Rapporter séparément les références informées et figées dans le futur manuscrit.
- Ne pas présenter le scénario à 25 % comme une victoire face à Leland informé, puisque l’intervalle inclut zéro.
- Conserver les résultats négatifs à 15 % et 30 % : ils sont nécessaires pour éviter une présentation sélective.
- Maintenir le test final fermé jusqu’au gel des expériences de changement de modèle et des réplications multigraines.

### Prochain jalon

Implémenter un scénario Heston documenté pour tester un changement de dynamique, avec contrôle des moments simulés et mêmes trajectoires par stratégie. Ensuite, répéter les scénarios extrêmes de coût et les expériences sensibles sur plusieurs graines avant de décider si le protocole peut être gelé.

## 2026-09-01 — Exécution 8

### Travail réalisé

- Vérification d’une source primaire supplémentaire sur la simulation Heston : Lord, Koekkoek et van Dijk (2010), DOI 10.1080/14697680802392496.
- Implémentation d’un simulateur Heston avec schéma de full truncation pour la variance et log-Euler pour le spot. La simulation accepte des chocs imposés afin de coupler les diagnostics de discrétisation.
- Ajout de quatre tests sur la reproductibilité, la positivité, le cas de variance constante, la validation de la corrélation et le proxy de delta à volatilité locale. La suite compte désormais 19 tests validés.
- Définition d’un scénario stylisé non calibré : \(v_0=\theta=0{,}04\), \(\kappa=3\), \(\xi=0{,}35\), \(\rho=-0{,}70\), 30 dates de couverture et huit sous-pas par intervalle. La condition de Feller est satisfaite avec une marge de 0,1175.
- Évaluation de la politique centrale figée sans lui transmettre la variance, face aux deltas Black–Scholes et Leland figées à 20 %, puis face à des proxys adaptatifs utilisant la variance instantanée simulée.
- Calcul de 1 000 réplications bootstrap appariées sur 100 000 trajectoires de développement. Le test final est resté fermé.

### Contrôles du simulateur

Sur l’évaluation principale, la moyenne terminale du spot vaut 99,9752 contre une espérance théorique de 100, soit un écart de -1,15 erreur-type. La variance terminale moyenne vaut 0,039991 contre 0,04, soit -0,14 erreur-type. La part de variances tronquées à zéro aux dates observées est \(3{,}23\times10^{-7}\). Ces valeurs ne révèlent pas de biais Monte-Carlo matériel dans les moments contrôlés.

Les log-rendements terminaux ont une asymétrie empirique de -0,578, cohérente avec le levier négatif imposé par \(\rho=-0{,}70\). Cette observation décrit uniquement la simulation et ne constitue pas une estimation sur données réelles.

Le contrôle couplé à 50 000 trajectoires donne les résultats suivants :

| Sous-pas par intervalle | Moyenne de \(S_T\) | Moyenne de \(v_T\) | Asymétrie du log-rendement | CVaR réseau |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 100,00117 | 0,040018 | -0,5744 | 1,8922 |
| 4 | 100,00062 | 0,040019 | -0,5784 | 1,8962 |
| 8 | 100,00023 | 0,040020 | -0,5802 | 1,8989 |

La CVaR neuronale varie de 0,0067 entre les grilles extrêmes, tandis que les moments se stabilisent. Huit sous-pas sont conservés pour l’évaluation principale. Ce diagnostic réduit le risque d’un résultat dicté par une discrétisation grossière sans démontrer une convergence exacte du schéma.

### Résultats hors modèle

| Stratégie | CVaR 95 % | Écart-type du P&L | Turnover | Quantile de perte 99 % |
| --- | ---: | ---: | ---: | ---: |
| Réseau figé, sans variance dans l’état | 1,8809 | 0,6642 | 234,17 | 2,0715 |
| Delta figée à 20 % | 2,2379 | 0,6070 | 273,96 | 2,5498 |
| Leland figé à 20 % | 2,0246 | 0,5891 | 262,82 | 2,2938 |
| Proxy delta à variance instantanée | 2,0763 | 0,5817 | 276,23 | 2,3216 |
| Proxy Leland à variance instantanée | 1,9253 | 0,5690 | 264,89 | 2,1250 |

L’amélioration de CVaR du réseau face à Leland figé vaut 0,1437, avec un intervalle bootstrap à 95 % de [0,1339 ; 0,1536]. Face au proxy Leland alimenté par la variance instantanée, elle vaut 0,0444, avec un intervalle de [0,0372 ; 0,0518]. Les 1 000 réplications sont positives dans les deux comparaisons.

Le réseau améliore aussi les quantiles de perte à 95 %, 99 % et 99,5 % face aux deux références de Leland, et son turnover est inférieur d’environ 11 %. Il ne domine cependant pas toute la distribution : son écart-type du P&L est plus élevé et son quantile 90 % vaut 1,3425 contre 1,3104 pour Leland figé. Le résultat reste donc spécifique à l’objectif de queue retenu.

### Limites et décisions

- Le scénario Heston est stylisé et n’est calibré sur aucun marché. Il isole un mécanisme de volatilité stochastique avec levier, pas une performance financière réelle.
- Le prix initial reste celui du modèle Black–Scholes d’entraînement. Comme il est commun aux stratégies, il translate les pertes sans modifier leurs écarts de CVaR dans un même scénario ; les niveaux absolus ne doivent pas servir à comparer les modèles générateurs.
- Les références adaptatives sont des proxys Black–Scholes à variance instantanée. Elles ne sont ni la delta analytique de Heston ni des stratégies optimisées pour la CVaR.
- Une seule politique entraînée est évaluée. L’intervalle bootstrap mesure l’incertitude des trajectoires conditionnellement à cette politique, pas l’incertitude d’apprentissage.
- Le résultat positif sera conservé comme observation de développement, sans affirmation de robustesse générale.

### Prochain jalon

Évaluer au moins une corrélation nulle et un stress de volatilité de la variance afin de vérifier si l’avantage survit à d’autres paramétrages Heston. Ensuite, répéter les coûts extrêmes et les fréquences sensibles sur plusieurs graines d’apprentissage avant le gel du protocole.

## 2026-09-01 — Exécution 9

### Travail réalisé

- Construction d’une grille factorielle stylisée croisant \(\rho\in\{-0{,}70,0\}\) et \(\xi\in\{0{,}35,0{,}60\}\), tous les autres paramètres restant identiques.
- Utilisation des mêmes matrices de chocs pour les quatre scénarios afin de réduire le bruit des comparaisons qualitatives.
- Évaluation sur 100 000 trajectoires de développement par scénario, avec 1 000 réplications bootstrap appariées face à Leland figé et au proxy Leland observant la variance instantanée.
- Contrôle couplé à 4 et 8 sous-pas sur les deux scénarios à forte volatilité de variance. Cette vérification est prioritaire car \(\xi=0{,}60\) viole la condition de Feller.
- Conservation de la même politique GBM figée, du même coût et de la même prime commune. Le réseau ne reçoit toujours pas la variance comme variable d’état.

### Résultats de la grille

| \(\xi\) | \(\rho\) | Condition de Feller | CVaR réseau | Leland figé | Proxy Leland | Amélioration face au proxy | IC bootstrap 95 % |
| ---: | ---: | :---: | ---: | ---: | ---: | ---: | ---: |
| 0,35 | -0,70 | oui | 1,8809 | 2,0246 | 1,9253 | 0,0444 | [0,0366 ; 0,0516] |
| 0,35 | 0 | oui | 2,0630 | 2,3112 | 2,1472 | 0,0842 | [0,0760 ; 0,0925] |
| 0,60 | -0,70 | non | 2,3082 | 2,4774 | 2,3136 | 0,0054 | [-0,0055 ; 0,0162] |
| 0,60 | 0 | non | 2,7011 | 3,0022 | 2,6797 | -0,0215 | [-0,0346 ; -0,0086] |

Une amélioration positive favorise le réseau. Celui-ci bat Leland figé dans les quatre scénarios, avec des améliorations comprises entre 0,1438 et 0,3010 et des intervalles entièrement positifs. Cette référence figée ne s’adapte toutefois pas à la variance stochastique.

Face au proxy qui observe la variance instantanée, le résultat dépend du régime. Le réseau gagne dans les deux scénarios à volatilité de variance modérée. Sous \(\xi=0{,}60\) avec levier, l’écart devient indiscernable de zéro. Sous \(\xi=0{,}60\) sans levier, le proxy fait significativement mieux de 0,0215 en CVaR. Cette perte d’avantage est un résultat négatif à conserver.

### Contrôle du scénario critique

Dans le stress à forte volatilité de variance, la part de variances nulles aux dates observées passe de 0,204 % avec quatre sous-pas à 0,127 % avec huit sous-pas. Les moments du spot et de la variance restent à moins de 1,34 et 0,16 erreur-type de leurs espérances respectives.

Pour \(\rho=0\), l’écart proxy moins réseau vaut -0,0437 à quatre sous-pas et -0,0430 à huit sous-pas sur les 50 000 trajectoires couplées. L’inversion ne vient donc pas du choix entre ces deux grilles. Pour \(\rho=-0{,}70\), l’écart reste proche de zéro : 0,0034 puis 0,0033.

### Interprétation prudente

Le réseau ne reçoit que le log-moneyness, le temps restant et l’inventaire précédent. Lorsque la volatilité de la variance est forte et que \(\rho=0\), le spot courant contient moins d’information indirecte sur la variance cachée que dans un régime de levier négatif. Le proxy adaptatif, lui, observe cette variance directement. Ce déficit d’information est une explication plausible de l’inversion, mais il n’est pas démontré causalement par la grille seule.

Une ablation ajoutant la variance à l’état d’une politique entraînée sous Heston permettrait de tester ce mécanisme. Elle constituerait toutefois un modèle différent de la politique GBM évaluée ici et devra être présentée séparément, sans réinterpréter après coup le test de transfert.

### Limites et décisions

- La grille n’est pas calibrée et ne couvre ni maturités, ni strikes, ni paramètres de retour à la moyenne différents.
- Les scénarios à \(\xi=0{,}60\) violent la condition de Feller ; la full truncation et le contrôle de grille limitent le biais numérique sans l’annuler.
- Les intervalles restent conditionnels à une seule politique entraînée.
- La robustesse générale sous Heston est rejetée : le résultat doit être formulé par régime et par niveau d’information de la référence.
- Le prochain effort de calcul portera sur l’incertitude d’apprentissage aux coûts extrêmes, plus directement liée à la conclusion principale.

### Prochain jalon

Réentraîner plusieurs graines supplémentaires à 0 et 50 points de base sous le budget figé de 2 000 époques, puis comparer la dispersion inter-graines, les intervalles appariés et le turnover. Garder le test final fermé.
