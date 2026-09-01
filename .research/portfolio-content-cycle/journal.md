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
