# Cycle scientifique du portfolio — septembre 2026

Ce dossier contient le journal de travail, les décisions méthodologiques et les résultats intermédiaires du cycle de cinq jours. Il commence par un point et n’est pas publié par Jekyll. Aucun résultat de ce dossier ne doit être présenté sur le site avant la fin des contrôles scientifiques.

## État courant

- **Jour :** 1 sur 5
- **Type principal retenu :** Projet
- **Sujet retenu :** couverture neuronale d’une option européenne sous coûts de transaction
- **Statut :** les sensibilités, les réplications multigraines et les ablations sont terminées ; le modèle central et le protocole sont désormais gelés
- **Résultat provisoire :** la borne 1,00 améliore très légèrement la CVaR de développement mais accroît le turnover ; la borne centrale 1,25 est conservée pour éviter une sélection rétrospective
- **Prochain jalon :** auditer le script final et les empreintes, puis ouvrir une seule fois le test préenregistré de 250 000 trajectoires
- **Temps restant :** quatre jours sur le cycle ; le test final préenregistré reste fermé

Les fichiers de référence sont :

- `selection-sujets.md` : comparaison pondérée des sujets candidats ;
- `protocole.md` : question, hypothèses, expériences et critères d'arrêt ;
- `gel-protocole.md` : spécification immuable du modèle et de l'analyse avant test final ;
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
