# Brief: make the "running late" notices readable (they went out looking broken)

What was posted in Discord (real examples, 10-05 00:16–00:19 KST):
1. "⏳ #27 passage: waiting 16m for the AI slot. why: waiting for #0 Ladder review ladder (estimate overdue); unknown, checking again in 15 min. new estimate: unknown, checking again in 15 min"
2. "⏳ #30 big-map-trades: waiting 29m for the game slot. why: waiting for #0 Ladder review ladder (estimate overdue); unknown, checking again in 15 min. new estimate: unknown, checking again in 15 min"
3. "⏳ #0 Ladder review: reading new ladder games is running late (22m so far, planned 17m). why: still working: 59 tool calls so far (28 reads, 2 builds, 11 game/replay runs, 13 edits); last: 'Compare queen exposure, distance from spawn and escort for us and oppon…'; 'List remote branches and find queen-hunt and ram code references'. new estimate: done ~00:25 KST / 17:25 CEST"
Problems: three posts within three minutes about one cause; "#0 Ladder review ladder"; "unknown, checking again…" printed twice; tool-count jargon nobody on the team can read.

## Wanted
- ONE post per cause. When a step is late and other cards wait behind it, post a single message for the late step and list the waiting cards in it. Cards waiting behind a step that is itself reported late do not get their own post. A card waiting 15+ min behind a step that is NOT late still gets its own short post.
- Plain words, teammate tone, no tool counts. Shape:
  "⏳ the ladder review (AI reading our new ladder games) is running late: 22m so far, planned 17m. it's still digging: comparing how exposed our queen is vs theirs. should be done ~00:25 KST / 17:25 CEST. waiting behind it: #27 passage, #30 big-map-trades"
  - For card steps: "⏳ #31 queen-hunt: building is running late: 45m so far, planned 27m. it's a big change, still editing and re-checking that it plays the same when off. should be done ~23:10 KST / 16:10 CEST".
  - "what it's doing" = one short clause from the latest activity description (lower-case first letter, strip trailing "…", ≤ 90 chars), or a generic clause by step kind when there is none. Mention identity re-checks or game runs in words if they dominate, never as counts.
  - Unknown estimate: say it once: "no estimate yet, i'll post again in 15 min".
- The ladder step is not a card: call it "the ladder review", never "#0".
- Never repeat the same sentence in "why" and "new estimate".

## Where
- Runner side: work ONLY in the worktree ~/meow-dev3 (branch dev/latefix, from main): work/loop/late.py (+ runner.py if needed) — reason text, the "holder" info (so meowbot can group), and no `late` event for a waiter whose holder is already late (or mark it `covered_by`). Tests in work/loop/tests; `python3 -m unittest discover -s work/loop/tests` must pass. Commit there if git allows; do not push.
- meowbot side: unsw-swarm/tools/meowbot.py (edit files only; never start/stop the bot; do not commit): the message format above, grouping, tests (tools/test_meow_late.py). ALL offline checks must pass: tools/check-*.py, tools/test_*.py, data/codex/check-*.py.
Write a ≤6-line note to data/codex/report-latefix.md with example outputs for: a late AI step with two waiters, a late batch, a lone waiter, and an unknown estimate.
