# Section-Tailoring Map — Operational Reference (N3)

Used by N3 SectionTailor when Node B type tag is `genius-current` or `genius-drift`.
Applied to the actual Node B document to produce tailored B1 findings.
**Headline Insight is processed FIRST, before all other sections.**

---

## Section-Tailoring Map Table

| # | Section Name | Section-Specific Focus | Idea-Extraction Strategy | Special Handling |
|---|---|---|---|---|
| 1 | Headline Insight | Primary conclusion + compound claim; structural risks called out as primary concerns | Extract the highest-leverage improvement area first; anchor every later idea against this | **Processed FIRST** — the headline insight or primary conclusion is the main indicator of the primary concern to base enhancement on initially, before moving to all other portions of analysis |
| 2 | Theory Collisions | Claim A vs. Claim B pairs + discriminating condition | One idea per unresolved collision; propose an enhancement that resolves or mitigates | For each collision: analyze Claim A and Claim B, take into account the discriminating condition, decide what it means, and how to create an enhanced solution based on the findings |
| 3 | Discovery vs. Proof | Gap between discovered claim and proof depth | One idea per partial-link; propose evidence-strengthening change to A | Flag unsupported claims as open questions when idea would overreach |
| 4 | Independence-Verified Bridges | High-score bridges (≥1.0) suggest structural insights available to A | One idea per bridge whose target insight exposes an A-level gap | Skip bridges whose "Disanalogy limit" invalidates transfer to A |
| 5 | Alternative Hypotheses | Confidence-ranked hypotheses with falsification conditions | Use ONLY the highest-confidence best-fit hypothesis as an ideation source | Not all aspects of alternative hypotheses are useful — most hypotheses are not correct, only one version will be correct. **Discard all but best-fit.** |
| 6 | Density-Checked Falsification | Counter-examples + failure classes + weakest link | One idea per counter-example that maps to a concrete A-level mitigation | Ideas requiring scope outside A are filtered at N8 |
| 7 | Scope Limits | Applies-to / does-not-extend-to / claims-refused | One idea per "Breaks at" that indicates a missing A-level guardrail | Do not propose scope expansion — guardrails only |
| 8 | Coherence Signals | STRONG-strength convergent findings (multiple independent chains) | One idea per STRONG signal not yet addressed in A | MODERATE / WEAK signals skipped in STANDARD mode |
| 9 | Generalization Checks | Holds-at / breaks-at boundaries | One idea per "Breaks at" boundary that is in scope for A | Asymptotic or by-design-excluded breaks skipped |
| 10 | Open Questions & Next Probes | HIGH-priority probes | One idea per HIGH-priority probe that suggests a testable change to A | LOW-priority probes skipped in STANDARD mode |

---

## Section Order in B1

Process in this order:
1. Headline Insight (FIRST — mandatory)
2. Theory Collisions
3. Discovery vs. Proof
4. Independence-Verified Bridges
5. Alternative Hypotheses
6. Density-Checked Falsification
7. Scope Limits
8. Coherence Signals
9. Generalization Checks
10. Open Questions & Next Probes

---

## Fallback (generic-fallback Node B)

When Node B type tag is `generic-fallback`: E04 gate condition fails → N3 is **skipped entirely**. N4 works from N2's flat findings directly. S2_thin_B signal is raised by N2 → E06 back-edge fires → N6 defixation runs.

Do NOT activate N3 for generic-fallback Node B. The E04 gate condition is the sole mechanism for this; no fallback activation paths.

---

## Drift Handling (genius-drift)

Run the Map on matched sections only. Unmatched sections are scanned generically and added as flat findings in N3's tailored_B1 output, tagged `source_section: "generic-scan"`.

---

## Genius Detection Algorithm (N1)

N1 IntakeDecompose classifies Node B using this algorithm:

**Canonical section headers and accepted drift synonyms:**

| Canonical Header | Accepted Drift Synonyms |
|---|---|
| `## Headline Insight` | "Primary Conclusion", "Main Finding" |
| `## Theory Collisions` | "Collisions", "Conflicts" |
| `## Discovery vs. Proof` | "Discovery/Proof", "Claim vs. Evidence" |
| `## Independence-Verified Bridges` | "Bridges", "Analogies" |
| `## Alternative Hypotheses` | "Hypotheses", "Alt Hypotheses" |
| `## Density-Checked Falsification` | "Falsification", "Counter-examples" |
| `## Scope Limits` | "Scope", "Applies To" |
| `## Coherence Signals` | "Convergence Signals", "Cross-chain Signals" |
| `## Generalization Checks` | "Generalization", "Holds At" |
| `## Open Questions & Next Probes` | "Open Questions", "Probes", "Next Steps" |

**Decision thresholds:**

| Count of canonical-or-synonym headers found | Tag | Behavior in graph |
|---|---|---|
| ≥8 | `genius-current` | E04 gate TRUE → N3 runs full 10-section Map |
| 3–7 | `genius-drift` | E04 gate TRUE → N3 runs Map on matched sections + generic scan |
| <3 | `generic-fallback` | E04 gate FALSE → N3 skipped; S2_thin_B raised by N2 → E06 → N6 |

**Drift tolerance:** The detection heuristic tolerates renamed sections (synonyms above), extra sections (unmatched → generic scan), missing sections (≤3 missing still qualifies as genius-drift), and reordered sections (order not part of the detection rule; only presence).

---

## Special Handling Details

### Headline Insight (Section 1) — Special Handling
- Processed FIRST before any other section
- The Headline Insight shapes the weighting of every downstream finding
- Its source_section tag is propagated to every idea that traces back to it
- Used by N10 for integration precedence: solutions tracing to Headline Insight are applied first

### Theory Collisions (Section 2) — Special Handling
- When Node B names two incompatible positions, extract BOTH as separate findings
- Do NOT synthesize them into one — N8 will generate independent solutions from each
- Never pre-resolve a collision at analysis (N3) time

### Alternative Hypotheses (Section 5) — Special Handling
- Extract ONLY the best-fit hypothesis (the one Node B itself prefers, or the one with strongest supporting evidence if no preference stated)
- Do NOT extract runner-up hypotheses — this prevents idea-pool dilution with low-utility alternatives
- One idea only from this section regardless of how many hypotheses are listed
