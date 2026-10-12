# v62 + card 55 attempt 3 against the queen hunter: queen tables only (mechanical; the games are already played)

Replays: `~/meow-redteam/solo/runs/<arm>/<map>-seed<S>-side<K>/game.replay` (+ `result.txt`). Scripts by an earlier builder, read-only:
`~/meow-redteam/solo/src/w-depth/qh_counts.py`, `qh_table.py` (read them and `~/meow-redteam/solo/src/w-depth/counts.md` for usage
and for the exact rows). You may not write outside this repo: copy the scripts to `data/codex/tmp-qf3/` and run them there
(adjust output paths only; do not change what they count).

Arms, all against the same opponent (`m3hunt`, team main + queen hunting), on the 16 games that all of them share
(8 map-seeds, both sides; the list is the folder names of `runs/m5q3_vh`):
- `m3b7qk_vh` = the live build (v62 switches)
- `m5q3_vh` = the live build + QUEEN_FALLBACK (card 55, attempt 3)
- `m4qf_vh` = the live build + QUEEN_FALLBACK as of attempt 2 (only if it has all 16 games; otherwise leave the column out and say so)
- `m5qh2_vh` = the live build + QUEEN_HERD (another candidate, for reference)

Table: every row of the two-arm table in `w-depth/counts.md` (depth rank, own heads within 3 and 5, turns with no mate within 5,
enemy head within 3 steps per 100 turns, chases a game / no mate at start / turns each, queen alive r100 / r150 / end,
rammed / boxed / dead end / into a head, pearls she eats, tiles from start, own dragons r100 / r300, total length r100 / r300),
one column per arm. Under it: the number of games per arm, any game missing or failed, the round at which each `m5q3_vh` game
first differs from the baseline game (the builder's script prints this), and each game's result per arm as a plain list.
Then a second small table for `m5q3_vh` only, from the replays: on her turns that start with more enemy heads than own heads
inside her 7 by 7 view (count her own head as one of ours), how many there were, and what she did (stepped away from the nearest
enemy head / toward it / toward the nearest mate / stayed level), next to the same counts for `m3b7qk_vh`.
Write to `data/codex/out-qf3.md` with a 5-line plain summary of what changed and what did not. Numbers only from the replays,
no opinion. No network, no games, no compiling.
