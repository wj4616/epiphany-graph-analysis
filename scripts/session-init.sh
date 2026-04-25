#!/usr/bin/env bash
# session-init.sh — epiphany-graph-analysis v1.0.0
# Usage: session-init.sh <session_dir_or_base>
#
# Two-mode behavior:
#   1) Path looks like a session id (basename matches YYYY-MM-DD-XXXX or contains
#      timestamp-style components, OR caller passed a path the orchestrator already
#      resolved): treat as the literal session dir; collision-suffix if it exists.
#   2) Path looks like a base dir (basename does not match a session id pattern,
#      e.g. "graph-analysis") AND contains no embedded session id: generate a fresh
#      session_id (YYYY-MM-DDTHH-MM-SS + 4-hex nonce) and append it.
#
# Dual-input model: session.md records node_a_path and node_b_path fields so the
# orchestrator can reference them throughout the session.
#
# Prints the resolved directory path (stdout line 1) for orchestrator to read back.
# Called by orchestrator STEP 1.

set -euo pipefail

RAW_SESSION_DIR="${1:?Usage: session-init.sh <session_dir_or_base>}"
# Strip trailing slash if present
SESSION_DIR="${RAW_SESSION_DIR%/}"

# Detect whether SESSION_DIR is a base dir (needs session_id generation) or
# already a fully-qualified session dir.
#
# Heuristic: a session id contains a date stamp (4 digits, dash, 2 digits, dash,
# 2 digits) or an explicit "T" time separator. Anything else is treated as a base.
BASENAME="$(basename "$SESSION_DIR")"
if [[ "$BASENAME" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}([T-][0-9]) ]]; then
  # Looks like a session id already — caller resolved it.
  :
else
  # Generate a session id and append.
  NONCE=$(printf '%04x' $((RANDOM % 65536)))
  SESSION_ID_GEN="$(date '+%Y-%m-%dT%H-%M-%S')-${NONCE}"
  SESSION_DIR="${SESSION_DIR}/${SESSION_ID_GEN}"
fi

# Collision safety: if dir exists, append -N suffix
if [ -d "$SESSION_DIR" ]; then
  N=1
  while [ -d "${SESSION_DIR}-${N}" ]; do
    N=$((N+1))
  done
  SESSION_DIR="${SESSION_DIR}-${N}"
fi

SESSION_ID="$(basename "$SESSION_DIR")"
STAGES_DIR="${SESSION_DIR}/stages"

mkdir -p "${STAGES_DIR}"

TIMESTAMP=$(date '+%Y-%m-%dT%H:%M:%S')
START_EPOCH=$(date +%s)

# session.md is YAML-ish key:value. Orchestrator (STEP 1.3) overwrites scale +
# modifiers with the actual run-time values. Other fields are append/incremental.
# node_a_path and node_b_path are written by the orchestrator after capturing
# user inputs in STEP 1 — they are left as placeholder strings here.
cat > "${STAGES_DIR}/session.md" << EOF
session_id: ${SESSION_ID}
timestamp: ${TIMESTAMP}
wall_seconds_start: ${START_EPOCH}
session_dir: ${SESSION_DIR}/
stages_dir: ${STAGES_DIR}/
scale: TBD
node_a_path: TBD
node_b_path: TBD
node_b_type: null
modifiers: []
spawns_total: 0
executed_nodes: []
back_edges_fired: []
abort_reason: null
warnings: []
verbose_trace: []
EOF

# Line 1 = resolved dir so the orchestrator can capture the final path
echo "${SESSION_DIR}"
echo "Session initialized: ${SESSION_DIR}"
echo "Stages directory: ${STAGES_DIR}"
