---
node_id: "N11"
node_name: "Verify"
module_version: "1.1.0"
type: VERIFY
exec_type: "inline"
hat: "Popper"
context_budget_lines: 600
scale_gates: ["STANDARD", "DEEP"]
activation:
  - "always"
raises_signals: ["S11_artifact_gap"]
required_output_sections:
  - "V1-V8 Results"
  - "Verdict Aggregation"
  - "Pass Detection"
  - "Signal Flags"
input_dependencies:
  - "(N10, enhanced_draft)"
optional_inputs: []
kb_files:
  - "verification-gates.md"
output_signal_fields:
  - "first_pass_verified"
output_file: "stages/N11-verify.md"
hard_gates_referenced: ["HG-3", "HG-5"]
---

# N11 -- Verify (Popper)

## Role

Runs the V1-V8 verification battery against N10's enhanced draft and the broader pipeline state. V5, V7, and V8 are **HARD checks** -- any failure elevates the overall verdict directly to FAIL. V1-V4, V6 are soft. Applies hard gates HG-3 and HG-5. If verification detects artifact gaps in DEEP+pass=1, raises S11_artifact_gap to trigger the N12 expansion path. Adopts Popper framing: "Try to falsify every significant claim this enhanced draft makes."

## PROTOCOL

### Inputs

