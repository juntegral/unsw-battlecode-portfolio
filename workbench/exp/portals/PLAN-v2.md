# exp/portals v2 — plan and pre-registered rule (2026-10-01 06:30 KST, before any v2 game)

**Base.** V7, the v1 Portals module (`exp/portals/bot`, `PLAN.md`). On the v1 confirmation keys it scored king500 median 48, P25 41. King deaths were 0.91 a game; about 0.5 a game of them happened before r300 in rooms.

**Team lead's goals (06:25)**
- Close the r300–400 growth gap to the elite top decile (+16 against +25).
- Cut early king deaths in rooms to ≤ 0.3 a game (about 1.0 with all causes).

## Facts that shape the design
Source: V7 confirmation games, seeds 11–20, 40 games, `runs/conf-v7`. Scripts: `analysis/harvest.js` and scratch `pocketep.js`.

**Tile classes on our half**
- **U-room:** a 2×2 compartment. Its two portal exits lead to two adjacent tiles of open water, the mouths. Entering from one mouth, the head takes 5 moves to come out at the other. There are 6 per half, with 24 spawn tiles.
- **Pocket:** a one-tile compartment with one portal exit. A head that enters cannot leave; it escape-splits or dies. There are 8 per half, with 8 spawn tiles.
- **Corridor:** the fountain column outside the 2-core, with 4 fountains of gap 1.

**Natural pearls eaten per game**
- U-rooms 186.7. By eater: length 4–7 75.7, 8+ non-king 57.1, pieces 28.9, the king 25.0.
- Corridor 49.7.
- Pockets 7.7.

**Visits, per game.** An episode runs from the head's first step into the class until it walks out, splits or dies. Net = length leaving − length entering; drops that are eaten later are not counted.

| Class | Walked out | Died | Escape-split | Net |
|---|---|---|---|---|
| U-rooms | 55 visits, +176 | 10 visits, −42 (length 8+: 1.6 a game, −19) | 7.8 | about +130 |
| Corridor | 6 visits | 16 visits of length 2–3, −33 | 15 visits, +28 | about −4 |
| Pockets | – | 33 visits of length 2–3 (mostly escape-split stubs), −76 | 17 visits, −17 | about −94 |

- In pockets, a visit eats 0.5–1 pearl.
- **Interpretation:** pockets are a pure loss. A dragon enters for one pearl, escape-splits, and its stub dies there. The loop repeats because a new child does not know that the portal leads into a dead end, and unexplored portals pull hungry dragons.

**Where kings die** (the longest dragon at length ≥ 8), per game:
- U-rooms: 0.35 trap and 0.25 ally head-on before r300, 0.15 trap after.
- Open water: 0.26.
- Pockets and corridor: 0.05.
- U-room deaths come from a blocked far mouth, or from a dragon entering from the other mouth.

## Rules (all act only in a process that recognised Portals, like v1)
- **A1 — pocket ban** (`PT2_POCKET_ON`): every dragon pays 40 per step onto a pocket tile. This applies to the first step, to the look-ahead, and to blind portal entries (the static board gives the exit).
- **A2 — U-room entry check** (`PT2_UROOM_ON`): a first step from a mouth into a U-room pays 15 unless the far mouth is safe:
  - no body there, except our own body that leaves within 5 moves;
  - no other dragon's head within Manhattan 2 of it.
  - The far mouth is adjacent to our head, so it is in view. `ptmap.hpp` holds the entry → far-mouth table.
- **A3 — team lead's hypothesis** (`PT2_BIG_ON`):
  - Any dragon of length ≥ 10 pays 40 per step onto a room tile of any kind (U-room, pocket, corridor).
  - Before r350, a dragon of length ≥ 10 that is not the king after r300 splits off a 3-child every 8 rounds or more while the team has fewer than 16 units. The child's spot must pass `csplitChildSafe`.

## Variants and games
- **Screen:** seeds 1–10, proxy4_swarm and proxy4_king, both sides, 40 games per variant, paired with V7. V7's games on these keys already exist in `runs/v5-full`; V5 ≡ V7 game for game.

| Variant | Switches |
|---|---|
| W1 | V7 + A1 |
| W2 | V7 + A1 + A2 |
| W3 | V7 + A1 + A3 |
| W4 | chosen after W1–W3: one parameter or component change, written here before it runs |

- **Confirmation:** the best by the rule against V7 on fresh seeds 51–70 (80 paired games; V7 is run on the same keys).
- **Identity:** the other 9 maps, seeds 1 and 2, event-identical.

