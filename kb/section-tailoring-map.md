# Section-Tailoring Map

Maps each of the 10 canonical genius-detection sections to its extraction strategy. Used by N3 (SectionTailor, Feynman hat) and referenced by N1 (Genius Detection) for the canonical section list.

## Canonical Section List (10 sections)

These are the 10 canonical sections in descending order of structural importance. N1 matches Node B's headers against these to determine `node_b_type`. N3 extracts content from matched sections using the strategies below.

### 1. Headline Insight

**Header variants**: "Headline Insight", "Key Insight", "Core Finding", "Main Discovery", "Central Thesis"

**Body expectations**: A concise, powerful statement of the single most important thing Node B found. Should be ≤3 sentences, immediately impactful.

**Extraction strategy (N3)**:
- Extract the core claim in ≤2 sentences
- If longer: the insight is buried; extract the most specific sentence
- If missing or generic: flag as "no headline insight — Node B lacks a center"

**AP-12 rule**: Process this section FIRST. The headline insight frames everything else.

### 2. Core Argument

**Header variants**: "Core Argument", "Main Argument", "Central Claim", "Thesis"

**Body expectations**: The argument's logical structure — premises, reasoning steps, conclusion. Should reference specific Node A sections.

**Extraction strategy (N3)**:
- Extract: conclusion (1 sentence) + strongest premise (1 sentence)
- If premise chain is present: preserve it (it's valuable structure)
- If only conclusion with no premises: flag as "assertion, not argument"

### 3. Supporting Evidence

**Header variants**: "Supporting Evidence", "Evidence", "Support", "Empirical Basis", "Data"

**Body expectations**: Evidence cited in support of the core argument. Should reference specific Node A passages, external sources, or logical demonstrations.

**Extraction strategy (N3)**:
- Extract the single strongest piece of evidence with its source reference
- If multiple evidence types (textual + logical + external): extract the best of each type
- If no evidence, only restatement: flag as "unsupported"

### 4. Counter-Arguments

**Header variants**: "Counter-Arguments", "Counterarguments", "Objections", "Challenges", "Alternatives Considered"

**Body expectations**: Arguments against the core argument, honestly presented and then addressed. Shows intellectual honesty.

**Extraction strategy (N3)**:
- Extract: strongest counter-argument (1-2 sentences) + its rebuttal (1-2 sentences)
- If counter-arguments presented but not rebutted: flag as "unresolved counter-arguments"
- If section exists but contains no actual counter-arguments (just "no significant counter-arguments found"): flag as ceremonial

### 5. Implications

**Header variants**: "Implications", "Consequences", "What This Means", "Impact", "Significance"

**Body expectations**: What follows if the core argument is correct. Practical, theoretical, or methodological consequences.

**Extraction strategy (N3)**:
- Extract the most surprising or consequential implication (not the most obvious one)
- If all implications are obvious follow-ons: flag as "low-novelty implications"

### 6. Limitations

**Header variants**: "Limitations", "Caveats", "Boundary Conditions", "Scope Limits", "Constraints"

**Body expectations**: Honest accounting of what the analysis does NOT cover, where it might break, what assumptions it depends on.

**Extraction strategy (N3)**:
- Extract every stated limitation (they are all valuable for downstream nodes)
- If section is perfunctory ("this analysis has limitations including scope"): flag as ceremonial

### 7. Alternative Views

**Header variants**: "Alternative Views", "Alternative Interpretations", "Other Perspectives", "Different Readings", "Competing Frameworks"

**Body expectations**: Ways Node A could be interpreted differently that are NOT counter-arguments to Node B's position.

**Extraction strategy (N3)**:
- Extract the most viable alternative (the one that a reasonable person might prefer)
- If all alternatives are straw men: flag as "weak alternatives"

### 8. Synthesis

**Header variants**: "Synthesis", "Integration", "Putting It Together", "Holistic View", "Unified Picture"

**Body expectations**: How the pieces fit together. Cross-section connections, emergent themes, the big picture.

**Extraction strategy (N3)**:
- Extract the integration insight (how pieces connect)
- If section is summary, not synthesis (restates pieces without connecting them): flag

### 9. Action Items

**Header variants**: "Action Items", "Recommendations", "Next Steps", "What To Do", "Applications", "Practical Steps"

**Body expectations**: Concrete, actionable recommendations derived from the analysis.

**Extraction strategy (N3)**:
- Extract every action item that is specific enough to execute
- Score actionability: concrete ("Add §2.3 example about...") vs. vague ("Improve the document")
- If no concrete items: flag as "no actionable output"

### 10. Open Questions & Next Probes

**Header variants**: "Open Questions", "Next Probes", "Future Work", "Unresolved", "Further Investigation", "Remaining Questions"

**Body expectations**: What Node B couldn't resolve. Honest unknowns. Specific questions for further investigation.

**Extraction strategy (N3)**:
- Extract the most provocative open question (the one that, if answered, would most change the analysis)
- If all questions are rhetorical or unanswerably broad: flag as "ceremonial"
