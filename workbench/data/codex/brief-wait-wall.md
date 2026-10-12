# Brief: trace one queen who waited (split 2 off her tail) and then ran into a wall

Read-only. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/wait-wall-analysis/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`.

## The question (from a teammate who watched the replay)
"The queen spawns mini dragons without moving for a few rounds, then for some reason she just ran into the wall, even though she was still pretty long and had plenty of space to spawn more." He wants to know why.

## Replay
`~/meow-loop-out/card-36/attempt-2/replays/candidate_sq_blobs_large_10038_13601_1.replay` (local game; first team = base bot, queen is dragon 0; second team = base + QUEEN_DEAD_END, queen is dragon 1). Both sides have QUEEN_WAIT on: when the real queen (id 0 or 1) is at least 4 long (`QW_MIN_LENGTH`) and stuck (no enterable move, or her chosen move does not reach her tail and has room below length + 2), she splits 2 cells off her tail instead of moving. Code for the candidate side: `data/online/smoke/qd36-bot/main.cpp` (search `QUEEN_WAIT`, `QW_`, `queen_wait`, and the dead-end code `QUEEN_DEAD_END`, `QUEEN_ROOM`, `QUEEN_DEAD_PENALTY`); base side: `data/online/smoke/bl17594-bot/main.cpp`.

## Reference code
`data/online/smoke/qw37-analysis/count.py` and `data/online/smoke/qd36-analysis/count.py` parse this replay format (sides, queen ids, splits with sizes, deaths and causes, lengths per round, flood-fill room).

## Do
1. For each of the two queens, list every run of consecutive 2-cell splits (round range, her length before and after the run) and her death (round, cause, her length).
2. Find the queen that matches the teammate's description: a run of waits followed within a few rounds by a death into a wall while she was still 4 or longer. For her, write a round-by-round table from 3 rounds before the run starts to her death: round, her length, head cell, what she did (move direction, split 2, other), the 4 neighbouring cells of her head and what is on each (free, wall or kelp edge, her own body, team-mate body or head, enemy body or head, pearl), her room by flood fill, and the nearest enemy head with its distance and length.
3. From the code, say which rule most plausibly made her last move: quote the lines (with line numbers) that decide between waiting and moving, and check each condition against the table for her last two turns (her length against `QW_MIN_LENGTH`, whether a move was enterable, room against length + 2, whether the move reaches her tail, any stop condition such as an enemy near, a round limit, a pearl in reach, a cap on waits). Say plainly what is measured from the replay and what is inferred from the code. If two explanations fit, give both.

## Output (write `summary.md` last)
`data/online/smoke/wait-wall-analysis/summary.md`: which queen and rounds, the round-by-round table, the code lines, the explanation in 5 lines or fewer of plain English, and what could not be determined without bot logs.
