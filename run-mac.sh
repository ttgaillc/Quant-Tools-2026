#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ ! -f ".env" ]]; then
  echo "Missing .env. Copy .env.example to .env and set your values first."
  exit 1
fi

if [[ ! -f "requirements.txt" ]]; then
  echo "Missing requirements.txt."
  exit 1
fi

if [[ ! -d ".venv" ]]; then
  echo "Creating virtual environment..."
  if command -v python3 >/dev/null 2>&1; then
    python3 -m venv .venv
  elif command -v python >/dev/null 2>&1; then
    python -m venv .venv
  else
    echo "Python 3 is not installed or not on PATH."
    exit 1
  fi
fi

if [[ ! -f ".venv/bin/activate" ]]; then
  echo "Could not find venv activation script."
  exit 1
fi

# shellcheck disable=SC1091
source ".venv/bin/activate"

echo "Loading env vars from .env..."
set -a
# shellcheck disable=SC1091
source ".env"
set +a

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Launching TTG CLI..."
python "ttg-cli.py" "$@"
