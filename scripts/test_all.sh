#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
PYTHON="$ROOT_DIR/.venv/bin/python"
if [ ! -x "$PYTHON" ]; then
  echo "ERROR: .venv/bin/python not found. Create the project virtual environment first." >&2
  exit 1
fi
echo "=== BACKEND TESTS ==="
PYTHONPATH="$ROOT_DIR/backend" "$PYTHON" -m pytest backend/tests -q
echo "=== GATEWAY TESTS ==="
PYTHONPATH="$ROOT_DIR/gateway" "$PYTHON" -m pytest --import-mode=importlib gateway/tests -q
echo "=== ALL TEST SUITES PASSED ==="