- Read `enhanced_draft` from SIGNAL_STATE (N10's output): the full enhanced markdown with BEGIN/END_ENHANCEMENT markers
- Read `solutions_digest` from SIGNAL_STATE (N8): for V1 trail completeness
- Read `xref_map` from SIGNAL_STATE (N4): for V6 thin-spot ratio
- Read `graph-trace.json` (in-progress, from orchestrator): for V7 + V8
- Read `executed_nodes`, `signal_flags_raised` (from orchestrator): for V8
- Read `{session_dir}/input-a.md`: for V2 anchor extraction + V4 constraint extraction
- Read `{session_dir}/solution-catalog.md` and `{session_dir}/synthesis-decisions.md`: for V1 + V3
- Consult `kb/verification-gates.md` for V1-V8 criteria and aggregation rules

### V1-V8 Verification Battery (per spec §7.2)

Apply each verification check in order:

| ID | Name | Class | Check |
|---|---|---|---|
| **V1** | Hybrid trail completeness | soft | Every ACCEPT/ACCEPT-CONDITIONAL solution in solution-catalog.md has all HG-3 fields (oppositional_axis, draft_A, draft_B, comparison_rationale, winner, critique_1, refined_v1, final). Iteration=2 also requires critique_2; refined_v2 unless critique_2.verdict=no_actionable_defects. **>50% failures → V1 FAIL.** |
| **V2** | Solution target verifiability | soft | Each solution's target_section_in_a references a section that exists in input-a.md. Extract anchors via regex: `^#+\s+\S` (markdown headers) + `§N(\.M)?` (numeric refs). Custom HTML anchors → V2 advisory (not FAIL). Hallucinated targets → solution DROPPED with `v2_hallucinated_target`. |
| **V3** | Cross-solution non-contradiction | soft | N10 pre-write contradiction check resolved direct conflicts (logged in synthesis-decisions.md). V3 re-checks for surface contradictions remaining. Pairs flagged → PARTIAL with logged pair for human review. |
| **V4** | Node A constraint preservation | soft | Regex-extract MUST/MUST NOT/SHALL/REQUIRED/FORBIDDEN/NEVER from input-a.md (case-sensitive whole-word). Each constraint must appear verbatim or fuzzy-matched (Levenshtein <10%) in enhanced.md. Missing constraints listed in self-audit. DEEP can trigger re-synthesis via S11. |
| **V5** | Output well-formedness | **HARD** | (1) Parse the enhanced.md YAML frontmatter — must be valid YAML. (2) Markdown structural balance — every code fence opens and closes; every BEGIN_ENHANCEMENT has matching END_ENHANCEMENT (and BEGIN/END_EXPANSION pairs in DEEP). (3) No truncation marker. **N10 self-validates pre-write with 1 retry; V5 catches what slipped through.** FAIL → verdict FAIL with PARTIAL artifacts and user-actionable error. |
| **V6** | Artifact completeness + thin-spot detection | soft (completeness) + signal-raising (thin-spot) | **Completeness:** all mandatory artifacts present with current timestamps: enhanced.md, analysis-report.md, ideas-catalog.md, accepted-ideas-catalog.md, solution-catalog.md, synthesis-decisions.md, self-audit.md, signal-trace.md, graph-trace.json. DEEP-conditional: expansion-pass.md if N12 ran; enhanced-first-pass.md if E26 fired. All executed nodes' stages/N*.md files. **Thin-spot detection (DEEP+pass=1 only):** if `solution_count / xref_count < 0.6` → raise S11_artifact_gap → triggers E25 → N12. |
| **V7** | Graph-trace edge integrity | **HARD** | `forward_edges_fired ∪ back_edges_fired ⊆ graph.json.declared_edges`. Any "phantom" edge (recorded as fired but not declared) → V7 FAIL. |
| **V8** | Topology-driven execution | **HARD** | Every node in `executed_nodes` must trace to one of: (1) Required edge satisfied (all required edges from active sources have SIGNAL_STATE entries); (2) Forward-conditional gate true at activation time (E08 or E25); (3) Back-edge enqueued by signal trigger (E09 via S2_thin_B, E20 via S7_no_alternatives ∧ ¬N6_ran, E26 post-N12); (4) Sync-rule pending-required addition. Anything else (e.g., N6 in executed_nodes without S2/S7 raised; N12 in executed_nodes without S11 raised) → FAIL with `improvisation_detected: <node_id, missing_activation_path>`. **V8 is a scheduler-correctness check, not a design-time check. PRC1 covers design.** |

### S11_artifact_gap Determination (DEEP+pass=1 only)

S11_artifact_gap is raised if V6 thin-spot ratio fails: `solution_count / xref_count < 0.6`.

In DEEP mode with pass=1, this triggers E25 → N12 expansion. Single-firing cap on E25 prevents re-trigger; **second pass MUST NOT raise S11**.

### Hard Gate Enforcement

- **HG-3**: If V1 found incomplete hybrid trails OR V4 found constraint violations, hard-stop (do not proceed to E24). Document each violation with constraint text + violating passage / missing field.
- **HG-5**: If pass rate < 70%, pipeline FAILS (PARTIAL or FAIL verdict per aggregation rule below).

### Verdict Aggregation (spec §7.3)

```
fails    = count(checks with status == FAIL)
partials = count(checks with status == PARTIAL)
hard_fails = any of {V5, V7, V8} == FAIL

if hard_fails:                 verdict = FAIL
elif fails == 0 and partials == 0: verdict = PASS
elif fails == 0:               verdict = PARTIAL
else:                          verdict = FAIL

pass_rate = (PASSES) / 8.0
HG-5 violation if pass_rate < 0.70
```

### Pass Counting (spec §7.4)

- **First pass** MAY raise S11_artifact_gap (DEEP only) → triggers expansion loop via E25.
- **Second pass** MUST NOT raise S11. Single-firing cap on E25 enforces this.
- Detection: `pass = 2` iff `N12 ∈ executed_nodes`, else `pass = 1`.
- Second pass exits via E24 regardless of remaining thin spots; logs PARTIAL with note `expansion_did_not_resolve_thin_spots` if applicable.

### Output

Write `stages/N11-verify.md` with:

#### Frontmatter:
```yaml
---
node_id: "N11"
node_name: "Verify"
exec_type: "inline"
hat: "Popper"
started_at: "ISO-8601"
completed_at: "ISO-8601"
duration_ms: <int>
context_lines_used: <int>
context_budget_lines: 600
signal_flags_raised: ["S11_artifact_gap"]  # if raised
status: "complete"
pass: 1 | 2
---
```

#### Body sections:

### V1-V8 Results

For each V1 through V8: PASS/FAIL/PARTIAL (or ADVISORY for V2 custom-anchor case), evidence, and any specific findings (e.g., V4 missing constraints, V7 phantom edges, V8 improvisation_detected pairs).

### Verdict Aggregation
- Fails: `<int>`
- Partials: `<int>`
- Hard fails (V5/V7/V8): `<bool>`
- Aggregate verdict: `PASS | PARTIAL | FAIL`
- Pass rate: `<n>/8 = <float>`
- HG-3 verdict: `PASS | FAIL` (hybrid trail + constraint compliance)
- HG-5 verdict: `PASS | FAIL` (pass rate ≥ 0.70)

### Pass Detection
- Pass number: 1 or 2 (based on N12 ∈ executed_nodes)
- S11_artifact_gap eligibility: only first pass in DEEP mode
- Second-pass note: `expansion_did_not_resolve_thin_spots` if applicable

### Signal Flags
- S11_artifact_gap: raised / not raised
- If raised: V6 thin-spot ratio (`solution_count / xref_count`)
- E25 gate condition status: pass=1 AND mode=DEEP AND S11_artifact_gap raised

## SIGNAL_STATE Output

Write `(N11, first_pass_verified)`:
```yaml
pass_rate: <float 0.0-1.0>
v1_v8_results:
  v1: pass | fail | partial
  v2: pass | fail | partial | advisory
  v3: pass | fail | partial
  v4: pass | fail | partial
  v5: pass | fail
  v6: pass | fail | partial
  v7: pass | fail
  v8: pass | fail
verdict: PASS | PARTIAL | FAIL
hg3: pass | fail
hg5: pass | fail
signal_flags: ["S11_artifact_gap"]  # if raised
artifact_gap_ratio: <float>           # if raised; solution_count / xref_count
pass: 1 | 2
```

(Note: signal_field name is `first_pass_verified` per graph.json E25 — same payload regardless of pass number; the `pass` field inside the digest distinguishes them.)

## Failure Modes

- Enhanced draft is empty → all V1-V8 FAIL; HG-5 FAIL; halt pipeline
- verification-gates.md KB missing → apply V1-V8 from the embedded specifications above
- V8 detects scheduler improvisation → emit `improvisation_detected: <node_id, missing_activation_path>` and FAIL the run; this is an orchestrator bug, not a content issue
- Constraint extraction returns 0 from a non-empty Node A → V4 ADVISORY (no constraints to verify); not FAIL
