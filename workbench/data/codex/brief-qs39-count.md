# Brief: behaviour counts for card #39 queen-safety (online replays, bot versions v29 and v30)

Read-only counting with a clear spec. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/qs39-analysis/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone. Do not interpret; count.

## Replays (each folder holds `game-*.json` and replay files; we are team id 1119)
- Live bot (v22 main, submission 17594), 90 games: vs test4 and WeHaveQuizzes `data/online/smoke/qw37-test2-new/` and `data/online/smoke/bl17594c-test-new/` (30 + 30); vs dev1 `data/online/smoke/qw37-dev1-new/` (15) and the live-only run `bl-v22-dev1` (15; find its download folder from `data/online/smoke/bl-v22-dev1.json`, the `old` half).
- New bot (v22 main + QUEEN_SAFETY), 45 games: `data/online/smoke/qs39-test-new/` (v30, 30 games vs test4 and WeHaveQuizzes) and `data/online/smoke/qs39-dev1-new/` (v29, 15 games vs dev1).
QUEEN_SAFETY (the author's words): raise our queen's threat multiplier from 1 to 4 and add a huge penalty when her next step is right next to an enemy dragon's head. Our queen is our dragon with id 0 or 1. Code: `data/online/smoke/qs39-bot/main.cpp` (`QUEEN_SAFETY`).

## Reference code (hand-checked on this replay format; reuse the parsing)
`data/online/smoke/qd36-analysis/count.py` (sides, queen ids, death causes, room by flood fill, lengths per round) and `data/online/smoke/kg34b-analysis/count.py` (enemy approaches, head-on pairing).

## Count, live vs new, split by opponent set (test4 + WeHaveQuizzes / dev1) and for the normal set also per opponent; sample size next to every number
1. Our queen: games in which she died; median round; died in rounds 0 to 5, 6 to 99, 100 to 200, after 200; cause (rammed head-on by an enemy and its length, wall, her own body, one of our bodies, an enemy body, other).
2. Turns she ended next to an enemy head: number of her turns that ended on a cell with an enemy head on one of the 4 neighbouring cells, per 1,000 alive rounds; and the same for "within 2 steps" (Manhattan distance 2 or less to any enemy head). For each such turn: was there a move that would have ended with no enemy head within 2 steps (a free neighbouring cell, not a wall or body) and how often was she rammed head-on in the next 2 rounds.
3. Rams on her: for each death by an enemy ram, how far the killer's head was from her head at the start of her last own turn (1, 2, 3, 4+ cells), and whether she moved toward it, away from it or stayed at the same distance on that turn.
4. Did the penalty push her into walls or tight spots instead: deaths by wall or own body within 3 rounds after an enemy head came within 3 cells; boxed-in deaths (no free neighbour or room below length + 2 at her last turn) as in the qd36 count.
5. Did she get more timid: different cells her head visited per 25 rounds (rounds 0 to 99 and 100 to 299), path distance from her start at rounds 50 and 100, length gained by eating per 100 alive rounds (0 to 99, 100 to 299), her length at rounds 100, 200 and at the end.
6. Their queen: games in which she died, for context.
7. End state: only our queen alive / only theirs / both / neither; and wins in games where their queen was alive at the end.
8. Context only: wins and mean final score, ours and theirs.

## Checks
Print raw events for two counted "ended next to an enemy head" turns (one per variant) and one ram death in the new bot's games, and confirm them by hand.

## Output (write `summary.md` last)
`data/online/smoke/qs39-analysis/count.py` and `summary.md`: tables for items 1 to 8, the list of her ram deaths in the new bot's games (opponent, map, round, killer length, distance at her last turn, what she did), the hand-checks, and what could not be measured.
