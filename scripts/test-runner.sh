#!/usr/bin/env bash
set -euo pipefail

# test-runner.sh — Run the test battery for epiphany-graph-analysis.
#
# Usage:
#   test-runner.sh [--quick] [--focus=<category>]
#
# Categories: smoke, signal, hg, verification, regression, replay
#
# --quick: run smoke + signal only (fast path, ~2 min)
# --focus=<cat>: run only that category
#
# Exit 0 if all pass; exit 1 with failure summary.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TESTS_DIR="${SKILL_DIR}/tests"
RESULTS_DIR="${TESTS_DIR}/results"

FOCUS=""
QUICK=false

for arg in "$@"; do
    case "$arg" in
        --quick) QUICK=true ;;
        --focus=*) FOCUS="${arg#--focus=}" ;;
        *) echo "Unknown argument: $arg" >&2; exit 2 ;;
    esac
done

# ── Determine which categories to run ───────────────────────────────────
if [[ -n "$FOCUS" ]]; then
    CATEGORIES=("$FOCUS")
elif $QUICK; then
    CATEGORIES=(smoke signal)
else
    CATEGORIES=(smoke signal hg verification regression replay)
fi

# ── Ensure results dir exists ───────────────────────────────────────────
mkdir -p "${RESULTS_DIR}"

RESULTS_FILE="${RESULTS_DIR}/$(date -u +%Y-%m-%d)-results.md"

# ── Header ──────────────────────────────────────────────────────────────
cat > "$RESULTS_FILE" <<EOF
# Test Results — $(date -u +%Y-%m-%dT%H:%M:%SZ)

| Category | Tests | Passed | Failed | Duration |
|---|---|---|---|---|
EOF

TOTAL_TESTS=0
TOTAL_PASSED=0
TOTAL_FAILED=0
FAILURES=()

# ── Run each category ───────────────────────────────────────────────────
for CAT in "${CATEGORIES[@]}"; do
    CAT_DIR="${TESTS_DIR}/${CAT}"
    if [[ ! -d "$CAT_DIR" ]]; then
        echo "  [skip] ${CAT}: directory not found" >&2
        echo "| ${CAT} | 0 | 0 | 0 | — |" >> "$RESULTS_FILE"
        continue
    fi

    CAT_TESTS=0
    CAT_PASSED=0
    CAT_FAILED=0
    CAT_START=$(date +%s)

    # Find and run test scripts/files in this category
    shopt -s nullglob
    for TEST_FILE in "${CAT_DIR}"/*.{sh,py,md}; do
        CAT_TESTS=$((CAT_TESTS + 1))

        case "$TEST_FILE" in
            *.sh)
                if bash "$TEST_FILE" &>/dev/null; then
                    CAT_PASSED=$((CAT_PASSED + 1))
                else
                    CAT_FAILED=$((CAT_FAILED + 1))
                    FAILURES+=("${CAT}: $(basename "$TEST_FILE")")
                fi
                ;;
            *.py)
                if python3 "$TEST_FILE" &>/dev/null; then
                    CAT_PASSED=$((CAT_PASSED + 1))
                else
                    CAT_FAILED=$((CAT_FAILED + 1))
                    FAILURES+=("${CAT}: $(basename "$TEST_FILE")")
                fi
                ;;
            *.md)
                # Markdown tests are checklists — read and verify
                # Each checked checkbox [x] = verified expectation
                TOTAL_CHECKS=$(grep -c '^\s*- \[.\]' "$TEST_FILE" 2>/dev/null || echo 0)
                CHECKED=$(grep -c '^\s*- \[[xX]\]' "$TEST_FILE" 2>/dev/null || echo 0)
                UNCHECKED=$(grep -c '^\s*- \[\s\]' "$TEST_FILE" 2>/dev/null || echo 0)
                if [[ "$UNCHECKED" -eq 0 && "$TOTAL_CHECKS" -gt 0 ]]; then
                    CAT_PASSED=$((CAT_PASSED + 1))
                elif [[ "$TOTAL_CHECKS" -eq 0 ]]; then
                    # No checklist items — not a test, skip
                    CAT_TESTS=$((CAT_TESTS - 1))
                else
                    CAT_FAILED=$((CAT_FAILED + 1))
                    FAILURES+=("${CAT}: $(basename "$TEST_FILE") (${UNCHECKED}/${TOTAL_CHECKS} unchecked)")
                fi
                ;;
        esac
    done
    shopt -u nullglob

    CAT_END=$(date +%s)
    CAT_DURATION=$((CAT_END - CAT_START))

    echo "| ${CAT} | ${CAT_TESTS} | ${CAT_PASSED} | ${CAT_FAILED} | ${CAT_DURATION}s |" >> "$RESULTS_FILE"

    TOTAL_TESTS=$((TOTAL_TESTS + CAT_TESTS))
    TOTAL_PASSED=$((TOTAL_PASSED + CAT_PASSED))
    TOTAL_FAILED=$((TOTAL_FAILED + CAT_FAILED))
done

# ── Summary ─────────────────────────────────────────────────────────────
cat >> "$RESULTS_FILE" <<EOF

---

## Summary

| Metric | Value |
|---|---|
| Total tests | ${TOTAL_TESTS} |
| Passed | ${TOTAL_PASSED} |
| Failed | ${TOTAL_FAILED} |
| Pass rate | $(awk "BEGIN {printf \"%.1f\", ${TOTAL_PASSED}*100/${TOTAL_TESTS}}")% |
EOF

if [[ "$TOTAL_FAILED" -gt 0 ]]; then
    echo "" >> "$RESULTS_FILE"
    echo "## Failures" >> "$RESULTS_FILE"
    for FAIL in "${FAILURES[@]}"; do
        echo "- ${FAIL}" >> "$RESULTS_FILE"
    done
    echo "" >> "$RESULTS_FILE"
    echo "**RESULT: FAIL** — ${TOTAL_FAILED} test(s) failed." >> "$RESULTS_FILE"
else
    echo "" >> "$RESULTS_FILE"
    echo "**RESULT: PASS** — All ${TOTAL_TESTS} tests passed." >> "$RESULTS_FILE"
fi

# ── Output ──────────────────────────────────────────────────────────────
echo "  [test] results → ${RESULTS_FILE}" >&2
echo "  [test] ${TOTAL_PASSED}/${TOTAL_TESTS} passed, ${TOTAL_FAILED} failed" >&2

if [[ "$TOTAL_FAILED" -gt 0 ]]; then
    exit 1
fi
