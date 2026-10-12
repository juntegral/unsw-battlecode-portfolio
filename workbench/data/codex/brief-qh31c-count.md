# Brief: behaviour counts for card #31 queen-hunt, third build (online replays)

Read-only counting with a clear spec. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/qh31c-analysis/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone. Do not interpret; count.

## Replays (each folder holds `game-*.json` and replay files; we are team id 1119)
- Live bot (submission 17184): `data/online/smoke/qh31b-test-old/` (30 games vs test4 and WeHaveQuizzes) and `data/online/smoke/qh31b-dev1-old/` (15 games vs dev1).
- Third build (live + QH_SCOUT): `data/online/smoke/qh31c-test-new/` (30 games, same opponents and maps) and `data/online/smoke/qh31c-dev1b-new/` (15 games).
- Second build, for comparison only: `data/online/smoke/qh31b-test-new/`, `qh31b-dev1-new/`.
QH_SCOUT: the first small dragon (length 4 or less, not our queen, not our leader) that sees the enemy queen hunts her and sends a sonar "ping" (hunter id + her cell) every turn; small dragons also hunt once our queen is dead and the round is 100+. Changed in the third build, on the author's request: (a) hunters no longer stand down when they hear another hunter with a different id, so several can hunt at once; (b) a hunter shut inside an enclosed space while their queen is clearly outside leaves through a portal at once; apart from that and real shortcuts, hunters do not use portals. The code is in `data/online/smoke/qh31c-bot/main.cpp` (`QH_`).

## Reference code (hand-checked on this replay format; reuse it)
`data/online/smoke/qh31b-analysis/count.py` and its `summary.md` (same items 1 to 7 as below were counted for the second build; keep the same definitions so the builds can be compared).

## Count: live, second build, third build; split by opponent set; sample size next to every number
1. Their queen: games in which she died, median round, cause (head-on with one of our dragons and that dragon's length, wall, her own body, another body, other).
2. Head-on kills of their queen by one of our dragons of length 4 or less; how many of those killers were pinging in the 3 rounds before.
3. Our queen: games in which she died, median round, died before round 100, cause.
4. Dragons that sent pings, split into first ping before / after our queen's death; rounds spent pinging (median, and 1-3, 4-10, 11-30, 31+); the closest each came to her while pinging (3 cells or fewer, 4-8, 9-15, 16+).
5. Several hunters at once (new in the third build): per round with at least one ping, how many different dragons of ours pinged; share of such rounds with 1, 2, 3, 4 or more pinging dragons; the largest number seen in a game. Same for the second build.
6. Portal use by pinging dragons: jumps in total and per game, and for the Portals map alone. For each jump in the third build: was the pinging dragon's cell before the jump inside an enclosed area (flood fill over free cells from its head, without using portals, reaches fewer than 40 cells) and was their queen outside that area. Count jumps that fit "shut in, queen outside" against all other jumps.
7. Shut-in hunters that did not leave: pinging dragons that stayed for 10 or more rounds in a row inside such an enclosed area with at least one portal edge on its border while their queen was outside. Count, and list up to 10 (game, map, rounds).
8. End state: only our queen alive / only theirs / both / neither.
9. Context only: wins and mean final score, ours and theirs.

## Checks
Print raw events for one counted jump of each kind in the third build (shut in and other, if they exist) and one round with three or more pinging dragons, and confirm them by hand.

## Output (write `summary.md` last)
`data/online/smoke/qh31c-analysis/count.py` and `summary.md`: tables for items 1 to 9, the list of small-dragon kills of their queen in the third build (opponent, map, round, killer length, was it pinging), the lists for items 6 and 7, the hand-checks, and what could not be measured.
