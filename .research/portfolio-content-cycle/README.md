# Cycle scientifique du portfolio — septembre 2026

Ce dossier contient le journal de travail, les décisions méthodologiques et les résultats intermédiaires du cycle de cinq jours. Il commence par un point et n’est pas publié par Jekyll. Aucun résultat de ce dossier ne doit être présenté sur le site avant la fin des contrôles scientifiques.

## État courant

- **Jour :** 1 sur 5
- **Type principal retenu :** Projet
- **Sujet retenu :** couverture neuronale d’une option européenne sous coûts de transaction
- **Statut :** environnement reproductible, convention de Leland, cœur différentiable et références classiques validés ; cinq apprentissages longs terminés
- **Résultat provisoire :** à 1 000 époques, les cinq graines battent Leland sur la CVaR à 95 % et réduisent les transactions ; il s’agit encore d’un résultat interne à un scénario
- **Prochain jalon :** quantifier l’incertitude Monte-Carlo par comparaison appariée, vérifier la convergence au-delà de 1 000 époques et analyser la politique avant les scénarios de robustesse

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
