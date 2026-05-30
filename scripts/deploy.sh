#!/usr/bin/env sh
set -eu

HOST_ADDRESS="${HOST_ADDRESS:-0.0.0.0}"
PORT="${PORT:-8000}"
SKIP_TESTS="${SKIP_TESTS:-0}"
NO_START="${NO_START:-0}"
RECREATE_VENV="${RECREATE_VENV:-0}"
UPGRADE_PIP="${UPGRADE_PIP:-0}"

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/.venv"
PYTHON_PATH="$VENV_PATH/bin/python"

cd "$PROJECT_ROOT"

echo "==> Deploying personal-AI-searcher from $PROJECT_ROOT"

if [ "$RECREATE_VENV" = "1" ] && [ -d "$VENV_PATH" ]; then
  echo "==> Removing existing virtual environment"
  rm -rf "$VENV_PATH"
fi

if [ ! -x "$PYTHON_PATH" ]; then
  echo "==> Creating virtual environment"
  python3 -m venv "$VENV_PATH"
fi

if [ "$UPGRADE_PIP" = "1" ]; then
  echo "==> Upgrading pip"
  "$PYTHON_PATH" -m pip install --upgrade pip
fi

echo "==> Installing dependencies"
"$PYTHON_PATH" -m pip install -r requirements.txt

echo "==> Initializing database"
"$PYTHON_PATH" -m app.db.init_db

if [ "$SKIP_TESTS" != "1" ]; then
  echo "==> Running tests"
  "$PYTHON_PATH" -m pytest
fi

if [ "$NO_START" = "1" ]; then
  echo "==> Deployment finished. Service was not started because NO_START=1."
  exit 0
fi

echo "==> Starting service at http://$HOST_ADDRESS:$PORT"
exec "$PYTHON_PATH" -m uvicorn app.main:app --host "$HOST_ADDRESS" --port "$PORT"
