# Brief: behaviour counts for card #39 queen-safety, second build, and card #36 on the new live bot (online replays)

Read-only counting. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/qs39b-analysis/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone. Do not interpret; count.

This repeats `data/online/smoke/qs39-analysis/count.py` (read it and its `summary.md`; keep every definition, items 1 to 8) on three variants that share the same opponents and maps:
- "v31 live" (main + queen-hunt): `data/online/smoke/qh31d-test-new/` (30 games vs test4 and WeHaveQuizzes), `data/online/smoke/qh31d-dev1-new/` (15 vs dev1), plus any finished live-only runs whose state files are `data/online/smoke/bl-v31-dev1.json` and `data/online/smoke/bl-v31-test.json` (use the download folder of their `old` half if the games are there; say how many games you found).
- "v31 + queen-safety, second build": `data/online/smoke/qs39b-test-new/` (30), `data/online/smoke/qs39b-dev1-new/` (15). The second build adds, on the author's request: when our queen is trapped and every move or sprint leads to a collision she falls back to the normal dragon logic; and the enemy queen is no longer treated as a big threat by our queen but like any enemy dragon. Code: `data/online/smoke/qs39b-bot/main.cpp` (`QUEEN_SAFETY`).
- "v31 + queen-dead-end": `data/online/smoke/qd36c-test-new/` (30), `data/online/smoke/qd36c-dev1-new/` (15). Code: `data/online/smoke/qd36c-bot/main.cpp` (`QUEEN_DEAD_END`).

Give every table with the three variants side by side, split by opponent set and, for the normal set, per opponent (test4, WeHaveQuizzes). Add two items:
9. Per variant and opponent: games in which their queen died, games we won, and games we won with their queen alive at the end.
10. For our queen's deaths before round 100: cause, and how many had an enemy head within 2 cells of her head at the start of her last own turn.

Checks: print raw events for one counted "ended next to an enemy head" turn per variant and confirm by hand.

Output (write `summary.md` last): `data/online/smoke/qs39b-analysis/count.py` and `summary.md` with the tables, the hand-checks, and what could not be measured.
