---
node_id: "N6"
node_name: "Defixation"
module_version: "1.0.0"
type: DEFIX
exec_type: "inline"
hat: "Ohlsson"
context_budget_lines: 700
scale_gates: ["STANDARD", "DEEP"]
activation:
  - "conditional:E09"
  - "conditional:E20"
raises_signals: []
required_output_sections:
  - "Defixation Pass"
  - "Breakthrough Ideas"
  - "Impasse Analysis"
input_dependencies: []
optional_inputs:
  - "(N2b, analysis_b_digest)"
  - "(N7, falsification_result)"
kb_files:
  - "ohlsson-defixation.md"
output_signal_fields:
  - "breakthrough_digest"
output_file: "stages/N6-defixation.md"
hard_gates_referenced: []
---

# N6 -- Defixation (Ohlsson)

## Role

Applies Ohlsson's defixation theory when the pipeline is stuck: either Node B is too thin (E09 back-edge triggered by S2_thin_B) or N7 falsification found no alternatives (E20 back-edge triggered by S7_no_alternatives). N6's job is to break fixation by changing problem representation -- not generating more ideas, but reframing the problem so new ideas become possible.

## PROTOCOL

### Activation

N6 fires via one of two back-edges:
- **E09**: `S2_thin_B` raised by N2b (Node B was thin → early defixation needed)
- **E20**: `S7_no_alternatives ∧ ¬N6_ran` raised by N7 via N9 router (falsification passed but found no viable alternatives → late defixation needed)

N6 fires at most once per session (both edges have `single_firing_cap: true`).

### Inputs

- If via E09: read `analysis_b_digest` from N2b to understand what Node B is thin on
- If via E20: read `falsification_result` from N7 to understand what the falsification found lacking
- Consult `kb/ohlsson-defixation.md` for defixation techniques

### Defixation Protocol

Ohlsson's theory: impasse occurs when the current problem representation blocks retrieval of relevant knowledge. Defixation requires changing the representation.

**Step 1: Diagnose the fixation.** What is the current representation?
- Summarize the implicit frame the pipeline has been using (e.g., "this is a technical problem requiring a technical solution")
- Identify what this representation makes salient AND what it obscures

**Step 2: Apply representation change techniques** (from `kb/ohlsson-defixation.md`):
- **Elaboration**: enrich the representation with new information (add missing constraints, add context, add stakeholders)
- **Re-encoding**: re-describe the problem in different terms (change domain language, change abstraction level, change temporal frame)
- **Constraint relaxation**: temporarily remove a constraint and see what becomes possible (what if budget wasn't a concern? what if the audience was different? what if the deliverable was a question instead of an answer?)

**Step 3: Generate breakthrough ideas from the new representation.** From each changed representation, generate 1-3 ideas that were invisible under the old representation.

**Step 4: Bridge back.** For each breakthrough idea, show how it connects to the original problem -- it should be surprising from the old frame but obvious from the new one.

### Output

Write `stages/N6-defixation.md` with:

#### Frontmatter:
```yaml
---
node_id: "N6"
node_name: "Defixation"
exec_type: "inline"
hat: "Ohlsson"
started_at: "ISO-8601"
completed_at: "ISO-8601"
duration_ms: <int>
context_lines_used: <int>
context_budget_lines: 700
signal_flags_raised: []
status: "complete"
triggered_by: "E09" | "E20"
---
```

#### Body sections:

### Defixation Pass

**Fixation Diagnosis:**
- Current problem representation (2-3 sentences)
- What this representation makes salient
- What it obscures or blocks

**Representation Changes Applied:**
For each technique applied (elaboration, re-encoding, constraint relaxation):
- Technique name and KB reference
- How it was applied to this specific case
- The new representation it produced

### Breakthrough Ideas
List each breakthrough idea with:
- Which representation change produced it
- The idea itself (concise, specific)
- Why it was invisible under the old representation
- How it bridges back to the original problem

### Impasse Analysis
- Why did the pipeline reach this impasse?
- Was the original representation wrong, or just incomplete?
- What should downstream nodes (N8, N10) do differently with these breakthrough ideas?

## SIGNAL_STATE Output

Write `(N6, breakthrough_digest)`:
```yaml
triggered_by: "E09" | "E20"
fixation_type: "<diagnosed fixation>"
representations_tried: [<list of representation change techniques>]
breakthrough_count: <int>
```

## Failure Modes

- Ohlsson KB unavailable → fall back to generic reframing: try 3 different perspectives (opposite audience, 10x faster, 100x bigger); generate ideas from each
- No breakthrough from any representation change → record empty breakthrough_digest with note; N8 and N10 must proceed with only N5.5's accepted ideas
- Both E09 AND E20 try to fire (shouldn't happen with single_firing_cap) → if somehow both, prefer E20's input context (richer); process once
