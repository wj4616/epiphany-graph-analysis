# Verification Gates — Operational Reference (N11, N8)

## Usage

N11 runs the V1-V8 battery against N10's enhanced draft per spec §7.2 — the canonical battery is defined in `modules/N11-verify.md` and is the source of truth. N8 references this file for the HG-3 hybrid-protocol comparison rubric. Each verification is applied as an explicit separate check; PASS / FAIL / PARTIAL recorded for each. V5, V7, V8 are HARD checks (any FAIL → verdict FAIL). HG-5 fails if pass rate < 70%.

---

## V1 — Hybrid Trail Completeness (soft)

**Purpose:** every ACCEPT / ACCEPT-CONDITIONAL solution in `solution-catalog.md` was carried through the full hybrid protocol.

**Required fields per solution:** `oppositional_axis`, `draft_A`, `draft_B`, `comparison_rationale`, `winner`, `critique_1`, `refined_v1`, `final`. Iteration=2 also requires `critique_2`; `refined_v2` unless `critique_2.verdict = no_actionable_defects`.

**Pass condition:** every accepted solution has every required field populated.
**Partial:** ≥1 accepted solution missing exactly one optional field (e.g. `critique_2` absent on iteration=1 — allowed).
**Fail:** >50% of accepted solutions missing required fields.

---

## V2 — Solution Target Verifiability (soft)

**Purpose:** every solution's `target_section_in_a` resolves to an anchor that actually exists in `input-a.md`.

**Anchor extraction:** regex `^#+\s+\S` (markdown headers) plus `§N(\.M)?` numeric refs. Custom HTML anchors → ADVISORY (not FAIL).

**Pass:** every solution target resolves.
**Fail:** any solution target hallucinated → solution DROPPED with `v2_hallucinated_target`.

---

## V3 — Cross-Solution Non-Contradiction (soft)

**Purpose:** N10's pre-write contradiction check resolved direct conflicts (logged in `synthesis-decisions.md`); V3 re-checks for surface contradictions remaining in the enhanced draft.

**Pass:** no cross-solution contradictions detected.
**Partial:** pairs flagged with logged pair for human review.
**Fail:** ≥3 unresolved direct contradictions.

---

## V4 — Node A Constraint Preservation (soft)

**Purpose:** every MUST / MUST NOT / SHALL / REQUIRED / FORBIDDEN / NEVER constraint extracted from `input-a.md` (case-sensitive whole-word) appears verbatim or fuzzy-matched (Levenshtein <10%) in `enhanced.md`.

**Pass:** all constraints preserved.
**Partial:** ≥1 constraint missing; logged in `self-audit.md`. DEEP can trigger re-synthesis via S11.
**Fail:** >25% of constraints missing.

**Edge case:** Constraint extraction returns 0 from a non-empty Node A → V4 ADVISORY (no constraints to verify); not FAIL.

---

## V5 — Output Well-Formedness (HARD)

**Purpose:** the enhanced markdown parses cleanly.

**Checks:**
1. YAML frontmatter parses (`yaml.safe_load`-able).
2. Markdown structural balance — every code fence opens and closes; every `<!-- BEGIN_ENHANCEMENT -->` has a matching `<!-- END_ENHANCEMENT -->` (and BEGIN/END_EXPANSION pairs in DEEP).
3. No truncation marker (`SYNTHESIS TRUNCATED`).

**Pass:** all three checks succeed.
**Fail:** any check fails → verdict FAIL with PARTIAL artifacts and user-actionable error. N10 self-validates pre-write with 1 retry; V5 catches what slipped through.

---

## V6 — Artifact Completeness + Thin-Spot Detection (soft + signal-raising)

**Completeness:** all mandatory artifacts present with current timestamps:
`enhanced.md`, `analysis-report.md`, `ideas-catalog.md`, `accepted-ideas-catalog.md`, `solution-catalog.md`, `synthesis-decisions.md`, `self-audit.md`, `signal-trace.md`, `graph-trace.json`. DEEP-conditional: `expansion-pass.md` if N12 ran; `enhanced-first-pass.md` if E26 fired. All executed nodes' `stages/N*.md` files.

**Thin-spot detection (DEEP + pass=1 only):** if `solution_count / xref_count < 0.6` → raise `S11_artifact_gap` → triggers E25 → N12.

**Pass:** all artifacts present; thin-spot ratio ≥ 0.6 (DEEP) or completeness check only (STANDARD).
**Partial:** completeness OK but thin-spot ratio < 0.6 in DEEP+pass=1 (raises S11 — pass-2 will retry).
**Fail:** any mandatory artifact missing.

---

## V7 — Graph-Trace Edge Integrity (HARD)

**Purpose:** every fired edge was declared in `graph.json`.

**Check:** `forward_edges_fired ∪ back_edges_fired ⊆ graph.json.declared_edges`.

**Pass:** no phantom edges.
**Fail:** any phantom edge ID recorded as fired but not in declared set → V7 FAIL.

---

## V8 — Topology-Driven Execution (HARD)

**Purpose:** every node in `executed_nodes` has a documented activation path.

**Legitimate activation paths:**
1. Required edge satisfied (all required edges from active sources have SIGNAL_STATE entries)
2. Forward-conditional gate true at activation time (E08 or E25)
3. Back-edge enqueued by signal trigger (E09 via `S2_thin_B`, E20 via `S7_no_alternatives ∧ ¬N6_ran`, E26 post-N12)
4. Sync-rule pending-required addition (e.g. late N6 re-adds N9 to ready set)

**Pass:** every executed node traces to one of the four paths.
**Fail:** any node in `executed_nodes` without a traceable path → `improvisation_detected: <node_id, missing_activation_path>`. V8 is a scheduler-correctness check, not a design-time check (PRC1 covers design).

---

## HG-3 Hybrid-Protocol Comparison Rubric (referenced by N8)

When N8 picks the winner between Draft A and Draft B for an idea, score along four axes:

- **Specificity:** which draft names concrete edits (target section, change type, content)?
- **Feasibility:** which draft can N10 actually execute as written?
- **Impact:** which draft produces a larger improvement to the enhanced draft?
- **Constraint compliance:** which draft respects Node A's MUST / MUST NOT directives?

The winning draft must beat the loser on at least two axes. If the result is a tie, prefer the more conservative draft (Pole 1 of the chosen axis).

---

## Verdict Aggregation (per spec §7.3)

```
fails       = count(checks with status == FAIL)
partials    = count(checks with status == PARTIAL)
hard_fails  = any of {V5, V7, V8} == FAIL

if hard_fails:                         verdict = FAIL
elif fails == 0 and partials == 0:     verdict = PASS
elif fails == 0:                       verdict = PARTIAL
else:                                  verdict = FAIL

pass_rate = passes / 8.0
HG-5 violation if pass_rate < 0.70
```
