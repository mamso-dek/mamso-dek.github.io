# Cycle scientifique du portfolio — septembre 2026

Ce dossier contient le journal de travail, les décisions méthodologiques et les résultats intermédiaires du cycle de cinq jours. Il commence par un point et n’est pas publié par Jekyll. Aucun résultat de ce dossier ne doit être présenté sur le site avant la fin des contrôles scientifiques.

## État courant

- **Jour :** 1 sur 5
- **Type principal retenu :** Projet
- **Sujet retenu :** couverture neuronale d’une option européenne sous coûts de transaction
- **Statut :** les sensibilités au coût, à la fréquence, à la volatilité et un premier changement de modèle Heston sont terminés sur les jeux de développement
- **Résultat provisoire :** dans le scénario Heston stylisé, le réseau figé réduit la CVaR de 0,1437 face à Leland figé et de 0,0444 face à un proxy de Leland alimenté par la variance instantanée ; ce résultat ne vaut ni calibration de marché ni comparaison à une delta Heston optimale
- **Prochain jalon :** varier les paramètres Heston, puis répéter les scénarios extrêmes sur plusieurs graines avant toute ouverture du test final
- **Temps restant :** quatre jours sur le cycle ; le test final préenregistré reste fermé

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
