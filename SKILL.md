---
name: epiphany-graph-analysis
version: 1.0.0
description: >
  Takes an original text (Node A) and an analysis of that text (Node B),
  producing multiple analysis artifacts through a 12-node graph-of-thought
  topology with signal-driven routing, scale-gated activation, and
  ready-set scheduling. Modes: MINIMAL (2 spawns, ≤8 min), STANDARD (4
  spawns, ≤18 min), DEEP (4 spawns + inline expansion, ≤35 min).
  5 artifacts: enhanced.md, analysis-report.md, solution-catalog.md,
  self-audit.md, graph-trace.json.
trigger:
  - "/epiphany-graph-analysis"
  - user says "epiphany-graph-analysis"
skill_path: ~/.claude/skills/epiphany-graph-analysis/
kb_base: ~/.claude/skills/epiphany-graph-analysis/kb/
graph_file: ~/.claude/skills/epiphany-graph-analysis/graph.json
session_output_base: ~/docs/epiphany/graph-analysis/
---

# epiphany-graph-analysis v1.0.0 — Orchestrator

You are the **orchestrator** for the `epiphany-graph-analysis` skill. You execute a Graph-of-Thought analysis pipeline declared in `graph.json`. Some nodes run **inline** in your own context (role-switched blocks); other heavy nodes run as **subagent spawns** via the `Agent` tool.

Your job: parse flags → load graph.json + run PRC1 → init session → capture dual inputs → run the ready-set execution loop (inline-to-fixpoint then parallel spawn fire) → assemble artifacts → emit summary line. Follow STEP 0–5 exactly.

## ARCHITECTURE

- **This file (SKILL.md):** orchestrator. You are the main agent.
- **`graph.json`:** node + edge registry. Single source of truth for topology, scale gates, exec types, signal fields, and required output sections.
- **`modules/N*.md`:** per-node protocols. INLINE nodes are read by you and executed in your own context (role-switched). SPAWN nodes are dispatched via the `Agent` tool.
- **`scripts/*.sh` / `scripts/*.py`:** shell helpers (session init, validation, test runner).
- **`kb/`:** operational KB files. Read by inline nodes (in your context) or spawn nodes (in subagent contexts).

**Three-layer rule:** You never modify graph.json mid-run. Inline nodes follow their module's PROTOCOL strictly. Spawn nodes receive predecessor digests inlined in their prompt plus relevant on-disk file paths.

**Source-of-truth rule:** When a module's frontmatter and graph.json disagree about edges or scale-gating, **graph.json is authoritative**. Module frontmatter is documentary.

## CONFIGURATION

| Variable | Default | Purpose |
|----------|---------|---------|
| `{skill_path}` | `~/.claude/skills/epiphany-graph-analysis/` | Skill install location |
| `{kb_base}` | `~/.claude/skills/epiphany-graph-analysis/kb/` | KB location |
| `{graph_file}` | `~/.claude/skills/epiphany-graph-analysis/graph.json` | Graph registry |
| `{session_output_base}` | `~/docs/epiphany/graph-analysis/` | Where session folders are written |

---

## STEP 0 — FLAG RESOLUTION + GRAPH LOAD + PRC1

### 0.1 Parse flags

Accepted flags: `--minimal`, `--standard`, `--deep`, `--no-save`, `--verbose`, `--quiet`, `--resume <session_dir>`

Determine **scale**:
- `--minimal` → MINIMAL
- `--deep` → DEEP
- `--standard` or no scale flag → STANDARD (default)

Determine **modifiers**: which of `--no-save`, `--verbose`, `--quiet`, `--resume` are set.

#### Invalid combinations (HALT with explicit error):
- Two or more of {`--minimal`, `--standard`, `--deep`} set simultaneously.
- Unknown flag not in the accepted set.
- `--resume` without a `<session_dir>` positional argument.

On HALT: print `FAILED: <reason>` and stop.

#### --verbose behavior
Emit one-line progress annotation per node as it starts and completes. Also log Agent() spawn prompts to `session.md` verbose_trace field.

#### --quiet behavior
Suppress per-node progress. Summary line and "Saved to" line always print.

#### --resume behavior
`/epiphany-graph-analysis --resume <session_dir>` where `<session_dir>` is an existing session directory. Validate that `<session_dir>/stages/session.md` exists; HALT if missing.

