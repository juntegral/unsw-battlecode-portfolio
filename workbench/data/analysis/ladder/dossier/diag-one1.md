# one1's own games: on big maps the swarm stops growing at round 201 because the 56-dragon rule starts the feeding phase there (team 1119; 40 games of the live model, 8 Oct 2026 22:35-23:05 KST)

1. **Finding.** The "we stop growing after r100" of the WHQ table is two different things. On the 10 maps of 1200 cells or fewer nothing is lost in r101-300 (ours +22.7 length a game, WHQ +26.3); those games are decided earlier or by the queen. On the 5 big maps we are level to round 200 (204 against 223) and then fall to 155 while WHQ goes to 310. The fall starts in one round: in all 7 games of the live model where we hold 56 or more dragons at r200, the first dragon that dies on purpose does so in round 201 or 202. From there natural pearls drop by a third at once (53 per 25 rounds before, 37 after; theirs 62 then 67 to 79), 21 to 81 short dragons a game die on purpose in r201-300, and the leader they build is rammed by a dragon of 2 to 5 (16 leaders of 10 to 56 long in 6 of the 7 games, r201-400). Our longest is 24 at r225 and 28 at r400; theirs, with no feeding before r350, is 37.
2. **Change.** Card 1: `FEED_CAP_ROUND` 200 -> 350 (main.cpp:78), so that 56 dragons no longer start the feeding phase 150 rounds before the other side folds. Card 2 (not new, both earlier diagnoses reached it; one1's games confirm it): `RALLY_END_FRESH` 0 -> 25 (main.cpp:277). No card for the queen: `QUEEN_DEFEND_STEPS` cannot fire as built (39 mate turns in 15 games had a head within 3 steps of her in view, 2 of them inside the mate's ram reach, both rammed).
3. **How sure.** High that the cap is what starts the fall (7 of 7 games to the round, the step in pearls is in the capped games and not in the 3 uncapped ones, the line in the code says so). Medium that moving it gives the length back: the swarm then sits at 60 dragons that cannot split and must grow longer, which ours did only slowly in r150-200 (+26 in 50 rounds against their +36). Low that it turns results by itself: it reaches 6 of 29 losses, and those are lost on longest or queen, not on total.

