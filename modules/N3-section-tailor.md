---
node_id: "N3"
node_name: "SectionTailor"
module_version: "1.0.0"
type: TAILOR
exec_type: "inline"
hat: "Feynman"
context_budget_lines: 600
scale_gates: ["STANDARD", "DEEP"]
activation:
  - "conditional:E08"
raises_signals: []
required_output_sections:
  - "Tailored Sections"
  - "Section-Tailoring Map Applied"
  - "Extraction Summary"
input_dependencies:
  - "(N2b, analysis_b_digest)"
  - "(N1, intake_digest)"
optional_inputs: []
kb_files:
  - "section-tailoring-map.md"
output_signal_fields:
  - "tailored_b_digest"
output_file: "stages/N3-section-tailor.md"
hard_gates_referenced: []
---

# N3 -- SectionTailor (Feynman)

## Role

Applies section-type-specific idea-extraction strategies to Node B's content. Active only when N1 classified Node B as genius-current or genius-drift (E08 gate). Uses the Section-Tailoring Map from KB to extract maximally useful content from each canonical section type. Adopts Feynman framing: "What is the simplest, most powerful extraction from this section?"

## PROTOCOL

### Activation

N3 fires only when E08 gate is true: `intake_digest.node_b_type ∈ {genius-current, genius-drift}`. If generic-fallback, this node is skipped entirely and N4 falls back to `analysis_b_digest` alone.

### Inputs

- Read `analysis_b_digest` from SIGNAL_STATE (N2b's output): includes N2b's species catalog, downstream hints, and the full per-section findings
- Read `intake_digest` from SIGNAL_STATE (N1's output): the 10-row canonical section match table, node_b_type
- Consult `kb/section-tailoring-map.md` for extraction strategies per section type

### Section-Tailoring Steps

For each canonical section that N1 matched in Node B:

1. **Identify the section type** from N1's match table (Headline Insight, Core Argument, etc.)
2. **Look up the extraction strategy** in `kb/section-tailoring-map.md`:
   - Each section type has a primary extraction pattern (e.g., Headline Insight → extract the core claim in ≤2 sentences; Supporting Evidence → extract the strongest piece of evidence with its source; Counter-Arguments → extract the strongest counter and its rebuttal)
3. **Apply the strategy**: read the body content N2b analyzed, apply the extraction pattern, produce the tailored output
4. **Preserve precision**: do not paraphrase into vagueness. If the original uses specific terminology, preserve it. If it uses vague language, flag it.
5. **AP-12 compliance**: Process Headline Insight section FIRST. The headline insight frames everything else; extracting it last produces incoherent output.

### Conflict Handling

If N2b flagged a section as CEREMONIAL (header doesn't match body), the tailoring strategy should note this and extract what IS there rather than forcing what the header promises.

### Output

Write `stages/N3-section-tailor.md` with:

#### Frontmatter (per spec §4.15):
```yaml
---
node_id: "N3"
node_name: "SectionTailor"
exec_type: "inline"
hat: "Feynman"
started_at: "ISO-8601"
completed_at: "ISO-8601"
duration_ms: <int>
context_lines_used: <int>
context_budget_lines: 600
signal_flags_raised: []
status: "complete"
---
```

#### Body sections:

### Tailored Sections

For each canonical section matched by N1 (in order, Headline Insight first per AP-12):

```
#### Section: <Canonical Section Name>
- **Extraction Strategy**: <from section-tailoring-map.md>
- **Tailored Output**: <the extracted content, precise and minimal>
- **Original Text Reference**: §N.M or header reference in Node B
- **Quality Note**: <if CEREMONIAL match, note the header/body gap>
```

### Section-Tailoring Map Applied

Table mapping each canonical section type to the specific extraction strategy applied, with the KB reference:

| Canonical Section | Extraction Strategy | KB Reference | Applied Successfully? |
|---|---|---|---|
| Headline Insight | ... | section-tailoring-map.md §... | Y/N/partial |
| ... | ... | ... | ... |

### Extraction Summary

- Total canonical sections matched by N1: `<int>`
- Sections with successful tailoring: `<int>`
- Sections with partial/ceremonial tailoring: `<int>`
- Key insights preserved: `<list of 2-5 most impactful extractions>`
- Content lost in tailoring: `<what was stripped and why (redundant, vague, out-of-scope)>`

## SIGNAL_STATE Output

Write `(N3, tailored_b_digest)`:
```yaml
sections_tailored: <int>
extraction_success_rate: <float 0.0-1.0>
headline_insight_extracted: "<the core extracted claim>"
```

## Failure Modes

- Section-tailoring-map.md missing or doesn't cover a matched section type → use generic extraction: summarize in 2-3 sentences preserving key claims; flag the missing KB entry
- N2b analysis_b_digest is incomplete → tailor what's available; mark missing sections as "unavailable"
- Context budget exceeded → prioritize Headline Insight, Core Argument, Supporting Evidence; demote remaining sections to single-sentence extraction
