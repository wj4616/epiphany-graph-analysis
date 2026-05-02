# Changelog

## [1.0.2] — 2026-04-29

### Pass 2 Audit Fixes

- **Top-level artifact writers wired**: SKILL.md §4.0 now extracts `ideas-catalog.md`, `accepted-ideas-catalog.md`, `solution-catalog.md`, `dropped-by-budget.md` (conditional), `synthesis-decisions.md`, `self-audit.md`, `expansion-pass.md` (DEEP+E25 only) from their stage files into top-level session artifacts per spec §4. Previously these were never written despite being declared mandatory.
- **B3 finished**: scrubbed all remaining `verification_report` references after the rename to `first_pass_verified` — `modules/N12-expand.md` (input_dependencies + protocol), `graph.json` E25 `gate_condition`, `docs/2026-04-29-design.md` lines 378-379 + line 825 enum.
- **B4 finished**: `SKILL.md §3.6` now captures **both** `(N7, falsification_result)` and `(N7, adversarial_digest)` from the spawn output. Previously the orchestrator wrote only the first.
- **B5 finished**: `modules/N9-router.md` frontmatter `context_budget_lines` raised 50→100 to match graph.json (drift fix); also added the missing standard stage frontmatter template.
- **KB taxonomy aligned**: `kb/section-tailoring-map.md` rewritten around the genius-minds canonical 10 sections (Headline Insight, Theory Collisions, Discovery vs. Proof, Independence-Verified Bridges, Alternative Hypotheses, Density-Checked Falsification, Scope Limits, Coherence Signals, Generalization Checks, Open Questions & Next Probes) — was using a generic-analysis taxonomy that didn't match N1's classification. N3 module references updated to match.
- **KB legacy contamination cleaned**: `kb/verification-gates.md` replaced with V1-V8-aligned content; removed legacy V1-V7 references to nonexistent `SKILL.md STEP 3c` and `stages/N7-v6-scope.txt`.
- **Flag rejection logic added**: `SKILL.md §0.1` now contains the spec §8.1 mode rejection matrix with verbatim Appendix E error messages (`--minimal`, conflicting scale flags, threshold inversion, conflicting verbosity, resume scale mismatch, etc.).
- **N5.5 zero-xref edge case**: thin-pool threshold changed to `max(1, ⌈xref_count × 0.4⌉)` so sparse pipelines (xref_count=0) still raise S5 when no accepted ideas exist. Fixed protocol/template drift (template said "5 ideas" while protocol said `min(20, ⌈1.5 × len(unmapped)⌉)`).
- **HG-1 message punctuation**: changed `--` to `—` to match spec Appendix E verbatim.
- **session.json update protocol** documented in SKILL.md RESUME section: orchestrator updates `executed_nodes`/`signal_state`/`back_edges_enqueued`/`failed_spawns`/`last_updated_at` after every node completion via atomic `.tmp` rename. Previously `last_updated_at` was set once and never refreshed; resume couldn't reconstruct mid-run state.
- **`enhancement_summary` now in `signal_field_enum`**: previously a side-channel SIGNAL_STATE entry not declared in the enum. Added to enum and to N10's `output_signal_fields` in graph.json + N12's `optional_inputs`.
- **PRC1 validator: 7th + 8th checks added** (`scripts/validate-graph.py`):
  - **Check 7 — Signal field coverage**: every `signal_field_enum` entry has ≥1 producing edge / module + ≥1 consuming edge / module (excluding `—`). Catches dead enum entries.
  - **Check 8 — Module dependency validity**: parses module YAML frontmatter and rejects `input_dependencies` / `optional_inputs` that reference signal fields not in the enum. Would have caught the B3 partial fix at validation time.
