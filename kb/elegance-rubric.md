# Elegance Rubric — Operational Reference (N3, N7)

## Three Components of Elegance

Elegance score = Simplicity + Symmetry + Depth (max 3.0)

### Component 1 — Simplicity

**Definition:** The minimum number of primitives needed to express the insight. Simpler expressions of the same content score higher.

**Scoring:**
- 1.0 — Irreducible: cannot remove any element without losing the core claim
- 0.7 — Near-irreducible: 1–2 elements could be compressed but loss would be minor
- 0.4 — Moderate redundancy: multiple framings of the same idea; main content present but padded
- 0.1 — High redundancy: significant scaffolding obscures the core; restates premise without adding structure

**Application:** After writing the candidate insight, attempt to halve the word count. If the content is unchanged, the original was not irreducible → score 0.7 or lower.

### Component 2 — Symmetry

**Definition:** The presence of structural patterns that recur across different contexts, scales, or domains. Symmetry signals that a deeper invariant is being exposed.

**Scoring:**
- 1.0 — Cross-domain recurrence: the same structural relationship appears independently in ≥3 distinct contexts (mathematics, physics, biology, social systems, etc.)
- 0.7 — Dual-domain recurrence: the pattern appears in ≥2 independent domains
- 0.4 — Single-domain pattern: consistent within one domain but no known cross-domain analog
- 0.1 — Isolated: no recognizable structural pattern; may still be true but is a one-off observation

**Application:** For each candidate, ask: "Does this structural relationship appear anywhere else in a different domain?" If yes, identify the domain and the analog explicitly.

### Component 3 — Depth

**Definition:** The ratio of explanatory yield to expressive cost. A deep insight generates many downstream implications from a compact premise. Depth is the inverse of triviality.

**Scoring:**
- 1.0 — Generates ≥5 independently verifiable implications; each implication reveals previously invisible structure
- 0.7 — Generates 3–4 testable implications; at least one opens a new problem category
- 0.4 — Generates 1–2 implications; confirms what is already broadly suspected
- 0.1 — Generates no new implications; tautological or circular

**Application:** After writing a candidate, generate all immediate consequences. Count those that are independently testable and not already known. Score accordingly.

## Composite Scoring

```
Elegance = Simplicity + Symmetry + Depth
Range: 0.3 (tautological, isolated, redundant) to 3.0 (irreducible, cross-domain, generative)
```

**Score bands:**
- 2.5–3.0: **HIGH elegance** — structural completeness gate met; prefer in selection
- 1.5–2.4: **MODERATE elegance** — useful; include in ranked output
- 0.8–1.4: **LOW elegance** — include only if no higher-scoring alternatives; flag
- <0.8: **Exclude** — not load-bearing; document as "low elegance, excluded"

## Tiebreaker Rules

When two candidates score within 0.1 of each other:
1. Prefer higher Symmetry score (cross-domain recurrence is more robust than within-domain pattern)
2. If Symmetry tied: prefer higher Depth score (more generative > more precise)
3. If Depth tied: prefer higher Simplicity score (parsimony is the final tiebreaker)

## Usage in N3 (Node Ranking)

After spreading activation:
- Score each convergent node on Elegance
- Combined ranking score: `a(node) × Elegance_score`
- Select top 3–5 by combined score for illumination

## Usage in N7 (Structural Coherence Weighting)

- Apply elegance scoring to the primary conclusion
- Unexpected symmetries (cross-domain recurrence) strengthen the conclusion's claim
- Transformational conclusions (Boden Type 3) require narrower V6 scope unless symmetry score ≥ 0.7
