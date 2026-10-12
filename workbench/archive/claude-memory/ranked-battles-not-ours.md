---
name: ranked-battles-not-ours
description: User (2026-10-01): battles the user did not mention were requested by other teams and don't use our tickets; ticket estimate now counts only our own ledger
metadata:
  type: feedback
---

On 2026-10-01 at about 09:05 KST the user said: "내가 랭크 대전 돌린거 아님. 난 앞으로도 너한테 말 안한거면 그냥 다른사람이 신청한거일거야 아마. 티켓 소진 안되었을거임."

Context: after the sprint freeze, ranked battles started every 5–7 minutes. `tools/online.js tickets` counted 4 of them as ours, because we were team A, and estimated 40 of 60 tickets left. That held the v1.2 wave back for an hour.

**Why:** since 9/28 the scrim team order is random (rules/CHANGES-2026-09-29.md), so "we are team A" no longer means we requested the battle. Every request we make goes through our tools and is written to `data/online/requests.jsonl`.

**How to apply:**
- Treat battles the user did not tell me about as other teams' requests.
- The ticket estimate in `tools/online.js` (both repos, fixed 09:06 KST) now counts only our local ledger. The server inference is printed for information only.
- If a request is refused for lack of tickets, report it rather than guessing.

Related: [[sprint-deadline-freeze]].
