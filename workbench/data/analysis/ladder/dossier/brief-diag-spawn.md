# The rank-1 team stands at the tiles that spawn pearls and we do not. Find how, and design one switch

You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
2026-10-09 15:00 KST; the qualifier maps are unseen, so no map names in any rule.

## The gap (measured; `dossier/target/scoreboard.md`: ours = 500 main ladder games, rank-1 = 597 of its own games,
both on the 19 shared layouts with each layout weighted equally)
- Turns that start on or beside a tile that has already spawned a pearl twice: rank-1 19.2% in rounds 0-100 and
  35.5% in rounds 101-300; ours 13.5% and 25.3%. Rank-1 is the higher one on 18 of 19 layouts.
- Rounds from a pearl's birth until it is eaten, for the pearls a side eats: rank-1 17.1 then 5.5; ours 26.6 then
  8.7 (rank-1 is slower on 3 and 1 of 19 layouts).
- Share of all pearls born in rounds 101-300 that the side eats: rank-1 56.5%, ours 42.4%. Dead-drop pearls:
  55.9% against 40.6%.
- A pearl on a neighbouring tile not taken: rank-1 19.3% of such turns in rounds 101-300, ours 26.9%.
An earlier analysis (`dossier/sweep.md`) refused a hot-tile card because "share of turns near a spawn tile" counts
eating twice. The wait from birth to eating does not have that fault: it says who is standing there when the
pearl comes. That is the question now.

## Already counted (read first)
`dossier/target/scoreboard.md`, `scoreboard.json`, `target/per-game-top1.jsonl` (rank-1 rows; replays under
`data/online/top1/`, team id 306), `dossier/per-game.jsonl` (ours; replays under `data/online/ladder/`),
`dossier/fingerprint.md`, `dossier/sweep.md` (the code lines of our hot-tile rule and of what moves a dragon with
nothing in view), `findings.md` (F14, F20), and for the layouts with known spawn intervals
`dossier/local/maps2/README.md` and `maps3/README.md`. Bot:
`~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp` (note_hot, HOT_*, WEIGHT_HOT, the soon
tile rule SOON_*, pearl_timer, target_bonus, ally_race_steps, in_leader_pearl_zone).

## Your job
1. From the replays of both teams on the shared layouts: for each natural pearl birth, where the nearest dragon of
   the side was at the moment of birth (steps away), whether a dragon of the side had been standing within 1 and
   within 2 steps for the 3 rounds before, and who ate it and when. Split tiles by how fast they respawn.
2. What does a rank-1 dragon do after it eats on a fast tile: stay within 1 step, circle, or leave, and for how
   many rounds? What does ours do? What do both do with the countdown a tile shows (a bot can see the rounds until
   the next spawn on tiles in view)? How many dragons does each side keep at one cluster of fast tiles?
3. Tie our behaviour to the lines: which rule moves our dragon off a tile that is about to spawn, or keeps it
   from going to one (the pull that ends at 6 steps, the nearest-team-mate rule, the mark wiped at a high
   countdown, the leader zone, a split child that starts with an empty memory).
4. Decide with confidence: ONE default-off switch that fits a single build round and makes our dragons wait at
   or return to tiles that are about to spawn, with a mechanism check a replay can show (rank-1's rates are the
   mark: wait from birth to eating, share of births with a dragon within 1 step). Or "no card" and why.
5. Say what it costs: dragons that wait do not explore or fight. Check on the same games whether rank-1's
   campers are the ones that get rammed.

## Hard limits
Read-only on everything existing. No server calls, no posts, no edits to bot or loop code. Write only
`data/analysis/ladder/dossier/diag-spawn.md` (110 lines or fewer) and scratch scripts under
`data/analysis/ladder/dossier/work/` (prefix `sp_`). Label every statement measured (script), read from code
(file:line) or estimate.

## Output: `diag-spawn.md`
1. Three lines: what rank-1 does at spawn tiles that we do not, the change in one sentence (or "no card"), how sure.
2. The tables for jobs 1 and 2. 3. "Why, in the code". 4. "The card": `title:`, `slug:`, `### Claim` (proposal and
   switch name), `### Evidence`, `### Expected signal`, `### What would show it's wrong`. 5. "Against it".
