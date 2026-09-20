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
HOME_DIR="${OPENSYNAPSE_HOME:-$HOME/.local/share/opensynapse}"
VENV_PY="$HOME_DIR/venv/bin/python"
PID_FILE="$STATE_DIR/tunnel.pid"
LOG_FILE="$STATE_DIR/tunnel.log"

if [[ ! -x "$BIN_DIR/opensynapse" ]]; then
  echo "OpenSynapse not found; installing the public first-value build..."
  curl -fsSL https://raw.githubusercontent.com/nslabhwan/ns-agent-reliability/main/try.sh | \
    OPENSYNAPSE_HOME="$HOME_DIR" OPENSYNAPSE_BIN_DIR="$BIN_DIR" OPENSYNAPSE_CONFIG="$CONFIG" OPENSYNAPSE_WORKSPACE="$WORKSPACE" bash
elif [[ "${OPENSYNAPSE_NO_UPDATE:-0}" != "1" && -x "$VENV_PY" ]]; then
  echo "Refreshing OpenSynapse from the public main branch without changing your config..."
  "$VENV_PY" -m pip install -q --upgrade \
    "ns-agent-reliability[http] @ git+https://github.com/nslabhwan/ns-agent-reliability.git@main"
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

terminate_tree() {
  local parent="$1" child
  if command -v pgrep >/dev/null 2>&1; then
    while IFS= read -r child; do
      [[ "$child" =~ ^[0-9]+$ ]] || continue
      terminate_tree "$child"
    done < <(pgrep -P "$parent" 2>/dev/null || true)
  fi
  kill -TERM "$parent" 2>/dev/null || true
}

OLD_PID=""
if [[ -f "$PID_FILE" ]]; then
  OLD_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ ! "$OLD_PID" =~ ^[0-9]+$ ]] || ! kill -0 "$OLD_PID" 2>/dev/null; then
    OLD_PID=""
    rm -f "$PID_FILE"
  fi
fi

# Prefer a systemd user service so the tunnel is restarted after crashes and user-session boots.
if [[ "${OPENSYNAPSE_NO_AUTOSTART:-0}" != "1" ]] && command -v systemctl >/dev/null 2>&1; then
  if [[ -n "$OLD_PID" ]]; then
    echo "Migrating the existing foreground-style tunnel to managed autostart..."
    terminate_tree "$OLD_PID"
    for _ in 1 2 3 4 5; do
      kill -0 "$OLD_PID" 2>/dev/null || break
      sleep 1
    done
    rm -f "$PID_FILE"
    OLD_PID=""
  fi

  set +e
  AUTOSTART_JSON="$("$BIN_DIR/opensynapse" autostart install \
    --tunnel-id "$TUNNEL_ID" \
    --config "$CONFIG" \
    --profile-dir "$PROFILE_DIR" \
    --runtime-key-file "$KEY_FILE" 2>/dev/null)"
  AUTOSTART_RC=$?
  set -e
  if [[ $AUTOSTART_RC -eq 0 ]] && grep -Eq '"reboot_recovery"[[:space:]]*:[[:space:]]*"(READY|READY_AFTER_LOGIN)"' <<<"$AUTOSTART_JSON"; then
    echo "$AUTOSTART_JSON"
    if grep -Eq '"reboot_recovery"[[:space:]]*:[[:space:]]*"READY_AFTER_LOGIN"' <<<"$AUTOSTART_JSON"; then
      echo "OpenSynapse tunnel AUTOSTART ACTIVE; unattended reboot recovery needs one OS setting shown above."
    else
      echo "OpenSynapse tunnel AUTOSTART READY."
    fi
    echo "Next: add the Tunnel in ChatGPT once, then use OpenSynapse from normal chats."
    exit 0
  fi
  echo "Systemd user autostart is unavailable here; falling back to a managed background process."
  [[ -n "$AUTOSTART_JSON" ]] && echo "$AUTOSTART_JSON"
fi

if [[ -n "$OLD_PID" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
  echo "OpenSynapse tunnel already running (pid=$OLD_PID)."
  exit 0
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
echo "Reboot recovery: PENDING (systemd user service unavailable)."
echo "Next: open ChatGPT and use the OpenSynapse tunnel connection for a real tool call."
