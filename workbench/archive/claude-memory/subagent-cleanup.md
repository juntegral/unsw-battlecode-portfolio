---
name: subagent-cleanup
description: "User preference (2026-10-01 02:15 KST): once a subagent finishes and its report is processed, stop it with TaskStop so the user's agent panel stays tidy"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ab529c8b-1bec-404e-b9b6-2b23c283b013
  modified: 2026-09-30T17:13:31.786Z
---

User, 2026-10-01 about 02:15 KST: "밑에 서브에이전트 끝나면 매번 정리좀 해줘. 아직도 정리가 안되어있음."

The panel at the bottom of the user's screen keeps listing completed subagents until they are stopped, so it was cluttered. Stopped agents show as "killed" in ListAgents.

**Why:** the user watches that panel to see what is really running.
**How to apply:**
- Right after processing a subagent's hand-back report, call `TaskStop` on its id: commit the files, verify the key numbers, relay the result to the user.
- Periodically check `ListAgents` for "completed" entries and stop them too.
- Do the same for background shell tasks that are done or stale.
- Never stop a running agent this way without a reason.

Related: [[codex-outsourcing]].
