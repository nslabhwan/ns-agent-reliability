#!/usr/bin/env bash
set -euo pipefail

PRODUCT="OpenSynapse"
HOME_DIR="${OPENSYNAPSE_HOME:-$HOME/.local/share/opensynapse}"
VENV="${HOME_DIR}/venv"
BIN_DIR="${OPENSYNAPSE_BIN_DIR:-$HOME/.local/bin}"
CONFIG="${OPENSYNAPSE_CONFIG:-$HOME/.config/opensynapse/config.json}"
ROOT="${OPENSYNAPSE_ROOT:-$PWD}"
WRITE_ROOT="${OPENSYNAPSE_WRITE_ROOT:-}"
ENABLE_SAFE="${OPENSYNAPSE_ENABLE_SAFE_COMMANDS:-0}"
SOURCE="${OPENSYNAPSE_SOURCE:-git+https://github.com/nslabhwan/ns-agent-reliability.git@main}"

choose_python() {
  for p in python3.13 python3.12 python3.11; do
    if command -v "$p" >/dev/null 2>&1; then
      command -v "$p"
      return 0
    fi
  done
  return 1
}

PYTHON="$(choose_python || true)"
if [[ -z "$PYTHON" ]]; then
  echo "ERROR: OpenSynapse alpha requires Python 3.11+." >&2
  exit 2
fi

mkdir -p "$HOME_DIR" "$BIN_DIR" "$(dirname "$CONFIG")"

if [[ ! -d "$VENV" ]]; then
  "$PYTHON" -m venv "$VENV"
fi

"$VENV/bin/python" -m pip install --upgrade pip >/dev/null
"$VENV/bin/python" -m pip install --upgrade "$SOURCE"

ln -sfn "$VENV/bin/opensynapse" "$BIN_DIR/opensynapse"

ARGS=(install --root "$ROOT" --config "$CONFIG" --force)
if [[ -n "$WRITE_ROOT" ]]; then
  ARGS+=(--write-root "$WRITE_ROOT")
fi
if [[ "$ENABLE_SAFE" == "1" ]]; then
  ARGS+=(--enable-safe-commands)
fi

"$VENV/bin/opensynapse" "${ARGS[@]}"

echo
echo "$PRODUCT installed."
echo "Binary: $BIN_DIR/opensynapse"
echo "Config: $CONFIG"
echo "Run: opensynapse doctor"
echo "Local MCP: opensynapse serve --transport http"
echo
echo "Security default: read-only root unless you explicitly set OPENSYNAPSE_WRITE_ROOT."
