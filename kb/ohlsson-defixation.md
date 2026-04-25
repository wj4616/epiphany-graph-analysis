# Ohlsson's De-fixation Mechanisms — Operational Reference

## Background: The Einstellung Effect

Einstellung is "the development of a mechanized state of mind" where a previously successful approach blocks access to better alternatives. It operates through Hebbian strengthening — prior solution paths dominate subsequent reasoning before deliberate reconsideration occurs.

**Override instruction (include at start of each de-fixation pass):**
> "Set aside all previous solution attempts. They are invalid for this pass. Begin from scratch."

This explicit anti-fixation instruction achieves 100% compliance in LLM execution (Luchins' "Don't be blind" finding: 50% human override rate from a single instruction; LLMs comply fully).

## The Three Mechanisms

### Mechanism 1 — Constraint Relaxation

**Definition:** Remove an assumed constraint that was blocking the solution path.

**Procedure:**
1. List all assumptions embedded in the current problem representation (be exhaustive — include implicit assumptions)
2. For each assumption, ask: what solutions open if this assumption is removed?
3. Mark each relaxation by what it enables (number of new solution paths)
4. Select the relaxation that opens the most paths

**Worked example:**  
Problem: "Design a bridge that can span 500m" — assumed constraints include: must use solid structural members, must connect from fixed points. Relaxing "solid members" → suspension cables. Relaxing "fixed endpoints" → floating pontoon bridge.

**Failure guard:** If all constraints are genuinely non-relaxable (physical laws, hard requirements), document why and proceed to Mechanism 2.

### Mechanism 2 — Chunk Decomposition

**Definition:** Break apart a functional unit treated as indivisible; recombine constituent parts independently.

**Procedure:**
1. List all elements of the problem treated as indivisible units (chunks)
2. For each chunk: decompose into constituent sub-elements
3. Ask: which sub-elements can now be recombined independently or in new groupings?
4. Generate new chunk structures from the decomposed parts

**Worked example:**  
Problem: "Improve car engine performance" — chunk: "engine block" treated as monolithic. Decompose: block + pistons + cylinders + cooling channels. Re-chunk: remove cooling channels from block → separate cooling unit → enables new materials for block.

**Failure guard:** If the chunk is truly atomic (cannot be subdivided further), document and proceed to Mechanism 3.

### Mechanism 3 — Re-encoding

**Definition:** Assign different features, roles, or labels to problem elements, changing the representational frame.

**Procedure:**
1. Re-express the problem from the perspective of someone encountering it for the first time
2. Assign new labels to each element (rename without the inherited meaning)
3. Rephrase the goal in the vocabulary of a completely different domain
4. Check: what solutions become visible in the new encoding that were invisible before?

**Representation frames to try (see representation-frames.md):**
- Symbolic → Spatial (turn equations into diagrams)
- Procedural → Declarative (turn "how to do it" into "what is true")
- Analogical → Structural (replace metaphors with structural descriptions)

**Worked example:**  
Problem: "Reduce customer wait time" (encoded as a queue/process problem). Re-encode as a perception problem: "eliminate the subjective experience of waiting" → add entertainment, progress indicators, useful tasks during wait → effective wait unchanged but perceived wait collapses.

## Verification Gate (after all three mechanisms)

**Einstellung-bias check:** For each candidate solution, ask:
- Does this candidate break from the prior solution structure, or is it the same solution in a different surface form?
- If it uses the same core mechanism as the blocked approach, it has not escaped fixation — mark as fixation-residue and exclude.

**Representation-coherence check:**
- Does the new representation remain internally consistent?
- Do the solution candidates make sense within the new frame?

## Output Requirements

For each mechanism, produce:
- ≥3 candidates (relaxation targets / chunk decompositions / re-encodings)
- Ranked by breakthrough-likelihood (most likely to break fixation → first)
- Notation: `[mechanism] [target] → [what opens]`

Select top "breakthrough candidate" across all three mechanisms — the one with highest break probability and most distinct from the prior approach.
