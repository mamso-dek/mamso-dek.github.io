# Carte des figures

Les figures sont générées par `generate_figures.py` depuis les artefacts JSON conservés. Le script ne simule aucune trajectoire et ne charge aucun checkpoint. Les PNG sont destinés au site et au notebook ; les SVG servent à l'impression et à l'inspection détaillée.

## Contrats visuels

| Figure | Question | Forme | Conclusion soutenue | Source |
| --- | --- | --- | --- | --- |
| `final-strategy-comparison` | Quelle couverture réduit le mieux la CVaR et le turnover dans le test final ? | Deux barres horizontales | Le réseau a la CVaR et le turnover les plus faibles parmi les trois couvertures. | `final-test-results.json`, 250 000 trajectoires finales. |
| `final-tail-quantiles` | La réduction de queue apparaît-elle au-delà du seul seuil de CVaR ? | Points groupés par quantile | Les quantiles 95 %, 99 % et 99,5 % du réseau sont inférieurs aux deux deltas. | `final-test-results.json`. |
| `development-cost-sensitivity` | Comment risque et activité évoluent-ils avec le coût ? | Deux courbes de sensibilité | La CVaR augmente avec le coût, le turnover neuronal diminue et reste sous Leland. | `cost-sensitivity.json`, développement. |
| `development-robustness` | L'avantage survit-il aux changements de volatilité et de modèle ? | Intervalles autour de zéro | Non systématiquement : le signe dépend du scénario et de l'information de la référence. | `frequency-volatility.json` et `heston-parameter-sensitivity.json`, développement. |
| `development-ablations` | L'inventaire et la capacité expliquent-ils le résultat central ? | Intervalles autour de zéro | L'inventaire réduit CVaR et turnover ; accroître fortement la capacité n'apporte qu'un petit gain de CVaR. | `model-ablations.json`, développement. |

## Politique graphique

- fond blanc, texte anthracite et grille grise légère ;
- bordeaux `#a83246` pour la politique neuronale ou les améliorations positives ;
- bleu ardoise `#416b85` pour les références ou écarts négatifs ;
- marqueurs, remplissages ouverts, traits et positions complètent la couleur ;
- titres descriptifs, contexte et taille d'échantillon dans les sous-titres ;
- échelles focalisées signalées explicitement lorsqu'elles ne partent pas de zéro ;
- sources et statut final/développement visibles dans chaque export ;
- textes alternatifs enregistrés dans `generated/manifest.json`.
