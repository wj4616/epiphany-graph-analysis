#!/usr/bin/env bash
# test-runner.sh — epiphany-graph-analysis v1.0.0
# Smoke test battery for the epiphany-graph-analysis skill.
#
# Usage:
#   ./test-runner.sh [--verbose]
#
# Tests:
#   T01  graph.json exists and is valid JSON
#   T02  graph.schema.json exists and is valid JSON
#   T03  All 12 node module files exist and have non-zero size
#   T04  All 8 KB files exist and have non-zero size
#   T05  session-init.sh is executable
#   T06  validate-graph.py exits 0 on full graph (no scale filter)
#   T07  validate-graph.py exits 0 for MINIMAL scale
#   T08  validate-graph.py exits 0 for STANDARD scale
#   T09  validate-graph.py exits 0 for DEEP scale
#   T10  session-init.sh creates a session dir with stages/session.md
#   T11  Node count is exactly 12
#   T12  Edge count is exactly 23 (E01-E24 minus E12)
#   T13  Back-edges E06/E16/E20 present with type back-edge
#   T14  Forward-conditional edges E04/E19 present with type forward-conditional
#   T15  Terminal edge E21 (N10->output) present
#   T16  SKILL.md exists and has non-zero size
#   T17  N6 activation is back-edge only (no forward edges targeting N6 except E06/E16)
#   T18  Signal fields S2_thin_B, S7_no_alternatives, S11_artifact_gap referenced
#
# Exit 0 = all tests pass. Exit 1 = >=1 test failed.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
GRAPH_JSON="${SKILL_DIR}/graph.json"
SCHEMA_JSON="${SKILL_DIR}/graph.schema.json"
VALIDATE_PY="${SCRIPT_DIR}/validate-graph.py"
SESSION_INIT="${SCRIPT_DIR}/session-init.sh"

VERBOSE=0
if [[ "${1:-}" == "--verbose" ]]; then
  VERBOSE=1
fi

PASS=0
FAIL=0
SKIP=0

pass() { echo "  PASS  $1"; PASS=$((PASS+1)); }
fail() { echo "  FAIL  $1"; FAIL=$((FAIL+1)); }
skip() { echo "  SKIP  $1"; SKIP=$((SKIP+1)); }

vlog() {
  if [[ $VERBOSE -eq 1 ]]; then
    echo "        $1"
  fi
}

echo "=== epiphany-graph-analysis smoke tests ==="
echo "Skill dir: ${SKILL_DIR}"
echo ""

# T01: graph.json exists and is valid JSON
echo "T01: graph.json exists and is valid JSON"
if [ -f "${GRAPH_JSON}" ] && python3 -c "import json; json.load(open('${GRAPH_JSON}'))" 2>/dev/null; then
  pass "T01"
else
  fail "T01: ${GRAPH_JSON} missing or invalid JSON"
fi

# T02: graph.schema.json exists and is valid JSON
echo "T02: graph.schema.json exists and is valid JSON"
if [ -f "${SCHEMA_JSON}" ] && python3 -c "import json; json.load(open('${SCHEMA_JSON}'))" 2>/dev/null; then
  pass "T02"
else
  fail "T02: ${SCHEMA_JSON} missing or invalid JSON"
fi

# T03: All 12 module files exist and have non-zero size
echo "T03: All 12 module files exist"
T03_FAIL=0
for N in N1 N2 N3 N4 N5 N6 N7 N8 N9 N10 N11 N12; do
  MODULE="${SKILL_DIR}/modules/${N}.md"
  if [ ! -s "${MODULE}" ]; then
    vlog "Missing or empty: ${MODULE}"
    T03_FAIL=$((T03_FAIL+1))
  fi
done
if [ $T03_FAIL -eq 0 ]; then
  pass "T03: all 12 module files present"
else
  fail "T03: ${T03_FAIL} module file(s) missing or empty"
fi

