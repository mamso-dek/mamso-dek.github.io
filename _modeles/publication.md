---
title: Titre de la publication
summary: Résumé court.
authors: Massavo Salako
year: 2026
date: 2026-08-15
venue: Revue, conférence ou institution
publication_type: Rapport technique
search_terms: mots clés utiles pour la recherche
comment_term: publication-identifiant-unique
published: false
# Pour un manuscrit non publié, ne téléversez pas son PDF dans le dépôt.
# full_text_note: Le texte intégral n’est pas diffusé publiquement à ce stade.
# Pour un document public, décommentez les champs pdf ci-dessous.
# pdf_url: /assets/publications/document.pdf
# pdf_title: Titre court du document
# pdf_pages: 20
# pdf_file_size: 2,4 Mo
# pdf_language: Français
# pdf_download: true
links:
  - label: DOI
    url: https://doi.org/identifiant
    external: true
---
## Résumé

Présentez ici le résumé ou les informations complémentaires.

## Formulation

$$
\widehat{\theta}
=
\underset{\theta}{\arg\min}\;L(\theta).
$$

## Exemple de code

```python
from sklearn.model_selection import cross_validate

scores = cross_validate(model, X, y, cv=5)
```

![Description du graphique](/assets/publications/graphique.svg)

*Source et nature des données.*
{: .figure-caption}
