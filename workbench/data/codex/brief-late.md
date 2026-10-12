# Brief: "running late" notices — reason + new end time, posted by meowbot

Team rule (required by the team lead): when a loop step runs past its estimate, or a card waits long for a slot, the team must be told in Discord WHY and WHEN it is now expected to finish. Example of what a person wrote by hand today and what the notice should carry automatically:
"#31 queen-hunt: building took 45 min (planned 27). Why: 124 tool calls — 56 reads of a 5,000-line bot file, 35 edits (~250 changed lines), 5 identity checks of 40 games each, plus a checker and unit tests. Now waiting for the game slot, which the pool validation holds until ~23:17."

## Part A — runner (edit ONLY in the worktree ~/meow-dev2, branch dev/late; never the live checkout; commit there, do not push)
Read work/loop/runner.py, jobs.py (step_timing, eta_minutes, remaining_wait, events.jsonl writer), tests.
1. Late detection, each poll, for every card with a running or waiting step:
   - running: late when elapsed > eta_minutes × 1.25 and elapsed − eta_minutes ≥ 5 min;
   - waiting on a lock: late when it has waited ≥ 15 min.
   Emit one `late` event to ~/meow-loop-out/events.jsonl per (card, step, level), where level increases each time the NEW estimate is missed again, so there is no spam: at most one notice per missed estimate.
2. Each late event carries: card, name, step, started, planned minutes, elapsed minutes, `reason` (plain English, ≤ 300 chars), `new_eta_minutes`, `new_eta_at`.
   Reason + new estimate by kind:
   - AI step (clarify/build/task/adopt/look/verdict/ladder/decide/reply): read the step's stream-json log (path in job.json `log`). Count tool calls by type and recognisable activities from Bash descriptions/commands (identity checks, builds, game/replay runs, reads). Take the last 2 tool descriptions. Reason like "still working: 124 tool calls so far (56 reads, 35 edits, 5 identity checks of 40 games); last: 'Run the toggle-off identity check'".
     New estimate: max(elapsed × 1.3, the longest finished run of this step kind) − elapsed, at least 5 min.
   - batch step (mechanism/outcome): progress from the result/row files and replay counts in the job's out dir (games done / planned from the plan json). Reason like "games are slower than planned: 96 of 320 done, 3.1/min". New estimate from the measured rate.
   - waiting: say what holds the lock: another card's step (name the card ref and step, with its remaining estimate) or a process outside the loop (find the holder pid via lsof on the lock file and describe its command briefly, e.g. "pool validation (work/pool.py)"). New estimate = the holder's remaining estimate + this step's own estimate; if unknown, say "unknown, checking again in 15 min".
3. status.json shows `late: true`, the reason and the new ETA for the card.
4. Unit tests for the three kinds, the once-per-level rule, and the text length. `python3 -m unittest discover -s work/loop/tests` must pass.

## Part B — meowbot (unsw-swarm/tools/meowbot.py; edit files only; never start/stop the bot; do not commit)
- On a `late` event post ONE message, e.g.:
  "⏳ #31 queen-hunt: building is running late (45m so far, planned 27m). why: <reason>. new estimate: done ~23:10 KST / 16:10 CEST"
  For waiting: "⏳ #31 queen-hunt: waiting 18m for the game slot. why: <reason>. new estimate: starts ~23:17 KST / 16:17 CEST".
  No @mentions. Card ref via the existing card_ref helper.
- /loop, /status and the /meow brain show the late flag, reason and new ETA.
- Offline tests; ALL checks must pass: tools/check-*.py, tools/test_*.py, data/codex/check-*.py; py_compile.

Write a ≤10-line note to data/codex/report-late.md, listing every changed/new file in both places.
