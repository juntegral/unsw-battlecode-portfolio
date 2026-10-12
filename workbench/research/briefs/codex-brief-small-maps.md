# Codex brief: why we are wiped out on small maps, and how the elite survive crowded boards

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. Read first:
- `AGENTS.md`, especially §1 and §3;
- `docs/WORKQUEUE.md`, task W7;
- the rules in `rules/ALL.md`: movement, head-on and body collisions, splitting, sprint, death drops, vision 7×7.

Reuse the code in `exp/spatial/`, `exp/pocket/`, `exp/general/` and `tools/mass_ledger.js`. Its `turn` hook fires at turnStart, before the move.

## Why
The qualifier is played on unseen maps. In our unseen-map baseline (`exp/gen/PLAN.md` §6) the shipped bot (FORTRESS default) was **eliminated in 24/24 games** on the three small bundled maps: arena 11×11, Colosseum 16×16 and default_small 16×16. It lost the same way with the SWARM engine.
- Example: on Colosseum we split into at most 8 small pieces (the csplit target), they are rammed one by one, and the game ends around r125. The proxy ends with 37 dragons.
- Trophy (25×25, the smallest known map) is 8/8 eliminations with recognition on or off.

Unseen qualifier maps may well be small. Losing every small map loses bo7 matches.

## Data
- **Ours (local):**
  - `exp/gen/v12-F-H/games/*` and `exp/gen/v12-S-H/games/*`: the bundled maps, FORTRESS and SWARM, vs `bots/proxy4_king` and `bots/proxy4_swarm`, seeds 1–2.
  - `exp/gen/v12-F-K` and `exp/gen/v12-S-K`: the known maps with recognition off, including Trophy.
  - Online, Trophy only: W0–W12 and `data/online/v1-w1..3`.
- **Elite:**
  - `data/top/index.jsonl`: Trophy top-vs-top games (about 1,560), excluding stalled ones.
  - `data/elite/`: top-10 teams vs anyone. Look for any map names outside the known 10, especially small ones; the sprint bracket on unseen maps runs from 16:30 KST today.

## Questions
1. **How we die on small maps.** For each of our small-map games, give the timeline:
   - splits (rule tag and round);
   - unit count;
   - deaths by cause (rammed, ram, trap, enemyBody, allyHead) and their position;
   - the moment the count ratio flips;
   - the last 20 rounds before elimination.
   Classify the collapse patterns and give their sizes. Include 2–3 board pictures with `node eval/board.js <replay> <Map> <a|b> <A|B> <rounds>`. On bundled maps use the map name as written in the replay header.
2. **What decides head-ons in crowded boards.** For each head-on (both heads die), record who moved into whom, the lengths, the local head counts (d3/d8) and whether it was a cornered move. Is our problem the number of pieces, their length, being cornered, or splitting too early?
3. **How the elite survive Trophy.** Elite winners vs losers vs ours:
   - split schedule;
   - head count curve;
   - trade (head-on) balance;
   - length distribution of pieces;
   - use of bodies as walls;
   - king safety distance;
   - when eliminations happen.
4. **Recommendations for an area- or density-triggered survival rule** that the bot can apply on any unknown map from what it observes. The map size is known at r0. Examples: at area below X, do not split below length L; a cap on our piece count relative to visible enemies; refuse head-ons unless the local balance is at least +k; wall formation. Give thresholds with N and an expected effect, labelled as hypotheses.

## Deliverables
- `exp/small/tables.json`, written first.
- `research/observations/small-maps.md`, in Korean:
  - [사실] and [해석] kept apart, with N everywhere;
  - the three-stage method (full-population scripts → classes with sizes → deep reads with game ids and rounds);
  - a final rule table.
- `exp/small/SUMMARY.txt`, written last (12 lines).

## Rules
- **Write scope:** only `exp/small/**` and `research/observations/small-maps.md`. Do not commit; the coordinator commits.
- No network, no uploads, no local games of your own. Use the existing replays only.
- At most 2 worker processes. Pause below 10% free memory or 21 GB free disk.
- Recount the key numbers independently and report both counts.
- **Target:** tables by 15:30 KST, everything by 16:30 KST.
