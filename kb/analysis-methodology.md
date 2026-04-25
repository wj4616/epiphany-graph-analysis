# Analysis Methodology — Operational Reference (N2 DualAnalyze)

## Overview

N2 DualAnalyze performs dual analysis of Node A and Node B by internally fanning out to two sub-subagents (A1 and B1) in parallel within its Agent context. This achieves parallel A1/B1 execution while counting as 1 orchestrator-level spawn.

---

## Dual Analysis Protocol

### Internal Fan-Out Architecture

N2 dispatches TWO parallel sub-subagent calls within its own Agent context:
- **Sub-agent A1:** Structural analysis of Node A
- **Sub-agent B1:** Findings analysis of Node B

Both run simultaneously. N2 consolidates their outputs before writing its stage file and digest.

**Spawn counting note:** This internal fan-out is within N2's Agent context. It counts as 1 spawn at the orchestrator level (N2 itself).

---

## Sub-agent A1 — Structural Analysis of Node A

### Purpose
Produce a full structural decomposition of Node A with 6 mandatory sections.

### 6 Mandatory Sections

**Intent:** What Node A is trying to accomplish. Its purpose, goals, intended audience. Be specific.

**Structure:** How Node A is organized. Section breakdown, heading hierarchy, flow. List every major section heading verbatim.

**Key Claims:** Explicit assertions, facts, or conclusions stated in Node A. One bullet per claim. Do not paraphrase.

**Constraints:** Every MUST, MUST-NOT, rule, or invariant Node A imposes — on itself, on consumers, or on its behavior. One bullet per constraint. This is the no-regression reference set used by N11 R4 check.

**Gaps:** Missing information, unstated assumptions, or areas where Node A is incomplete.

**Technical Details:** Technical specifics, implementation details, domain-specific content.

### A1 Output Schema

```
a1_complete: true|false
intent: <one paragraph>
structure: [list of section headings verbatim]
key_claims: [list of explicit assertions]
constraints: [list of constraints — CRITICAL: used as R4 reference in N11]
gaps: [list of gaps]
technical_details: [list of technical items]
```

### A1 Completeness Rules

- Mark a1_complete: true when all 6 sections are non-empty OR explicitly marked "(none found)"
- Do NOT retry a section that yields 0 items — record "(none found)" and continue
- Do NOT fabricate content to fill a section
- Verbatim preservation: Key Claims and Constraints must use verbatim or close-paraphrase

---

## Sub-agent B1 — Findings Analysis of Node B

### Purpose (genius-current or genius-drift)
Extract findings from Node B using the Section-Tailoring Map structure.
Produce section-ordered findings list.

### Purpose (generic-fallback)
Run a single generic extraction pass over the full document.
Produce flat findings list with best-guess source_section tags.

### B1 Finding Schema

Each finding:
```
{
  source_section: <section name or "generic">,
  finding_text: <verbatim or close-paraphrase>,
  confidence: H|M|L,
  action_potential: enhance|refine|restructure|validate|none
}
```

### B1 Section Order (genius-current/drift)

1. Headline Insight (FIRST — mandatory)
2. Theory Collisions
3. Discovery vs. Proof
4. Independence-Verified Bridges
5. Alternative Hypotheses (best-fit only — discard runner-ups)
6. Density-Checked Falsification
7. Scope Limits (guardrails only — no scope expansion)
8. Coherence Signals (STRONG only — skip MODERATE/WEAK)
9. Generalization Checks (in-scope breaks only)
10. Open Questions & Next Probes (HIGH-priority only — skip LOW)

### B1 Quality Rules

- For Theory Collisions: extract BOTH positions — never pre-synthesize
- For Alternative Hypotheses: best-fit only — one finding from this section maximum
- For Scope Limits: guardrails only — do not propose scope expansion
- No inference: do not infer findings not stated in Node B

---

## Thin Analysis Detection

N2 raises the S2_thin_B signal when any of:

1. node_b_type == "generic-fallback"
2. node_b_type == "inline-substitute"
3. Fewer than 3 canonical genius sections found (from N1 matched_sections count)

When S2_thin_B is raised:
- Include "S2_thin_B" in analysis_digest.signal_flags
- E04 gate (N2->N3) evaluates FALSE -> N3 not activated
- E06 back-edge gate evaluates TRUE -> N6 defixation enqueued

---

## Full Analysis Digest Schema

```
a1_summary:
  intent: <paragraph>
  structure: [section headings]
  key_claims: [list]
  constraints: [list - critical for R4 in N11]
  gaps: [list]
  technical_details: [list]
b1_summary:
  findings: [{source_section, finding_text, confidence, action_potential}]
  finding_count: N
  sections_covered: [list]
node_b_type: genius-current|genius-drift|generic-fallback|inline-substitute
signal_flags: [S2_thin_B] or []
a1_section_count: N
b1_finding_count: N
```
