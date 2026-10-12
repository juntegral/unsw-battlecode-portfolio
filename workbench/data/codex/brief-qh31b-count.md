# Brief: behaviour counts for card #31 queen-hunt with the portal rule (online replays)

Read-only counting with a clear spec. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/qh31b-analysis/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone.

## Replays (each folder holds `game-*.json` and replay files; we are team id 1119)
- Live bot (submission 17184): `data/online/smoke/qh31b-test-old/` (30 games vs test4 and WeHaveQuizzes) and `data/online/smoke/qh31b-dev1-old/` (15 games vs dev1).
- New bot (live + QH_SCOUT with the portal rule): `data/online/smoke/qh31b-test-new/` (30 games) and `data/online/smoke/qh31b-dev1-new/` (15 games).
QH_SCOUT: the first small dragon (length 4 or less, not our queen, not our leader) that sees the enemy queen hunts her and sends a sonar "ping" (hunter id + her cell) every turn; small dragons also hunt once our queen is dead and the round is 100+. New in this version: a hunter takes a portal only when her last seen position is clearly closer to the tile on the other side.

## Reference code (already hand-checked on this replay format; reuse it)
`data/online/smoke/qh31-analysis/qh31_count.py` (parsing, sides, queen ids, death causes, head-on pairing, ping decoding, exposure) and `data/online/smoke/tc30-analysis/count.py`. The earlier run's numbers for comparison are in `data/online/smoke/qh31-analysis/summary.txt`.

## Count, live vs new, split by opponent set (test4 + WeHaveQuizzes / dev1)
1. Their queen: games in which she died, median round, cause (head-on with one of our dragons and that dragon's length, wall, her own body, another body, other).
2. Head-on kills of their queen by one of our dragons of length 4 or less; in the new half, how many of those killers were pinging in the 3 rounds before.
3. Our queen: games in which she died, median round, died before round 100, cause.
4. New half: number of our dragons that sent pings, split into first ping before / after our queen's death; for each, rounds spent pinging (median, and how many pinged 1-3, 4-10, 11-30, 31+ rounds) and the closest it came to her while pinging (3 cells or fewer, 4-8, 9-15, 16+).
5. Portal use, the point of this version: for dragons while they are pinging, how many portal jumps they made in total and per game, and the same number for the Portals map alone. If the replay marks a portal move, use that; otherwise detect a jump as a head move of more than one step's reach between two cells joined by a portal link. Give the same count from the earlier run's new half (`data/online/smoke/qh31-test-new/`) so the two versions can be compared.
6. End state: only our queen alive / only theirs / both / neither.
7. Context only: wins and mean final score, ours and theirs.

## Checks
Print raw events for one counted portal jump by a pinging dragon in the earlier run and (if any exists) one in the new run, and confirm by hand. Sample sizes next to every number. Do not interpret; count.

## Output (write `summary.md` last)
`data/online/smoke/qh31b-analysis/count.py` and `summary.md`: tables for items 1-7, the list of small-dragon kills of their queen (half, opponent, map, round, killer length, was it pinging), the hand-checks, and what could not be measured.
