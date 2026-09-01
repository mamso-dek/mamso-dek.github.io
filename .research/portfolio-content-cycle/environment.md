# Environnement de calcul

## Plateforme de développement

- Architecture : Apple Silicon ARM64.
- Système : macOS 26.6.2.
- Python : 3.12.13.
- Environnement de travail : `.venv`, non suivi par Git.
- Environnement propre de contrôle du verrou : `.lock-venv`, non suivi par Git.
- Accélérateur disponible : MPS ; périphérique de référence retenu : CPU.

## Versions contrôlées

- PyTorch : 2.13.0.
- NumPy : 2.3.5.
- SciPy : 1.18.1.
- pandas : 2.2.3.
- scikit-learn : 1.9.0.
- Matplotlib : 3.11.1.
- nbformat : 5.11.1.
- nbconvert : 7.17.1.

`requirements.txt` fixe les dépendances directes et `requirements-lock.txt` contient l’environnement complet résolu. Ce verrou a été recréé dans un environnement sans paquets hérités, puis contrôlé avec `pip check`.

## Politique de reproductibilité

- Les versions exactes sont figées dans `requirements-lock.txt`.
- Les graines NumPy et PyTorch seront fixées et enregistrées par expérience.
- Les ensembles d’entraînement, de validation et de test auront des graines disjointes.
- Les résultats de référence seront recalculés sur CPU.
- `torch.use_deterministic_algorithms(True)` sera activé pendant les tests de reproductibilité lorsque toutes les opérations utilisées le permettent.
- Une accélération MPS ne sera retenue pour les expériences longues que si elle ne modifie pas matériellement les résultats de contrôle.

La documentation officielle de PyTorch précise que le déterminisme dépend aussi du logiciel et du matériel. Les versions, le périphérique et les graines devront donc accompagner chaque résultat.

## Choix du périphérique de référence

Le test de 20 époques a pris 0,764 seconde sur CPU et 0,869 seconde sur MPS. L’écart numérique maximal observé sur les métriques neuronales est de \(7,63\times10^{-6}\), sans différence matérielle, mais MPS n’apporte aucun gain de vitesse à cette échelle. Les résultats de référence seront donc produits sur CPU ; MPS reste disponible pour un contrôle secondaire.

## Sources techniques

- [Installation locale de PyTorch](https://docs.pytorch.org/get-started/locally/)
- [Backend MPS sur macOS](https://docs.pytorch.org/docs/stable/notes/mps.html)
- [Algorithmes déterministes](https://docs.pytorch.org/docs/stable/generated/torch.use_deterministic_algorithms.html)
