---
node_id: "N1"
node_name: "IntakeDecompose"
module_version: "1.0.0"
type: DECOMPOSE
exec_type: "inline"
hat: "Einstein/Feynman"
context_budget_lines: 200
scale_gates: ["STANDARD", "DEEP"]
activation:
  - "always"
raises_signals:
  - "S1_input_complexity"
required_output_sections:
  - "Input Class"
  - "HG-1 Verification"
  - "Node A Decomposition"
  - "Node B Genius Detection"
  - "Complexity Signal"
  - "Session Init"
input_dependencies: []
optional_inputs: []
kb_files:
  - "input-preloading-templates.md"
  - "vocabulary-rubric.md"
output_signal_fields:
  - "intake_digest"
output_file: "stages/N1-intake-decompose.md"
hard_gates_referenced:
  - "HG-1"
---

# N1 — IntakeDecompose

## Role

Reads Node A (original text) and Node B (analysis document), classifies them, computes the S1_input_complexity signal, enforces HG-1 (output != input), and initializes the session directory for downstream nodes.

## PROTOCOL

You are now adopting the Einstein/Feynman persona for this stage. Focus on first-principles decomposition -- identify what the text IS (structure, claims, constraints) and what has been DONE to it (analysis headers, depth, classification).

### Step 1: Read inputs
- Read Node A from `{session_dir}/input-a.md` (already written verbatim by orchestrator before N1 dispatch)
- Read Node B from `{session_dir}/input-b.md` (verbatim, or contains "inline-substitute" marker if no Node B provided)
- If Node B is empty or missing: treat as `inline-substitute`; generate a structural analysis placeholder

### Step 2: HG-1 -- Output != Input check
Verify that `enhanced.md` target path != Node A source path.
- If Node A was provided inline (no source file path): trivially satisfied, record `node_a_source: 'inline'`
- If both are paths and they match: HALT with `FAILED: HG-1 — enhanced.md target path equals Node A source path. Output would overwrite input.`
- If paths differ: PASS and record

### Step 3: Node A Decomposition
Count and characterize Node A:
- `line_count`: total lines (use 1 if file is empty to avoid log10(0))
- `structural_depth`: max markdown header nesting depth. Extract via regex `^(#+)\s+\S` per line, take `max(len(group_1))` across all matches; default 1 if no headers (flat prose)
- `constraint_count`: total occurrences of MUST/MUST NOT/SHALL/REQUIRED/FORBIDDEN/NEVER (case-sensitive whole-word match) in Node A
- List all extracted section anchors (regex `^#+\s+\S` and `§N(\.M)?` references)
- Record `node_a_source` (file path or "inline")

### Step 4: Node B Genius Detection
Count canonical and synonym section headers in Node B against the 10 canonical sections:

| # | Canonical Header | Accepted Synonyms |
|---|---|---|
| 1 | Headline Insight | "Primary Insight", "Lead Insight", "Top-Line Insight", "Bottom Line", "Core Insight" |
| 2 | Theory Collisions | "Theoretical Conflicts", "Conflicting Claims", "Theory Conflicts", "Claim Conflicts" |
| 3 | Discovery vs. Proof | "Discovery vs Proof", "Discovery-Proof Gap", "Claim vs Evidence", "Discovery and Proof" |
| 4 | Independence-Verified Bridges | "Independence Bridges", "Verified Bridges", "Cross-Domain Bridges", "Bridges (Verified)" |
| 5 | Alternative Hypotheses | "Alt Hypotheses", "Alternative Theories", "Counter-Hypotheses", "Competing Hypotheses" |
| 6 | Density-Checked Falsification | "Falsification (Density-Checked)", "Density Falsification", "Counter-Examples", "Falsification Checks" |
| 7 | Scope Limits | "Scope Boundaries", "Applies-to / Does-not-extend-to", "Boundaries", "Domain Limits" |
| 8 | Coherence Signals | "Convergent Signals", "Coherence Indicators", "Signal Convergence", "STRONG/MODERATE/WEAK Signals" |
| 9 | Generalization Checks | "Generalization", "Holds-at / Breaks-at", "Generality Checks", "Universality Tests" |
| 10 | Open Questions & Next Probes | "Open Questions", "Next Probes", "Questions & Probes", "Future Probes", "Probes & Questions" |