# T04: All 8 KB files exist
echo "T04: All 8 KB files exist"
KB_FILES=(
  "analysis-methodology.md"
  "debono-techniques.md"
  "domain-catalog.md"
  "falsification-checklists.md"
  "input-preloading-templates.md"
  "ohlsson-defixation.md"
  "section-tailoring-map.md"
  "verification-gates.md"
)
T04_FAIL=0
for KBF in "${KB_FILES[@]}"; do
  TARGET="${SKILL_DIR}/kb/${KBF}"
  if [ ! -s "${TARGET}" ]; then
    vlog "Missing or empty: ${TARGET}"
    T04_FAIL=$((T04_FAIL+1))
  fi
done
if [ $T04_FAIL -eq 0 ]; then
  pass "T04: all 8 KB files present"
else
  fail "T04: ${T04_FAIL} KB file(s) missing or empty"
fi

# T05: session-init.sh is executable
echo "T05: session-init.sh is executable"
if [ -x "${SESSION_INIT}" ]; then
  pass "T05"
else
  fail "T05: ${SESSION_INIT} not executable or missing"
fi

# T06: validate-graph.py exits 0 on full graph
echo "T06: validate-graph.py full graph validation"
if python3 "${VALIDATE_PY}" "${GRAPH_JSON}" > /dev/null 2>&1; then
  pass "T06"
else
  DETAIL=$(python3 "${VALIDATE_PY}" "${GRAPH_JSON}" 2>&1 || true)
  vlog "${DETAIL}"
  fail "T06: validate-graph.py failed on full graph"
fi

# T07: validate-graph.py MINIMAL scale
echo "T07: validate-graph.py --scale MINIMAL"
if python3 "${VALIDATE_PY}" "${GRAPH_JSON}" --scale MINIMAL > /dev/null 2>&1; then
  pass "T07"
else
  DETAIL=$(python3 "${VALIDATE_PY}" "${GRAPH_JSON}" --scale MINIMAL 2>&1 || true)
  vlog "${DETAIL}"
  fail "T07: validate-graph.py failed for MINIMAL"
fi

# T08: validate-graph.py STANDARD scale
echo "T08: validate-graph.py --scale STANDARD"
if python3 "${VALIDATE_PY}" "${GRAPH_JSON}" --scale STANDARD > /dev/null 2>&1; then
  pass "T08"
else
  DETAIL=$(python3 "${VALIDATE_PY}" "${GRAPH_JSON}" --scale STANDARD 2>&1 || true)
  vlog "${DETAIL}"
  fail "T08: validate-graph.py failed for STANDARD"
fi

# T09: validate-graph.py DEEP scale
echo "T09: validate-graph.py --scale DEEP"
if python3 "${VALIDATE_PY}" "${GRAPH_JSON}" --scale DEEP > /dev/null 2>&1; then
  pass "T09"
else
  DETAIL=$(python3 "${VALIDATE_PY}" "${GRAPH_JSON}" --scale DEEP 2>&1 || true)
  vlog "${DETAIL}"
  fail "T09: validate-graph.py failed for DEEP"
fi

# T10: session-init.sh creates a session dir with stages/session.md
echo "T10: session-init.sh creates session dir"
TMP_BASE="$(mktemp -d)"
SESSION_OUT=$("${SESSION_INIT}" "${TMP_BASE}/graph-analysis" 2>/dev/null | head -1)
if [ -f "${SESSION_OUT}/stages/session.md" ]; then
  pass "T10: session dir created at ${SESSION_OUT}"
else
  fail "T10: stages/session.md not created"
fi
rm -rf "${TMP_BASE}"

# T11: Node count is exactly 12
echo "T11: Node count = 12"
NODE_COUNT=$(python3 -c "import json; g=json.load(open('${GRAPH_JSON}')); print(len(g['nodes']))")
if [ "${NODE_COUNT}" -eq 12 ]; then
  pass "T11: ${NODE_COUNT} nodes"
