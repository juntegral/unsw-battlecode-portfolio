# aAah is a flat swarm that never feeds, larp is our plan with feeders that eat; the one line to copy is the feeder's (team 1119; 8 Oct 2026, data on disk at 16:27 KST)

## 1. Three lines
1. **Finding.** [M] aAah (105 fresh games, 81 won) keeps no leader and feeds nobody: 203 total length and 10 dragons of 6 or more at round 200 (Cutlery on the same layouts 128 and 3.3; ours 115 and 2.8), half Cutlery's boxed-in deaths, a pearl beside a head taken on 86% of turns (Cutlery 77%, ours 72%), a queen 3 long that is rammed in 26% of games (Cutlery 42%, ours 43%), 54% of games won by wiping the other side out. larp (86 games, 57 won) plays our own plan, a swarm and then a leader fed by small dragons that die beside it, and its leader ends 39.6 long against Cutlery's 28.2 and our 26.1, and its small dragons go on eating while they feed (ours stop). In our live build's 30 games against larp and Cutlery themselves (6 won) we eat as much per turn to round 100 (86.5 per 1,000 turns against 84 and 106), are rammed 6.5 times a game by then and ram 2.5, and after round 300 eat 52 to 68 per 1,000 turns to their 103 to 125.
2. **Change.** One card, FEEDER_EAT (default off): a feeder is paid for the pearl on its own step and keeps the nearer-than-the-leader exemption; one bool, two conditions. No second card: the other gaps are a label, already carded, tested and dropped, or the subject of the three sibling briefs (four leads at the end of section 4).
3. **How sure.** Sure of the counts: every game on disk, final state equal to the replay's own result in 832 of 832, and my scanner gives Cutlery's scoreboard marks within 7% on 11 of 11 rates checked. Sure the gap is ours alone: in the same situation four top teams take the pearl in 68 to 97% of turns and our three sets in 24 to 70%. Fairly sure of the cause (the code gives 520 against 440, and 520 minus 600; measured 59% and 33%), not certain: I rebuild the feeder flag from the true longest dragon and cannot read it from the bot. Small in results against the top: it acts after round 200 and those games are behind by round 100.

Labels: [M] measured by my scripts in dossier/work/ (ta_scan.py with ta_agg.py and ta_extra.py: the rates; ta_s2.py with ta_s2agg.py: steps per turn and the replay timelines; ta_s4.py with ta_s4agg.py and ta_card.py: the pearl beside the head), [C] read from data/online/smoke/agg8-bot/main.cpp (line), [E] estimate. A cell marked * rests on fewer than 20 games. Rates pool numerator and denominator over the column; "Cutlery matched" = Cutlery to 5 Oct re-weighted to the layouts of the column beside it (all 18 layouts covered).

