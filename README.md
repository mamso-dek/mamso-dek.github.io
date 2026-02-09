# Portfolio de Massavo Salako

Site statique (HTML/CSS/JS) pret pour GitHub Pages en 0 euro.

## Fichiers

- `index.html`: contenu du portfolio
- `styles.css`: design responsive
- `script.js`: animations
- `assets/cvPro.pdf`: CV telechargeable

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
