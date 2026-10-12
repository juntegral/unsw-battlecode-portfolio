# Add the agg9 arm to the online report

Tool: `data/analysis/ladder/dossier/online/agg7_report.py` (output `agg7.md`, `agg7-games.json`, `agg7-validation.json`, `agg7-done.txt`).
A new online label is coming: `agg9-a1` (`data/online/smoke/agg9-a1.json`, replays `agg9-a1-new/`, wins in `agg9-a1-report.log`;
the label is not there yet, or only partly, when you start: the tool must run cleanly with it absent, half-written and complete).
Its bot is the live build (arm B7Q) plus three switches: LUNGE_PEARL true, TRADE_SHORT_BY 1, FEEDER_EAT true
(source of the bot: `data/online/smoke/agg9-bot/main.cpp`; grep the three names there to read the exact conditions).

Do this:
1. Add the label as a fourth arm `B10` (any label starting `agg9-a`). Every per-arm table gets a fourth column. Read wins the
   same way as for agg8-q1 (per-opponent lines of `<label>-report.log`, since the live bot is another build).
2. Paired comparison section: B10 vs B7Q paired by (opponent, map) with `agg8-q1` (say in the heading that the hours differ),
   and B10 vs MAIN paired by (opponent, map) with each of agg7-m1..m3 separately and pooled. Same layout as the existing pair table.
3. Three new rows in the switch-event table, counted from the replays for ALL arms (so the off arms give the base rate),
   each with a one-line definition under the table:
   - TRADE_SHORT_BY: head-to-head hits started by our non-queen dragon on an enemy head exactly one shorter than ours,
     split by our length (3, 4, 5+). Also the count of our hits on an equal head and on a head two or more shorter, for scale.
   - LUNGE_PEARL: our hits on an enemy head in which our dragon also ate a pearl in the same turn's movement (paid sprint steps
     through a pearl cell), and next to it all our paid-sprint hits.
   - FEEDER_EAT: read the condition in the bot source and count the closest replay-observable event (expected: pearls eaten by a
     non-queen, non-longest dragon in the turns right before it is absorbed by / feeds our longest dragon). State the definition used.
   Reuse the collision and pearl extraction the tool already has (hunt_small, trade_even, eaten). Per-game counts go in `extra.counts`.
4. Rerun `nice -n 10 python3 -B data/analysis/ladder/dossier/online/agg7_report.py`. Check that MAIN, B7 and B7Q game counts and
   wins are unchanged from the current `agg7.md` (90/21, 60/23, 30/14) and every game is counted once.
5. Append to `agg7-done.txt` five lines at most: what was added, the three definitions, anything that could not be counted and why.

Write only under `data/analysis/ladder/dossier/online/`. No network, no posts, no games, no compiling. Keep the cache working
(`agg7-cache.json`) so a rerun after the label completes only reads the new games.
