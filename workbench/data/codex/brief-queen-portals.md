# Brief: does a queen that uses portals do better or worse, by map size? (count from existing replays)

Read-only counting. Work in this repository (unsw-swarm). Write only inside `data/analysis/queen-portals/`. No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone. Do not interpret; count, and say what could not be measured.

## The question (from the team chat, 5 Oct)
Zhe: our queen went through a portal to the other side and that should be stopped. QWQ: hard to fix, and on small maps the game ends in elimination anyway, so a queen that does not cross or use the portal loses anyway. Zhe: "can we try testing a bunch of different maps to see at what map size the queen stops needing portals to be useful".
We already hold thousands of replays, so count there first.

## Data
- Ladder replays used by the top-team study: find their location and the parser from `data/analysis/top1/lib.py` and the study scripts listed in `data/analysis/top1/REPORT.md` section 8 (2,343 games: the top three teams and ours, with their opponents). Use every game in which the map has at least one portal. Count every queen in those games (both teams), and tag each as ours (team 1119 "meow"), top three (Vibing++, SSS, forgot to mention), or other.
- Today's online games of our live bot, same replay format: `data/online/smoke/qh31b-test-old/`, `qh31b-dev1-old/` (45 games). Portal-jump detection that was hand-checked on this format is in `data/online/smoke/qh31b-analysis/count.py` (a head move longer than one turn's reach between two cells joined by the same portal label); reuse it. The queen is the dragon with id 0 or 1.

## Count
For each map: name, cells (width x height, and free cells if easy), number of portals. Put maps in size groups by cells: up to 600, 601 to 1,200, 1,201 to 2,400, over 2,400 (and list the maps in each group).

Per size group and per team tag (ours / top three / other), with the number of games next to every number:
1. Share of queen-games in which the queen made at least one portal jump; jumps per game; round of her first jump (median).
2. How those games ended (elimination, queen rule, longest dragon, total length), for queens that jumped and for queens that never jumped.
3. Win rate of the queen's team, jumped against never jumped. Also the same restricted to games where she was alive at round 100 (so an early death does not hide inside "never jumped").
4. Her fate: alive at the end; died within 10 rounds after a jump, within 30; cause of those deaths (rammed head-on by an enemy, wall, own body, team body, other) and how far the landing cell was from the nearest enemy head at the moment of the jump (0-3, 4-8, 9+ cells; "not seen" if no enemy within 15).
5. Jumps "to the other side": the landing cell is nearer to the enemy queen's start cell than to her own start cell. Share of jumps, and items 3 and 4 again for those jumps only.
6. For our queen only: the list of games where she jumped (source, opponent, map, round of each jump, landing distance to nearest enemy head, what happened to her in the next 30 rounds, final result).
7. Share of all games per size group that ended in elimination (jump or not), so QWQ's "small maps always end in elimination" can be checked.

## Checks
Print the raw events for three counted jumps (one ours, one top three, one that was followed by her death within 10 rounds) and confirm them by hand. Report how many games had a portal map but could not be parsed.

## Output (write `summary.md` last)
`data/analysis/queen-portals/count.py` and `summary.md`: the map table, tables for items 1 to 5 and 7 per size group, the list for item 6, the hand-checks, and the limits. English, plain words, sample sizes everywhere.
