#!/usr/bin/env bash
set -euo pipefail

# session-init.sh — Create and initialize a session directory for epiphany-graph-analysis.
#
# Usage:
#   session-init.sh <output_base> <node_a> <node_b> <mode>
#
#   output_base  : e.g., ~/docs/epiphany/graph-analysis/
#   node_a       : text or file path (Node A — the original text)
#   node_b       : text or file path (Node B — the analysis), or "-" for none
#   mode         : STANDARD | DEEP
#
# Outputs to stdout:
#   SESSION_DIR=<path>
#   SESSION_ID=<id>
#   CREATED_AT=<ISO-8601>

OUTPUT_BASE="${1:?missing output_base}"
NODE_A="${2:?missing node_a}"
NODE_B="${3:--}"
MODE="${4:-STANDARD}"

# ── Resolve script location ─────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# ── Generate session ID ─────────────────────────────────────────────────
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DATE_SHORT="$(date -u +%Y-%m-%d)"
RANDOM_HEX="$(openssl rand -hex 4 2>/dev/null || python3 -c 'import secrets; print(secrets.token_hex(4))')"
SESSION_ID="${DATE_SHORT}-${RANDOM_HEX}"

# ── Create directories ──────────────────────────────────────────────────
SESSION_DIR="${OUTPUT_BASE%/}/${SESSION_ID}"
mkdir -p "${SESSION_DIR}/stages"

# ── Resolve Node A ──────────────────────────────────────────────────────
if [[ -f "$NODE_A" ]]; then
    cp "$NODE_A" "${SESSION_DIR}/input-a.md"
    echo "  [init] Node A copied from file: ${NODE_A}" >&2
    NODE_A_CLASS="file"
else
    echo "$NODE_A" > "${SESSION_DIR}/input-a.md"
    echo "  [init] Node A inlined (${#NODE_A} chars)" >&2
    NODE_A_CLASS="inline"
fi

# ── Resolve Node B ──────────────────────────────────────────────────────
if [[ "$NODE_B" == "-" ]]; then
    NODE_B_CLASS="none"
    echo "  [init] Node B not provided — N1 will substitute inline" >&2
elif [[ -f "$NODE_B" ]]; then
    cp "$NODE_B" "${SESSION_DIR}/input-b.md"
    echo "  [init] Node B copied from file: ${NODE_B}" >&2
    NODE_B_CLASS="file"
else
    echo "$NODE_B" > "${SESSION_DIR}/input-b.md"
    echo "  [init] Node B inlined (${#NODE_B} chars)" >&2
    NODE_B_CLASS="inline"
fi

# ── Write session metadata ──────────────────────────────────────────────
python3 -c "
import json, sys
meta = {
    'session_id': '${SESSION_ID}',
    'created_at': '${TIMESTAMP}',
    'mode': '${MODE}',
    'skill_version': '1.0.0',
    'node_a_source': '${NODE_A_CLASS}',
    'node_b_source': '${NODE_B_CLASS}',
    'session_dir': '${SESSION_DIR}',
    'stages_dir': '${SESSION_DIR}/stages',
}
json.dump(meta, sys.stdout, indent=2)
" > "${SESSION_DIR}/session.json"

echo "  [init] session.json written" >&2

# ── Copy graph snapshot for replay ──────────────────────────────────────
cp "${SKILL_DIR}/graph.json" "${SESSION_DIR}/graph-snapshot.json"

echo "  [init] session ${SESSION_ID} ready (mode=${MODE})" >&2

# ── Emit to stdout for the orchestrator to capture ──────────────────────
cat <<EOF
SESSION_DIR=${SESSION_DIR}
SESSION_ID=${SESSION_ID}
CREATED_AT=${TIMESTAMP}
EOF
