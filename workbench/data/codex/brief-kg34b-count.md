# Brief: behaviour counts for card #34 keep-guards (cap fix), online replays

Read-only counting with a clear spec. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/kg34b-analysis/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone.

## Replays (each folder holds `game-*.json` and replay files; we are team id 1119)
- Live bot (submission 17184): `data/online/smoke/qh31b-test-old/` (30 games vs test4 and WeHaveQuizzes) and `data/online/smoke/qh31b-dev1-old/` (15 games vs dev1).
- New bot (live + KEEP_GUARDS): `data/online/smoke/kg34b-test-new/` (30 games, same opponents and maps) and `data/online/smoke/kg34b-dev1-new/` (15 games).
KEEP_GUARDS: once feeding the queen starts (after round 200), the queen names up to 3 of our dragons near her as guards; they stay a few cells from her instead of feeding in, ram enemy heads that come for her, and feed in during the last 10 rounds. Everyone else feeds as before. Our queen is our dragon with id 0 or 1.

## Reference code (hand-checked on this online replay format; reuse the parsing)
`data/online/smoke/qh31b-analysis/count.py` (sides, queen ids, death causes, head-on pairing, sonar decoding) and `data/online/smoke/qh31-analysis/qh31_count.py`. The definitions below follow the local look note at `~/meow-loop-out/card-34/attempt-2/look.md` (read its "Words used here" section; do not copy its numbers).

## Count, live vs new, split by opponent set (test4 + WeHaveQuizzes / dev1), sample size next to every number
1. Our queen: games in which she died; median round; died before round 100, in rounds 100 to 200, after round 200; cause (rammed head-on by an enemy and that enemy's length, wall, her own body, another body of ours, an enemy body, other).
2. For every death of our queen after round 200: how many of our dragons were within 6 cells of her head at the start of that round and 5 rounds before, and their lengths. List these deaths (half, opponent, map, round, cause, attacker length, ours within 6 cells).
3. Games where our final score is 0: count, and for each the reason visible in the replay (queen dead at the end and in which round she died).
4. Guards there: over rounds after 200 while our queen is alive, the share of rounds with nobody of ours within 6 cells of her head; mean number of ours within 6 cells (capped at 3) and mean number inside the 7x7 square around her head; share of rounds with 4 or more and with 5 or more of ours inside that square. Give it also for rounds 420 to the end.
5. Fed as before: our queen's length at rounds 200, 300, 400 and at the end (mean and median over games where she is alive at that round, with the number of games); number of feeds into our queen after round 200 per game if the replay shows them.
6. Guard rams: our dragons that died head to head on their own move within 8 cells of our queen after round 200: count, their lengths, the enemy's length, and whether our queen was alive 20 rounds later.
7. Enemy approaches: times an enemy head came within 6 cells of our queen's head after round 200 (a new approach after 10 rounds away), and how often she was alive 20 rounds later.
8. Their queen: games in which she died, and her length at the end when alive (mean), for context.
9. End state: only our queen alive / only theirs / both / neither; when both alive, how often ours was longer.
10. Context only: wins and mean final score, ours and theirs.

## Checks
Print the raw events for two counted deaths of our queen after round 200 in the new half and one guard ram, and confirm them by hand. If round 200 is not where feeding starts in the code (`KG_` constants in `data/online/smoke/kg34b-bot/main.cpp`), say what the code uses and keep round 200 for the tables. Do not interpret; count.

## Output (write `summary.md` last)
`data/online/smoke/kg34b-analysis/count.py` and `summary.md`: tables for items 1 to 10 per opponent set, the two lists (item 2, item 3), the hand-checks, and what could not be measured.
