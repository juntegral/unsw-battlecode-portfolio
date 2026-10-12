---
name: loop-status-first
description: "user rule 10-05: every status report opens with the running card loop's state (per card), before Discord/GitHub/anything else"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e3d433df-e6c2-41f6-81d4-738b9ea48abd
  modified: 2026-10-04T15:46:16.706Z
---

Every status report to the user starts with the card loop: what is running right now, what is queued behind it, what is waiting on a person, and anything late. Discord, GitHub, online tests and background studies come after.

**Why:** On 2026-10-05 the user asked "지금 상황" twice and got Discord and the #27 online test first, with the loop buried further down. They replied "그니까 지금 돌아가고 있는 루프 알려달라고. 루프 상황을 항상 맨 위에 말해줘." To them "상황" means the loop (my reading: the loop is the thing they steer; the rest is context).

**How to apply:** Read `~/meow-loop-out/status.json` and `runner.log` on every status question and lead with a per-card rundown (#N name, step, running/queued/waiting, ETA or how late). The [[discord-first]] check still runs first as an action; it just isn't the first thing reported. Keep it short and in Korean per [[report-in-korean]].

"상황 확인" (named by the user on 2026-10-05): shorthand for "check Discord and the loop status". When the user says it, run the Discord/GitHub check, read the new messages, and report the loop first, then Discord.
