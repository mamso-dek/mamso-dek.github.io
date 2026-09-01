# Cycle scientifique du portfolio — septembre 2026

Ce dossier contient le journal de travail, les décisions méthodologiques et les résultats intermédiaires du cycle de cinq jours. Il commence par un point et n’est pas publié par Jekyll. Aucun résultat de ce dossier ne doit être présenté sur le site avant la fin des contrôles scientifiques.

## État courant

- **Jour :** 1 sur 5
- **Type principal retenu :** Projet
- **Sujet retenu :** couverture neuronale d’une option européenne sous coûts de transaction
- **Statut :** cinq apprentissages longs, une réplication prolongée à 1 500 époques, un bootstrap apparié et les premiers diagnostics de politique sont terminés
- **Résultat provisoire :** la réplication prolongée réduit la CVaR de 0,1503 face à Leland ; l’intervalle bootstrap à 95 % est [0,1425 ; 0,1578], conditionnellement au scénario et au modèle entraîné
- **Prochain jalon :** confirmer le plateau au-delà de 1 500 époques, puis lancer les sensibilités au coût et aux paramètres de marché

Les fichiers de référence sont :

- `selection-sujets.md` : comparaison pondérée des sujets candidats ;
- `protocole.md` : question, hypothèses, expériences et critères d’arrêt ;
- `matrice-litterature.md` : sources vérifiées et rôle dans l’étude ;
- `bibliographie.bib` : métadonnées bibliographiques réutilisables ;
- `environment.md` : plateforme, dépendances et règles de reproductibilité ;
- `conventions.md` : définition du coût et traduction de la formule de Leland ;
- `affirmations-sources.md` : traçabilité des affirmations importantes ;
- `journal.md` : progression exécution par exécution ;
- `pilot/` : code et résultats exploratoires non publiables ;
- `src/deep_hedging/` : simulateur, P&L différentiable, mesure de risque et politique neuronale ;
- `tests/` : tests unitaires du noyau scientifique ;
- `benchmarks/` : comparaisons CPU/MPS et références Monte-Carlo internes.
