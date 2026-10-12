---
name: dev1-not-informative
description: Zhe 10-06 — dev test 1 has become too strong to tell our bots apart; online tests should lean on normal-team opponents
metadata:
  node_type: memory
  type: project
  originSessionId: bf4f8138-7733-48a7-8829-36025e05cdcd
  modified: 2026-10-06T07:44:58.861Z
---

Zhe in #meow, 2026-10-06 16:40 KST, right after the #43 smoke result against dev1 (1/15 for both main and main + idle-exit): "dev1 is lowkey too op for our tests now, so its not really giving us any useful info anymore". dev test 1 was rated about 2417 that day against our 1850~1880.

**Why:** when almost every game is lost, wins and scores stop separating two of our builds; only behaviour counts from the replays still say something.

**How to apply:** this is Zhe's read, not a rule the user set. For online tests asked for after this, default to normal-team opponents (test4, WeHaveQuizzes or similar-rated teams) and add dev1 only when someone asks for it or the question is about our queen being hunted. Say which opponents were used. Related: [[same-hour-baseline]], [[zhe-intuition]], [[online-feedback-mechanism-check]].
