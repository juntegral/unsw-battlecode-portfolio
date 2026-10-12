# Brief: counts for the narrow queen-defend switch (w-escort)

You do the counting only: finish and check two counting scripts, run them, write one result file.
Do not start, stop or replay any game, do not change any bot source, do not build bots, do not judge the result.
Work dir: this repo (`unsw-swarm`). The game data is in `~/meow-redteam` (you may read it, you cannot write there).

## Rules
- Write only inside `data/codex/tmp-escort/` (scripts, json lines, logs) and the one result file `data/codex/out-escort-counts.md`. Nothing else anywhere.
- Never start a game (the engine does not run in your sandbox) and never kill any process you did not start yourself; stop your own by PID only, never by pattern.
- Run python jobs under `nice -n 10` (a `setpriority: Operation not permitted` warning is harmless). Do not run `count_local.py` itself (its full recount is heavy); importing from it is fine.
- If something fails, say so in the result file with the error text. Do not invent numbers; a missing number is written as `n/a` with the reason.

## Background (what the numbers are for)
Game: two sides of snakes ("dragons") on a torus grid; a head rammed into an enemy head kills both ("head-on", death reason 3).
The queen of a side is its dragon with the lowest starting id. Three arms, all playing against the bot `m3hunt`:
- `m3b7qk_vh`: baseline (live build). Runs exist: 32 maps, seeds 1 and 2, both sides.
- `m4qd_vh`: baseline + "defend radius 5": any mate that sees our queen and an enemy head within 5 tiles of her attacks that head. Runs exist: 29 maps, seed 1, both sides (58 games).
- `m5dn_vh`: baseline + "narrow defend": only a mate of length 4 or less, and only when the enemy head is within 3 steps of our queen.
  Its 8 games (seed 1, both sides of `sqheld_open_small_90012`, `sqheld_portals_medium_90007`, `sqheld_portals_medium_90020`, `ladder_islands_1`) are being played by someone else right now; you only wait for them (step 4).
Runs are at `~/meow-redteam/solo/runs/<arm>/<map>-seed<S>-side<K>/{game.replay,result.txt}`; `side<K>` is the team index our arm plays.

## Step 1: copy the scripts
Copy every `*.py` from `~/meow-redteam/solo/src/w-escort/` into `data/codex/tmp-escort/` and work on the copies only.
`esc_scan.py`, `esc_tab.py`, `esc_view.py`, `esc_dump.py` are finished and trusted. `dn_scan.py` and `dn_tab.py` are unverified drafts of step 2 left by an interrupted run:
read them against step 2 line by line, fix or rewrite what does not match, and run the checks of step 2 before using them.
The scripts write their json lines next to themselves, so the copies write into `data/codex/tmp-escort/`. For the check of step 2 also copy `esc-m3b7qk_vh.jsonl` and `esc-m5es_vh.jsonl` from the same folder.
If `~/meow-redteam/solo/src/w-escort/dn-m3b7qk_vh.jsonl` or `dn-m4qd_vh.jsonl` exist there, they were made by the unverified draft: do not use them unless your checked `dn_scan.py` is byte-identical to the draft; otherwise rescan.

## Step 2: extend the counting scripts
Existing, working (now copied into `data/codex/tmp-escort/`): `esc_scan.py` (one json line per game to `esc-<arm>.jsonl`; parser = `replay_format.py` and `Geo` from
`~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/local/`), `esc_tab.py` (table of two or more arms on their common games),
`esc_view.py`, `esc_dump.py`. Read `esc_scan.py` and `esc_tab.py` fully before changing anything. Definitions already in them and to be kept:
tiles = torus Manhattan distance; steps = path over open edges and portals with bodies ignored (`Geo.adj`); a chase = consecutive queen turns that start with
a non-queen enemy head within 3 steps of our queen's head; "within 5 tiles of her" for a head-on = our dragon's head is within 5 tiles of our queen's head when it dies.

