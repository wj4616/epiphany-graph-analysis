---
node_id: "N2b"
node_name: "AnalyzeB"
module_version: "1.0.0"
type: ANALYZE-B
exec_type: "spawn"
hat: "Darwin (variation-survey)"
context_budget_lines: 1500
scale_gates: ["STANDARD", "DEEP"]
activation:
  - "always"
raises_signals: ["S2_thin_B"]
required_output_sections:
  - "Methodology"
  - "Findings"
  - "Confidence"
  - "Open Questions"
  - "Genius Detection Corroboration"
input_dependencies:
  - "(N1, intake_digest)"
optional_inputs: []
kb_files:
  - "analysis-methodology.md"
  - "section-tailoring-map.md"
output_signal_fields:
  - "analysis_b_digest"
output_file: "stages/N2b-analyze-b.md"
hard_gates_referenced: []
---

# N2b -- AnalyzeB (Darwin Variation-Survey)

## Role

Performs a deep structural analysis of Node B (the analysis/commentary text). Adopts a Darwin (variation-survey) persona -- catalog the variation in claims, assess section quality, detect patterns across sections. This is a spawn node dispatched via the Agent tool; operates with 1500-line context budget.

Node B is typically an epiphany-analysis output or similar structured commentary on Node A. N2b's job is to survey the "species" of claims Node B makes, assess their fitness, and crucially **corroborate or challenge N1's genius classification** by reading Node B's actual body content (not just headers).

## PROTOCOL (spawn prompt template)

You are now adopting the Darwin (variation-survey) persona for this stage. Survey the variation in claims across Node B. Catalog what species of analysis are present. Assess which are well-adapted (evidence-rich, specific) and which are rudimentary. Your core question: does the *content* of Node B match the form suggested by its headers?

