---
node_id: "N12"
node_name: "Expand"
module_version: "1.0.0"
type: EXPANSION
exec_type: "inline"
hat: "Feynman"
context_budget_lines: 800
scale_gates: ["DEEP"]
activation:
  - "conditional:E25"
raises_signals: []
required_output_sections:
  - "Thin-Spot Identification"
  - "Proposed Depth Passes"
  - "Expansion Targets"
input_dependencies:
  - "(N11, first_pass_verified)"
  - "(N10, enhanced_draft)"
optional_inputs:
  - "(N10, enhancement_summary)"
kb_files: []
output_signal_fields:
  - "expansion_digest"
output_file: "stages/N12-expand.md"
hard_gates_referenced: []
---

# N12 -- Expand (Feynman)

## Role

DEEP-only node activated when N11's verification detects artifact gaps in the first-pass enhanced draft. N12 identifies exactly where the draft is thin, proposes targeted depth passes, and feeds expansion targets back to N10 for re-synthesis via the E26 back-edge. Adopts Feynman framing: "Where is the draft still confused? What specific questions would force it to be clearer?"

## PROTOCOL

### Activation

N12 fires only when E25 gate is true: ALL of:
- `mode == DEEP`
- `pass == 1` (first pass only -- prevents infinite expansion loops)
- `S11_artifact_gap ∈ first_pass_verified.signal_flags`

### Inputs

- Read `first_pass_verified` from SIGNAL_STATE (N11's output): which artifact gap types, specific V-check failures, pass rate
- Read `enhanced_draft` and `enhancement_summary` from SIGNAL_STATE (N10's output): the current draft text and N10's synthesis decisions

### Expansion Protocol

**Step 1: Identify thin spots.** Using N11's verification report and reading the draft text, locate specific passages/sections where:
- V1 flagged factual issues → read the surrounding paragraph, identify what's missing
- V2 flagged low claim density → find the section with sparse claims
- V5 flagged missing sections → identify which Node A sections are unaddressed
- V6 flagged low density → find the sections below 0.03 enhancement density

**Step 2: Classify thin spots by type:**
- **Depth gap**: the topic IS addressed but shallowly (needs more detail, examples, or reasoning)
- **Coverage gap**: the topic is NOT addressed at all (needs a new section or paragraph)
- **Connection gap**: the topic is addressed but not connected to other sections (needs bridging text)
- **Evidence gap**: claims are present but unsupported (needs reasoning, examples, or data)

**Step 3: Propose depth passes.** For each thin spot, write a specific expansion instruction:
- What should be added? (be specific: "a paragraph explaining why X follows from Y" not "expand this section")
- What question should the expansion answer?
- What source material should it draw from? (N5.5 accepted idea, N6 breakthrough, N8 solution, N4 xref_map)
- Priority: HIGH (blocking), MEDIUM (quality impact), LOW (nice-to-have)

**Step 4: Identify expansion targets.** Select the top-N thin spots to expand, respecting:
- Hard budget: total proposed expansion ≤ 1000 additional words
- Priority sort: HIGH first, then MEDIUM if budget allows
- Minimum bar: at least 1 HIGH-priority expansion if any exist

### Output

Write `stages/N12-expand.md` with:

#### Frontmatter:
```yaml
---
node_id: "N12"
node_name: "Expand"
exec_type: "inline"
hat: "Feynman"
started_at: "ISO-8601"
completed_at: "ISO-8601"
duration_ms: <int>
context_lines_used: <int>
context_budget_lines: 800
signal_flags_raised: []
status: "complete"
---
```

#### Body sections:

### Thin-Spot Identification
Table of thin spots:

| ID | Section | Location | Type | Source Flag | Priority | Description |
|---|---|---|---|---|---|---|
| T1 | §N.M | para 3 | depth | V2 FAIL | HIGH | ... |
| T2 | §P.Q | missing entirely | coverage | V5 FAIL | HIGH | ... |
| ... | ... | ... | ... | ... | ... | ... |

### Proposed Depth Passes

For each thin spot targeted for expansion:

```
### Expansion E1 (Priority: HIGH, Type: depth)
- **Target Location**: <section/paragraph reference in enhanced draft>
- **What to Add**: <specific content description>
- **Question to Answer**: <what should this addition resolve?>
- **Source Material**: <N5.5 idea #X, N6 breakthrough #Y, etc.>
- **Estimated Words**: <int>
```

### Expansion Targets
Summary:
- Total thin spots identified: `<int>`
- Targeted for expansion: `<int>`
- Total proposed word budget: `<int> / 1000`
- Prioritization rationale: 1-2 sentences on why these targets were chosen

## SIGNAL_STATE Output

Write `(N12, expansion_digest)`:
```yaml
thin_spot_count: <int>
expansion_count: <int>
total_proposed_words: <int>
expansion_targets: [<list of E-ids with section refs and instructions>]
```

## Failure Modes

- No thin spots found despite S11_artifact_gap being raised → inconsistency between N11 and N12; re-read draft; if genuinely no thin spots, write empty expansion_digest and skip E26
- All thin spots LOW priority → still propose at least 1 expansion (even LOW priority is still an artifact gap)
- Word budget forces dropping HIGH priority expansions → flag this; N10 should prioritize the ones that fit
