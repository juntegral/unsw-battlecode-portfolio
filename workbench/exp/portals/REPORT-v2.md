# exp/portals REPORT v2 (2026-10-01): pocket ban (W1) adopted

The Portals agent could not write report files, so the coordinator saved its final report here.
- Plan, amendments and decisions: `exp/portals/PLAN-v2.md`
- Commits: a7bcc25 … 31fd914

## 0. Result
**What changed.** Every dragon, not only the king, pays 40 for any step into a pocket (a one-tile dead end behind a portal). The penalty applies to the first step, to the look-ahead, and to blind portal entries resolved through the static board.

**Confirmation vs V7** (seeds 51–70, 80 paired games):

| | Median [P25–P75] | Mean | P10 / min | King deaths /game (r300+) |
|---|---|---|---|---|
| V7 | 45.0 [41.0–50.0] | 45.0 | 34.9 / 17 | 1.24 (0.31) |
| W1 | 49.0 [42.8–55.0] | 48.8 | 37.9 / 28 | 1.55 (0.30) |

- Median +4.0 (bootstrap 95% 0.0 to +7.5); mean +3.8 (+1.2 to +6.5).
- Same-key games: 46 better, 28 worse.
- 0 eliminations, timeouts or errors.
- Adopted by rule 1 (median better by more than 1.0).

**On v1.2** (91a1cca, which carries V7 and the beacon; seeds 71–80, 40 paired games):
- Median 45.5 → 48.0 (95% −1.0 to +7.0); mean +2.8 (95% −0.4 to +6.1).
- The direction matches the confirmation above, but at this N the interval does not exclude 0.

**Patches and code.**
- `exp/portals/portals-v2-v1.2.diff`: for `versions/v1.2/bot`; apply with `git apply --directory=versions/v1.2`. The merged copy is `exp/portals/bot3-v12`.
- `exp/portals/portals-v2-delta.diff`: the same change against the V7 build `exp/portals/bot`.
- Final code: `exp/portals/bot3`.

**Identity.**
- The other 9 maps, seeds 1 and 2: 18/18 identical (v1.2 vs bot3-v12) and 18/18 (base vs bot3).
- Portals: `bot3` plays identically to the confirmed build `var/w1-pocket` (6/6).

**CPU (points per turn).** p50 6.9–7.0M, p99 11.2–11.9M, max 18.9M, the same as V7.

## 1. Facts (V7 confirmation games unless noted)
Our half has three kinds of spawn area:
- **U-rooms:** six 2×2 rooms. A dragon enters by one open-water mouth and leaves by the adjacent mouth 5 moves later.
- **Pockets:** eight one-tile dead ends behind portals. A head that enters cannot leave.
- **Corridor:** the fountain column, 4 fountains that respawn every round, outside the 2-core.

**Harvest** (seeds 11–20, 40 games; natural pearls per game): U-rooms 187, corridor 50, pockets 8.

**Net mass per game by area** (length out − length in per visit; drops eaten again are not counted):
- **U-rooms:** +176 from 55 walk-outs. The 10 deaths there cost −42, of which −19 are dragons of length ≥ 8.
- **Corridor:** about −4.
- **Pockets:** about −94. There are about 50 visits a game, each eating 0.5–1 pearl, with 33 deaths (mostly escape-split stubs) and 17 escape splits. The typical sequence: a dragon enters for one pearl, escape-splits, and the stub dies inside.

**Mechanism on the confirmation keys, V7 → W1:**

| | V7 | W1 |
|---|---|---|
| Pocket deaths per game | 33.1 | 16.3 |
| Dead length per game | 74 | 41 |
| U-room harvest | 190 | 226 |
| Mass at r250 | – | +10.9 vs V7 |
| King growth r300 → r400 (median) | 14 | 16 |

**Remaining pocket entries under W1** (about 17 a game):
- All are by the module's own processes, and 13.6 are blind portal entries.
- The move values are desperate (median −66; 31% below −100). The dragons are cornered at pocket mouths, not choosing the pocket.

