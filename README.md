# Portfolio de Massavo Salako

Site statique (HTML/CSS/JS) pret pour GitHub Pages en 0 euro.

## Fichiers

- `index.html`: contenu du portfolio
- `styles.css`: design responsive
- `script.js`: animations
- `assets/cvPro.pdf`: CV telechargeable
- `media/`: images, documents et videos publies sur le site

## Tester en local

```bash
cd /Users/massavosalako/Documents/portofolio
python3 -m http.server 8080
```

Puis ouvre `http://localhost:8080`.

## Publication sur GitHub Pages

### Cas recommande (site a la racine)

Si ton pseudo GitHub est `mamso-dek`, cree un repo nomme:

`mamso-dek.github.io`

Ton site sera servi ici:

`https://mamso-dek.github.io`

### Commandes de push

```bash
cd /Users/massavosalako/Documents/portofolio
git init
git checkout -b main
git add .
git commit -m "Initial portfolio"
git remote add origin https://github.com/mamso-dek/mamso-dek.github.io.git
git push -u origin main
```

Si ton pseudo GitHub est different, remplace `mamso-dek`.

### Activer Pages (si necessaire)

1. Ouvre le repo sur GitHub.
2. Va dans `Settings` -> `Pages`.
3. Choisis `Deploy from a branch`.
4. Branche: `main`, dossier: `/ (root)`.
5. Attends 1 a 3 minutes.

## URL finale

- Repo `mamso-dek.github.io` -> `https://mamso-dek.github.io`
- Repo `portfolio` -> `https://mamso-dek.github.io/portfolio/`

## Publier images, documents et videos

1. Ouvre ton repo GitHub `mamso-dek.github.io`.
2. Va dans le dossier `media/`.
3. Clique `Add file` -> `Upload files`.
4. Valide le commit sur `main`.
5. Attends 1 a 2 minutes: la section `Publications` du site se met a jour automatiquement.

Types supportes:

- Images: `jpg`, `jpeg`, `png`, `webp`, `gif`, `svg`, `avif`
- Videos: `mp4`, `webm`, `ogg`, `mov`, `m4v`
- Documents: `pdf`, `doc`, `docx`, `ppt`, `pptx`, `xls`, `xlsx`, `txt`, `csv`

## Activer les commentaires publics (gratuit)

Le site utilise `utterances` (commentaires via GitHub Issues).

1. Dans le repo GitHub, verifie que `Issues` est active.
2. Installe l'app `utterances` sur ton compte GitHub:
   `https://github.com/apps/utterances`
3. Donne acces au repo `mamso-dek.github.io`.
4. Recharge le site: la section `Commentaires` sera active.

Note: les visiteurs doivent avoir un compte GitHub pour commenter.
