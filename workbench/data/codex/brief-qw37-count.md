# Brief: behaviour counts for PR #37 queen-wait (card #25), online replays

Read-only counting with a clear spec. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/qw37-analysis/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone. Do not interpret; count.

## Replays (each folder holds `game-*.json` and replay files; we are team id 1119)
- Live bot (submission 17184): `data/online/smoke/qh31b-test-old/` (30 games vs test4 and WeHaveQuizzes) and `data/online/smoke/qh31b-dev1-old/` (15 games vs dev1).
- New bot (live + QUEEN_WAIT, now merged to main): `data/online/smoke/qw37-test2-new/` (30 games, same opponents and maps) and `data/online/smoke/qw37-dev1-new/` (15 games).
QUEEN_WAIT: when our real queen (dragon id 0 or 1) is at least 4 long and stuck (no enterable move, or her chosen move does not reach her tail and has room below length + 2), she splits 2 cells off her tail instead of moving, so her head stays where it is. Before, a stuck queen split off length − 2 in one go and was left 2 long. The switch code is in `data/online/smoke/qw37-bot/main.cpp` (`QUEEN_WAIT`, `QW_`).

## Reference code (hand-checked on this replay format; reuse it)
`data/online/smoke/kg34b-analysis/count.py` (sides, queen ids, death causes, head-on pairing, lengths per round) and its `summary.md` for the layout.

## Count, live vs new, split by opponent set, sample size next to every number
1. Our queen: games in which she died; median round; died in rounds 0 to 5, 6 to 99, 100 to 200, after 200; cause (rammed head-on by an enemy and its length, wall, her own body, one of our bodies, an enemy body, other).
2. Queen splits: per game, the number of times our queen split, and for each split how many cells she gave away and her length before and after. Totals for "gave away exactly 2" (the wait) and "gave away more" (the old escape split), by round band (0 to 5, 6 to 99, 100+). The same for the live half.
3. For every wait (a 2-cell split): was she alive 5 and 20 rounds later; how many waits in a row; her length when the run of waits ended; did an enemy head stand within 3 cells of her head at the time of the wait.
4. Her length at rounds 50, 100, 200 and at the end (mean and median over games where she is alive at that round, with the number of games).
5. Per map, live against new: result (win or loss), our final score, their final score, the round our queen died and the cause. One row per opponent and map, so the pairs that flipped can be seen. Mark the games where our final score is 0.
6. Slithery Fight alone: the first 10 rounds of our queen in each game (round, length, what she did).
7. End state: only our queen alive / only theirs / both / neither; how the game ended if the replay says (elimination, queen rule, longest dragon).
8. Context only: wins and mean final score, ours and theirs.

## Checks
Print raw events for two counted waits and one queen death in the new half that came within 5 rounds after a wait (if any), and confirm them by hand.

## Output (write `summary.md` last)
`data/online/smoke/qw37-analysis/count.py` and `summary.md`: tables for items 1 to 4, 7 and 8 per opponent set, the per-map table (item 5), the Slithery Fight trace (item 6), the hand-checks, and what could not be measured.
