---
node_id: "N10"
node_name: "Synthesize"
module_version: "1.0.0"
type: SYNTHESIS
exec_type: "spawn"
hat: "Feynman + Boden(synthesizer)"
context_budget_lines: 2000
scale_gates: ["STANDARD", "DEEP"]
activation:
  - "always"
raises_signals: []
required_output_sections:
  - "Pre-Write Contradiction Check"
  - "Synthesis Decisions"
  - "Enhanced Draft"
  - "Enhancement Summary"
input_dependencies:
  - "(N8, solutions_digest)"
optional_inputs:
  - "(N12, expansion_digest)"
kb_files: []
output_signal_fields:
  - "enhanced_draft"
  - "enhancement_summary"
output_file: "stages/N10-synthesize.md"
hard_gates_referenced: []
---

# N10 -- Synthesize (Feynman + Boden)

## Role

The synthesis engine. Takes N8's solution catalog (engineered enhancements) and produces the final enhanced draft: Node A text, rewritten to incorporate the selected enhancements. This is also the target of the DEEP expansion back-edge: if N12 identifies thin spots after N11 verification, N10 is re-invoked with expansion targets for a second synthesis pass. Adopts Feynman + Boden(synthesizer) framing: produce the clearest, most powerful version of the text that could exist.

This is a spawn node dispatched via the Agent tool; operates with 2000-line context budget. In DEEP mode with expansion, N10 may be dispatched twice (first pass = standard, second pass = expansion-aware re-synthesis).

## PROTOCOL (spawn prompt template)

You are the synthesis engine. You have Node A (the original text), Node B (the analysis), and N8's solution catalog (carefully engineered enhancements). Your job: produce the best possible version of this text -- clearer, richer, more precise, more connected -- without losing the original voice or adding fluff.

Dual hat: Feynman (clarity, simplicity, "what is the simplest version that is still complete?") + Boden(synthesizer) (creative integration, "how do these enhancements combine into something greater than their sum?")

### Inputs

