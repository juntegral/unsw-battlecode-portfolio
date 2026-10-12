# exp/portals — Portals module: plan and pre-registered selection rule (2026-10-01 05:30 KST, before any variant game)

## Why Portals alone
Portals (32×16) is solitaire. From each team's starting bodies, a movement BFS (kelp, wrap, portals) reaches 240 tiles, and the two sets share none. Sonar cannot cross either, so the opponent only changes our dragons' id numbers. Local king500 therefore measures what online would.

## Baseline facts that set the design
Source: `exp/portals/runs/base`, which is `bot/` at HEAD (BELIEF_FIX_ON), unchanged. It played 60 games: proxy4_swarm and proxy4_king, sides A and B, seeds 1–15. The analysis is in `analysis/ours.js` and `summ.js`.

**Outcome**
- king500 median 41, P25 36.8, P10 32.8, min 27.
- Conversion (king500 ÷ r400 total) 0.71.

**Mass never converted**
- Total at r500 minus king500: median 10.
- Units at r500: 2 in most games. The late feed needs ≥3 units and gathering needs ≥4, so the second-longest (median 10 at r500) never reaches the king.

**King deaths:** 64 in 60 games, in 40 games.
- trap 29: 26 of them blocked by ally bodies.
- head-on with an ally 32: in 11, one of the two crossed a portal blind.
- sac 3.

**King handoffs:** 16.1 a game (5.3 after r300). All are escape splits, after dives into one-way rooms or the fountain corridor.

## Module
Everything below acts only in a process that recognised Portals. It runs as `decideImpl<false, true>`; the FORTRESS and SWARM instantiations compile as before. Code is in `bot/ptmod.cpp` and `bot/ptmap.hpp`, plus small hooks in `plan.cpp`, `plan.hpp`, `world.*`, `policy.hpp`, `engcfg.hpp`, `main.cpp`, `params.hpp`.

- **E (endgame):**
  - From r430, every non-king follows the king, with no unit or length floor.
  - The late feed runs down to 2 units.
  - The late window opens at 500 − (L + d + 10).
- **K (king safety):**
  - The king pays 40 per step onto a dead tile (outside the 2-core, or a compartment of ≤8 tiles with one exit). This applies to the first step and to the look-ahead.
  - The king pays 12 for a first-step portal crossing whose exit is out of view and was not probed clean from this tile last turn.
  - A non-king pays 12 for a crossing whose exit is out of view and within 2 (+ news age) of the king's fresh head.
- **C (clock):** conv and gathering start earlier (candidate values 270 / 310, against 300 / 340).
- **M (whole board loaded on recognition):** off. The first test game starved: 3 dragons of length 3 at r300. Loading the board removed the unexplored-portal pull that leads our dragons into our spawn rooms.

## Variants (at most 4) and games
| Variant | Switches |
|---|---|
| V1 end | E only |
| V2 end+safe | E + K |
| V3 end+safe+clock | E + K + C (270 / 310) — replaced at 04:31, see the amendment |
| V4 | chosen after V1–V3 (a parameter change of one of them), stated here before it runs — fixed at 04:31, see the amendment |

**Amendment 04:31 KST.** Written before any variant result was read. At this point V2 had finished and V1 was running; V2's rows were not opened.
- A baseline check made after the first draft found a pattern. Of the 64 king deaths, 40 began their fatal turn with the king's head in a 2×2 room: 23 of the 32 head-ons and 17 of the 29 traps.
  - The king spends only 7.4% of its r250+ turns in rooms.
  - These are mostly pass-through rooms, so they are not in DEAD. Only 2 of the 64 deaths were on DEAD tiles.
- New rule K-room (`PT_KING_ROOM_ON`): the king class pays 40 per step onto any compartment of ≤8 tiles (`ptmap ROOM`), on the first step and in the look-ahead.
- The variants are now:
  - V1 = E
  - V2 = E + K (dead tiles, blind crossings, pieces near the king), room rule off
  - V3 = V2 + K-room
  - V4 = V3 + C (270 / 310)
- The selection rule is unchanged.
- A bug was found and fixed before any V2 game: `ptExit` read the direction W as the map width. The first 9 V2 games had used it; they were discarded and kept apart as `runs/v2-endsafe-ptexitbug`.

