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
