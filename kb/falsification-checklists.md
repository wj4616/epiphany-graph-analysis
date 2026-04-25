# Falsification Checklists — Operational Reference (N7)

## Three Complementary Checklists

Apply all three in N7 Steps 3–5. Each tests a different dimension of falsifiability.

---

## Checklist 1 — Extreme Scenario Construction (Einstein)

Test the primary conclusion (from N1 + N5) at boundary regimes. A claim that only holds in the middle of its parameter range is weaker than one that holds at the extremes.

**For each relevant parameter, construct the extreme scenario:**

| Regime | Question |
|--------|----------|
| Parameter → 0 | What happens as [key quantity] approaches zero? Does the claim still hold? |
| Parameter → ∞ | What happens as [key quantity] grows without bound? |
| Population → 1 | What if only one agent/instance exists? |
| Population → ∞ | What if the number of agents/instances is uncountably large? |
| Time → 0 | What happens in the immediate instant? |
| Time → ∞ | What happens in the long run (asymptotic behavior)? |
| Adversarial scenario | What if an agent with perfect information is actively optimizing against the claim? |
| Random/noisy scenario | What if all inputs are uniformly random noise? |

**Record for each scenario:**
- Claim behavior: [still holds / fails / degenerate / undefined]
- If fails: what does the failure reveal about the claim's scope? → feed to V6

---

## Checklist 2 — Millikan Test (Feynman Differential-Effort Detection)

Feynman's critique of cargo-cult science, derived from Millikan's oil-drop experiment: Millikan got a value for electron charge that was slightly off. Later experimenters kept getting values "between Millikan and the truth" — each one adjusting slightly toward Millikan's value because of experimenter bias. The problem: when you get a result that disagrees with what you expect, you look harder for error than when you get a result that agrees.

**Test for this bias in the reasoning:**

For each alternative hypothesis or rival explanation:
1. **Effort inventory:** How hard did the reasoning work to find evidence against this hypothesis vs. how hard it worked to find evidence for the primary conclusion?
2. **Selection audit:** Are the examples, instances, or evidence patterns that support the primary conclusion genuinely representative, or were they selectively chosen?
3. **Difficulty asymmetry flag:** Does refuting a rival hypothesis seem to require much less work than refuting the primary conclusion? If so, flag: the scoring may be rigged.

**Format:**
```
[MILLIKAN] Hypothesis [X]: 
  Effort to refute: [low / medium / high]
  Effort to support primary: [low / medium / high]
  Asymmetry: [yes / no]
  If asymmetric: [what additional counter-evidence should be sought?]
```

---

## Checklist 3 — Darwin's Golden Rule (Active Disconfirming-Evidence Search)

Darwin kept a special notebook for observations that contradicted his theory of natural selection. He wrote them down immediately because he knew human memory preferentially forgets disconfirming evidence within 24–48 hours.

**Systematic disconfirming-evidence search:**

For the primary conclusion, actively search for:

1. **Known counter-examples:** Are there documented cases where the primary conclusion fails? State them explicitly. Do not skip this step because you cannot think of any — if none come to mind, that is itself a suspicious finding.

2. **Classes of problem where this approach fails:** What problem structures are NOT addressed by the conclusion?

3. **Theoretical objections:** What would someone who disagrees with the conclusion cite as their strongest evidence?

4. **Literature / known results that cut against:** What established results make the conclusion harder to believe?

5. **Mechanism gaps:** What part of the causal mechanism from premises to conclusion is least well-supported?

**Density report:**
```
Disconfirming evidence found: [N items]
Counter-examples: [list or "none identified — flag as suspicious"]
Failure classes: [list]
Strongest objection: [one sentence]
Weakest link in mechanism: [one sentence]
Density assessment: [high (≥5 items) / medium (3–4) / low (<3)]
```

**Low density flag:** If fewer than 3 disconfirming items were found, this does not mean the conclusion is strong — it means the search was not aggressive enough. State: `[LOW-DENSITY WARNING] Fewer than 3 disconfirming items found. Re-examine: have any known counter-examples been dismissed too quickly?`

---

## Cargo-Cult Scan

Before writing N7 output, check the reasoning for cargo-cult patterns — steps that look like falsification but do not actually challenge the conclusion:

| Cargo-cult pattern | Real falsification |
|--------------------|-------------------|
| "One could imagine a case where this fails..." (without specifying the case) | "The case [X] specifically contradicts this because [mechanism]" |
| "The theory is not universal..." (without stating where it fails) | "It fails when [condition] because [reason]" |
| "Further research is needed..." (as a falsification move) | "The gap [G] is specifically what would change the conclusion if resolved" |
| "This has limitations..." (without specifying them) | "Limitation: [X], which means the conclusion does not apply to [specific class of problem]" |

Flag any cargo-cult pattern found. Replace with genuine falsification or mark as `[UNFALSIFIED]`.
