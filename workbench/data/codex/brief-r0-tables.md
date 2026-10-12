# Round-0 split alone: table only (mechanical; the games are already played)

Same method as `data/codex/brief-open-guard-tables.md` (read it; reuse `data/codex/tmp-open/` with the builder's `op_scan.py` and `op_tab.py`).
One table on the 16 games all four arms share (8 maps, seed 1, both sides, opponent plain main), every row of
`~/meow-redteam/solo/src/w-open/op_table_pack.txt`:
`m4bq_vb` (baseline, the live build) | `m5r0_vb` (baseline + SPLIT_ROUND0 only) | `m5og_vb` (SPLIT_ROUND0 + QS_KEEP_ROUND 40 + QS_KEEP_CLEAR 6) | `m5op_vb` (that without the guard, plus HEADING_TIE).
Under it: games per arm, anything missing or failed, each game's result per arm as a plain list.
Write to `data/codex/out-r0.md` with a 4-line plain summary (which rows move with SPLIT_ROUND0 alone and which only with the queen
rule). Numbers only from the replays, no opinion. No network, no games, no compiling.
