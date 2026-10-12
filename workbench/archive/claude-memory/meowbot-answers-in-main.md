---
name: meowbot-answers-in-main
description: "user rule 10-07: answers to teammates via meowbot are worked in the main session without subagents, to save tokens"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6b21c578-03fd-4530-b02b-c691ebabcf55
  modified: 2026-10-06T18:18:48.801Z
---

For answering Zhe's or QWQ's questions through meowbot, work in the main session and do not spawn subagents. Scope: meowbot answers only; other work still follows [[main-session-master-workbench]].

**Why:** on 10-07 ~03:20 KST the user saw two Opus subagents (one per Zhe question) each reach ~200k context and ~6M cache-read tokens in 11 minutes and was worried about usage. He said he will usually tell teammates to wait for the answer, so parallel speed is not needed. This replaces what he said 15 minutes earlier (one Opus subagent per question in parallel).

The user confirmed the cause: nearly all of the spend was cache reads, i.e. number of calls × context size. So the lever is fewer calls on a smaller context, not just "no subagents".

**How to apply:** answer questions one at a time in main. Batch work into few tool calls (one script instead of 50 small looks). Keep main's context lean, since everything read here is re-read on every later wake-up: put counting/tracing into one script that writes to a file, then read only the summary; cap output with head/cut; never dump replays or long JSON. My own caveat given to the user (not his words): a very deep investigation (dozens of replay traces) may cost more in main than in one tightly scoped subagent — say so and let him choose when that case comes up.

10-07 08:0x KST user, morning review: the proactive overnight work was good, but the first two-subagent run used a lot of tokens. "앞으로는 혹시 내가 그런 작업을 하자고 했을때 미리 재차 확인을 받는 편이 나을것 같아." So before spawning subagents for a job, even one the user proposed, confirm once with a rough size (how many agents, how long, roughly how many tokens) and go only on a yes.
