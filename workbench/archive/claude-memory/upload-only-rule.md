---
name: upload-only-rule
description: "Online submissions in the heuristic work are upload-only: after an online test never re-activate an older submission; rollback is the user's call"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ab529c8b-1bec-404e-b9b6-2b23c283b013
  modified: 2026-09-29T17:25:31.656Z
---

On 2026-09-30 02:25 KST, during the overnight loop, the user said: "복귀를 할 필요는 없어. 이제 마지막까지 서버에 있는 온라인 모델은 그냥 업데이트만 하면 돼 … 그냥 업로드 규칙인거임. 혹시 나중에 철회하는거면 그건 내가 하는거임. 넌 올리기만."

- After an online test, leave the tested candidate active, even if it is not adopted. Never run `tools/submit.js activate` to restore an older submission.
- The next upload simply replaces the active one.
- Adoption into `bot/` is still judged and recorded separately. The user said not to over-read the rule: it changes only what is active on the server, not how candidates are judged.

- **First upload after the post-sprint ladder reset (user, 2026-10-01 19:3x KST):** "첫 서버 업로드는 최대한 늦추는게 나을것 같아. 확실한 완결성 있는 코드로 시작" — after the reset every team is at 1500 with no active bot; once we upload, autoscrims run 3/hour and a weak start loses rating fast. Do not upload until a complete, solid build exists, and only when the user says so.
**Why:** the user owns rollback decisions for the public submission.
**How to apply:** run online tests with the revert step off (scratchpad `online_candidate.js` with revertId `none`). Never auto-revert, including in morning reports or protocol docs. Related: [[heuristic-repo]].

10-04 17:25 user: stop hesitating on submits/uploads for tests ("그냥 주저없이 하라고 제발"). For online comparison tests (30:30 pair etc.), just upload, run, and swap back; announce start/end in Discord. No pre-confirmation needed. Freeze 10-08 20:00 KST still applies.
10-04 18:55 user: do NOT ration uploads because of rating swings or seeding ("말도 안 됨"); keep uploading/testing freely. On what to ship and how to play, follow QWQ's and Zhe's judgment fully. While the user is away: check Discord/loop/live bot every ~10 minutes and handle what comes up.
