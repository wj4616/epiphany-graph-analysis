# epiphany-graph-analysis

**Graph-of-Thought analysis skill for Claude Code.**

Takes an original text (Node A) and an analysis of that text (Node B), and produces multiple enhanced artifacts through a 12-node graph topology with signal-driven routing, scale-gated activation, and ready-set scheduling.

---

## What it does

Replaces the sequential `epiphany-analysis` pipeline with a parallel graph-of-thought execution model. Key improvements:

- **Parallel dual analysis** — Node A and Node B are analyzed simultaneously by internal sub-subagents (halves wall-clock time vs. sequential)
- **Signal-driven routing** — thin analysis, no-alternatives, and artifact gaps are detected and handled automatically via back-edge triggers
- **Scale modes** — MINIMAL (2 spawns, ≤8 min) / STANDARD (4 spawns, ≤18 min) / DEEP (4+expansion, ≤35 min)
- **Adaptive depth** — Section-Tailoring Map activates only for genius-level Node B; generic Node B takes a flat-extraction path
- **5 output artifacts** — enhanced Node A, full analysis report, solution catalog, self-audit, and execution trace

---

## Usage

```
/epiphany-graph-analysis <path-to-A> <path-to-B>
/epiphany-graph-analysis <path-to-A> <path-to-B> --minimal
/epiphany-graph-analysis <path-to-A> <path-to-B> --deep
/epiphany-graph-analysis <path-to-A>              # asks for Node B
/epiphany-graph-analysis                          # asks for both
```

**Flags:**

| Flag | Effect |
|------|--------|
| `--minimal` | Fast path: 2 spawns, ≤8 min, no ideation or adversarial testing |
| `--standard` | Default: 4 spawns, full pipeline, ≤18 min |
| `--deep` | Full pipeline + expansion pass, ≤35 min |
| `--no-save` | Skip writing session to disk |
| `--verbose` | Per-node progress annotations |
| `--quiet` | Suppress non-essential output |
| `--resume <session_dir>` | Resume from an interrupted session |

**Node B is optional.** If omitted, the skill generates an inline structural analysis of Node A and uses it as a substitute (advisory emitted). Richer results require a dedicated analysis document — ideally from `/epiphany-genius` or `/epiphany-graph-genius`.

---

## Output artifacts

All artifacts are written to `~/docs/epiphany/graph-analysis/<session-id>/`.

| Artifact | Writer | Contents |
|----------|--------|----------|
| `enhanced.md` | N10 | Fresh enhanced Node A with all accepted solutions integrated + Enhancement Summary section |
| `analysis-report.md` | Orchestrator | A1 structural analysis + B1 findings analysis + cross-reference map |
| `solution-catalog.md` | N8 | All solutions with two-draft comparisons, pro/con/utility ratings, ACCEPT/REJECT status |
| `self-audit.md` | N11 | R1–R6 verification checks with PASS/PARTIAL/FAIL verdict |
| `graph-trace.json` | Orchestrator | Execution trace: node timings, signal state, spawn count, back-edges fired |

**Non-overwrite guarantee:** `enhanced.md` is never written to Node A's directory. The skill halts (HG-1) if the target path would equal the source path.

---

## Graph topology

12 nodes, 23 edges, 3 signals across 3 scale modes.

```
input → N1 (IntakeDecompose) [inline]
           │
           ├──► N2 (DualAnalyze) [SPAWN — A1 ‖ B1 internal fan-out]
           │      │
           │      ├─[genius-current/drift]──► N3 (SectionTailor) [inline]
           │      │                               │
           │      │                    N4 (CrossReference) [inline]
           │      │◄──[S2_thin_B back-edge E06]   │
           │                                      ├──► N5 (LateralIdeate) [SPAWN]
           │                                      │      │
           │      N6 (Defixation) [inline]         ├──► N7 (AdversarialVerify) [SPAWN]
           │      (triggered by E06 or E16)        │      │
           │                                      │      ▼
           │                                      │    N9 (Router) [inline]
           │                                      │      ├──[S7_no_alternatives]──► N6 (E16)
           │                                      │      └──► gate-open to N8
           │                                      │
           │                                N8 (SolutionEngineer) [inline — two-drafts]
           │                                           │
           │                                      N10 (Synthesize) [SPAWN]
           │                                           │
           │                                      N11 (Verify) [inline]
           │                                           │
           │                         [DEEP+S11_artifact_gap]──► N12 (Expand) [inline]
           │                                                          │
           └──────────────────────────── back-edge E20 ──────────────┘
```

