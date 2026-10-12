# Brief: meowbot pings for the loop states

Repo: unsw-swarm, tools/meowbot.py. Read battlecode docs/LOOP.md (~/01. Project/개인 프로젝트/battlecode/docs/LOOP.md) for the states.
Add:
1. When an [Idea] card gets one of these labels, post a short message to #meow that @mentions the card's author (by:* label → MEMBERS id; by:ai → no mention):
   - status:needs-info: "<@author> the loop has a few questions before building #N: <link>";
   - status:needs-look: "<@author> #N is built, can you check 2–3 replays? <link>";
   - status:tested: the existing verdict post plus an @mention.
   status:candidate is already covered by the candidate card flow.
   Messages should be casual and short, like a teammate. Post at most one message per (card, state) change.
2. /loop and /board: show each open card's status:* state as a column/field (card layout as now). Hide final states (kept/rejected/inconclusive) in /loop.
Keep everything else unchanged.
- py_compile must pass.
- Add offline fake tests in the style of data/codex/check-approver.py.
- Do not run, restart or kill the bot. Do not commit.
- ≤10-line note to data/codex/report-meowbot-states.md.