**Elite** (200 top-vs-top Portals team-games):
- About 106 pocket deaths a game (dead length 281), eating only 7.6 pocket pearls.
- Teams with king500 ≥ 51 have about 90.
- The elite waste the pockets too; W1 simply stops most of it.

**King deaths per game** (V7, seeds 11–20):
- U-rooms before r300: 0.35 trapped, 0.25 head-on with an ally.
- U-rooms after r300: 0.15.
- Open water: 0.26.
- Pockets and corridor: 0.05.

## 2. Variants
Screen: seeds 1–10, 40 games each, vs V7 (= V5) on the same keys. All were pre-registered in PLAN-v2.md.

| Variant | Median [P25–P75] | Mean | King deaths /game | Early room king deaths | Mass r250 | Verdict |
|---|---|---|---|---|---|---|
| V7 | 49.0 [43.8–54.0] | 47.6 | 1.15 | 0.75 | 84.5 | baseline |
| W1 pocket ban | 49.5 [44.8–53.0] | 48.9 | 1.52 | 1.00 | 95.3 | best; confirmed |
| W2 W1 + U-room far-mouth check, all dragons | 45.0 | 43.6 | 1.27 | 0.60 | 85.5 | late traps 11 vs 2, 1 elimination |
| W3 dragons ≥ 10 kept out of all rooms, splitting off 3-children (the coordinator's hypothesis) | 44.0 [40.8–47.3] | 43.3 | 2.55 | 1.48 | – | median −5 (95% −8 to −1) |
| W4 W1 + check for the king only | 46.5 | 45.6 | – (0.50 after r300) | 0.60 | – | rejected |
| X2 W1 + one-way U-rooms | 45.5 | – | 1.30 | 0.80 | 80.8 | −4.0 vs W1 (95% −7.0 to −0.5); cuts harvest |
| W5 W1 + king check before r300 only | 46.5 | – | – (0.47 after r300) | 0.60 | – | −3.0 vs W1; identical to W4 until r300 |

- **W3 failed** because the longest dragon was more often a mid-size harvester that still dived into rooms.
- **X1 (forget pocket pearls)** was withdrawn before any game: it would have edited the spawn records that symmetry inference reads.

## 3. The goals
**Growth r300 → r400** (ours +16 vs the elite's +25): partly closed.
- Median per-game growth: 14 with V7, 16 with W1 on the confirmation keys; 13 → 15.5 on v1.2.

**Early king deaths in rooms ≤ 0.3 per game:** not met.
- W1 raises them from 0.55 to 0.80 per game, and all king deaths from 1.24 to 1.55.
- The rise comes before r300: more pieces harvest the U-rooms, and the mid-size harvesters that count as "king" die there.
- After r300 the rate is unchanged (0.30 vs 0.31).
- Every rule that cut early room deaths also cut harvest or added late deaths, and lost median.

**Interpretation:** the early "king" deaths are deaths of the largest harvester, not of the final king. W1 has more of them and still a higher king500.

## 4. Key case
proxy4_king A, seed 65: king500 is 26 under V7 and 47 under W1, with 58 fewer pocket deaths under W1.

At r200:
- V7: 15 dragons, total 82: [13 11 11 8 7 6 5 5 3 3 2 2 2 2 2]
- W1: 13 dragons, total 96: [19 19 19 10 6 5 4 3 3 2 2 2 2]

## 5. Next leads
1. **Pocket mouths.** Dragons are still cornered there, about 16 pocket deaths a game. A safe version of X1: a planner-side exclusion that stops the pearl field pulling toward pocket mouths, without editing world records.
2. **U-room traffic without cutting harvest.** Every check tested so far traded harvest for safety. The elite harvest twice our U-room pearls (395 vs 187–226) with twice the heads (25.7 vs 12 at r100, from the spatial table).
3. **Early king deaths.** Either a different king-class notion (mass-weighted rather than longest), or safer harvesting by the longest dragon.
