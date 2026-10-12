# Brief: behaviour counts for card #36 queen-dead-end (online replays)

Read-only counting with a clear spec. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/qd36-analysis/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone. Do not interpret; count.

## Replays (each folder holds `game-*.json` and replay files; we are team id 1119)
- Live bot (submission 17594, main with queen-wait): `data/online/smoke/qw37-test2-new/` (30 games vs test4 and WeHaveQuizzes) and `data/online/smoke/qw37-dev1-new/` (15 games vs dev1). Call this "live".
- New bot (live + QUEEN_DEAD_END): `data/online/smoke/qd36-test-new/` (30 games, same opponents and maps) and `data/online/smoke/qd36-dev1-new/` (15 games).
QUEEN_DEAD_END (the author's words): our queen (dragon id 0 or 1) pays a 6000 penalty for a dead end; a space with room below her length + 8 counts as too tight; the room is counted over tiles she has seen only, so unseen tiles do not make a dead end look bigger; the check still runs when her tail is out of sight. Code: `data/online/smoke/qd36-bot/main.cpp` (`QUEEN_DEAD_END`, `QUEEN_DEAD_PENALTY`, `QUEEN_ROOM`).

## Reference code (hand-checked on this replay format; reuse the parsing)
`data/online/smoke/qw37-analysis/count.py` and `data/online/smoke/kg34b-analysis/count.py` (sides, queen ids, death causes, lengths per round, splits). "Room" below = flood fill from her head over free cells at the start of her turn, bodies and walls block, portals are not passed, stop at 60 (so 60 means 60 or more).

## Count, live vs new, split by opponent set, sample size next to every number
1. Our queen: games in which she died; median round; died in rounds 0 to 5, 6 to 99, 100 to 200, after 200; cause (rammed head-on by an enemy and its length, wall, her own body, one of our bodies, an enemy body, other).
2. Boxed-in deaths: deaths where, at the start of her last turn, she had no free neighbour cell, or her room was below her length + 2. Count, and what closed the space (walls only, her own body, a team-mate's body or head, an enemy body). List them (opponent, map, round, her length, room, what closed it).
3. Tight spaces: share of her alive rounds with room below length + 2, below length + 8, below 12. Number of entries per game (her room goes from length + 8 or more to below length + 8 on her own move), and for each entry: did she leave within 10 rounds, did she die within 20 rounds. Totals per variant.
4. Did she get more timid: different cells her head visited per 25 rounds (mean over rounds 0 to 99 and 100 to 299), path distance from her start cell at rounds 50 and 100, and her length at rounds 50, 100, 200 and at the end (games where she is alive at that round).
5. Pearls she ate: length gained by eating per 100 alive rounds, rounds 0 to 99 and 100 to 299.
6. Queen splits: number per game and the sizes given away (2 cells, more), by round band 0 to 5, 6 to 99, 100+.
7. Per opponent and map, live against new: result, our and their final score, the round our queen died and the cause; mark games where our final score is 0.
8. End state: only our queen alive / only theirs / both / neither.
9. Context only: wins and mean final score, ours and theirs.

## Checks
Print raw events for two counted boxed-in deaths (one per variant if they exist) and one entry into a tight space that she left again, and confirm them by hand.

## Output (write `summary.md` last)
`data/online/smoke/qd36-analysis/count.py` and `summary.md`: tables for items 1 to 6, 8 and 9 per opponent set, the per-map table (item 7), the list for item 2, the hand-checks, and what could not be measured.
