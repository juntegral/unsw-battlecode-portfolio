---
name: bottleneck-notice
description: user rule 10-05: a confirmed bottleneck we cannot remove ourselves gets a ⚠️ important notice in #meow via meowbot, same format as the online-test one
metadata:
  type: feedback
---

When a bottleneck is confirmed (not a guess) and is of a kind we cannot fix by our own means (an outside constraint such as server rules, hourly allowances, other teams' actions, machine limits), post a "⚠️ important" notice to #meow through meowbot (`unsw-swarm/tools/meowbot.py --announce-file`), without waiting to be asked.

**Why:** On 2026-10-05 ~03:45 KST, after the online-test swap notice went out, the user said: "뭔가 저렇게 확정적으로. 우리의 자력으로 수정이 불가능한. 형태의 병목이 있으면 꼭 같은 방식으로 공지를 때려줘." They called that one "사실상 첫 병목" and wanted the team to share the picture.

**How to apply:** Same shape as the 03:41 notice (file `unsw-swarm/data/guide/px-bottleneck.txt`): one line saying what the bottleneck is; a short plain explanation of the mechanism; when it hit, with times and cards; what is being done to soften it; what it means for teammates (what to do or avoid). English, casual, few colons ([[discord-msg-style]]), under 2000 characters. Tell the user right after posting. This is a standing permission for this one kind of meowbot post; ordinary Discord messages are still the user's to send. If the notice promises a fix, add it to the ledger ([[discord-promises]]). Not for things we can simply fix ourselves, and not for unconfirmed suspicions.
