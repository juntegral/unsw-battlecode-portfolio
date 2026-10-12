# Brief: behaviour counts for card #23 queen-no-trap (online replays)

Read-only measurement. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/qn23-analysis/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone.

## What the card changes
Card #23 adds a switch `QUEEN_NO_TRAP` to our bot (team meow, id 1119): before each step our queen (the dragon with id 0 or 1) checks that she can keep moving from the cell she steps to, and avoids cells she cannot get out of (a pearl in a dead end is not worth it for her); it also guards her splits. Other dragons are unchanged. The idea is to stop the queen from killing herself (wall, her own body, another dragon's body, no valid move).

## Replays (each folder holds `game-*.json` and replay files; we are team id 1119)
New bot (switch on): `data/online/smoke/qn23-test-new/` (45 games: 15 each vs test4, WeHaveQuizzes and dev1).
Live bot (switch off), same opponents and maps: `safer-stride-test-old/`, `passage2-test-old/`, `qh31-test-old/`, `passage-test-old/` (30 games each vs test4 and WeHaveQuizzes) and `tc30-dev1-old/` (15 games vs dev1), all under `data/online/smoke/`.

## Reference code (already hand-checked on these replays)
`data/online/smoke/tc30-analysis/count.py` and `data/online/smoke/qh31-analysis/qh31_count.py` (parsing, sides, queen ids, death causes, head-on pairing, exposure, map size). Replay parser: `~/01. Project/개인 프로젝트/battlecode/replay.py`.

## Count, live vs new, split by opponent set (test4 + WeHaveQuizzes / dev1) and overall
1. Our queen: games in which she died; cause split (head-on with an enemy, wall, her own body, another dragon's body and whose team, no valid move / other); median death round; died before round 100; alive at the end.
2. For each self-inflicted death (anything except a head-on with an enemy): the number of free neighbouring cells she had at the start of that turn, whether an enemy head was within 3 cells, whether she ate a pearl in the 3 rounds before, and whether she split in the round before.
3. For each head-on death: the same pearl question (did she eat within the 3 rounds before), and how many free neighbouring cells out of every visible enemy's reach she had at the start of the turn if you can compute reach the way the bot's rule works (reach per round = ceil(L/4) + (L-2) for a dragon of length L, minimum length 2); if you cannot do this reliably, say so and skip it.
4. Queen growth: her length at rounds 50, 100, 200 (mean over games where she is alive) and pearls she ate before round 100 per game, to see whether avoiding dead ends costs her food.
5. Context only: wins and mean final score, ours and theirs.

## Checks
Before trusting the script, print raw events for two self-inflicted queen deaths (one per group) and one head-on death and confirm the classification by hand. Give sample sizes next to every number. Do not interpret; count.

## Output (write `summary.md` last)
`data/online/smoke/qn23-analysis/count.py` and `summary.md` (tables for items 1-5, the list of self-inflicted deaths with game id, opponent, map, round and the item-2 fields, the hand-checks, and what could not be measured).