Matching rules:
- Case-insensitive, ignore trailing punctuation, strip leading numbering (`1.`, `(a)`) and trailing parentheticals
- Match on `## Header` lines first, fall back to `**Header**` bold-line variants
- Each canonical section counts at most once; synonym match counts equally with canonical match
- Empty-body sections still count; first recognized form wins per section

Classification (using effective thresholds, defaults: genius_threshold=8, drift_threshold=3):
- `score >= 8` -> `genius-current`
- `3 <= score < 8` -> `genius-drift`
- `score < 3` -> `generic-fallback`
- No Node B -> `inline-substitute`

### Step 5: Compute S1 -- Complexity Signal
```
complexity_score = log10(line_count) + structural_depth + min(constraint_count / 10, 5.0)
```
Map to bucket:
- `score < 5` -> `low`
- `5 <= score < 9` -> `medium`
- `score >= 9` -> `high`

Raise signal: `S1_input_complexity` with value = bucket and raw_score = complexity_score.

### Step 6: Write stage file
Write `stages/N1-intake-decompose.md` with all 6 required output sections, each as an H2 header with substantive content.

## Input Class

Record Node A metrics: `line_count`, `structural_depth`, `constraint_count`, and `node_a_source` (file path or `"inline"`). For Node B: list all identified section headers matched, the match variant used for each, and the classification (`node_b_type`).

## HG-1 Verification

Document the HG-1 check result. If Node A was inline: record `node_a_source: 'inline'` and PASS. If both are file paths that differ: record both paths and PASS. If paths match: HALT with the prescribed error message. Include rationale.

## Node A Decomposition

Provide the full structural breakdown:
- All section headers found (extracted via `^#+\s+\S` regex)
- All `§N` and `§N.M` section-anchor references
- Constraint keyword table: for each of MUST, MUST NOT, SHALL, REQUIRED, FORBIDDEN, NEVER -- show count and line-number locations
- `structural_depth` value and the header line that produced it

## Node B Genius Detection

Present the 10-row canonical section match table:

| # | Canonical Section | Matched (Y/N) | Variant Matched |
|---|---|---|---|
| 1 | Headline Insight | ... | ... |
| ... | ... | ... | ... |
| 10 | Open Questions & Next Probes | ... | ... |

Include: `score` (number of sections matched), `classification` (genius-current / genius-drift / generic-fallback / inline-substitute), and notes on empty-body sections if any.

## Complexity Signal

Show the S1 formula breakdown with each term's value:
```
complexity_score = log10(line_count) + structural_depth + min(constraint_count / 10, 5.0)
                 = <val1> + <val2> + <val3>
                 = <total>
```
Declare `bucket` (low / medium / high) and confirm `S1_input_complexity` signal raised with `raw_score` and `value`.

## Session Init

Record: `session_id`, `created_at` (ISO-8601 timestamp), `input_a_path`, `input_b_path` (or "inline-substitute"), and `stage_file` path written.

### Step 7: Write SIGNAL_STATE entry
Write `(N1, intake_digest)` containing:
```yaml
node_b_type: "genius-current" | "genius-drift" | "generic-fallback" | "inline-substitute"
complexity_bucket: "low" | "medium" | "high"
complexity_score: <float>
structural_depth: <int>
line_count: <int>
constraint_count: <int>
s1_signal_flags: ["S1_input_complexity"]
```

## Output Format

Stage file frontmatter per spec §4.15:
```yaml
---
node_id: "N1"
node_name: "IntakeDecompose"
exec_type: "inline"
hat: "Einstein/Feynman"
started_at: "ISO-8601"
completed_at: "ISO-8601"
duration_ms: <int>
context_lines_used: <int>
context_budget_lines: 200
signal_flags_raised: ["S1_input_complexity"]
status: "complete"
---
```

Body contains the 6 required sections as H2 headers with substantive content under each.

## Hard Gates Enforced

- **HG-1** (Output != Input): verified in Step 2; HALT on path equality
- **HG-4** (Fresh copy only): all writes go to `{session_dir}/`; no writes to source paths

## Failure Modes

- Node A is binary/non-text -> HALT: "FAILED: Node A must be text content (markdown, plain text, or structured prose)."
- Node B has zero recognizable markers -> classify as `generic-fallback`; pipeline continues
- Node A >5000 lines -> advisory logged; S1=high regardless
- All genius headers matched but empty body sections -> still counts; note in Genius Detection
