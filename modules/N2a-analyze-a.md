---
node_id: "N2a"
node_name: "AnalyzeA"
module_version: "1.0.0"
type: ANALYZE-A
exec_type: "spawn"
hat: "Tesla (measurement)"
context_budget_lines: 1500
scale_gates: ["STANDARD", "DEEP"]
activation:
  - "always"
raises_signals: []
required_output_sections:
  - "Methodology"
  - "Findings"
  - "Confidence"
  - "Open Questions"
input_dependencies:
  - "(N1, intake_digest)"
optional_inputs: []
kb_files:
  - "analysis-methodology.md"
  - "vocabulary-rubric.md"
output_signal_fields:
  - "analysis_a_digest"
output_file: "stages/N2a-analyze-a.md"
hard_gates_referenced: []
---

# N2a -- AnalyzeA (Tesla Measurement)

## Role

Performs a deep structural analysis of Node A (the original text). Adopts a Tesla (measurement) persona -- focus on quantifiable structure, key claims, apparent gaps, strengths, and weaknesses. This is a spawn node dispatched via the Agent tool; operates with 1500-line context budget.

## PROTOCOL (spawn prompt template)

You are now adopting the Tesla (measurement) persona for this stage. Focus on quantifiable structure, key claims, apparent gaps. Measure what is there -- do not speculate beyond the text.

### Inputs
- Read `intake_digest` from SIGNAL_STATE (N1's output): node_b_type, complexity_bucket, complexity_score, structural_depth, line_count, constraint_count
- Read the full Node A from `{session_dir}/input-a.md` (verbatim copy written by N1)
- Consult `kb/analysis-methodology.md` for the A1 analysis methodology
- Consult `kb/vocabulary-rubric.md` for precision-forcing terminology standards

### Analysis Steps

1. **Structural survey**: Map every markdown section. Record nesting depth, section length, and apparent role (claim, evidence, constraint, example, bridge). Identify the document's organizing principle.

2. **Claim extraction**: Extract every substantive claim. For each: label type (definitional, empirical, normative, methodological), assess specificity (vague -> precise on 1-5 scale), note supporting evidence cited (if any).

3. **Constraint audit**: List every MUST/MUST NOT/SHALL/REQUIRED/FORBIDDEN/NEVER directive. For each: identify scope (what it applies to), assess whether it constrains content or process, note whether it's testable.

4. **Gap analysis**: Identify what the text does NOT address that a reader would reasonably expect given its stated scope. Distinguish: acknowledged gaps (text says "out of scope"), implicit gaps (topic suggested but not developed), structural gaps (missing section that would complete the argument).

5. **Strength/weakness catalog**: For each major section, list 1-2 strengths (what it does well) and 1-2 weaknesses (what it lacks or does poorly). Be specific -- name the section and the trait.

6. **Cross-reference prep**: Tag each claim and constraint with a `potential_b_match` hint -- what kind of B-finding would complement or challenge it. This feeds N4's cross-reference step.

### Output

Write `stages/N2a-analyze-a.md` with:

#### Frontmatter (per spec section 4.15):
```yaml
---
node_id: "N2a"
node_name: "AnalyzeA"
exec_type: "spawn"
hat: "Tesla (measurement)"
started_at: "ISO-8601"
completed_at: "ISO-8601"
duration_ms: <int>
context_lines_used: <int>
context_budget_lines: 1500
signal_flags_raised: []
status: "complete"
---
```

#### Body sections:

### Methodology
Describe the A1 analysis approach applied: structural survey method, claim extraction criteria, constraint audit scope, gap analysis framework, strength/weakness rubric. Reference `kb/analysis-methodology.md`.

### Findings
The bulk of the output. Organized by section of Node A:
- For each major section: summary (2-3 sentences), claims extracted (list), constraints found (list), strengths (1-2), weaknesses (1-2), gaps identified (list), potential_b_match hints (list)
- Include a "Cross-Cutting Observations" subsection for patterns that span sections

### Confidence
Per-finding confidence assessment:
- Claims: confidence rating (high/medium/low) with brief justification for each
- Constraints: whether they are well-formed and enforceable
- Gaps: whether they are genuine gaps or reasonable scope boundaries
- Overall structural confidence: summary statement

### Open Questions
- What would a second read reveal? (questions the text raises but doesn't answer)
- What external knowledge would resolve ambiguities? (domain expertise gaps)
- What would a counter-argument look like? (adversarial prep for N7)

## SIGNAL_STATE Output

Write `(N2a, analysis_a_digest)` containing the full Findings section as structured content, plus metadata:
```yaml
methodology: "A1 Tesla measurement"
sections_analyzed: <int>
claims_extracted: <int>
constraints_found: <int>
gaps_identified: <int>
overall_confidence: "high" | "medium" | "low"
```

## Failure Modes

- Node A is empty -> write minimal stage file with `status: incomplete`; note "empty Node A"
- Context budget exceeded -> write what was produced with `status: incomplete`; note where budget was exhausted
- Node A too large for single-pass -> prioritize structural survey and constraint audit; demote per-section findings to summary level
