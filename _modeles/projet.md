---
title: Titre du projet
summary: Résumé court affiché dans la liste des travaux.
date: 2026-08-07
order: 10
featured: false
domain: Domaine principal
project_type: Type de travail
methods: Méthode 1, méthode 2
methods_label: MÉTHODE 1 · MÉTHODE 2
objective: Objectif principal du projet.
visual: default
search_terms: mots clés utiles pour la recherche
contact_subject: Demande au sujet du projet
comment_term: projet-identifiant-unique
published: false
steps:
  - title: Première étape
    description: Description de la première étape.
# Décommentez ce bloc lorsqu’un fichier est prêt à être publié.
# resources:
#   - label: Rapport du projet
#     type: Rapport
#     format: PDF
#     description: Présentation de la méthode et des résultats.
#     action: Télécharger
#     download: true
#     file_size: 2,4 Mo
#     url: /assets/projets/nom-du-projet/rapport.pdf
#   - label: Notebook d’analyse
#     type: Notebook
#     format: IPYNB
#     action: Télécharger
#     download: true
#     url: /assets/notebooks/nom-du-notebook.ipynb
# Pour intégrer un notebook HTML, retirez le symbole # des deux lignes suivantes.
# notebook_source: /assets/notebooks/nom-du-notebook.ipynb
# notebook_html: /assets/notebooks/rendered/nom-du-notebook.html
---
## Question étudiée

Présentez ici le problème, les données et le contexte.

## Résultats

Présentez ici les résultats importants.

## Formulation mathématique

Présentez une équation dans un bloc délimité par deux symboles dollar :

$$
y_t = f(x_t,\theta) + \varepsilon_t.
$$

## Code

```python
import pandas as pd

data = pd.read_csv("donnees.csv")
print(data.describe())
```

## Figure

![Description précise du graphique](/assets/projets/nom-du-projet/graphique.svg)

*Indiquez la source des données et précisez si elles sont réelles ou simulées.*
{: .figure-caption}
