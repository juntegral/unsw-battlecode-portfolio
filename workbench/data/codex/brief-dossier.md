# Behaviour dossier: both sides in every ladder game, by layout

Read-only counts from replays. Do not edit existing files, call no model, post nowhere, no server calls.
Write only inside `data/analysis/ladder/dossier/`.
Inputs: `data/analysis/ladder/rows.jsonl` (use `our_code == "main"`, every game), `data/analysis/ladder/maps.json`,
the ladder replays under `data/online/`, and the earlier replay passes whose parsing, path-distance and view code you
should reuse: `data/analysis/ladder/losses/work/eg_*.py`, `data/analysis/ladder/losses/counts/`, `.../split/`.
"Ours" is team meow, "theirs" the opponent in the same game. A dragon sees the 7x7 box round its head. Path steps =
shortest walk on open tiles, walls and portals respected, bodies ignored.

## Per game and side, in four phases (rounds 0-50, 51-100, 101-200, 201-300)
1. Economy: pearls eaten, splits, dragons alive and total length at the phase end.
2. Deaths by cause: head-on as the mover, head-on as the one hit, wall, own body, another body, no action.
3. Exploring: share of the board the side has seen by the phase end; on turns that start with no pearl in the
   dragon's view: share where the first step keeps the previous turn's direction, share where the step lands on one
   of that dragon's own last 12 tiles ("dither"), and distinct tiles visited per dragon per 20 rounds.
4. Pearls: of pearls born in the phase, the share born within 6 path steps of the side's nearest head, the share
   each side ate, and rounds from birth to being eaten; share of turns with a pearl on an open neighbouring tile
   that is not eaten; share of the side's turn starts on or next to a tile that had already spawned 2 or more
   pearls ("hot tile").
5. Portals: steps through a portal per game; pearls born in rooms reachable only through a portal and who ate them.
6. Contact: first round an enemy head is in view of the side; head-on trades by round 100 and the net length each
   side lost in them; share of the side's heads in the enemy half of the map at rounds 50 and 100.
7. Queen: death round and cause; her length at rounds 50, 100, 200.
Also per game: layout key, cells, starting dragons and their lengths, opponent rating, our side, result, how it ended.

## Tables for `summary.md` (90 lines or fewer, numbers only, no advice)
A. One row per layout (19 rows): games, our wins, and ours against theirs for: pearls by r50 and r100, dragons at
   r100, dither share r0-100, keeps-direction share r0-100, board seen by r100, hot-tile share r0-100, portal steps,
   head-on net length by r100, queen dead by r100.
B. The same columns for all layouts pooled, split by opponent rating (under 1900, 1900-2099, 2100+).
C. For the four layouts where we win least (Islands, Stripes, Australia, Tower Defense, each on its own): every
   measure of sections 1 to 7 for rounds 0-100 and 101-300, ours against theirs, sorted by the size of the gap,
   with the same measure on the 15 other layouts pooled next to it.
D. Inside each layout (so the layout does not explain it): our dither share r0-100 in the games we won against the
   games we lost, and the same for board seen by r100 and pearls by r50. Then the pooled within-layout correlation
   of our dither share r0-100 with our pearls by r100.
Definitions and limits at the end. `per-game.jsonl` (one row per game and side), the scripts, and `last.txt`
written LAST (5 lines or fewer, with the check that reconstructed final standings match rows.jsonl for every game used).
