---
node_id: "N8"
node_name: "SolutionEngineer"
module_version: "1.0.0"
type: ENGINEER
exec_type: "inline"
hat: "Feynman + Boden"
context_budget_lines: 2000
scale_gates: ["STANDARD", "DEEP"]
activation:
  - "always"
raises_signals: []
required_output_sections:
  - "Solution Catalog"
  - "Budget Report"
  - "Dropped-by-Budget"
  - "Failure Mode Log"
input_dependencies:
  - "(N4, xref_map)"
  - "(N5.5, accepted_ideas_digest)"
  - "(N9, falsification_digest)"
optional_inputs:
  - "(N6, breakthrough_digest)"
  - "(N7, adversarial_digest)"
  - "(N1, intake_digest)"
kb_files:
  - "verification-gates.md"
  - "oppositional-drafting-axes.md"
output_signal_fields:
  - "solutions_digest"
output_file: "stages/N8-solution-engineer.md"
hard_gates_referenced: ["HG-3"]
---

# N8 -- SolutionEngineer (Feynman + Boden)

## Role

The most consequential cognitive operation in the pipeline. Takes every accepted idea (from N5.5) and breakthrough idea (from N6), and engineers each into a concrete, budgeted solution that N10 can integrate into the enhanced draft. Each solution is produced via the **hybrid protocol**: oppositional drafting (A vs B along a chosen axis), winner selection, critique-and-refine (1 or 2 iterations).

This is the quality heart of the pipeline. Every solution that reaches N10 was drafted twice, compared, critiqued, and refined.

## PROTOCOL

### Inputs

From SIGNAL_STATE:
- `accepted_ideas_digest` (E14, from N5.5): filtered accepted ideas with Boden scores
- `xref_map` (E12, from N4): cross-reference map for target context
- `falsification_digest` (E21, from N9): router verdict, whether N7 passed
- `breakthrough_digest` (E16, optional, from N6): breakthrough ideas if defixation ran
- `adversarial_digest` (E19, optional, from N7): per-idea falsification results with verdicts
- `intake_digest` (from N1): for S1 complexity bucket

From disk:
- `kb/oppositional-drafting-axes.md`: the 7 axes (A0-A6) with pole definitions
- `kb/verification-gates.md`: comparison rubric and HG-3 criteria
- `{session_dir}/input-a.md`: full Node A source text for context

### Iteration Count

| Mode | S1 Complexity | Iterations After Winner |
|---|---|---|
| STANDARD | low | 1 (refined_v1 = final) |
| STANDARD | medium | 1 |
| STANDARD | high | 2 (refined_v2 = final) |
| DEEP | any | 2 |

### Hybrid Protocol (per idea)

For each accepted idea `I_n` (and each breakthrough idea `B_n` if N6 ran):

#### Step 1: Pick Oppositional Axis

Apply the selection algorithm (most-specific first, A0 fallback):

```
if idea touches phrasing or style → A1
elif idea scope is ambiguous → A2
elif idea creates constraint tension → A3
elif idea is principle-vs-procedure choice → A4
elif idea has uncertain payoff → A5
elif idea target section format ambiguous → A6
else → A0
```

The 7 axes:

| Axis | Pole 1 | Pole 2 | When Applied |
|---|---|---|---|
| **A0** | Minimal-change | Ambitious-restructure | Default fallback |
| A1 | Preserve-original-voice | Rewrite-for-clarity | Touches phrasing/style |
| A2 | Conservative-scope | Expansive-scope | Scope ambiguous |
| A3 | Strict-constraint-preservation | Constraint-relaxation | Creates constraint tension |
| A4 | Abstract-principle | Specific-recipe | Principle-vs-procedure choice |
| A5 | Risk-averse | Risk-seeking | Uncertain payoff |
| A6 | Inline-integration | Sidebar-integration | Format ambiguous |

Reference `kb/oppositional-drafting-axes.md` for the full definitions.

#### Step 2: Draft A (Pole 1)

Role-switch into pole-1 stance. Draft a concrete solution: what specific text change, addition, or restructuring should N10 apply to Node A? Be concrete: specify the target section (§N.M), the change type (insert/rewrite/augment/reconnect/qualify/restructure/elevate), and the content of the change.

