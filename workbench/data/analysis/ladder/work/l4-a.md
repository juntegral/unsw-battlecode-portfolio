### F7 On 2-dragon-start layouts we sometimes fail to grow at all in the first 100 rounds; on Tower Defense it is every game
status: confirmed      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 04:03 KST
measured: Stall = at r100 we have at most 6 dragons alive and they have at least 15. Layouts where each team starts with 2 dragons, games that reached r100.
  main: 18 stalls in 96 games, 3 won (Tower Defense 10 of 15, Queen Of Spades 3, Trophy 3, Trauma 2; Maze, weakhold, Stripes 0). v31: 23 stalls in 156 games, 1 won.
  The verifier recounted the first 84 games exactly (15 stalls: band b 3 of 24, band c 8 of 56, 2100+ 4 of 4).
  New this hour: 6 games on 2-start layouts reached r100 (Trauma 3, weakhold 2, Maze 1), 0 stalls. Since the bar was set: 12 games, 3 stalls, 1 won. No Tower Defense game this hour.
  Tower Defense, every game on disk: our pearls eaten in r0-100 are between 1 and 7 in 15 of 15 main games and 22 of 22 v31 games. Wins there: 5 of 15 and 2 of 22.
  Own count this hour (work/h5_decline.py): on Tower Defense in r0-100 one of our dragons starts a turn next to a pearl only 62 times in 15 main games (opponents 1,008 times) and 105 times in 22 v31 games (964).
  When a pearl is next to us there we eat it (97 percent). So the dragons do not get near the pearls; they do not refuse them.
  Verifier's limits, which I accept: this is a Tower Defense fact plus 8 of 81 elsewhere; 4 of the first 15 stalls (Trophy, Trauma) ate 17 to 41 pearls and are dragon losses, not unreached food.
would be wrong if: (first hour) stalls under 8 percent of main games on 2-start layouts, none below 2100, 30 percent or more won, or v31 under 8 percent. All passed and were recounted.
  (new games) weakened if, once 20 new games exist, stalls are under 8 percent or 30 percent or more are won. 12 so far: 3 stalls, 1 won.
inferred: On Tower Defense the first pearls are 20 to 36 path steps from spawn and nothing in main.cpp pulls a dragon that far: the pearl pull (TARGET_REWARD 260 minus TARGET_DECAY 40 a step) is zero
  from 7 steps, PEARL_FAR_DECAY and EXPLORE_GAIN are 0, and a dragon sees only 3 tiles (VISION_RADIUS 3). The map property is "2 starting dragons and the first pearls far by path".
not checked: what our dragons had seen or been told at those rounds. All main games are from 6 Oct and the first hours of 7 Oct KST.
look at: data/online/ladder/1263705/M1263705.replay r0-100 (Tower Defense vs 2022: 3 dragons against 23 at r100, 2 pearls against 70);
  data/online/ladder/1255360/M1255361.replay r0-100 (Tower Defense vs 1873: nearest pearl 37 path steps away for 50 rounds).
smallest test: unchanged. Two default-off switches already in main.cpp, local games on Tower Defense: PEARL_FAR_DECAY above 0 (for example 5) or EXPLORE_GAIN above 0, only while we have
  3 or fewer dragons. Pass mark to write first: our pearls by r100 on Tower Defense rise from 4 to at least 20, with no drop in wins on the other layouts.

### F13 In a quarter of our games we hold the only living queen and then lose her, alone and to a ram she could have stepped away from
status: confirmed as a count (verifier: holds in part); the two new ram counts are to-verify      first seen: 7 Oct 03:13 KST   last tested: 7 Oct 04:08 KST
measured: Free layouts (queen can leave spawn), games where their queen dies in an earlier round than ours.
  main: 72 games (71 last hour plus 1 new, which we won with her alive). Our queen dies later in 47: we win 26 of those. She survives in 25: we win 25. v31: 159 games, 112 die later (45 won), 47 survive (47 won).
  The verifier recounted every figure and narrowed the claim, and I accept all three points: winning when she survives is the queen rule itself (mirror: 0 of 31); their lone queen dies just as often
  (60 of 91 main, 121 of 182 v31), so two in three is how often any lone queen dies; "about half lost" is a 1900-2099 figure (17 of 33 won; 9 of 12 against 1700-1899).
  What stands: in 47 of 180 main games on free layouts we had the queen lead and lost her; 21 of those games were lost; 30 of the 47 by an enemy dragon moving into her head.
  A queen's death rate per round roughly doubles once the other queen is dead, on both sides (verifier).
  New this hour, own count (work/h4_pass.py; bars from 03:24 KST), the rams on our lone queen:
  - She is alone. Fewer than 2 of our other heads within 5 tiles of her at the ram: main 27 of 30 (none at all in 18), v31 57 of 75 (none in 35). Bands: main b 7 of 8, c 18 of 20; v31 b 27 of 40, c 23 of 25.
    We had a median of 14 other dragons alive at those moments (10 or more in 17 of the 30 rams, fewer than 5 in 8). Their lone queen when we ram her is just as alone (35 of 42, 46 of 58).
  - She had a way out. At her last turn before the ram a legal single step ending beyond the rammer's free steps existed in 17 of 27 main rams (3 of the 30 had a rammer born after her last turn) and 59 of 75 on v31.
    On the stricter reading (a step ending farther away than the ram actually travelled) it is 11 of 27 and 43 of 75: 13 of 27 and 38 of 75 rams were paid sprints (the rammer spent length for extra steps).
  - The rammer was in view. It was inside the 7 by 7 square around her head at her last turn in 23 of 27 (main) and 66 of 75 (v31). She always moves before it in the round (the ram is in the same round as her last turn in 252 of 253 rams on our queen).
  - What she did, all rams on our queen, lone or not: her last step took her from outside the rammer's full reach (free steps plus length it can pay, the bot's own enemy_reach) to inside it in 41 of 83 main rams and 113 of 170 on v31;
    in 36 and 50 she was already inside it and did not get out. Their queens do the same (61 of 90 and 116 of 162 stepped in).
  - Lengths at the ram (our lone queen, main): queen 2 (21 times), 3 (6); rammer 3 (18 times), 2 (5).
