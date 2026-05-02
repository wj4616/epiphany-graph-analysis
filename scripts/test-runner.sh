#!/usr/bin/env bash
set -uo pipefail

# test-runner.sh — Run the test battery for epiphany-graph-analysis.
#
# Usage:
#   test-runner.sh [--quick] [--focus=<category>]
#
# Categories: unit, smoke, signal, hg, verification, regression, replay
#
# --quick: run unit + smoke + signal only (fast path, ~2 min)
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
    CATEGORIES=(unit smoke signal)
else
    CATEGORIES=(unit smoke signal hg verification regression replay)
fi

# ── Ensure results dir exists ───────────────────────────────────────────
mkdir -p "${RESULTS_DIR}"

RESULTS_FILE="${RESULTS_DIR}/$(date -u +%Y-%m-%d)-results.md"

# ── Header ──────────────────────────────────────────────────────────────
{
    echo "# Test Results — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo ""
    echo "| Category | Tests | Passed | Failed | Duration |"
    echo "|---|---|---|---|---|"
} > "$RESULTS_FILE"

TOTAL_TESTS=0
TOTAL_PASSED=0
TOTAL_FAILED=0
FAILURES=()

run_pytest_dir() {
    # Returns: prints "<tests> <passed> <failed>" to stdout
    local dir="$1"
    local tmp
    tmp=$(mktemp)
    if python3 -m pytest "$dir" -q --no-header 2>&1 > "$tmp"; then
        :
    fi
    # Parse final summary line, e.g. "10 passed in 0.05s" or "1 failed, 9 passed"
    local passed failed
    passed=$(grep -oE '[0-9]+ passed' "$tmp" | tail -1 | grep -oE '[0-9]+' || echo 0)
    failed=$(grep -oE '[0-9]+ failed' "$tmp" | tail -1 | grep -oE '[0-9]+' || echo 0)
    passed=${passed:-0}
    failed=${failed:-0}
    local total=$((passed + failed))
    rm -f "$tmp"
    printf '%d %d %d\n' "$total" "$passed" "$failed"
}

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

    # Look for any pytest-style .py files; if any exist, run pytest on the directory
    shopt -s nullglob
    PY_FILES=("${CAT_DIR}"/*.py)
    SH_FILES=("${CAT_DIR}"/*.sh)
    shopt -u nullglob

    if (( ${#PY_FILES[@]} > 0 )); then
        read -r ptot ppass pfail < <(run_pytest_dir "$CAT_DIR")
        CAT_TESTS=$((CAT_TESTS + ptot))
        CAT_PASSED=$((CAT_PASSED + ppass))
        CAT_FAILED=$((CAT_FAILED + pfail))
        if (( pfail > 0 )); then
            FAILURES+=("${CAT}: ${pfail} pytest failure(s)")
        fi
    fi

    # Run shell tests; each script's exit code is one test
    for TEST_FILE in "${SH_FILES[@]}"; do
        CAT_TESTS=$((CAT_TESTS + 1))
        if bash "$TEST_FILE" >/dev/null 2>&1; then
            CAT_PASSED=$((CAT_PASSED + 1))
        else
            CAT_FAILED=$((CAT_FAILED + 1))
            FAILURES+=("${CAT}: $(basename "$TEST_FILE")")
        fi
    done

    CAT_END=$(date +%s)
    CAT_DURATION=$((CAT_END - CAT_START))

    echo "| ${CAT} | ${CAT_TESTS} | ${CAT_PASSED} | ${CAT_FAILED} | ${CAT_DURATION}s |" >> "$RESULTS_FILE"

    TOTAL_TESTS=$((TOTAL_TESTS + CAT_TESTS))
    TOTAL_PASSED=$((TOTAL_PASSED + CAT_PASSED))
    TOTAL_FAILED=$((TOTAL_FAILED + CAT_FAILED))
done

# ── Summary ─────────────────────────────────────────────────────────────
{
    echo ""
    echo "---"
    echo ""
    echo "## Summary"
    echo ""
    echo "| Metric | Value |"
    echo "|---|---|"
    echo "| Total tests | ${TOTAL_TESTS} |"
    echo "| Passed | ${TOTAL_PASSED} |"
    echo "| Failed | ${TOTAL_FAILED} |"
    if (( TOTAL_TESTS > 0 )); then
        echo "| Pass rate | $(awk -v p="${TOTAL_PASSED}" -v t="${TOTAL_TESTS}" 'BEGIN{printf "%.1f", p*100/t}')% |"
    fi
} >> "$RESULTS_FILE"

if (( TOTAL_FAILED > 0 )); then
    {
        echo ""
        echo "## Failures"
        for FAIL in "${FAILURES[@]}"; do
            echo "- ${FAIL}"
        done
        echo ""
        echo "**RESULT: FAIL** — ${TOTAL_FAILED} test(s) failed."
    } >> "$RESULTS_FILE"
else
    echo "" >> "$RESULTS_FILE"
    echo "**RESULT: PASS** — All ${TOTAL_TESTS} tests passed." >> "$RESULTS_FILE"
fi

echo "  [test] results → ${RESULTS_FILE}" >&2
echo "  [test] ${TOTAL_PASSED}/${TOTAL_TESTS} passed, ${TOTAL_FAILED} failed" >&2

if (( TOTAL_FAILED > 0 )); then
    exit 1
fi
