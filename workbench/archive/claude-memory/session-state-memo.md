---
name: session-state-memo
description: "user-agreed 10-07: the command-post session keeps unsw-swarm/docs/SESSION-STATE.md; update it before every /compact or handover, re-read it right after"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6b21c578-03fd-4530-b02b-c691ebabcf55
  modified: 2026-10-07T00:20:00.943Z
---

The command-post session keeps a short state memo at `unsw-swarm/docs/SESSION-STATE.md` (rules changed today, per-card loop state, scheduled jobs and watchers, daemon restart commands, open items). Update it right before the user compacts or before a handover, and read it first thing after.

**Why:** on 10-07 the main session reached 340k context and each wake cost about 1M cache-read tokens; auto-compaction never fired by then, so it is only a safety net. The user agreed (09:1x KST) to manual `/compact` at task boundaries plus this memo, and asked whether compaction raises the risk of made-up details. It does for anything not written down, so the memo and the source files are the guard.

**How to apply:** compact only right after a big job that swelled the context (user, 10-07 09:1x KST: "뭔가 큰 작업을 하는 경우에만 하는게 맞을것 같음"), not during routine watching and short replies. At that point say "압축할 때" in one line of the report and refresh the memo; the user types `/compact` (Claude cannot). The earlier "past 150k" trigger was my proposal and is dropped. After compaction treat remembered numbers, ids and quotes as leads only and reopen the file before telling a teammate anything as fact. About once a day, or after two or three compactions, do a full handover instead. See [[handover-semi-auto]] and [[meowbot-answers-in-main]].
