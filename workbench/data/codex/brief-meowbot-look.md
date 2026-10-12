# Brief: meowbot attaches the "look" replays

Repo: unsw-swarm, tools/meowbot.py (the status ping code was just added; read data/codex/report-meowbot-states.md).
When posting the status:needs-look ping for card N:
- read `~/meow-loop-out/card-N/look.json` ({"replays":[paths], "note": "..."}), if it exists;
- attach those replay files to the Discord message (discord.File), at most 3 files, skipping any over 24 MB;
- add the note in one short line, plus a one-liner on how to watch a replay: the team uses the official viewer. Check README/docs in ~/01. Project/개인 프로젝트/battlecode for how a .replay is opened, and say it in ≤1 line.
- If look.json is missing, post the ping as now.
Constraints:
- py_compile must pass;
- add an offline fake test;
- do not run, restart or kill the bot; do not commit.
Write a ≤5-line note to data/codex/report-meowbot-look.md.
