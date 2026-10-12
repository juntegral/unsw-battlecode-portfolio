# exp/portals REPORT (2026-10-01)

This is the Portals agent's final report, saved by the coordinator because the agent could not write report files. The coordinator recomputed the confirmation numbers from `runs/base/rows.jsonl` and `runs/conf-v7/rows.jsonl` at 06:10:
- 80 same keys.
- Baseline: median 41.0, mean 39.8.
- V7: median 48.0, mean 47.8.
- V7 was higher on 66 keys and lower on 14. All match the figures below.

## 0. Result
**Chosen: V7.** It combines four rules: the endgame merge (E + E2), the length memory (LEN), king prices on dead-end tiles and blind crossings (K), and piece prices on crossings near the king (P).

**Patches** (each passed `git apply --check` against a fresh copy of its base):
- `exp/portals/portals.diff`: against `bot/` at HEAD 40660cc (v1 final).
- `exp/portals/portals-v1.1.diff`: against `versions/v1.1/bot` at d347ef6. Apply with `git apply --directory=versions/v1.1`.
- `exp/portals/portals-5497983.diff`: against the bot as built and measured.

**Confirmation on fresh keys.** Seeds 11–30, proxy4_swarm and proxy4_king, sides A and B, 80 paired games.

| | Median | P25 | P75 | Mean | P10 | Min |
|---|---|---|---|---|---|---|
| Baseline (`bot/` HEAD, unchanged) | 41.0 | 34.0 | 45.0 | 39.8 | 31 | 19 |
| V7 | 48.0 | 41.0 | 53.0 | 47.8 | 38 | 22 |

- Median +7.0 (bootstrap 95% +4.0 to +11.5). Mean +8.0 (+5.6 to +10.4).
- V7 was higher on 66 of the 80 same keys and lower on 14.
- Seeds 1–30 pooled (120 keys): 41.0 [36–45] → 48.0 [42–54]. Mean +7.1 (+5.0 to +9.1).
- V7 over 200 games (seeds 1–50): median 47, P25 41.8, P10 37, min 22, no eliminations.
- Conversion (king500 ÷ r400 total mass): 0.73 → 0.82.
- Mass not converted by r500: median 10 → 0.

**King deaths by its own move** (king = our longest dragon at length ≥ 8):

| | Per game | After r300 | From r400 |
|---|---|---|---|
| Baseline, 120 games | 1.03 | 0.23 | 3 |
| V7, 120 games | 0.99 | 0.14 | 1 |
| V7, 200 games | 1.02 | 0.17 | 4 |

- The target of 0.1 per game is **not met**. Most remaining deaths come before r300: mid-size harvesters (length 10–20) dying in 2×2 rooms.

**Other checks.**
- **CPU** (points per turn, 6 games each):
  - V7: p50 6.8–7.1M, p99 11.3–11.6M, max 22.8M.
  - Baseline: p50 6.8–7.1M, p99 11.0–11.5M, max 23.0M.
  - 0 timeouts and 0 errors in 793 local games.
- **Identity, other 9 maps** (seeds 1 and 2, as A vs proxy4_king): the event stream is identical in 18/18 for `bot/` HEAD vs the patched copy, and 18/18 for the original base vs the module.
- **Portals fingerprints, 18/18 identical:**
  - v1 final plays exactly like the measured baseline.
  - The rebased module plays exactly like the measured one.
  - The cleaned final plays exactly like the tested V7.
- **On v1.1** (with its king beacon): median 40.5 → 45.0, mean +5.6 (+2.6 to +8.7), over 40 paired games. The beacon alone does not change Portals (−2.0 median, interval includes 0).
- **Estimated win rate** (interpretation from the map-atlas model vs the top 6, where king 40 → 57% and 45 → 73%): about 60% → 75–80% on Portals.

## 1. Facts: our Portals games
### 1.1 Online W0–W12 (105 team-games vs the top 7)

| Era | Games | King deaths (/game) | Head in a room at the fatal turn | Causes | Handoffs /game (r300+) |
|---|---|---|---|---|---|
| W0–W4 | 49 | 25 (0.51) | 14 | trap 14, ally head-on 10, sac 1 | 11.2 (7.1) |
| W5–W9 | 35 | 48 (1.37) | 37 | trap 23, ally head-on 25 | 20.8 (10.7) |
| W10–W12 | 21 | 22 (1.05) | 13 | trap 8, ally head-on 12, sac 2 | 25.1 (14.1) |

- 64 of the 95 king deaths (67%) began their fatal turn with the king's head in a 2×2 room.
- Kings spend 9–13% of their turns from r250 on in rooms.
- A room is a walled compartment of ≤ 8 tiles or a tile outside the 2-core (`ptmap` ROOM, 114 tiles).

