# Brief: behaviour counts for card #30 big-map-trades (online replays)

Read-only measurement. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/tc30-analysis/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Other files here have unrelated uncommitted changes: leave them alone.

## What the card changes
Card #30 adds a switch `TRADE_CONTACT` to our bot (team meow, id 1119). With it on, a small dragon (length 4 or less, not the queen, not the leader) may ram an enemy head at least as long as itself on ANY map. Without it, on maps above 1,200 cells it may only ram a target that is at least 5 long and at least 2 longer than itself, and only when the team has 8+ dragons. On maps of 1,200 cells or fewer nothing changes. A head-on (one head moves into another head) kills both dragons. The queen is the dragon with id 0 or 1.

## Replays (each folder holds `game-*.json` and the replay files; we are team id 1119)
New bot (switch on): `data/online/smoke/tc30-test-new/` (30 games vs test4 and WeHaveQuizzes) and `data/online/smoke/tc30-dev1b-new/` (15 games vs dev1).
Live bot (switch off), same opponents and maps: `data/online/smoke/safer-stride-test-old/`, `passage2-test-old/`, `qh31-test-old/`, `passage-test-old/` (30 games each vs test4 and WeHaveQuizzes) and `tc30-dev1-old/` (15 games vs dev1).

## Reference code (already hand-checked on these replay formats)
`data/online/smoke/qh31-analysis/qh31_count.py` (parsing, sides, queen ids, death causes, head-on pairing, exposure within 8 cells, map size and wrap handling) and the replay parser `~/01. Project/개인 프로젝트/battlecode/replay.py`. The card's own counting rule came from `~/meow-loop-out/card-0/attempt-1791101197/analyse*.py`.

## Count, per group (live vs new), split by map size (above 1,200 cells / 1,200 or fewer) and by opponent set (test4 + WeHaveQuizzes / dev1)
1. Ram rate, using the card's rule: rounds 0-299; turns where one of our small dragons (length 4 or less, not the queen) starts next to an enemy head (neighbouring cell, no kelp between, portal links not counted); how many of those turns ended in a head-on that killed it. Same for the opponent's small dragons next to our heads.
2. Head-ons we started before round 300, per game, and those the opponent started.
3. Our unit count and theirs at rounds 100 and 200 (mean per game).
4. Enemy heads within 8 cells of our queen, mean over rounds 20-200 while she is alive (same method as qh31_count.py), and our heads within 8 of their queen.
5. Our queen: games in which she died, median death round, and causes (head-on with an enemy, wall, own body, another body).
6. Final result context only: wins and mean final score, ours and theirs.

## Checks
Before trusting the script, print the raw events for one above-1,200-cell game from each group and confirm two counted rams and two declined turns by hand. State sample sizes (games and turns) next to every number. Do not interpret; count.

## Output (write `summary.md` last)
`data/online/smoke/tc30-analysis/count.py` and `data/online/smoke/tc30-analysis/summary.md`: one table per opponent set with live vs new for items 1-6 split by map size, the list of above-1,200-cell maps with games per group, the two hand-checks, and what could not be measured.
