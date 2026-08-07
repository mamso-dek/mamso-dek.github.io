# Gérer le contenu du portfolio

Ce guide permet d’ajouter et modifier le contenu sans rédiger de page HTML et sans passer par Codex.

## 1. Comment fonctionne le site

Vous rédigez un fichier Markdown. Jekyll applique automatiquement le bon modèle de page, ajoute le contenu dans la bonne rubrique et l’intègre à la recherche.

```text
Fichier Markdown + informations en haut
                 ↓
               Jekyll
                 ↓
Page web + liste Travaux/Enseignement + recherche
```

Les informations placées entre les deux lignes `---` s’appellent le front matter. Elles indiquent à Jekyll le titre, la date, le résumé, les ressources et les options du contenu. Tout ce qui vient après est le texte de la page en Markdown.

## 2. Choisir le bon dossier

| Contenu | Dossier | Résultat |
| --- | --- | --- |
| Projet | `_projets/` | Rubrique Projets dans Travaux |
| Publication | `_publications/` | Rubrique Publications dans Travaux |
| Note | `_notes/` | Rubrique Notes dans Travaux |
| Cours, TD/TP, atelier ou tutorat | `_enseignements/` | Page Enseignement |

Les fichiers de départ se trouvent dans `_modeles/`.

## 3. Ajouter un contenu directement depuis GitHub

1. Ouvrir le dépôt `mamso-dek.github.io`.
2. Ouvrir le modèle correspondant dans `_modeles/`.
3. Copier son contenu.
4. Ouvrir le dossier de destination, par exemple `_projets/`.
5. Cliquer sur `Add file`, puis `Create new file`.
6. Donner un nom simple en minuscules, sans accent ni espace, par exemple `prevision-inflation.md`.
7. Coller le modèle et remplacer les informations.
8. Passer `published: false` à `published: true`.
9. Cliquer sur `Commit changes`.
10. Attendre quelques minutes : la page, la liste et la recherche sont actualisées automatiquement.

Pour préparer un brouillon invisible, laisser `published: false`.

## 4. Rédiger en Markdown

```markdown
## Un grand titre de section

Un paragraphe normal avec un mot en **gras** et un lien vers
[une ressource](https://example.com).

### Un sous-titre

- Premier élément
- Deuxième élément

![Description de l’image](/assets/projets/mon-projet/figure.png)
```

Il n’est pas nécessaire de connaître le HTML.

### Ajouter une formule

Les formules utilisent la syntaxe LaTeX et sont rendues automatiquement par MathJax.

Une formule dans une phrase :

```markdown
La variance conditionnelle est notée \(\sigma_t^2\).
```

Une formule centrée :

```markdown
$$
\sigma_t^2 = \omega + \alpha\varepsilon_{t-1}^2
              + \beta\sigma_{t-1}^2.
$$
```

### Ajouter du code

Placer trois accents graves avant et après le code, en précisant le langage :

````markdown
```python
import pandas as pd

data = pd.read_csv("donnees.csv")
```
````

Les langages `python`, `r`, `sql`, `bash` et `json` sont notamment reconnus.

### Ajouter un graphique

Téléverser d’abord l’image dans `assets/`, puis l’insérer avec :

```markdown
![Description du graphique](/assets/projets/mon-projet/graphique.svg)

*Données simulées ou source des données réelles.*
{: .figure-caption}
```

Les formats `svg`, `png`, `jpg` et `webp` sont adaptés. Le format SVG reste recommandé pour les courbes et diagrammes, car il reste net sur téléphone et ordinateur.

Toujours préciser si une figure utilise des données réelles, simulées ou uniquement illustratives.

## 5. Ajouter un projet

Créer `_projets/nom-du-projet.md` à partir de `_modeles/projet.md`.

Les champs principaux sont :