would be wrong if: (03:13) our queen dies later in under 40 percent of these games on main or v31, or we win 75 percent or more of the games in which she dies later. Passed, recounted.
  (03:24, counted 04:08) F13_ram: under 60 percent of the rams have fewer than 2 friends within 5 tiles. Passed: 90 and 76 percent.
  F13_escape: an escaping step (beyond free steps) existed in under half. Passed: 63 and 79 percent. On the stricter reading main is under half (41 percent); I report both and keep the bar as written.
  (new games) weakened if, once 15 new theirs-first games exist, ours dies later in under 40 percent. 1 so far (she survived).
inferred: Two separate openings, in the bot's own terms. (1) Nobody guards her: QUEEN_DEFEND_RADIUS is 0 and QUEEN_GUARD_CELLS is 0, so with a median of 14 other dragons alive none stays within 5 tiles.
  (2) She walks into reach: QUEEN_SAFETY is on and enemy_reach() already models paid sprints, yet in half to two thirds of the rams her own last step is what puts her head inside the rammer's reach,
  with the rammer in view. A head-on needs her head to face the rammer, so "stepped toward it" is partly what defines the event; the count that matters is that a step out existed in 6 to 8 of 10.
  Opponents' queens die the same way, so this is not a thing top teams do better; it is a free gain if it can be fixed.
not checked: whether the escaping step was safe from other enemy heads (only the rammer was tested; a median of 2 enemy heads were within 5 tiles of her); whether she knew their queen was dead (qh_foe_dead());
  what the bot scored for the step she took. 21 losses is an upper limit on what could be gained.
look at: data/online/ladder/1250697/M1250697.replay r270-282 (Default vs 1952: their queen died r79; our lone queen, length 2, no friend within 5, three legal steps all out of free reach, she steps to distance 2 of a length-3 rammer);
  data/online/ladder/1256138/M1256140.replay r26-69 (Default vs 2021: their queen dies r26, ours rammed r69 at length 2, then eliminated);
  data/online/ladder/1255595/M1255595.replay r87-141 (Islands vs 2020: rammed with 5 friends near, one legal step, no way out: the other kind).
smallest test: a default-off switch, say LONE_QUEEN_GUARD, active once qh_foe_dead() is true and our queen is alive: (a) QUEEN_DEFEND_RADIUS 5 so that a few small dragons stay by her;
  (b) for her own step, refuse any tile inside enemy_reach() of a visible enemy head when another legal tile is outside it (the margin from queen_kill_map, QB_MARGIN_CAP).
  Pass mark to write before any local test: of games where their queen dies first, ours alive at r500 rises from about 1 in 3 to 1 in 2, and wins in those games do not fall.

### F11 On large layouts we eat a third of the pearls, because their heads are nearer to the pearls and they also take more of the ones they are nearer to
status: confirmed (verifier: holds); the two contested-pearl counts are to-verify      first seen: 7 Oct 03:11 KST   last tested: 7 Oct 04:10 KST
measured: Large = 2000 or more open tiles: Around UNSW, Australia, Islands, Schooltime 1 and 2. Share = pearls we ate / pearls both sides ate.
  r101-300: main large 0.340 (55 games; 0.334 on the 51 the verifier recounted), v31 large 0.341 (95 games). Other layouts 0.471 and 0.473. All five large layouts under 0.45 in both codes; every rating band.
  Wins on large layouts: main 22 of 55, v31 37 of 95; elsewhere 104 of 170 and 166 of 315.
  Verifier: every number reproduced; 46 of 51 main large games under one half; survives leaving out any opponent, either evening, the three worst games and both Schooltime layouts; and it is not a head-count effect
  (we hold 0.48 of the living dragons after r100 on large layouts and still eat a third). Its limits: the window is not special (0.43 in r0-100, 0.33 after r300); "other layouts" averages 0.09 to 0.78,
  and Tower Defense and Stripes are worse than any large layout; counted by layout, 5 of 19 at random do this badly in about 5 percent of draws.
  New this hour: 4 large-layout games, share 0.412 (1,703 against 2,431): Schooltime 1 0.24 (won), Around UNSW 0.44 (won) and 0.35 (lost), Australia 0.53 (lost). Too few for the bar (10).
  New this hour, own count (work/h4_pass.py), natural pearls born within 6 tiles of a head of both sides:
  - Who is nearer. Our head is the nearer one in 0.412 of non-tied births on main large layouts (8,887 against 12,667) and 0.401 on v31 (14,912 against 22,284). Other layouts 0.469 and 0.456.
    Per large layout 0.36 to 0.43 (main) and 0.34 to 0.44 (v31); main band b 0.435, band c 0.405.
  - Who converts. On large layouts we eat 0.774 (main) and 0.764 (v31) of the pearls we are nearer to; they eat 0.882 and 0.906 of the pearls they are nearer to.
    On other layouts the two are equal (0.774 and 0.774; 0.724 and 0.735). Equal distance on large layouts goes to us in 0.42 and 0.40 (0.54 and 0.53 elsewhere).
  - Length of the nearest dragon matters less than distance: when ours is nearer we eat 0.81 if ours is longer and 0.74 if theirs is longer (main, large).