- **Replay tests strengthened**: `tests/replay/test_resume_retry.py::TestSessionJsonStructure` now actually invokes `session-init.sh`, parses the resulting `session.json`, and asserts every spec §4.13 field is present. Previously `REQUIRED_SESSION_FIELDS` was a hand-curated list that didn't match the real schema and was never compared against a real file.
- **`test_n11_writes_e25_signal_field` strengthened**: parses N11 YAML frontmatter and inspects `output_signal_fields` instead of doing a substring match (which would have passed even if the field were only mentioned in a comment).
- **Two new validator regression tests**: `test_validator_rejects_stale_dependency_signal` and `test_validator_rejects_dead_enum_entry` — exercise checks 7 and 8 against synthetic broken graphs.
- **README updated** to v1.0.2 status; removed "implementation in progress" line.

### Test count: 117 → 122 (PRC1 = 6 → 8 checks)

## [1.0.1] — 2026-04-29

### Audit Fixes

- **N11 V1-V8 rewrite**: replaced incorrect V1-V8 set with the spec §7.2 battery (Hybrid trail completeness, Solution target verifiability, Cross-solution non-contradiction, Node A constraint preservation, Output well-formedness HARD, Artifact completeness + thin-spot, Graph-trace edge integrity HARD, Topology-driven execution HARD). Verdict aggregation switched to spec §7.3 hard/soft semantics.
- **N11 signal field**: now writes `(N11, first_pass_verified)` matching graph.json E25 (was `verification_report`). Removed orphan `gate:S11_artifact_gap` from signal_field_enum.
- **N7 adversarial_digest**: N7 now writes both `falsification_result` (E18) and `adversarial_digest` (E19) to SIGNAL_STATE.
- **N9 budget**: raised `context_budget_lines` from 50 → 100 to fit module protocol.
- **session.json schema**: session-init.sh now writes the full spec §4.13 schema (executed_nodes, signal_state, back_edges_enqueued, failed_spawns, halt_reason, verbose_trace, last_updated_at, input_paths). Atomic-write pattern via `.tmp` rename. Hardened against quote-injection via env vars.
- **Smoke test fixed**: tests/smoke/test_pipeline_execution.sh now uses positional args matching session-init.sh.
- **N10 V5 self-check + first-pass rename**: added pre-write well-formedness check (1 retry) and explicit `enhanced.md` → `enhanced-first-pass.md` rename on E26 fire.
- **N5.5 S5 threshold**: changed to spec formula `accepted_count < ceil(xref_count × 0.4)`; supplemental cap `min(20, ceil(1.5 × len(unmapped_findings)))`.
- **test-runner.sh**: now invokes `python3 -m pytest` for `.py` files; includes `unit/` category; hardened summary handling.
- **N7 hard_gates_referenced**: cleared (HG-4 was incorrect).
- **KB stale node references**: `verification-gates.md` (now N11+N8), `falsification-checklists.md` (N7), `elegance-rubric.md` (N5/N5.5/N8), `debono-techniques.md` (N5), `domain-catalog.md` (N5).

## [1.0.0] — 2026-04-29

### Initial Release

Graph-of-Thought reimplementation of `epiphany-analysis`. Full 14-node, 26-edge signal-driven graph topology with parallel spawn nodes and inline role-switched blocks.

### Architecture

- **SKILL.md**: Top-level orchestrator following `epiphany-graph-genius` pattern. Mode resolution (STANDARD/DEEP), ready-set scheduler (inline-to-fixpoint then parallel spawn fire), PRC1 pre-execution validation, signal state management, hard gate enforcement, artifact assembly.
- **graph.json**: Full topology definition — 14 nodes, 26 edges, 18 signal field enum, JSON Schema (draft-07) validation.
- **graph.schema.json**: JSON Schema for graph topology validation.

### Nodes

| ID | Name | Exec | Hat |
|----|------|------|-----|
| N1 | IntakeDecompose | inline | Einstein/Feynman |
| N2a | AnalyzeA | spawn | Tesla |
| N2b | AnalyzeB | spawn | Darwin |
| N3 | SectionTailor | inline | Feynman |
| N4 | CrossReference | inline | Tesla |
| N5 | LateralIdeate | spawn | de Bono |
| N5.5 | IdeaFilter | inline | Boden |
| N6 | Defixation | inline | Ohlsson |
| N7 | AdversarialVerify | spawn | Popper + Millikan |
| N8 | SolutionEngineer | inline | Feynman + Boden |
| N9 | Router | inline | — |
| N10 | Synthesize | spawn | Feynman + Boden |
| N11 | Verify | inline | Popper |
| N12 | Expand | inline (DEEP) | Feynman |