else
  fail "T11: expected 12 nodes, got ${NODE_COUNT}"
fi

# T12: Edge count is exactly 23 (E01-E24 minus E12)
echo "T12: Edge count = 23"
EDGE_COUNT=$(python3 -c "import json; g=json.load(open('${GRAPH_JSON}')); print(len(g['edges']))")
if [ "${EDGE_COUNT}" -eq 23 ]; then
  pass "T12: ${EDGE_COUNT} edges"
else
  fail "T12: expected 23 edges, got ${EDGE_COUNT}"
fi

# T13: Back-edges E06/E16/E20 present with type back-edge
echo "T13: Back-edges E06/E16/E20 present"
T13_FAIL=0
for EID in E06 E16 E20; do
  ETYPE=$(python3 -c "
import json
g = json.load(open('${GRAPH_JSON}'))
e = next((x for x in g['edges'] if x['id'] == '${EID}'), None)
print(e['type'] if e else 'MISSING')
" 2>/dev/null)
  if [ "${ETYPE}" != "back-edge" ]; then
    vlog "Edge ${EID}: expected back-edge, got '${ETYPE}'"
    T13_FAIL=$((T13_FAIL+1))
  fi
done
if [ $T13_FAIL -eq 0 ]; then
  pass "T13: E06/E16/E20 all typed back-edge"
else
  fail "T13: ${T13_FAIL} back-edge(s) missing or mis-typed"
fi

# T14: Forward-conditional edges E04/E19 present
echo "T14: Forward-conditional edges E04/E19 present"
T14_FAIL=0
for EID in E04 E19; do
  ETYPE=$(python3 -c "
import json
g = json.load(open('${GRAPH_JSON}'))
e = next((x for x in g['edges'] if x['id'] == '${EID}'), None)
print(e['type'] if e else 'MISSING')
" 2>/dev/null)
  if [ "${ETYPE}" != "forward-conditional" ]; then
    vlog "Edge ${EID}: expected forward-conditional, got '${ETYPE}'"
    T14_FAIL=$((T14_FAIL+1))
  fi
done
if [ $T14_FAIL -eq 0 ]; then
  pass "T14: E04/E19 all typed forward-conditional"
else
  fail "T14: ${T14_FAIL} forward-conditional edge(s) missing or mis-typed"
fi

# T15: Terminal edge E21 (N10->output) present
echo "T15: Terminal edge E21 (N10->output) present"
E21_CHECK=$(python3 -c "
import json
g = json.load(open('${GRAPH_JSON}'))
e = next((x for x in g['edges'] if x['id'] == 'E21'), None)
if e and e['source'] == 'N10' and e['target'] == 'output' and e['type'] == 'terminal':
  print('OK')
else:
  print('FAIL')
" 2>/dev/null)
if [ "${E21_CHECK}" = "OK" ]; then
  pass "T15"
else
  fail "T15: E21 missing or not N10->output terminal"
fi

# T16: SKILL.md exists and has non-zero size
echo "T16: SKILL.md exists"
if [ -s "${SKILL_DIR}/SKILL.md" ]; then
  pass "T16"
else
  fail "T16: SKILL.md missing or empty"
fi

# T17: N6 has no forward edges targeting it except back-edges E06/E16
echo "T17: N6 is back-edge-only target (no plain forward edges)"
NON_BACK_TO_N6=$(python3 -c "
import json
g = json.load(open('${GRAPH_JSON}'))
bad = [e['id'] for e in g['edges']
       if e['target'] == 'N6' and e['type'] not in ('back-edge',) and e['id'] not in ('E06','E16')]
print(len(bad), ','.join(bad))
" 2>/dev/null)
COUNT=$(echo "${NON_BACK_TO_N6}" | cut -d' ' -f1)
if [ "${COUNT}" -eq 0 ]; then
  pass "T17: N6 only activated via back-edges"
else
  DETAILS=$(echo "${NON_BACK_TO_N6}" | cut -d' ' -f2-)
  fail "T17: non-back-edge(s) targeting N6: ${DETAILS}"
fi

# T18: Signal fields for all 3 signals are referenced in gate_conditions
echo "T18: All 3 signal names referenced in graph"
T18_FAIL=0
GRAPH_TEXT=$(python3 -c "import json; print(json.dumps(json.load(open('${GRAPH_JSON}'))))")
for SIG in S2_thin_B S7_no_alternatives S11_artifact_gap; do
  if echo "${GRAPH_TEXT}" | grep -q "${SIG}"; then
    vlog "Signal ${SIG}: found"
  else
    T18_FAIL=$((T18_FAIL+1))
    vlog "Signal ${SIG}: NOT FOUND in graph.json"
  fi
done
if [ $T18_FAIL -eq 0 ]; then
  pass "T18: all 3 signal names referenced"
else
  fail "T18: ${T18_FAIL} signal name(s) missing from graph.json"
fi

# T19: HG-1 non-overwrite text in SKILL.md
echo "T19: HG-1 and enhanced.md mentioned in SKILL.md"
if grep -q "HG-1" "${SKILL_DIR}/SKILL.md" && grep -q "enhanced.md" "${SKILL_DIR}/SKILL.md"; then
  pass "T19: HG-1 / enhanced.md found in SKILL.md"
else
  fail "T19: HG-1 or enhanced.md not found in SKILL.md"
fi

# T20: ANTI-PATTERNS section in SKILL.md
echo "T20: ANTI-PATTERNS section in SKILL.md"
if grep -q "ANTI-PATTERNS" "${SKILL_DIR}/SKILL.md"; then
  pass "T20"
else
  fail "T20: ANTI-PATTERNS section missing from SKILL.md"
fi

# T21: Early back-edge sync rule in SKILL.md
echo "T21: Early back-edge sync rule in SKILL.md"
if grep -qi "early back-edge sync" "${SKILL_DIR}/SKILL.md"; then
  pass "T21"
else
  fail "T21: Early back-edge sync rule missing from SKILL.md"
fi

# T22: E07 (N3->N4) is optional in graph.json
echo "T22: E07 (N3->N4) type = optional"
E07_TYPE=$(python3 -c "
import json
g = json.load(open('${GRAPH_JSON}'))
e = next((x for x in g['edges'] if x['id'] == 'E07'), None)
print(e['type'] if e else 'MISSING')
" 2>/dev/null)
if [ "${E07_TYPE}" = "optional" ]; then
  pass "T22: E07 is optional"
else
  fail "T22: E07 type is '${E07_TYPE}', expected 'optional'"
fi

# T23: session-init.sh writes back_edges_fired
echo "T23: session-init.sh contains back_edges_fired"
if grep -q "back_edges_fired" "${SKILL_DIR}/scripts/session-init.sh"; then
  pass "T23"
else
  fail "T23: back_edges_fired missing from session-init.sh"
fi

# T24: N10 input_dependencies does not include N12
echo "T24: N10 input_dependencies excludes N12"
N10_DEPS=$(python3 -c "
import json
g = json.load(open('${GRAPH_JSON}'))
n = next((x for x in g['nodes'] if x['id'] == 'N10'), None)
print(' '.join(n.get('input_dependencies', [])) if n else '')
" 2>/dev/null)
if echo "${N10_DEPS}" | grep -q "N12"; then
  fail "T24: N12-expand.md still in N10 input_dependencies: ${N10_DEPS}"
else
  pass "T24: N10 input_dependencies clean"
fi

echo ""
echo "=== Results ==="
echo "  Passed: ${PASS}"
echo "  Failed: ${FAIL}"
echo "  Skipped: ${SKIP}"
echo ""

if [ $FAIL -gt 0 ]; then
  echo "FAIL: ${FAIL} test(s) failed. Run with --verbose for detail."
  exit 1
else
  echo "PASS: all ${PASS} tests passed."
  exit 0
fi
