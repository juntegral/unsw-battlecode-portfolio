---
name: loop-first
description: user rule 10-03: run experiments almost only as loops (board queue + runner), not long-lived Opus agents
metadata:
  type: feedback
---
From 10-03 on, work runs almost entirely in loop form: ideas go on the board (loop:ready), and a runner script plays the games while Claude is called only for short steps (implement, analyse, report).

**Why:** the two long-lived Opus agents (bigmap-state, zhe-queen) burned the weekly budget to 95% while mostly waiting on CPU-bound batches, and three concurrent batches overloaded the Mac. Board ideas like #10/#11/#14 are loop material.

**How to apply:** do not spawn standing agents for experiments; queue the card, let the runner wait on batches without tokens, and run one batch at a time. See [[claude-usage-budget]], [[overnight-loop-1003]].