- `title` : titre complet ;
- `summary` : résumé court affiché dans la liste ;
- `order` : ordre d’affichage, 1 avant 2 ;
- `featured` : `true` pour l’afficher aussi sur l’accueil ;
- `domain`, `project_type`, `methods` : informations de la fiche ;
- `search_terms` : mots permettant de retrouver le projet ;
- `comment_term` : identifiant unique de sa discussion ;
- `resources` : fichiers ou liens liés au projet.

Exemple de ressources :

```yaml
resources:
  - label: Rapport PDF
    url: /assets/projets/prevision-inflation/rapport.pdf
  - label: Code source
    url: https://github.com/mamso-dek/nom-du-depot
    external: true
```

## 6. Ajouter une publication

Créer `_publications/nom-publication.md` à partir de `_modeles/publication.md`.

La page accepte un résumé Markdown et plusieurs liens : PDF, DOI, dépôt de code ou page de la revue.

```yaml
links:
  - label: Lire le PDF
    url: /assets/publications/article.pdf
  - label: DOI
    url: https://doi.org/...
    external: true
```

## 7. Ajouter une note

Créer `_notes/nom-de-la-note.md` à partir de `_modeles/note.md`.

Une note sert à publier une explication, une réflexion, un retour d’expérience ou un tutoriel plus léger qu’un projet complet. Les commentaires peuvent être activés avec `comments: true`.

## 8. Ajouter un contenu d’enseignement

Créer `_enseignements/nom-du-contenu.md` à partir de `_modeles/enseignement.md`.

Choisir une catégorie :

- `courses` : cours ;
- `practical` : TD ou TP ;
- `workshops` : atelier ou formation ;
- `tutoring` : tutorat ou accompagnement.

Les PDF, diapositives et feuilles d’exercices se déclarent dans `resources`.

## 9. Ajouter des fichiers

Créer de préférence un dossier par contenu :

```text
assets/
  projets/prevision-inflation/
  publications/
  notes/
  enseignement/
  notebooks/
```

Depuis GitHub, ouvrir le dossier voulu, puis `Add file` et `Upload files`. Copier ensuite le chemin du fichier dans le front matter ou dans le Markdown.

Les images et vidéos intégrées dans le Markdown restent dans la page concernée. Les PDF et autres documents apparaissent comme liens de ressources.

## 10. Gérer un notebook

### Option simple recommandée depuis GitHub

1. Téléverser le fichier `.ipynb` dans `assets/notebooks/`.
2. Ajouter un lien nbviewer dans les ressources du projet ou de la note.

```yaml
resources:
  - label: Parcourir le notebook
    url: https://nbviewer.org/github/mamso-dek/mamso-dek.github.io/blob/main/assets/notebooks/mon-notebook.ipynb
    external: true
  - label: Télécharger le notebook
    url: /assets/notebooks/mon-notebook.ipynb
```

Le visiteur peut ainsi lire le notebook sans ouvrir le dépôt GitHub.

### Option intégrée dans la page

Sur votre ordinateur, convertir le notebook en HTML :

```bash
./scripts/convert_notebook.sh assets/notebooks/mon-notebook.ipynb
```

Puis ajouter dans le fichier Markdown :

```yaml
notebook_source: /assets/notebooks/mon-notebook.ipynb
notebook_html: /assets/notebooks/rendered/mon-notebook.html
```

Le notebook sera visible directement dans la page du projet ou de la note.

## 11. Modifier ou supprimer

- Pour modifier : ouvrir le fichier Markdown dans GitHub, cliquer sur le crayon, corriger puis valider.
- Pour masquer temporairement : ajouter `published: false`.
- Pour supprimer : supprimer le fichier Markdown. Sa page disparaîtra lors de la reconstruction suivante.

## 12. Commentaires

Chaque `comment_term` doit être unique et ne doit plus changer après les premiers commentaires. Utterances crée une discussion GitHub attachée à ce contenu. Les notifications GitHub peuvent être envoyées à votre adresse Gmail si cette adresse est configurée dans les paramètres de notifications de votre compte GitHub.
