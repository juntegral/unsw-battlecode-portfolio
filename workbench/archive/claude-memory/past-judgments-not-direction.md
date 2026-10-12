---
name: past-judgments-not-direction
description: "User principle for the lineage loops - past verdicts must not steer future research; records are facts only, criteria set independently from the hypothesis alone"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ab529c8b-1bec-404e-b9b6-2b23c283b013
  modified: 2026-09-29T08:14:06.905Z
---

The user holds that past judgments ("promising", "next try X", verdicts) must not steer later research direction. They said preventing that is the reason they use loop engineering at all. Their evaluation of my proposals on 2026-09-29:
- Record format: they deliberately left the failure record (오답노트) free-form, because the optimal format is unknown. Research it before fixing a schema.
- Criteria: self-judged failure was intentional, but they welcome an independent evaluator that sees only the hypothesis content and sets the evaluation criteria itself.
- Enforcement: the read and write obligations must be enforced mechanically, not left to prompt advice.

**Why:** Loop engineering exists so each wave judges from facts, not inherited opinions. A fresh session should be able to judge from recorded facts and numbers.

**How to apply:**
- Anything carried between waves contains facts and numbers (what was tested, which criteria were met or missed and by how much, activation, causes, raw paths), never recommendations.
- Criteria agents get only the hypothesis core.
- Prefer runner or tool gates over doc instructions.
- Flag conflicts, like CURRENT.md "next steps" or the next-wave merge rule in `LOOP.md`, to the user rather than silently keeping or removing them.

Related: [[g3-g4-isolated-runner]]
