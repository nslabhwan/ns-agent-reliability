#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${OPENSYNAPSE_WORKSPACE:-$HOME/OpenSynapseWorkspace}"
BIN_DIR="${OPENSYNAPSE_BIN_DIR:-$HOME/.local/bin}"
CONFIG="${OPENSYNAPSE_CONFIG:-$HOME/.config/opensynapse/config.json}"
INSTALL_URL="https://raw.githubusercontent.com/nslabhwan/ns-agent-reliability/main/install.sh"

mkdir -p "$WORKSPACE"

echo "[1/3] Installing OpenSynapse with the bounded demo health check..."
curl -fsSL "$INSTALL_URL" | env \
  OPENSYNAPSE_ROOT="$WORKSPACE" \
  OPENSYNAPSE_WRITE_ROOT="$WORKSPACE" \
  OPENSYNAPSE_ENABLE_SAFE_COMMANDS=1 \
  OPENSYNAPSE_BIN_DIR="$BIN_DIR" \
  OPENSYNAPSE_CONFIG="$CONFIG" \
  bash

echo "[2/3] Seeding a deliberately broken service inside the isolated workspace..."
"$BIN_DIR/opensynapse" demo \
  --scenario server-recovery \
  --config "$CONFIG" \
  --workspace "$WORKSPACE"

echo "[3/3] Ready for the AI recovery run."
echo
echo "Ask your connected AI client:"
echo "Recover the broken service in $WORKSPACE/server-recovery-demo."
echo "Read the log and config, make the smallest required change, then run demohealth."
echo "Only report success if demohealth returns HEALTHY."
echo
echo "This scenario never touches a real system service. It is an isolated proof of"
echo "log -> diagnosis -> bounded config repair -> independent health verification."
