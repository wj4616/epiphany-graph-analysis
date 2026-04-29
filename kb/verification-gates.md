# Verification Gates V1–V7 — Operational Reference (N7)

## Usage

N7 runs this battery in order after constructing the primary conclusion. Each gate is applied as an explicit separate check. All gates must be applied; none may be skipped. Pass/fail/partial recorded for each.

---

## V1 — Logic Gate

**Purpose:** Verify every inferential link in the primary conclusion is sound.

**Check protocol:**
1. List every inferential step from N1 primitives to the primary conclusion
2. For each step: state the inference form (modus ponens, analogy, induction, etc.)
3. For each step: ask — "Does the conclusion follow from the premises by a valid inference rule?"
4. Flag any step where the inference form is not clearly valid

**Pass condition:** All inferential links are explicitly stated and valid.
**Partial:** ≥1 step requires an additional assumption not in N1 — state the assumption explicitly.
**Fail:** ≥1 step cannot be reconstructed as a valid inference — the conclusion is not supported at that link.

**Output:** `V1 Logic: [PASS / PARTIAL / FAIL] — [brief justification, list of weak links if any]`

---

## V2 — Cargo-Cult Detection

**Purpose:** Identify any step that looks like rigorous reasoning without being rigorous.

**Check protocol (scan for each pattern):**

| Pattern | Flag |
|---------|------|
| Assertion with jargon-heavy framing but no concrete referent | [CC-JARGON] |
| Statistical claim without sample size or methodology | [CC-STAT] |
| Appeal to authority without reproducible evidence | [CC-AUTH] |
| "Studies show..." without naming which studies | [CC-ANON] |
| Analogy used as proof rather than illustration | [CC-ANALOGY] |
| Threshold precision ("exactly 42%") without calibration | [CC-PRECISION] |
| Correlation stated as causation without mechanism | [CC-CAUSAL] |

**Pass condition:** No cargo-cult patterns found.
**Fail:** ≥1 pattern found → list each occurrence and why it does not constitute genuine evidence.

**Output:** `V2 Cargo-Cult: [PASS / FAIL] — [list of patterns found, or "none detected"]`

---

## V3 — Symmetric Scrutiny

**Purpose:** Verify the same degree of skepticism was applied to the primary conclusion as to its rivals.

**Check protocol:**
1. For the primary conclusion: list the challenges and objections that were raised
2. For each rival hypothesis in N6: list the challenges and objections that were raised
3. Compare: is the burden of proof equal? Or was the primary conclusion held to a lower standard?

**Pass condition:** The primary conclusion faces at least as many serious objections as the best rival.
**Fail:** Rival hypotheses were dismissed with less evidence/reasoning than the primary conclusion required for acceptance.

**Output:** `V3 Symmetric Scrutiny: [PASS / FAIL] — [justification]`

---

## V4 — Completeness

**Purpose:** Verify that every stage output contributed substantively to the primary conclusion. Identifies thin stages for possible retry.

**Check protocol:**
1. For each stage that ran: what specific content from that stage appears in the primary conclusion or evidence base?
2. Flag any stage whose output is not cited or used anywhere in the N7 conclusion or verification process

**Pass condition:** Every ran stage is cited at least once in substantive conclusion-building.
**Thin stage signal:** A stage returned `complete` status but its output does not appear in the conclusion — flag for retry (see SKILL.md STEP 3c post-execution checks).
**Output:** `V4 Completeness: [PASS] or [THIN: N[N]] — [explanation]`

**Note:** V4 is the only gate that can trigger an external action (back-edge retry via SKILL.md STEP 3c). All other gates are final within N7.

---

## V5 — Constructive Verification

**Purpose:** Verify the primary conclusion is constructive — you could build, observe, or test the thing it claims.

**Check protocol:**
1. State the minimal procedure or object that would demonstrate the conclusion is true
2. Is this demonstration possible in principle? (Does not need to be currently feasible — but must not be logically impossible)
3. Is anything eliminable from the constructive spec without losing the demonstration? (minimality check)

**Pass condition:** Constructive spec is complete and minimal.
**Fail:** The conclusion cannot be demonstrated even in principle, or the demonstration presupposes something not established.

**Output:** `V5 Constructive: [PASS / FAIL] — constructive spec: [one sentence description]`

---

## V6 — Scope / Domain-Boundary-Refusal

**Purpose:** Write the definitive scope statement. Refusal of out-of-scope claims is a feature, not a limitation.

**CRITICAL:** Write `stages/N7-v6-scope.txt` with exactly these 3 labels and fill each in:

```
**Applies to:** [what specific classes of problem, conditions, domains the conclusion holds for — be specific, not "many cases"]
**Does not extend to:** [what the conclusion explicitly does NOT cover — enumerate, don't vague-wave]
**Claims refused:** [any inference that was requested but not supported — or "(none)" if no such inference was attempted]
```

**Verbatim format requirements:**
- Labels must be EXACTLY as above (bold, colon)
- Each entry must be substantive — no "TBD", no "see conclusion"
- "Claims refused: (none)" is a valid and complete entry when nothing was refused

**Scope narrowing by Boden type:**
- Combinatorial: moderate narrowing — list the combined domain only
- Exploratory: name the conceptual space and its defining rules
- Transformational: aggressive narrowing — name the new space, explicitly exclude the old space

**Output:** Write file `stages/N7-v6-scope.txt`. Also include V6 entry in N7 verification report:
`V6 Scope: [PASS] — wrote stages/N7-v6-scope.txt`

---

## V7 — Representational Coherence (v1.1.0)

**Purpose:** Compare the representation of the primary conclusion to the representation of the original input. Document any shift.

**Check protocol:**
1. Read the original input from `stages/00-processed-input.md` — what representational frame is it in? (see representation-frames.md)
2. Read the primary conclusion — what representational frame is it in?
3. Are they the same frame?

**If same frame:**
Output: `V7 Representational: No shift — conclusion is in the same frame as input [frame name].`

**If different frame (shifted):**
1. Name the shift: [source frame] → [target frame]
2. Note that the conclusion is a **re-representation**, not a direct answer to the original form of the question
3. Feed this information to V6: the scope statement must reflect the frame shift (the conclusion applies within the new frame)
4. If applicable, add to N3.1 activation record or Representational Signals section in N9

Output: `V7 Representational: Shift detected — [source frame] → [target frame]. Conclusion is a re-representation. V6 scope narrowed to [new frame].`

**Frame names** (from representation-frames.md): symbolic, spatial, procedural, declarative, analogical, narrative

---

## V1–V7 Summary Block (required at end of N7 output)

```
## Verification Report

V1 Logic: [PASS / PARTIAL / FAIL] — [notes]
V2 Cargo-Cult: [PASS / FAIL] — [notes]
V3 Symmetric Scrutiny: [PASS / FAIL] — [notes]
V4 Completeness: [PASS] or [THIN: stages] — [notes]
V5 Constructive: [PASS / FAIL] — constructive spec: [one sentence]
V6 Scope: [PASS] — wrote stages/N7-v6-scope.txt
V7 Representational: [No shift / Shift: A→B] — [notes]

Overall: [N PASS] / [M PARTIAL/FAIL] out of 7 gates
```
