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
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || pwd)"

if [[ -f "$SCRIPT_DIR/pyproject.toml" && -d "$SCRIPT_DIR/src" ]]; then
  SOURCE="${OPENSYNAPSE_SOURCE:-$SCRIPT_DIR}"
else
  SOURCE="${OPENSYNAPSE_SOURCE:-git+https://github.com/nslabhwan/ns-agent-reliability.git@main}"
fi

is_termux() {
  [[ -n "${TERMUX_VERSION:-}" ]] || [[ "${PREFIX:-}" == *"com.termux"* ]]
}

ensure_termux_prereqs() {
  if ! is_termux; then
    return 0
  fi
  local missing=()
  command -v python3 >/dev/null 2>&1 || missing+=(python)
  command -v git >/dev/null 2>&1 || missing+=(git)
  if (("${#missing[@]}" > 0)); then
    if ! command -v pkg >/dev/null 2>&1; then
      echo "ERROR: Termux prerequisites are missing and pkg is unavailable." >&2
      exit 2
    fi
    echo "Installing Termux prerequisites: ${missing[*]}"
    pkg install -y "${missing[@]}"
  fi
}

python_ok() {
  "$1" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1
}

choose_python() {
  local p
  for p in python3.13 python3.12 python3.11 python3 python; do
    if command -v "$p" >/dev/null 2>&1 && python_ok "$(command -v "$p")"; then
      command -v "$p"
      return 0
    fi
  done
  return 1
}

if is_termux; then
  if [[ -z "${OPENSYNAPSE_ROOT:-}" ]]; then
    ROOT="$HOME/OpenSynapseWorkspace"
    mkdir -p "$ROOT"
  fi
  if [[ -z "${OPENSYNAPSE_WRITE_ROOT+x}" ]]; then
    WRITE_ROOT="$ROOT"
  fi
fi

ensure_termux_prereqs
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
if is_termux; then
  "$VENV/bin/python" -m pip install --upgrade "$SOURCE"
else
  if [[ "$SOURCE" == git+* ]]; then
    "$VENV/bin/python" -m pip install --upgrade "ns-agent-reliability[http] @ $SOURCE"
  else
    "$VENV/bin/python" -m pip install --upgrade "${SOURCE}[http]"
  fi
fi

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
echo "Local MCP stdio: opensynapse serve --transport stdio"
if ! is_termux; then
  echo "Local MCP HTTP: opensynapse serve --transport http"
fi
if is_termux; then
  echo "Node: Android / Termux"
  echo "Workspace: $ROOT"
fi
echo
if is_termux; then
  echo "Security default: only the dedicated OpenSynapse workspace is writable."
else
  echo "Security default: read-only root unless you explicitly set OPENSYNAPSE_WRITE_ROOT."
fi
