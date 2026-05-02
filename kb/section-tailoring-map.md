# Section-Tailoring Map

Maps each of the 10 canonical genius-minds sections to its extraction strategy. Used by N3 (SectionTailor, Feynman hat) and referenced by N1 (Genius Detection) for the canonical section list. The taxonomy is the spec's Appendix C list — it must stay in lockstep with `modules/N1-intake.md` Step 4.

## Canonical Section List (10 sections)

These are the 10 canonical sections in descending order of structural importance. N1 matches Node B's headers against these to determine `node_b_type`. N3 extracts content from matched sections using the strategies below.

### 1. Headline Insight

**Header variants**: "Headline Insight", "Primary Insight", "Lead Insight", "Top-Line Insight", "Bottom Line", "Core Insight"

**Body expectations**: A concise, powerful statement of the single most important thing Node B found. Should be ≤3 sentences, immediately impactful.

**Extraction strategy (N3)**:
- Extract the core claim in ≤2 sentences
- If longer: the insight is buried; extract the most specific sentence
- If missing or generic: flag as "no headline insight — Node B lacks a center"

**AP-12 rule**: Process this section FIRST. The headline insight frames everything else.

### 2. Theory Collisions

**Header variants**: "Theory Collisions", "Theoretical Conflicts", "Conflicting Claims", "Theory Conflicts", "Claim Conflicts"

**Body expectations**: Cases where two theoretical frames make incompatible predictions about Node A. Should name both frames and the predicted divergence.

**Extraction strategy (N3)**:
- Extract each named frame pair + the divergence point as a tuple `(frame_a, frame_b, divergence)`
- If a "collision" is presented but only one frame is described: flag as "asymmetric collision — only one frame characterized"
- If divergence is rhetorical only (no operational difference): flag as "ceremonial collision"

### 3. Discovery vs. Proof

**Header variants**: "Discovery vs Proof", "Discovery–Proof Gap", "Claim vs Evidence", "Discovery and Proof"

**Body expectations**: Honest split between what Node B *discovered* (a claim it generated) versus what it *proved* (a claim it supported with independent evidence). The gap is informative.

**Extraction strategy (N3)**:
- Build two lists: `discovered` (claims) and `proven` (claims with attached independent evidence)
- For each `discovered`-only claim: note "discovery-only — no independent proof yet" — these are candidates for N6 defixation if they're load-bearing
- If everything is in one column: flag as "discovery-without-proof" or "proof-without-discovery" depending on which side is empty

### 4. Independence-Verified Bridges

**Header variants**: "Independence Bridges", "Verified Bridges", "Cross-Domain Bridges", "Bridges (Verified)"

**Body expectations**: Connections between Node A and external domains where the bridge has been validated against an independent source — not assumed by analogy.

**Extraction strategy (N3)**:
- Extract each bridge as `(node_a_anchor, external_domain, verification_source)`
- If the verification source is the same author / same paper as the bridge claim: demote to "self-verified" and flag — these are weaker
- Bridges with verified independence are the strongest candidates for N5 lateral ideation seeds

### 5. Alternative Hypotheses

**Header variants**: "Alt Hypotheses", "Alternative Theories", "Counter-Hypotheses", "Competing Hypotheses"

**Body expectations**: Hypotheses other than Node B's primary one that explain the same data. The strongest alternative should be characterized fairly.

**Extraction strategy (N3)**:
- Extract the **best-fit** alternative (per AP-10: do NOT treat alternative hypotheses as a multiple-competing-ideas list — only the strongest)
- Record the operational difference between primary and best-fit alternative
- If alternatives are presented as straw men (only weakest is named): flag as "alternatives-as-strawmen"

### 6. Density-Checked Falsification

**Header variants**: "Falsification (Density-Checked)", "Density Falsification", "Counter-Examples", "Falsification Checks"

**Body expectations**: Specific falsifying conditions plus an honest assessment of how often those conditions occur in practice (the density check distinguishes "could-fail-in-principle" from "actually-fails-here").

**Extraction strategy (N3)**:
- Extract each falsification condition + its density assessment as `(condition, density: low|medium|high, evidence)`
- Density-low falsifications are advisories (the condition rarely occurs); density-high falsifications are blockers (the condition is common)
- If a condition is listed without density: flag as "undensitied falsification — assess before relying"

### 7. Scope Limits

**Header variants**: "Scope Boundaries", "Applies-to / Does-not-extend-to", "Boundaries", "Domain Limits"

**Body expectations**: Where the analysis applies and — crucially — where it does NOT extend. The "does-not-extend-to" half is what most documents skip.

**Extraction strategy (N3)**:
- Extract two lists: `applies_to` and `does_not_extend_to`
- If `does_not_extend_to` is empty or perfunctory: flag as "asymmetric scope — limits unstated"
- The strongest scope limits cite a specific kind of input that breaks the analysis

### 8. Coherence Signals

**Header variants**: "Convergent Signals", "Coherence Indicators", "Signal Convergence", "STRONG/MODERATE/WEAK Signals"

**Body expectations**: Independent indicators that converge on the same conclusion. Strength rating (STRONG/MODERATE/WEAK) per signal.

**Extraction strategy (N3)**:
- Extract each signal as `(indicator, source, strength: STRONG|MODERATE|WEAK)`
- Coherence is real only when sources are independent — flag any cluster of signals from a single source as "single-source coherence"
- STRONG signals from independent sources are the most actionable for N8 synthesis

### 9. Generalization Checks

**Header variants**: "Generalization", "Holds-at / Breaks-at", "Generality Checks", "Universality Tests"

**Body expectations**: Tests of how far the analysis generalizes — does it hold at scale? at edge cases? in adjacent domains?

**Extraction strategy (N3)**:
- Extract each test as `(test_dimension, holds_at, breaks_at)`
- If only "holds-at" cases are listed (no breaking points): flag as "untested generalization — breaking points not characterized"
- "Breaks-at" findings are often the most useful — they sharpen Node A's actual scope

### 10. Open Questions & Next Probes

**Header variants**: "Open Questions", "Next Probes", "Future Work", "Unresolved", "Further Investigation", "Questions & Probes", "Probes & Questions"

**Body expectations**: What Node B couldn't resolve. Honest unknowns. Specific questions for further investigation, ideally with a method for answering each.

**Extraction strategy (N3)**:
- Extract the most provocative open question (the one that, if answered, would most change the analysis)
- For each question, capture the suggested probe/method if any
- If all questions are rhetorical or unanswerably broad: flag as "ceremonial"
