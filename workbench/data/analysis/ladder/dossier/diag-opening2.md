# The second starter's late pearls are a round-0 tie broken by noise, not the centre pull (team 1119; 48 online games on two-dragon starts, 113 ladder games of ours, 136 of rank-1's; written 8 Oct 2026)

1. **The finding.** The centre pull is not the term. On the one layout that carries the gap (25 by 35, where `center_map` is false and the term is on for 0% of steps) our second starter eats 1.21 pearls by round 40 against 3.47 for its opponents and 5.62 for rank-1, because in round 0 the step straight ahead and the step to the side score the same and the id-and-round noise (0.5 of a point) picks the side step, in 32 of 34 ladder games and 12 of 12 online. From there the never-seen-tile bonus walks it into ground where no pearl is born; rank-1's and most opponents' second starter goes straight ahead and is through a portal ten steps on by round 10 (rank-1 88%, its opponents 73%, our ladder opponents 32%; ours 3% and 0 of 12). Where the centre pull does decide steps (the 32 by 16 walled start, 33% of them) rank-1 eats later than we do.
2. **The change.** One card: a short dragon that is not the queen breaks near-ties for the step straight ahead (HEADING_TIE, +1.5 a step, default off). No card for the centre pull: with it off, or off while we hold 2 dragons or fewer, the walked-forward second starter eats no more on any of the four layouts and less on one.
3. **How sure.** Sure of the terms: my rebuild of score_step names the step played on 96% of 3,720 ladder turns and 95 to 97% online (38% by chance). Fairly sure the card moves this start: walked forward with +1.5, our second starter plays rank-1's first ten steps and eats 5.06 by round 40 there (1.12 as built), with +3, +6, 20 rounds only or alone only giving the same. Not sure it travels: the whole gain is one layout of four, and no game was played.

Labels: [M] measured by my scripts in dossier/work/ (o2_scan.py: one row per starter turn of rounds 0-60 with the score terms of every step on offer for ours; o2_agg.py: the tables, commands tally, class, route, pearls, terms, card, head, keep, paths, view, cmap; o2_sim.py with o2_simagg.py: the walk forward; o2_spawnmap.py, o2_peek.py: maps). [C] read from data/online/smoke/agg8-bot/main.cpp, line given. [E] my estimate.
Terms: "two-dragon start" = each side starts with two dragons of total length 4 to 6 (four layouts: 24x12, 32x16 walled, 25x25, 25x35). "Second starter" = the starting dragon that is not the queen. "Blind turn" = a move turn with no pearl in its 7 by 7. Steps are path steps on the empty map (kelp shut, portals open). "Spawn tile" = a tile a natural pearl is born on at some time in that game. Online = agg7-m1, m2, m3 (MAIN, 24 games), agg7-b1, b2 (B7, 16), agg8-q1 (B7Q, 8); agg8-q2 was not on disk. A cell "a / b / c" is ours on the ladder / its opponents / rank-1 unless said.

## 2a. Pearls by round 40 and the walk (jobs 1, 2) [M o2_agg.py tally, class, route, keep]
| Second starter, rounds 0-40 | Ladder ours / opponents / rank-1 | Online MAIN, B7, B7Q / their opponents |
|---|---|---|
| Pearls it eats, all four layouts (queen beside it) | 1.35 / 2.73 / 2.98 (queen 2.01 / 1.81 / 2.69) | 1.62, 2.44, 2.75 / 2.54 (queen 1.46, 2.81, 2.88 / 2.15) |
| ... 25x35, two portals (34, 26 and 12 games) | 1.21 / 3.47 / 5.62 | 0.83, 1.00, 0.00 / 2.75 |
| ... 24x12, portal rooms (24, 30, 12) | 0.12 / 2.04 / 3.00 | 0.17, 2.25, 3.00 / 2.50 |
| ... 32x16, walled start (32, 38, 12) | 0.47 / 0.84 / 0.18 | 0.33, 1.00, 0.50 / 1.08 |
| ... 25x25 (23, 42, 12) | 4.09 / 4.96 / 3.86 | 5.17, 5.50, 7.50 / 3.83 |
| Its first pearl, median round; the side's second pearl | r51 / r17 / r11; r24 / r18 / r13 | r42, r13, r14 / r13; r21, r18, r30 / r18 |
| Blind turns: number; step ends nearer the centre; nearer a never-seen tile | 2,273; 61%; 66% / 2,227; 49%; 68% / 2,367; 54%; 82% | 505, 310, 162; 59, 58, 58%; 77, 78, 76% / 918; 49%; 73% |
| Blind turns by aim: known pearl, centre and unseen, centre only, unseen only, elsewhere % | 15, 36, 23, 21, 6 / 11, 28, 17, 31, 12 / 12, 37, 11, 35, 4 | MAIN 22, 38, 14, 21, 6 / 13, 31, 13, 34, 10 |
| Pearl in view: turns; eats or steps nearer | 1,836; 63% / 1,760; 63% / 1,730; 66% | 383, 192, 76; 63, 70, 83% / 672; 66% |
| ... not taken, by who is nearest: itself within 6 steps; a mate level; the queen nearer; another mate; itself 7+ steps; an enemy | 357, 177, 69, 37, 20, 17 of 677 (293 of the 357 on 24x12) / 238, 130, 89, 52, 96, 50 of 655 / 176, 105, 74, 94, 87, 47 of 583 | MAIN 75, 30, 17, 7, 9, 3 of 141 |

