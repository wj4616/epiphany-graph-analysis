# Analysis Methodology

Referenced by N2a (AnalyzeA, Tesla measurement) and N2b (AnalyzeB, Darwin variation-survey). Defines the A1 and B1 analysis frameworks.

## A1 — Node A Structural Analysis (Tesla Measurement)

Applied by N2a. Focus on quantifiable structure.

### Structural Survey Method

1. Parse all markdown headers via regex `^(#+)\s+\S`. Record nesting depth (= len(m.group(1))), header text, and line number.
2. For each section: measure line count (header to next header or EOF), classify apparent role from header text and first sentence:
   - **claim** — asserts something as true
   - **evidence** — provides support for a claim
   - **constraint** — states what must/must not be done
   - **example** — illustrates with a concrete case
   - **bridge** — connects two other sections
   - **meta** — about the document itself (preamble, scope, conventions)

### Claim Extraction Criteria

A "claim" is a declarative sentence that asserts something a reader could disagree with. Exclude:
- Section headers
- Metacommentary ("This section discusses...")
- Questions
- Imperatives (these are constraints, not claims)

For each claim: label type, rate specificity (1=vague to 5=precise), note supporting evidence cited.

### Constraint Audit Scope

Search for MUST, MUST NOT, SHALL, REQUIRED, FORBIDDEN, NEVER (case-sensitive, whole word). For each match: extract the full sentence, identify scope, assess testability (can you objectively determine compliance?).

### Gap Analysis Framework

Three gap types:
- **Acknowledged**: text says "out of scope" or equivalent
- **Implicit**: topic is mentioned/named but never developed
- **Structural**: a section that would logically complete the argument is absent

### Strength/Weakness Rubric

For each section, score 1-5 on:
- **Clarity**: is the section's purpose immediately clear?
- **Depth**: does it go beyond surface-level treatment?
- **Specificity**: are claims concrete or abstract?
- **Connection**: does it link to other sections or stand isolated?

## B1 — Node B Variation Survey (Darwin)

Applied by N2b. Focus on cataloging variation and assessing fitness.

### Species Classification

Each section of Node B is classified by its dominant content type(s):

| Species | Description | Example Signal |
|---|---|---|
| claim-assertion | States something as true about Node A | "Node A argues that..." |
| evidence-citation | Cites or quotes Node A as evidence | "See §3.2 where..." |
| constraint-derivation | Derives a constraint from Node A's content | "This implies we MUST..." |
| pattern-detection | Identifies a pattern across Node A's sections | "Sections 2-4 all share..." |
| question-generation | Raises a question Node A doesn't answer | "What about the case where...?" |
| summary-restatement | Restates Node A content in different words | (low value unless it adds precision) |
| elaboration-extension | Extends Node A's ideas further | "Building on §2.1, we could..." |
| challenge-refutation | Disagrees with or qualifies Node A | "However, §4.2 overlooks..." |

### Quality Audit Scales

**Specificity** (1-5):
- 1: entirely abstract, no concrete referents ("This is important")
- 3: some concrete elements but mostly general ("The section on methods could be improved by adding more detail")
- 5: precisely specified, falsifiable ("§3.2's claim that X causes Y is unsupported because the only cited study shows correlation, not causation")

**Evidence level**: none / anecdotal / systematic

**Novelty** (relative to Node A): restatement / extension / transformation

**Actionability**: dead-end / informational / actionable

### Corroboration Framework

The corroboration verdict assesses whether Node B's section *bodies* deliver what their *headers* promise:

- Read the body text under each matched header
- For each canonical section, ask: "If I only read this body text, would I know this section serves the canonical purpose?"
- CONFIRMED: ≥80% of matched sections substantiated
- MIXED: 50-79% substantiated
- CEREMONIAL: <50% substantiated — headers are decorative
