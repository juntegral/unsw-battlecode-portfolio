# Codex brief: map atlas — how each map (and layout) differs, and which engine each needs

You work in the new repository `~/01. Project/개인 프로젝트/unsw-swarm` (UNSW Battlecode 2026, "deep-sea dragon" game, our team 583).

## Hard rules
- **Writes:** write only under `research/observations/map-atlas.md` and `exp/map-atlas/`. Do not modify any other file, including anything under `legacy/`, `data/` or `.cache/`, which are links to the old repo. Put caches in `exp/map-atlas/cache/`.
- **Commands:** no network, no uploads, no git commits.
  - The whole run inherits niceness from its parent, so do not call `nice` yourself. Use at most 2 worker processes.
  - Pause if `memory_pressure` shows free memory below 10%, or `df -g /` shows less than 20 GB free.
- **Questions:** do not stop to ask questions. Make reasonable choices, record them in the report, and continue.

## Read first
- `CLAUDE.md`, `ENGINE.md`, `EVAL.md`, `DECISIONS.md`, `research/CHECKPOINT-2026-10-01.md`.
- `research/KNOWLEDGE.md`. It indexes every inherited dataset, cache, study and verdict. Use all of it, as the user asked: "최대한 기존 기보, 그리고 우리가 사용했던 가설 검증 과정에서 나왔던 자세한 데이터를 다 활용해줘. 전부 다."
- The official rules in `rules/`. The score is the longest single dragon alive at round 500; a team with no dragons loses at once.

## Why
Against the top 6 teams we won 75 of our 81 wins (900 games, 15 waves) on three maps:

| Map | Wins |
|---|---|
| Autarky | 37/90 |
| Prisoners Dilemma | 22/90 |
| Portals | 16/90 |
| Trauma | 3/90 |
| Slithery Fight | 3/90 |
| Default, Queen Of Spades, Schooltime, Trophy, Devil | 0/450 in total |

The user wants several engines, possibly one per map: "지도별로 엔진을 다 나눠도 될 것 같다. 진짜 최적화를 하고 싶으면." The user also said: "지도별로 정확히 어떻게 달라지는지 잘 모르겠다." This study answers that.

## Population (full; state N everywhere)
- **Top-vs-top:** every game in `data/top/index.jsonl`. Replays are `data/top/<battle>/<game>.replay.gz`.
  - Exclude games in which a team stalled: 0 pings and ≤3 splits in ≥100 rounds. State how many you excluded.
  - Separate each map by layout: Devil, Queen Of Spades, Schooltime and Slithery Fight have a and b; Prisoners Dilemma has a 6-dragon and a 10-dragon layout.
  - The bot's recogniser tables in `bot/mapdb.hpp` and `bot/terrdb.hpp` and the layout files in `maps/` identify layouts. The mass-ledger cache and earlier studies also classify layouts.
- **Ours:** every wave set listed in `research/KNOWLEDGE.md` §1, W0–W12 plus the earlier lineage sets.
  - Our tags (`dragonIndicator` text) show which mechanism acted. `tools/mech_check.js` `parseInd()` has the grammar.
  - Also use the per-wave mechanism reports `legacy/research/experiments/mech-cand-stack*.md`. They contain per-map values for every mechanism.
- **Caches you should reuse** (definitions in `tools/mass_ledger.js`):
  - `.cache/mass-ledger/top-sample.jsonl` (all top games at 23:55) and `online-*.jsonl`
  - `data/decisions/*` (per-dragon-turn rows)
  - `.cache/intake-gap`, `.cache/endgame-king`, `.cache/supply-chain`, `.cache/econ-principles`
- **Recount the key per-map numbers with an independent script,** and report both values.

## Questions: answer per map and per layout, with numbers and N
1. **Geometry and setup.**
   - Size, wrap, walls and kelp, portals.
   - Starting dragons: count, lengths, positions.
   - Fountains (spawn tiles, gaps) and the territory split between the two sides.
   - Distance between the two teams.
   - How separated the halves are: connectivity, chokepoints, path distances.
2. **What the elite do on this map (top-vs-top), winners vs losers.**
   - Head curve (r10, r25, r50, r100, r150, r250, r350) and split speed per phase.
   - Late piece births; natural intake per phase; territory held (Voronoi share, the enemy-nearer share).
   - Raids into the enemy side, eliminations and their timing.
   - Sacrifice onset (clock) and volume, and king-line sacrifice pearls.
   - King length at r300/r400/r500 and king growth per round.
   - King exposure to enemy heads; king kills (how, when, by what length).
3. **What wins on this map.** The winner-minus-loser differences that are largest and most consistent. Test consistency across teams and across both seats.
4. **Our performance on this map across W0–W12.**
   - Wins, eliminations, final longest, heads, intake share, and line sacrifice pearls.
   - Each mechanism's firing and application rate on this map, from our tags and the mech reports: csplit, lsplit, frag, F/F2, cl, cov, conv, feed/g, grab, tg, esc, escape-split/no-exit, portal, floor, kcap, bsp, lnt veto, and pf where local data exist.
   - Which mechanisms helped or hurt on this map. Report the correlation with outcomes carefully, and flag confounding.
5. **Clustering.** Which maps behave alike in the elite-behaviour features, and how many distinct engines this warrants. Present a clustering with the features and distances.
6. **An engine recommendation per map/layout, with evidence.** Assign one archetype:
   - "fortress" (our current behaviour);
   - "swarm economy" (the elite engine: fast splits, re-split 2+2, local feeding, the longest survivor becomes king);
   - an elimination-map specialist;
   - or a hybrid.
   Give target numbers for each assignment: head curve targets, split speed, the sacrifice clock round, feeding radius, the trading stance under local head counts, and king safety distance. Also say where our fortress engine should not be touched: the maps where we win, and why it wins there.

## Output
- `research/observations/map-atlas.md`, in Korean:
  - a population header, definitions, and [사실]/[해석] kept separate;
  - one section per map and layout, each with tables and N;
  - a summary table: map × key features × elite targets × our current values × recommended engine;
  - the clustering and the engine count recommendation.
- Code in `exp/map-atlas/`.
- Write `exp/map-atlas/SUMMARY.txt` last: a 25-line English summary with the per-map engine table. It is the completion marker.
