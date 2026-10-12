# Opening pack, guard arm: tables only (mechanical; the games are already played)

Replays: `~/meow-redteam/solo/runs/<arm>/<map>-seed1-side<K>/game.replay` (+ `result.txt`). Scripts by the builder, read-only:
`~/meow-redteam/solo/src/w-open/op_scan.py` and `op_tab.py` (read them for usage). You may not write outside this repo, so copy the
two scripts to `data/codex/tmp-open/` and run them there (adjust output paths only; do not change what they count).

1. Table A, games shared by all three arms (16 expected; 8 maps, seed 1, both sides, opponent plain main):
   `m4bq_vb` (baseline, the live build) | `m5op_vb` (pack with HEADING_TIE, no guard) | `m5og_vb` (SPLIT_ROUND0 + QS_KEEP_ROUND 40 + QS_KEEP_CLEAR 6).
   Every row of `~/meow-redteam/solo/src/w-open/op_table_pack.txt`.
2. Table B, games shared by both arms (12 expected; 6 maps, seed 1, both sides, opponent the queen hunter):
   `m3b7qk_vh` (baseline) | `m5og_vh`. The same rows, plus one line per queen death in either arm: game, round, her length, cause
   (rammed / boxed in / ran into a head), and whether an enemy head was within 6 tiles when she last split.
3. Under each table: the number of games behind it, any game missing or failed (check `result.txt`), and the win/loss of each game
   for each arm (winner == the arm's side) as a plain list, not a rate.
Write both tables and a 5-line plain summary of what changed and what did not to `data/codex/out-open-guard.md`.
Numbers only from the replays. No opinion on whether to ship. No network, no games, no compiling.
