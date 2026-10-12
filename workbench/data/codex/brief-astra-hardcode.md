# Astra analyst: hardcode

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `hardcode`. This is not a card hunt: the output is a verdict.

Question: is the opponent "dev test 1" (team 545, flagged `dev`) playing from knowledge of the ladder maps that a bot could not
have from its 7 by 7 views (stored routes, stored pearl tiles, per-map openings), or is it a general bot? A teammate saw one of
its dragons walk past a pearl in front of it and suspects scripting. The qualifier is on unseen maps, so the team must know whether
what dev test 1 does in the first 100 rounds is something a general bot can do at all. WeHaveQuizzes (team 87) and our own bot
are the controls: run every test on all three sides and report them side by side.

Data: `data/online/smoke/one{1,3,4,5}-d1-old/` (60 games against dev test 1, the same 15 maps four times) and
`data/online/smoke/one{1,2,3,4,5}-w1-old/` (WHQ; one5-w1 may still be arriving). Also look once under `data/top1/` and
`data/analysis/ladder/` for games of team 545 against other teams and use them if the replay format matches.

Tests (each must be able to come out either way; say for each what a general bot would show):
1. Knowledge beyond sight. Rebuild what each side has seen (union of 7 by 7 views so far). For rounds 0-60, take every dragon turn
   on which no pearl and no pearl-bearing tile has ever been seen by that side. On those turns, how often does the step reduce the
   walking distance to the nearest pearl-bearing tile that side has NOT yet seen, against the share of its free steps that would?
   Report the ratio per side, small and big maps apart. Also the round of the first meal against the walking distance from the
   start to that tile (a bot that knows the tile arrives in about that many rounds).
2. Same map, different game. For each map and side, compare dev test 1's dragon paths across the four games: the first round at
   which they differ, and what differed in its view at that round (a pearl, one of our dragons, nothing). A script keeps the path
   when the view changes; a general bot leaves it when the view changes. Same for WHQ across its sets.
3. Pearls passed by. Turns with an uneaten pearl one free step from the head that the dragon does not take, r0-100, per side.
   For dev test 1 list the tiles: do the same tiles on the same map recur across the four games (script) or are they spread
   (score trade-off like ours)? Give ten clearest moments (game id, round, dragon, where it went instead).
4. Map dependence, only if games of 545 on maps outside these 15 or against many teams exist: its first-100-round pearl lead by map.

Report (`data/codex/astra/hardcode/report.md`, under 400 words plus tables): first three lines = verdict (scripted / general /
cannot tell), the single strongest number for it, how sure. Then one table per test, and what was not checked. No card needed.
If the verdict is "general", add two lines on what it does in r0-60 that ours does not, as measured in test 1 or 2.
