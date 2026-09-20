#!/usr/bin/env bash
set -euo pipefail

TUNNEL_ID="${1:-}"
if [[ ! "$TUNNEL_ID" =~ ^tunnel_[0-9a-f]{32}$ ]]; then
  echo "usage: bash connect-openai.sh tunnel_<32 lowercase hex>" >&2
  exit 2
fi

BIN_DIR="${OPENSYNAPSE_BIN_DIR:-$HOME/.local/bin}"
KEY_FILE="${OPENSYNAPSE_RUNTIME_KEY_FILE:-$HOME/.config/opensynapse/private/control-plane-api-key}"
CONFIG="${OPENSYNAPSE_CONFIG:-$HOME/.config/opensynapse/config.json}"
WORKSPACE="${OPENSYNAPSE_WORKSPACE:-$HOME/OpenSynapseWorkspace}"

if [[ ! -x "$BIN_DIR/opensynapse" ]]; then
  echo "OpenSynapse not found; installing the public first-value build..."
  curl -fsSL https://raw.githubusercontent.com/nslabhwan/ns-agent-reliability/main/try.sh | \
    OPENSYNAPSE_BIN_DIR="$BIN_DIR" OPENSYNAPSE_CONFIG="$CONFIG" OPENSYNAPSE_WORKSPACE="$WORKSPACE" bash
fi

mkdir -p "$(dirname "$KEY_FILE")"
chmod 700 "$(dirname "$KEY_FILE")"
printf 'OpenSynapse Runtime API key: ' >/dev/tty
IFS= read -r -s KEY </dev/tty
printf '\n' >/dev/tty
if [[ ${#KEY} -lt 20 || "$KEY" == *[[:space:]]* ]]; then
  unset KEY
  echo "INVALID_KEY_FORMAT" >&2
  exit 2
fi
TMP="${KEY_FILE}.tmp.$$"
printf '%s' "$KEY" > "$TMP"
chmod 600 "$TMP"
mv -f "$TMP" "$KEY_FILE"
unset KEY

echo "Runtime credential stored locally with mode 600; raw value is not passed in argv."
"$BIN_DIR/opensynapse" connect openai \
  --tunnel-id "$TUNNEL_ID" \
  --config "$CONFIG" \
  --runtime-key-file "$KEY_FILE" \
  --no-run
