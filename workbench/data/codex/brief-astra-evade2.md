# Analyst: evade2

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `evade2`. Background: `data/codex/astra/evade/report.md` and the
builder's notes `data/codex/build/evade/done.txt`.

one7 (live 02:31 to now, `data/online/smoke/one7-bot/main.cpp`, sets `one7-w1` and `one7-c1`) switched on `SHORT_EVADE`: a
non-queen, non-leader dragon of 4 or less, not ahead in heads in view, refuses a final move into the free reach of a visible
enemy head when a safe alternative exists. The first report said 329 of 559 rams on our non-queens (one5, r0-200) had a free
way out. But the rate of our dragons dying to an enemy ram did not move: per 1,000 of our turns, r0-100 / r101-300, one7 4.16 /
4.21 against one5 4.13 / 4.56 (WHQ), 4.34 / 5.24 against 4.33 / 4.80 (Cache me outside). Find out why.
1. Redo the first report's table for one7-w1 and one7-c1 (rams on our non-queens r0-200: all, with a free way out, without, not
   seen) beside one5's. Did the avoidable ones fall?
2. For every ram on a non-queen of ours in the one7 sets: on our last turn before it, would the rule as written in the code have
   applied (length, leader, heads in view, enemy head visible, reach)? Classes: rule applied and we still died (why: the attacker
   used paid sprint steps, came from outside the 7 by 7, a second attacker, the alternative was the one hit); rule did not apply
   (which condition failed); the move was one the rule exempts (intended ram, hunt, trade, split, stop). Give the share of each.
3. How often did the rule change a move at all (reconstruct from positions: turns where the old scoring's first choice was in
   reach and the dragon went elsewhere is not observable, so estimate from the conditions), and what happened to those dragons
   in the next 5 rounds against one5's dragons in the same condition (dead, ate, alive)?
4. Verdict: keep as is, widen (name the condition to drop or the reach to add, for example one paid step, or dragons of 5 to 8,
   or heads not in view but known from the side's shared sightings), or switch off. One card with lines.
