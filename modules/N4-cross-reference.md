---
node_id: "N4"
node_name: "CrossReference"
module_version: "1.0.0"
type: XREF
exec_type: "inline"
hat: "Tesla (bridge-builder)"
context_budget_lines: 800
scale_gates: ["STANDARD", "DEEP"]
activation:
  - "always"
raises_signals: ["S4_xref_density"]
required_output_sections:
  - "Cross-Reference Map"
  - "Overlap Resolution"
  - "S4 Signal"
  - "Coverage Summary"
input_dependencies:
  - "(N1, intake_digest)"
  - "(N2a, analysis_a_digest)"
  - "(N2b, analysis_b_digest)"
optional_inputs:
  - "(N3, tailored_b_digest)"
kb_files: []
output_signal_fields:
  - "xref_map"
output_file: "stages/N4-cross-reference.md"
hard_gates_referenced: []
---

# N4 -- CrossReference (Tesla Bridge-Builder)

## Role

Builds a cross-reference map connecting every finding in Node B's analysis to the corresponding section in Node A. This is the bridge that enables all downstream nodes to work with both texts in relationship rather than isolation. Adopts Tesla (bridge-builder) framing: measure the connections, quantify the coverage, identify the gaps.

## PROTOCOL

### Inputs

- Read `analysis_a_digest` from SIGNAL_STATE (N2a): per-section claims, constraints, gaps, cross-reference hints
- Read `analysis_b_digest` from SIGNAL_STATE (N2b): per-section species, quality scores, cross-reference hints
- Read `tailored_b_digest` from SIGNAL_STATE (N3) if N3 was active (genius-current/drift). If N3 was not active (generic-fallback), use only `analysis_b_digest`.
- Read `intake_digest` from SIGNAL_STATE (N1): for node_b_type and complexity context

### Overlap Resolution Rule

When N3 IS active, N4 receives both `analysis_b_digest` (from N2b) and `tailored_b_digest` (from N3). These cover the same Node B sections but at different levels of processing. Resolution:

- **Matched sections** (N3 applied a tailoring strategy): **Prefer `tailored_b_digest`**. It has been processed through section-type-specific extraction and is more actionable.
- **Unmatched sections** (N3 had no tailoring strategy for this section type): **Use `analysis_b_digest`**. N2b's raw analysis is the best available.
- **N3-only sections** (N3 found content N2b didn't catalog as a separate section): **Corroborate before use**. Cross-check against N2b's findings; if N2b saw this content embedded in another section, note the overlap. If N2b genuinely missed it, use with lower confidence.
- **Conflict** (N3 and N2b disagree about a section's quality): Prefer N2b's assessment (N2b did the full-body reading; N3 applied an extraction strategy). Flag the disagreement.

### Cross-Reference Construction

For each finding in the resolved B-analysis:

1. **Identify the finding**: from the resolved source (tailored_b_digest or analysis_b_digest)
2. **Match to Node A section(s)**: using N2a's `potential_b_match` hints AND N2b's `n4_xref_hint` hints
3. **Score relevance** (1-5):
   - 1 = this B finding is about a topic Node A barely mentions
   - 3 = this B finding addresses a topic Node A covers but from a different angle
   - 5 = this B finding directly engages with Node A content (quotes, refutes, extends)
4. **Determine potential action**: what could a downstream node DO with this connection?
   - `extend`: B finding can extend/enrich A content
   - `challenge`: B finding contradicts or questions A content
   - `corroborate`: B finding independently supports A content
   - `fill_gap`: B finding addresses what Node A left unaddressed
   - `tangential`: interesting but not directly actionable
5. **Assign a stable B finding ID**: `B<seq>` for traceability through downstream nodes

### S4_xref_density Signal

Compute `xref_density`:
```
xref_density = total_xref_count / max(node_a_constraint_count, 1)
```

Classify:
- **sparse** (< 0.5): few connections relative to structure → N5 uses 3 lateral passes
- **normal** (0.5 -- 2.0): expected connection density → N5 uses 2 lateral passes
- **dense** (> 2.0): rich web of connections → N5 uses 1 lateral pass (quality over quantity)

Raise `S4_xref_density` with the computed value and classification.

### Output

Write `stages/N4-cross-reference.md` with:

#### Frontmatter:
```yaml
---
node_id: "N4"
node_name: "CrossReference"
exec_type: "inline"
hat: "Tesla (bridge-builder)"
started_at: "ISO-8601"
completed_at: "ISO-8601"
duration_ms: <int>
context_lines_used: <int>
context_budget_lines: 800
signal_flags_raised: ["S4_xref_density"]
status: "complete"
---
```

#### Body sections:

### Cross-Reference Map

Full table:

| B-ID | B Finding | Source | A Section | Relevance | Action |
|---|---|---|---|---|---|
| B1 | <finding text or summary> | N3/N2b | §N.M | 1-5 | extend/challenge/... |
| B2 | ... | ... | ... | ... | ... |

Include an "Unmatched B Findings" subsection for findings that couldn't be mapped to any A section (relevance=0 or truly orthogonal topic).

### Overlap Resolution

Document:
- N3 active? YES/NO
- Sections resolved via tailored_b_digest (preferred): `<int>`
- Sections resolved via analysis_b_digest (fallback): `<int>`
- N3-only sections (corroborated): `<int>`
- Conflicts between N2b and N3: `<int>` with brief description of each

### S4 Signal

- Total cross-references: `<int>`
- Node A constraint count (from N1): `<int>`
- xref_density = `<float>` = `<classification>` (sparse/normal/dense)
- N5 lateral pass count: 3 / 2 / 1

### Coverage Summary

- Node A sections covered (≥1 B finding mapped): `<int>` / `<total Node A sections>`
- Node A sections uncovered (no B finding mapped): list of §refs
- B findings unmapped (no A section match): `<int>`
- Mean relevance score: `<float>`
- Action distribution: extend=<int>, challenge=<int>, corroborate=<int>, fill_gap=<int>, tangential=<int>

## SIGNAL_STATE Output

Write `(N4, xref_map)`:
```yaml
xref_count: <int>
xref_density: <float>
xref_classification: "sparse" | "normal" | "dense"
n5_lateral_passes: 3 | 2 | 1
coverage_rate: <float 0.0-1.0 sections covered>
unmapped_b_count: <int>
```

## Failure Modes

- N2a or N2b output missing → cannot build xref map without both A and B analyses; halt with error
- All B findings unmapped to A → xref_count=0; S4_xref_density = sparse (0.0); N5 runs 3 passes with generic domain catalog coverage
- Tailored and raw B analyses conflict on >30% of sections → flag systematic disagreement; use tailored_b for matched sections but annotate every conflict