## Selection rule (fixed now; the same as v1)
1. **Median king500 first.** A variant beats another when its median is higher; medians within 1.0 count as a tie.
2. **Then the lower quartile (P25)**, same 1.0 tie band.
3. **Then own-move king deaths per game.**
4. **Reported, not ranked:** king deaths in rooms before r300 (goal ≤ 0.3), king growth r300→r400, eliminations, CPU.
5. **Adoption:** the confirmed variant replaces V7 only if it beats V7 by rule 1 on the confirmation keys, or ties on 1 and beats it on 2, or ties on 1 and 2 and beats it on 3 by at least 0.1 a game (about 8 deaths in 80 games; the v1 V9 lesson). Otherwise V7 stays.

## Amendment 06:45 KST (after the W1–W3 screen; W4 fixed before it runs)
**Screen results** (seeds 1–10, 40 games each, against V7 on the same keys):

| Variant | Median [P25–P75] | Mean | P10 / min | King deaths /game (r300+) | Room king deaths before r300 | Mass r250 | King r300 → r400 |
|---|---|---|---|---|---|---|---|
| V7 | 49.0 [43.8–54.0] | 47.6 | 37.7 / 26 | 1.15 (0.10) | 0.75 | 84.5 | 18 → 32 |
| W1 | 49.5 [44.8–53.0] | 48.9 | 42.0 / 39 | 1.52 (0.23) | 1.00 | 95.3 | 15 → 33 |
| W2 | 45.0 [39.3–52.0] | 43.6 | 29.6 / 0 (1 elimination) | 1.27 (0.35) | 0.60 | 85.5 | – |
| W3 | 44.0 [40.8–47.3] | 43.3 | 35.0 / 20 | 2.55 (0.42) | 1.48 | – | – |

- By the rule W1 is the best of the three. Against V7 it ties on median and P25, and it has more king deaths.
- **What W2 showed:** checking every dragon's U-room entry cut early room deaths to 0.60, but the harvest fell (mass at r250 85.5) and late room traps rose (11 against 2).
- **What W3 showed:** the hypothesis as implemented failed. With big dragons kept out of rooms, the "king" (longest ≥ 8) was more often a mid-size harvester still diving; king deaths 2.55 a game, median −5 (95% −8 to −1).
- **W4 = W1 + A2 for the king class only** (`PT2_UROOM_KING_ONLY`): pieces harvest the U-rooms freely; only the king checks the far mouth before entering.
- **Confirmation:** the best of W1–W4 by the rule, on seeds 51–70 against V7.

## Amendment 06:50 KST (after W4; the confirmation is fixed before it runs)
**W4 result:** median 46.5 [42.8–52.0], mean 45.6, P10 35.9, min 5. King deaths 1.38 a game (0.50 from r300, 3 of them from r400); room king deaths before r300 0.60.
- The king-only check brings back W2's late problem, so A2 is rejected in both forms.

**By the rule, W1 is the best of W1–W4:** its median of 49.5 is ahead of W4 (46.5), W2 (45.0) and W3 (44.0).

**Confirmation:** W1 (`var/w1-pocket`) against V7 (`var/v7-full2`, the build of the v1 confirmation) on seeds 51–70. That is 80 games each, same opponents and sides. The adoption rule in this file applies.

## Decision (07:06 KST)
**Confirmation:** seeds 51–70, 80 paired games, the same keys for both.

| | Median [P25–P75] | Mean | P10 / min | King deaths /game (r300+) | Room king deaths before r300 | Mass r250 | King r300 → r400 |
|---|---|---|---|---|---|---|---|
| V7 | 45.0 [41.0–50.0] | 45.0 | 34.9 / 17 | 1.24 (0.31) | 0.55 | 83.9 | 16 → 30 |
| W1 | 49.0 [42.8–55.0] | 48.8 | 37.9 / 28 | 1.55 (0.30) | 0.80 | 94.8 | 16 → 33 |

- Median +4.0 (bootstrap 95% 0.0 to +7.5); mean +3.8 (+1.2 to +6.5). W1 wins 46 same-key games and loses 28. No eliminations; no timeouts or errors.
- **Adoption rule 1** (median better by more than 1.0): **W1 replaces V7.**
- **Goal 2 is not met:** own-move king deaths rise from 1.24 to 1.55 a game. The rise is before r300 and in rooms, where W1 sends more traffic into the U-rooms. From r300 on they are unchanged (0.30 against 0.31).
- **Goal 1 moves partly:** king growth r300 → r400 is 14 → 16 (median of per-game).
- The final v2 is W1 with the rejected A2 and A3 code removed: `exp/portals/bot3`. It must play Portals identically to `var/w1-pocket` (fingerprints in `identity/v2-confirmed-build.txt`).

