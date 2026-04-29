# Vocabulary Rubric — Operational Reference (N5)

## Purpose

Feynman's diagnostic: if you cannot explain something to a five-year-old, you don't understand it. Da Vinci's multi-representation principle: a claim that cannot be expressed in multiple forms is partially understood at best. Applied systematically across 5 levels.

---

## The 5 Levels

### Level 1 — Five-Year-Old

**Target audience:** A child with no domain knowledge whatsoever.
**Permitted:** Everyday words only. No technical terms. Analogies to very familiar things (toys, food, weather, family).
**Forbidden:** Jargon, technical abbreviations, domain-specific concepts that require prior knowledge.

**Instruction:** Rewrite the claim using only the 3000 most common English words. If you must use a technical term, define it immediately in one sentence using everyday words.

**Success test:** Read the output to someone with no background in the domain. They should be able to repeat the central idea.

**Diagnostic value:** Elements that resist Level 1 phrasing are candidates for vague claims — they may have no concrete referent.

---

### Level 2 — Fifteen-Year-Old (Bright Non-Specialist)

**Target audience:** An intelligent person with general education but no specialist training.
**Permitted:** Subject terms that are part of general literacy (evolution, gravity, algorithm, economy). Analogies to historical events, school subjects.
**Forbidden:** Technical jargon specific to the field. Unexplained acronyms. Mathematical notation.

**Instruction:** Write for a curious, intelligent person who is reading outside their expertise.

**Success test:** The claim is clear to anyone who completed secondary education.

---

### Level 3 — Domain Expert

**Target audience:** A practitioner in the same field.
**Permitted:** Full technical vocabulary of the domain. Mathematical notation. Formal definitions.
**Instruction:** Use the field's standard vocabulary precisely. Do not simplify terminology. Do not hedge claims that are technically well-established.

**Success test:** A peer in the field would consider this a clear, technically correct statement.

---

### Level 4 — Mathematician / Logician

**Target audience:** A formal reasoner — abstract structures, axioms, quantifiers.
**Permitted:** Formal logic notation, set theory, function notation, quantifiers (∀, ∃), predicate logic.
**Instruction:** Strip all natural-language hedging. Express the claim as a formal statement with explicit quantifiers, conditions, and scope. Every term must be precisely defined.

**Example transformation:**
- Level 3: "The algorithm runs faster with more memory"
- Level 4: ∀ε > 0, ∃M₀ such that ∀M ≥ M₀: T(n, M) ≤ T(n, M₀) - ε, where T(n, M) is runtime with n inputs and M memory units.

---

### Level 5 — Minimal Symbol

**Target audience:** Communication with the minimum possible vocabulary — a Turing machine specification, a diagram, an equation.
**Instruction:** Express the claim as: an equation, a diagram description, a pseudocode procedure of ≤5 lines, or a single-sentence conditional (IF [condition] THEN [consequence]).
**Goal:** Irreducible expression — nothing can be removed without losing the core claim.

---

## Vagueness Detection

After producing all 5 levels:

**Flag as vague claim** if:
- The claim cannot be stated at Level 4 (formal quantifiers) without introducing terms whose meaning is contested or undefined
- The claim at Level 5 produces either a tautology or an empty statement
- The Level 1 and Level 3 formulations appear to be about different things

**Vague claim output:**
```
[VAGUE] "[exact phrase from the claim]"
Reason: [why it resists formalization]
Possible resolution: [what would need to be specified to make it well-formed?]
```

---

## Constructive Specification (Level 5 into N5 Step 3)

After Level 5:
**Specify the minimal object** — what is the smallest procedure, structure, or test that would demonstrate the claim is true?

Format:
```
Constructive spec: An agent that [minimal action sequence] and produces [observable outcome] constitutes a demonstration of the claim.
```

**Minimal-model check:** Can any element of the constructive spec be removed while leaving the claim demonstrable? If yes, remove it.