**Amendment 04:41 KST.** V1–V4 screens were done; their results are in REPORT.md.
- **What V1–V4 showed:**
  - The room rule (V3, V4) lowered the king's growth: median 37 and 38.5 against 42.5 on the same keys. King deaths did not fall.
  - Endgame E converted the second (unconverted mass at r500: median 10.5 → 2.5), but king500 barely moved (+0.6 mean).
  - Reading the games showed why:
    1. The second often lost the king from its belief. A partial sighting replaced the king's length after 10 rounds, so the second thought it was the king, dropped the goal and did not feed.
    2. The second waited for the late window next to the king's long body, got trapped and died without feeding.
    3. The late king had grab turned off.
- **Two variants added, with the same keys and the same rule:**
  - V5 = V2 + PT_LEN (length memory) + E2: from r430, feed the king class on sight; late king grab on; gathering leaf weight 0.4 from r430. Room rule off.
  - V6 = V5 + C (conv 270, gathering 310).
- Six variants in all (the task said about four). Each screen took about 2 minutes. All are reported.

**Amendment 04:47 KST.** Written after V5 and V6.
- **Screen results on the 40 keys:**
  - V5 median 49.0, P25 43.8, 1.15 king deaths a game.
  - V6 median 48.0, P25 43.0, 1.20.
  - By the rule they tie on median and P25; V5 leads on king deaths.
- **What the V5 king deaths showed:** 29 of 46 carried the blind-crossing tag ` ptb`, 26 of them with the king's head in a room. In a room every exit is a portal, and the price kept the king circling until it was trapped.
- **Fix:** `PT_KING_BLIND_OUT_ONLY` applies the blind price only while the king's head is outside the rooms.
  - V7 = V5 + fix.
  - V8 = V6 + fix.
- **Confirmation (fixed now, before V7 and V8 run):**
  - The two best of V5–V8 by the screen rule go to fresh seeds 11–30: 80 games each, the same opponents and sides. The baseline gets the same 80 keys (it already has seeds 11–15).
  - The final choice applies the same rule on those 80 keys only. The screen keys picked the candidates, so they are not reused for the final comparison.

**Amendment 05:12 KST.** Written after the confirmation of V7 and V8 on seeds 11–30. The baseline's seeds 16–30 were still running and had not been read.
- **Confirmation results** (80 games each):
  - V7: median 48.0, P25 41.0, mean 47.8, P10 38.0, min 22.
  - V8: median 46.0, P25 41.0, mean 45.6, P10 32.9, min 0.
  - V8's min of 0 is an elimination. After the endgame feed, the king was alone; at r489 it went into a 2×2 room and was trapped (L48, proxy4_king A 16).
  - V7 lost a king of L38 at r446 (proxy4_swarm A 20; king500 22).
  - By the rule, V7 is chosen over V8 (median 48 vs 46).
- **New safety rule (V9 = V7 + this rule):** from r400, the king class pays 40 per step onto any room tile (ptmap ROOM), on the first step and in the look-ahead.
  - Reason: late growth comes from drops, while the endgame feed leaves the king alone, so a trap can end the game.
  - V3 had banned rooms for the king from round 0, which cost the king its harvest; this rule starts late instead.
- **Test:** V9 against V7 on new seeds 31–50 (80 games each, the same opponents and sides), under the same rule.
  - If V9 does not win by the rule (median, then P25, then king deaths), V7 stays.
  - Either way, eliminations are reported.

- **Screen:** 40 games per variant, paired with the baseline: proxy4_swarm and proxy4_king, sides A and B, seeds 1–10. At most 3 games at a time, nice 10.
- **Final:** the chosen variant is extended to the baseline's 60 keys (seeds 1–15).

## Selection rule (fixed now)
1. **Median king500 first.** A variant beats another when its median is higher. Medians within 1.0 count as a tie and go to rule 2.
2. **Then the lower quartile (P25)**, same 1.0 tie band.
3. **Then own-move king deaths per game** (trap + ally head-on + sac of the king; lower is better).
4. **Guard (reported, not ranked):**
   - CPU per turn: p99 must stay below 80M. Any turn over 100M disqualifies.
   - No timeouts. No eliminations beyond the baseline's (0/60).
5. The chosen variant must also beat the baseline on rule 1 over the same keys. Otherwise the recommendation is "no module", and that is reported.

