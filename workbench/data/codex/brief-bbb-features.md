# Brief: per-feature behaviour counts, v31 against main + idle-exit, vs Big Bobs Bots (online replays)

Read-only counting. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/bbb-analysis/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone. Do not interpret; count.

Two variants against the same opponent (team 946, Big Bobs Bots) on the same 15 maps, played back to back in two passes on 6 Oct (17:00 and 18:10 KST):
- "v31": `data/online/smoke/ie43-bob1-old/` and `data/online/smoke/ie43-bob2-old/` (15 games each). Code: `~/meow-cards/card-31/mybot2/main.cpp`.
- "main + idle-exit": `data/online/smoke/ie43-bob1-new/` and `data/online/smoke/ie43-bob2-new/` (15 games each). Code: `data/online/smoke/ie43-bot/main.cpp`. It is v31 with four switches added: `QUEEN_DEAD_END` (card #36), `SN_TAIL_MOUTH` (#42), `QUEEN_SAFETY` (#39) and `IDLE_EXIT` (#43).
Say how many games you found in each folder. If a folder has fewer than 15, count what is there and say so.

Each feature has a check script that defines what to count. They read local `.replay` files; these folders hold the server's `game-<id>.json` replays. `data/online/smoke/ie43-analysis/count.py` (already ported for #43) and `data/online/smoke/qs39b-analysis/count.py` and `data/online/smoke/m39-analysis/count.py` read the server format: take the file format, which side is ours (team 1119), and the death-cause rules from those. Keep each check script's own definitions.

Tables with the two variants side by side: pooled (30 against 30), per pass, and per map for the pooled set.

A. Card #36, definitions from `~/01. Project/개인 프로젝트/battlecode/work/card_36_check.py`: queen moves in total; queen moves whose step fails the "known room" rule (does not surely fit), count and share; the same when a step that does fit was available; queen deaths with the queen boxed in at her last turn; queen wall deaths.
B. Card #39, definitions from `~/01. Project/개인 프로젝트/battlecode/work/card_39_check.py`: queen turns ending inside the free-hit zone of a visible enemy head, and inside the pay ring, count and share of queen turns; the same when a tile outside both was available; queen deaths by head-on, with the attacker's length and its distance at the start of that round; queen splits (count, child size 2 / queen length minus 2 / other) and the queen's fate within 3 rounds after a split (alive, rammed, other death).
C. Card #42, definitions from `~/01. Project/개인 프로젝트/battlecode/work/card_42_check.py`: chances (a tail tip on a portal opening a teammate could come through), per game; deaths of our dragons whose head came through a portal onto a teammate's tail tile, per game; all deaths of our dragons right after a portal step, per game.
D. Card #43, exactly items 1, 2, 3, 4 and 7 of `data/codex/brief-ie43-count.md` (reuse `data/online/smoke/ie43-analysis/count.py`).
E. Overall: wins; our and their final score; how the game ended (longest dragon, elimination, queen rule, total length, draw); our queen alive at the end, round of death (median and list), final length; games we ended on score 0; deaths of our non-queen dragons per game by cause (head-on, wall, enemy body, own body, other) up to round 150 and over the whole game; turns our non-queen dragons grew, up to round 150 and over the whole game; number of our dragons alive at rounds 50, 100, 200 and 300; the same for the enemy.

Checks: for each of A, B, C and D print the raw events of one counted case per variant and confirm it by hand. If a definition cannot be evaluated from the server replay, say exactly which and why, and leave that row empty rather than approximating.

Output (write `summary.md` last): `data/online/smoke/bbb-analysis/count.py` and `summary.md` with the tables, the hand-checks, and what could not be measured. Put the pooled tables A to E first.

F. The maps Stripes, Trauma and Queen Of Spades (pooled: v31 won 5 of 6, the new bot 0 of 6). For each of the 12 games: the result and how it ended, the round and cause of our queen's death with the attacker's length where it is a head-on, our and their dragon counts at rounds 25, 50 and 100, and the round our last dragon died if we were wiped out. Then for these maps only, tables A to D for the two variants side by side.