## Post-decision check: v2 on v1.2 (07:26 KST; not part of the selection)
**Setup:** `versions/v1.2/bot` at 91a1cca, which carries V7 and the beacon, against the same with `portals-v2-v1.2.diff`. Portals, seeds 71–80, 40 paired games.

| | Median [P25–P75] | Mean | P10 / min | Mass r250 | King r300 → r400 | King deaths /game (r300+) |
|---|---|---|---|---|---|---|
| v1.2 | 45.5 [39.8–51.0] | 45.1 | 35.9 / 28 | 83.0 | 18.5 → 30 | 1.15 (0.30) |
| v1.2 + v2 | 48.0 [45.0–52.3] | 47.9 | 37.9 / 25 | 96.6 | 15.5 → 33 | 1.45 (0.30) |

- Difference: median +2.5 (bootstrap 95% −1.0 to +7.0), mean +2.8 (−0.4 to +6.1).
- **Identity** (other 9 maps, seeds 1 and 2): `bot3-v12` ≡ v1.2 in 18 of 18 games; `bot3` ≡ `bot-base` in 18 of 18.
- **Build equivalence:** the cleaned `bot3` ≡ the confirmed build `var/w1-pocket` on Portals (6 of 6 fingerprints).


## Amendment 07:28 KST: a v3 round (pre-registered before it runs)
**Diagnosis of W1** (confirmation games, seeds 51–60):
- About 17 pocket entries a game remain, all by processes running the module.
- 13.6 of them are blind portal entries.
- Their move values are desperate: median −66, 31% below −100. So the dragons are cornered at pocket mouths, not choosing the pocket.
- Early king deaths are in U-rooms: trap and head-on with an ally.

**Two candidates:**
- **X1 = W1 + `PT2_POCKET_FORGET`:** each module turn, before the pearl field, the pocket tiles are marked as never spawning and holding no pearl. No dragon is pulled toward a pocket mouth any more.
- **X2 = W1 + `PT2_ONEWAY_ON`:** every U-room is entered only from the mouth with the lower tile index. Entering from the other mouth pays 30 on the first step and in the look-ahead. Two dragons can then never meet head-on inside a room.

**Screen:** seeds 1–10, 40 games each, against W1 (`runs/w1-pocket`, cached).

**Confirmation:** the better of X1 and X2 by the rule, and only if it at least ties W1 on the screen (median within 1.0 or better). It runs against W1 on fresh seeds 81–100, 80 paired games each. The adoption rule is the same as for v2.
- **07:29, before any v3 game: X1 is withdrawn.** Marking pocket tiles as never spawning changes the world's spawn records. The symmetry inference also reads those records, and our pockets' mirror tiles lie in the other half, where we can see them. That could kill the true symmetry hypothesis. A safe X1 needs its own field or a symmetry-aware mark.
- **Only X2 is screened.**

## Amendment 07:35 KST: X2 result, and W5 (pre-registered before it runs)
**X2 (one-way U-rooms)** against W1 on seeds 1–10:
- Median 45.5 against 49.5, a change of −4.0 (95% −7.0 to −0.5). Mean −3.3.
- Mass at r250 80.8 against 95.3. Early room king deaths 0.80 against 1.00.
- It cuts the harvest more than it saves. By the rule it does not tie W1, so there is no confirmation; W1 stays.

**W5 = W1 + A2 for the king class before r300 only** (`PT2_UROOM_KING_ONLY`, `PT2_UROOM_UNTIL = 300`).
- Why: W4 (the king-only check at every round) had early room deaths of 0.60 and kept most of the mass (92.4), but its late deaths rose (0.50 a game from r300). Early deaths are the target.
- **Screen:** seeds 1–10 against W1.
- **Confirmation:** only if W5 at least ties W1 on the median. It then runs against W1 on fresh seeds 81–100, 80 paired games each, under the same adoption rule.

## W5 result (07:39 KST): no confirmation, W1 stays
**W5 against W1** on seeds 1–10:
- Median 46.5 against 49.5, a change of −3.0 (95% −6.0 to +2.5). Mean −1.5.
- Early room king deaths 0.60 against 1.00. King deaths from r300 0.47 against 0.23.
- W5 plays exactly like W4 until r300 (same mass and king at r250 and r300). Its late deaths are therefore not the check acting late; they follow the different game state at r300, or they are noise (19 against 9 deaths).
- By the rule W5 does not tie W1, so there is no confirmation.

**The v3 round is closed. The final Portals module is W1** (`exp/portals/bot3`; `portals-v2-v1.2.diff` for v1.2).

