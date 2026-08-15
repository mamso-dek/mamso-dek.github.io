---
title: "Modéliser l’incertitude : au-delà de la prévision ponctuelle"
summary: Pourquoi une prévision doit être accompagnée d’intervalles, de scénarios et d’une analyse des risques avant d’éclairer une décision.
authors: Massavo Salako
year: 2026
venue: "Article de synthèse · Version de travail"
publication_type: Article de synthèse
search_terms: incertitude prévision intervalle confiance scénario risque calibration probabilités décision modélisation
comment_term: publication-modeliser-incertitude-prevision
---
## Résumé

Une valeur prévue donne l’illusion d’une réponse définitive : un prix, une demande, un indicateur ou une probabilité. Pourtant, toute prévision dépend de données incomplètes, d’hypothèses et d’un modèle imparfait. Cette publication présente les principales formes d’incertitude et montre comment les intégrer à une analyse destinée à la décision.

## La prévision ponctuelle ne suffit pas

Deux modèles peuvent produire la même valeur centrale tout en impliquant des niveaux de risque très différents. Prévoir une demande de 1 000 unités n’a pas le même sens si l’erreur habituelle est de 20 unités ou de 400 unités.

La décision exige donc au minimum trois informations :

- une estimation centrale ;
- une mesure de dispersion ou un intervalle ;
- les conditions dans lesquelles cette estimation reste crédible.

## Identifier les sources d’incertitude

L’incertitude observée peut provenir de plusieurs niveaux.

### Les données

Les mesures peuvent être bruitées, manquantes ou révisées. L’échantillon peut aussi représenter imparfaitement la population ou le contexte futur.

### Les paramètres

Les coefficients d’un modèle sont estimés à partir d’un nombre limité d’observations. D’autres échantillons plausibles conduiraient à des valeurs légèrement différentes.

### La structure du modèle

Tout modèle simplifie la réalité. Le choix des variables, de la forme fonctionnelle ou de la distribution introduit une incertitude qui n’apparaît pas toujours dans les intervalles classiques.

### Le contexte futur

Une rupture réglementaire, économique, technologique ou comportementale peut rendre moins pertinentes les relations apprises dans le passé.

## Intervalles, distributions et scénarios

Un intervalle de prévision décrit une plage de valeurs plausibles pour une future observation. Une distribution prédictive va plus loin en attribuant un poids relatif aux différentes valeurs possibles. Les scénarios, quant à eux, permettent d’explorer des hypothèses structurées qui ne sont pas nécessairement présentes dans l’historique.

Ces outils sont complémentaires :

| Outil | Question principale |
| --- | --- |
| Intervalle | Dans quelle plage la valeur future peut-elle se situer ? |
| Distribution | Quelles valeurs sont les plus ou les moins probables ? |
| Scénario | Que se passerait-il sous une hypothèse particulière ? |
| Test de sensibilité | Quels paramètres influencent le plus le résultat ? |

Pour une probabilité de couverture \(1-\alpha\), un intervalle prédictif peut être défini à partir des quantiles conditionnels :

$$
I_{1-\alpha}(x)
=
\left[
Q_{\alpha/2}(Y\mid X=x),
Q_{1-\alpha/2}(Y\mid X=x)
\right].
$$

L’intervalle concerne une observation future ; il est généralement plus large qu’un intervalle portant uniquement sur la moyenne conditionnelle.

### Estimation de quantiles en Python

```python
from sklearn.ensemble import GradientBoostingRegressor

levels = (0.05, 0.50, 0.95)
quantile_models = {}

for level in levels:
    model = GradientBoostingRegressor(
        loss="quantile",
        alpha=level,
        n_estimators=300,
        max_depth=3,
        random_state=42,
    )
    quantile_models[level] = model.fit(X_train, y_train)

lower = quantile_models[0.05].predict(X_test)
median = quantile_models[0.50].predict(X_test)
upper = quantile_models[0.95].predict(X_test)
empirical_coverage = ((y_test >= lower) & (y_test <= upper)).mean()
```

![Prévision centrale et intervalle prédictif simulé](/assets/publications/intervalle-predictif.svg)

*Données simulées : la bande s’élargit avec l’horizon pour rendre visible l’augmentation de l’incertitude.*
{: .figure-caption}

## Vérifier la calibration

Un intervalle annoncé à 90 % devrait contenir la valeur observée environ neuf fois sur dix, sur une série suffisamment longue de situations comparables. Cette propriété, appelée calibration, doit être vérifiée empiriquement.

Des intervalles trop étroits donnent une confiance excessive. Des intervalles systématiquement trop larges protègent contre l’erreur, mais apportent peu d’information. La bonne représentation de l’incertitude recherche un équilibre entre couverture et précision.

## Relier l’incertitude à la décision

L’incertitude devient opérationnelle lorsqu’elle est comparée aux conséquences possibles. Une décision réversible et peu coûteuse n’exige pas le même niveau de prudence qu’une décision engageant des ressources importantes.

Il est alors utile de raisonner en pertes attendues, en seuils de risque ou en scénarios défavorables. Le meilleur choix n’est pas toujours celui associé à la prévision moyenne la plus favorable, mais celui dont les conséquences restent acceptables dans plusieurs situations plausibles.

## Conclusion

Présenter l’incertitude ne fragilise pas un modèle ; cela le rend plus honnête et plus utile. Une prévision accompagnée d’intervalles, de scénarios et d’une analyse de sensibilité permet de passer d’un chiffre isolé à une décision réellement informée.