Labels: [M] measured by my scripts in dossier/work/ (`o1_scan.py` replays a game: every death with cause, length, free tiles and who ate its pearls, every pearl eaten by origin, paid segments, splits, a snapshot every 25 rounds; `o1_ledger.py`, `o1_net.py`, `o1_bins.py`, `o1_dead.py`, `o1_shape.py` print the tables; `o1_strike.py` + `o1_striketab.py` the first strike; `o1_qdef.py` the queen's mates; `o1_rams.py` rammer steps). The ledger closes in every game: end total = start + eaten - dead - paid, residual 0 on both sides. [C] read from `data/online/smoke/one1-bot/main.cpp`, line given. [E] estimate.
Samples: w1 = one1 against WeHaveQuizzes (15), d1 = one1 against dev test 1 (15), live = ranked battles played by submission 20850 (10 games: 1461163-67 Cache me outside, 1462081-85). Battles b1459601 and b1460075 in `live-one1/` were played by other submissions (20835, 20366; the bot id is in the replay) and are left out. v62 for reference: nc62-whq1-old and the WHQ half of agg8-q1-new.
Terms: "boxed" = dies with no free tile beside its head (wall, own body, a mate's body or no action). "Stop" = dies by no action with a free tile (the feeder's death). "Rammed" / "rams" = victim / mover of a head-on between the sides. Net loss = length of the dead minus their pearls eaten again by the own side. Big = more than 1200 cells. Capped game = big map, 56 or more of our dragons at the end of r200.

## 1. Where the length goes, r101-300 (question 1)

### 1.1 The gap is on the big maps [M]
| one1 against WHQ, r101-300, per game | 10 small maps, ours | theirs | 5 big maps, ours | theirs |
|---|---|---|---|---|
| total length r100 -> r300 | 44.5 -> 67.2 | 40.6 -> 66.9 | 132.6 -> 155.4 | 126.4 -> 310.2 |
| dragons r100 -> r300 | 17.8 -> 25.3 | 16.6 -> 26.5 | 50.8 -> 53.8 | 44.0 -> 61.2 |
| + natural pearls | 154.6 | 151.9 | 376.6 | 462.8 |
| + pearls of the other side's dead | 12.4 | 14.5 | 58.8 | 109.4 |
| - rammed: dragons / length / net loss | 13.7 / 37.8 / 26.9 | 5.5 / 15.8 / 11.4 | 63.4 / 219.6 / 180.8 | 27.2 / 97.0 / 69.4 |
| - rams: dragons / length / net loss | 5.5 / 14.1 / 8.9 | 13.7 / 38.5 / 20.8 | 27.2 / 66.6 / 38.8 | 63.4 / 190.6 / 94.0 |
| - boxed: dragons / length / net loss | 90.4 / 213.5 / 94.7 | 68.5 / 157.0 / 71.7 | 109.0 / 264.2 / 130.8 | 118.4 / 318.2 / 163.6 |
| - stop: dragons / length / net loss | 5.6 / 11.8 / 5.8 | 3.9 / 10.8 / 4.6 | 28.4 / 71.6 / 34.2 | 1.2 / 5.2 / 2.2 |
| - other own moves, mate heads: net loss | 6.7 | 14.4 | 26.8 | 30.0 |
| - paid sprint segments | 0.0 | 15.5 | 1.6 | 24.8 |

"441 pearls eaten for +23" in the 4-column table counts the pearls of our own dead eaten again (184 a game): a boxed dragon of 2 drops 1 pearl and a mate eats it. Net of that we take in 257 from outside (229 natural + 28 of their dead) and they 302.

It is many short dragons, not a few long ones: of 163 of our deaths a game in r101-300, 105 are 2 long, 48 are 3, 5 are 4, 4 are 5 to 9 and 1.1 are 10 or longer (17.6 length). The long ones matter on the big maps only (43.6 length a game rammed at 10+, see 1.3).

Boxed deaths are the price of pearls in dead ends and both sides pay it alike (ours 99 dragons a game, theirs 88; 52 against 59 of all deaths come within one round of a split; [E] that is the trapped front half left behind when the tail half is split off and walks out). No card there.

### 1.2 The big maps break at round 201 [M]
Per game, the 5 big maps against WHQ, by 25 rounds:
| rounds | our dragons | our total | our longest | our natural pearls | our stops (dragons / length) | their total | their natural pearls | their stops |
|---|---|---|---|---|---|---|---|---|
| 101-125 | 59.2 | 163.6 | 7.2 | 64.2 | 0 | 155.2 | 58.0 | 0 |
| 126-150 | 60.4 | 186.2 | 9.8 | 59.0 | 0 | 169.8 | 52.4 | 0 |
| 151-175 | 58.6 | 191.8 | 13.2 | 51.2 | 0 | 188.0 | 51.0 | 0 |
| 176-200 | 58.2 | 203.6 | 15.8 | 54.0 | 0 | 222.6 | 58.6 | 0 |
| 201-225 | 54.6 | 181.8 | 24.0 | 37.2 | 11.6 / 32.4 | 253.2 | 57.8 | 0 |
| 226-250 | 54.8 | 175.8 | 25.2 | 36.2 | 7.0 / 16.2 | 266.2 | 62.4 | 0 |
| 251-275 | 54.2 | 157.8 | 16.0 | 39.6 | 5.4 / 13.0 | 283.2 | 59.8 | 0.2 |
| 276-300 | 53.8 | 155.4 | 17.2 | 35.2 | 4.4 / 10.0 | 310.2 | 62.8 | 1.0 |
| 301-350 | 53.2 | 152.0 | 17.0 | 73.2 (two bins) | 7.4 / 16.8 | 327.0 | 130.8 | 4.8 |
| 351-400 | 53.8 | 157.6 | 17.6 | 76.8 | 11.2 / 24.8 | 310.4 | 122.2 | 26.6 |
| 401-499 | 34.4 | 183.4 | 43.0 | 134.6 | 36.8 / 98.2 | 244.4 | 173.4 | 71.8 / 289 |

The 7 capped games of the live model (w1 Australia, Islands, Around UNSW, Slithery Fight; d1 Around UNSW, Slithery Fight; live Slithery Fight):
- first stop in round 202, 202, 201, 201, 201, 201, 202;
- natural pearls per 25 rounds, r101 to r400: 64.6, 62.7, 52.7, 52.7 | 37.3, 38.6, 40.3, 37.0, 30.0, 38.9, 29.6, 39.7 (theirs 68.3, 65.4, 61.6, 63.0 | 67.1, 69.6, 73.1, 79.0, 75.0, 80.6, 76.1, 74.4);
- our total r200 / r225 / r250 / r300 / r400: 212 / 190 / 184 / 168 / 167 (theirs 227 / 245 / 252 / 279 / 283); ours grew r200 -> r300 in 1 of 7, theirs in 6 of 7;
- stops in r201-300: 25, 35, 42, 38, 21, 81, 69 dragons (77 to 208 length);
- our longest r200 / r225 / r400: 14.3 / 23.9 / 28.0; theirs 12.3 / 13.6 / 37.1.
The 3 big-map games with 25 to 55 dragons at r200 (w1 Schooltime, d1 Islands, live Australia): first stop in round 254, 406, 434; natural pearls per 25 rounds flat (28.7, 25.3 | 27.7, 29.0, 28.7, 33.3); total r200 -> r300 93 -> 111.
Natural pearls per 100 dragon-rounds, r101-200 against r201-300: capped 3.4 -> 1.8, 3.6 -> 3.0, 3.2 -> 2.4, 5.7 -> 2.9, 2.7 -> 2.1, 4.5 -> 3.5, 4.7 -> 3.0; the other side in the same games 3.7 -> 3.6, 4.3 -> 3.5, 4.0 -> 3.9, 5.0 -> 5.1, 6.2 -> 6.0, 4.8 -> 6.3, 4.4 -> 5.3.

[C] The rule: `feeding_phase()` (main.cpp:5543-5546) is true after `feed_round` (400, or 300 in a queen game) **or** when `round > FEED_CAP_ROUND` (200, line 78) and the side has `FEED_CAP_UNITS` (56, line 77) dragons. In that phase every dragon within 15 tiles of the leader and half its length or less becomes a feeder (`pick_feed_target`, 2417-2445), walks to a drop cell and dies there (`ready_to_die`, 5548-5559 and `act` 635-638; FEEDER_REWARD 3000 against a pearl's few hundred). The count then falls under 56, the phase ends, the 4-long split again, the count passes 56 and the next feeders die: our dragon count sits at 53 to 55 from r201 to r400 and nearly every dragon stays 2 or 3 long (r300: 30.8 of 2, 19.4 of 3, 1.0 of 5 to 9; theirs 19.2, 14.2 and 13.2 of 5 to 9, 7.6 of 10+). v62 has the same rule (first stop r201 to r218 in its capped games); one1's better opening only reaches 56 dragons in more games and sooner (by r150 in all 7).
[M] What WHQ does in those rounds that ours does not: nothing special. It sits at 60 to 64 dragons that cannot split and lets them grow (total 223 -> 310), and it starts stopping at r351 (10 dragons in r351-375, 17 in r376-400, 46 in r401-450), 150 rounds after us.

### 1.3 The leader that the feeders build is rammed [M]
Our dragons of 10 or longer rammed in r201-400 in the 7 capped games: Australia 37 (r263, by a 4 from 1 step); Islands 10, 12, 10, 21; Around UNSW 28 (r227), 29 (r266), 11 (r275); Slithery 12, 11; d1 Around UNSW 13, 16, 19; d1 Slithery 21 (r235), 37 (r284, by a 2 from 1 step), 56 (r369, by a 3); live Slithery none. 16 leaders, 343 length, and the other side eats most of the drop (Australia r263: 10 of 19 pearls to them). Of our 19 dragons of 10+ that died in those rounds 16 were rammed. Theirs lose such dragons to our rams too (26 of their 77 deaths at 10+, the rest boxed 39, stop 10, as rammer 2), but they hold 8 to 11 dragons of 10+ at a time from r300 and we 1 to 3, all of our stored length in one body.

### 1.4 Head-ons: who starts gets the pearls [M]
Against WHQ, big maps, r101-300, per game: they start 63.4 head-ons, we 27.2. A head-on they start costs their side 0.2 length net and ours 2.6 (they eat 180 of the 237 pearls both dead drop); one we start costs us 0.4 and them 2.2 (we eat 55 of 93). Their rammer comes from 1 / 2 / 3+ steps in 23.0 / 28.6 / 11.8 cases, ours in 19.4 / 6.2 / 1.6; a 3 of theirs rams a shorter dragon 18.2 times a game, ours 0.4 times (the parts >= length test at line 2818). With an enemy head inside its ram reach a dragon of ours of 2 to 4 rams on 17% of turns, theirs on 34%; when ours does not, the local-edge test (line 2811) alone is shut on 46 turns a game, the parts test alone on 30, two or more on 57. Being rammed after declining is no more common for us than for them (9% both), so first strike adds rams of ours and does not remove many of theirs (12 of the 63). This is b-rams' ground; the numbers are here for it.
The ratio holds everywhere: rams on ours to rams on theirs, whole games: WHQ 788 : 355, dev test 1 584 : 273, ranked 259 : 212.

## 2. The queen, r150 on (question 2) [M]
One1's queen deaths in the 40 games: 22 rammed, 11 boxed (9 of them 2 long), 1 ran into a head, 6 alive at the end.
- **From how far.** The rammer's own steps in its last turn: 1 step 5, 2 steps 3, 3 steps 5, 4 steps 6, 5 or 6 steps 3. So 14 of 22 come by a sprint of 3 or more, by a dragon of 3 or 4 that was outside her 3-step ring when she and her mates last moved (Islands 1460557 r207: she is 7, a 3 runs 4 steps; Default 1460562 r157: a 4 runs 4; Slithery 1460569 r274: a 13 runs 5).
- **Her mates.** No mate within 5 tiles at the hit in 12 of 22; in the other 10 there were 1 to 8 mates within 5 and none could act.
- **Why QUEEN_DEFEND_STEPS fired twice.** [C] `guards_queen` (2827-2854) needs the mate to be 4 or shorter, to see her and the head, and the head within 3 steps of her; the ram itself then needs the head inside the mate's own reach over free tiles (`ram_path`, 2870: 1 step for a 2, 2 for a 3). [M] Against WHQ 39 mate turns in 15 games met the first three conditions; the head was inside the mate's reach in 2 (both rammed), 2 to 6 steps off in 12 and behind bodies or kelp in 25. Dev test 1: 38 turns, 2 in reach, 2 rammed. Ranked: 63, 3, 3. The switch does what it says; the case almost never exists, because her mates are 2 and 3 long and the pursuer strikes from beyond 3 steps. d1 Slithery 1461142 r298 shows it: 8 mates within 5 tiles, two see a 3 two steps from her, neither has a free path to its head, it rams her next move.
- **Boxed at 2.** 8 of her 11 boxed deaths are at length 2 between r83 and r183 on maps of 1152 cells or fewer, with 1 to 7 mates within 5 tiles (Maze r183, Portals r162; dev test 1: weakhold r88, Maze r83, Stripes r84, Tower Defense r92, Devil r92). Five of them are against dev test 1. I did not separate "boxed by the mates she herds with" from "boxed by kelp"; it is the next thing to look at for the queen, not a card.

## 3. Does it hold against the others (question 3) [M]
| | one1 v WHQ (15) | one1 v dev test 1 (15) | one1 ranked (10) |
|---|---|---|---|
| won | 4 | 1 | 6 |
| lost by elimination / queen / longest | 4 / 4 / 3 | 6 / 5 / 3 | 2 / 1 / 1 |
| small maps: total r100, ours / theirs | 44 / 41 | 28 / 54 | 37 / 34 |
| big maps: total r100 | 133 / 126 | 81 / 164 | 106 / 138 |
| big maps: total r200 -> r300, ours | 204 -> 155 | 108 -> 96 | 131 -> 150 |
| big maps: total r200 -> r300, theirs | 223 -> 310 | 274 -> 338 | 230 -> 264 |
| capped games / first stop in r201-202 / ours shrank r200-300 | 4 / 4 / 4 | 2 / 2 / 2 | 1 / 1 / 0 |
| rams on ours : on theirs, a game | 52.5 : 23.7 | 38.9 : 18.2 | 25.9 : 21.2 |
| queen rammed / boxed / alive at end | 10 / 3 / 2 | 8 / 6 / 1 | 4 / 2 / 3 (1 ran into a head) |
| queen alive r100 / r150 / r300 | 11 / 8 / 3 | 8 / 3 / 2 | 8 / 5 / 4 |

- The cap (section 1.2) holds wherever we reach 56 dragons: 7 of 7 games, three opponents.
- "Early game fixed" is WHQ only. Dev test 1 eats 74 natural pearls to our 47 in r1-100 on small maps and 215 to 110 on big ones, and is twice our length at r100 on both. That is a different problem (their opening), and one1 reaches the cap in only 2 of its 5 big-map games there.
- The ram ratio and the queen's manner of death hold against all three.

## 4. Cards (question 4)

### Card 1. The 56-dragon rule starts the feeding phase at round 350, not 200
- **Rule.** When the side has 56 or more dragons, dragons near the leader become feeders only after round 350 (today 200); before that they keep eating, and at 60 dragons they grow instead of splitting.
- **Where.** `constexpr int FEED_CAP_ROUND = 200;` main.cpp:78 -> 350. It is read once, in `feeding_phase()` at 5543-5546. Nothing else changes: `board_short()` (3732) is already false at 56 dragons, so the leader and its pearl zone exist from r150 as today. (350 is where WHQ's own stops begin. `FEED_CAP_UNITS = 0`, line 77, is the plainer variant: feeding at r400 only, r300 in a queen game.)
- **Reaches.** The capped games: 6 of one1's 29 losses (w1 Australia, Islands, Around UNSW, Slithery; d1 Around UNSW, Slithery), every big map we open well on.
- **Works if** (capped games): first stop not before r351 (today r201-202 in 7 of 7); natural pearls per 25 rounds in r201-300 stay near the r151-200 level (today 53 -> 37); total at r300 above total at r200 (today 1 of 7 games); dragons of 5 to 9 at r300 well above 1.
- **Wrong if:** the total still falls after r200 with no stops (then the rams are the cause and not the cap); or the length rammed away from dragons of 5+ in r201-350 grows by more than the 72 a game that the stops cost today; or our longest at the end is shorter than today's 43 (the 5 big maps against WHQ) (feeding then has 150 rounds and not 300; today's 200 early rounds bought 14 length of leader, 14 -> 28, and 16 dead leaders).
- **Sure:** high on the diagnosis, medium on the effect (E about +70 to +100 total at r300 in capped games: 15 natural pearls per 25 rounds back and 34 net no longer lost to stops), low on results alone.

### Card 2. After the feed round a short dragon walks to the leader it knows (the rally; diag-longest and diag-whq card, unchanged)
- **Rule.** After `feed_round`, a dragon that may feed, is further than 15 tiles from the leader it knows and heard of it within 25 rounds, walks to it.
- **Where.** `constexpr int RALLY_END_FRESH = 0;` main.cpp:277 -> 25; read in `rally_ready()` 5526-5534, used at 670-672.
- **Reaches.** The games lost on longest with our dragons unspent: w1 Australia (end 59 dragons, total 232 against 191, longest 24 against 67), Around UNSW (56 dragons, 297 against 236, 31 against 82), Islands (24, 158 against 135, 50 against 62), d1 Maze (20, 119 against 160, 53 against 75), and with card 1 it is what turns the extra length into the leader. 4 to 5 of 29, overlapping card 1 in 3.
- **Works if:** dragons alive at the end on big maps fall from 34 towards WHQ's 16; stops in r401-499 rise from 37 a game towards their 72; longest at the end up.
- **Wrong if:** the walkers are rammed on the way (rammed deaths of 2 and 3 long in r401-499 up by more than stops rise), or the leader dies with more in it (one ram loses everything: section 1.3).
- **Sure:** as the two earlier reports: medium that it fires, about one in three that it changes results. I add only that one1 loses these games in the same way, with more dragons left over than v62 had.

### Looked at and not carded
- Queen: `QUEEN_DEFEND_STEPS` cannot fire as built (section 2); a wider ring would not help while her mates reach 1 or 2 steps. No measured rule that reaches a quarter of her deaths.
- The fed leader rammed (16 in 7 games): real and large, but the switch for it (`LONG_SAFETY`, lines 150-153, card #54) is a team mate's and I did not measure it.
- First strike: section 1.4, for b-rams.
- Elimination on small maps (12 of 29 losses): decided before r150; nothing in r101-300 separates the sides there against WHQ, and against dev test 1 it is the opening.

## 5. Replay moments
- w1 1460556 Australia: r200 60 dragons, total 202; r202 first stop; 25 stops by r300; r263 the leader, 37 long, rammed by a 4 from one step, 10 of its 19 pearls eaten by them; total 122 at r300 (theirs 147 -> 303).
- w1 1460561 Around UNSW: r201 first stop; leaders rammed at r227 (28), r266 (29), r275 (11); total 199 -> 147; game lost on longest 31 against 82 with 56 of our dragons alive.
- d1 1461142 Slithery Fight: r201 first stop, 81 stops in r201-300; leaders rammed at r235 (21), r284 (37, by a 2), r369 (56, by a 3); queen rammed r298 with 8 mates within 5 tiles.
- Not capped, for contrast: d1 1461130 Islands, 31 dragons at r200, no stop before r406, total 69 -> 102 in r200-300.

## 6. Added 23:13: the cards against one2 and against dev test 1
All ranked games counted above are submission 20850 (one1), checked by the bot id in each replay; none is one2. one2 = submission 20880, `one2-w1-old`, 15 games against WHQ, 6 won (set `o2` in `o1_scan.py`).

### 6.1 Card 1 on one2 [M] (4 capped games: Islands, Around UNSW, Schooltime, Slithery Fight; Australia had 50 dragons at r200)
| capped games against WHQ, per game | one1 (4) | one2 (4) |
|---|---|---|
| first stop | r202, 202, 201, 201 | r202, 201, 201, 201 |
| stops r201-300 | 25, 35, 42, 38 | 20, 51, 23, 63 |
| our natural pearls per 25 rounds, r151-200 | 52.2, 55.0 | 48.2, 47.0 |
| r201-300 | 34.8, 35.0, 39.0, 34.2 | 35.5, 41.2, 48.5, 51.2 |
| our total r200 / r225 / r250 / r300 / r400 | 217 / 190 / 182 / 160 / 164 | 198 / 174 / 172 / 191 / 188 |
| their total r200 / r300 / r400 | 212 / 282 / 275 | 232 / 279 / 251 |
| our longest r200 / r300 / r400 | 15.5 / 17.0 / 20.5 | 12.0 / 28.5 / 39.2 |
| our leaders of 10+ rammed r201-400 | 10 | 10 |
| rams on theirs r101-200 / r201-300 / r301-400 | 13.0 / 15.0 / 20.8 | 28.0 / 21.0 / 16.2 |
| rams on ours, same windows | 25.0 / 35.8 / 32.5 | 28.8 / 29.2 / 25.0 |
| snapshots r225-400 with fewer than 56 of our dragons | 18 of 32 | 13 of 32 |

- The cap fires in one2 exactly as in one1 (now 11 of 11 capped games of the two builds, first stop r201 or r202) and costs the same first 50 rounds (total 198 -> 172). one2 then recovers by r300 where one1 did not, and keeps a longer leader (39 at r400 against 20). Four games each; I would not read more than the direction.
- New with one2: `ATTACK_MIN_UNITS` and `FEED_CAP_UNITS` are both 56 (one2 main.cpp:105 and :77). The feeding phase kills feeders until the count is under 56, which is where the two attack switches turn off. one2's rams on theirs are level with theirs on ours while it holds 60 dragons (r101-200: 28.0 against 28.8, one1 13.0 against 25.0) and fall to 21.0 and 16.2 after r200, with the count under 56 at 13 of 32 snapshots. [E] Card 1 therefore does two things in one2: it removes the r201 dip and it keeps the count at 60, so the attack switches stay on to r350. That makes card 1 worth more on one2 than on one1, not less.
- Wrong-if for card 1 on one2 is unchanged, plus: rams on theirs in r201-350 should stay near the r101-200 level (28 a game); if they fall anyway, the count is not what turns them off.
- Card 2 on one2: the two big-map losses are Australia (ends with 53 dragons, total 242 against 179, longest 32 against 56) and Schooltime (49 dragons, 160 against 308, 14 against 76). The rally reaches the first. one2's three big-map wins also end with 48 to 59 dragons unspent and margins of 55 against 48 and 55 against 50 on longest.

### 6.2 Which opponent the cards reach
| one1 losses | WHQ (11) | dev test 1 (14) | ranked (4) |
|---|---|---|---|
| card 1 (capped big-map games) | 4 | 2 (Around UNSW, Slithery Fight) | 0 |
| card 2 (lost on longest with dragons unspent) | 3 (the same big maps) | 1 (Maze) | 1, weak (Australia: 27 dragons, total 120 against their longest 77) |
| reached by neither | 7 | 11 | 3 |

Dev test 1 beats us in a different way from WHQ and the cards do not reach it. WHQ is level with one1 to r200 and wins the middle game on big maps and the queen on small ones. Dev test 1 wins the first 100 rounds: 74 natural pearls to our 47 on small maps and 215 to 110 on big ones, twice our dragons and length at r100 on both (22.0 / 53.7 against 11.3 / 28.2; 52.0 / 164 against 32.4 / 81), queen alive at r150 in 3 of 15. In 3 of its 5 big-map games we hold 10 to 31 dragons at r200 (two never reach 56, one reaches it at r400), so the cap does not fire there. Its ram ratio on us is the same as WHQ's (2.1 to 1). Both cards are WHQ-shaped: they reach games where we open level and hold 56 dragons.

## 7. Added 23:36: card 1 on local games (job A) [M]
one3 = one2 + `FEED_CAP_ROUND` 350, against one2 on the same map, seed 1 and side: arms `m9f3_vh` / `m8o2_vh` against the queen hunter (5 big maps) and `m9f3_vb` / `m8o2_vb` against plain main (3 big maps). 16 pairs, 14 of them with 56+ dragons at r200 (the two Schooltime games hold 36 and 37 and are left out). Every pair is identical to r200 (total 449 both). Scripts `o1_local.py`, `o1_localtab.py`.

| 14 capped pairs, mean per game | one3 | one2 | one3 higher / lower |
|---|---|---|---|
| first on-purpose stop | r351 | r204 | |
| feeders dead r201-300 | 0 | 44 | |
| natural pearls per 25 rounds r201-300 (r151-200: 133 both) | 140 | 130 | 11 / 1 |
| total length r300 | 490 | 426 | 10 / 4 |
| total length r350 | 489 | 436 | |
| total length at the end | 470 | 443 | 11 / 3 |
| our longest r300 / r400 | 30 / 49 | 50 / 67 | |
| our longest, peak at a 25-round snapshot | 72 | 108 | 3 / 11 |
| our longest at the end, mean (median) | 59.9 (48.5) | 81.9 (57.0) | 6 / 6, 2 equal |
| ours minus their longest at the end, mean (median) | +4.0 (+8.0) | -1.8 (-5.5) | |
| dragons of 5-9 / 10+ at r300 | 14.9 / 18.2 | 9.6 / 12.3 | |
| length rammed off dragons of 5+ in r201-350 (net of pearls eaten back) | 449 (304) | 367 (247) | 9 / 5 |
| length of feeders dead r201-350 (net) | 1 (1) | 292 (143) | |
| rams on us / by us, r201-350 | 38.4 / 32.5 | 28.6 / 46.4 | by us lower in 12 |
| games won | 8 | 7 | hunter 6 v 7, main 2 v 0 |

- The switch does what it says and nothing else moves before r200. No crash, no stall, 56-58 dragons to the end.
- The works-if rows hold: first stop after r350, pearls up in 11 of 14, total at r300 above r200 (490 against 449; one2 falls to 426), dragons of 5 to 9 up. The wrong-if row holds narrowly: the stops no longer cost 143 net, rams on our longer dragons cost 57 net more.
- Side effect I had not foreseen (and section 6.1 guessed the other way): we ram a third less and are rammed a third more in r201-350, because dragons that are not fed away outgrow the trader length (`TRADE_MAX_LENGTH` 4, line 93).
- End-of-game longest: worse by 22 in the mean (60 against 82), by 8.5 in the median, and all of the mean comes from one map: sqheld_open_large, where one2 fed a leader to 218 and 214 over 300 rounds and one3 reached 46 and 83. On the other 12 pairs the two are equal (59.1 against 59.6). The margin over the opponent's longest is not worse (+4 against -2), because the opponent's leader also ends shorter against one3 (56 against 84).
- Reading for the live bot: safe to put live. The open-map case is the one to watch: with 150 rounds of feeding the leader peaks at 72 instead of 108. Online that peak has never survived (our longest at r400 is 20 on one1's capped games and 39 on one2's, because the fed leader is rammed), so I expect less to be lost online than here, but it is the row to read first: our longest at the end on big maps, one2's being 55, 55, 34, 32, 14. If it falls, 300 is the next value to try, not 200.
- Local games are a richer regime than online (total 449 at r200 against 200, 12 to 18 dragons of 10+ against 1 to 3) and the opponents are our own family of bots; the cap cost a third of the pearls online and 7% here.
- Our longest dragon (at 20+) is rammed after r200 2.4 times a game in one3 and 2.1 in one2: card 1 does not change the leader's fate.

## 8. Added 23:45: the early pearl race, rounds 0-100 (job B)
Sets: one1 against WHQ (w1) and dev test 1 (d1), one2 against WHQ (o2), 15 games each; ranked one1 games where said. Scripts: `o1_early.py` + `o1_earlytab.py` (every dragon turn of both sides in one class), `o1_pearl.py` (every natural pearl: nearest head of each side at birth, who eats it, when; dragons per round; splits), `o1_respawn.py` and `o1_after.py` (tiles eaten from: when the next pearl comes and where the eater is). One class per turn: eat / split / died / no pearl in the 7 by 7 / pearls in view but none within 7 free steps / a mate is nearer to every reachable pearl / ends nearer its nearest own pearl / does not. [M] unless marked.

### 8.1 The turns where ours does not eat
| share of dragon turns, r0-100 | small maps: ours | dev test 1 | big maps: ours | dev test 1 |
|---|---|---|---|---|
| dragon turns a game | 743 | 1170 | 2220 | 3322 |
| eat | 8.6% | 9.1% | 6.8% | 8.6% |
| split | 3.7% | 3.9% | 3.1% | 3.1% |
| died | 1.8% | 2.0% | 1.5% | 1.6% |
| no pearl in view | 39.2% | 31.9% | 47.4% | 51.6% |
| pearls in view, none within 7 free steps | 28.8% | 33.5% | 22.2% | 18.6% |
| a mate is nearer | 4.1% | 6.6% | 6.4% | 5.8% |
| walking to its pearl | 11.1% | 10.4% | 8.7% | 8.3% |
| not walking to it | 2.5% | 2.6% | 4.0% | 2.4% |
| of that: pearl one step away, not taken | 1.0% | 0.9% | 1.9% | 1.0% |

Nothing is walked away from on small maps: the classes match within a few points, and so do they against WHQ. The one class where ours is worse is on big maps, a pearl one step away and not taken (42 turns a game against 151 meals; 2.7% against 0.9% in r0-25); I did not get to which term. Dev test 1's 74 natural pearls to our 47 (small) is 1.58 times our dragon turns at nearly our meals per turn; on big maps 1.50 times the turns and 1.26 times the meals per turn.

### 8.2 What decides a pearl
- The side whose head is nearer (free-path steps) when the pearl is born eats it in 82 to 98% of cases, both sides, every set and window (typically 9 in 10). Pearls born with no head within 12 steps split about evenly.
- Pearls come back where they were eaten: 45% of the natural births of r1-100 on small maps and 67% on big ones are on a tile eaten from before; the commonest gap is 4 rounds (29%), the median 7, 73% within 10; the same side eats the new pearl in 90 to 99%.
- [E] So income follows the number of dragons standing in the pearl fields, a small lead in dragons at r10-25 compounds, and no choice made with a pearl already in view moves much.
- After a meal on a fast tile nobody camps on small maps: our eater is 4 or more steps away at the rebirth in 88 to 97% of cases and theirs in 83 to 95%, in both cases because another pearl was in view (96 to 100% of ours). On big maps ours stays as often as theirs or more (within 3 steps 45 to 54% against 35 to 45%).

### 8.3 Where the dragon count is lost
| dragons, ours / theirs | r0 | r10 | r25 | r50 | r100 |
|---|---|---|---|---|---|
| small, queen starts 4 long, v dev test 1 (5 games) | 4.0 / 4.8 | 4.4 / 4.6 | 4.2 / 5.6 | 7.4 / 9.6 | 15.4 / 18.2 |
| same layouts v WHQ, one1 | 4.0 / 5.0 | 4.0 / 4.8 | 4.6 / 6.0 | 10.4 / 11.0 | 20.6 / 21.2 |
| small, two-dragon start, v dev test 1 (5) | 2.2 / 2.2 | 3.0 / 2.4 | 3.6 / 5.6 | 5.4 / 11.8 | 7.2 / 25.8 |
| same layouts v WHQ, one1 | 2.2 / 2.2 | 2.8 / 3.0 | 4.8 / 4.8 | 7.4 / 8.0 | 15.2 / 12.0 |
| same layouts v WHQ, one2 | 2.2 / 2.2 | 3.2 / 2.8 | 4.0 / 4.4 | 6.6 / 10.0 | 10.0 / 20.6 |
| big, v dev test 1 (5) | 8.8 / 9.2 | 11.4 / 12.8 | 15.4 / 17.6 | 22.6 / 34.4 | 32.4 / 52.0 |

- **The queen holds a dragon back.** Where a queen starts 4 long, theirs splits in round 0 in 14 of 15 small-map games and 12 of 12 big ones; ours in 0 of 15 (6 of 12 on big maps, the 6-long starts). On two-dragon starts theirs splits at 4 between r5 and r14 (r20 once); ours at 5 between r14 and r22. Our queen is 4 or longer and does not split on about 25 of her first 51 turns on small maps (theirs 0 to 2), which is 10% of all our dragon turns of r0-50 there (2 to 25% by layout: Trauma 25, weakhold 18, Queen Of Spades 14). [C] `QS_KEEP_LEN` 3 at main.cpp:146, the test at 1139-1142.
- **Layouts that fail the same way every game** (pearls eaten by r30, ours / theirs): Queen Of Spades 1/11, 1/13, 3/7, 2/6, 2/10 (the round-0 tie of diag-opening2 and diag-med20); Australia 7/11, 2/11, 4/27, 5/45; Stripes 6/15, 7/17, 8/14 (pearls in view on 88% of our turns, eaten on 7% against 15%: the rooms behind portals of diag-stripes); Tower Defense 3/3, 1/1, 1/1 (both stall).
- **Other dragons at 4 that do not split**: on small maps 7.1 turns a game in r0-50 beside 10.5 splits (theirs 3.2 beside 13.7): tail beside a portal 1.8 (lines 1180-1184; theirs split there), fewer than 5 free tiles behind the tail 1.7 (`CHILD_MIN_ROOM`, 357), a pearl beside the head 2.1, tail with no exit 0.9. Real, and 1.6% of our turns: not a card. On Slithery Fight it is 120 turns beside 92 splits, and we are not behind there.
- Caution on the baseline: one2 changes nothing below 56 dragons, yet on small maps it stands at 12.7 dragons against 22.4 at r100 where one1 stood at 17.9 against 16.6 half an hour earlier. Ten games a set; "early game fixed against WHQ" is inside that noise, or WHQ changed.

### 8.4 The card (one, weak)
- **Rule.** Before round 20 the queen splits at 4 like any other dragon, unless an enemy head is within 6 tiles of her; from round 20 she keeps 3 as today.
- **Where.** `QS_KEEP_ROUND` 0 -> 20 and `QS_KEEP_CLEAR` 0 -> 6, one2-bot/main.cpp:147-148, read at 1139-1142. Both exist; b-open built and played them at 40 (dragons r20 7.1 against 6.0, r40 21.1 against 19.2, then total length 7 to 16% lower from r100, so it was set aside).
- **What is new.** Both online opponents split the queen exactly there, and against dev test 1 the count separates in r10-25. [E] 20 allows one split (round 0 on a 4-long start, about r10-16 on a two-dragon start) and has her back under the keep rule before the middle game, where 40 allowed two or three and left her 2 long at r40.
- **Reaches.** The opening on every layout; 4.0 against 4.8-5.0 dragons from round 0 on five small layouts. Not Queen Of Spades (tie), not Australia.
- **Works if:** her turns at 4+ without a split in r0-25 on small maps fall from 14 to under 5; our dragons at r25 on small maps rise from 4.3 towards 5.5; total length at r100 is not lower.
- **Wrong if:** she dies before r60 more often than now (alive at r100 in 6 of 10 small-map games against WHQ, 3 of 10 against dev test 1), or total length at r100 falls as it did locally.
- **Sure:** medium that this is one place the count is lost, low that the value 20 avoids the middle-game cost, low on results. If only one change can go in before the deadline, card 1 (taken) is worth more than this.

## 9. Added 23:55: the first 30 rounds on the starts we always lose (job C)
**No one general rule: four different accidents, one shared fingerprint, and one new decision that repeats.** [M] unless marked; `o1_open.py`, `o1_opentrace.py`, `o1_look.py`; sets w1, d1, o2 (one3's had not arrived).

1. **Where they go.**
 - Queen Of Spades (3 of 3 games): both opponents' second starter keeps its heading 4 steps, enters a portal at r8, eats at r8-10 and three times by r15-19; its children stay there. Ours turns in round 0 (6 of 6 starter first moves; r0-4 straight 10% against 79-100%), walks the other way, takes no portal in 30 rounds; first pearl r15-26. The known round-0 tie.
 - Australia (3 of 3): a pearl on a corner tile 5 steps from the starts, (46,38) or its mirror (17,25). Theirs eats it at r9 and again about every 8 rounds (r14-18, r22-24, r31-33, r41-43). Ours stand one or two steps from it with mates in view and circle a 2 by 2 block: it lies 30 rounds in d1 1461129 (r9-39; dragons 17, 5, 7 in turn), 34 in o2 1462981, 19 in w1 1460556 (r23-42), and is taken on the first turn with no mate in view. d1 and o2 are identical to r39, so it reproduces.
 - Stripes: first pearls level (r9-10), then diag-stripes' rooms. Two-dragon starts: the queen's split (section 8).
2. **The second decision: a pearl left beside mates.** A non-queen dragon with its own pearl one free step away leaves it on 14-19% of such turns on big maps (theirs 8-12%); on small maps 12% with a lower-numbered mate in view, 8% without (Tower Defense 21 of 42). [E] The term: territory. A step into a corner hands every cell beyond it to the mates that now reach it first; `WEIGHT_TERRITORY` 1.5 with no distance discount (`TERRITORY_DECAY` 0, lines 376-378) can outweigh the 460 points a pearl step leads by. Not confirmed; pocket, crowd load and staffing do not fit the code.
3. **Shared fingerprint.** With no pearl in view our starters keep heading on 35% of moves in r0-4 and 45% in r5-30; dev test 1 51 and 57%, WHQ 52 and 54% (theirs higher on 11 of 15 layouts). Tiles seen by r30 are fewer on Queen Of Spades, Australia, Tower Defense, Trauma.
4. **Dev test 1 against WHQ, r0-30.** Straighter on small maps (65% against 54%), 86 spawn tiles seen against 68; a head within 3 steps when a tile it ate from bears again in 43-61% (WHQ 29-45%).

**Card (conditional).** `EAT_BONUS` 300 -> 1000, one3-bot/main.cpp:110 (added at 5728): a pearl one step away is taken unless a trap or head-threat penalty forbids it. First check, one local game on ladder_australia_1: the corner tile is eaten at r9, not r39. Works if "one step away, not taken" falls under 10% and meals by r30 on Australia rise from 2-7. Wrong if deaths within 3 rounds of a meal rise. Low confidence until the trace names the term. `HEADING_TIE` should cover every blind move through r30, not round 0 only.

## 10. Added 23:59: EAT_BONUS 1000 on local games (job D)
**Verdict: no.** [M] `o1_eb.py`; bonus arm `m9eb_vh` against the live set (`m9lv_vh`, `m9f3_vh`), queen hunter, seed 1, same map and side; 6 of 10 pairs finished (Australia, Tower Defense, open_small; both sides).
- The Australia corner pearl is untouched by the bonus: tile (46,38) born r7, eaten r19, born r26, eaten r36; the mirror (17,25) born r22, eaten r30; the same rounds in both arms. Rounds 0-30 are identical in all six pairs (pearls by r30 13.3 both, dragons 9.2 both), and both Tower Defense games are identical through r100.
- Bonus | live, per game: pearl one step away not taken 7.2% | 8.7% (66 of 921 | 78 of 893; with a mate in view 7.3 | 8.9, without 6.3 | 7.8); pearls by r100 148.8 | 142.8; dragons at r100 28.7 | 28.8; deaths within 3 rounds of a meal 21.5 | 19.7; boxed-in deaths to r100 7.7 | 6.7; queen's pearls to r100 5.5 | 5.5, queen alive at r100 3 of 6 both (she dies at r200 against r328 in one game). [C] The bonus applies to her too: the line at 5727-5728 has no queen test.
- So the refusal is not a margin of a few hundred points. Local game `m9eb_vh/ladder_australia_1-seed1-side0`, dragon 17, length 3: at r9 head (45,38), body (44,38) (43,38), pearl one step east; it steps south to (45,39). At r19 it stands in exactly that position again and eats. The only difference in its 7 by 7 is a mate's head at (45,41) at r9.
- The real term: not found by reading. What I can rule out [C]: territory (1.5 a cell cannot make 1,160 points), the mate-head penalty of 450 (no mate beside the tile), the staffing and barren routes (need a known portal; none is in view), the queen hunter (needs their queen seen), threat (enemy heads only), pocket (open region). What is left is the room test at 5638-5655 (400 a missing cell, 5,000 if trapped) seeing the corner as tight while the mate stands at its only way out, or something I have not read.
- The change to name instead: none yet. One step gets it: `DEBUG_LOG` (line 21) prints every direction's score; set it, replay that one game, read dragon 17 at round 9.
- All ten pairs (00:05): rounds 0-30 identical in every pair (pearls 29.1 both, dragons 13.2 both); not taken 8.8% | 10.1%; pearls by r100 251 | 253; dragons at r100 34.5 | 35.7, total 95 | 101; deaths within 3 rounds of a meal 37.6 | 34.8; boxed-in 14.7 | 14.6; won 10 | 9. Verdict unchanged.

## 11. Added 00:08: is one3's 2 of 15 against WHQ the feed-cap change (job E)
**Verdict: noise and queen fates, not card 1. Keep 350.** [M] one1 (22:35), one2 (23:03), one3 (23:40) on the same 15 maps; sets w1, o2, o3 in `o1_scan.py`.

1. **Capped games** (56+ of our dragons at a snapshot in r200-350), one3: five.
| map | first stop | our total r200 / r300 / r400 / end | our longest r300 / r400 / end (theirs at the end) | decided | one1, one2 on this map |
|---|---|---|---|---|---|
| Default | r302 (queen game) | 117 / 160 / 116 / 122 | 7 / 7 / 22 (17) | won, longest | lost elim; won elim |
| Maze | r351 | 175 / 163 / 130 / 81 | 7 / 5 / 52 (67) | lost, longest | lost queen 50 (59); lost longest 50 (55) |
| Slithery Fight | r305 (queen game) | 241 / 249 / 210 / 136 | 15 / 50 / 22 (66) | lost, queen: ours, 82 long, rammed at r480 | lost queen; won queen (theirs, 90 long, rammed at r473) |
| Schooltime | r351 | 178 / 197 / 199 / 120 | 35 / 61 / 7 (75) | lost, longest: our 61 rammed at r461 | won 69 (42), not capped; lost 14 (76), capped |
| Around UNSW | r351 | 252 / 282 / 232 / 253 | 16 / 25 / 45 (72) | lost, queen: theirs never died | lost longest 31 (82); won longest 55 (50), their queen rammed at r198 |
 Card 1's own rows hold online: total grew r200 to r300 in 4 of 5 (one1 0 of 5, one2 3 of 6), no stop before r351 outside queen games.
2. **Noise floor.** Up to r200 the three builds run the same code below 56 dragons, yet: wins on the eight small maps that never capped 3 / 2 / 1, with the result flipping on Stripes (L W L), Devil (W L W), Portals (L W L), weakhold (W L L), Trophy (W L L); our total at r100 74 / 58 / 59 and at r200 on big maps 204 / 182 / 171. One3's Australia (20 dragons, total 49 at r200; one1 202, one2 118) and Islands (136 at r200; 227, 172) were lost before the code could differ.
3. **The five wins one2 had and one3 lost:** Stripes, Portals, Islands (identical code path), Around UNSW (their queen was killed at r198 in one2, before the code differs, and lived in one3), Slithery Fight (a ram on a queen of 82 or 90 at r473-480, ours this time). None is a longest-dragon decision lost for want of feeding rounds.
4. **WHQ** did not change between one2 and one3: its total at r100 / r200 is 86 / 130 and 83 / 125 (one1's set: 69 / 117, so the shift, if any, was before one2).
5. **What the capped games do show:** from r350 the total drains (249 to 136, 197 to 120, 163 to 81) into a leader that is then rammed (82 at r480, 61 at r461, 53 at r375). The missing half is keeping the long queen or leader alive in the last 100 rounds, not the feed round and not the rally: of the four capped losses the rally reaches only Schooltime (44 dragons, total 120, longest 7).

## 12. Added 00:15: how our long queen or leader is rammed after r300 (job F)
**No strong card: the plain LONG_SAFETY veto would have saved 1 of the 8 non-queen bodies, at most 2 at its widest.** [M] 90 games of one1, one2, one3 (WHQ, dev test 1, ranked); `o1_long.py`, `o1_longtab.py`; every case is listed by `o1_longtab.py`.

1. **Count.** 13 of our dragons of 20+ rammed after r300: 5 queens (21, 30, 53, 52, 82 long), 8 others (20 to 61). That is 2.7 per 1,000 long-dragon turns against 1.4 for theirs, and 4.7 against 2.2 per 100 turns with an enemy head within 3 tiles.
2. **The rammer.** 2 to 5 long in 11 of 13 (12 and 13 the others). Inside her 7 by 7 one turn before in 13 of 13, two turns before in 10. It came by 1 step in 3, by 2 in 1, by 3 to 5 in 9; four of those ran further than free plus paid steps allow (a 3 running 3 or 4, a 4 running 5): they eat pearls on the way.
3. **Ours.** Never stood still, never boxed (a free tile beside her head in 12 of 12), moved 1 to 4 steps. A mate within 5 tiles in 2 of 13, none with the rammer in reach.
4. **The veto, checked on the tile each ended on** (heads in her view at her last turn, reach = free steps + 1): inside reach in 4 of 12 (Islands 21 and 33, Schooltime 61, Around UNSW 39); a clean first step was open in 1 (Islands 33); the 21 is under LS_MIN_LENGTH. Counting all paid steps: inside in 6, clean tile in 5. Out of any veto's reach: rammer not in view (3: queens 30 and 82, leader 25) and pearl runs (4: leader 56, queens 53 and 52, a 20).
5. **Queen's ring:** rammer out of view 2, pearl run beyond paid reach 2, one part visible at the view edge 1 (Trauma, a 4 running 3). Never "no clean tile".
6. **Theirs.** 22,583 long-dragon turns to our 4,740. Same exposure (head within 3 on 6.1% against 5.8% of turns, 1.85 against 1.61 steps a turn, 1.0 against 1.1 mates within 5). They do nothing different; they hold five times as many, so one ram costs a fifth. We rammed 31 (queens of 73 and 90).
7. **Our chances.** 44 turns of a 2-4 long with a 20+ head in reach, 18 taken: 12 of 12 with 2 x own length visible (`HUNT_SMALL_RATIO`, line 2762), 6 of 32 without, because the long body lies outside the view. A 3-part end hunt would add 4.2 targets a game after r400, 3.6 of them short dragons: not a card.

**If one switch:** `LONG_SAFETY` true, `LS_MIN_LENGTH` 20, `LS_PAY_STEPS` 3, veto only (lines 151-153, 4190, 4351): at most 2 of 8 on paper, cheap (0.44% of long-dragon turns end inside reach). The real asymmetry is one body against many.

## 13. Added 00:22: where the losses sit (job G)
[M] `o1_buckets.py` (`-g` lists every game). 96 games of one1, one2, one3; one4's sets had not landed (line 2 below is open until they do). Buckets, first match wins: (a) eliminated, or our dragons under half of theirs at r150; (b) lost on queen with ours dead, theirs alive and our total at r300 at least 80% of theirs; (c) lost on longest dragon; (d) the rest.

| group | build | games | won | (a) | (b) | (c) | (d) |
|---|---|---|---|---|---|---|---|
| WHQ | one1 | 15 | 4 | 5 | 2 | 3 | 1 |
| WHQ | one2 | 15 | 6 | 4 | 0 | 4 | 1 |
| WHQ | one3 | 15 | 2 | 5 | 2 | 5 | 1 |
| dev test 1 | one1 | 15 | 1 | 10 | 1 | 1 | 2 |
| dev test 1 | one3 | 15 | 1 | 9 | 1 | 3 | 1 |
| ranked | one1 | 10 | 6 | 4 | 0 | 0 | 0 |
| ranked | one3 | 10 | 4 | 4 | 1 | 0 | 1 |
| all | | 96 | 24 | 41 | 7 | 16 | 7 |

- (a) 41: 26 eliminated, 15 with the count gone; 33 on maps of 1200 cells or fewer. Our count stays under half of theirs from r75 (median, WHQ) and r100 (dev test 1); dragons at r50 4.4 against 10.7 and 6.7 against 12.6.
- (b) 7: our queen died in r51-150 twice, r151-300 three times, r301+ twice; rammed 4, boxed 3. In none of the 7 (and in none of the 27 lost games that end with their queen alive and ours dead) did a short dragon of ours ever have her head in reach. Where one did, over all 96 games, it rammed her on 42 of 47 turns.
- (c) 16: gap in longest 22 at the median (5 to 68); our total was the larger in 5, all against WHQ; we end with 24 dragons at the median.
- (d) 7: queen dead with the swarm behind 5, both queens alive and ours shorter 2 (Trauma, 43 against 75 and 50 against 74).

1. **Largest bucket:** (a) against every group: WHQ 14 of 33 losses (then (c) 12), dev test 1 19 of 28, ranked 8 of 10.
2. **One4's opening against dev test 1:** open, no games yet.
3. **Where a rule can still buy most:** (a), and inside it the queen's early split that one4 already carries; the next step in the same place is the non-queen split held back by the tail tests (section 8.3: 7 unsplit turns beside 10.5 splits in r0-50 on small maps). For WHQ alone (c) is as large: 5 of its 12 are games where our total is the larger and 24 dragons are left over, which is the end rally (card 2) with the leader kept alive.

## 14. Added 00:45: one4's early queen split and tie-break (job H, part 2)
[M] one4 (20941) against one3 on the same 15 maps, WHQ and dev test 1; `o1_q4.py`, `o1_one4.py`.
1. **The split.** She split 4 to 2 before r20 in 12 of 15 games against WHQ (round 0 in 8) and 9 of 15 against dev test 1 (round 0 in 7). After a round-0 split she stayed 2 for 2, 5, 22, 28, 79, 95, 124 rounds (WHQ) and 2, 6, 10, 51, 62, 62, 113 (dev test 1), median 40, and never grew back in 4 of the 14 (weakhold and Around UNSW in both sets: 0 pearls in 51 to 124 rounds, dead at 2; one3's queen ate 11 and 15 on weakhold). After a split at r3-17, when she had just eaten her way to 4, she was 3 again in 2 to 17 rounds (median 4).
2. **Her life.** Alive at r100: 8 against 8 (WHQ, one4 against one3) and 10 against 8; at r300: 2 against 4 and 4 against 3. Dead at length 2: 6 against 3 and 5 against 6. Her mean length at r50: 2.3 against 2.7 and 2.0 against 3.0; her pearls by r100: 3.9 against 4.1 and 3.5 against 4.9. The two queens missing at r300 against WHQ (Default, Slithery Fight) did not die at 2.
3. **What it bought.** Dragons at r25: 8.9 against 8.8 (WHQ) and 8.3 against 8.5 (dev test 1); on the five 4-long-queen small starts 6.2 against 5.8 and 6.2 against 5.0; at r100 on all maps 25.3 against 23.7 and 18.3 against 20.7. No gain that outlasts r25.
4. **The four wins against dev test 1:** Queen Of Spades (no queen split; first pearl r16 where one3 never ate, 12 against 1 dragons at r100: the tie-break), Trauma (round-0 split, first pearl r11 against r22, 6 against 4 dragons at r25, queen alive to the end), Portals and Islands (dragons at r25 and r100 no better than one3's: not opening wins). Against WHQ the tie-break gives Queen Of Spades 8 pearls by r30 where five earlier games had 1 to 3. One win of the four is the tie-break's; 1 to 4 of 15 is inside the noise of section 11.
5. **Verdict.** Keep the tie-break. Keep the queen's early split only from round 1 on: the round-0 split leaves her 2 long with no pearl in reach for a median of 40 rounds and buys no dragons by r100; the splits after she has eaten cost a median of 4 rounds. [C] one line at one4-bot/main.cpp:1139-1142, the keep test also holding in round 0.
6. **Correction to point 4:** in the Queen Of Spades game won against dev test 1 its own opening was slow too (its first pearl r17, 1 pearl by r30), so that win is not clean evidence. The clean case is the WHQ game: our first three pearls at r11, 13, 15 (theirs r8, 14, 15), 9 pearls by r30, where one1 to one3 first ate at r15 to r26 or never.
7. **The one4 line of section 13.** Buckets, one4: WHQ 15 games, won 3, (a) 6, (b) 0, (c) 4, (d) 2; dev test 1 15 games, won 4, (a) 7, (b) 0, (c) 1, (d) 3. Two-dragon small starts against dev test 1: dragons 3.2 against 3.8 at r25 and 9.2 against 23.6 at r100 (one1 3.6 against 5.6 and 7.2 against 25.8; one3 3.6 against 4.0 and 8.6 against 23.4). Bucket (a) has not moved against dev test 1.

## 15. Added 00:55: the end rally on one4, local (job H, part 1)
[M] `o1_rally.py`; `mArl_vh` (one4 + `RALLY_END_FRESH` 25) against `mAl4_vh` (one4), queen hunter, seed 1, both sides, 4 big maps, 8 pairs, identical to r400 (58 dragons, total 366, longest 34.5 in both).

| mean of 8 | rally | one4 | rally higher / lower |
|---|---|---|---|
| dragons alive at the end | 47.9 | 56.4 | 1 / 7 |
| stops r401-499 (length) | 59.2 (201) | 52.4 (177) | 6 / 2 |
| our longest at the end | 80.8 | 66.9 | 5 / 3 |
| their longest at the end | 64.9 | 61.6 | 4 / 4 |
| our total at the end | 346 | 399 | 1 / 7 |
| their total at the end | 343 | 264 | 7 / 1 |
| rams on us after r400 | 10.9 | 13.6 | 1 / 5 |
| games with our longest rammed after r400 | 1 | 3 | |
| won | 5 | 5 | one each way |

- Decided on longest in 7 of 8 in both arms, on queen in 1 (Around UNSW side 0, their queen alive, lost in both). Our queen is dead at the end in all 16.
- Shorter with the rally: Around UNSW 53 against 67 and 50 against 56 (the second turned a win into a loss), portalrooms 76 against 103. Longer: blobs 119 against 36 and 76 against 32 (a loss turned into a win), Australia 50 against 26 and 58 against 52.
- The body it feeds is not rammed more: our longest is rammed after r400 in 1 of 8 games (blobs side 1, at 35 and 37) against 3 of 8 without it.
- **Verdict: yes, narrowly.** Left-over dragons fall from 56 to 48 and the longest ends 14 longer without more leader deaths; it costs 54 of total, the other side ends with 79 more, and the results are 5 against 5.
