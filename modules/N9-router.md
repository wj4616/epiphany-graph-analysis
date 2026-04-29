---
node_id: "N9"
node_name: "Router"
module_version: "1.0.0"
type: ROUTER
exec_type: "inline"
hat: null
context_budget_lines: 50
scale_gates: ["STANDARD", "DEEP"]
activation:
  - "always"
raises_signals: []
required_output_sections:
  - "Routing Decision"
  - "Falsification Summary"
  - "Gate Evaluation"
input_dependencies:
  - "(N7, falsification_result)"
optional_inputs:
  - "(N6, breakthrough_digest)"
kb_files: []
output_signal_fields:
  - "falsification_digest"
output_file: "stages/N9-router.md"
hard_gates_referenced: ["HG-4"]
---

# N9 -- Router

## Role

Minimal decision node. Reads N7's falsification result and determines whether the pipeline proceeds to N8 (synthesis) or loops back through N6 (defixation). This is a pure routing function with no creative hat.

## PROTOCOL

### Inputs

- Read `falsification_result` from SIGNAL_STATE (N7's output): `verdict` (pass/fail/partial), `signal_flags`
- Check `executed_nodes` list for N6 -- has defixation already run?

### Decision Logic

1. If `falsification_result.verdict == "pass"`:
   - Route: N9 → N8 (via E21 gate-open)
   - Write `falsification_digest` with status=go
   - N6 back-edge (E20) does NOT fire

2. If `falsification_result.verdict in ("fail", "partial")` AND `S7_no_alternatives in falsification_result.signal_flags` AND N6 has NOT run:
   - Route: N9 → N6 (via E20 back-edge)
   - E20 gate condition: `falsification_result.signal_flags ∋ S7_no_alternatives ∧ N6 ∉ executed_nodes`
   - E21 to N8 is HELD until N6 completes and N9 re-evaluates
   - Write `falsification_digest` with status=loopback

3. If `falsification_result.verdict in ("fail", "partial")` but S7_no_alternatives is NOT raised (or N6 already ran):
   - Route: N9 → N8 (via E21) with warning annotation
   - Write `falsification_digest` with status=go-with-warnings

### Output

Write `stages/N9-router.md` with:

### Routing Decision
Declare: chosen route (N8 / N6-loopback / N8-with-warnings). Include the specific condition that triggered the decision.

### Falsification Summary
Compact restatement of N7's verdict, any signal flags raised, and whether breakthrough_digest from N6 was available.

### Gate Evaluation
For E20 (back-edge to N6): evaluate `S7_no_alternatives ∧ ¬N6_ran` -> result (true/false).
For E21 (gate-open to N8): declare whether gate is open.

## SIGNAL_STATE Output

Write `(N9, falsification_digest)`:
```yaml
router_verdict: "go" | "loopback" | "go-with-warnings"
route: "N8" | "N6" | "N8-warn"
e20_fired: true | false
e21_open: true | false
```

## Failure Modes

- N7 output missing -> halt with HG-4 failure; cannot route without falsification result
- N6 already ran but falsification still fails -> route to N8 with warnings; do not loop infinitely