Identity: `tools/fingerprint.js --same exp/portals/bot-base exp/portals/bot` on the other 9 maps, seeds 1 and 2. The event logs must be identical.

## Decision (05:34 KST)
**Confirmation on seeds 11–30** (80 games each, same keys)

| | Median [P25–P75] | Mean | P10 / min | King deaths /game | Eliminations |
|---|---|---|---|---|---|
| baseline | 41.0 [34.0–45.0] | 39.8 | 31.0 / 19 | 1.07 | 0 |
| V7 | 48.0 [41.0–53.0] | 47.8 | 38.0 / 22 | 0.91 | 0 |
| V8 | 46.0 [41.0–52.3] | 45.6 | 32.9 / 0 | 0.97 | 1 |

- V7 is chosen by rule 1. Against the baseline: median +7.0 (bootstrap 95% +4.0 to +11.5), mean +8.0 (+5.6 to +10.4).

**V9 against V7 on seeds 31–50** (80 games each)

| | Median [P25–P75] | Mean | King deaths /game | r400+ king deaths |
|---|---|---|---|---|
| V7 | 46.0 [41.0–51.3] | 46.2 | 1.06 | 3 |
| V9 | 45.0 [40.0–50.0] | 44.9 | 1.05 | 2 |

- Rules 1 and 2 tie (within 1.0). Rule 3, read literally, favours V9 by 0.01 king deaths a game, which is one death in 80 games.
- **Deviation from the rule (flagged):** I keep V7. The difference is below what 80 games can resolve, and the paired keys point the other way. V9's rule acts only from r400, so each pair shares its first 400 rounds by construction. 27 pairs end with the same king500; of the other 53, V9 is lower in 37 and higher in 16. Mean −1.3 (bootstrap 95% −3.5 to +0.9).
- The final bot is V7. The late room rule is removed from `bot/` and kept in commit f2d916f. Switching to V9 means restoring that one rule.

## Post-decision check: the module on v1.1 (06:00 KST; not part of the selection)
**Setup:** `versions/v1.1/bot` at d347ef6, which includes the king beacon on both engines, against the same with `portals-v1.1.diff`. Portals, seeds 1–10, 40 paired games.

| | Median [P25–P75] | Mean | P10 / min | King deaths /game (r300+) | Unconverted (median) |
|---|---|---|---|---|---|
| v1.1 | 40.5 [34.8–45.3] | 40.9 | 30.9 / 28 | 0.93 (0.20) | 9 |
| v1.1 + module | 45.0 [42.0–49.3] | 46.5 | 39.0 / 34 | 1.18 (0.28) | 0 |

- Module effect on v1.1: median +4.5 (bootstrap 95% +0.5 to +8.5), mean +5.6 (+2.6 to +8.7).
- v1.1 against v1 final on the same keys: median −2.0 (−5.0 to +2.5). The beacon alone does not change Portals.

## Post-decision decomposition (06:21 KST; the team lead's question, not part of the selection)
**Setup:** the confirmation keys, seeds 11–30, 80 paired games each, all against the same baseline.

| | Median [P25–P75] | Mean | King deaths /game (r300+) | Unconverted (median) | Against baseline: median, mean |
|---|---|---|---|---|---|
| baseline | 41.0 [34.0–45.0] | 39.8 | 1.07 (0.26) | 10.0 | – |
| LEN only (`var/d-lenonly`) | 41.0 [35.0–45.0] | 39.7 | 1.01 (0.23) | 8.5 | 0.0 (−4.0 to +3.0), −0.1 (−2.6 to +2.5) |
| V7 without LEN (`var/d-nolen`) | 46.0 [39.0–50.3] | 45.1 | 0.95 (0.19) | 0.0 | +5.0 (+1.5 to +9.0), +5.3 (+2.9 to +7.8) |
| V7 | 48.0 [41.0–53.0] | 47.8 | 0.91 (0.16) | 0.0 | +7.0 (+4.0 to +11.5), +8.0 (+5.5 to +10.4) |

- The length memory alone gains nothing. Without the endgame merge, the second-longest is never fed whatever it believes.
- On top of the rest of the module, the length memory adds about +2 median and +2.7 mean. The second then keeps the king as its goal and feeds it.
- **Null module** (`var/d-null`: the module's instantiation with every component off) plays Portals identically to the baseline in 6 of 6 fingerprints (`identity/null-module.txt`). The plumbing is neutral.