### Nodes

| ID | Name | Type | Exec | Hat | Budget | Scale |
|----|------|------|------|-----|--------|-------|
| N1 | IntakeDecompose | DECOMPOSITION | inline | Einstein/Feynman | 200L | MIN/STD/DEEP |
| N2 | DualAnalyze | ANALYZE | **spawn** | Tesla+Darwin | 1500L | MIN/STD/DEEP |
| N3 | SectionTailor | TAILOR | inline | Feynman | 600L | STD/DEEP (conditional) |
| N4 | CrossReference | XREF | inline | Tesla (bridge-builder) | 800L | MIN/STD/DEEP |
| N5 | LateralIdeate | LATERAL | **spawn** | de Bono | 1200L | STD/DEEP |
| N6 | Defixation | DEFIXATION | inline | Ohlsson | 700L | STD/DEEP (back-edge only) |
| N7 | AdversarialVerify | ADVERSARIAL | **spawn** | Popper+Millikan | 1500L | STD/DEEP |
| N8 | SolutionEngineer | ENGINEER | inline (role-switched) | Feynman+Boden | 1500L | MIN/STD/DEEP |
| N9 | Router | ROUTER | inline | — | 50L | STD/DEEP |
| N10 | Synthesize | SYNTHESIS | **spawn** | Feynman+Boden | 2000L | MIN/STD/DEEP |
| N11 | Verify | VERIFICATION | inline | Popper | 600L | MIN/STD/DEEP |
| N12 | Expand | EXPANSION | inline | Feynman | 800L | DEEP (conditional) |

### Signals

| Signal | Raised by | Condition | Effect |
|--------|-----------|-----------|--------|
| S2_thin_B | N2 | Node B is generic-fallback OR <3 canonical genius sections | E06 back-edge → N6 defixation; N3 skipped |
| S7_no_alternatives | N7 | All solution candidates survive falsification with no counter-examples | E16 back-edge (via N9) → N6 defixation if not yet run |
| S11_artifact_gap | N11 | R1–R5 pass but artifact gaps detected in DEEP mode | E19 → N12 expansion → E20 back-edge → N10 re-synthesis |

### Scale modes

| Mode | Flag | Active Nodes | Spawns | Wall-clock |
|------|------|--------------|--------|------------|
| MINIMAL | `--minimal` | N1, N2, N4, N8, N10, N11 | ≤2 | ≤8 min |
| STANDARD | *(default)* | N1–N11 (N3, N6 conditional) | ≤4 | ≤18 min |
| DEEP | `--deep` | N1–N12 (N3, N6, N12 conditional) | ≤5 | ≤35 min |

---

## Node B detection (Genius Detection)

N1 runs Genius Detection on Node B to classify it:

| Match count | Type | Behavior |
|-------------|------|----------|
| ≥8 canonical headers | `genius-current` | Full 10-section Section-Tailoring Map |
| 3–7 canonical headers | `genius-drift` | Section-Tailoring Map on matched sections; generic scan for unmatched |
| <3 canonical headers | `generic-fallback` | Skip Section-Tailoring Map; flat extraction; S2_thin_B raised → defixation |

Canonical headers (drift synonyms accepted): Headline Insight, Theory Collisions, Discovery vs. Proof, Independence-Verified Bridges, Alternative Hypotheses, Density-Checked Falsification, Scope Limits, Coherence Signals, Generalization Checks, Open Questions & Next Probes.

Best Node B source: output of `/epiphany-genius` or `/epiphany-graph-genius`.

---

## Hard gates

| Gate | Checkpoint | Rule |
|------|-----------|------|
| HG-1 | STEP 1 | `enhanced.md` path ≠ Node A path. Halts if equal. |
| HG-2 | All steps | No web search, grep, glob, or user questions once N1 starts. |
| HG-3 | N8 | Every solution must come from comparing two independently drafted solutions. No single-draft solutions. |
| HG-4 | STEP 1 | All outputs written to session directory. Never write to Node A's directory. |
| HG-5 | N5, N6, N12 | Bounded iteration: ideation ≤3 passes/≤50 ideas; defixation fires ≤1×; expansion ≤1 pass. |

