# Brief: far fewer delay notices in Discord

Two working copies: the loop code in the git worktree `~/meow-deploy` (branch deploy/fair-latefix, same commit as main) and the Discord bot in this repository (unsw-swarm, `tools/meowbot.py`). Edit loop files only inside `~/meow-deploy/work/loop/` (plus `docs/LOOP.md` there); edit bot files only under `tools/` here. Never touch `~/01. Project/개인 프로젝트/battlecode/work/loop/` (the live runner reads it). No commits, no pushes, no network, do not start the runner or the bot. Never read `docs/api.txt` or `docs/discord.txt`.

## Problem
The loop emits a `late` event for every card that waits for a lock (first after 15 minutes, then again every 15 minutes or at each new estimate), and the bot posts each one. In under two hours this morning that was 12 "waiting …" posts against 2 "running late" posts. Waiting in a queue is normal; the team finds this far too noisy.

## New rule
1. A card that is only waiting for a lock (the AI slot or the game slot) produces no Discord notice, with one exception: when it has waited 120 minutes in a row, one notice; then one more every further 120 minutes while it is still waiting. That notice names what is ahead of it and, if known, when it should start.
2. A running step that is late: first notice when it has run for at least 1.25 times its planned minutes and at least 5 minutes over; a second when it reaches 2 times the planned minutes; after that at most one every 60 minutes. Each of these keeps the existing "waiting behind it: …" list, which is how waiting cards are made visible.
3. `status.json` keeps every field it has now for every card (`late`, `reason`, `new_eta_at`, `queue`, `elapsed_minutes`, …), computed as before. Only the events that lead to Discord posts change. If the simplest way is to keep writing all events and mark the ones that should not be posted (for example `"post": false`) so the bot skips them, do that, and keep old events without the mark behaving as before.
4. Wording of the notices that remain stays as it is.

## Tests
Update the loop tests in `~/meow-deploy/work/loop/tests/` and the bot tests under `tools/` to the new rule, and add cases for: a card waiting 30, 60 and 119 minutes (no post), 120 minutes (one post), 240 minutes (second post); a running step at 1.2x (no post), 1.3x (post), 1.9x (no second post), 2x (second post), then one per 60 minutes. Run both suites and make them pass:
- `cd ~/meow-deploy/work/loop && python3 -m unittest discover -s tests`
- `cd tools && python3 -m unittest discover -p 'test_*.py'` (from this repository)

## Output
Write `data/codex/report-quiet-late.md` last: what changed in each repo, the last 4 lines of both test runs, and how many Discord posts the new rule would have produced for this sequence: three cards wait behind one 26-minute build that takes 65 minutes, then behind a 77-minute test that takes 92 minutes.