## 2. Tables
### 2a. Fingerprint, the scoreboard's definitions [M] (pairs "a; b" as named in the row)
| Rate | aAah fresh (105) | aAah to 5 Oct (19*) | larp fresh (86) | Cutlery to 5 Oct (299 of 597) | Cutlery fresh (71) | chad gdp fresh (76) | ours B7Q (30) | ours main (90) | ours live v larp, Cutlery (30) |
|---|---|---|---|---|---|---|---|---|---|
| Won %; won by wiping them out % | 77; 54 | 79; 47 | 66; 33 | 65; 30 | 48; 24 | 53; 30 | 47; 23 | 23; 17 | 20; 10 |
| Opponent rating; last round (means) | 2245; 324 | 2223; 371 | 2243; 360 | 2186; 366 | 2467; 348 | 2390; 331 | 2196; 386 | 2216; 384 | 2464; 373 |
| Dragons; total length at r100 | 31.5; 95.8 | 28.0; 87.6 | 31.2; 81.9 | 24.6; 63.9 | 22.1; 55.0 | 24.5; 63.4 | 27.3; 69.0 | 25.8; 64.3 | 23.3; 58.7 |
| Total length; dragons of 6+ at r200 | 203; 10.1 | 168; 8.6 | 152; 5.1 | 115; 2.7 | 87; 1.6 | 124; 3.5 | 115; 2.8 | 95; 2.1 | 89; 1.1 |
| Longest; second longest at r300 | 13.2; 11.0 | 15.3; 11.1 | 26.8; 16.2 | 13.7; 8.5 | 11.3; 5.8 | 10.8; 8.0 | 14.2; 7.7 | 9.5; 6.2 | 8.2; 4.3 |
| Longest at the end | 12.1 | 15.2 | 39.6 | 28.2 | 19.3 | 18.7 | 26.1 | 17.9 | 15.3 |
| Pearls /1k turns r0-100; r101-300 | 84.8; 75.2 | 83.7; 73.2 | 85.2; 81.9 | 100.5; 83.2 | 95.3; 79.2 | 92.3; 90.9 | 83.9; 63.8 | 78.9; 55.3 | 86.5; 63.3 |
| Net length /1k (pearls minus length lost) r0-100; r101-300 | 41.6; 15.0 | 38.3; 11.8 | 34.3; 5.1 | 30.0; 6.6 | 25.8; 3.3 | 32.6; 8.3 | 34.3; 6.0 | 31.8; 2.7 | 29.4; 2.8 |
| Natural pearls born r101-300 that the side eats % | 68.4 | 64.4 | 56.4 | 57.0 | 41.6 | 61.9 | 47.2 | 38.2 | 35.0 |
| Pearl beside the head not taken % r101-300 | 13.6 | 13.6 | 19.7 | 21.6 | 23.6 | 18.4 | 27.9 | 29.9 | 23.2 |
| Their dead born r0-100 that the side eats % | 23.1 | 31.8 | 16.6 | 17.5 | 16.0 | 21.2 | 13.5 | 9.0 | 9.2 |
| Boxed-in deaths /1k r0-100 (no free tile; any label) | 10.2 | 8.4 | 14.6 | 20.9 | 20.2 | 8.1 | 15.3 | 15.2 | 17.6 |
| Label of that death | own body | own body | wall | illegal split | illegal split | no action | wall | wall | wall |
| Deaths with a free tile, not head-on /1k r101-300 | 0.47 | 0.68 | 3.76 | 1.01 | 1.19 | 9.09 | 4.19 | 1.70 | 2.16 |
| Head-ons started /1k r0-100; rammed /1k r101-300 | 2.27; 2.15 | 3.34; 2.43 | 2.72; 2.98 | 4.18; 3.03 | 4.49; 3.28 | 3.97; 3.04 | 1.83; 4.07 | 1.17; 4.58 | 1.91; 4.91 |
| Rams started by r100 a game (mover the longer %) | 4.1 (29) | 5.8 (30) | 4.7 (29) | 5.6 (38) | 6.0 (37) | 5.5 (31) | 2.6 (10) | 1.6 (12) | 2.5 (11) |
| Same-team head-ons /1k r101-300 | 0.04 | 0.06 | 0.01 | 0.30 | 0.28 | 0.26 | 0.13 | 0.12 | 0.12 |
| Turns of 2+ steps /1k r101-300; segments paid /1k | 167; 7.7 | 137; 10.2 | 76; 1.4 | 46; 5.5 | 30; 4.6 | 100; 14.6 | 32; 0.6 | 45; 0.4 | 16; 0.7 |
| Turns by dragons of 6+ % r101-300 | 19.0 | 19.9 | 9.4 | 7.0 | 4.7 | 9.0 | 3.6 | 4.8 | 2.1 |
| Splits by a parent of exactly 4 %; 4-long starters that split in round 0 % | 37; 93 | 31; 92 | 71; 98 | 61; 74 | 62; 62 | 52; 81 | 69; 4 | 65; 4 | 69; 4 |
| Blind direction kept % r101-300 | 45.9 | 38.2 | 60.1 | 49.1 | 49.1 | 49.7 | 36.3 | 36.7 | 36.0 |
| Repeated-spawn tile nearby % r101-300; portal steps /1k | 28.8; 10.5 | 32.6; 4.6 | 33.5; 10.9 | 36.8; 11.3 | 36.3; 12.4 | 34.6; 23.6 | 31.6; 13.1 | 26.1; 13.5 | 32.0; 12.0 |
| Queen r101-300: turns within R of her start %; own heads within 5 tiles | 28.5; 2.9 | 44.1; 2.5 | 58.2; 3.3 | 28.8; 2.2 | 46.2; 2.1 | 43.2; 2.3 | 33.8; 1.9 | 43.9; 1.9 | 47.6; 1.9 |
| Queen r101-300: enemy head within 5 tiles %; her mean length | 27.0; 3.1 | 32.7; 3.0 | 24.4; 5.6 | 33.7; 6.5 | 39.9; 3.7 | 27.5; 2.8 | 45.4; 4.0 | 35.1; 2.9 | 44.3; 3.7 |
| Own queen rammed (games %); dead at the end % | 26; 37 | 26; 32 | 37; 66 | 44; 70 | 54; 76 | 33; 55 | 43; 73 | 54; 82 | 57; 80 |
| Their queen rammed by the side (games %) | 64 | 74 | 49 | 65 | 35 | 49 | 43 | 33 | 30 |
- Check [M]: for Cutlery to 5 Oct my 299 games against scoreboard.md's 597: head-ons started 4.18 / 4.01, blind kept 49.1 / 49.1, pearl beside the head missed 21.6 / 21.7, natural harvest 57.0 / 56.7, wait 12.4 / 13.3, all deaths 27.9 / 27.2, splits 29.5 / 28.6, spawn tile 36.8 / 36.3, illegal split 21.2 / 19.8, first contact 12.2 / 12.6, portal steps 11.3 / 11.6.
- In every column an own queen alive with theirs dead won every game (53 of 53 for aAah, 20 of 20 larp, 57 of 57 Cutlery, 23 of 23 chad gdp, 3 of 3 ours) and the reverse lost every game (0 of 9, 17, 40, 15; ours 0 of 10, and 0 of 13 against larp and Cutlery). aAah reaches the first state in 50% of its games, larp 23%, ours 10%.
- Ours against larp; against Cutlery, same games, ours v theirs (15* each) [M]: dragons at r50 14.3 v 17.3; 11.9 v 15.3, at r100 21.7 v 33.1; 25.0 v 28.9; pearls /1k to r100 88.2 v 84.3; 84.6 v 106.3; rammed /1k to r100 5.0 v 1.5; 4.6 v 1.6; rams started by r100 2.7 v 7.1; 2.3 v 5.9; pearls /1k after r300 68.0 v 124.6; 51.8 v 103.2; pearl beside the head not taken after r300 34% v 22%; 41% v 30%; queen dead in 12 v 6; 12 v 8 games.

