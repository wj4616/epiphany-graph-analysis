# De Bono Lateral Thinking Techniques — Operational Reference

## Three Core Techniques for N5 Step 8 Fallback

Applied as N5's lateral fallback when Step 6 shows <3 viable analogy mappings. Use provocation, random-entry, and reversal together to generate ≥5 structurally distinct candidates.

---

## Technique 1 — Provocation (Po)

**Mechanism:** State a deliberately impossible or absurd version of the problem, then work backward to what makes it work or what it implies.

**Instruction:**
1. Prefix statement with "Po:" to mark it as a provocation (not a claim)
2. State an impossible, absurd, or reversed version: "Po: [absurd scenario]"
3. Ask: "What would have to be true for this to work?" and "What principles does this suggest?"
4. Extract the workable insight from the absurd premise

**Application template:**
```
Po: [reverse the goal completely, or make it extreme/absurd]
→ For this to work: [what conditions would enable it?]
→ Candidate insight: [the underlying principle that emerges]
```

**Examples:**
- Problem: "Cars cause traffic jams" → Po: "Cars drive through each other" → Insight: transparent/invisible routing, virtual convoys, phasing
- Problem: "Software has bugs" → Po: "Software writes its own tests" → Insight: self-testing code, property-based testing, fuzzing

---

## Technique 2 — Random Entry

**Mechanism:** Introduce an unrelated random concept and force connections to the problem. Breaks path-dependence by forcing association from an unexpected starting point.

**Instruction:**
1. Select a random noun from a diverse category (object, animal, natural phenomenon, historical event)
2. List 5–8 attributes or associations of that random noun
3. Force each attribute into connection with the problem: "How could [attribute] apply to [problem]?"
4. Select the 1–2 connections that produce the most structurally different candidates

**Random noun categories (use one from each when needed):**
- Natural objects: coral reef, glacier, spider web, river delta, volcanic eruption
- Artifacts: compass, lens, key, sail, pendulum, lever
- Biological: photosynthesis, immune system, migration, metamorphosis, symbiosis
- Abstract: recursion, equilibrium, threshold, gradient, resonance

**Application template:**
```
Random noun: [noun]
Attributes: [list 5-8 properties/behaviors]
Forced connections:
  - [attribute 1] applied to problem → [candidate]
  - [attribute 2] applied to problem → [candidate]
Best candidate: [the most structurally distinct result]
```

---

## Technique 3 — Reversal

**Mechanism:** State the opposite of what you want to achieve, solve that reversed problem, then invert the solution. Often reveals hidden structure.

**Instruction:**
1. State the reversed goal: "Instead of achieving X, how would we maximally prevent/destroy X?"
2. List the methods to achieve the reversal (5–8 methods)
3. Invert each method: "If we did the opposite of [reversal method], what would we get?"
4. Select candidates that are structurally different from prior approaches

**Application template:**
```
Reversed goal: [opposite of the actual goal]
Reversal methods:
  1. [method to destroy/prevent the goal]
  2. ...
Inversions:
  - Opposite of [method 1] → [candidate]
  - Opposite of [method 2] → [candidate]
Best candidates: [top 2 inversions]
```

---

## Output Requirements (N5 Step 8)

Produce ≥5 candidates total across the three techniques. Distribution across techniques should be balanced — do not emit five provocations and zero reversals. Each candidate must include:

- Technique used: [Provocation / Random Entry / Reversal]
- Structural justification: why this candidate is structurally distinct from prior mappings
- Emit under `<fallback_library>` sub-element

Each candidate must NOT be a surface restatement of a prior N5 mapping — check structural distinctness explicitly before including.
