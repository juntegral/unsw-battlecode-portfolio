# Brief: behaviour counts, v36 against the new main (online replays)

Read-only counting. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/m39-analysis/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone. Do not interpret; count.

Repeat `data/online/smoke/qs39b-analysis/count.py` (read it and its `summary.md`; keep every definition, items 1 to 10) on these variants, same opponents and maps:
- "v36" (v31 + queen-dead-end): `data/online/smoke/qd36c-test-new/` (30 games vs test4 and WeHaveQuizzes), `data/online/smoke/qd36c-dev1-new/` (15 vs dev1). Code `data/online/smoke/qd36c-bot/main.cpp`.
- "new main" (v36 + tail-on-portal ping + queen-safety third build): `data/online/smoke/m39-test-new/` (30), `data/online/smoke/m39-dev1-new/` (15). Code `data/online/smoke/qs39d-bot/main.cpp` (`QUEEN_SAFETY`, `SN_TAIL_MOUTH`). The third build adds: tiles an enemy dragon of length 3 or more can reach by paying length count as dangerous for our queen; she risks them only if she cannot split off a small dragon and the enemy could hit other tiles for free; and when every tile including her own is high risk she stays and splits off a child of (queen length - 2) instead of 2.
- "v36 + queen-safety second build" (partial): `data/online/smoke/qs39c-dev1-new/` (15 vs dev1) and `data/online/smoke/qs39c-test-new/` (15 vs test4 only; say how many games you found).

Tables with the variants side by side, split by opponent set and per opponent (test4, WeHaveQuizzes, dev1). Add:
11. Per variant: how often our queen split (rounds in which our dragon count rose while the queen's length fell), the size of the child at each split (2, or queen length - 2, other), and what happened to the queen within 3 rounds after a split (alive, rammed, other death).
12. Per variant and opponent: games we ended on score 0, and in those games the round and cause of our queen's death.
13. Per variant and opponent: the enemy's final score split into queen length and the rest if the replay allows it; if not, say so.

Checks: print raw events for one counted split per variant and confirm by hand.

Output (write `summary.md` last): `data/online/smoke/m39-analysis/count.py` and `summary.md` with the tables, the hand-checks, and what could not be measured.