### 0.2 Load graph.json

Read `{graph_file}`. Apply the **scale-gate filter** to nodes and edges:

A node `n` is ACTIVE iff `scale ∈ n.scale_gates` AND `(n.enabled_when is null OR condition is true)`.

An edge `e` is ACTIVE iff:
1. `e.source` node is active (or source = "input")
2. `e.target` node is active (or target = "output")
3. `e.scale_gates` includes current scale

Filter inactive nodes and edges out of the working topology.

### 0.3 PRC1 validation (inline)

Verify on the **active topology**:

1. **DAG check:** Excluding back-edges (E06, E16, E20 — identified by `type: "back-edge"`), the active subgraph contains no cycles. Run a topological sort; it must visit every active node.

2. **Edge resolution:** Every active edge's `source` and `target` resolve to a declared active node id (or `"input"` / `"output"` sentinels).

3. **Signal field validity:** Every active edge's `signal_field` is one of the declared digest names OR a gate literal (begins with `"gate:"`) OR the em-dash sentinel (`"—"`).

4. **Connectivity:** The active subgraph (back-edges INCLUDED for connectivity) is connected with N1 as source and N10→output as sink.

5. **(Optional, recommended) Mechanized check:** Run `python3 {skill_path}scripts/validate-graph.py {graph_file} --scale {SCALE}`. Exit 0 = pass.

If any check fails: HALT with explicit error. Do not proceed to STEP 1.

---

## STEP 1 — SESSION INIT + DUAL-INPUT CAPTURE

### 1.1 Invoke session-init.sh

Run:
```bash
RESOLVED_DIR=$(bash {skill_path}scripts/session-init.sh {session_output_base} | head -n1)
```

If `--resume`: pass the session_dir from the `--resume` argument.

If new session: pass `{session_output_base}`; the script generates a session_id and creates the directory.

Use `RESOLVED_DIR` as the authoritative `{session_dir}` for all subsequent steps.

### 1.2 Dual input capture

If new session (not `--resume`):

**Node A (original text):**
- Accept file path positional argument OR inline content in user's prompt.
- Write verbatim to `{session_dir}/input-a.md`.

**Node B (analysis document):**
- Accept file path positional argument.
- If missing or empty: generate inline structural analysis of Node A as substitute. Write to `{session_dir}/input-b.md`. Tag `node_b_type = "inline-substitute"`. Emit advisory: "No analysis document provided. Generating inline structural analysis as Node B substitute. For richer results, provide a dedicated analysis document."
- If provided: read file and write verbatim to `{session_dir}/input-b.md`.

**HG-1 check (CRITICAL):** Verify that `{session_dir}/enhanced.md` target path ≠ Node A source path. If equal, HALT: "HG-1 violation: Node A source path equals enhanced.md target. The skill never overwrites Node A."

### 1.3 Initialize session.md

Write `{session_dir}/stages/session.md` with the canonical schema:

```yaml
session_id: <from session-init.sh>
scale: <MINIMAL | STANDARD | DEEP>
node_a_path: <path or "inline">
node_b_path: <path or "inline-substitute">
node_b_type: <genius-current | genius-drift | generic-fallback | inline-substitute>
modifiers: [list of active flag names]
wall_seconds_start: <epoch seconds>
spawns_total: 0
executed_nodes: []
back_edges_fired: []
abort_reason: null
warnings: []
verbose_trace: []
```

If `--resume`: do NOT overwrite session.md; read existing fields and continue.

---

## STEP 2 — READY_SET INIT

### 2.1 Initial READY_SET

`READY_SET = {N1}` — N1 is the only node with no required incoming edges (other than from "input").

`SIGNAL_STATE = {}` — empty in-memory map keyed by `(node_id, signal_field)` tuples.

### 2.2 --resume rehydration

If `--resume` is set:

a. Scan `{session_dir}/stages/` for `N*-*.md` files.
b. For each found stage file: parse its signal digest(s) and populate SIGNAL_STATE[(node_id, signal_field)] = digest_text.
c. Append rehydrated node_ids to `session.md.executed_nodes`.
d. Run STEP 3e (ready-set recompute) once to seed READY_SET from rehydrated SIGNAL_STATE.

If not `--resume`: skip 2.2; READY_SET stays `{N1}`.

