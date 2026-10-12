# Brief: fountain counts, second pass with real respawn ranges

Read-only counting. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/fountain-analysis-2/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone. Do not interpret; count.

The first pass (`data/codex/brief-fountain-count.md`, output `data/online/smoke/fountain-analysis/`) could not tell fountain tiles apart because the server replays carry `TILE x y 0 0`. Reuse its `count.py` (file reading, sides, eats from `tileChange`, deaths). This pass gets the respawn ranges from elsewhere.

A. Maps with a local copy that has real ranges:
- Australia: map header inside `~/01. Project/개인 프로젝트/battlecode/work/ab2/MB61_australia_3000_0.replay`
- Around UNSW: map header inside `~/01. Project/개인 프로젝트/battlecode/work/ab2/MB61_around_unsw_3000_0.replay`
- Schooltime, Devil, Trophy, Trauma, Queen Of Spades, Default: `~/01. Project/개인 프로젝트/battlecode/maps/` (`schooltime.map`, `devil.map`, `trophy.map`, `trauma.map`, `queen_of_spades.map`, `default.map`)
Before using a local copy, check it is the same map as in the server replay: width, height, edges or walls, and the starting dragons. Report the check per map. If it differs, do not use it and say so.

B. Maps without a local copy (Islands, Slithery Fight and the rest): estimate from the server replays themselves. For each tile, collect the intervals between a pearl leaving the tile and the next pearl appearing there, over all 105 games' games on that map. Call it "fountain (observed)" when it has at least 5 such intervals and their median is 12 rounds or less. Keep these results in separate tables marked as observed, and run the same estimate on the maps of group A so the two methods can be compared (how many true fountain tiles the estimate finds, how many it adds).

A "fountain" in group A is a tile with 1 <= maxGap <= 12.

For every map with a fountain set, and pooled for the big maps (Australia, Around UNSW, Schooltime, Islands, Slithery Fight) with group A and group B kept apart:
1. Map facts: spawning tiles, fountain tiles by (minGap, maxGap) class, expected pearls per round from fountains and from the other spawning tiles if every pearl were eaten at once, and the fountain share.
2. Pearls eaten per game by us and by them on fountain tiles and on other tiles, in r1-50, r51-100, r101-200, r201-end, with each side's share of the fountain pearls.
3. How long a fountain pearl sat before it was eaten (mean, median), and who ate it.
4. Per window, the mean number of our heads and of their heads within 3 tiles (Chebyshev) of any fountain tile, and the first round each side has a head that close.
5. Manhattan distance from each side's starting dragons to the nearest fountain tile.

Checks: three hand-checked fountain eats (ours, theirs, one that sat more than 5 rounds), as in the first pass.

Output (write `summary.md` last): `count.py` and `summary.md` in the folder above, pooled big-map tables first, then per map, then the local-copy checks, the comparison of the two methods, the hand-checks and what could not be measured.
