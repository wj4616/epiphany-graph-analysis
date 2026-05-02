#!/usr/bin/env bash
# Smoke test: basic pipeline execution verification
# Category: smoke
# Dependencies: SKILL.md, scripts/session-init.sh, fixtures/

set -euo pipefail

SKILL_DIR="${SKILL_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
FIXTURES="$SKILL_DIR/tests/fixtures"
RESULTS="$SKILL_DIR/tests/results"
RESULT_FILE="$RESULTS/$(date +%Y-%m-%d)-smoke-results.md"

PASSED=0
FAILED=0

pass() { echo "  ✅ PASS: $1"; PASSED=$((PASSED + 1)); }
fail() { echo "  ❌ FAIL: $1 — $2"; FAILED=$((FAILED + 1)); }

echo "# Smoke Test Results — $(date)" > "$RESULT_FILE"
echo "" >> "$RESULT_FILE"

# ─── T1: session-init creates session directory ───
echo "## T1: Session Init" >> "$RESULT_FILE"
echo "" >> "$RESULT_FILE"

SMOKE_OUTPUT_BASE="${SMOKE_OUTPUT_BASE:-${HOME}/docs/epiphany/graph-analysis-smoke}"
mkdir -p "$SMOKE_OUTPUT_BASE"

SESSION_OUTPUT=$(bash "$SKILL_DIR/scripts/session-init.sh" \
  "$SMOKE_OUTPUT_BASE" \
  "$FIXTURES/node-a-low.md" \
  "$FIXTURES/node-b-genius.md" \
  "STANDARD" 2>&1) || {
  fail "T1-session-init" "script exited non-zero: $SESSION_OUTPUT"
  echo "FAIL: T1 — $SESSION_OUTPUT" >> "$RESULT_FILE"
}

SESSION_DIR=$(echo "$SESSION_OUTPUT" | grep '^SESSION_DIR=' | cut -d= -f2)
SESSION_ID=$(echo "$SESSION_OUTPUT" | grep '^SESSION_ID=' | cut -d= -f2)

if [[ -n "$SESSION_DIR" && -d "$SESSION_DIR" ]]; then
  pass "T1.1: session directory created at $SESSION_DIR"
  echo "✅ T1.1: session directory created" >> "$RESULT_FILE"
else
  fail "T1.1" "SESSION_DIR not found or not a directory: $SESSION_DIR"
  echo "❌ T1.1: $SESSION_DIR" >> "$RESULT_FILE"
fi

if [[ -n "$SESSION_ID" ]]; then
  pass "T1.2: session ID generated: $SESSION_ID"
  echo "✅ T1.2: session ID: $SESSION_ID" >> "$RESULT_FILE"
else
  fail "T1.2" "SESSION_ID empty"
  echo "❌ T1.2: empty SESSION_ID" >> "$RESULT_FILE"
fi

if [[ -f "$SESSION_DIR/session.json" ]]; then
  pass "T1.3: session.json written"
  echo "✅ T1.3: session.json" >> "$RESULT_FILE"
else
  fail "T1.3" "session.json missing from $SESSION_DIR"
  echo "❌ T1.3: missing session.json" >> "$RESULT_FILE"
fi

if [[ -f "$SESSION_DIR/input-a.md" ]]; then
  pass "T1.4: input-a.md copied"
  echo "✅ T1.4: input-a.md" >> "$RESULT_FILE"
else
  fail "T1.4" "input-a.md missing"
  echo "❌ T1.4: missing input-a.md" >> "$RESULT_FILE"
fi

if [[ -f "$SESSION_DIR/input-b.md" ]]; then
  pass "T1.5: input-b.md copied"
  echo "✅ T1.5: input-b.md" >> "$RESULT_FILE"
else
  fail "T1.5" "input-b.md missing"
  echo "❌ T1.5: missing input-b.md" >> "$RESULT_FILE"
fi

# ─── T2: Graph topology loads and validates ───
echo "## T2: Graph Validation" >> "$RESULT_FILE"
echo "" >> "$RESULT_FILE"

GRAPH_VALIDATION=$(python3 "$SKILL_DIR/scripts/validate-graph.py" "$SKILL_DIR/graph.json" 2>&1) || {
  fail "T2.1-graph-validation" "$GRAPH_VALIDATION"
  echo "❌ T2.1: $GRAPH_VALIDATION" >> "$RESULT_FILE"
}
if [[ $? -eq 0 ]]; then
  pass "T2.1: graph.json passes PRC1 validation"
  echo "✅ T2.1: PRC1 passed" >> "$RESULT_FILE"
fi

# ─── T3: Low-complexity Node A smoke ───
echo "## T3: Low-Complexity Node A" >> "$RESULT_FILE"
echo "" >> "$RESULT_FILE"

LOW_A_LINES=$(wc -l < "$FIXTURES/node-a-low.md")
LOW_A_CONSTRAINTS=$(grep -ci 'MUST\|SHALL\|REQUIRED' "$FIXTURES/node-a-low.md" || echo 0)

