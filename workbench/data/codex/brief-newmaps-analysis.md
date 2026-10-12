# Brief: why we lose on the new maps (Australia, Tower Defense, Islands, Around UNSW, Stripes)

Context: team meow's ladder win rates for v61 (893 games):
- Australia 15%, Tower Defense 17%, Islands 20%, Around UNSW 37%, Stripes 37%;
- old maps 40–82%.
QWQ thinks big maps are the main weakness. Note that Tower Defense is 32×16 and not big. Hard rule: NO per-map hardcoding; the qualifier is on unseen maps. Every proposal must be a general rule keyed on game state or terrain type (corridor width, pocket size, portal rooms, distance to the enemy), never a map name or size gate.

Data (find all of it; list what you used):
- Our ladder games: battlecode/work/nr/, work/nr_*.txt (battle lists), unsw-swarm/data/online/** (downloaded battles: game-*.json, M*.replay, events-*.jsonl.gz), ~/meow-loop-out/** (the loop's ladder downloads).
- Parsers: battlecode/replay.py (replay.parse/load, EVENT_NAMES), work/feedcheck.py, bigdeath*.py, lossan.py, leadfate.py, deathwin.py, howmap.py and others in battlecode/work/. Reuse them.
- Map files: battlecode/tune_runs/official127/*.map.
- Earlier findings to check against the data, not to trust blindly: battlecode/work/plan.md, lines ~600–650. These cover:
  - Tower Defense stay-home: PENALTY_NO_TAIL + CENTER_PULL, and the C2/C3 variants with CENTER_PULL=0 + NO_TAIL_ROOM=6;
  - Australia pocket deaths;
  - the Islands dead-end loop;
  - queen deaths;
  - top length at r400.
  Also check whether those fixes are actually ON in v61: v60toggles.txt + POCKET_CAP=48 + QUEEN_HOME_CLOSED=true. Report which C2/C3/NT toggles are on or off.

Analyse every game we have on those 5 maps (no sampling). Use the old maps as the comparison group. Measure:
1. Win/loss by how the game ended (queen rule vs longest vs total).
2. Our vs their length curves (longest, total, units) at r50/100/200/300/400/end.
3. Our deaths by cause, round and length (wall/self/body/head-on/enemy), and where they happen (a pocket, a dead end, a corridor, near a portal). Use the map geometry.
4. Territory and economy: cells visited by r100/r200, and pearls eaten per 50 rounds, vs the opponent.
5. Queen fate: the death round and cause.
6. Feeding: suicides, and whether the dropped length was eaten by them or by us.
Then find the 3–5 biggest gaps that explain the losses, ranked by estimated games affected, and say which are shared across maps.

Output:
- ~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/newmaps-2026-10-04.md: the plain summary first, then tables, then findings with evidence (game ids + rounds).
- For each finding, a draft idea card in the [Idea] template style (Claim / Evidence / Expected signal / What would show it's wrong / Test plan). Each must be a general rule, no map names in the logic. Save them as data/analysis/cards/NN-<slug>.md.
- Answer plainly whether the C2/C3 stay-home fix is in v61.
Read-only on the code; don't change bots or run ladder requests. Local replays/scripts are fine. No commits, no GitHub posts.