---

## STEP 3 — READY-SET EXECUTION LOOP

### Termination / failure HALT

At the top of each `while READY_SET ≠ ∅` iteration, check:

```
HALT condition: READY_SET is empty AND (N10 ∉ executed_nodes OR N11 ∉ executed_nodes)
```

If HALT triggers (cascade failure):
- Write to session.md: `abort_reason: "READY_SET empty before terminal; missing digests: <list>"`
- Print: `FAILED: epiphany-graph-analysis aborted — see {session_dir}/stages/session.md`
- Do NOT emit normal summary line. Stop.

### Spawn failure handling

If any `Agent()` spawn returns with an error:

1. Log to `session.md.warnings[]` with `{node_id, error_message}`.
2. Do NOT write SIGNAL_STATE for the failed node.
3. Do NOT add the failed node to `executed_nodes`.
4. Block dependents: they fail their required-edge check, cascading naturally.
5. Continue the loop with remaining nodes.
6. If the failure cascade empties READY_SET before N10 completes: HALT rule triggers.
7. **MINIMAL mode special case:** If N2 spawn fails, attempt inline fallback — run N2 protocol inline in orchestrator context (reduced quality, same output schema).

### Wall-clock budget enforcement

Track `wall_seconds_elapsed = now - wall_seconds_start`.

| Mode | Soft Target | Hard Halt |
|------|-------------|-----------|
| MINIMAL | 480s (8 min) | 900s (15 min) |
| STANDARD | 1080s (18 min) | 1800s (30 min) |
| DEEP | 2100s (35 min) | 3000s (50 min) |

Per-node hard halt: 600s (10 min).

If soft target exceeded: emit advisory in graph-trace.json. Continue.
If hard halt reached: write all current artifacts with PARTIAL status. Emit recovery guidance. Stop.

### Main loop: While READY_SET ≠ ∅

Each iteration is a "wave." Within each wave: run all inline nodes to fixpoint (3a), then compute and fire spawns in parallel (3b-3d).

#### 3a. Inline-to-fixpoint phase

```
REPEAT:
  INLINE_NODES = { n ∈ READY_SET | n.exec_type == "inline" AND n ∉ executed_nodes }
  IF INLINE_NODES is empty: BREAK
  FOR EACH n ∈ INLINE_NODES (sequentially):
    Execute n inline per 3c below.
    After completion: run 3e ready-set recompute (may surface further inline nodes).
END REPEAT
```

#### 3b. Compute SPAWN_NODES (after fixpoint)

```
SPAWN_NODES = { n ∈ READY_SET | n.exec_type == "spawn" AND n ∉ executed_nodes }
```

#### 3c. Per-inline-node execution

For each inline node `n`:

1. **Emit role-switched preamble:**
   ```
   You are now executing {n.id} ({n.type}) as {n.hat}. Read modules/{n.id}.md
   and its kb_files from {kb_base}. Node A is at {session_dir}/input-a.md.
   Node B is at {session_dir}/input-b.md.
   Execute the module's PROTOCOL. Do not reason about orchestrator state during this block.
   ```

2. **Read** `modules/{n.id}.md` and each file in `n.kb_files` (paths relative to `{kb_base}`).

3. **Execute the module's PROTOCOL.** Apply cognitive operations to inputs + predecessor digests in SIGNAL_STATE.

4. **Write full output** to `{session_dir}/{n.output_file}`.

5. **Extract signal digest(s).** Each node's PROTOCOL specifies its output digest format. Validate:
   - Required fields present: `key_findings`, `signal_flags`
   - Line count reasonable (5–20 lines)

6. **On validation failure:** log warning to `session.md.warnings[]` with `{node_id, parse_error}`. Mark digest as MISSING in SIGNAL_STATE. Block dependents. Continue.

7. **On success:** for each output digest, write `SIGNAL_STATE[(n.id, signal_field)] = digest_text`. PRC2: never overwrite an existing key.

8. **Append `n.id`** to `session.md.executed_nodes`.

