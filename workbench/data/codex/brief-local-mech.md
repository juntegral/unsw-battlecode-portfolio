# Count two behaviours in local replays, arm by arm

Four builds of our bot ("arms": base, fb, te, both) each play the same opponent on the same maps, seeds and sides.
Replays: `~/meow-redteam/solo/runs/<arm>/<map>-seed<S>-side<K>/game.replay` (+ `result.json`).
`side<K>` is the side OUR bot (the arm) played; the other side is the opponent. Games are still being played while
you write this: your counter must take whatever replays exist when it is run, and be cheap to rerun.
Local replay format: read `~/meow-redteam/tools/show.py` and `~/meow-redteam/docs/`.
Definitions to copy exactly: the ladder scripts in `data/analysis/ladder/dossier/work/` (`isl_zone.py` for skips,
eating and splits; `au_scan.py`, `au_scan2.py`, `au_net.py` for head-on meetings, chances and net length). Those read
ladder replays; port the definitions to the local format, do not change them. Say so wherever you had to.

## Deliverable
`data/analysis/ladder/dossier/local/count_local.py` (run as `python3 count_local.py`, no arguments; optional
`--runs <dir>`), writing next to itself: `rows.jsonl` (one row per game) and `table.md`.

Per game, for our side and theirs (rounds are raw 0-based replay rounds, windows inclusive):
1. map, cells (width x height), seed, side, arm, winner, how it ended, last round.
2. dragons alive at the end of r100, r150, r200, r300, r400 and at the end; longest dragon and total length at r300,
   r400, end; queen (lowest starting id of the side) alive at the end.
3. per window r101-150, r151-200, r201-300, r301-400: pearls eaten, splits, deaths.
4. skip share per window r101-150 and r151-200, as isl_zone.py defines it (non-queen turn that starts beside a pearl
   and eats nothing, no enemy head within 2 tiles).
5. share of rounds 151-400 in which our count is under 56 at the start of the round.
6. cross-team head-on meetings by which side moved, for r0-100, r101-300, r301-499.
7. as au_scan2.py: turns in r101-300 where a short dragon (length 2 to 4, not the queen) starts with an equal or
   longer enemy head in reach and the edge; how many of them are "taken"; split by our count under 59 / 59 or more.
8. as au_net.py: net length from meetings per side, r101-300; and whether a queen died as the mover of a head-on.

`table.md` (80 lines or fewer), in this order:
- A. one row per arm: games, won, and the means of every measure above (ours / theirs).
- B. the same, only games where the BASE arm's game on the same map, seed and side had our count under 56 at r150.
- C. paired against base (same map, seed, side): for fb, te and both, the number of pairs in which the game differs
  from base at all (compare the sequence of our dragon counts per round), and mean paired differences for: pearls and
  splits r151-200, skip share r151-200, dragons alive r200 and r300, longest at end, meetings we start r101-300,
  take rate under 59, net length from meetings, wins.
- D. per pair list, one line each: map, side, arm, result base -> arm, our count r150/r300 base -> arm, longest at end base -> arm.
- Notes: anything you could not port exactly, and games skipped (no replay, crash).

## Rules
Write only under `data/analysis/ladder/dossier/local/`. Do not run games, do not touch the bot sources, no network,
no posts. Test your counter on the replays that exist now and make sure rerunning it later just works.
Write `data/analysis/ladder/dossier/local/done.txt` (one line) as the very last step.