would be wrong if: (03:11, passed, recounted) pooled r101-300 share on large layouts 0.45 or more on main or v31; fewer than 3 of 5 layouts under 0.45 in both codes; share elsewhere under 0.47.
  (03:24, tightened 04:02 before counting to leave ties out; counted 04:10) our-nearer share 0.48 or more on main or v31 large layouts. Passed: 0.41 and 0.40.
  (04:02) our conversion when nearer is not at least 5 points below theirs when they are nearer. Passed: 11 and 14 points.
  (new games) weakened if, once 10 new main games on large layouts exist, our r101-300 share there is 0.45 or more. 4 so far: 0.41.
inferred: Both halves of the loss are real on large layouts: where our dragons stand (41 percent nearer) and what happens after (77 against 88 to 91 percent). The second half exists only on large layouts.
  See F16 and F20 for where their dragons stand: together at the tiles that keep giving pearls.
not checked: why they convert better there (a second head arriving, or our dragon turning away: SMALL_THREAT_MULT and the threat fields). Distance is straight-line with wrap, not path.
  Schooltime is also a sealed-queen layout; it is here for size only.
look at: data/online/ladder/1255622/M1255622.replay r100-300 (Islands vs 1934: pearls 144 against 895 in r101-300);
  data/online/ladder/1270027/M1270028.replay r100-300 (Around UNSW vs 1851, new: 60 dragons each at r100, pearls 495 against 905);
  data/online/ladder/1248527/M1248527.replay r100-300 (Australia vs 1946: 155 against 957).
smallest test: no change yet; F20 names where their dragons stand, and the test belongs there.

### F10 On four 2-dragon-start layouts we get about a third of the pearls by round 50
status: confirmed in the verifier's narrower wording (holds in part)      first seen: 7 Oct 03:10 KST   last tested: 7 Oct 04:03 KST
measured: Tower Defense, Stripes, Trauma, Queen Of Spades together, share of pearls eaten by r50: main 0.339 (63 games, 327 against 637), v31 0.296 (91 games). All other layouts 0.510 and 0.507.
  Verifier: every count reproduced; 0 of 2000 shuffles; share under one half in 37 of 59 main games. Per layout main / v31: Tower Defense 0.37 / 0.38, Stripes 0.28 / 0.27, Trauma 0.20 / 0.33, Queen Of Spades 0.44 / 0.28.
  What the verifier took away, and I accept: scarcity as such is not the cause (Schooltime and Default are scarce and near half); "absent against 1700-1899 teams" is fragile (0.49 pooled, 0.33 without our three
  best games); late splitting explains at most Stripes and Queen Of Spades (on Trauma both sides split at r0 and r1 and we are still lowest).
  New this hour: 4 games (Stripes 8 against 10, Trauma 1 against 1, 7 against 0, 2 against 1). Against 1900+ only 1 new game; the bar needs 10.
  New this hour: Stripes is now explained separately (F18): the pearls there sit in small closed rooms our dragons will not eat in.
would be wrong if: (03:10, passed, recounted) pooled share on scarce layouts 0.45 or more; fewer than 3 scarce layouts under 0.45 in both codes; share elsewhere under 0.47.
  (new games) weakened if, once 10 new main games on these four layouts against 1900+ exist, our share by r50 is 0.45 or more. 1 so far.
inferred: This is no longer one thing. Tower Defense is far pearls (F7). Stripes is the pocket rule (F18). Queen Of Spades and Trauma are not explained.
not checked: Queen Of Spades (we eat 0 by r50 in some games; first split r31 against r12) and Trauma (splits level, share 0.20).
look at: data/online/ladder/1259377/M1259378.replay r0-60 (Queen Of Spades vs 2011: we eat 0 by r50, they 28; our first split r52, theirs r11);
  data/online/ladder/1240151/M1240153.replay r0-50 (Trauma vs 1985: 2 against 22).
smallest test: none of its own; F7 and F18 carry Tower Defense and Stripes. For Queen Of Spades, trace one opening first (work/h4_trace.py prints it).