---

## Skill structure

```
~/.claude/skills/epiphany-graph-analysis/
├── SKILL.md                    # Orchestrator (STEP 0–5)
├── graph.json                  # Node/edge registry (source of truth)
├── graph.schema.json           # JSON Schema for PRC1 validation
├── modules/
│   ├── N1.md  — N12.md        # Per-node protocols
├── kb/
│   ├── section-tailoring-map.md    # 10-section map + Genius Detection
│   ├── analysis-methodology.md     # N2 dual-analysis + A1/B1 fan-out
│   ├── input-preloading-templates.md
│   ├── ohlsson-defixation.md       # N6
│   ├── falsification-checklists.md # N7
│   ├── verification-gates.md       # N8
│   ├── domain-catalog.md           # N5
│   └── debono-techniques.md        # N5
├── scripts/
│   ├── session-init.sh         # Session directory creation
│   ├── validate-graph.py       # PRC1 validator (DAG, edges, signals, connectivity)
│   └── test-runner.sh          # 24-test smoke battery
└── tests/
    ├── README.md               # Live-execution test plan (LT-01 to LT-11)
    └── fixtures/               # Test inputs for Node A and Node B
        ├── input-a-generic.md
        ├── input-b-generic.md  # generic-fallback (triggers S2_thin_B)
        ├── input-b-genius.md   # genius-current (≥8 canonical headers)
        └── input-b-drift.md    # genius-drift (3–7 headers)
```

---

## Running tests

```bash
cd ~/.claude/skills/epiphany-graph-analysis

# Structural smoke tests (no live run needed) — 24 tests
bash scripts/test-runner.sh

# PRC1 graph validation (all 3 scales)
python3 scripts/validate-graph.py graph.json
python3 scripts/validate-graph.py graph.json --scale MINIMAL
python3 scripts/validate-graph.py graph.json --scale STANDARD
python3 scripts/validate-graph.py graph.json --scale DEEP
```

Live-execution tests (LT-01 to LT-11) require an actual skill run. See `tests/README.md`.

---

## Relationship to other skills

| Skill | Relationship |
|-------|-------------|
| `epiphany-analysis` | This skill replaces it. Same dual-input model; graph topology eliminates sequential bottleneck. |
| `epiphany-graph-genius` | Architectural model. Adapted: 11→12 nodes, analysis-specific signals, dual-input session schema. |
| `epiphany-genius` | Best source for Node B. Its output is `genius-current` and triggers the full Section-Tailoring Map. |
| `epiphany-graph-genius` | Also a valid Node B source. Produces richer findings than epiphany-genius for complex inputs. |

---

## Session output example

```
~/docs/epiphany/graph-analysis/2026-04-25T10-30-00-ab12/
├── input-a.md              # Node A verbatim copy
├── input-b.md              # Node B verbatim copy (or inline substitute)
├── enhanced.md             # Primary output: enhanced Node A
├── analysis-report.md      # A1 + B1 analyses + cross-reference map
├── solution-catalog.md     # All solutions with two-draft comparisons
├── self-audit.md           # R1–R6 verification verdict
├── graph-trace.json        # Execution trace
└── stages/
    ├── session.md          # Runtime state
    ├── N1-intake-decompose.md
    ├── N2-dual-analyze.md
    ├── N3-section-tailor.md  (if genius-current/drift)
    ├── N4-cross-reference.md
    ├── N5-lateral-ideate.md  (STANDARD/DEEP)
    ├── N6-defixation.md      (if S2_thin_B or S7_no_alternatives)
    ├── N7-adversarial-verify.md (STANDARD/DEEP)
    ├── N8-solution-engineer.md
    ├── N9-router-record.md   (STANDARD/DEEP)
    ├── N10-synthesize.md
    ├── N11-verify.md
    └── N12-expand.md         (DEEP + S11_artifact_gap only)
```

Completion summary line (always printed):
```
epiphany-graph-analysis completed: PASS | scale=STANDARD | spawns=4 | wall-clock=842s | artifacts=[enhanced.md, analysis-report.md, solution-catalog.md, self-audit.md, graph-trace.json]
```
