#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: ./scripts/convert_notebook.sh chemin/vers/notebook.ipynb"
  exit 1
fi

if ! command -v jupyter >/dev/null 2>&1; then
  echo "Jupyter est requis. Installez nbconvert avec: pip install nbconvert"
  exit 1
fi

input="$1"
output_dir="assets/notebooks/rendered"
mkdir -p "$output_dir"

jupyter nbconvert --to html --output-dir "$output_dir" "$input"
echo "Notebook converti dans $output_dir"
