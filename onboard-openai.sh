#!/usr/bin/env bash
set -euo pipefail

TUNNELS_URL="https://platform.openai.com/settings/organization/tunnels"
KEYS_URL="https://platform.openai.com/settings/organization/api-keys"
CHATGPT_PLUGINS_URL="https://chatgpt.com/plugins"
DOCS_URL="https://developers.openai.com/api/docs/guides/secure-mcp-tunnels"
CONNECT_URL="https://raw.githubusercontent.com/nslabhwan/ns-agent-reliability/main/connect-openai.sh"
BIN_DIR="${OPENSYNAPSE_BIN_DIR:-$HOME/.local/bin}"
STATE_FILE="${OPENSYNAPSE_ONBOARDING_STATE:-$HOME/.config/opensynapse/onboarding.json}"

open_url() {
  local url="$1"
  if [[ "${OPENSYNAPSE_OPEN_BROWSER:-0}" != "1" ]]; then
    return 0
  fi
  if command -v termux-open-url >/dev/null 2>&1; then
    termux-open-url "$url" >/dev/null 2>&1 || true
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$url" >/dev/null 2>&1 || true
  elif command -v open >/dev/null 2>&1; then
    open "$url" >/dev/null 2>&1 || true
  fi
}

print_chatgpt_settings() {
  local tunnel_id="$1"
  cat <<TXT

=== ChatGPT one-time plugin settings ===
Open: $CHATGPT_PLUGINS_URL
Name: OpenSynapse Main
Connection: Tunnel
Tunnel: $tunnel_id
Authentication: None / No authentication
Acknowledge the custom MCP risk notice, then create/connect the plugin.

Final verification prompt:
OpenSynapse Main을 사용해서 내 OpenSynapse 작업공간 상태를 확인하고, OPENSYNAPSE_E2E.txt 파일을 생성한 뒤 다시 읽어서 내용과 SHA-256이 일치하는지 검증해.
TXT
}

write_state() {
  local tunnel_id="$1" status="$2"
  mkdir -p "$(dirname "$STATE_FILE")"
  chmod 700 "$(dirname "$STATE_FILE")"
  python3 - "$STATE_FILE" "$tunnel_id" "$status" <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path
p=Path(sys.argv[1])
obj={
  "product":"OpenSynapse",
  "provider":"openai-secure-mcp-tunnel",
  "tunnel_id":sys.argv[2],
  "local_status":sys.argv[3],
  "updated_at":datetime.now(timezone.utc).isoformat(),
  "secret_stored_here":False,
}
p.write_text(json.dumps(obj, indent=2)+"\n", encoding="utf-8")
p.chmod(0o600)
PY
}

show_status() {
  echo "=== OpenSynapse onboarding status ==="
  if [[ -f "$STATE_FILE" ]]; then
    cat "$STATE_FILE"
  else
    echo "No onboarding state file yet: $STATE_FILE"
  fi
  if [[ -x "$BIN_DIR/opensynapse" ]]; then
    echo
    echo "=== OpenSynapse node ==="
    "$BIN_DIR/opensynapse" status || true
    echo
    echo "=== Tunnel autostart ==="
    "$BIN_DIR/opensynapse" autostart status || true
  fi
}

if [[ "${1:-}" == "--status" ]]; then
  show_status
  exit 0
fi

TUNNEL_ID="${1:-}"
cat <<TXT
OpenSynapse guided ChatGPT onboarding

This flow keeps the raw runtime API key on this machine. Do not paste the key into ChatGPT or a shell command.

1) Create an OpenAI Tunnel and include the ChatGPT workspace you will use:
   $TUNNELS_URL

2) Create a Restricted runtime API key with Tunnels Read + Use:
   $KEYS_URL

Official Secure MCP Tunnel guide:
   $DOCS_URL
TXT

open_url "$TUNNELS_URL"
open_url "$KEYS_URL"

if [[ -z "$TUNNEL_ID" ]]; then
  printf '\nPaste the tunnel ID (tunnel_...): ' >/dev/tty
  IFS= read -r TUNNEL_ID </dev/tty
fi
if [[ ! "$TUNNEL_ID" =~ ^tunnel_[0-9a-f]{32}$ ]]; then
  echo "ERROR: tunnel ID must look like tunnel_<32 lowercase hex>." >&2
  exit 2
fi

write_state "$TUNNEL_ID" "CONNECTING"

echo
echo "3) Preparing the local OpenSynapse node, validating Tunnel Doctor, and enabling recovery..."
curl -fsSL "$CONNECT_URL" | bash -s -- "$TUNNEL_ID"

LOCAL_STATUS="CONNECTED"
if [[ -x "$BIN_DIR/opensynapse" ]]; then
  AUTOSTART_JSON="$("$BIN_DIR/opensynapse" autostart status 2>/dev/null || true)"
  if grep -Eq '"reboot_recovery"[[:space:]]*:[[:space:]]*"READY"' <<<"$AUTOSTART_JSON"; then
    LOCAL_STATUS="CONNECTED_AUTOSTART_READY"
  elif grep -Eq '"reboot_recovery"[[:space:]]*:[[:space:]]*"READY_AFTER_LOGIN"' <<<"$AUTOSTART_JSON"; then
    LOCAL_STATUS="CONNECTED_AUTOSTART_AFTER_LOGIN"
  fi
fi
write_state "$TUNNEL_ID" "$LOCAL_STATUS"

open_url "$CHATGPT_PLUGINS_URL"
print_chatgpt_settings "$TUNNEL_ID"

echo
echo "Local onboarding status: $LOCAL_STATUS"
echo "Resume/check later with:"
echo "  curl -fsSL https://raw.githubusercontent.com/nslabhwan/ns-agent-reliability/main/onboard-openai.sh | bash -s -- --status"