### 2b. Where aAah differs most from Cutlery (same layouts), and what the replays show [M]
1. One flat swarm, about half again the length: total 95.8 against 65.4 at r100 and 203 against 128 at r200, 10.1 dragons of 6+ against 3.3, longest at the end 12.1 against 29.0. No feeding at all: 0.47 deaths with a free tile per 1,000 turns (Cutlery 1.14, larp 3.76, ours 4.19).
2. Two-step turns 167 per 1,000 against 50. It is the same free second step we take, on five times the dragons: a dragon of 5 to 8 takes 2+ steps on 56 to 68% of its turns (ours 55 to 65% after r100, 3 to 12% before), and dragons of 6 or more hold 19.0% of its turns against our 3.6%. It also pays: 7.7 segments per 1,000 turns (ours 0.6), 42% of the paid turns end on a pearl, and 46% of its rams use a paid step (ours 26%).
3. Half the boxed-in deaths (10.2 against 20.1 per 1,000 turns to r100) on fewer pearls (84.8 against 98.2), so more net length (41.6 against 30.2; r101-300 15.0 against 6.9). Cutlery eats where it will be boxed in; aAah does not.
4. A pearl beside the head is not taken on 13.6% of turns against 22.6%, and 68% of natural pearls born in r101-300 are eaten against 58%. With no mate or enemy near and room behind the pearl it takes 96% (table 2d).
5. The queen: rammed in 26% of games against 42%, dead at the end in 37% against 69%, 3.1 long against 5.5. aAah starts fewer rams than Cutlery (2.27 against 4.04 per 1,000 turns to r100) and almost never hits its own (0.04 against 0.30).
- 1429033 (32 by 32, four starters of 4): all four split in round 0; the queen is back within 4 to 9 tiles of her start tile by r19 and stays to r150, splitting 4 into 2 + 2 at r22, 58, 80, 105, 120 and 133. Level at r59 (13 v 13 dragons); from r70 three rams every ten rounds, one for one, while it eats 12 to 20 pearls per ten rounds to their 1 to 4: 19 v 11 at r79, 31 v 4 at r109, their queen rammed at r107 by a 2-long.
- 1429831 (same board, against chad gdp): one dragon is left to grow to 6 by r19 and takes five free two-step turns (8 pearls in r10-19 to their 2), then splits 6 into 2 + 4 at r20 and an 8 into 2 + 6 at r35; 13 v 3 dragons at r39, their queen rammed at r75, its own queen 7 to 10 tiles from her start from r59 on.

