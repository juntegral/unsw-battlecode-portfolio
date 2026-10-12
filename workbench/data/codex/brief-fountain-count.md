# Brief: who eats at the fountains on the big maps (online replays)

Read-only counting. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/fountain-analysis/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone. Do not interpret; count.

Games: our team 1119 against team 946 (Big Bobs Bots) on 6 Oct, 105 games in seven folders under `data/online/smoke/`: `ie43-bob1-old`, `ie43-bob2-old`, `ie43-bob1-new`, `ie43-bob2-new`, `main-bob1-new`, `nd36-bob1-new`, `ns39-bob1-new` (15 games each, one per map). `data/online/smoke/bbb-analysis/count.py` already reads these files (game JSON for result and side, `M<id>.replay` for events): take the format, which side is ours and the death rules from there. Pool all seven folders; our bot variants differ only in queen rules and one idle rule.

A tile's pearl respawn range is in the replay's map header as `TILE x y minGap maxGap` (maxGap 0 = never spawns). Call a tile a "fountain" when 1 <= maxGap <= 12. Call the rest of the spawning tiles "slow".

For each of the 15 maps, and pooled for the five largest (Australia, Around UNSW, Schooltime, Islands, Slithery Fight) against the other ten:
1. Map facts: tiles, spawning tiles, fountain tiles with their (minGap, maxGap) classes and counts, the expected pearls per round from fountains and from slow tiles if every pearl were eaten at once (sum of 1 / mean gap), and the fountain share of that.
2. Pearls eaten per game by us and by them, split into fountain tiles and slow tiles, in the windows r1-50, r51-100, r101-200, r201-end. Give counts and each side's share of all fountain pearls eaten.
3. Fountain pearls that sat uneaten: for each fountain tile, rounds it held a pearl before it was eaten (mean and median), and by whom it was then eaten.
4. Presence: per window, the mean number of our dragons and of their dragons whose head is within 3 tiles (Chebyshev) of any fountain tile; and the first round each side has a head within 3 tiles of a fountain.
5. Distance at birth: for each side, the path-free Manhattan distance from each team's two starting dragons to the nearest fountain tile.
6. Dragons alive at r50, r100, r200, r300 for both sides, and deaths of our dragons by cause in the same four windows (head-on, wall, enemy body, own body, other).
If the replay does not record pearl spawns or eats directly, derive eats from a dragon's length growing on a step onto a tile, say exactly how, and check it by hand on one game.

Checks: print the raw events of three counted fountain eats (one ours, one theirs, one where the pearl sat more than 5 rounds) and confirm by hand.

Output (write `summary.md` last): `data/online/smoke/fountain-analysis/count.py` and `summary.md`, pooled big-map tables first, then per map, then the hand-checks and what could not be measured.
