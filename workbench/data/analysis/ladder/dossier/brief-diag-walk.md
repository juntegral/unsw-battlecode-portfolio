# With no pearl in view the rank-1 team walks on and we turn back. Is that worth a switch now?

You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
2026-10-09 15:00 KST; the qualifier maps are unseen, so no map names in any rule.

## The gap (measured; `dossier/target/scoreboard.md`: ours = 500 main ladder games, rank-1 = 597 of its own games,
on the 19 shared layouts, each weighted equally)
- A step onto one of the dragon's own last 12 tiles when no pearl is in view: ours 17.8% (rounds 0-100) and 19.7%
  (101-300); rank-1 10.4% and 11.2%. Rank-1 is the lower one on 17 and 18 of 19 layouts.
- Keeps its previous direction when no pearl is in view: ours 40.4% and 37.4%; rank-1 48.9% and 47.9% (18 of 19).
- Turns that start with no pearl in view: ours 48.3%, rank-1 40.8% (rounds 101-300).
- First contact with the enemy: round 19.9 for us, 12.5 for rank-1.
An earlier analysis (`dossier/sweep.md`) said "no card" on this, comparing us with our average opponents (16.3%
against 13.2%) and finding that inside our own games the low-dither games do not eat more. Against rank-1 the gap
is three times that size. Decide again, with rank-1 as the mark.

## Already counted (read first)
`dossier/sweep.md` (the verdict, the cuts, and the code lines: nothing knows the last direction, NO_REVERSE is off,
FAR_GAIN, the unseen bonus, CENTER_PULL, PENALTY_NO_TAIL), `dossier/target/scoreboard.md`, `scoreboard.json`,
`target/per-game-top1.jsonl` (rank-1 rows; replays `data/online/top1/`, team id 306), `dossier/per-game.jsonl`
(ours; replays `data/online/ladder/`), `losses/early-growth.md`, `findings.md` (F4, F10, F14, F41).
Bot: `~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp`.

## Your job
1. Where do our re-treading steps happen and what are they: by dragon length, by rounds since the dragon was born
   (a split child starts with an empty memory), by what is around (a team mate within 3 tiles, a wall pocket, a
   portal, open ground), and by which term of our step score decided the step where you can reconstruct it.
   The same split for rank-1. Which kind accounts for the difference?
2. Is it worth pearls against rank-1's mark? Inside each layout, compare rank-1's games and ours on: tiles seen by
   round 50 and 100, rounds to the first pearl eaten by a new-born dragon, pearls eaten per dragon turn by dragons
   with nothing in view for the last 5 rounds, and the first contact round. If walking on buys rank-1 nothing you
   can measure, say "no card" again and say what the 7 points of extra blind turns come from instead.
3. If it is worth it: ONE default-off switch that fits a single build round (for example a small cost on a step
   onto the dragon's own recent tiles, or on changing direction, only when no pearl, soon tile, hot tile or
   threat scores; or NO_REVERSE as it is), the lines it touches, and a mechanism check a replay can show with
   rank-1's rates as the mark (re-tread about 11%, direction kept about 48%). Say what it must not change
   (dragons in a pocket, dragons fleeing, the queen).

## Hard limits
Read-only on everything existing. No server calls, no posts, no edits to bot or loop code. Write only
`data/analysis/ladder/dossier/diag-walk.md` (110 lines or fewer) and scratch scripts under
`data/analysis/ladder/dossier/work/` (prefix `wk_`). Label every statement measured (script), read from code
(file:line) or estimate.

## Output: `diag-walk.md`
1. Three lines: what the re-treading is and whether it costs, the change in one sentence (or "no card"), how sure.
2. The tables. 3. "Why, in the code". 4. "The card": `title:`, `slug:`, `### Claim`, `### Evidence`,
   `### Expected signal`, `### What would show it's wrong`. 5. "Against it".
