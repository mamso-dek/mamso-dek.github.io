# Cycle scientifique du portfolio — septembre 2026

Ce dossier contient le journal de travail, les décisions méthodologiques et les résultats intermédiaires du cycle de cinq jours. Il commence par un point et n’est pas publié par Jekyll. Aucun résultat de ce dossier ne doit être présenté sur le site avant la fin des contrôles scientifiques.

## État courant

- **Jour :** 1 sur 5
- **Type principal retenu :** Projet
- **Sujet retenu :** couverture neuronale d’une option européenne sous coûts de transaction
- **Statut :** le test final préenregistré a été ouvert une fois et ses résultats intègres sont conservés
- **Résultat final :** la politique neuronale réduit la CVaR de 0,1615 face à Leland, IC 95 % [0,1565 ; 0,1664], tout en réduisant le turnover de 28,79 ; son écart-type de P&L reste supérieur
- **Prochain jalon :** construire les figures et tableaux définitifs, puis rédiger le notebook et le rapport technique sans recalculer le test final
- **Temps restant :** quatre jours sur le cycle ; le test final est définitivement fermé

Les fichiers de référence sont :

- `selection-sujets.md` : comparaison pondérée des sujets candidats ;
- `protocole.md` : question, hypothèses, expériences et critères d'arrêt ;
- `gel-protocole.md` : spécification immuable du modèle et de l'analyse avant test final ;
- `resultats-finaux.md` : interprétation du test final et limites de portée ;
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
