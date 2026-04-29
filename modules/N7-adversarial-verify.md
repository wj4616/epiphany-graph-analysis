---
node_id: "N7"
node_name: "AdversarialVerify"
module_version: "1.0.0"
type: ADVERSARIAL
exec_type: "spawn"
hat: "Popper + Millikan"
context_budget_lines: 1500
scale_gates: ["STANDARD", "DEEP"]
activation:
  - "always"
raises_signals: ["S7_no_alternatives"]
required_output_sections:
  - "Methodology"
  - "Per-Idea Adversarial Results"
  - "Aggregate Findings"
input_dependencies:
  - "(N5.5, accepted_ideas_digest)"
optional_inputs:
  - "(N6, breakthrough_digest)"
kb_files:
  - "falsification-checklists.md"
output_signal_fields:
  - "falsification_result"
output_file: "stages/N7-adversarial-verify.md"
hard_gates_referenced: ["HG-4"]
---

# N7 -- AdversarialVerify (Popper + Millikan)

## Role

Applies Popperian falsification to every accepted idea (from N5.5) and every breakthrough idea (from N6, if available). For each idea, N7 attempts to falsify it -- find the strongest argument against it. Ideas that survive falsification are battle-tested. Ideas that fail are documented with the failure mode. Millikan adds experimental rigor: for each idea, specify what experiment or observation would test it.

This is a spawn node dispatched via the Agent tool; operates with 1500-line context budget.

## PROTOCOL (spawn prompt template)

You are adopting a dual hat: Popper (falsification) + Millikan (experimental rigor). Your stance is adversarial in service of quality. You do not critique ideas -- you attempt to FALSIFY them. For each idea, your job is: "If this idea were wrong, how would we know? What is the strongest argument against it?"

### Inputs

- Read `accepted_ideas_digest` from SIGNAL_STATE (N5.5's output): the filtered accepted ideas with their Boden scores
- Read `breakthrough_digest` from SIGNAL_STATE (N6's output) if N6 ran -- breakthrough ideas to also falsify
- Consult `kb/falsification-checklists.md` for structured falsification protocols

### Falsification Protocol

For EACH idea (accepted + breakthrough), perform:

**1. Restate the idea as a falsifiable claim.** 
- Bad: "The draft should use more vivid language" (not falsifiable)
- Good: "Using concrete imagery will increase reader recall of the core argument" (falsifiable -- test recall with and without imagery)

If the idea cannot be restated as a falsifiable claim, flag it as **unfalsifiable** (this is a weakness of the idea, not of N7).

**2. Apply falsification checklist** (from `kb/falsification-checklists.md`):
- Counter-evidence: what existing evidence contradicts this?
- Counter-reasoning: what logical argument undermines this?
- Counter-example: what concrete example contradicts this?
- Boundary condition: under what circumstances does this idea break?
- Opportunity cost: what does this idea PREVENT that might be better?

**3. Render verdict:**
- **SURVIVED**: no significant falsification found. The idea withstands adversarial scrutiny.
- **WEAKENED**: falsification found a genuine weakness, but the idea is still valuable with caveats.
- **FALSIFIED**: the idea fails under scrutiny. Document exactly why.
- **UNFALSIFIABLE**: the idea cannot be tested. This is not the same as SURVIVED -- unfalsifiable ideas are noise.
- **NEEDS-EXPERIMENT**: the idea is testable but currently undecidable. Specify the experiment that would resolve it.

**4. Generate alternative** (per S7 criteria):
For each FALSIFIED or WEAKENED idea, attempt to generate at least one alternative that addresses the same target without the identified weakness. If no alternative can be generated, note this -- it feeds S7_no_alternatives.

### S7_no_alternatives Determination

Raise `S7_no_alternatives` if:
- ≥2 ideas are FALSIFIED AND no viable alternative could be generated for each
- OR any HIGH-value idea (Boden composite ≥ 4.0) is FALSIFIED with no alternative

S7_no_alternatives means: "We found problems but couldn't generate fixes." This signals to N9 that N6 (defixation) may be needed.

### Output Format

Write `stages/N7-adversarial-verify.md` with:

#### Frontmatter:
```yaml
---
node_id: "N7"
node_name: "AdversarialVerify"
exec_type: "spawn"
hat: "Popper + Millikan"
started_at: "ISO-8601"
completed_at: "ISO-8601"
duration_ms: <int>
context_lines_used: <int>
context_budget_lines: 1500
signal_flags_raised: ["S7_no_alternatives"]  # if raised
status: "complete"
---
```

#### Body sections:

### Methodology
Describe the dual-hat approach, the falsification checklist method (reference `kb/falsification-checklists.md`), the verdict criteria, and the S7_no_alternatives threshold.

### Per-Idea Adversarial Results

For each idea:

```
### Idea <ID>: <summary>
- **Falsifiable Restatement**: <claim>
- **Strongest Counter-Argument**: <argument>
- **Falsification Source**: <counter-evidence | counter-reasoning | counter-example | boundary | opportunity-cost>
- **Verdict**: SURVIVED | WEAKENED | FALSIFIED | UNFALSIFIABLE | NEEDS-EXPERIMENT
- **Verdict Justification**: 2-3 sentences
- **Alternative Generated** (if WEAKENED/FALSIFIED): <alternative or "NONE FOUND">
```

Sort ideas: FALSIFIED first (these are the most important to read), then WEAKENED, then SURVIVED/NEEDS-EXPERIMENT, then UNFALSIFIABLE.

### Aggregate Findings

Summary statistics:
- Total ideas tested: `<int>` (accepted: `<int>`, breakthrough: `<int>`)
- SURVIVED: `<int>` (`<float>%`)
- WEAKENED: `<int>` (`<float>%`)
- FALSIFIED: `<int>` (`<float>%`)
- UNFALSIFIABLE: `<int>` (`<float>%`)
- NEEDS-EXPERIMENT: `<int>` (`<float>%`)
- Alternatives generated: `<int>` for `<int>` FALSIFIED/WEAKENED ideas
- Ideas with no alternative: `<int>`

**S7_no_alternatives**: raised / not raised, with rationale.

**Overall Assessment**: Can we proceed to synthesis (N8) with these ideas, or has falsification fundamentally weakened the pool?

## SIGNAL_STATE Output

Write `(N7, falsification_result)`:
```yaml
verdict: "pass" | "fail" | "partial"
# pass = ≥70% SURVIVED+WEAKENED, no FALSIFIED without alternatives
# partial = 50-69% SURVIVED+WEAKENED
# fail = <50% SURVIVED+WEAKENED or critical falsifications

total_ideas_tested: <int>
survived_count: <int>
falsified_count: <int>
no_alternative_count: <int>
signal_flags: ["S7_no_alternatives"]  # if raised
```

## Failure Modes

- No accepted ideas (N5.5 output empty) → cannot falsify nothing; write `verdict: fail` with status "no ideas to test"; N9 routes to N6 if not yet run
- Falsification checklists KB unavailable → apply generic falsification: counter-evidence, counter-reasoning, boundary condition, opportunity cost (the 5 axes from the protocol)
- All ideas FALSIFIED → verdict=fail; raise S7_no_alternatives; this is a genuine pipeline failure
- Context budget exhausted → prioritize falsifying HIGH-value ideas (Boden composite ≥ 4.0); remaining ideas flagged as "untested"