| The 25x35 layout, second starter | Ladder ours | Its opponents | Rank-1 | Rank-1's opponents | Online ours (12) / opponents |
|---|---|---|---|---|---|
| Round 0: steps straight ahead | 6% (2 of 34) | 68% | 85% | 81% | 0 of 12 / 75% |
| First four steps, both sides read from one start | E,S,W,S 28; E,S,S,S 4 | N,N,N,N 18 of 34 | N,N,E,E 18; N,N,N,N 3 of 26 | N,N,N,N 15 of 26 | E,S,W,S 11; E,S,S,S 1 / N,N,N 8 |
| Through a portal by r10; by r20 | 3%; 3% | 32%; 53% | 88%; 96% | 73%; 77% | 0; 0 / 25%; 25% |
| First pearl: round; steps from its start; nearer its own starts than theirs | r29; 21; 37% | r13; 11; 90% | r11; 10; 96% | r10; 10; 92% | r35; 16 to 21; 0 to 50% / r12.5; 11; 83% |
| Pearls in view a turn; steps to the nearest spawn tile; to the centre | 0.51; 5.8; 10.8 | 1.31; 2.7; 18.2 | 1.51; 1.6; 19.0 | | 0.12 to 0.26; 5.1 to 5.8; 8.1 to 9.2 / 1.55; 1.8; 19.5 |
- Where theirs find the first three pearls [M pearls, o2_spawnmap.py]: on 25x35 through the portal ten steps from the start into a walled field of spawn tiles, or along the rim column; 55 to 69% of their first pearls lie farther from the centre than the start (ours 32%) and 42 to 62% beside a kelp edge (ours 58%, no difference). Ours crosses a band 5 rows deep where nothing is born. On the other three layouts the first pearl comes from the same place for all (25x25: r9 / r9 / r9; 32x16: every side's nearest pearl is 24 to 38 steps off at r10 to r20).
- Round 0 straight ahead over all four layouts: ours 68%, opponents 58%, rank-1 33%, rank-1's opponents 83%. Rank-1 is not straighter than we are in general (blind turns 52% against 51%); the difference is this one start.

## 2b. Which term decides (job 3) [M o2_agg.py terms, card, cmap]
| Second starter, move turns r0-40 with 2+ steps on offer | Turns | Rebuild names the step | Centre term on for the step played | Step changes if the term is removed: centre; tie noise; territory; mate's head; unseen; pearl | Largest term, played step against next best |
|---|---|---|---|---|---|
| Ladder, all four | 3,720 | 96% (98% with no enemy in view) | 33% | 11; 15; 7; 5; 3; 4% | unseen 20, noise 20, pearl 17, centre 12, territory 11% |
| Ladder 25x35 (centre rule off) | 1,316 | 98% | 0% | 0; 29; 10; 1; 5; 1% | unseen 39, noise 39, territory 9% |
| Ladder 32x16 walled | 830 | 98% | 96% | 33; 3; 8; 19; 0; 0% | centre 35, mate 19, territory 17, unseen 16% |
| Ladder 25x25 | 733 | 90% | 36% | 12; 15; 8; 1; 2; 5% | noise 22, pearl 19, territory 16, eat 11, centre 8% |
| Ladder 24x12 | 841 | 96% | 21% | 5; 2; 0; 0; 1; 12% | pearl 52, cramped 18, centre 9% |
| Online MAIN / B7 / B7Q, all four | 800 / 438 / 207 | 97 / 96 / 95% | 33 / 34 / 34% | centre 8 / 7 / 4; noise 16 / 19 / 20; territory 8 / 8 / 8% | noise 24 / 27 / 33, unseen 14 / 15 / 19, centre 13 / 13 / 10% |
- Hot tiles decide 0% everywhere. The stall release is in the online builds and not in the ladder build: with it the rebuild names 95 to 97% online (86 to 92% without) and 91% on the ladder (96% without). Released, the pull is 40 a step to the nearest never-seen tile (stall seek).
- `center_map` [C 493-496, M cmap] is true on 8 of the 17 layout names in the two dossiers: 24x12, the four 32x16, 40x15 and 54x18 for 60 rounds, 25x25 for 30. False on 25x35 (875 cells, not wide), 32x32, both 48x24 (wide but 1,152 cells) and everything larger.
- Centre variants, first order [M card]: CENTER_PULL 0 changes the rebuilt step on 414 of 3,725 ladder turns (11%; 274 of them on 32x16) and 102 of 1,445 online; "off while we hold 2 dragons or fewer" on 309 and 66. The new step is farther from the centre in 82 to 100% and nearer a spawn tile in 24% against 39% farther (ladder).

## 2c. The walk forward (job 4) [M o2_sim.py, o2_simagg.py]
Our second starter is walked for 40 rounds as a virtual dragon by the rebuilt score, in the replay's own world; pearls it eats by round 40.
| | Real | As built | Heading +1.5 | Centre off | Centre off at 2 dragons or fewer |
|---|---|---|---|---|---|
| Ladder, all four (113) | 1.35 | 1.50 | 2.82 | 1.45 | 1.56 |
| Ladder 25x35 (34): pearls; first pearl; through a portal by r10 | 1.21; r53; 3% | 1.12; none by r40; 3% | 5.06; r12.5; 44% | 1.12 | 1.12 |
| Ladder 25x25 / 32x16 / 24x12 | 4.09 / 0.47 / 0.12 | 5.04 / 0.44 / 0.08 | 5.74 / 0.41 / 0.08 | 4.70 / 0.50 / 0.08 | 5.26 / 0.47 / 0.08 |
| Online, all four (48) | 2.08 | 1.67 | 3.27 | 1.40 | 1.54 |
| Online 25x35 (12) / 25x25 (12) / 32x16 (12) | 0.75 / 5.67 / 0.58 | 0.92 / 5.08 / 0.58 | 5.92 (portal 75%) / 6.50 / 0.58 | 0.92 / 4.00 / 0.58 | 0.92 / 4.67 / 0.50 |
- Heading variants on the ladder, all four: +3 2.79; +6 2.78; rounds 0-19 only 2.74; only with no mate's head in view 2.84; only with no pearl bonus on offer 2.81.
- First order [M head]: +1.5 changes the rebuilt step on 469 of the second starter's 3,720 ladder turns (13%; 25x35 359, 25x25 82, 32x16 24, 24x12 4) and 237 of 1,445 online (16%); 82% of them are blind turns. The queen, whom the card leaves out, would change on 322 of 4,186.
- Dead by round 40 in the walk: ladder 12% as built, 13% with +1.5 (25x35: 0 to 5 of 34 on the ladder and 0 to 2 of 12 online, at r28 to r39, three of the seven the turn after a second portal step).

## 3. Why, in the code [C agg8-bot/main.cpp]
- Centre pull: 5161-5165 take 40 a tile of wrapped distance to (width/2, height/2) from a dragon of 4 or less, while round is under 60 (wide) or 30 (700 cells or fewer), only for a step with no pearl or hot bonus; 3134-3142 and 5072-5074 are the release. On 25x35 none of this runs.
- The tie: 5483 adds 0.25 x ((id x 31 + round x 17 + k x 7) % 5), 0 to 1 point, k in the order north, east, south, west. Nothing in pick_direction reads the heading; ct.get_dir() is read once, at 1445, for the sonar report.
- What is left when nothing is in view: the never-seen bonus 0.2 x (260 - 40 x steps), 20 at 4 steps and 12 at 5 (5115), far gain 2 a step (5124-5133), and territory at 1.5 a tile where a tile a mate reaches first counts nothing (2978-2989, 5055-5059). Steps run over edges nobody has seen as if open (1381-1391), so a kelp line in view puts the tiles behind it "farther" and the walk bends into open ground.
- Portals: a short dragon beside a portal with an unknown exit takes it at best base + 88 (5348-5350, 5476-5478) and is pulled to one it has seen within 6 steps (3051-3054, 5119). The queen may not (3772-3774, 5259-5261) on more than 600 cells (3411-3413).
- [M view] Replay 1422316 (live bot, 25x35, won): round 0, #2 at (2,9) facing north: north and east 1504 each before the noise and west 1494; territory 641 on all three, never-seen 20, 20, 12, far gain 152, 152, 150; noise 0.5, 1.0, 0.75. East by half a point. Round 1 at (3,9): south 1302, east 1300, north 1174 (territory 435, 444, 307, the queen at (6,11) in view). Rounds 4 to 13 south or east on 20 against 12. It stands at (6,16) in r13, (9,20) in r20, (14,19) in r26; no pearl in view on 25 of 27 turns, the nearest on the board 12 to 22 steps off through r25; none eaten by r40. Its queen stands on the portal tile (4,3) in r13 and eats first in r33.
- [M paths, o2_simagg.py paths] Replay 1046961 (rank-1, the same start): north, north, east x 3, north x 4, west to (4,3), through the portal in r10 to (8,33), 6 pearls by r40. The walk forward of 1421774 and 1422316 with +1.5 plays the same ten steps and the portal in r10: pearls at r12, 15, 18, 21, 23 and at r11, 14, 15, 17, 23, 33. Ladder 1254075 and 1241492, the two of 34 where ours went north by itself: 6 and 9 pearls by r40.
- [M view] Replay 1421771 (live bot, 32x16): #3 goes west from (26,8) to (23,8) in r0-r2, the centre term 80 points a step (-360 against -440), then east along a one-wide row with one step on offer in r4-r9; the nearest pearl on the board is 35 to 41 steps off through r15; it eats in r16 a pearl born beside it. The term decides here and there is nothing to walk to.

## 4. The card
title: Break near-ties for the step straight ahead, not by id-and-round noise (default-off HEADING_TIE)
slug: heading tie
### Claim
[M] On a two-dragon start where the two best first steps tie, the noise sends our second starter sideways in 44 of 46 games and it eats its first pearl at round 29 on the ladder against round 10 to 13 for the other teams. [C] Proposal: a constant HEADING_TIE (0 = off, test 1.5); in pick_direction, beside the noise line, a dragon of length 4 or less that is not the queen, the leader or a feeder adds HEADING_TIE to a scored step in the direction it faces. 1.5 is above the noise (1) and below one step of far gain (2) and of the never-seen bonus (8).
### Evidence
- [M] Sections 2a and 2c: round 0 straight ahead 6% against 68 to 85%; through the portal by r10 3% against 32 to 88%; walked forward 1.12 to 5.06 pearls by r40 on that start (rank-1's real 5.62), 1.50 to 2.82 over the four layouts, 1.67 to 3.27 online; five variants within 2.74 to 2.84.
- [M] The rebuilt step changes on 13% of the second starter's ladder turns and 16% online; 98% of the changed steps on the ladder were the step really played, so the count is not an artefact of the rebuild.
- [C] 5483 and 1445: the heading exists and is not used.
### Expected signal
[E] o2_scan.py and o2_agg.py name no map and run on any replays of ours. Second starter on two-dragon starts: round 0 straight ahead where it is on offer, now 68% (6% on the start above), to 95% or more; steps straight ahead on blind turns 51% to 60% or more; through a portal by r10 on starts that have one within 12 steps 3% to 40% or more; its pearls by r40 1.35 to above 2.5 and its first pearl r51 to r25 or earlier (ladder base; online 2.08 and r19).
### What would show it's wrong
- Round 0 straight ahead stays under 80%: another path moves the dragon (stride, escape, route), or get_dir() is not the facing I assume after a portal step or at birth.
- The path changes and pearls by r40 do not rise on the start where it changed, or fall by more than 0.5 on the 25x25 start (now 5.2 online).
- Deaths of dragons of 4 or less in rounds 0-60 on a wall, their own body or with no step rise by more than a tenth: straight on led into dead ends.
- A pair of local games on a layout with a closed start shows a later exit than now.

Diff against data/online/smoke/agg8-bot/main.cpp:
```diff
@@ -22,1 +22,3 @@
 constexpr int TIE_SEED = 0;
+// Card: a short dragon that is not the queen breaks near-ties for the step straight ahead (0 = off, test 1.5).
+constexpr double HEADING_TIE = 0.0;
@@ -5483,2 +5485,6 @@
             score += 0.25 * ((TIE_SEED * 101 + ct.get_id() * 31 + round * 17 + static_cast<int>(k) * 7) % 5);
+            if (HEADING_TIE > 0.0 && length <= CENTER_MAX_LENGTH && !real_queen() && !is_leader() && !is_feeder() &&
+                scored[k] && score > SCORE_REJECT * 0.5 && direction == ct.get_dir()) {
+                score += HEADING_TIE;
+            }
```
Not a card, the centre pull. [M] It decides a third of the steps on the walled 32x16 start and a tenth elsewhere, and neither variant feeds the second starter sooner (2c); on 25x25 the walk without it eats 0.3 (ladder) to 1.1 (online) fewer. What it was bought for [read, losses/early-growth.md 64, the bot owner's notes, not re-run]: with CENTER_PULL 0 the local set won 7 of 8 on the walled start and lost three other layouts 0 of 8 each, so it stayed and card #51 added the release. docs/SESSION-STATE.md 108 lists a local arm with CENTER_PULL 0 started today; I read no result.

## 5. Against it
- [M] One layout. Of 5.06 - 1.12 the whole is the 25x35 start; 25x25 gains 0.7, the walled start loses 0.03, 24x12 moves nothing. There the dragon happens to face the portal. That a start faces something useful is a map maker's habit, not a rule, and the qualifier maps are unseen. On the mirrored side the same rule reaches the portal at r26, not r10 (the direction order and the noise are not mirrored), which is why the portal share is 44% and not 90%.
- [M] Rank-1 does not keep its heading in general (round 0 straight 33% over the four layouts, blind turns 52%). The card copies what rank-1 does on this start, not a rank-1 rule. diag-hungry counted that inside our games a dragon that kept its heading eats no sooner (24.4% against 26.1% within 20 turns; alone 23.0 against 18.1).
- [M] The walk forward is not a game. One virtual dragon; its children are not walked, the real queen and the enemy do not react, real dragons eat pearls on their real schedule. As built it gives 1.50 for a real 1.35 on the ladder, but 5.04 for 4.09 on 25x25 and 0.08 for 1.33 on 24x12 online (harvest and the portal-room rules are not rebuilt), so sizes are rough. Its deaths cannot be trusted either way.
- [M] Pearls are not wins: on 25x35 we win 25 of 34 on the ladder with the late start and 3 of 12 online. The card also reaches every non-queen dragon of 4 or less for the whole game, which nothing here measures; a round limit (the 0-19 variant gives 2.74) would keep it to what was measured at the cost of a second constant.
- [E] Countdowns are not in these replays; the soon, hot, spawn-clear and territory weights use rounds to the next real birth. Not rebuilt: threat terms (an enemy head is in view on 12% of turns), routes, harvest, the leader zone, sonar, a closed home on 600 cells or fewer; the queen's rows are weaker for it and are not used for the card.
- [M] The other half of that start is the queen: she finds the portal by r13 and may not take it. Lifting her ban is not proposed: it was bought after she died in a 4-tile room behind a portal at round 4 (findings.md F23).
- Not checked: that agg8-bot/main.cpp is the build that played agg8-q1 (the rebuild fits it at 95%); what get_dir() returns after a portal step and for a new child; no build and no game. Housekeeping: the Write tool is refused for this folder (path spelling), so files went through the Python route; scans ran plain, two at a time, about 12 minutes in all. Left in work/: 8 o2_ scripts, o2_scan-O0, -L0, -R0 and -test.jsonl (20 MB), o2_sim-O0 and -L0.jsonl. Nothing else was written.
