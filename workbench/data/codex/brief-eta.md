# Brief: tell the team when long loop steps start and how long they'll take

Teammates can't see how long things take. meowbot should say so when a long step starts.

## Part A — runner (edit ONLY in the worktree ~/meow-dev, branch dev/eta; never the live checkout)
Files: ~/meow-dev/work/loop/runner.py, jobs.py, tests.
- For every step the runner starts (clarify, build, task, adopt, mechanism, look, outcome, verdict, ladder), record in ~/meow-loop-out/status.json under the card:
  `step_started` (ISO time), `eta_minutes`, `eta_at` (ISO), and `queue` (what it waits on, if waiting).
- eta_minutes = the median duration of finished jobs of the same step kind. Read the existing job records under ~/meow-loop-out/**/jobs/<step>/ (job.json start → done.json finished; look at the real files for the field names). Take the last 10. With fewer than 2 samples, use these defaults:
  clarify 3, build 20, task 15, adopt 5, mechanism 30, look 8, outcome 150, verdict 5, ladder 20.
- When a card is waiting on a lock, estimate the wait from the running job's remaining ETA.
- Also append one line per step start/finish to ~/meow-loop-out/events.jsonl:
  {time, card, title, step, event: "start"|"done"|"failed", eta_minutes, minutes (on done), note}.
- Tests for the ETA calculation and the events file. `python3 -m unittest discover -s work/loop/tests` must pass. Commit on dev/eta (the commit is fine there); do not push.

## Part B — meowbot (unsw-swarm/tools/meowbot.py)
- Tail ~/meow-loop-out/events.jsonl. Keep a byte offset in state; on the first run start at the end, no replay.
- Post ONE short line to #meow when a step with eta_minutes ≥ 10 starts, e.g.
  "⏱ #17 local A/B started, about 2h 30m (done ~20:10 KST / 13:10 CEST)".
  Step names in plain words: build = "building", mechanism = "quick behaviour check", outcome = "local A/B", ladder = "reading new ladder games", task = "task build + check".
  Show both KST and Europe/Stockholm times (zoneinfo).
- Post on failure: "⚠️ #17 <step> failed: <note, short>; the loop retries or needs a look".
- Do not post on normal step completion; results already have their own posts. No @mentions.
- /loop and /status show for each running card: the step, minutes elapsed, and the ETA.
- /meow brain includes the same ETA info (tools/meow_chat.py build_brain reads status.json already; make sure the new fields show).
- Offline fake tests; py_compile must pass. Do not run, restart or kill the bot. Do not commit in unsw-swarm.

Write a ≤8-line note to data/codex/report-eta.md, listing the new untracked files, if any.
