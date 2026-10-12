# g1 NOTES

Bot: `lineages/g1/bot/` (C++20. `main.cpp` + generated `maps_data.hpp`. Own protocol 3 reader; the helper is not used.)

## Design (per dragon, each turn)
1. **Map memory**: stores kelp, portals (id -> edge pair), pearl countdowns and last-seen round for every tile seen.
   **Public map built in**: `gen_maps.py` compresses the maps from `maps/online-20260927` plus the tool's bundled maps
   (15 total) into `maps_data.hpp`. At runtime the bot eliminates candidate maps by W,H and the edges it observes,
   and once one map remains it fills in every kelp edge, every portal, and each tile's average spawn rate. Portal ids
   are used only if they match what was observed. On an unknown map it falls back to memory only.
2. **Candidates**: 4 single moves. Two-step sprints are also evaluated only when in danger (no surviving move,
   enemy threat nearby, or negative score), with a -1500 penalty per extra segment.
3. **Survival**: time-aware BFS from the new head. Own body segment k becomes passable after `len-k+1+SLACK(2)`
   steps, delayed by pearls eaten along the path. Other dragons free up only if the whole chain is visible,
   otherwise they block permanently. Unknown edges within 3 steps are not trusted. A move counts as surviving if
   the max BFS depth is >= min(len+1,60) or the area is >= 2len+30.
4. **Food**: max-target term (value·0.9^d) plus a small discounted-sum term. Value: visible pearl 1, spawn
   expected before arrival 0.7, remembered pearl decays, a stale tile past its predicted spawn 0.6, unseen tile
   gets a spawn probability from the map's spawn rate. Tiles an enemy reaches first are discounted.
5. **Threats**: an enemy head can sprint up to len-1 steps (kamikaze), so the head-on risk penalty is weighted by
   BFS reach within 4 steps. Sealing an enemy's last escape gets a bonus; sealing an ally's gets a penalty.
   Portal exits outside vision get -150.
6. **Head trade**: only when our UNIT_COUNT >= 3 and the enemy is much longer (eL >= 2L+3, or endgame eL >= L+6).
7. **Splitting**: (a) escape split: when no move survives, try child sizes {2, L/2, L-3, L-2} and split only if
   at least one part survives (e.g. the dead-end corridors in prisoners_dilemma). (b) growth split: L>=40,
   round<380, units<12, no enemy nearby, and both parts must pass the survival check.
8. **CPU**: pow/exp are table lookups; the virtual clock is used as a points meter, so extra candidates and
   splits are cut after 55-75M. Max measured: 50M on a 64×64 map, 27M on schooltime.

## Key fixes found during testing (cause -> fix)
- Circling forever in front of a portal: blind-exit penalty of 700 was larger than the food value -> lowered to 150.
- Length shrinking to 3 from repeated sprints -> sprint cost raised to 1500.
- Coiling into a pocket, then a pearl spawning on the vacated tail tile -> SLACK 2 and eat-aware BFS.
- Split children piling up and dying in cascades -> escape split only on real survival failure; growth split must pass the survival check.
- Hunter killing us with sprint head-ons -> threat reach model.

## Local results (sandbox, judge 1.1.0, 10 online maps, seeds 1-2, alternating sides)
- vs replay_rules_v8: 8-10/20 (loses mainly on length in autarky, prisoners_dilemma, schooltime, slithery_fight, trophy)
- vs archetype_hunter: 13/20, vs archetype_swarm: 9/10, vs h2: 10/10
- SPLIT_AT comparison (40 games, v8+hunter): no split 22, 40 -> 23, 24 -> 16. Default set to 40.

## Remaining weaknesses
- Our longest dragon is shorter than v8's (it has many dragons plus suicide feeding). No king-feeding coordination.
- No sonar used. No symmetry inference on unknown maps.

## Tools (in this folder)
`match.sh`, `batch.sh <bot> <seeds> <opp...>` (2 in parallel), `why.sh <map> <opp> <seed> [n] [botdir]` (death context with
the G1DEBUG build), `gen_maps.py`, `render.py`.

---
## Changes after r1 (lineages/g1/bot current version, 20:10)
Local eval: 10 online maps × 6 seeds (1-6) × {replay_rules_v8, archetype_hunter}, 60 games each, alternating sides.
r1 (=SPLIT_AT 40, unrestricted escape split) scored v8 25/60 · hunter 40/60 on the same seeds 1-3 basis (13/30, 20/30).

1. **Escape split restricted (ESC_MD=3)**: the escape split used to fire whenever no move passed the survival test,
   which chopped dragons into length 2-5 in cascades (a trophy game had 85 deaths). Now it fires only when the best
   candidate's max BFS depth is <= 3 (really cornered). Seeds 1-3: v8 13 -> 17/30. Sweep: ESC 1 -> 14, 5 -> 12,
   off -> 7.
2. **Growth split SPLIT_AT 16, MAX_UNITS 20** (was 40/12). 6-seed totals (v8+hunter, 120 games): 40 -> 67, 20 -> 64,
   16 -> 72, 12 -> 71. vs swarm 19/20, vs h2 19/20.
3. **Partial-trail robustness**: when the body beyond vision is unknown (start of the game, long dragons), moving into
   one of my own unidentified segments counts as death, and BFS keeps those cells blocked for len+1+SLACK. Chain
   reconstruction falls back to adjacency when facing does not match.
4. **Emergency split when the tail is not visible**: parent keeps 2, child gets LEN-2.
5. **Symmetry**: maps_data now carries the SYMMETRY value (y = mirror left-right, xy = 180° rotation, verified
   against tile gaps). The countdown seen on a tile is copied to its mirror tile, but only for tiles never seen
   directly (MIRROR=1). Effect is within noise.
6. Tried and not adopted (6 seeds, v8/hunter): THREATW 0.5 (23/43), 2.0 (20/45), SLACK 1 (22/48), SLACK 3 (27/44),
   FOODMAX 700 (19/40), 250 (22/43). Current default is 28/44.
