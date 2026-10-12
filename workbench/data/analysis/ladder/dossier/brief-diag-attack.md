# Why are we the side that gets rammed? Find what their attackers do that ours do not, and design one switch

You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
2026-10-09 15:00 KST; the qualifier maps are unseen, so no map names in any rule.

## What is already known (read first, do not recount)
- `dossier/fingerprint.md`: over 500 main ladder games their dragons start a cross-team head-on 3.2 times per 1,000
  dragon turns and ours 1.5, in both windows, on 15 to 16 of 19 layouts and in every rating band. Deaths per game
  to round 300: as the one hit, ours 20.7 and theirs 11.7; as the mover, ours 9.7 and theirs 22.6.
- `dossier/diag-australia.md`: above 1200 cells and under 59 dragons our short dragons may ram only a head of 5 or
  more parts (main.cpp 2664-2677; TRADE_EVEN is off). That switch is already being tested by me; do not propose it
  again. It explains big layouts below the cap only: the gap is there on small layouts and at the cap too.
- `dossier/diag-feeding.md`: after feeding begins we make no trades at all (main.cpp 2667, round <= feed_round),
  while their short dragons (2 to 5 long) kill our leaders: 125 of 127 leader deaths are rams, the rammer starts
  1 to 3 tiles away and pays segments for the lunge in 154 of 194. 16 lost games turn on it.
- `dossier/summary.md`, `per-game.jsonl` (schema in `count_dossier.py`), `findings.md` (F8, F13, F28, F39, F42),
  `losses/plan.md`. Bot: `~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp` (mark_trade_targets,
  is_trader, is_trade_target_cell, TRADE_*, RAM_MAX_STEPS, guards_big_ally, END_HUNT_*, ASSASSIN_*, QH_*, the
  threat marking SMALL_UNIT_THREAT_REACH and SMALL_SPRINT_THREAT). Replays under `data/online/`.

## Your job
1. Describe their attack as a rule a dragon could follow, from the replays of all 500 games: for every cross-team
   head-on, the mover's length, the victim's length, the distance at the start of the mover's turn, whether it
   paid segments (a sprint beyond its free steps), how many of each side's heads were within 5 tiles, the round,
   and what each side had lost and gained 15 rounds later (drops eaten included). Do it for their attacks on us
   and for ours on them.
2. Count the chances each side passes up: turns on which a dragon could have reached an enemy head this turn
   (with and without paying), by its own length, the target's length, the local head count and the phase (before
   our switch round, after it, after feeding begins). Which class of chance do they take and we refuse? Rank the
   classes by (their take rate minus ours) times how often the chance comes up times what the trade is worth.
3. Tie the largest class to the lines in main.cpp that make us refuse it.
4. Decide with confidence: ONE default-off switch that fits a single build round and makes our dragons take that
   class of attack, with a mechanism check a replay can show (their rate is the mark). Candidates you may weigh,
   or better ones of your own: trades stay allowed after feeding begins for dragons that are not feeders in
   range of a leader; a short dragon may pay segments to ram a head at least twice its length; a short dragon
   rams the enemy's longest dragon in view whatever the local count. If nothing survives the numbers, "no card".
5. Say what the switch costs in the terms the game is decided on: dragons and length we lose per attack against
   what they lose, and what happens to our longest dragon and our queen.

## Hard limits
Read-only on everything existing. No server calls, no posts, no edits to bot or loop code. Write only
`data/analysis/ladder/dossier/diag-attack.md` (110 lines or fewer) and scratch scripts under
`data/analysis/ladder/dossier/work/` (prefix `at_`). Label every statement measured (script), read from code
(file:line) or estimate.

## Output: `diag-attack.md`
1. Three lines: what their attackers do that ours do not, the change in one sentence (or "no card"), how sure.
2. The tables for jobs 1 and 2. 3. "Why, in the code". 4. "The card": `title:`, `slug:`, `### Claim` (proposal and
   switch name), `### Evidence`, `### Expected signal`, `### What would show it's wrong`. 5. "Against it".