9. **POST-EXECUTION BACK-EDGE CHECKS:**
   - **IF n == N2** AND `SIGNAL_STATE[(N2, analysis_digest)].signal_flags` includes `"S2_thin_B"` AND `"N6" ∉ executed_nodes`: enqueue N6 to READY_SET (E06 back-edge). Record `"E06"` in `session.md.back_edges_fired`. Single-firing cap: only enqueue if N6 not already in executed_nodes.
   - **IF n == N9**: Check `SIGNAL_STATE[(N7, falsification_result)].signal_flags` includes `"S7_no_alternatives"` AND `"N6" ∉ executed_nodes` → enqueue N6 to READY_SET (E16 back-edge). Record `"E16"` in `session.md.back_edges_fired`. Single-firing cap enforced.
   - **IF n == N11** (DEEP mode only): Check `SIGNAL_STATE[(N11, verification_report)].signal_flags` includes `"S11_artifact_gap"` AND mode == DEEP → enqueue N12 to READY_SET (E19 forward-conditional). After N12 completes: enqueue N10 back to READY_SET (E20 back-edge). Record `"E20"` in `session.md.back_edges_fired`. Cap: N12 runs ≤1 time; N10 re-runs ≤1 time in DEEP.

#### 3d. Spawn fire (after inline fixpoint)

If `SPAWN_NODES ≠ ∅`:

0. **Early back-edge sync rule:** If `SIGNAL_STATE[(N2, analysis_digest)].signal_flags` includes `"S2_thin_B"` AND `"N6" ∉ executed_nodes`, then N7 MUST NOT be included in SPAWN_NODES for this wave, even if E10 (N5→N7, required) is already satisfied. This prevents N7 from missing N6's optional breakthrough_digest via E24. N7 joins SPAWN_NODES only after N6 appears in executed_nodes.

1. **Pre-spawn budget check (HARD):** Verify `session.md.spawns_total + len(SPAWN_NODES) ≤ scale_budget` where:
   - MINIMAL: ≤2 | STANDARD: ≤4 | DEEP: ≤5
   If would exceed:
   - Write to session.md: `abort_reason: "Spawn budget exceeded: attempted {spawns_total + len(SPAWN_NODES)} of {SCALE_BUDGET} limit"`
   - Emit: `FAILED: spawn budget exceeded (HARD limit) — see {session_dir}/stages/session.md`
   - HALT. Do not fire any spawns in this wave.

2. **Construct spawn prompts** for all nodes in SPAWN_NODES. Template:
   ```
   You are executing {n.id} ({n.type}) as {n.hat} for the epiphany-graph-analysis pipeline.

   Session directory: {session_dir}
   Module file path: {skill_path}modules/{n.id}.md
   Scale: {scale}
   Node A path: {session_dir}/input-a.md
   Node B path: {session_dir}/input-b.md
   node_b_type: {node_b_type}

   Predecessor digests (inlined from SIGNAL_STATE):
     {for each required incoming edge: emit predecessor digest verbatim}
     {for each optional incoming edge whose source is in executed_nodes: emit [OPTIONAL] digest}

   Instructions: Execute the PROTOCOL in your module file. Read your kb_files from {kb_base}.
   Write your full output to {session_dir}/{n.output_file}.
   Return a SIGNAL OUTPUT block with your digest(s).
   ```

3. **Fire all spawns in parallel.** In a SINGLE message, emit all `Agent()` calls (one per node in SPAWN_NODES).

4. **Wait for all returns.** Parse each subagent's SIGNAL OUTPUT block.

5. **For each return:**
   - On success: write `SIGNAL_STATE[(n.id, signal_field)] = digest_text`. Append `n.id` to `executed_nodes`.
   - On failure (EC): apply spawn failure handling above.

6. **Increment** `session.md.spawns_total` by `len(SPAWN_NODES)`.

#### 3e. READY_SET recompute

For each active node `n` NOT in `executed_nodes`:

- **Back-edge-only-target rule (CRITICAL):** If `n`'s ONLY incoming edges are `type: "back-edge"`, `n` is NEVER activated by the standard rule. `n` activates ONLY via explicit enqueue from STEP 3c post-execution checks. (N6 is the back-edge target in this graph.)

- **Required edges:** Every `required` incoming edge to `n` must have `SIGNAL_STATE[(edge.source, edge.signal_field)]` present.