### 2c. Where larp differs most from Cutlery (same layouts) [M]
1. With no pearl in view it keeps its direction on 60.1% of steps against 49.0% (ours 36.3%).
2. A leader sooner and longer: longest 26.8 against 14.6 at r300, second longest 16.2 against 8.8, 39.6 against 30.0 at the end (93 and 56 at the end on boards above 1,200 cells). Deaths with a free tile 3.76 per 1,000 turns in r101-300 against 1.27 (3.55 of them labelled no action, our own feeder label), 14 to 18 after r300.
3. The queen nearer home: 58% of her turns within R of her start against 25%, 3.3 own heads within 5 tiles against 2.4, and she splits at 4 from round 0.
4. More length from fewer deaths, not more pearls: total 81.9 against 67.9 at r100 on 85.2 pearls against 97.0, boxed-in deaths 14.6 against 19.8; 71% of its splits are at exactly 4 (Cutlery 57%).
5. It pays and collides less: 1.4 segments paid per 1,000 turns against 5.1, same-team head-ons 0.01 against 0.33, head-ons started 2.72 against 3.65.
- 1429179 (48 by 24, walled start, against SSS): the queen stays 2 to 11 tiles from her start with 1 to 12 own heads within 5 tiles and splits 4 into 2 + 2 ten times by r114; no ram before r99; 63 dragons at r149 and nothing longer than 5. 1428371 (32 by 32 open): two rams in the first ten rounds, 7 dragons until r49, the queen roams 15 to 26 tiles out and is rammed at r131 by a 2-long; larp still wins by elimination at r243.

### 2d. A pearl beside the head after round 100: turns on which it is taken % [M] (lone = not the queen, not the longest, no own head beside the pearl, no enemy head within 3 tiles, 2+ free tiles beside the head; feeding = round over 400, or over 200 with 56+ own dragons)
| Situation | ours B7Q (30) | ours main (90) | ours live v larp, Cutlery (30) | aAah (105) | larp (86) | Cutlery fresh (71) | chad gdp (76) |
|---|---|---|---|---|---|---|---|
| Lone 2 or 3 long, room of 3L+8 behind the pearl: before the leader round | 89 | 89 | 90 | 98 | 92 | 95 | 92 |
| the same: leader round passed, no feeding yet | 88 | 53 | 85 | 97 | 90 | 89 | 91 |
| the same: feeding, more than 15 tiles from the side's longest (or that longest under twice its length) | 69 | 63 | 70 | 97 | 90 | 86 | 85 |
| the same: feeding, within 15 tiles of the longest, pearl more than 9 from it | 59 | 49 | 50 | 95 | 92 | 80 | 85 |
| the same: feeding, within 15 tiles, pearl within 9 of it | 33 | 29 | 24 | 95 | 83 | 68 | 85 |
| Any dragon but the queen and the longest, feeding, pearl not in a one-tile nook | 62 | 56 | 59 | 90 | 80 | 77 | 81 |
| Lone, any phase, room behind the pearl under L+2; L+2 to 3L+7; a one-tile nook | 40; 66; 8 | 37; 57; 7 | 50; 71; 5 | 79; 94; 24 | 74; 85; 19 | 64; 78; 28 | 63; 84; 25 |
- Main without ZONE_NEARER took 53% once the leader round had passed and B7Q with it takes 88%: that switch did its job. What is left is the feeding phase: 119 turns a game in B7Q on which the pearl is passed (3,576 in 30 games), 49 a game against larp and Cutlery, 48 on main.
- A pearl first passed by a small dragon near our longest in the feeding phase goes to that longest in 26% of cases, to another mate in 46%, back to the decliner in 15%, to the enemy or nobody in 12%, a median 5 rounds later (ta_s3.py, B7Q). The same pearls of aAah and larp are gone in 1 to 2 rounds.