### 1.2 Local baseline (`bot/` HEAD, belief fix on; 60 games, seeds 1–15)
- **king500:** median 41, P25 36.8, P10 32.8.
- **King length (median):** r250 16.5, r300 16, r350 20, r400 30.5, r450 38.
- **Units (mean):** r250 13.7, r300 14.1, r400 5.7, r450 2.9.
- **King deaths: 64 in 40 games.**
  - Causes: trap 29 (26 of them blocked by an ally's body), ally head-on 32, sac 3.
  - 40 began in a room, although the king spends only 7.4% of its r250+ turns there. Only 2 were on dead-end tiles.
  - Head-ons: in 7 the other dragon entered an unexplored portal blind; in 3 the king did.
  - Vision does not pass through portals, so two heads meet on the far side.
- **Handoffs:** 16.1 per game (5.3 from r300). All were escape splits after dives into one-way rooms or the fountain corridor.
- **Final king's lineage from r300:** 13.9 at r300, +6.7 natural pearls, +28.8 own drops, −7.5 left behind in handoffs.
- **Endgame:** most games end with 2 units, and the second-longest is a median 10 long. Two rules stop it from being fed: the late feed needs ≥ 3 units, and gathering needs ≥ 4 units and length ≥ 4.
- **Losses after r250:** trapped escape-split stubs, 29 deaths and 64 length per game. The king eats 5–7% of those drops, against 44% of sacrifice drops.
- **`exp/v1` Portals games** (12 each):
  - Belief fix off: king500 median 24, conversion 0.30, 21.5 unconverted, 2.0 king deaths per game.
  - Belief fix on: 43, 0.73, 9.5 unconverted, 1.08 king deaths per game.

### 1.3 A belief fault that affects every map
- With BELIEF_FIX_ON, a partial sighting replaces an ally's length bound once it is older than BELIEF_LEN_STALE (10 rounds).
- Example: a king 42 long, seen with only 12 segments in view, becomes "12". The second-longest (13) then believes it is the king (`bl12 k1`), drops its gathering goal and never feeds.
- Traced in `runs/v2-endsafe` proxy4_king A 8 (r452–500) and `runs/v1-end` proxy4_king B 4.
- The module fixes this for Portals only (`World::ptUpdateLens`). For all maps: a sighting without the tail should only raise the bound.

### 1.4 Key cases
**Legend:**
- `K` = king head, `=` or `/` = king body.
- Digits = other heads (`#` = length ≥ 10), `.` = other bodies.
- `o` = pearl, `%` = death drop.

Our open water is the left half. All our spawn tiles are in 2×2 rooms, many of them on the right side (reached through portals) or in the x = 15 corridor.

**(a) Head-on through a portal.** `runs/base` proxy4_swarm A 14, r334.
- King #413 (length 18) moves N inside the room at (18–19, 0–1).
- Piece #467 (length 2, already doomed at value −696) enters an unexplored portal blind and comes out on the king's head. Both die.

```
|   .....oo     ,  K=            |
|   .    oo   ..o  ==      oo    |
| 6 .%%   ...oo.,  %   oo        |
```

**(b) Trapped in a pass-through room.** `runs/base` proxy4_swarm A 5, r334.
- King #495 (length 19) circles the room at (18–19, 8–9).
- Both portal exits lead onto an ally's body (#479, length 10).
- At turn start the king had 0 free neighbours and scored the move +1.5.

```
|.. ...  oo   %=%o =K      6.    |
|.       o%    = , ==      oo    |
```

**(c) The second is never converted.** `runs/base` proxy4_king A 5.
- At r450 the lengths are [37 22 2]. At r499 they are [37 24 10]: king500 37, total 71.
- On the same key, V5 and V7 reach king500 49.

**(d) Lone king trapped late.** `runs/conf-v8` proxy4_king A 16.
- After the endgame feed the king (length 44–48) is alone.
- From r486 to r489 it chases pearls into the room at (22–23, 6–7) and is trapped (value −1574). The team is eliminated at r490.

## 2. Facts: elite Portals games (subagent run)
3,458 team-games. The atlas rule dropped 47 games with a stalled team; ledger checks 0.

| Band | N | king500 | Conversion | King r300 / 350 / 400 / 450 | Units r250 → r450 | King deaths /game | Handoffs /game, r300+ |
|---|---|---|---|---|---|---|---|
| Top decile (≥ 51) | 354 | 54 | 0.85 | 11 / 24 / 36 / 48 | 32 → 4.5 | 0.23 | 2.7 |
| Median band | 788 | 34 | 0.48 | – | – | 0.74 | – |
| Ours W10–W12 | 21 | 26 | 0.31 | 17 / 18 / 19 / 24 | – | 1.05 | 14.1 |

- Mass at r250 is about 80–85 in every band.
- The top decile sacrifices from r250 (42 length sacrificed in r250–299; ours 0.8).
- In the top decile, the king at r350 is the final king's ancestor in 88% of games.

## 3. Design
**Structure.**
- The module is `exp/portals/bot/ptmod.cpp` plus `ptmap.hpp`.
- `ptmap.hpp` is generated from the map file by `gen/genptmap.js`. It holds every edge and portal id, plus the DEAD (66 tiles) and ROOM (114 tiles) sets.
- Checks:
  - Kelp edges and portal pairs match a replay's map, with 0 mismatches.
  - `gen/ptexit_test.cpp` checks `ptExit` against a reference on all 2,048 tile–direction pairs.
- **Hooks:**
  - `policy.hpp` gives the Portals row `portals = true`, and `decide()` then runs `decideImpl<3>`.
  - Every module block is `if constexpr`, so the FORTRESS, W4 and SWARM instantiations compile exactly as before.
  - The world hooks (length memory) run before the turn clock starts, and only on Portals.

**Rules.**
- **E:** from r430, every non-king follows the king with no floor on units or length. The late feed runs down to 2 units, with window = 500 − (L + d + 10).
- **E2:** from r430, a non-king feeds the king class as soon as it sees it (≤ 5 path steps). The late king keeps grabbing. Gathering weight is 0.4 per tile.
- **LEN:** an ally's length is the longest evidence from the last 20 rounds, unless its whole chain is in view.
- **K:** the king pays 40 per step onto DEAD tiles, on the first step and in the look-ahead. Outside rooms only, it also pays 12 for a first-step crossing whose exit is out of view and has no clean probe from that tile.
- **P:** a non-king pays 12 for a crossing whose exit is out of view and within 2 (plus the age of the news) of the king's fresh head.

**Rejected by measurement.**
- Loading the whole board at recognition: dragons starved (3 dragons of length 3 at r300 in one test). The pull of unexplored portals is what leads them into the spawn rooms.
- King banned from rooms from r0 (V3, V4).
- Earlier clock of r270/310 (V6, V8).
- King banned from rooms from r400 (V9).

## 4. Measurement
`PLAN.md` holds the rule, pre-registered, plus five timestamped amendments.

**Screen** (seeds 1–10, 40 games each):

| Variant | Median [P25–P75] | Mean | King deaths /game | Unconverted mass |
|---|---|---|---|---|
| base | 42.5 [39–45.3] | 42.5 | 0.95 | 10.5 |
| V1: E | 42.0 [39–48.3] | 43.1 | 0.95 | 2.5 |
| V2: E+K+P | 45.0 [39–51] | 43.9 | 1.23 | 8.5 |
| V3: + room ban r0 | 37.0 [33.8–43] | 38.6 | 1.20 | 2.0 |
| V4: V3 + LEN | 38.5 [34.8–45] | 39.4 | 1.07 | 6.5 |
| V5: V2 + LEN + E2 | 49.0 [43.8–54] | 47.6 | 1.15 | 0 |
| V6: V5 + clock 270/310 | 48.0 [43–52.3] | 47.8 | 1.20 | 0 |

- V7 and V8 are V5 and V6 with the blind-crossing rule off inside rooms. They matched V5 and V6 game for game.
- **Confirmation** (seeds 11–30): V7 48.0 [41–53] beats V8 46.0 [41–52.3]. V8 also had one elimination.
- **V9 vs V7** (seeds 31–50): median 45.0 vs 46.0, P25 tied, king deaths 1.05 vs 1.06 per game.
- **Deviation from the rule, flagged:** read literally, the rule's third criterion favours V9 by one death in 80 games. V7 was kept.
  - V9 only changes play from r400, so each pair shares its first 400 rounds.
  - 27 pairs ended equal. Of the other 53, V9 was lower in 37.
  - Restoring V9 is one rule, kept in commit f2d916f.

## 5. Interpretation and next steps
- **What moved king500:** mostly the endgame rules (E, E2, LEN).
  - King at r450: 38 → 41. Mass unconverted at r500: 10 → 0.
  - K and P cut handoffs (V2: 15.8 → 12.5 per game) but did not lower king deaths.
- **Remaining gap to the elite top decile (54):**
  - Growth from r300 to r400: ours +16, theirs +25.
  - Early king deaths in rooms.
- **Next hypothesis (Portals v2):** long dragons never dive into rooms themselves; they split off a 2–3 child to harvest them. A length-3 piece can circle a 2×2 room and leave. This targets both the early king deaths and the stub churn.
- **For v1.1 on all maps:** the partial-sighting length reset (§1.3).