- **Forward-conditional edges:** Evaluate gate condition against current SIGNAL_STATE at ready-set compute time. If gate condition fails, edge is treated as blocking (node cannot activate via this path).
  - E04 gate: `SIGNAL_STATE[(N1, intake_digest)].node_b_type in ['genius-current', 'genius-drift']`
  - E19 gate: `SIGNAL_STATE[(N11, first_pass_verified)].signal_flags includes 'S11_artifact_gap' AND mode=DEEP`

- **Gate-open edges:** Resolve unconditionally once source has executed.

- **Optional edges:** Never block activation.

- **N3 activation:** N3 (SectionTailor) activates only when E04 (N2→N3, forward-conditional) gate condition is TRUE — i.e., node_b_type is 'genius-current' or 'genius-drift'. For generic-fallback Node B, E04 gate fails, N3 is skipped entirely, and E07 (N3→N4, optional) never fires. N4 then activates from E05 (N2→N4, required) alone. N3 also receives E23 (N1→N3, optional) which provides Node A context directly.

- **N8 activation in STANDARD/DEEP:** Requires BOTH E09 (xref_map from N4) AND E11 (ideas_digest from N5). Also requires gate-open E17 (from N9). Optional: E22 (adversarial_digest from N7) and E13 (breakthrough_digest from N6).

- **N8 activation in MINIMAL:** E11 is inactive (N5 not active). N8 activates on E09 alone (from N4).

If all required + gate-open checks pass AND forward-conditional gates evaluate true AND back-edge-only rule does not exclude AND `n ∉ executed_nodes`: add `n` to READY_SET.

Remove just-executed nodes from READY_SET.

#### Terminal condition

Pipeline ends when E21 (N10→output terminal edge) fires (N10 completes) AND N11 has completed verification. Exit the while loop and proceed to STEP 4.

---

## STEP 4 — ARTIFACT ASSEMBLY

The orchestrator assembles two of the five artifacts from node stage outputs.

### 4.1 Assemble analysis-report.md

Read:
- `{session_dir}/stages/N2-dual-analyze.md` — extract A1 structural analysis and B1 findings sections
- `{session_dir}/stages/N4-cross-reference.md` — extract cross-reference map table

Write `{session_dir}/analysis-report.md`:
```yaml
---
session_id: <session_id>
node_a_source: <node_a_path>
node_b_source: <node_b_path>
node_b_type: <node_b_type>
a1_section_count: <count>
b1_section_count: <count>
xref_count: <count of B-finding→A-section pairs>
---
```

Body:
- `## Section 1: Node A1 Analysis` — from N2 A1 output
- `## Section 2: Node B1 Analysis` — from N2/N3 B1 output
- `## Section 3: Cross-Reference Map` — from N4 output (table format)

### 4.2 Assemble graph-trace.json

Collect from runtime state:
- session_id, scale, node_b_type
- n3_activated: whether N3 appeared in executed_nodes
- executed_nodes: list in execution order
- signal_state: snapshot of SIGNAL_STATE dict (serialize tuples as "N1/intake_digest" keys)
- spawn_count: session.md.spawns_total
- wall_clock_seconds: now - wall_seconds_start
- back_edges_fired: session.md.back_edges_fired
- node_timings: {node_id: {start, end, type}} for each executed node

Write `{session_dir}/graph-trace.json`.

---

## STEP 5 — OUTPUT + SUMMARY

### 5.1 Write all 5 artifacts

Verify all 5 artifacts exist in `{session_dir}/`:

1. `enhanced.md` — written by N10
2. `analysis-report.md` — assembled by orchestrator in STEP 4.1
3. `solution-catalog.md` — written by N8
4. `self-audit.md` — written by N11
5. `graph-trace.json` — assembled by orchestrator in STEP 4.2

If any artifact is missing: log to `session.md.warnings[]`. Mark session as PARTIAL.

### 5.2 Emit completion summary line (always, even under --quiet)

```
epiphany-graph-analysis completed: [PASS|PARTIAL|FAIL] | scale=[MINIMAL|STANDARD|DEEP] | spawns=[N] | wall-clock=[X]s | artifacts=[enhanced.md, analysis-report.md, solution-catalog.md, self-audit.md, graph-trace.json]
```

Determine verdict:
- PASS: all 5 artifacts present + N11 self-audit reports PASS
- PARTIAL: all 5 artifacts present but N11 reports PARTIAL, or some artifacts have warnings
- FAIL: critical artifacts missing or N11 reports FAIL

### 5.3 Print save location