### Inputs
- Read `intake_digest` from SIGNAL_STATE (N1's output): node_b_type, complexity_bucket, complexity_score, the 10-row canonical section match table with score
- Read the full Node B from `{session_dir}/input-b.md` (verbatim copy written by N1)
- Consult `kb/analysis-methodology.md` for the analysis assessment framework
- Consult `kb/section-tailoring-map.md` for section-type-specific extraction strategies

### Analysis Steps

1. **Variation catalog**: For each major section of Node B, classify the "species" of content: claim-assertion, evidence-citation, constraint-derivation, pattern-detection, question-generation, summary-restatement, elaboration-extension, challenge-refutation. Note the mix -- a single-type section is a monoculture (fragile).

2. **Genius Detection Corroboration**: This is the critical step. N1 classified Node B by matching section *headers* against a canonical table. Your job is to verify that the *body content* under those headers is genuinely what the header promises. For each matched canonical section:
   - Read the full body text under that header
   - Assess: does this content actually fulfill the canonical section's purpose? (e.g., a "Headline Insight" section whose body is generic commentary is a ceremonial match only)
   - Flag mismatches: header says X but body delivers Y
   - Empty-body sections: note them explicitly -- they count as ceremonial
   - Produce a `corroboration_verdict`: CONFIRMED (content matches header, ≥80% of matched sections substantiated), MIXED (50-79% substantiated), or CEREMONIAL (<50% substantiated -- headers are decoration)

3. **Section quality audit**: For each section of Node B, assess:
   - Specificity: are claims concrete or abstract? (1-5 scale, 1=vague platitudes, 5=precise falsifiable claims)
   - Evidence: does the section cite evidence, examples, or reasoning? (none / anecdotal / systematic)
   - Novelty: does this section say something Node A didn't already say? (restatement / extension / transformation)
   - Actionability: can this section's output be *used* downstream? (dead-end / informational / actionable)

4. **Cross-section patterns**: Identify patterns that span Node B sections:
   - Consistent themes (appear in ≥3 sections)
   - Contradictions (Section X says P, Section Y says ¬P or implies ¬P)
   - Escalating insights (later sections build on earlier ones vs. independent observations)
   - Missing connective tissue (sections read as independent bullets rather than a chain)

5. **S2_thin_B determination**: Node B is "thin" if ANY of:
   - `node_b_type == "generic-fallback"` (N1 already classified it as non-genius)
   - `< 3 canonical sections matched by N1` (too few structural matches)
   - `corroboration_verdict == CEREMONIAL` (headers matched but bodies didn't deliver)
   - Average specificity across sections < 2.5 (concrete-starved)
   - ≥30% of matched sections have empty or near-empty bodies (< 2 substantive sentences)

   If thin: add `"S2_thin_B"` to `signal_flags_raised` in output frontmatter AND in the SIGNAL_STATE entry. This triggers E09 back-edge to N6 (early defixation).

6. **Downstream hints**: Tag each section with hints for downstream nodes:
   - `n3_tailoring_hint`: what extraction strategy from section-tailoring-map.md applies?
   - `n4_xref_hint`: which Node A sections does this B section most naturally connect to?
   - `n7_adversarial_hint`: what claim in this section is most vulnerable to falsification?

### Output

Write `stages/N2b-analyze-b.md` with:

#### Frontmatter (per spec section 4.15):
```yaml
---
node_id: "N2b"
node_name: "AnalyzeB"
exec_type: "spawn"
hat: "Darwin (variation-survey)"
started_at: "ISO-8601"
completed_at: "ISO-8601"
duration_ms: <int>
context_lines_used: <int>
context_budget_lines: 1500
signal_flags_raised: ["S2_thin_B"]  # if thin, else []
status: "complete"
---
```

#### Body sections:

### Methodology
Describe the variation-survey approach: section species classification method, corroboration framework (header-vs-body assessment), quality audit rubric (specificity/evidence/novelty/actionability scales), cross-section pattern detection method, S2_thin_B criteria. Reference `kb/analysis-methodology.md`.

### Findings
The bulk of the output. Organized by section of Node B:
- For each major section: species classification (list of content types present), specificity score (1-5), evidence level (none/anecdotal/systematic), novelty assessment (restatement/extension/transformation), actionability (dead-end/informational/actionable), strengths (1-2), weaknesses (1-2), downstream hints (n3_tailoring_hint, n4_xref_hint, n7_adversarial_hint)
- Include a "Cross-Cutting Observations" subsection: consistent themes (≥3 sections), contradictions found, escalation patterns (or lack thereof), connective tissue assessment

### Confidence
Per-finding confidence assessment:
- Species classifications: confidence rating (high/medium/low) with justification
- Quality scores: inter-section consistency check (are similar-quality sections scored similarly?)
- Corroboration verdict confidence: how certain is the CEREMONIAL/MIXED/CONFIRMED call?
- Overall confidence summary

### Open Questions
- What would a second analysis pass reveal? (questions Node B raises but doesn't resolve)
- What did Node B *not* say that it should have given its headers? (content-to-header gaps)
- What external knowledge would strengthen Node B's claims? (domain expertise gaps)
- What would a counter-analysis look like? (adversarial prep for N7)

### Genius Detection Corroboration
Present the full corroboration table:

| # | Canonical Section | N1 Matched? | Body Substantiated? | Evidence Level | Mismatch? | Notes |
|---|---|---|---|---|---|---|
| 1 | Headline Insight | Y/N | Y/N/EMPTY | none/anecdotal/systematic | none/partial/full | ... |
| 2 | Core Argument | ... | ... | ... | ... | ... |
| 3 | Supporting Evidence | ... | ... | ... | ... | ... |
| 4 | Counter-Arguments | ... | ... | ... | ... | ... |
| 5 | Implications | ... | ... | ... | ... | ... |
| 6 | Limitations | ... | ... | ... | ... | ... |
| 7 | Alternative Views | ... | ... | ... | ... | ... |
| 8 | Synthesis | ... | ... | ... | ... | ... |
| 9 | Action Items | ... | ... | ... | ... | ... |
| 10 | Open Questions & Next Probes | ... | ... | ... | ... | ... |

Compute:
- `sections_substantiated`: count of rows where Body Substantiated == Y
- `sections_matched_by_n1`: count of rows where N1 Matched == Y
- `substantiation_rate`: sections_substantiated / max(sections_matched_by_n1, 1)
- `corroboration_verdict`: CONFIRMED (≥80%), MIXED (50-79%), CEREMONIAL (<50%)

Include a narrative assessment: does Node B's *actual content* deserve the classification N1 gave it? Flag specific mismatches with section references (§N.M or header text).

If `corroboration_verdict == CEREMONIAL`: raise S2_thin_B regardless of node_b_type.

## SIGNAL_STATE Output

Write `(N2b, analysis_b_digest)` containing the full Findings + Genius Detection Corroboration as structured content, plus metadata:
```yaml
methodology: "B1 Darwin variation-survey"
sections_analyzed: <int>
species_cataloged: [<list of content types found>]
mean_specificity: <float 1-5>
corroboration_verdict: "CONFIRMED" | "MIXED" | "CEREMONIAL"
substantiation_rate: <float 0.0-1.0>
signal_flags: ["S2_thin_B"]  # if raised, else []
node_b_type_corroborated: true | false
```

## Failure Modes

- Node B is empty -> write minimal stage file with `status: incomplete`; note "empty Node B"; raise S2_thin_B
- Context budget exceeded -> write what was produced with `status: incomplete`; note where budget was exhausted; include partial corroboration verdict
- Node B has no recognizable sections -> treat as generic-fallback; raise S2_thin_B; produce flat findings
- Node B section headers are ceremonial (body content doesn't match header promises) -> record CEREMONIAL verdict; raise S2_thin_B; this is NOT a failure of N2b -- it's a legitimate finding
