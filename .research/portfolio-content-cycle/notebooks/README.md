# Notebook narratif

`deep-hedging-couts-transaction.ipynb` est le compagnon exécutable du rapport technique. Il ne simule pas le test final : il contrôle et relit les artefacts JSON conservés, puis affiche les tableaux et figures validés.

## Reconstruction

Depuis la racine `.research/portfolio-content-cycle` :

```bash
.lock-venv/bin/python notebooks/build_notebook.py
```

## Exécution

```bash
JUPYTER_CONFIG_DIR=/tmp/codex-jupyter-config \
JUPYTER_DATA_DIR=/tmp/codex-jupyter-data \
JUPYTER_RUNTIME_DIR=/tmp/codex-jupyter-runtime \
IPYTHONDIR=/tmp/codex-ipython \
PYTHONDONTWRITEBYTECODE=1 \
.lock-venv/bin/python -m jupyter nbconvert \
  --execute --to notebook --inplace \
  --ExecutePreprocessor.timeout=180 \
  notebooks/deep-hedging-couts-transaction.ipynb
```

## Rendu HTML

```bash
JUPYTER_CONFIG_DIR=/tmp/codex-jupyter-config \
JUPYTER_DATA_DIR=/tmp/codex-jupyter-data \
JUPYTER_RUNTIME_DIR=/tmp/codex-jupyter-runtime \
IPYTHONDIR=/tmp/codex-ipython \
.lock-venv/bin/python -m jupyter nbconvert \
  --to html \
  --template classic \
  --HTMLExporter.embed_images=True \
  --output-dir notebooks/rendered \
  notebooks/deep-hedging-couts-transaction.ipynb
```

Le modèle `classic` conserve dans le HTML les textes alternatifs intégrés aux sorties PNG. Les cinq figures sont embarquées dans le fichier HTML ; aucun fichier image séparé n'est nécessaire pour les consulter.

La reconstruction remplace le notebook par une version sans sorties. Il faut donc toujours l'exécuter de nouveau avant livraison.
