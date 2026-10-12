# Our queen is rammed from 2 steps away with the queen-safety rule on. Find out why the rule did not save her

You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
2026-10-09 15:00 KST; the qualifier maps are unseen, so no map names in any rule.

## What today's online games show (measured: `data/analysis/ladder/dossier/online/agg7.md`, tool
`online/agg7_report.py`, per-game detail `online/agg7-games.json`)
Current team main played 30 games this morning (labels `agg7-m1`; 7 wins) and 15 last night (`sr51-bob1`; same
code). The winner is the side with the longer queen (dead queen = 0), then the longest dragon. 12 of the 30 games
were decided on queen length and our queen was alive at the end in 5. In the 23 losses she died before round 100
in 11 and in rounds 100-300 in 9, nearly always "head-on hit": an enemy head moved into her head. The typical line
is `Q r57/head-on hit/L2/a0 <- #34:L3, d2/k2`: she is 2 long, no own head within 5 tiles, the rammer is 3 long,
starts its turn 2 steps from her and walks 2 steps (one free, one paid).
Replays: `data/online/smoke/<label>-new/M*.replay` with `game-*.json`; more labels of the same bot arrive today
(`agg7-m2`, `agg7-m3`); `agg7-b*` is another build, leave it out. The bot is
`data/online/smoke/sr51-bot/main.cpp` (= team main a358ec8). Card 39's rule: `QUEEN_SAFETY`, `queen_wary()`, the
hit ring (tiles an enemy head reaches on free steps) and the pay ring (paid steps, up to 3 tiles); she should
never end a step or sprint on a ringed tile while a clean one exists. Also read `QUEEN_MIN_CELLS`,
`QUEEN_SAFE_ROUND`, `QUEEN_SAFE_SPAN`, `real_queen()` / `is_queen()` and every condition that turns the rule off.

## Your job
1. Every death of our queen by head-on hit in those games (and each game she survives a turn with an enemy head
   within 3 steps: the denominator). For her last own turn before the hit rebuild what she could know: which
   enemy heads were in her 7 by 7 view, the rings the code would draw from them, whether the tile she ended on
   was ringed, whether a clean step or sprint existed, whether the rule was on at all for her on that turn
   (which condition, with the value), and what the rammer then did (steps, paid length, was it in her view, did
   it come through a portal or from outside the view).
2. Sort every death into exclusive classes with counts, for example: rule off (which condition); rammer not in
   view; rammer in view but its ring drawn too small (why: length seen, free-step formula, paid steps beyond the
   cap); she ended on a ringed tile with a clean one open (a bug: which term outvoted the veto); no clean tile
   existed (boxed in: by what); she moved after the rammer could no longer be avoided (speed); rammed while
   splitting or on a turn she made no move; other. Give the same split for rounds 0-100 and 100-300, and by
   layout size (cells <= 700, 701-1200, above 1200).
3. For the two largest classes tie the cause to main.cpp lines and say what the smallest generic fix is. Check
   each proposed fix against the deaths: how many of the counted deaths it would have prevented by the rule as
   you state it (replay the decision on paper from the rebuilt view), and what it costs (turns where it would
   also have fired without a hit following: count them in the survived-turn denominator).
4. Decide: up to TWO default-off switches, each fitting a single build round, generic, with a mechanism check a
   replay can show. If a class is a plain bug (the rule as written should have held), say so and give the diff.

## Hard limits
Read-only on everything existing. No server calls, no posts, no games, no compiling. Write only
`data/analysis/ladder/dossier/diag-queenhit.md` (110 lines or fewer) and scratch scripts under
`data/analysis/ladder/dossier/work/` (prefix `qh_`). Label every statement measured (script), read from code
(file:line) or estimate. Heavy scans with `nice -n 10`, at most 4 processes.

## Output: `diag-queenhit.md`
1. Three lines: why the rule does not save her (the classes with counts), the change in one or two sentences,
   how sure. 2. The class table (all, by round band, by layout size). 3. "Why, in the code" for the two largest
   classes, with the replay turns that show each (game id, round, positions). 4. "The card(s)" (`title:`, `slug:`,
   `### Claim`, `### Evidence`, `### Expected signal`, `### What would show it's wrong`) with the diff against
   sr51-bot/main.cpp. 5. "Against it".