Draft A should be a self-contained enhancement specification, not a paragraph of prose about the idea.

#### Step 3: Draft B (Pole 2)

**Pattern α framing**: Before drafting B, explicitly instruct yourself: *"Forget Draft A entirely. You are drafting fresh from the idea description and pole-2 framing only. Do not echo, contrast, or reference Draft A."*

Apply pole-2 stance. Draft a fresh solution targeting the same Node A location. Do NOT produce a reaction to Draft A -- produce an independent solution that happens to be from the opposite pole.

#### Step 4: Compare

Compare Draft A and Draft B using the rubric from `kb/verification-gates.md`. Assess:
- Which is more specific? (concrete edits vs. general direction)
- Which is more feasible? (can N10 actually execute this?)
- Which is more impactful? (larger improvement to the enhanced draft)
- Which is more constraint-compliant? (respects Node A's MUST/MUST NOT directives)

Record `comparison_rationale` naming specific strengths of each draft. Pick `winner ∈ {A, B}`.

#### Step 5: Critique Winner

Critique the winning draft against:
1. **Original B-finding**: does this solution actually address what Node B identified?
2. **Node A constraint**: does this solution violate any constraint N1 cataloged?
3. **Loser's strengths**: does the losing draft have strengths the winner lacks? Can they be incorporated?
4. **Adversarial results** (if available from N7): did N7's falsification identify weaknesses in the idea this solution is based on?
5. **Counter-examples**: can you think of a case where this solution would make things worse?

Record `critique_1` as a structured assessment: what's strong, what's weak, what's missing.

#### Step 6: Refine v1

Produce `refined_v1`: the winning draft, improved by addressing every actionable item from `critique_1`. If critique found no actionable defects, `refined_v1` can be identical to the winner (note: "no actionable defects").

#### Step 7: Conditional Iteration 2

If iteration count = 2:
- **7a. Critique refined_v1** with fresh eyes. Ask: "If this were the final version shipped to N10, what would go wrong?" If answer is "nothing actionable," record `critique_2.verdict = "no_actionable_defects"` and use refined_v1 as final.
- **7b. Refine v2** addressing `critique_2`. This is `refined_v2`.

#### Step 8: Finalize

`final = refined_v2` (if exists) else `refined_v1`.

#### Step 9: Score

Assign final scores:
- **pro** ∈ {high, medium, low}: strength of the solution's positive case
- **con** ∈ {high, medium, low}: severity of remaining weaknesses
- **utility** ∈ {high, medium, low}: net value to the enhanced draft
- **status** ∈ {ACCEPT, ACCEPT-CONDITIONAL, REJECT, DROPPED}:
  - ACCEPT: ready for N10 integration, no conditions
  - ACCEPT-CONDITIONAL: ready but N10 must resolve a noted tension
  - REJECT: protocol determined this solution is not viable
  - DROPPED: not fully processed (budget exhaustion, context loss, both drafts weak, wrong direction)

#### Step 10: Append to Solution Catalog

### HG-3 Compliance

Every solution with `status ∈ {ACCEPT, ACCEPT-CONDITIONAL}` MUST have:
1. `oppositional_axis` named (A0-A6)
2. `draft_A` and `draft_B` both present
3. `comparison_rationale`, `winner`, `critique_1`, `refined_v1`
4. When iterations=2: `critique_2` always required; `refined_v2` required UNLESS `critique_2.verdict = "no_actionable_defects"`
5. `final` field set

### Wall-Clock Budget

- 1 iteration: ~30-60 sec per solution
- 2 iterations: ~50-90 sec per solution
- Hard halt: 15 minutes total for N8

**Budget-defer trigger**: If accumulated wall-clock reaches 75% of the 15-minute hard halt (i.e., 11.25 min) AND <100% of accepted ideas have been processed, stop processing. Write unprocessed ideas to `dropped-by-budget.md`.

Context budget is monitored separately: if approaching 2000-line limit, complete the current solution and stop.

### Output

Write `stages/N8-solution-engineer.md` with:

#### Frontmatter:
```yaml
---
node_id: "N8"
node_name: "SolutionEngineer"
exec_type: "inline"
hat: "Feynman + Boden"
started_at: "ISO-8601"
completed_at: "ISO-8601"
duration_ms: <int>
context_lines_used: <int>
context_budget_lines: 2000
signal_flags_raised: []
status: "complete"
iteration_count: 1 | 2
---
```

#### Body sections:

### Solution Catalog

For each accepted idea processed, a full solution entry:

```
### S<NN>: <title>

- **Source Idea**: <I_n or B_n ID from N5.5/N6>
- **Boden Scores**: novelty=<int>, value=<int>, non-obviousness=<int>, composite=<float>
- **Target**: §N.M in Node A, B-ID from xref_map
- **Oppositional Axis**: A0–A6
- **Pole 1 / Pole 2**: <which poles>

**Draft A (Pole 1 — <name>):**
<concrete solution text>

**Draft B (Pole 2 — <name>):**
<concrete solution text, produced with Pattern α>

**Comparison Rationale:**
- Draft A strengths: ...
- Draft B strengths: ...
- Winner: A | B
- Reason: ...

**Critique 1:**
- Against B-finding: ...
- Against constraints: ...
- Loser's strengths to incorporate: ...
- Adversarial findings (if any): ...
- Counter-examples: ...

**Refined v1:**
<refined solution text>

[If iteration count = 2:]
**Critique 2:**
- Verdict: actionable_defects | no_actionable_defects
- [If actionable:] Specific issues: ...

**Refined v2:**
<further refined solution, or "not produced — no_actionable_defects">

**Final:** <final solution text, or "= refined_v1" if no v2>

**Scores:**
- Pro: high | medium | low
- Con: high | medium | low
- Utility: high | medium | low
- Status: ACCEPT | ACCEPT-CONDITIONAL | REJECT | DROPPED
```

### Budget Report

- Accepted ideas received (N5.5): `<int>`
- Breakthrough ideas received (N6): `<int>` (or 0)
- Total ideas to process: `<int>`
- Ideas fully processed: `<int>`
- Ideas deferred by budget: `<int>` (listed in Dropped-by-Budget)
- Wall-clock used: `<int>` sec / 900 sec hard halt
- Status: COMPLETE | BUDGET-DEFERRED | TRUNCATED

### Dropped-by-Budget

Only present if budget-defer trigger fired. For each unprocessed idea:
- Idea ID, summary, Boden composite, recommended axis (what would have been picked)

### Failure Mode Log

Every protocol failure:
- Ideas where both drafts were weak → `both_drafts_inadequate`, DROPPED
- Ideas where critique found wrong direction → `wrong_direction`, DROPPED
- Ideas where refined_v2 was strictly worse than refined_v1 → used refined_v1, logged
- Ideas where context exhausted mid-solution → PARTIAL, remaining ideas DROPPED

## SIGNAL_STATE Output

Write `(N8, solutions_digest)`:
```yaml
total_accepted_ideas: <int from N5.5 + N6>
solutions_finalized: <int>      # entered full protocol, got final with status ACCEPT/ACCEPT-CONDITIONAL
solutions_dropped_in_protocol: <int>  # entered protocol but was REJECT/DROPPED during it
solutions_deferred_by_budget: <int>   # never entered protocol; in dropped-by-budget.md
status_distribution: {ACCEPT: <int>, ACCEPT-CONDITIONAL: <int>, REJECT: <int>, DROPPED: <int>}
```

## Failure Modes

- No accepted ideas (N5.5 produced zero) → write empty solution catalog with status "no_input"; N10 will produce degraded synthesis
- Oppositional-drafting-axes KB missing → use A0 for all ideas (A0 is self-contained in the protocol)
- Both drafts equivalently weak for an idea → DROPPED with `both_drafts_inadequate`; this is a legitimate outcome
- Context budget exhausted mid-protocol → complete current solution, HALT; remaining ideas listed in dropped-by-budget as "CONTEXT-EXHAUSTED"
- All ideas REJECTED/DROPPED → write catalog with zero ACCEPT solutions; N10 degrades to readability-only synthesis
