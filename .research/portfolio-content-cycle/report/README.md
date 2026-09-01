# Rapport technique

Le fichier source `rapport-technique.qmd` produit un rapport de projet en HTML et en PDF. Les cellules Python relisent les artefacts JSON conservés, vérifient leurs empreintes et ne simulent aucune trajectoire.

Depuis la racine `.research/portfolio-content-cycle` :

~~~bash
cd report
mkdir -p output/html output/pdf

QUARTO_PYTHON=../.lock-venv/bin/python \
quarto render rapport-technique.qmd \
  --to html \
  --output-dir output/html

QUARTO_PYTHON=../.lock-venv/bin/python \
quarto render rapport-technique.qmd \
  --to pdf \
  --output-dir output/pdf
~~~

Le PDF doit ensuite être rendu page par page avec Poppler et contrôlé visuellement avant livraison.
