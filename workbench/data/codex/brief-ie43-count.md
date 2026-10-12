# Brief: behaviour counts, main against main + idle-exit (#43), online replays

Read-only counting. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/ie43-analysis/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone. Do not interpret; count.

Two variants, same opponents and the same 15 maps:
- "main" (v31 + #36 + #42 + #39): `data/online/smoke/m39-test-new/` (30 games vs test4 and WeHaveQuizzes), `data/online/smoke/m39-dev1-new/` (15 vs dev1). Played 6 Oct about 07:30 KST.
- "main + idle-exit" (the same bot with `IDLE_EXIT` on): `data/online/smoke/ie43-dev1-new/` (15 vs dev1) only. Played 6 Oct 15:52 KST. Code `data/online/smoke/ie43-bot/main.cpp` (`IDLE_EXIT`, `idle_exit_target()`). The 30 games against test4 and WeHaveQuizzes were not played, so for that opponent set report "main" alone and say the other side is missing.
Say how many games you found in each folder.

Definitions come from `~/meow-cards/card-43/work/card_43_check.py` (read it; keep its meaning of "stuck turn", "explored edge", "toward the edge", the round 150 limit and the queen being dragon 0 or 1 of our team). That script reads local `.replay` files. These folders hold the server's `game-<id>.json` replays, which `data/online/smoke/qs39b-analysis/count.py` already reads: take the file format, which side is ours, and the death-cause rules from there.

Tables with the two variants side by side, split by opponent set (test4 + WeHaveQuizzes; dev1), per opponent, and one extra row set for the map Tower Defense alone:
1. Stuck turns up to round 150 and the share whose first step goes toward the edge; the same for all rounds, raw.
2. Stuck spells started by round 150: count, mean length in turns, longest, spells of 30 turns or more.
3. Share of the map our non-queen dragons have seen by round 50, 100 and 150.
4. Turns on which our non-queen dragons grew by round 150, per game.
5. Deaths of our non-queen dragons per game, by cause (head-on, wall, enemy body, own body, other), up to round 150 and over the whole game.
6. Our queen: deaths, round of death, final length; games we ended on score 0.
7. Parking next to a pearl: turns up to round 150 where one of our non-queen dragons has not grown for 20 rounds, remembers a pearl within 6 steps, and its step does not bring it closer to any remembered pearl. Count the turns, the spells, and the spells of 10 turns or more.
8. Wins, our final score and their final score per opponent, from the result in each replay.

Checks: for each variant print the raw events of one counted stuck spell and one counted parking spell and confirm them by hand.

Output (write `summary.md` last): `data/online/smoke/ie43-analysis/count.py` and `summary.md` with the tables, the hand-checks, and what could not be measured.
