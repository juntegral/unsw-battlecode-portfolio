# Brief: tools/top_metrics.py — per-game timelines from top-team replays

Repo: unsw-swarm. Replays: data/online/top1/<battleId>/ (game-<id>.json with teamAId/teamBId/teamAName/teamBName/teamAElo/teamBElo/winner/scoresA/scoresB/mapName/ranked, and M<id>.replay). Index of collected battles: data/top1/index.jsonl. The collector keeps adding battles; the script must be re-runnable and incremental (cache per game under data/analysis/top1/cache/).
Our own ladder games, for comparison: data/online/dl-*/, data/online/smoke/*/ (same file layout; our team id is 1119).
Replay parser: ~/01. Project/개인 프로젝트/battlecode/replay.py (import via sys.path; see battlecode/work/feedcheck.py, work/stridemech.py, bigdeath*.py, leadfate.py and unsw-swarm/tools/smoke_pick.py for how events, lengths, deaths, splits, suicides and heads are read). Map geometry: the replay itself carries the map (info["map"]). Game rules that matter: the board is a torus; queens are dragon ids 0 and 1; the queen rule (longer living queen wins; a dead queen counts 0), then longest dragon; sprint gives ceil(L/4) free steps; sonar messages.

## Output (all under data/analysis/top1/)
1. `games.csv`: one row per game: ids, map, cells (W*H), both team ids/names/elos, winner, how it ended (queen rule / longest / total / wipe-out, as far as the replay tells), rounds, final longest, final total and units for both.
2. `timeline.csv`: one row per (game, team, round bucket) with buckets at 25, 50, 100, 150, 200, 250, 300, 350, 400, 450, end. Columns:
   - units alive; total length; longest length;
   - cells visited so far (distinct head positions);
   - pearls eaten in the bucket (length gains not from eating corpses, if separable; otherwise length gained);
   - splits in the bucket (by parent length class: ≤4, 5–9, 10+);
   - deaths in the bucket by cause (wall/self/body/head-on/other) and by length class;
   - suicides (and whether within 6 cells of the team's longest dragon = feeding);
   - head-on events initiated (a head moves into an enemy head) by length class;
   - multi-step moves (sprints): count and mean steps, by length class;
   - portal crossings;
   - sonar messages sent, if the replay shows them;
   - queen: alive?, length, distance from her start cell, number of teammates within 6 cells, nearest enemy head distance.
3. `team_summary.md`: for each of the top teams (≥ 20 games), a table of medians of the above per bucket, split by map size class (≤700, 701–1500, >1500 cells) and by win/loss; win rate vs ≥2000 opponents; share of wins by end type. The same table for us (1119) from our own ladder games.
4. `gap.md`: for the rank-1 team (the one with the highest elo in the newest game files; print which) vs us: for every metric and bucket, their median, ours, the ratio, sorted by the largest relative gaps. Plus the same vs the other two top teams, to tell what is special to the rank-1 team from what all top teams share.
5. `losses.md`: the rank-1 team's losses vs ≥2000 opponents: the same timeline for winner vs loser, to show what the winner did differently.
6. `notable.json`: 15 game ids worth reading closely: the rank-1 team's biggest wins and its losses, spread over map size classes and opponents (with file paths).

Performance: 2,000+ games; use multiprocessing (4 workers), cache per game, progress lines. python3 stdlib only. `python3 -m py_compile` must pass. Run it on what is collected so far before finishing and report runtime per game.
Do not touch other tools, the bot, the collector process, or anything outside unsw-swarm/tools/top_metrics.py and data/analysis/top1/. No network. No commits.
Write a ≤10-line note to data/codex/report-top-metrics.md: what could and could not be measured from the replay format (be explicit), and row counts.
