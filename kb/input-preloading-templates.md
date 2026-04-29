# Input Preloading Templates

Patterns for constructing spawn agent prompts with precisely the right context. Used by the orchestrator (SKILL.md) when dispatching spawn nodes (N2a, N2b, N5, N7, N10).

## Template Structure

Every spawn dispatch prompt follows this structure:

```
1. ROLE ASSIGNMENT (hat + persona framing) — 2-3 sentences
2. TASK DESCRIPTION (what to produce) — 3-5 sentences  
3. INPUT INVENTORY (exactly what files/signals to read) — bullet list
4. PROTOCOL (step-by-step instructions) — numbered steps
5. OUTPUT SPECIFICATION (format, sections, frontmatter) — structured
6. SIGNAL OUTPUT (what to write to SIGNAL_STATE) — YAML block
7. FAILURE MODES (what to do when things go wrong) — bullet list
```

## Context Budgeting

Per-node context budgets from graph.json:

| Node | Budget (lines) | Preload Strategy |
|---|---|---|
| N2a | 1500 | Full intake_digest + Node A path; do NOT inline Node A text (read from disk) |
| N2b | 1500 | Full intake_digest + Node B path; do NOT inline Node B text |
| N5 | 1200 | Full xref_map + complexity bucket; do NOT inline KB files (read from disk) |
| N7 | 1500 | Full accepted_ideas_digest + breakthrough_digest (if available); KB on disk |
| N10 | 2000 | Full solutions_digest + Node A path; expansion_digest only if pass=2 |

## Input Inlining Rules

**Inline** (include in prompt body):
- SIGNAL_STATE entries (always — they are small structured YAML)
- Short KB excerpts (<50 lines) that are essential to the protocol
- Routing decisions and signal flags

**Reference** (by path, agent reads from disk):
- Full Node A / Node B text (may be thousands of lines)
- Full KB files (agent reads what it needs)
- Other nodes' stage files (too large; agent reads relevant sections)

## Hat → Prompt Translation

When a node specifies a hat, the spawn prompt opens with the persona framing:

| Hat | Opening Framing |
|---|---|
| Einstein/Feynman | "You are adopting dual framing: Einstein (holistic pattern recognition) and Feynman (relentless clarity). See the whole, then reduce it to its simplest, most powerful form." |
| Tesla (measurement) | "You are now adopting the Tesla (measurement) persona. Focus on quantifiable structure, key claims, apparent gaps. Measure what is there — do not speculate beyond the text." |
| Darwin (variation-survey) | "You are now adopting the Darwin (variation-survey) persona. Survey the variation in claims across the text. Catalog what species of analysis are present. Assess which are well-adapted and which are rudimentary." |
| de Bono | "You are now adopting the de Bono (lateral thinking) persona. Your job is not to critique or filter — it is to GENERATE. Think sideways. Move across domains. Provoke new connections." |
| Boden | "You are now adopting the Boden (creativity theory) persona. Assess whether each idea represents a genuine transformation of the conceptual space — novel, valuable, and non-obvious." |
| Popper + Millikan | "You are adopting a dual hat: Popper (falsification) + Millikan (experimental rigor). Your stance is adversarial in service of quality. For each idea: if it were wrong, how would we know?" |
| Feynman + Boden(synthesizer) | "Dual hat: Feynman (clarity, simplicity — 'what is the simplest version that is still complete?') + Boden(synthesizer) (creative integration — 'how do these enhancements combine into something greater than their sum?')" |

## Session Directory Convention

All spawn agents write to `{session_dir}/stages/`. The session directory path is provided in the dispatch prompt as `SESSION_DIR=<path>`. No agent writes outside this directory (HG-4).