`dn_scan.py` and `dn_tab.py` are `esc_scan.py` and `esc_tab.py` plus the following (the draft may already have part of it):
1. In the scan, for every turn keep the mover's length at the start of its turn (`L0`) and the number of head moves it has made in the turn (event kind 9 with a new head tile for the actor).
2. For every death with reason 3 also store: `L0` of the mover, `moved` = head moves of the mover in that turn up to the collision, and for an enemy dragon that dies:
   `qsteps` = steps from our queen's head to that enemy's head (breadth-first over `Geo.adj`, cap 8, 99 if farther or if our queen is dead) and `qtiles` = tiles between them, both taken at the START of the mover's turn
   (so for a mate that rams, it is where the enemy head stood before the mate moved; for an enemy that rams, where it stood before it moved).
   Output file name: `dn-<arm>.jsonl` (same `only=<file>` option as today).
3. In the table, a head-on pair = two reason-3 deaths of the same round and mover, one ours and one theirs (as `pairs()` does today). Count only pairs where ours is not our queen, theirs is not their queen, and ours died within 5 tiles of our queen. New rows:
   - mate moved, by rammer length `L0` 2 / 3 / 4 / 5+, each split into "target was a pursuer" (`qsteps` <= 3) and "target only in the radius" (`qsteps` > 3);
   - enemy moved (count);
   - paid hunt sprints by a 5+: mate moved, `L0` >= 5 and `moved` > ceil(`L0` / 4) (free steps are ceil(L/4); every step beyond costs one segment); give the count and the segments paid in total (`moved` - ceil(`L0`/4), summed);
   - length lost by us / by them in those pairs (length at death, as today).
   - "pursuers rammed by a mate": mate-moved pairs with `qsteps` <= 3, all rammer lengths (count).
   Keep every row `esc_tab.py` prints today (chases; turns each; lasting 4+; rounds the queen lived; queen deaths by kind; boxed-in deaths; mates dead on their own move near her; own dragons and total length at r100 and r300; enemy dragons; pearls).
4. A size filter option for the table: `cells<=700` and `cells>700` (cells = w x h of the game record).
Check before trusting the new script: `python3 dn_tab.py m3b7qk_vh m5es_vh` (after scanning `m5es_vh` with `dn_scan.py`) must print the same numbers as `python3 esc_tab.py m3b7qk_vh m5es_vh`
on the rows both have (for example head-ons mate moved / enemy moved = 19 / 2 and 61 / 18, chases 24; 3.5; 9 and 31; 2.3; 7). Also the sum over the new length-by-target cells must equal the mate-moved count. Put both checks in the result file.

## Step 3: counts on the existing arms (no games needed)
Scan `m4qd_vh` (all 58 games) and `m3b7qk_vh` (all games; about 5 minutes each, start them in the background and wait with one bounded `until` loop), then in the result file:
- Table A: `m3b7qk_vh` against `m4qd_vh` on their common games (expected 58: seed 1 of the 29 maps `m4qd_vh` has). Say the exact number of games.
- Table B: the same for games with cells <= 700.
- Table C: the same for games with cells > 700.
Under each table give the number of games, and under Table A one line per small-map game (cells <= 700): game, who won in each arm, own dragons at r100 in each arm, round the queen died in each arm.

## Step 4: counts on the new arm
Wait for the 8 games (`ls ~/meow-redteam/solo/runs/m5dn_vh/*/result.txt | wc -l` reaches 8; one bounded `until` loop with a 60-minute limit; if the limit passes, report what finished and use those). Then scan `m5dn_vh` and write:
- Table D: `m3b7qk_vh`, `m4qd_vh`, `m5dn_vh` on the 8 games all three have (three columns, same rows as Table A).
- Table E: the same for the two `sqheld_open_small_90012` games only.
- Per game: winner, rounds, own dragons at r100 and r300, round and kind of our queen's death, for the three arms.
- List 1: every mate-moved head-on of `m5dn_vh` within 5 tiles of our queen: game, round, mate id / `L0` / tile it stood on (x,y), enemy id / length / tile, `qsteps`, `qtiles`, our queen's tile. Mark the ones the baseline rule would not allow
  (baseline: a mate of 4 or less rams only a head at least as long as itself; so mark rows where the enemy is shorter than the mate's `L0`).
- List 2: every chase of our queen in `m5dn_vh`: game, first and last round, turns, pursuer ids and lengths, mates within 5 tiles at the first turn, how it ended (pursuer rammed by a mate / queen rammed / pursuer left).

## Output
One file: `data/codex/out-escort-counts.md`, in English, tables in GitHub markdown, the checks of step 2 first, then Tables A to E and the lists.
State for every table the number of games behind it. No interpretation, no recommendation. Last line of the file: `DONE <date time>`.
