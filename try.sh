#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${OPENSYNAPSE_WORKSPACE:-$HOME/OpenSynapseWorkspace}"
BIN_DIR="${OPENSYNAPSE_BIN_DIR:-$HOME/.local/bin}"
CONFIG="${OPENSYNAPSE_CONFIG:-$HOME/.config/opensynapse/config.json}"
INSTALL_URL="https://raw.githubusercontent.com/nslabhwan/ns-agent-reliability/main/install.sh"

mkdir -p "$WORKSPACE"

echo "[1/3] Installing OpenSynapse into an isolated user environment..."
curl -fsSL "$INSTALL_URL" | env \
  OPENSYNAPSE_ROOT="$WORKSPACE" \
  OPENSYNAPSE_WRITE_ROOT="$WORKSPACE" \
  OPENSYNAPSE_ENABLE_SAFE_COMMANDS=1 \
  OPENSYNAPSE_BIN_DIR="$BIN_DIR" \
  OPENSYNAPSE_CONFIG="$CONFIG" \
  bash

echo "[2/3] Checking the effective access boundary..."
"$BIN_DIR/opensynapse" doctor --config "$CONFIG"

echo "[3/3] Running a real bounded write -> readback proof..."
"$BIN_DIR/opensynapse" demo --config "$CONFIG" --workspace "$WORKSPACE"

echo
echo "OpenSynapse first-value proof complete."
echo "Proof file: $WORKSPACE/OPENSYNAPSE_DEMO.txt"
echo "Next: connect your MCP client and keep work inside $WORKSPACE"
