---
name: handover-1006
description: session handover written 2026-10-06 09:50 KST; a new session should read unsw-swarm/docs/HANDOVER-2026-10-06.md first (replaces the 10-05 handover)
metadata:
  type: reference
---
The "meow-main02" session was handed over on 2026-10-06 ~09:50 KST at the user's request.
Read `~/01. Project/개인 프로젝트/unsw-swarm/docs/HANDOVER-2026-10-06.md` first: main vs server state (they differ on purpose), version table, open decisions, what is running and how to restart it, tools, rules.
Then run `python3 tools/team_watch.py` in unsw-swarm and start the two session watchers as background tasks: `python3 tools/loop_watch.py 7200` and `python3 tools/team_watch.py --prs --wait 86400` (they die with the session that started them).
The older `docs/HANDOVER-2026-10-05.md` is history only.
Related: [[loop-spec-1004]], [[team-dynamics]], [[main-session-master-workbench]], [[bot-speaks-when-mentioned]], [[same-hour-baseline]].
