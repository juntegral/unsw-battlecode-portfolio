# Codex brief: spatial occupancy study (where the food appears vs where the heads are)

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. It is the new lineage of our UNSW Battlecode 2026 bot: the deep-sea dragon game, our team is 583, and the score is the longest single dragon alive at round 500.

Read these first:
- `CLAUDE.md`, `ENGINE.md`, `EVAL.md`
- `research/KNOWLEDGE.md`: the index of every dataset and study
- `exp/map-atlas/INTERIM.md`: per-map engine families and targets
- `tools/mass_ledger.js`: the header comment defines every field

`legacy/` = `../unsw-heuristic`. `data/` and `.cache/` link to its data.

## Why (a finding from actual replays, 2026-10-01 03:25)
In our v1 local games vs `proxy4_king` (`exp/v1/v1-a-px4/games/*`), our swarm parks in its own backyard while the food appears elsewhere:

| Map | Our head samples in the two x-bands nearest our start (r50–374) | Natural pearls appearing there | Natural eaten, us vs them |
|---|---|---|---|
| Slithery Fight a | 86% | 3% | 191 vs 1,663 |
| Devil a | 96% | 14% | 83 vs 669 |
| Trauma | 82% | 22% | 64 vs 312 |
| Schooltime a (we won 35 vs 26) | heads spread evenly across the map | – | 828 vs 732 |

- **Dispersal targets (tag ` sd<dist>@x,y<o|u>`):** 39% of them on Slithery Fight point at dead-end pocket tiles. These are 1-wide kelp corridors that are not in the 2-core of the passable graph. Their pearls sit uneaten in 98% of rounds, because entering one is a trap death.
- Many other top targets hold a pearl in only 0–9% of rounds.
- My scripts: `/private/tmp/claude-501/-Users-jun-01--Project---------unsw-arena/ab529c8b-1bec-404e-b9b6-2b23c283b013/scratchpad/inspect_batch.js` (plus `inspect_food.js`, `inspect_sd.js`, `inspect_tile.js`). Reuse them freely.
- **Pitfall:** the ledger's `turn` hook fires at `turnStart`, before the move. A pearl that disappears between two hook calls belongs to the PREVIOUS hook's dragon. With that attribution, the recount equals the ledger's `eat_nat` totals exactly; check this on every game.

## Question
Per map and layout (Devil, Queen Of Spades, Schooltime and Slithery Fight a/b; Prisoners Dilemma 6 and 10 dragons), where do natural pearls appear, where do elite winners, elite losers and we keep our heads, and who eats what where? Turn the answer into dispersal-target rules the bot can use per map.

## Population (full; no samples)
- **Top games:** every game in `data/top/index.jsonl` except stalled ones. A team stalls when, from r100 on, it has ping 0 and ≤ 3 splits; the map atlas kept 17,057 of 17,331. Winners and losers are separate groups.
- **Ours:** all wave sets W0–W12 listed in `research/KNOWLEDGE.md` §1, plus the earlier lineages listed there. Excluded: `r1-online`, `r1-autoscrim`, `g1`, `g2`.
- **Local:** `exp/v1/*-px4/games/*` (v1 vs the v0-tagged build).

## Definitions
- **Frontier index** of a tile for a team: f = d_own / (d_own + d_enemy), with movement distances from each team's starting bodies (kelp, portals and wrap as in `mass_ledger.js`). Use 5 bins: [0, .2), [.2, .4), [.4, .6), [.6, .8), [.8, 1]. This is orientation-free, so sides A and B pool.
- **Pocket tile:** not in the 2-core of the passable graph. Iteratively prune tiles with ≤ 1 remaining passable neighbours; portals count as edges.
- **Fountain:** a tile whose spawn gap mean (min + max) / 2 is ≤ 12, from the map files (as in `mass_ledger.js`). A fountain group is fountains within Manhattan 3, the bot's FG_GROUP_DIST.
- **Group held** by a team in a round: the nearest head to the group (path distance) is that team's, within 3.

## Measure (per map/layout × group: elite winners, elite losers, ours by version family, v1 local)
1. **Pearl appearances** by f-bin, per phase (r0–99, 100–249, 250–374, 375–499).
2. **Head share** by f-bin at r25, r50, r100, r250, r375, and time-averaged over r50–374.
3. **Natural intake** by f-bin and per head-round by f-bin, with the correct attribution above.
4. **Deaths** by f-bin and cause (ledger causes), per head-round.
5. **Fountain groups:** yield (pearls/round), f-bin, pocket or not, and the share of rounds each group is held by winners, losers and us.
   - Winners' heads per group vs the group's yield: do they staff groups in proportion to yield?
   - Contested (centre) groups: who holds them, and how many heads sit there.
6. **Pocket fountains:** per map, list them and say how often pearls there are eaten, and by whom.
   - Deaths inside pockets.
   - Our dragons' time parked within 4 of a pocket mouth.
7. **Our v1 local sd targets:** share aimed at pockets; pearl presence on targets; distance-to-target distribution.

## Deliverables
1. **`exp/spatial/tables.json`:** machine-readable, per map/layout.
   - f-bin appearance shares, winners' and losers' head shares, and per-head intake by f-bin.
   - The fountain group list with yield, f, pocket flag and winners' hold rate.
   - A recommended head allocation by f-bin at r50, r100 and r250, and target rules.
   - **Write this first, as soon as the numbers exist, before the report.**
2. **`research/observations/spatial-occupancy.md`** (Korean):
   - Separate [사실] and [해석], and give N everywhere.
   - Describe the three-stage method: full-population scripts → classes with sizes → selected deep reads (cite game ids and rounds).
   - End with a per-map "dispersal rule" table for `bot/policy.hpp`: candidate groups, weights, frontier rule, pocket exclusion.
3. **`eval/spatial_report.js`:** a NEW file (do not edit other files in `eval/`).
   - A per-set diagnostic: `node eval/spatial_report.js <set dir or exp dir>` prints, per map, head share vs appearance by f-bin, natural eaten us/them, the sd-to-pocket share and trap deaths by f-bin.
   - It must reproduce the Slithery Fight numbers above on `exp/v1/v1-a-px4/games/proxy4_king_slithery_fight_A_1`.
4. **`exp/spatial/SUMMARY.txt`**, written last: 15 lines of key numbers.

## Rules
- **Write scope:** only `exp/spatial/**`, `research/observations/spatial-occupancy.md` and `eval/spatial_report.js`.
  - Caches go in `exp/spatial/cache/`.
  - `node tools/mass_ledger.js extract ...` may extend the shared ledger cache.
  - Do not write in `legacy/`, `data/`, `.cache/`, `bot/`, `versions/` or `exp/v1/`.
  - Do not commit; the coordinator commits.
- **No network, no uploads.** Do not read `unsw-arena-clean-control/operator-only/`.
- **Resources:** at most 3 worker processes. Another agent runs local games; pause if free memory is under 10% or disk free is under 20 GB.
- **Verification:** recount the key per-map numbers with a second, independent script, and report both.
- **Target:** `tables.json` by 06:00, everything by 07:30 KST. If you must stop early, leave `tables.json` and a partial report that say what is missing.