### 2e. Structure asked for in the brief [M]
- Fixed opening: none beyond the round-0 split. Two games from the same start share 2.2 leading rounds of identical actions for aAah (4 pairs*), 5.6 for larp (11 pairs*), 6.3 for ours (15 pairs*); counted on the first 22, 32 and 30 games.
- Guard around the queen: no dragon is told off to guard her that I can see; she has more company (2.9 and 3.3 own heads within 5 tiles to our 1.9) because she splits at 4 all game and stays near where the swarm is.
- Second long dragon: larp yes (16.2 at r300), aAah has no long dragon at all. Deliberate deaths: aAah none, larp and chad gdp as we do. Cutlery's illegal split (20 per 1,000 turns) is its label for a boxed-in death: with a free tile beside the head it dies 1.0 times per 1,000 turns.
- Portal steps, turns beside a repeated-spawn tile and enemies dying on the side's bodies (0.14, 0.08, 0.26 per 1,000 enemy turns; ours 0.13) are level with ours. All four top teams refuse a one-tile nook as we do.

## 3. Why, in the code
- [C] Who is a feeder (2326-2353): in the feeding phase (5002-5005; feed_round is 400, or 300 once the queen game is set at 536-547) every dragon that is not the queen, knows a leader at least twice its length (4995-5000) and is within 15 tiles (48, 2338) of that leader's last known place, which may be 25 rounds old (58, 1757).
- [C] What a feeder is paid: 3,000 less 60 a step to the drop tile (5241-5243); no EAT_BONUS for a pearl on its step (5144); no look-ahead (5361, 804); a pearl within 9 tiles of the leader costs 600 (5158-5160) and is no target (3004-3005), and the ZONE_NEARER exemption is refused to feeders by name (2392). The pearl goes on pulling: 2 x (260 - 40 a step) (5105-5110, 3335-3341), which is 520 on its tile and 440 beside it.
- [E] So a feeder beside a pearl outside the zone weighs 520 less up to 120 of feed pull against 440: a coin (measured 59%). Inside the zone it weighs 520 less 600: no (measured 33%; my zone is the true longest, the bot's is its remembered leader). It walks round the pearl instead.
- [M] 1421780, our leader 65 to 70 long 6 to 12 tiles away: dragon 1043 (3 long) starts beside a pearl on r426 at (22,13), r428 at (21,12), r429 at (21,11), r432 at (21,12) and r433 at (21,11) and steps away each time (to (21,13), (21,11), (20,11), (21,11), (21,10)); the pearls are at (22,12) and (22,11). Dragon 1393 does the same at (15,14) and (15,16) on r426, 428, 430 and 432.
- [C] A feeder of 2 that eats delivers 2 pearls where it would have delivered 1 (a dead dragon of L leaves L/2 rounded up); ready_to_die (571, 5007-5018) is tested before any step and is untouched.

## 4. The card
title: A feeder eats the pearl beside it (default-off FEEDER_EAT)
slug: feeder-eat
### Claim
[M] In the feeding phase our small dragons pass a pearl beside the head on 38% of turns (B7Q; 41 to 44% on the other two sets) where larp, Cutlery and chad gdp, which all feed a leader, pass it on 19 to 23%, and larp's leader ends half again as long as ours. [C] Proposal: add "constexpr bool FEEDER_EAT = false;" and let a feeder take EAT_BONUS and the ZONE_NEARER exemption. Every map, no round, no new state. With the switch off the build is the same.
### Evidence
- [M] Table 2d, rows 3 to 6: ours 24 to 70%, the four top teams 68 to 97%, and the three teams that feed 68 to 92%; the same order on all three of our sets.
- [M] After round 300 we eat 62 to 68 pearls per 1,000 turns (52 to 68 against larp and Cutlery), larp 121 to 128, Cutlery 88 to 108, chad gdp 96 to 127, and 39 to 43% of the natural pearls born then to larp's 49 and 67% and chad gdp's 58 and 72% (Cutlery 55 and 54% to 5 Oct; 38 and 27% fresh, half of it against aAah).
- [M] Feeding more does not need eating less: larp has 14 to 18 deaths with a free tile per 1,000 turns after r300 against our 9 to 10 and its final longest is 42 and 93 (boards up to and above 1,200 cells) against our 29 and 48.
- [C] Section 3: 520 against 440, and 520 less 600. [M] The replay turns of section 3.
### Expected signal
[E] ta_s4.py then ta_card.py on any replays of ours, no map named: "any dragon but the queen and the longest, feeding" from 62% to 78% or more (larp 80, Cutlery 77, chad gdp 81); the two "within 15 tiles" rows from 59 and 33% to 75% or more; pearls per 1,000 turns after r300 up from 62 to 68; final longest not below 26.1; deaths with a free tile after r300 not below 8.8 per 1,000 turns. It reaches 119 turns a game in B7Q (3,576 in 30 games; 179 a game in the 20 that reach feeding), 1,467 in the 30 games against larp and Cutlery, 4,347 in the 90 main games; at larp's rate that is about 55 more pearl steps a game.
### What would show it's wrong
- The feeding rows stay under 70%: another term decides; log the terms of one such turn before tuning.
- Final longest falls, or deaths with a free tile after r300 fall by a third: feeders stopped arriving.
- Any turn of a dragon that is not a feeder changes, or any turn before the feeding phase: the switch reached code it should not.
### Diff (agg8-bot/main.cpp)
    66   constexpr bool ZONE_NEARER = true;
    +    constexpr bool FEEDER_EAT = false;
    2392 -        if (ZONE_NEARER && !is_feeder() &&
         +        if (ZONE_NEARER && (FEEDER_EAT || !is_feeder()) &&
    5144 -        if (pearl_here[index_of(destination)] && !is_feeder() && !in_leader_pearl_zone(index_of(destination)) && !pocket_full) {
         +        if (pearl_here[index_of(destination)] && (FEEDER_EAT || !is_feeder()) && !in_leader_pearl_zone(index_of(destination)) && !pocket_full) {
Leads, no card, by size [E]: (1) Rams. [C] 2726 lets a trader ram only a head at least its own length and 2719 only when we outnumber in view; [M] our mover is the longer in 7 to 12% of rams, theirs in 26 to 38%, and we start 1.6 to 2.6 by r100 to their 4.1 to 6.0 (5.9 and 7.1 against us). The topfight brief owns it. (2) The queen. [C] QS_KEEP_LEN 3 (137, 1057) keeps ours at 3 to 5; [M] both top queens split at 4 from round 0 and have half again our company. The topqueen brief owns it; QUEEN_HOME_LEASH is already carded. (3) Round-0 split of 4-long starters: 93, 98, 81 and 62 to 74% against our 4%; the lead of diag-opening, about one dragon-turn a starter. (4) Small rooms: lone, room under L+2 we take 40% to their 63 to 79%. CRAMPED_EAT covers only the next class up and was tested and dropped on 8 Oct (bundle 105 to 98 wins in 128 pairs, docs/SESSION-STATE.md 08:40); not offered again.

## 5. Against it
- [M] It is a late switch. Against larp and Cutlery we hold 21.7 and 25.0 dragons at r100 to their 33.1 and 28.9; 13 of the 24 losses had our queen dead and theirs alive, and 9 were wipe-outs. The card moves none of that. Its games are those that reach feeding: 20 of 30 for B7Q, 18 of 30 against the two.
- [M] The feeder and zone rows are a rebuild from the true board (the side's longest, 15 and 9 tiles, the unit count), not the bot's flags; the largest row (feeding, far from the true longest, 26 passed turns a game) I explain by a remembered leader up to 25 rounds old, which I did not check. For aAah the rows are not feeding at all; the fair controls are larp, Cutlery and chad gdp.
- [M] Opponents are not held equal. Layouts are matched for the Cutlery comparisons; ratings are not (aAah's fresh opponents average 2245, ours 2196, the direct set 2464). aAah's column moved when stronger opponents arrived (enemy head near its queen 13% on the first 22 games, 27% on 105).
- [E] Larp's longer leader may come from its whole economy and not from its feeders eating; I count the step, not what the leader gains. A pearl switch that measured well (CRAMPED_EAT) lost games in the bundle.
- [C] A feeder that eats up to 4 may split (1040-1094 has no feeder test); two feeders of 2 deliver what one of 3 does, so I left it. Line 5146 (the pocket bookkeeping twin of 5144) is not in the diff. Nothing was compiled or played.
- [M] The steps-per-turn figures of 2b.2 are on the 16:10 cut (61 aAah, 59 larp games); the collector was still adding battles; top-l2 (against aAah) had not arrived. Cutlery to 5 Oct is every other game (299 of 597).
- Housekeeping: the Write tool and shell redirects are refused for this folder (path spelling), so scripts and this file went through Python. Never more than 2 scan processes at once, about 40 minutes in all. Left in work/: 11 ta_ scripts and 30 output files (ta_index, ta_scan-*, ta_s2-*, ta_s3-*, ta_s4-*; 64 MB, one of them a 2-game test). Nothing else was written.
