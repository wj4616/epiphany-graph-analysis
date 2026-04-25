# Input Pre-loading Templates — Dual-Input Reference (N1)

## Usage

N1 IntakeDecompose uses these templates to classify Node A's document type and structure its primitive enumeration. Node B classification uses the Genius Detection algorithm (see section-tailoring-map.md). This file covers Node A classification only.

---

## Node A Class Detection

| Class | Signal |
|-------|--------|
| Algorithmic | Code snippets, pseudocode, performance/complexity language, data structure references |
| Design | Architecture decisions, trade-offs, UX/UI, system design, API surface, constraints between components |
| Proof | Mathematical notation, "prove that", "show that", logical claims, formal definitions |
| Diagnostic | "Why is X not working", error messages, unexpected behavior, debugging, root-cause |
| Specification | Requirements lists, MUST/MUST-NOT statements, feature definitions, acceptance criteria |
| Prose/Conceptual | Essays, explanations, conceptual frameworks, strategic/planning documents |
| Other | Mixed or unclassifiable; use Template 6 |

---

## Template 1 — Algorithmic

**Primitive categories (enumerate ≥20 per category):**

1. **Facts known** — What does the code/algorithm currently do? What are its guaranteed properties?
2. **Constraints** — Time complexity bounds, space bounds, input size assumptions, ordering guarantees, data structure requirements
3. **Unknowns** — What behavior is unspecified? What edge cases are unhandled?
4. **Failed approaches** — Which implementations have been attempted and why did they fail?
5. **Performance measurements** — Specific timings, throughput numbers, bottleneck locations if known
6. **Input invariants** — What can be assumed about inputs that is not explicitly stated?
7. **Adjacent operations** — What other operations operate on the same data? Are there ordering dependencies?

**Gap indicators:** Missing error handling, unspecified edge cases, implicit invariants.

---

## Template 2 — Design

**Primitive categories (enumerate ≥20 per category):**

1. **Components** — What are the system components? What does each do independently?
2. **Interfaces** — What are the communication contracts between components? Which are hard vs. soft?
3. **Known constraints** — Performance SLAs, team/org constraints, technology mandates, budget
4. **Quality attributes** — Scalability, maintainability, testability, security — what is actually required vs. desirable?
5. **Stakeholder requirements** — Explicit vs. implicit needs; who owns which requirements?
6. **Trade-off history** — What design decisions have been made and what was sacrificed?
7. **Failure modes** — What can go wrong in each component? What cascade failure paths exist?

**Gap indicators:** Undocumented trade-offs, implicit stakeholder requirements, unspecified failure modes.

---

## Template 3 — Proof

**Primitive categories (enumerate ≥20 per category):**

1. **Definitions** — All formal definitions in use (stated verbatim, not paraphrased)
2. **Axioms/given facts** — What is assumed without proof?
3. **Target claim** — The exact statement to be proved (verbatim, then formalized)
4. **Known partial results** — What has been proven? What lemmas are available?
5. **Failed proof attempts** — Which proof strategies were tried? Where did they break down?
6. **Analogous results** — What structurally similar theorems exist in the literature?
7. **Necessary conditions** — What must be true for the claim to hold?

**Gap indicators:** Unverified lemmas, circular dependencies, unspecified scope conditions.

---

## Template 4 — Diagnostic

**Primitive categories (enumerate ≥20 per category):**

1. **Observed symptoms** — Exact error messages, observed behaviors, unexpected outputs (verbatim)
2. **Expected behavior** — What should happen instead? Under what conditions?
3. **Reproduction conditions** — What triggers the problem? Is it consistent or intermittent?
4. **System state** — Environment, version, configuration, recent changes
5. **Hypotheses tested** — What causes have been ruled out? How was each ruled out?
6. **Causal candidates** — What could still explain the symptom? (full list including unlikely)
7. **Interactions** — What other system components interact with the failing component?

**Gap indicators:** Untested hypotheses, missing reproduction steps, unexplored interactions.

---

## Template 5 — Specification

**Primitive categories (enumerate ≥20 per category):**

1. **Functional requirements** — What the system MUST do (explicit MUST/SHALL statements)
2. **Non-functional requirements** — Performance, security, usability, reliability constraints
3. **Constraints** — What the system MUST NOT do; hard limits
4. **Stakeholders** — Who are the stakeholders? What does each value?
5. **Acceptance criteria** — How will compliance be verified? What constitutes success?
6. **Out of scope** — What is explicitly excluded from this specification?
7. **Open questions** — What decisions remain undecided?

**Gap indicators:** Missing acceptance criteria, ambiguous MUST statements, unstated stakeholder needs.

---

## Template 6 — Prose/Conceptual/Other

**Primitive categories (enumerate ≥20 per category):**

1. **Core claim/question** — What is the central thing being asked or asserted?
2. **Background facts** — What is established about the topic?
3. **Key tensions** — Where do competing considerations pull in different directions?
4. **Stakeholders** — Who is affected by the answer? What do they value?
5. **Analogous domains** — What areas have faced similar structural questions?
6. **Success criteria** — What would a good answer or solution look like?
7. **Open sub-questions** — What questions must be answered before the main question?

**Gap indicators:** Unsupported claims, implicit assumptions, missing analogous domain references.

---

## Count Requirement

For each category: enumerate ≥20 primitives. If fewer than 20 candidates genuinely exist in Node A, state the cap explicitly:
"Node A contains [N] [category] primitives; 20-item target not met — constraint is the input, not enumeration."

Do NOT fabricate primitives to meet the count.

---

## Dual-Input Summary Format (N1 Output)

After enumerating Node A primitives and performing Genius Detection on Node B, write the intake_digest in this format:

```
node_a_path: <path or "inline">
node_b_path: <path or "inline-substitute">
node_b_type: <genius-current|genius-drift|generic-fallback|inline-substitute>
node_a_word_count: <integer>
node_a_class: <Algorithmic|Design|Proof|Diagnostic|Specification|Prose|Other>
node_b_section_count: <integer — total sections found in Node B>
node_a_summary: <2-3 sentence plain description of Node A's purpose and structure>
matched_sections: [<list of matched canonical sections for genius-drift, or empty>]
signal_flags: []
```

---

## HG-1 Verification Template

After loading both inputs, verify before any further work:

```
HG-1 Check:
  enhanced.md target: {session_dir}/enhanced.md
  Node A source: {node_a_path}
  Same path? <YES → HALT / NO → continue>
```

If same path: HALT with message: "HG-1 violation: Node A source path equals enhanced.md target. The skill never overwrites Node A."
