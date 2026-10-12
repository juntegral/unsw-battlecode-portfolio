---
name: handover-semi-auto
description: "user decision 10-06 — session handovers are semi-automatic: on \"인계해\" Claude writes the doc, starts the next session and reports; the new session takes over and stops the old one"
metadata:
  node_type: memory
  type: project
  originSessionId: bf4f8138-7733-48a7-8829-36025e05cdcd
  modified: 2026-10-06T13:26:03.223Z
---

User decision 2026-10-06 22:25 KST ("그럼 그냥 앞으로도 반자동으로 하자"): handovers between main sessions run semi-automatically from now on. The user gives the word ("인계해"); nothing starts on a timer.

Steps, in this order so two sessions never answer the same mention:
1. Old session writes `unsw-swarm/docs/HANDOVER-<date>.md` (state, open decisions, open promises, what the user must do by hand, rules) and commits it locally.
2. Old session starts the next one in the background (`claude --bg --name meow-mainNN` with the same start prompt the user typed on 10-06: read the handover, run team_watch, start the two watchers, check the server bot and loop, report loop first in Korean) and tells the user its name.
3. New session confirms its own watchers are up, then stops the old session's watchers and the old session (`claude stop <id>`), as was done by hand for meow-main02 on 10-06.

**Why:** the user does not want to retype the start steps each time, and a curated doc carries the day's lessons better than an automatic summary.

**How to apply:** first run is untested as of 10-06: starting a session from inside a session may be refused by the permission classifier. If it is, do not route around it; give the user the one line to run. Pushing the doc to the remote has needed the user's hand so far. Related: [[handover-1006]], [[main-session-master-workbench]], [[discord-first]].
