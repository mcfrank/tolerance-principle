#!/usr/bin/env bash
# Render the book (or one chapter: ./render.sh 01-derivation.qmd) with the project Python.
set -euo pipefail
cd "$(dirname "$0")"
if [ -x "../.venv/bin/python" ]; then
  export QUARTO_PYTHON="$(cd .. && pwd)/.venv/bin/python"
else
  export QUARTO_PYTHON="$(command -v python3)"
fi
quarto render "$@"