### Edges

26 edges: 14 required, 2 forward-conditional, 3 back-edges (E09, E20, E26), 1 gate-open, 1 terminal. Three back-edges form the pipeline safety net.

### Signals

6 signals: S1_input_complexity, S2_thin_B, S4_xref_density, S5_idea_pool_thin, S7_no_alternatives, S11_artifact_gap.

### Hard Gates

5 hard gates (HG-1 through HG-5): HG-1 through HG-4 are HALT severity; HG-5 is FAIL severity (pass rate <70%).

### Modes

- **STANDARD**: 13 active nodes, ≤6 spawns, 22 min soft / 35 min hard target.
- **DEEP**: 14 active nodes (adds N12 Expand + E26 re-synthesis loop), ≤7 spawns, 38 min soft / 55 min hard target.

### Verification Battery (per spec §7.2)

V1-V8 — V5/V7/V8 are HARD checks; failure → verdict FAIL:
- V1 — Hybrid trail completeness (soft): every ACCEPT solution has all HG-3 fields
- V2 — Solution target verifiability (soft): targets resolve to anchors in input-a.md
- V3 — Cross-solution non-contradiction (soft): N10 pre-write resolves; V3 audits
- V4 — Node A constraint preservation (soft): MUST/SHALL etc preserved verbatim or fuzzy <10%
- V5 — Output well-formedness (HARD): YAML + markdown structural balance
- V6 — Artifact completeness + thin-spot detection: solution_count / xref_count < 0.6 raises S11
- V7 — Graph-trace edge integrity (HARD): forward/back edges fired ⊆ declared edges
- V8 — Topology-driven execution (HARD): every executed node has a documented activation path

Verdict aggregation: hard-fail in {V5,V7,V8} → FAIL; else PASS/PARTIAL/FAIL by soft-fail count. HG-5 fails when pass rate < 70%.

### KB Files

- `analysis-methodology.md` — A1/B1 analysis frameworks, species classification (8 types), corroboration framework
- `section-tailoring-map.md` — 10 canonical sections with header variants and extraction strategies
- `input-preloading-templates.md` — Spawn dispatch prompt structure, context budgeting, hat-to-prompt translation
- `oppositional-drafting-axes.md` — 7 axes (A0-A6) with pole definitions and Pattern α rationale

### Scripts

- `scripts/validate-graph.py` — PRC1 validation (6 checks): JSON Schema, DAG, edge resolution, signal field validity, connectivity, KB existence
- `scripts/session-init.sh` — Session directory creation, input resolution, metadata writing
- `scripts/test-runner.sh` — 6-category test battery runner

### Tests

6 categories, 105 tests across 6 Python files + 1 shell script:
- **Smoke** (12 tests): Pipeline execution, session init, graph validation, module/KB completeness
- **Signal** (20 tests): S1-S11 raise conditions, propagation integrity, edge references, no orphan signals
- **HG** (17 tests): HG-1 through HG-5 enforcement, path separation, write confinement, pass rate calculation
- **Verification** (18 tests): V1-V8 definitions, N11 protocol, weighted pass rate, DEEP re-verify loop
- **Regression** (24 tests): Empty inputs, budget boundaries, DAG invariants, fixture consistency, S1 formula boundaries, scale gate consistency
- **Replay** (18 tests): --resume and --retry-failed flags, session.json structure, SIGNAL_STATE preservation
- **Unit** (4 tests): Graph schema validation (accept good, reject missing target, reject invalid signal field, reject cycle)

### Fixtures

- `node-a-low.md` — Low-complexity Node A for smoke testing
- `node-a-high.md` — High-complexity Node A with deep nesting and many constraints
- `node-b-genius.md` — Full 10-section genius-current analysis
- `node-b-drift.md` — Partial genius-drift analysis
- `node-b-generic.md` — Unstructured generic-fallback analysis
