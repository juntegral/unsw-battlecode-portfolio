---
name: weak-loss-rule
description: user rule 10-09 02:52: every ranked game lost to a team rated 100+ below us gets its cause found and a fix made; unsw-swarm/tools/weak_watch.py automates the detection and the analyst
metadata:
  type: feedback
---

Every single game lost to a team rated 100 or more below us must have its cause found and then be fixed, not just noted.

**Why:** said by the user 2026-10-09 02:52 KST. One 2-3 battle lost to a team 165 points lower cost 98 rating points that night (a 3-2 win over such a team gives about +25), and the qualifier is a best of seven where one such game can decide it.

**How to apply:** `unsw-swarm/tools/weak_watch.py --new` finds new such games in `data/online/live-one1/` (ledger `weak-handled.txt`) and starts one Codex analyst per battle (`data/codex/astra/weak-b<battle>/report.md`). Keep it polling in the background, read each report, turn each distinct cause into a switch in the next bundle ([[active-means-spend]]), and tell the user what the cause was and what was changed.

10-09 04:08 extension by the user ("토큰맥싱"): analyse EVERY incoming game every 30 minutes, lost games more deeply. `unsw-swarm/tools/sweep_loop.sh` does it (rounds under `data/codex/astra/sweep/<HHMM>/`; the main session reads only `synth/report.md`; shared card list `data/codex/astra/CARDS.md` must be updated at every release). It replaced the separate weak_watch polling.