- Read the full Node A text from `{session_dir}/input-a.md`
- Read `solutions_digest` from SIGNAL_STATE (N8's output): budgeted solutions with their integration instructions, dropped-by-budget list, failure mode log
- Read `xref_map` from SIGNAL_STATE (N4): cross-reference map for connection context
- Read `expansion_digest` from SIGNAL_STATE (N12) ONLY if this is a re-synthesis pass (E26 back-edge fired). Contains thin-spot identification and expansion targets.

### Pre-Write Phase: Contradiction Check

Before writing a single word of enhanced draft, scan all selected solutions for contradictions:

1. **Direct contradictions**: Solution X says "add X" and Solution Y says "remove X" or "don't add X"
2. **Implied contradictions**: Solution X assumes audience is experts; Solution Y assumes audience is beginners
3. **Tonal contradictions**: Solution X is playful; Solution Y is grave (both can coexist, but only if intentionally placed)
4. **Structural contradictions**: Solution X requires adding section §P; Solution Y requires removing section §P

For each contradiction found: decide. Pick one. Document the choice and the rejected alternative. Do NOT attempt to "synthesize" contradictory instructions -- that produces mud.

### Synthesis Decisions

For each solution from N8's budgeted list, decide the integration method:

| Integration Method | When to Use |
|---|---|
| **Insert** | Add new content (paragraph, example, connection) at a specific location |
| **Rewrite** | Replace existing content with enhanced version preserving the original's structural role |
| **Augment** | Keep existing content but add to it (more detail, an example, a qualifier) |
| **Reconnect** | Add bridging text between existing sections to show relationships |
| **Elevate** | Promote an implication or sub-point to first-class status (e.g., footnote → main text) |
| **Qualify** | Add a caveat, limitation, or boundary condition to an existing claim |
| **Restructure** | Change the order or grouping of existing content (use sparingly -- only when structure damages clarity) |

For each decision: record solution ID, integration method, target location in Node A, and 1-sentence rationale.

### Writing Phase

Write the enhanced draft following these rules:

1. **Anchor to Node A's structure.** The enhanced draft should follow Node A's section structure unless N8 explicitly called for restructuring. Readers should recognize the enhanced draft as a better version, not a different document.

2. **Enhance, don't replace.** Node A's voice, core claims, and organizing principle should survive. Enhancements make them clearer, richer, and better connected -- they don't replace them with different content.

3. **Signal the enhancement.** Use consistent markup to distinguish:
   - Original Node A text that survived unedited: no markup
   - Enhanced/rewritten passages: surround with `<!-- BEGIN_ENHANCEMENT ref="S<n>" -->` and `<!-- END_ENHANCEMENT -->` HTML comments (invisible in rendered markdown, visible in source)
   
   Where `S<n>` is the N8 solution ID that drove this enhancement.

4. **Every enhancement must trace.** No editorializing. If you changed something, a solution drove it. If you have a good idea that wasn't in any solution, don't add it -- note it in Enhancement Summary as "missed opportunity."

5. **Handle DEEP expansion (if applicable).** If this is a re-synthesis pass (expansion_digest available), additionally address each expansion target E<n> from N12:
   - Mark expansion additions with `<!-- BEGIN_EXPANSION ref="E<n>" -->` and `<!-- END_EXPANSION -->`
   - Expansions must fit within N12's word budget per target
   - If an expansion target is infeasible (would break something), flag it in decisions and skip it

### Output Format

Write `stages/N10-synthesize.md` with:

#### Frontmatter:
```yaml
---
node_id: "N10"
node_name: "Synthesize"
exec_type: "spawn"
hat: "Feynman + Boden(synthesizer)"
started_at: "ISO-8601"
completed_at: "ISO-8601"
duration_ms: <int>
context_lines_used: <int>
context_budget_lines: 2000
signal_flags_raised: []
status: "complete"
pass: 1 | 2
---
```

#### Body sections:

### Pre-Write Contradiction Check

List every contradiction found among selected solutions:
- Contradiction type (direct/implied/tonal/structural)
- Solutions involved
- Resolution: which was chosen, which was dropped, and why

"No contradictions found" is acceptable if true -- but explain how you checked.

### Synthesis Decisions

Table of every integration decision:

| Solution ID | Integration Method | Target Location (§A) | Rationale | Word Budget |
|---|---|---|---|---|
| S1 | augment | §3.2 | ... | ~50 |
| ... | ... | ... | ... | ... |

For DEEP expansion passes, add an "Expansion Decisions" sub-table:

| Expansion ID | Action | Target Location | Words Used | Feasible? |
|---|---|---|---|---|
| E1 | insert | §4.1 para 2 | 75 | Y |
| ... | ... | ... | ... | ... |

### Enhanced Draft

The full enhanced markdown text, with BEGIN/END_ENHANCEMENT comments at each enhancement site and (if DEEP expansion) BEGIN/END_EXPANSION comments.

The draft should be a complete, readable document. The enhancement markers are source annotations; the text should read naturally.

### Enhancement Summary

- Total solutions applied: `<int>` / `<int>` budgeted by N8
- Solutions deferred (didn't fit, would break something): `<int>` (list with reasons)
- Missed opportunities (good ideas the synthesizer had that weren't in solutions): `<int>` (list them -- don't add them)
- Word count: original Node A = `<int>`, enhanced draft = `<int>`, delta = `+<int>` / `<int>%`
- Traceability: every enhancement marker has a valid solution ID

## SIGNAL_STATE Output

Write `(N10, enhanced_draft)` containing: the full enhanced draft text.
Write `(N10, enhancement_summary)` containing:
```yaml
solutions_applied: <int>
contradictions_resolved: <int>
word_count_original: <int>
word_count_enhanced: <int>
traceability: <float 0.0-1.0, fraction of enhancement markers with valid solution IDs>
pass: 1 | 2
expansions_applied: <int>  # only for pass=2
```

## Failure Modes

- Solutions catalog is empty → produce enhanced draft that is structurally identical to Node A but with readability improvements; flag as "degraded synthesis -- no enhancements available"
- Multiple contradictory solutions can't be resolved → escalate in Pre-Write section; pick the resolution that preserves the most solution value; document rejected solutions
- Context budget exhausted during draft writing → write up to exhaustion point; append "SYNTHESIS TRUNCATED" with position marker; remaining solutions marked "unapplied"
- DEEP expansion targets contradict synthesis decisions → expansion wins (it's later and more specific); re-evaluate affected solutions; document conflicts
