# Oppositional Drafting Axes

Referenced by N8 (SolutionEngineer) for the hybrid protocol. Defines 7 axes (A0-A6), each with two poles. For each accepted idea, N8 picks the most applicable axis, drafts a solution from each pole independently, then compares and refines.

## Axis Selection Algorithm

```
function pick_axis(idea, target_section, node_a_text):
    if idea.touches_phrasing_or_style:           return A1
    elif idea.scope_is_ambiguous:                return A2
    elif idea.creates_constraint_tension:        return A3
    elif idea.is_principle_vs_procedure_choice:  return A4
    elif idea.has_uncertain_payoff:              return A5
    elif idea.target_section_format_ambiguous:   return A6
    else:                                        return A0
```

## The 7 Axes

### A0 — Structural Scope (Default Fallback)

Applied when no more specific axis fits. The most general opposition.

| Pole 1: Minimal-change | Pole 2: Ambitious-restructure |
|---|---|
| Make the smallest possible change that addresses the idea. Preserve existing structure, phrasing, and flow. The reader should barely notice the edit. | Restructure or rewrite the target section to fully accommodate the idea. Change organization, add subsections, reorder content. The section should feel transformed. |

**When**: No clear domain pull from other axes.

**Drafting guidance**:
- Pole 1: "What is the minimal edit — a sentence, a qualifier, a connection — that captures this idea?"
- Pole 2: "If this section were rewritten with this idea as a central concern, what would it look like?"

### A1 — Voice & Style

Applied when the idea touches phrasing, style, tone, or voice choices.

| Pole 1: Preserve-original-voice | Pole 2: Rewrite-for-clarity |
|---|---|
| Match the existing voice, vocabulary level, sentence rhythm, and tone. Enhancements should feel like they were written by the same author on a better day. | Prioritize clarity over voice fidelity. If the original voice obscures meaning, clarity wins. Shorter sentences, plainer words, more direct structure. |

**When**: Idea touches phrasing or style.

**Drafting guidance**:
- Pole 1: Read the surrounding text. Match its rhythm, vocabulary tier, and sentence length distribution.
- Pole 2: "How would Feynman say this? What is the clearest possible version?"

### A2 — Scope

Applied when the idea's scope is ambiguous (could be narrow or broad).

| Pole 1: Conservative-scope | Pole 2: Expansive-scope |
|---|---|
| Apply the idea only to the specific section it targets. Do not generalize or extend to other sections. Local enhancement only. | Apply the idea wherever it fits. If §3.2 benefits from this idea, check whether §4.1 and §5.3 do too. Cross-section application. |

**When**: Idea scope is ambiguous.

**Drafting guidance**:
- Pole 1: "This applies to §N.M only. Do not look beyond this section."
- Pole 2: "Where else in Node A would this idea improve things? Apply it everywhere it fits."

### A3 — Constraint Relationship

Applied when the idea creates tension with existing constraints.

| Pole 1: Strict-constraint-preservation | Pole 2: Constraint-relaxation |
|---|---|
| The solution must not violate any existing constraint from Node A. If the idea conflicts with a MUST/MUST NOT, the constraint wins — modify the idea to comply. | If the idea is powerful enough, relax the constraint. Document the tension and the decision. The constraint may have been overly strict for the original Node A context. |

**When**: Idea creates constraint tension.

**Drafting guidance**:
- Pole 1: Check every constraint from N1's audit. The solution must pass all of them.
- Pole 2: "Is this constraint load-bearing? What happens if we relax it? Does the resulting freedom justify the relaxation?"

### A4 — Abstraction Level

Applied when the idea could be deployed as a principle or as a specific recipe.

| Pole 1: Abstract-principle | Pole 2: Specific-recipe |
|---|---|
| State the enhancement as a general principle (why it works, when it applies). Let N10 decide the concrete form. | Provide step-by-step instructions for N10: exactly what text to add, where, in what format. No ambiguity. |

**When**: Idea is principle-vs-procedure choice.

**Drafting guidance**:
- Pole 1: "What is the principle behind this idea? When should N10 apply it?"
- Pole 2: "What exact text should N10 insert at line N of §N.M?"

### A5 — Risk Posture

Applied when the idea has uncertain payoff.

| Pole 1: Risk-averse | Pole 2: Risk-seeking |
|---|---|
| Hedge the enhancement. Add qualifiers, caveats, "may" instead of "will". Make it easy for the reader to dismiss if they disagree. Make it easy for N10 to drop if it doesn't fit. | Commit fully. The idea might be wrong, but if it's right it should land hard. No hedging. Bold claims, strong framing. |

**When**: Idea has uncertain payoff.

**Drafting guidance**:
- Pole 1: "Assume this idea might be wrong. How can it improve the draft while being easy to ignore if incorrect?"
- Pole 2: "Assume this idea is correct. What is the boldest, most impactful version?"

### A6 — Format

Applied when the target section's format is ambiguous.

| Pole 1: Inline-integration | Pole 2: Sidebar-integration |
|---|---|
| Blend the enhancement into the main text flow. It becomes part of the paragraph structure. Readers see it as continuous text. | Separate the enhancement as a callout, footnote, example box, or sidebar. Readers can engage with it or skip it. Keeps main flow clean. |

**When**: Idea's target section format is ambiguous.

**Drafting guidance**:
- Pole 1: "Write the enhancement as part of the paragraph — same voice, same flow."
- Pole 2: "Write the enhancement as a discrete block — >quote, _example box, or (footnote)."

## Pattern α (Draft B Independence)

When drafting Pole 2 (Draft B), N8 MUST apply Pattern α to ensure independence:

> *"Forget Draft A entirely. You are drafting fresh from the idea description and pole-2 framing only. Do not echo, contrast, or reference Draft A."*

Without Pattern α, Draft B becomes a reaction to Draft A rather than an independent alternative — collapsing the opposition into a binary choice between A and not-A rather than a genuine exploration of the axis.

## Why Two Drafts?

Two independent drafts from opposite poles force the solution to earn its place. A single draft has no competition; it can be mediocre and still get accepted. Two drafts, compared, mean the winner was tested against a concrete alternative — not just against "could this be better?" but against "here is another version; which one actually improves the text more?"

The loser's strengths feed the critique step, so even the rejected draft contributes to the final solution's quality.