If NOT `--no-save`:
```
Session: {session_dir}
```

---

## HARD GATES (enforced at listed checkpoints)

1. **HG-1 — Output ≠ Input (STEP 1.2):** enhanced.md target path ≠ Node A source path. Abort before any work if equal.
2. **HG-2 — Self-contained runtime (all steps):** No web search, grep, glob, or user questions once N1 starts. Runtime is deterministic w.r.t. (Node A, Node B).
3. **HG-3 — Two-drafts-per-solution (N8):** N8 never writes a solution from a single draft. Two independently-drafted solutions compared, or solution candidate is dropped. No exceptions.
4. **HG-4 — Fresh copy only (STEP 1.2):** All outputs in session directory. Never write to Node A's directory.
5. **HG-5 — Bounded iteration (N5, N6, N12):** Ideation: ≤3 passes, ≤50 ideas. Defixation: ≤1 back-edge firing per trigger (E06 and E16 are mutually exclusive). Expansion: ≤1 pass. No unbounded constructs.

---

## ANTI-PATTERNS

1. DO NOT remove, paraphrase, or summarize any directive from Node A or Node B — verbatim preservation.
2. DO NOT introduce infinite loops — every iterate rule has a termination condition.
3. DO NOT overengineer — must be realistic to implement without overcomplexity.
4. DO NOT cause regression or loss of information from Node A during integration.
5. DO NOT overwrite the original Node A.
6. DO NOT assume a literal persistent database — stage files are markdown.
7. DO NOT let the runtime ask the user questions or perform external research.
8. DO NOT generate solutions outside the two-drafts-pick-best protocol (HG-3).
9. DO NOT treat Alternative Hypotheses as multiple competing ideas — only best-fit.
10. DO NOT pick a section list at runtime by guessing — use Genius Detection + Section-Tailoring Map.
11. DO NOT run all stages regardless of input complexity — use signal-driven routing to skip unnecessary work.
12. DO NOT run ideation sequentially with analysis — use N2 internal parallelism and ready-set scheduling for independent nodes.
13. DO NOT treat defixation as always-necessary — only trigger via back-edge signals (E06 or E16).

---

## SIGNAL SYSTEM REFERENCE

| Signal | Raised By | Condition | Effect |
|--------|-----------|-----------|--------|
| S2_thin_B | N2 | Node B is generic-fallback OR <3 canonical genius sections | E06 back-edge → N6 defixation; E04 gate condition fails → N3 skipped |
| S7_no_alternatives | N7 | All solution candidates survive falsification with no counter-examples | E16 back-edge (via N9) → N6 defixation if N6 hasn't run |
| S11_artifact_gap | N11 | R1-R5 pass but R6 reveals artifact gaps in DEEP mode | E19 → N12 expansion pass → E20 back-edge → N10 re-synthesis |

**Back-edge single-firing caps (HG-5):**
- E06 fires once if S2_thin_B raised (N2→N6)
- E16 fires once if S7_no_alternatives raised AND N6 not yet in executed_nodes (N9→N6)
- E06 and E16 are mutually exclusive: if E06 fires N6, E16's gate condition `'N6' not in executed_nodes` fails → E16 cannot fire
- E20 fires once after N12 expansion (N12→N10)

---

## SIGNAL_STATE INVARIANT (PRC2)

SIGNAL_STATE is **append-only**. Never overwrite an existing `(node_id, signal_field)` key. Each node writes its output digest(s) upon completion. Subsequent nodes read but never modify.

---

## MODE ACTIVATION MATRIX

| Mode | Active Nodes | Spawn Budget | Wall-clock Target |
|------|-------------|-------------|-------------------|
| MINIMAL | N1, N2, N4, N8, N10, N11 | ≤2 | ≤8 min |
| STANDARD | N1-N11 (N3 conditional, N6 conditional) | ≤4 | ≤18 min |
| DEEP | N1-N12 (N3, N6 conditional; N12 conditional on S11_artifact_gap) | ≤5 | ≤35 min |

**MINIMAL:** N2(spawn) + N10(spawn) = 2 spawns
**STANDARD:** N2(spawn) + N5(spawn) + N7(spawn) + N10(spawn) = 4 spawns
**DEEP:** Same 4 spawns; N12 is inline ≤5 cap satisfied.
