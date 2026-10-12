# Brief: behaviour counts for card #31 queen-hunt rebuilt on the new main (online replays)

Read-only counting. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/qh31d-analysis/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone. Do not interpret; count.

This repeats `data/online/smoke/qh31c-analysis/count.py` (read it and its `summary.md`; keep every definition, items 1 to 9) on two variants:
- "live": submission 17594 (main with queen-wait): `data/online/smoke/qw37-test2-new/` (30 games vs test4 and WeHaveQuizzes) and `data/online/smoke/qw37-dev1-new/` (15 games vs dev1).
- "fourth build": live + QH_SCOUT, the queen-hunt card rebuilt on that main: `data/online/smoke/qh31d-test-new/` (30 games) and `data/online/smoke/qh31d-dev1-new/` (15 games).
Add a third column "third build" by copying the numbers from `data/online/smoke/qh31c-analysis/summary.md` (do not recount it), so the rebuild can be compared with the build the author approved.

One extra item, because the new main changes how our queen behaves when stuck: 10. Our queen's splits per game and the sizes given away (2 cells, more), by round band 0 to 5, 6 to 99, 100+, live against fourth build; and her deaths in rounds 0 to 5.

Checks: print raw events for one small-dragon kill of their queen by a pinging dragon and one round with three or more pinging dragons in the fourth build, and confirm by hand.

Output (write `summary.md` last): `data/online/smoke/qh31d-analysis/count.py` and `summary.md` with the tables for items 1 to 10 per opponent set, the list of small-dragon kills of their queen in the fourth build, the hand-checks, and what could not be measured.
