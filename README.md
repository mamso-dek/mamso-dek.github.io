# Portfolio de Massavo Salako

Portfolio personnel construit avec Jekyll et hébergé gratuitement sur GitHub Pages.

## Principe

Le design est défini une seule fois dans les layouts. Les contenus sont ensuite rédigés en Markdown :

- `_projets/` : projets ;
- `_publications/` : publications ;
- `_notes/` : notes ;
- `_enseignements/` : cours, TD/TP, ateliers et tutorat ;
- `_modeles/` : modèles prêts à réutiliser ;
- `assets/` : PDF, images, vidéos, notebooks et supports.

Jekyll transforme automatiquement chaque fichier Markdown en page web et actualise les listes et la recherche.

## Ajouter du contenu

Le mode d’emploi détaillé se trouve dans `GUIDE_CONTENU.md`.

## Tester localement

```bash
bundle install
bundle exec jekyll serve
```

Puis ouvrir `http://127.0.0.1:4000`.

## Hébergement

Le dépôt `mamso-dek.github.io` est publié gratuitement à l’adresse :

https://mamso-dek.github.io

GitHub Pages reconstruit le site après chaque modification validée sur la branche `main`.

## Commentaires

Les discussions utilisent Utterances et restent attachées à chaque projet ou note. Les visiteurs se connectent avec GitHub pour commenter.