if [[ "$LOW_A_LINES" -lt 25 ]]; then
  pass "T3.1: low-complexity Node A is under 25 lines ($LOW_A_LINES lines)"
  echo "✅ T3.1: $LOW_A_LINES lines" >> "$RESULT_FILE"
else
  fail "T3.1" "expected <25 lines, got $LOW_A_LINES"
  echo "❌ T3.1: $LOW_A_LINES lines" >> "$RESULT_FILE"
fi

if [[ "$LOW_A_CONSTRAINTS" -le 3 ]]; then
  pass "T3.2: low-complexity Node A has ≤3 constraints (found $LOW_A_CONSTRAINTS)"
  echo "✅ T3.2: $LOW_A_CONSTRAINTS constraints" >> "$RESULT_FILE"
else
  fail "T3.2" "expected ≤3 constraints, got $LOW_A_CONSTRAINTS"
  echo "❌ T3.2: $LOW_A_CONSTRAINTS constraints" >> "$RESULT_FILE"
fi

# ─── T4: High-complexity Node A smoke ───
echo "## T4: High-Complexity Node A" >> "$RESULT_FILE"
echo "" >> "$RESULT_FILE"

HIGH_A_LINES=$(wc -l < "$FIXTURES/node-a-high.md")
HIGH_A_CONSTRAINTS=$(grep -ci 'MUST\|SHALL\|REQUIRED\|FORBIDDEN\|NEVER' "$FIXTURES/node-a-high.md" || echo 0)

if [[ "$HIGH_A_LINES" -gt 50 ]]; then
  pass "T4.1: high-complexity Node A is over 50 lines ($HIGH_A_LINES lines)"
  echo "✅ T4.1: $HIGH_A_LINES lines" >> "$RESULT_FILE"
else
  fail "T4.1" "expected >50 lines, got $HIGH_A_LINES"
  echo "❌ T4.1: $HIGH_A_LINES lines" >> "$RESULT_FILE"
fi

if [[ "$HIGH_A_CONSTRAINTS" -gt 10 ]]; then
  pass "T4.2: high-complexity Node A has >10 constraints (found $HIGH_A_CONSTRAINTS)"
  echo "✅ T4.2: $HIGH_A_CONSTRAINTS constraints" >> "$RESULT_FILE"
else
  fail "T4.2" "expected >10 constraints, got $HIGH_A_CONSTRAINTS"
  echo "❌ T4.2: $HIGH_A_CONSTRAINTS constraints" >> "$RESULT_FILE"
fi

# ─── T5: All module files present ───
echo "## T5: Module Completeness" >> "$RESULT_FILE"
echo "" >> "$RESULT_FILE"

EXPECTED_MODULES=(
  "N1-intake"
  "N2a-analyze-a"
  "N2b-analyze-b"
  "N3-section-tailor"
  "N4-cross-reference"
  "N5-lateral-ideate"
  "N5.5-idea-filter"
  "N6-defixation"
  "N7-adversarial-verify"
  "N8-solution-engineer"
  "N9-router"
  "N10-synthesize"
  "N11-verify"
  "N12-expand"
)

ALL_PRESENT=true
for mod in "${EXPECTED_MODULES[@]}"; do
  if [[ ! -f "$SKILL_DIR/modules/${mod}.md" ]]; then
    echo "❌ T5: missing modules/${mod}.md" >> "$RESULT_FILE"
    ALL_PRESENT=false
  fi
done

if $ALL_PRESENT; then
  pass "T5.1: all 14 module files present"
  echo "✅ T5.1: 14/14 modules present" >> "$RESULT_FILE"
else
  fail "T5.1" "some module files missing"
  echo "❌ T5.1: modules missing" >> "$RESULT_FILE"
fi

# ─── T6: KB files present ───
echo "## T6: KB Completeness" >> "$RESULT_FILE"
echo "" >> "$RESULT_FILE"

EXPECTED_KB=(
  "analysis-methodology.md"
  "section-tailoring-map.md"
  "input-preloading-templates.md"
  "oppositional-drafting-axes.md"
)

KB_ALL=true
for kb in "${EXPECTED_KB[@]}"; do
  if [[ ! -f "$SKILL_DIR/kb/${kb}" ]]; then
    echo "❌ T6: missing kb/${kb}" >> "$RESULT_FILE"
    KB_ALL=false
  fi
done

if $KB_ALL; then
  pass "T6.1: all 4 KB files present"
  echo "✅ T6.1: 4/4 KB files" >> "$RESULT_FILE"
else
  fail "T6.1" "some KB files missing"
  echo "❌ T6.1: KB files missing" >> "$RESULT_FILE"
fi

# ─── Summary ───
echo "" >> "$RESULT_FILE"
echo "---" >> "$RESULT_FILE"
echo "**Total: $((PASSED + FAILED))** | Passed: $PASSED | Failed: $FAILED" >> "$RESULT_FILE"

echo ""
echo "Smoke tests complete: $PASSED passed, $FAILED failed"
echo "Results: $RESULT_FILE"

exit $FAILED
