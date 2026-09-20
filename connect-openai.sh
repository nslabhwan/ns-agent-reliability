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
PROFILE_DIR="${OPENSYNAPSE_PROFILE_DIR:-$HOME/.config/opensynapse/tunnel}"
STATE_DIR="${OPENSYNAPSE_STATE_DIR:-$HOME/.local/state/opensynapse}"
PID_FILE="$STATE_DIR/tunnel.pid"
LOG_FILE="$STATE_DIR/tunnel.log"

if [[ ! -x "$BIN_DIR/opensynapse" ]]; then
  echo "OpenSynapse not found; installing the public first-value build..."
  curl -fsSL https://raw.githubusercontent.com/nslabhwan/ns-agent-reliability/main/try.sh | \
    OPENSYNAPSE_BIN_DIR="$BIN_DIR" OPENSYNAPSE_CONFIG="$CONFIG" OPENSYNAPSE_WORKSPACE="$WORKSPACE" bash
fi

mkdir -p "$(dirname "$KEY_FILE")" "$STATE_DIR"
chmod 700 "$(dirname "$KEY_FILE")" "$STATE_DIR"

if [[ -s "$KEY_FILE" ]]; then
  chmod 600 "$KEY_FILE"
  echo "Using existing local runtime credential (value not displayed)."
else
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
fi

# Always verify the official tunnel profile before starting a long-lived process.
"$BIN_DIR/opensynapse" connect openai \
  --tunnel-id "$TUNNEL_ID" \
  --config "$CONFIG" \
  --profile-dir "$PROFILE_DIR" \
  --runtime-key-file "$KEY_FILE" \
  --no-run

if [[ "${OPENSYNAPSE_NO_RUN:-0}" == "1" ]]; then
  echo "Doctor PASS; daemon start skipped by OPENSYNAPSE_NO_RUN=1."
  exit 0
fi

if [[ -f "$PID_FILE" ]]; then
  OLD_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ "$OLD_PID" =~ ^[0-9]+$ ]] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "OpenSynapse tunnel already running (pid=$OLD_PID)."
    exit 0
  fi
  rm -f "$PID_FILE"
fi

nohup "$BIN_DIR/opensynapse" connect openai \
  --tunnel-id "$TUNNEL_ID" \
  --config "$CONFIG" \
  --profile-dir "$PROFILE_DIR" \
  --runtime-key-file "$KEY_FILE" \
  >"$LOG_FILE" 2>&1 </dev/null &
PID=$!
printf '%s\n' "$PID" > "$PID_FILE"
chmod 600 "$PID_FILE" "$LOG_FILE" 2>/dev/null || true
sleep 3
if ! kill -0 "$PID" 2>/dev/null; then
  echo "Tunnel process exited during startup. Inspect: $LOG_FILE" >&2
  tail -40 "$LOG_FILE" >&2 || true
  exit 1
fi

echo "OpenSynapse tunnel STARTED (pid=$PID)."
echo "Log: $LOG_FILE"
echo "Next: open ChatGPT and use the OpenSynapse tunnel connection for a real tool call."
