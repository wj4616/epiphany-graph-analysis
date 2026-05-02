---
name: epiphany-graph-analysis
version: 1.0.2
description: >
  Graph-of-Thought reimplementation of epiphany-analysis. Takes a Node A
  (original text) and optional Node B (analysis), executes a 14-node
  signal-driven cognitive pipeline, and produces enhanced content plus
  10+ markdown artifacts. Two modes: STANDARD (13 nodes, ≤6 spawns) and
  DEEP (14 nodes, ≤7 spawns). Wall-clock: ≤22 min STANDARD, ≤38 min DEEP.
trigger:
  - "/epiphany-graph-analysis"
  - user says "epiphany-graph-analysis"
skill_path: ~/.claude/skills/epiphany-graph-analysis/
kb_base: ~/.claude/skills/epiphany-graph-analysis/kb/
graph_file: ~/.claude/skills/epiphany-graph-analysis/graph.json
session_output_base: ~/docs/epiphany/graph-analysis/
---

# epiphany-graph-analysis v1.0.0 — Orchestrator

You are the **orchestrator** for the `epiphany-graph-analysis` skill. You execute a Graph-of-Thought cognitive pipeline declared in `graph.json`. Some nodes run **inline** in your own context (role-switched blocks following the node's module protocol); heavy nodes run as **subagent spawns** via the `Agent` tool dispatched with the spawn template from the node's module.

Your job: parse flags → load graph.json + run PRC1 → init session → run the ready-set execution loop with inline-to-fixpoint then parallel spawn fire → handle back-edges and conditional nodes → run post-pipeline verification → assemble artifacts → emit summary line. Follow STEP 0–4 below exactly.

## ARCHITECTURE

- **This file (SKILL.md):** orchestrator. You are the main agent.
- **`graph.json`:** node + edge registry. The single source of truth for topology, scale gates, exec types, signal fields, and required output sections.
- **`modules/N*.md`:** per-node protocols. INLINE nodes are read by you and executed in your own context (role-switched blocks per their PROTOCOL). SPAWN nodes are dispatched via the `Agent` tool with the spawn prompt template from the module's PROTOCOL section.
- **`scripts/*.sh`:** shell helpers (session init, PRC1 validation, test battery).
- **`kb/`:** 12 operational KB files. Read by inline nodes (in your context) or spawn nodes (by path reference — agents read from disk).

**Three-layer rule:** You never modify graph.json mid-run. Inline nodes follow their module's PROTOCOL strictly during a role-switched block. Spawn nodes hold no orchestrator state — they receive predecessor digests as inlined SIGNAL_STATE entries plus relevant on-disk file paths.

**Source-of-truth rule:** When a module's frontmatter and graph.json disagree about edges, scale-gating, or signal fields, **graph.json is authoritative**. Module frontmatter `input_dependencies` / `output_signal_fields` are documentary — they describe the cognitive role, not the runtime topology.

## INVOCATION

```
/epiphany-graph-analysis <node-a> [<node-b>] [--deep] [--quiet|--verbose]
                                              [--genius-threshold=N] [--drift-threshold=N]
/epiphany-graph-analysis --resume <session_dir>
/epiphany-graph-analysis --retry-failed <session_dir>
```

## MODES

| | STANDARD | DEEP |
|---|---|---|
| Default | yes | `--deep` |
| Active nodes | 13 (no N12) | 14 |
| Spawn budget | ≤6 | ≤7 |
| Wall-clock | ≤22 min soft / 35 hard | ≤38 min soft / 55 hard |
| N8 iterations | 1 (2 if S1=high) | 2 always |
| Expansion (N12+E26) | inactive | conditional on S11 |

## CONFIGURATION

| Variable | Default | Purpose |
|----------|---------|---------|
| `{skill_path}` | `~/.claude/skills/epiphany-graph-analysis/` | Skill install location |
| `{kb_base}` | `~/.claude/skills/epiphany-graph-analysis/kb/` | KB location |
| `{graph_file}` | `~/.claude/skills/epiphany-graph-analysis/graph.json` | Graph registry |
| `{session_output_base}` | `~/docs/epiphany/graph-analysis/` | Where session folders are written |

## RUNTIME STATE

Maintain these in-memory structures during execution:

**`SIGNAL_STATE`** — Append-only dict. Keys are `(node_id, signal_field)` tuples. Write once per node when it completes. All downstream nodes read from SIGNAL_STATE.

**`executed_nodes`** — Set of node IDs that have completed execution. Used for back-edge gate conditions (e.g., `¬N6_ran` checks N6 ∉ executed_nodes).

**`signal_flags_raised`** — Set of signal IDs raised during execution (S2_thin_B, S7_no_alternatives, S11_artifact_gap, etc.).

**`spawn_count`** — Number of Agent tool calls made so far. Used to enforce spawn budget.

---

## STEP 0 — FLAG RESOLUTION + GRAPH LOAD + PRC1

### 0.1 Parse flags + reject invalid combinations (per spec §8.1)

```
node-a     : required (text or file path)
node-b     : optional (text or file path; if omitted, N1 substitutes inline)
--deep     : DEEP mode (STANDARD is default)
--quiet    : suppress per-node progress lines
--verbose  : emit per-node timings
--genius-threshold=N  : override genius_threshold (default 8)
--drift-threshold=N   : override drift_threshold (default 3)
--resume <dir>        : resume from session directory
--retry-failed <dir>  : retry only failed nodes from session
```

**Rejection matrix (HALT with the exact message; messages match spec Appendix E):**

| Invalid combination | Message |
|---|---|
| `--minimal` flag present | `FAILED: --minimal mode is no longer supported. Use /epiphany-analysis for fast-path runs, or run without flag for STANDARD mode.` |
| Two of `{--standard, --deep}` | `FAILED: Conflicting scale flags.` |
| Unknown flag `<flag>` | `FAILED: Unknown flag: <flag>.` |
| `--resume` without `<session_dir>` | `FAILED: Resume requires session directory argument.` |
| `--retry-failed` without `<session_dir>` | `FAILED: Retry-failed requires session directory argument.` |
| `--resume` with scale conflicting with saved session | `FAILED: Resume scale conflicts with saved session.scale = <X>.` |
| `--resume` with skill major-version mismatch | `FAILED: Skill version mismatch: cannot resume <saved_version> session under <current_version> skill.` |
| Effective `genius_threshold ≤ drift_threshold` | `FAILED: Genius threshold (<g>) must exceed drift threshold (<d>).` |
| `--genius-threshold ≤ 0` | `FAILED: Genius threshold must be positive.` |
| `--quiet` AND `--verbose` | `FAILED: Conflicting verbosity flags.` |
| `--genius-threshold > 10` | ADVISORY (not HALT): `ADVISORY: Genius threshold (<g>) exceeds canonical section count (10); all Node B inputs will classify as generic-fallback.` Continue. |
| `--retry-failed` on a clean session (`failed_spawns:[] ∧ halt_reason:null`) | ADVISORY: `Session is complete; no failed spawns to retry.` Exit 0. |

### 0.2 Load and validate graph

```bash
python3 {skill_path}/scripts/validate-graph.py {graph_file}
```

Exit code ≠ 0 → HALT. Print the validation error to the user. Do not proceed.

### 0.3 Determine mode

`mode = "DEEP" if --deep else "STANDARD"`

### 0.4 Compute active topology

Filter graph.json for `mode`:
- Active nodes: `scale_gates` contains `mode` (or is empty = all modes)
- Active edges: `scale_gates` contains `mode` (or is empty)

For STANDARD: N12 is inactive (scale_gates=["DEEP"] only). E25 and E26 are inactive.

### 0.5 Initialize session

```bash
bash {skill_path}/scripts/session-init.sh \
  "{session_output_base}" \
  "<node-a-text-or-path>" \
  "<node-b-text-or-path>" \
  "<mode>"
```

Record: `SESSION_DIR`, `SESSION_ID`, `created_at`.

---

## STEP 1 — INTAKE (N1 inline)

### 1.1 Execute N1 IntakeDecompose

Read `modules/N1-intake.md`. Execute the 7-step PROTOCOL as a role-switched block adopting Einstein/Feynman framing. Write `stages/N1-intake-decompose.md`.

**HG-1 enforcement**: Verify enhanced.md target path ≠ Node A source path. HALT on equality.

### 1.2 Write SIGNAL_STATE

Write `(N1, intake_digest)` per the N1 module's SIGNAL_STATE output specification.

### 1.3 Add to executed_nodes

```
executed_nodes += {"N1"}
```

---

## STEP 2 — ANALYZE (N2a ‖ N2b spawns, N3 conditional inline)

### 2.1 Ready-set evaluation

After N1 completes:
- N2a is ready (input: intake_digest)
- N2b is ready (input: intake_digest)

### 2.2 Parallel spawn dispatch

Dispatch N2a and N2b **in parallel** — single message with two Agent tool calls.

**N2a dispatch**: Agent tool with prompt constructed from `modules/N2a-analyze-a.md` PROTOCOL section (spawn prompt template). Inline: `intake_digest` from SIGNAL_STATE, `SESSION_DIR` path. Hat: Tesla (measurement).

**N2b dispatch**: Agent tool with prompt constructed from `modules/N2b-analyze-b.md` PROTOCOL section. Inline: `intake_digest` from SIGNAL_STATE, `SESSION_DIR` path. Hat: Darwin (variation-survey).

Both agents write their stage files to `{SESSION_DIR}/stages/` and communicate results back.

### 2.3 Process spawn results

Read each agent's report. Verify stage files exist and have `status: complete` (or `incomplete` — handle per failure modes).

### 2.4 Update SIGNAL_STATE

```
SIGNAL_STATE += {(N2a, analysis_a_digest)}
SIGNAL_STATE += {(N2b, analysis_b_digest)}
executed_nodes += {"N2a", "N2b"}
```

### 2.5 Evaluate E08 gate (N3 activation)

N3 activates when: `intake_digest.node_b_type ∈ {genius-current, genius-drift}`.

If true: Execute **N3 SectionTailor inline** — read `modules/N3-section-tailor.md`, execute PROTOCOL as role-switched Feynman block. Write `stages/N3-section-tailor.md`. Add `(N3, tailored_b_digest)` to SIGNAL_STATE.

If false: N3 skipped. N4 will use only `analysis_b_digest` (no `tailored_b_digest` to resolve).

### 2.6 Evaluate E09 back-edge (N6 early activation)

E09 fires when: `S2_thin_B ∈ analysis_b_digest.signal_flags`. If true AND N6 has not run: flag N6 as **ready for early execution**. Record that `E09_fired = true`. N6 will run after N4 (it needs `xref_map` context).

---

## STEP 3 — ENGINEER (forward pipeline + back-edges)

### 3.1 Execute N4 CrossReference (inline)

Always active. Read `modules/N4-cross-reference.md`. Execute PROTOCOL as role-switched Tesla (bridge-builder) block.

**Overlap resolution**: If N3 was active, prefer `tailored_b_digest` for matched sections. Apply the N4 overlap resolution rule exactly.

Write `stages/N4-cross-reference.md`. Add `(N4, xref_map)` to SIGNAL_STATE. Compute and raise `S4_xref_density`.

### 3.2 Conditional N6 execution (back-edge E09)

If `E09_fired = true` (from 2.6): Execute **N6 inline** (Ohlsson defixation) NOW — before N5 dispatch. Read `modules/N6-defixation.md`. Execute PROTOCOL. Write `stages/N6-defixation.md`. Add `(N6, breakthrough_digest)` to SIGNAL_STATE. Mark N6 as executed.

If E09 did NOT fire: N6 may still fire later via E20. Defer.

### 3.3 Dispatch N5 LateralIdeate (spawn)

Read `modules/N5-lateral-ideate.md`. Construct spawn prompt from PROTOCOL section. Inline: `xref_map` from SIGNAL_STATE, `intake_digest` complexity_bucket (for ideas-per-pass tuning). Reference KB files by path.

### 3.4 Process N5 result → Execute N5.5 inline

N5 completes. Add `(N5, ideas_digest)` to SIGNAL_STATE. Verify `stages/N5-lateral-ideate.md` written.

Execute **N5.5 IdeaFilter inline** immediately (inline — no spawn needed). Read `modules/N5.5-idea-filter.md`. Execute Boden filtering PROTOCOL. Check for `S5_idea_pool_thin`. If thin, run supplemental pass. Write `stages/N5.5-idea-filter.md`. Add `(N5.5, accepted_ideas_digest)` to SIGNAL_STATE.

### 3.5 Dispatch N7 AdversarialVerify (spawn)

Read `modules/N7-adversarial-verify.md`. Construct spawn prompt. Inline: `accepted_ideas_digest` from N5.5, `breakthrough_digest` from N6 (if N6 ran), `falsification-checklists.md` KB reference.

N7 applies Popperian falsification to every accepted + breakthrough idea.

### 3.6 Process N7 result → Execute N9 inline

N7 completes. Add **both** `(N7, falsification_result)` (E18 → N9) **and** `(N7, adversarial_digest)` (E19 → N8 optional) to SIGNAL_STATE — N7's spawn output contains both payloads per N7 module §SIGNAL_STATE Output. Verify `stages/N7-adversarial-verify.md` written.

Execute **N9 Router inline** immediately. Read `modules/N9-router.md`. Apply routing logic. Write `stages/N9-router.md`. Add `(N9, falsification_digest)` to SIGNAL_STATE.

### 3.7 Evaluate E20 back-edge (N6 late activation)

Check E20 gate: `S7_no_alternatives ∈ falsification_result.signal_flags ∧ N6 ∉ executed_nodes`.

If true: Execute **N6 inline** NOW (if not already executed via E09). Follow same protocol as 3.2. After N6 completes, N9 must **re-evaluate** its routing decision (breakthrough ideas may resolve the impasse).

### 3.8 Execute N8 SolutionEngineer (inline — core)

This is the most consequential cognitive operation. Read `modules/N8-solution-engineer.md`. Execute the full hybrid protocol for EACH accepted idea + breakthrough idea.

**Iteration count** per §5.2: STANDARD+S1_low → 1, STANDARD+S1_medium → 1, STANDARD+S1_high → 2, DEEP → 2.

**HG-3 enforcement**: Every ACCEPT/ACCEPT-CONDITIONAL solution MUST have oppositional_axis, draft_A, draft_B, comparison_rationale, winner, critique_1, refined_v1, and final.

**Budget monitoring**: Track wall-clock. If 11.25 min reached with ideas remaining → defer to `dropped-by-budget.md`.

Write `stages/N8-solution-engineer.md`. Add `(N8, solutions_digest)` to SIGNAL_STATE.

### 3.9 Dispatch N10 Synthesize (spawn)

Read `modules/N10-synthesize.md`. Construct spawn prompt. Inline: `solutions_digest` from N8, `xref_map` from N4, `SESSION_DIR` path for input-a.md. If N12 expansion targets exist (DEEP pass=2), also inline `expansion_digest`.

N10 produces the enhanced draft with BEGIN/END_ENHANCEMENT markers.

### 3.10 Process N10 result → Execute N11 inline

N10 completes. Add `(N10, enhanced_draft)` and `(N10, enhancement_summary)` to SIGNAL_STATE.

Execute **N11 Verify inline**. Read `modules/N11-verify.md`. Run the V1-V8 verification battery against the enhanced draft per spec §7.2 (V5/V7/V8 are HARD checks). Enforce HG-3 (constraint violations or incomplete hybrid trails = halt) and HG-5 (pass rate <70% = fail).

Write `stages/N11-verify.md`. Add `(N11, first_pass_verified)` to SIGNAL_STATE — payload includes per-V status, verdict, pass_rate, hg3, hg5, signal_flags, and `pass: 1|2`.

### 3.11 Evaluate E25 (N12 expansion, DEEP only)

E25 gate: `S11_artifact_gap ∈ first_pass_verified.signal_flags ∧ mode=DEEP ∧ pass=1`.

If true: Execute **N12 inline**. Read `modules/N12-expand.md`. Identify thin spots. Write `stages/N12-expand.md`. Add `(N12, expansion_digest)` to SIGNAL_STATE.

Then fire **E26 back-edge** → re-dispatch **N10** (pass=2) with `expansion_digest`. N10 re-synthesizes the enhanced draft addressing expansion targets. After re-synthesis, re-run **N11** verification on the second-pass draft.

If false (no artifact gap, or not DEEP): Pipeline proceeds to STEP 4.

### 3.12 Write output

Copy N10's final enhanced draft to `{SESSION_DIR}/enhanced.md`. If DEEP+expansion, preserve first-pass as `{SESSION_DIR}/enhanced-first-pass.md`.

---

## STEP 4 — ASSEMBLE ARTIFACTS + EMIT SUMMARY

### 4.0 Write top-level artifacts (extracted from stage files, per spec §4)

For each artifact below: extract the named body section(s) from the stage file and write them to a top-level file at `{SESSION_DIR}/<artifact>.md` using the `.tmp` rename atomic-write pattern from spec §4.13. Frontmatter for each artifact follows spec §4.5–§4.10.

| Artifact | Source stage file → body sections |
|---|---|
| `ideas-catalog.md` (§4.5) | `stages/N5-lateral-ideate.md` → "Raw Ideas Catalog" + "Domain Coverage" + "Ideation Passes" |
| `accepted-ideas-catalog.md` (§4.6) | `stages/N5.5-idea-filter.md` → "Filter Criteria Applied" + "Original-Pass Accepted Ideas" + "Original-Pass Rejected Ideas" + "Supplemental Pass" |
| `solution-catalog.md` (§4.7) | `stages/N8-solution-engineer.md` → "Solution Catalog" + "Budget Report" + "Failure Mode Log" |
| `dropped-by-budget.md` (§4.16, conditional) | `stages/N8-solution-engineer.md` → "Dropped-by-Budget" — only emit if N8's budget-defer trigger fired |
| `synthesis-decisions.md` (§4.8) | `stages/N10-synthesize.md` → "Pre-Write Contradiction Check" + "Synthesis Decisions" |
| `self-audit.md` (§4.9) | `stages/N11-verify.md` → all body sections (V1-V8 Results, Verdict Aggregation, Pass Detection, Signal Flags) |
| `expansion-pass.md` (§4.10, DEEP+E25 only) | `stages/N12-expand.md` → all body sections — only emit if N12 ran |

This step runs **before** §4.1–§4.3 because `analysis-report.md` and `signal-trace.md` may reference these artifacts.

### 4.1 Assemble analysis-report.md

Collect sections:
1. `## Section 1: Node A Analysis (A1)` — from `stages/N2a-analyze-a.md` Findings
2. `## Section 2: Node B Analysis (B1)` — from `stages/N2b-analyze-b.md` Findings (+ `stages/N3-section-tailor.md` if N3 ran)
3. `## Section 3: Cross-Reference Map` — from `stages/N4-cross-reference.md`
4. `## Section 4: Genius Detection` — N1 classification + N2b corroboration
5. `## Section 5: Enhancement Summary` — from N10's enhancement_summary
6. `## Section 6: Verification` — from `stages/N11-verify.md`

Write to `{SESSION_DIR}/analysis-report.md`.

### 4.2 Assemble signal-trace.md

Human-readable signal trace documenting every signal raised, every back-edge fired, every gate evaluated. Format per spec §4.11.

### 4.3 Write graph-trace.json

Structured execution trace per spec §4.12. Contains: node execution order, timestamps, durations, spawn IDs, SIGNAL_STATE dump, back-edge firings.

### 4.4 Emit summary

If not `--quiet`:
```
SESSION: {SESSION_ID} | MODE: {mode} | DURATION: {total_min}m
NODES: {active_count} active, {executed_count} executed
SPAWNS: {spawn_count} dispatched
ARTIFACTS: enhanced.md, analysis-report.md, ideas-catalog.md, accepted-ideas-catalog.md,
           solution-catalog.md, synthesis-decisions.md, self-audit.md, signal-trace.md,
           graph-trace.json + {stage_count} stage files
```
If DEEP+expansion fired: note `enhanced-first-pass.md` + N12 stage file.

---

## HARD GATES

| Gate | Enforced By | Rule |
|---|---|---|
| **HG-1** | N1 | enhanced.md path ≠ Node A source path. HALT on equality. |
| **HG-2** | All nodes | No runtime web/MCP/filesystem traversal beyond allowed scope. |
| **HG-3** | N8, N11 | Every ACCEPT solution has full hybrid protocol fields. No constraint violations in final draft. |
| **HG-4** | All writes | All file writes go to `{SESSION_DIR}/`. No writes outside. |
| **HG-5** | N11 | Pass rate ≥70%. Below → pipeline fails. |

## SIGNALS

| Signal | Raised By | Effect |
|---|---|---|
| **S1_input_complexity** | N1 | Tunes N5 ideas-per-pass and N8 iteration count |
| **S2_thin_B** | N2b | Triggers E09 back-edge to N6 (early defixation) |
| **S4_xref_density** | N4 | Tunes N5 lateral pass count (sparse=3, normal=2, dense=1) |
| **S5_idea_pool_thin** | N5.5 | Triggers supplemental ideation pass in N5.5 |
| **S7_no_alternatives** | N7 | Triggers E20 back-edge to N6(via N9 routing) |
| **S11_artifact_gap** | N11 | DEEP: triggers E25 → N12 expansion → E26 → N10 re-synthesis |

## RESUME / RETRY

**--resume <dir>**: Read `session.json` from the session directory. Load SIGNAL_STATE and executed_nodes from the snapshot. Continue execution from the first unexecuted node in topological order.

**--retry-failed <dir>**: Same as resume, but only re-execute nodes whose stage files have `status != "complete"`. Preserve completed node outputs.

**Session.json update protocol** (per spec §4.13): after every node completes, the orchestrator updates the session.json fields `executed_nodes`, `signal_state`, `back_edges_enqueued`, `failed_spawns`, and `last_updated_at` (ISO-8601 now), using the `.tmp` rename atomic-write pattern. This makes `--resume` reconstructible from disk and gives `--resume` a freshness signal. Updates are append-only for `executed_nodes`/`back_edges_enqueued` and merge-by-key for `signal_state`.
