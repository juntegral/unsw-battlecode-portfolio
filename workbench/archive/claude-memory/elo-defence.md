---
name: elo-defence
description: "user rule 10-06 — when switching bots (after tests, interruptions, deploys) simply keep the best-rated copy of the intended code live; do not over-engineer it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: bf4f8138-7733-48a7-8829-36025e05cdcd
  modified: 2026-10-06T16:13:12.440Z
---

User rule 2026-10-06 23:50 KST: "elo 변화 기준을 아까 확인했으니까, 그 기준으로 elo를 최대한 방어하는 방식으로 간단하게 앞으로 봇을 바꾸면서 진행하면 되는거야. 어려울것 없어." He said this after I answered a simple request with a long design and a safety list.

The basis (measured 10-06, see [[same-hour-baseline]]): the server keeps a rating per submission; the team rating is the active submission's; test bots play on their own rating; an idle submission keeps its number.

The rule, plainly:
- Experiments always run on their own submission, so the main copies are never touched.
- Whenever the live bot is put back (test over, test interrupted by ranked scrims, a manual pause), make live the copy of the intended code with the highest rating, not necessarily the one that was live before. "Same code" = same source hash on the server.
- A test bot that is the same code as main is just another copy; keep whichever is higher.
- A human's own switch (Zhe moves between copies by hand) is left alone.

Update 2026-10-07 01:11 KST (Zhe agreed in #meow to the plan I laid out at his request; the user had said the bot should manage version switching): the two same-code copies run as a ratchet. The higher-rated copy stays parked (idle, its number frozen, nobody can scrim it); the lower one is active and plays; when the playing copy climbs 5 or more above the parked one, `tools/park_watch.py` (resident since 01:14, 5-minute polls, log `unsw-swarm/data/online/park/log.jsonl`) posts "swap due" in #meow and a person activates the parked one on the site; right before seeding is read the parked copy is turned on. Zhe says seeding follows the final elo (his statement, not verified by me); when it is read is unknown. Consequence for tools: after a test return to the playing copy, not the highest, so every test launcher sets `SMOKE_RESTORE_BEST=0` (the tool default is still "highest"). This replaces "keep the best-rated copy live" above until the seeding moment.

**Why:** the user wants the rating protected as a matter of routine during the last days before the qualifier, without ceremony.

**How to apply:** do it and mention it in one line; no proposals, no option lists. I cannot activate a live bot directly (the classifier refuses a production deploy), so the test script does the restore; when a hand step is needed give the one line. Related: [[act-on-context]], [[upload-only-rule]].

10-07 08:0x KST user: automatic swapping of the two copies is allowed ("지금은 그냥 자동 전환 허용할게. 공지만 간단하게 해"). tools/park_watch.py now activates the parked copy itself when the playing one leads by 5, posts one short untagged line ("🔁 swapped. …"), retries a refused activation each check and asks a person after 30 minutes stuck. Commit 59d9e30 (local). Other live activations and uploads still follow the earlier rules.
