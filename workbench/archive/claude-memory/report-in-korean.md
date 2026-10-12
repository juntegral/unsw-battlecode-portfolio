---
name: report-in-korean
description: User rule (2026-10-01 08:45 KST): every report and status update to the user must be written in Korean
metadata:
  type: feedback
---

On 2026-10-01 at about 08:45 KST the user said: "앞으로 이런거는 다 한글로 보고해." It came right after I gave a v1.4 progress report and short status updates in English.

**Why:** the user reads the reports in Korean. Several overnight notices and status lines had drifted into English.

**How to apply:** write every user-facing reply in Korean. That covers progress reports, status lines, notification acknowledgements and summaries of agent hand-offs. Code, file paths, commit messages and agent briefs may stay in English. Log lines in `OVERNIGHT-*.md` are already Korean. Before sending, check that the reply is Korean even when the input (agent messages, tool output) is English.

Related: [[user-research-style]].
