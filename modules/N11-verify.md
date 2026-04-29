---
node_id: "N11"
node_name: "Verify"
module_version: "1.0.0"
type: VERIFY
exec_type: "inline"
hat: "Popper"
context_budget_lines: 600
scale_gates: ["STANDARD", "DEEP"]
activation:
  - "always"
raises_signals: ["S11_artifact_gap"]
required_output_sections:
  - "V1-V8 Results"
  - "Verdict Aggregation"
  - "Pass Detection"
  - "Signal Flags"
input_dependencies:
  - "(N10, enhanced_draft)"
optional_inputs: []
kb_files:
  - "verification-gates.md"
output_signal_fields:
  - "verification_report"
output_file: "stages/N11-verify.md"
hard_gates_referenced: ["HG-3", "HG-5"]
---

# N11 -- Verify (Popper)

## Role

Runs the V1-V8 verification battery against N10's enhanced draft. Applies hard gates HG-3 and HG-5. If verification detects thin spots or artifact gaps, raises S11_artifact_gap which may trigger the DEEP expansion path (N12). Adopts Popper framing: "Here is the enhanced draft. Try to falsify every significant claim it makes."

## PROTOCOL

### Inputs

- Read `enhanced_draft` and `enhancement_summary` from SIGNAL_STATE (N10's output)
- Consult `kb/verification-gates.md` for V1-V8 criteria and HG-3/HG-5 definitions

### V1-V8 Verification Battery

Apply each verification check to the enhanced draft:

| ID | Check | Method | Criterion |
|---|---|---|---|
| **V1** | Factual Accuracy | Compare claims against Node A source text and Node B analysis | No claim contradicts a source claim without acknowledging the disagreement |
| **V2** | Claim Completeness | Count explicit claims in each section of the enhanced draft | Every node-a section has ≥1 enhanced claim; no section is bare restatement |
| **V3** | Source Fidelity | Trace each enhanced claim back to its origin (N5.5 accepted idea, N6 breakthrough, N8 solution, or N10 synthesis decision) | Every non-editorial claim has a traceable origin |
| **V4** | Constraint Compliance | Scan enhanced draft for violations of constraints cataloged in N1's constraint table | Zero MUST/MUST NOT violations |
| **V5** | Section Coverage | Compare enhanced draft section structure against N1's decomposition | Every major Node A section is addressed; missing sections flagged |
| **V6** | Enhancement Density | For each section: count enhancements / word count | Mean enhancement density ≥0.05 (1 enhancement per 20 words); sparse sections flagged |
| **V7** | Anti-Pattern Scan | Check enhanced draft against AP-1 through AP-20 | Zero anti-pattern matches; each match flagged with AP number |
| **V8** | Readability | Flesch-Kincaid grade level estimate; sentence length distribution | Reading level within ±2 grade levels of Node A; no 50+ word sentences |

### S11_artifact_gap Determination

The enhanced draft has an "artifact gap" if:
- V1 FAIL (factual contradictions) → artifact gap: accuracy
- V2 FAIL < 100% coverage → artifact gap: completeness
- V5 FAIL (missing sections) → artifact gap: coverage
- V6 mean density < 0.03 → artifact gap: depth
- V3 < 80% traceability → artifact gap: provenance
- V4 has any violation → hard stop HG-3, not an artifact gap (must fix not expand)

If any artifact gap: raise S11_artifact_gap. In DEEP mode with pass=1, this triggers E25 → N12 expansion.

### HG-3 and HG-5 Enforcement

- **HG-3**: If V4 found constraint violations, hard-stop the pipeline. Do not proceed to output. Document every violation with the constraint text and the violating passage.
- **HG-5**: If overall pass rate < 70%, pipeline fails. Document which verifications failed and why.

### Output

Write `stages/N11-verify.md` with:

#### Frontmatter:
```yaml
---
node_id: "N11"
node_name: "Verify"
exec_type: "inline"
hat: "Popper"
started_at: "ISO-8601"
completed_at: "ISO-8601"
duration_ms: <int>
context_lines_used: <int>
context_budget_lines: 600
signal_flags_raised: ["S11_artifact_gap"]  # if raised
status: "complete"
---
```

#### Body sections:

### V1-V8 Results
For each V1 through V8: PASS/FAIL, evidence (specific citations from the draft), score where applicable (V6 density value, V8 grade level).

### Verdict Aggregation
- Pass count: `<int>/8`
- Pass rate: `<float>`
- HG-3 verdict: PASS/FAIL (constraint compliance)
- HG-5 verdict: PASS/FAIL (overall >= 70%)

### Pass Detection
Narrative assessment: what passed easily, what barely passed, what failed, and whether failures cluster in a particular area (suggesting systematic weakness rather than scattered errors).

### Signal Flags
- S11_artifact_gap: raised / not raised
- If raised: which artifact gap types detected (accuracy/completeness/coverage/depth/provenance)
- E25 gate condition: whether pass=1 AND mode=DEEP AND S11_artifact_gap raised

## SIGNAL_STATE Output

Write `(N11, verification_report)`:
```yaml
pass_rate: <float 0.0-1.0>
v1_v8_results: {v1: pass|fail, v2: pass|fail, ..., v8: pass|fail}
hg3: pass|fail
hg5: pass|fail
signal_flags: ["S11_artifact_gap"]  # if raised
artifact_gap_types: [<list>]  # if raised
```

## Failure Modes

- Enhanced draft is empty → all V1-V8 FAIL; HG-5 FAIL; halt pipeline
- Verification-gates.md KB missing → apply V1-V8 from the embedded table above with the default criteria
- V1-V8 battery takes too long → prioritize V1 (accuracy), V4 (constraints), V8 (readability); the rest can be sampled rather than exhaustive
