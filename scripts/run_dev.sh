#!/usr/bin/env bash
set -euo pipefail

# Convenience script to create venv, install deps and run uvicorn for local development
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$ROOT/.venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtualenv in $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

echo "Activating virtualenv and installing requirements..."
source "$VENV_DIR/bin/activate"
pip install -U pip
pip install -r "$ROOT/requirements.txt"

echo "Starting app: uvicorn app.main:app --reload"
exec "$VENV_DIR/bin/uvicorn" app.main:app --reload
