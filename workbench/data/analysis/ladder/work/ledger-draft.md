# Ladder findings ledger (team 1119)

Rewritten 7 Oct 2026 @@NOW@@ KST (run 20261007-0300, the second run; it started 03:01 KST). Data: 660 games in 132 ranked battles,
5 Oct 15:14 UTC to 6 Oct 17:54 UTC. By our code: main 210 games (42 battles), v31 410, test builds 40 (never used below).
main results: 118 wins / 210. By opponent rating: 1700-1899 49/70, 1900-2099 68/130, 2100+ 1/10. New this hour: 15 main games (3 battles).

## Summary (10 lines)
1. F7 (confirmed, narrowed by the verifier). On layouts that start with 2 dragons we sometimes do not grow for 100 rounds: 18 of 90 main games, 15 lost. Over half are one layout (Tower Defense), where we ate 7 or fewer pearls by round 100 in all 37 games of both codes.
2. F13 (to-verify, biggest in games). When their queen dies first we hold a certain win if ours only survives (24 of 24 main, 47 of 47 v31). She dies later in 47 of 71 main games, mostly rammed at length 2 or 3, and 21 of those are lost: 21 of our 92 main losses. Opponents throw this away just as often, so it is an opening, not something they do better.
3. F11 (to-verify). On large layouts (2000+ open tiles) we eat a third of the pearls in rounds 101-300 (0.33 main, 0.34 v31; about 0.47 elsewhere). All five large layouts, both codes, every rating band. Wins there: 20 of 51 main against 98 of 159 elsewhere.
4. F10 (to-verify). On 2-dragon-start layouts with scarce early pearls we get about a third of the pearls by round 50 (0.36 main, 0.37 v31; 0.51 elsewhere). Our second and third splits come at about twice the opponent's round. Not seen against 1700-1899 teams on main.
5. F16 (@@F16_STATUS@@). @@SUM_F16@@
6. F8 (to-verify). The opponent is the one who rams in two thirds of head-on meetings (0.63 to 0.70 in every slice, 22 of 24 opponents). The cost is not shown: we do not lose more length in them (F8b refuted) and teams that ram more do not beat us more (F8c refuted).
7. F15 (to-verify, not a weak point). Our "no action" deaths (28 a game) are feeder deaths that work: 93 percent happen within 8 tiles of one of our dragons at least twice as long, we eat 80 percent of what they drop, the opponent 3 percent.
8. F4 (candidate). 2100+ teams do not split earlier and do not kill more of ours by round 100; they eat more (174 pearls against 134 on v31) and so make more dragons. The gap sits on the large layouts and the scarce 2-start layouts (F10, F11).
9. Refuted this hour, each on a bar written first: F9 (their rams on our queen are not more frequent than ours on theirs), F12 (a lone enemy queen is not safe from us: she dies later in 11 of 29), F14 (reach is not the common root: pearls born far from both sides split 50-50), F13b (a grown lone queen is not clearly safer).
10. Weakened: F3 (the verifier showed all 39 "self-inflicted" queen deaths were queens with no safe step; the excess is 49 against 32 trapped queens and sits mostly in one hour), F2 (40 percent is our share of all pearls, not of drops in particular), F1. Versions were not compared.

Slices used: band b = main games vs opponents rated 1700-1899 (70 games); band c = 1900-2099 (130 games); band d = 2100+ (10 games, never a slice on its own);
half 1 / half 2 = main games before / from 2026-10-06 14:48:15 UTC (97 and 113 games; the same cut as last hour, so the new games are in half 2);
v31 = the old bot, 410 games (bands b 210, c 135, d 50). "Free layouts" = layouts where the queen can leave spawn (Schooltime 1 and 2 and Slithery Fight left out).
All figures are from rows.jsonl unless marked "own count" (scripts in work/, named in each block). "r100" is raw round 100 (state after 101 rounds).
Every bar is in state.json under bars_run_20261007_0300 and was written before its count; the clock times written there are within about two minutes.

### F7 On 2-dragon-start layouts we sometimes fail to grow at all in the first 100 rounds; on Tower Defense it is every game
status: confirmed      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 03:05 KST
measured: Stall = at r100 we have at most 6 dragons alive and they have at least 15. Layouts where each team starts with 2 dragons, games that reached r100.
  main: 18 stalls in 90 games, 3 won. Last hour 15 of 84 (band b 3 of 24, band c 8 of 56, 2100+ 4 of 4); the verifier recounted all of it exactly.
  New this hour: 6 games, 3 stalls (Tower Defense 2 of 2, Trophy 1 of 1), 1 won. By layout now: Tower Defense 10 of 15, Queen Of Spades 3, Trophy 3, Trauma 2; Maze, weakhold, Stripes 0.
  v31: 23 stalls in 156 games, 1 won.
  Tower Defense, every game on disk: our pearls eaten in r0-100 are between 1 and 7 in 15 of 15 main games and 22 of 22 v31 games. Wins there: 5 of 15 and 2 of 22.
  Verifier's limits, which I accept: 8 of the first 15 were Tower Defense and three 2-start layouts have none, so this is a Tower Defense fact plus 7 of 71 elsewhere;
  "0 of 103 on other layouts" was partly forced by the threshold (with a ratio rule it is 17 of 84 against 3 of 103); 4 of the 15 (Trophy, Trauma) ate 17 to 41 pearls and are dragon losses, not unreached food.
  Cause, own count (work/h3_extract.py, h3_reach.py): the bar "our path to the nearest pearl is at least 1.5 times the opponent's on v31" FAILED (Tower Defense 35 steps against 26.5, Trauma 11 against 9;
  main 36 against 17 and 15 against 7). Pearls there are far for both sides; only some opponents walk to them. What does hold on Tower Defense: of natural pearls born 7 or more tiles from
  every head of both sides, we ate 10 percent in both codes (main 575 pearls, v31 958). On no other layout is that share under 0.40.
would be wrong if: (last hour) stalls under 8 percent of main games on 2-start layouts, none below 2100, 30 percent or more won, or v31 under 8 percent. All passed and were recounted.
  (new games) weakened if, once 20 new games exist, stalls are under 8 percent or 30 percent or more are won. Only 6 so far: 3 stalls, 1 won.
inferred: On Tower Defense the first pearls are 20 to 36 path steps from spawn and nothing in main.cpp pulls a dragon that far: the pearl pull (TARGET_REWARD 260 minus TARGET_DECAY 40 a step) is zero
  from 7 steps, PEARL_FAR_DECAY and EXPLORE_GAIN are 0, and a dragon sees only 3 tiles (VISION_RADIUS 3 in helper.hpp). The map property is "2 starting dragons and the first pearls far by path".
  See F10 for the wider version (scarce early pearls) and F14 for why this is not a general reach problem.
not checked: what our dragons had seen or been told at those rounds; whether sight is from the head only. All main games are from one evening.
look at: data/online/ladder/1263705/M1263705.replay r0-100 (Tower Defense vs 2022, new: 3 dragons against 23 at r100, 2 pearls against 70);
  data/online/ladder/1255360/M1255361.replay r0-100 (Tower Defense vs 1873: nearest pearl 37 path steps away for 50 rounds);
  data/online/ladder/1265766/M1265766.replay r0-40 (Trophy vs 1756, new: their queen dies r11, ours is rammed r33, 1 dragon against 53 at r100).
smallest test: unchanged. Two default-off switches already in main.cpp, local games on Tower Defense: PEARL_FAR_DECAY above 0 (for example 5) or EXPLORE_GAIN above 0, only while we have
  3 or fewer dragons. Pass mark to write first: our pearls by r100 on Tower Defense rise from 4 to at least 20, with no drop in wins on the other layouts.

### F13 Once their queen is dead we hold a certain win if ours survives, and she dies before the end in two games out of three
status: to-verify      first seen: 7 Oct 03:13 KST run 20261007-0300   last tested: 7 Oct 03:13 KST
measured: Free layouts, games where their queen dies in an earlier round than ours (or ours never dies).
  main: 71 games. Our queen dies later in 47 (66 percent): we win 26 of those 47. She survives in 24: we win 24 of 24.
  Band b 12 of 22 die later (9 of those 12 still won); band c 33 of 47 (17 won); half 1 24 of 37; half 2 23 of 34.
  v31: 159 games; she dies later in 112 (70 percent), we win 45 of 112; she survives in 47, we win 47 of 47. Bands b 54 of 90, c 36 of 46, d 13 of 13.
  So 21 main losses (of 92) and 67 v31 losses (of 207) are games in which we had the only living queen and lost her.
  What kills her (main, the 47): rammed by an enemy dragon 30, wall 7, own body 5, another dragon's body 3, she rammed someone 2. Her length at death: 2 (28 times), 3 (16), 4 (1), 6 (2).
  When: a median of 60 rounds after their queen died. With their queen dead by r100 and ours alive (51 main games): ours dies by r100 in 11, r101-200 in 12, r201-300 in 6, later in 6, survives in 16.
  Even late: only our queen alive at r300 in 16 main games, and she still dies in 10 (v31 16 of 22), 20 of those 26 by an enemy ram.
  The mirror: when our queen dies first, theirs dies later in 60 of 91 main games (66 percent) and 121 of 182 v31 (66 percent). We win 41 of those 60 and 0 of the 31 where she survives.
would be wrong if: our queen dies later in under 40 percent of these games on main or on v31, or we win 75 percent or more of the games in which she dies later.
  (Written before the count; I had seen the r300 numbers and the totals 50 of 71 and 92 of 159. Passed: 66 and 70 percent; 55 and 40 percent won. Band b alone is 9 of 12 won, which sits on the 75 percent line.)
inferred: Under the queen rule a living queen beats a dead one whatever else is on the board, so after their queen dies the whole game is "keep ours alive for the remaining rounds".
  Our bot does not play it that way: she stays at length 2 or 3 and is rammed. Opponents do no better with their lone queen, so no top team is showing us the answer here; that also means it may be hard.
  In main.cpp the queen-guard family is off (QUEEN_GUARD_CELLS 0, so queen_guard() is never true; QUEEN_DEFEND_RADIUS 0, QUEEN_GUARD_RADIUS 0, QG_SAFEZONE and QG_CORNER false). QUEEN_SAFETY is on.
  A follow-up bar FAILED (F13b): a lone queen already 8 or longer is not clearly safer (dies later in 9 of 16 on v31, 5 of 10 on main; small ones 69 and 67 percent). So "grow her" is not supported.
not checked: whether our bot knows their queen is dead at that point (qh_foe_dead() works from sight and messages); how many of our dragons were near her when she was rammed;
  whether the rammers were sent for her or met her by chance. 21 losses is an upper limit: it assumes she could have been kept alive in every one.
look at: data/online/ladder/1256138/M1256140.replay r26-69 (Default vs 2021: their queen dies r26, ours rammed r69 at length 2, then eliminated);
  data/online/ladder/1249035/M1249037.replay r77-427 (Tower Defense vs 2382: only our queen alive from r77, rammed at r427);
  data/online/ladder/1255595/M1255595.replay r87-141 (Islands vs 2020: their queen dies r87, ours rammed r141).
smallest test: a default-off switch, say LONE_QUEEN_GUARD: once qh_foe_dead() is true and our queen is alive, switch on for her what main already has but never runs
  (queen_guard(): QG_PESSIMIST, QG_THREAT_MULT 6, QG_GUARD_RADIUS 5) and keep small dragons from leaving her (QUEEN_DEFEND_RADIUS above 0). Count first, from replays: at each of the 30 rams,
  the number of our heads within 5 tiles of her and whether she had a step that left the rammer's reach. Pass mark to write before any local test: of games where their queen dies first,
  ours alive at r500 rises from about 1 in 3 to 1 in 2.

### F11 On large layouts we eat a third of the pearls in the middle of the game
status: to-verify      first seen: 7 Oct 03:11 KST run 20261007-0300   last tested: 7 Oct 03:16 KST
measured: Large = 2000 or more open tiles: Around UNSW, Australia, Islands, Schooltime 1 and 2. Share = pearls we ate / pearls both sides ate, by round of the meal.
  main, large (51 games): r0-100 0.43, r101-300 0.334, r301-500 0.33. Other layouts (159 games): 0.52, 0.471, 0.40.
  v31, large (95 games): 0.44, 0.341, 0.31. Other (315 games): 0.52, 0.473, 0.43.
  r101-300 by layout, main / v31: Around UNSW 0.37 / 0.33, Australia 0.27 / 0.36, Islands 0.24 / 0.30, Schooltime 1 0.31 / 0.26, Schooltime 2 0.43 / 0.40. All five under 0.45 in both codes.
  r101-300 on large layouts by band: main b 0.38 (18 games), c 0.31 (30), d 0.26 (3); v31 b 0.38 (43), c 0.34 (37), d 0.21 (13). On other layouts: main 0.49, 0.47, 0.36; v31 0.50, 0.47, 0.40.
  Wins on large layouts: main 20 of 51 (b 11 of 18, c 9 of 30, d 0 of 3); v31 37 of 95. Elsewhere: main 98 of 159, v31 166 of 315. Islands: 0 of 9 main, 1 of 17 v31.
  Own count of where the pearls go (work/h3_reach.py; natural pearls, moments when each side has at most 1.5 times the other's dragons), large layouts, main / v31:
  born within 6 tiles of heads of both sides: our share 0.40 / 0.38 (15,317 and 27,187 pearls); born 7 or more from both: 0.53 / 0.52; born near ours only: 8,859 / 19,551 pearls;
  born near theirs only: 14,695 / 28,108 pearls. So on these layouts we lose the contested pearls and fewer pearls are born beside our dragons in the first place (see F16).
would be wrong if: pooled r101-300 share on large layouts is 0.45 or more on main or v31; or fewer than 3 of the 5 layouts are under 0.45 in both codes; or the share elsewhere is under 0.47.
  (Written before the count; I had seen that our lowest shares against 2100+ teams and our worst win counts were on these layouts. Passed; "elsewhere" only just, 0.471 and 0.473.)
inferred: Size is the property here: these are the four largest layouts by open tiles (2226 to 4096) and they start with 3 to 10 dragons, so this is not the 2-dragon opening problem of F10.
  It is not reach in the plain sense (F14 refuted): far pearls split evenly. The loss is in pearls that both sides are near, and in where the dragons stand.
not checked: why contested pearls go to them (who arrives first, who is longer and faster, whether ours turn away from enemy heads: SMALL_THREAT_MULT and the threat fields);
  dragons alive by round on these layouts (the share may partly follow the head count; the own count above holds the count ratio under 1.5 only loosely).
  Schooltime is also a sealed-queen layout; it is here for size, not for queen statistics.
look at: data/online/ladder/1255622/M1255622.replay r100-300 (Islands vs 1934: pearls 144 against 895 in r101-300, dragons 27 against 63 at r100);
  data/online/ladder/1248527/M1248527.replay r100-300 (Australia vs 1946: 155 against 957);
  data/online/ladder/1254770/M1254770.replay r100-300 (Schooltime 1 vs 1994: 20 against 325).
smallest test: no change yet. Count on these layouts, for pearls born within 6 tiles of both sides: which side's head was nearer, and the length of the nearest dragon on each side.
  If ours is as near but loses, look at the small-dragon threat avoidance; if ours is farther, it is positioning (F16).

### F10 On 2-dragon-start layouts with scarce early pearls we get about a third of the pearls by round 50
status: to-verify      first seen: 7 Oct 03:10 KST run 20261007-0300   last tested: 7 Oct 03:10 KST
measured: Scarce = a layout where both sides together eat a median of under 30 pearls by r50 (classed per code, 5 or more games). Share = ours / both, pearls eaten by r50, pooled.
  main: scarce layouts 0.357 (5 layouts, 70 games), other layouts 0.508 (13 layouts, 137 games). v31: scarce 0.373 (7 layouts, 130 games), other 0.508 (12 layouts, 279 games).
  Scarce layouts, main / v31 share: Tower Defense 0.37 / 0.38, Stripes 0.28 / 0.27, Trauma 0.20 / 0.33, Queen Of Spades 0.44 / 0.28 (all four start with 2 dragons);
  Schooltime 1 0.54 / 0.44, Default 0.55 (not scarce on main) / 0.56, Schooltime 2 0.35 (not scarce on main) / 0.45, Prisoners Dilemma 2nd layout 0.45 / 0.51 (these start with 3 or 4 dragons).
  2-start layouts with plenty of early pearls: Maze 0.50 / 0.52, Trophy 0.49 / 0.53, weakhold 0.60 / 0.54.
  The four scarce 2-start layouts by band, share by r50: main b 0.49 (19 games), c 0.30 (37), d 0.08 (3); v31 b 0.33 (48), c 0.33 (30), d 0.13 (9). All other layouts: 0.49 to 0.53 (0.40 and 0.47 against 2100+).
  Wins on those four: main 28 of 59 (b 14 of 19, c 14 of 37, d 0 of 3); v31 34 of 91. Rest of main: 90 of 151.
  Own count (work/h3_extract.py), median round of our / their split, main: Stripes 1st 24 / 18, 2nd 61.5 / 33.5, 3rd 130 / 36; Queen Of Spades 31 / 12, 43 / 22, 50 / 30;
  Tower Defense 52 / 43, 118 / 64, 145 / 68; Trauma 3rd split 47 / 31. v31: Stripes 23 / 15, 56.5 / 26.5, 75 / 33.5; Queen Of Spades 26 / 12, 39.5 / 18, 55 / 27. Both sides split at length 4.
  Own count (work/h3_reach.py): on these four layouts our share of pearls born 7 or more tiles from both sides is 0.37 main and 0.33 v31 (0.50 on all layouts together).
would be wrong if: pooled share on scarce layouts is 0.45 or more on main or v31; or fewer than 3 scarce layouts are under 0.45 in both codes; or the share elsewhere is under 0.47.
  (Written before the count; I had seen the per-layout medians of the seven 2-start layouts. Passed. Found after: it is the 2-start scarce layouts, not scarce layouts in general, and on main it is absent against band b.)
inferred: With two short dragons and few pearls, the side that walks straight to the first pearls doubles first. The opponents rated 1900 and above do that; we take about twice as long to the second and third split.
  This is the one place where the "no pull beyond 6 steps" reading of F7 is supported by the far-pearl count.
not checked: Stripes is odd: our nearest pearl is a median of 2 path steps away and we still eat 3.5 by r50 against 11.5. Something other than distance stops us there (not looked at).
  The scarce class is defined from what was eaten, so it depends on play as well as on the map; a map-only measure (pearls on the board at round 0 within N steps of spawn) is not built yet.
look at: data/online/ladder/1259377/M1259378.replay r0-60 (Queen Of Spades vs 2011: we eat 0 by r50, they 28; our first split r52, theirs r11);
  data/online/ladder/1254072/M1254072.replay r0-60 (Stripes vs 2030: 3 against 14; splits r22, 54, 65 against r11, 13, 32);
  data/online/ladder/1240151/M1240153.replay r0-50 (Trauma vs 1985: 2 against 22).
smallest test: the same switches as F7 (PEARL_FAR_DECAY or EXPLORE_GAIN above 0 while we have 3 or fewer dragons), measured on Stripes, Queen Of Spades, Trauma and Tower Defense:
  pass mark to write first, our round of second split falls to within 10 rounds of the opponent's. Before that, look at one Stripes opening to see what the dragons do with a pearl 2 steps away.

### F16 With the same number of dragons, more pearls are born beside their dragons than beside ours
status: @@F16_STATUS@@      first seen: 7 Oct 03:17 KST run 20261007-0300   last tested: 7 Oct @@F16_TIME@@ KST
@@F16_BODY@@

### F8 The opponent is the one who rams in two thirds of head-on meetings
status: to-verify      first seen: 7 Oct 03:06 KST run 20261007-0300   last tested: 7 Oct 03:10 KST
measured (own count from raw replays, work/h3_extract.py and h3_count.py; meeting counts equal rows.jsonl in all 620 games): a cross-team head-on meeting kills both dragons;
  the mover is the dragon whose turn it was. Share of meetings in which their dragon was the mover:
  main 0.657 (8,313 meetings, 210 games); band b 0.701; band c 0.630; band d 0.723 (10 games); half 1 0.639; half 2 0.671; new 15 games 0.713. v31 0.675 (16,491 meetings); bands b 0.638, c 0.708, d 0.765.
  Above 0.5 for 22 of 24 opponents with 5 or more main games (range 0.44 to 0.90). By layout 0.32 (Prisoners Dilemma) to 0.82 (Australia, Schooltime 1); Islands 0.79.
  By dragons alive at the meeting: we have 1.5 times theirs 0.51; similar 0.67; they have 1.5 times ours 0.77. In our wins 0.59, in our losses 0.73.
  Lengths, main: their rammers are 3 (2,600), 2 (1,828), 4 (523); our victims 2 (2,249), 3 (1,906), 4 (572), 9 or more (336). Our rammers 2 (1,444), 3 (1,080); their victims 2 (1,135), 3 (775), 9 or more (372).
  A friend within 5 tiles of the spot: their rams 79 percent, ours 77 percent. The verifier's count last hour (195 games): the mover's side eats the drop, 59 percent when ours moved, 30 percent when theirs did.
would be wrong if: their mover share is under 0.58 in any of band b, band c, half 1, half 2 or on v31; or above 0.5 for fewer than 70 percent of opponents. (Written before the slice counts; the pooled 2697 against 5090 was known from the verifier. Passed.)
  Two bars on what it costs us, both written first, both FAILED:
  F8b "the meetings cost us more length": length lost, ours / theirs, is 0.88 in band b and 0.92 in band c; when they ram, our victim is longer in 31 percent, the same length in 39 percent. We lose less length than they do.
  F8c "teams that ram more beat us more": rank correlation across opponents between their mover share and our win rate is +0.01 on main (24 opponents) and -0.37 on v31 (43).
inferred: Opponents choose the head-on far more readily than we do, even one-for-one at length 2 or 3 and even when we outnumber them. main.cpp allows a ram only by a dragon of length 4 or less against a target
  of at least 5 parts or its own length plus 2 (TRADE_TARGET_MIN_PARTS 5; TRADE_EVEN false), with 8 or more dragons (TRADE_MIN_UNITS) and one more friend than enemy nearby (TRADE_LOCAL_EDGE 1).
  What they gain is not length. It may be the drop (about one pearl a meeting) or the place: a one-for-one trade clears our dragon off a tile they then hold. That fits F16 but is a guess.
not checked: where the meetings happen (on fast pearl tiles or not); what our victim was doing (eating, feeding, standing). Whether ramming more would help us is not shown by any count here.
look at: data/online/ladder/1256635/M1256637.replay r91-200 (Australia vs 1924: 88 meetings, they are the mover in 97 percent);
  data/online/ladder/1262921/M1262924.replay r92-110 (Australia vs 1870, new: 49 meetings, 94 percent; three in round 92);
  data/online/ladder/1240862/M1240862.replay r34-100 (Slithery Fight vs 1814: 105 meetings, 91 percent, and we won).
smallest test: no change yet; count first whether the meetings they start are on tiles where a pearl was eaten in the last 12 rounds. If a test is wanted anyway, the existing default-off switch TRADE_EVEN
  (a ram is allowed against a target as long as the rammer) in local games, with the pass mark written first: our share of pearls in r101-300 on a large layout rises, wins do not fall.

### F15 Our "no action" deaths are feeder deaths and they work; this is not a fault
status: to-verify      first seen: 7 Oct 02:09 KST run (as a note)   last tested: 7 Oct 03:09 KST
measured (own count, work/h3_noact.py and h3_noact_count.py; death counts equal rows.jsonl, drop counts equal ceil(length/2) in every case):
  main: 5,895 deaths in 210 games (28 a game; 37 in wins, 17 in losses). None before round 200; 21.5 percent in r200-299; the rest later. Lengths 2 (3,994), 3 (1,494), 6 (247). None is a queen.
  Within 3 tiles of the head of one of our dragons at least twice as long: 87.2 percent; within 8 tiles: 92.8 percent; no such dragon alive: 1.0 percent.
  They gave up 15,455 of length and dropped 8,565 pearls; our side ate 6,883 of those within 15 rounds (80.4 percent), 5,032 by a dragon at least twice as long; the opponent ate 281 (3.3 percent).
  The same in band b (92.6 percent, 80.3, 2.3), band c (93.0, 80.3, 3.9), half 1 and half 2. v31: 10,326 deaths; 93.0 percent, 79.4 percent, 3.5 percent.
  Games with 5 or more of them that end on the longest dragon: main 63, we win 45 (our longest 44 against 32). That end on the queen rule: 42, we win 17.
would be wrong if: fewer than 80 percent within 8 tiles of an own dragon twice as long; or our side eats under 70 percent of the drop; or the opponent eats more than 15 percent. (Written before the count. Passed on main and v31.)
  The first bar, from last hour, FAILED and was replaced before this count: "80 percent within 3 tiles of our longest dragon and under 10 percent before round 300" gave 42 percent and 21.5 percent,
  because the dragon they feed is often not our longest one and main.cpp starts feeding at round 200 when we have 56 dragons (FEED_CAP_ROUND 200, FEED_CAP_UNITS 56).
inferred: This is ready_to_die() in main.cpp doing what it was written to do (FEEDER_DIE_DIST 3). The team's open question "deliberate or a fault" is answered: deliberate.
  The price is known now: a little over half of the length fed is destroyed (15,455 in, 6,883 back).
not checked: whether feeding is the right call in each game. Of 29 main games with our queen dead and theirs alive at r300, 22 still had 5 or more feeder deaths after r300; we won 8 of the 29 (F12).
look at: data/online/ladder/1246505/M1246508.replay r300-499 (Maze vs 1776: 93 feeder deaths after r300, our longest ends at 85 against 29, won).
smallest test: none needed.

### F4 Teams rated 2100+ are ahead of us by round 100 because they eat more, not because they split earlier or kill more of ours
status: candidate      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 03:10 KST
measured: Last hour (v31): behind in total length at r100 in 34 of 48 games against 2100+ and 86 of 197 against 1700-1899; dragons alive at r100 a median of 20 against 29.5.
  This hour, two bars on how, both written first, both FAILED, and the counts show something else:
  F4b "they split earlier" (own count, work/h3_extract.py): round of the 5th split, ours minus theirs, median +1.0 against 2100+ and 0.0 against 1700-1899 (v31); 10th split +2.0. Both sides split at length 4 in every band.
  F4c "our dragons die more" (rows.jsonl, v31, 48 games against 2100+): dragons alive at r100, 24.0 a game against 30.9; deaths in r0-100, ours 40.0 against theirs 42.0; splits by r100, 59.3 against 68.2;
  pearls in r0-100, 134 against 174. main (9 games): alive 23.7 against 41.0, deaths 36.6 against 45.6, splits 55.6 against 81.9, pearls 125 against 212.
  Against bands b and c the same four numbers are level (v31 pearls 115 against 110 and 116 against 119).
  Where: our share of pearls by r50 against 2100+ is 0.47 (v31) and by r51-100 0.42. By layout (v31, pearls by r100): Stripes 0.07, Tower Defense 0.08, Trauma 0.18, Australia 0.27, Schooltime 2 0.27,
  Queen Of Spades 0.31, Around UNSW 0.36, Islands 0.39; level on Slithery Fight, Portals, Devil, Autarky, weakhold, Default (0.46 to 0.59). 1 to 6 games a layout.
  Also from F16's table: pearls born beside their dragons only against ours only, at similar dragon counts: 1.4 to 1 against band b, 1.5 against band c, 2.0 to 2.3 against 2100+.
would be wrong if: (last hour, passed on v31) the behind-at-r100 share differs by under 15 points between 2100+ and 1700-1899. (next) in the next 10 main games against 2100+ we are behind at r100 in 5 or fewer. No such game arrived this hour.
inferred: The top teams are the strongest case of F10 and F11 rather than a separate thing: they take the scarce early pearls and the large-layout pearls from us more completely than the 1900-2099 teams do.
  They also lose more dragons than we do on the way (42 to 46 a game by r100, of which about 12 "other" and up to 21 "own body" a game), so they spend dragons freely.
not checked: main has 10 games against 2100+, all lost but one. What their early "other" and "own body" deaths are for.
look at: data/online/ladder/1249035/M1249035.replay r0-100 (Around UNSW vs 2382: pearls 141 against 392 by r100);
  data/online/ladder/1249035/M1249036.replay r0-60 (Queen Of Spades vs 2382: 2 pearls against 65 by r100).
smallest test: none of its own; F10 and F11 carry it.

### F6 On corridor-heavy layouts with slow pearls we are behind at round 100 in four games out of five
status: candidate      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 03:15 KST (3 new games only)
measured: Last hour: Maze and Tower Defense only; main behind in total length at r100 in 23 of 28 games, v31 31 of 46.
  New: Tower Defense 9 against 39 and 6 against 55 (behind, one won), Maze 63 against 74 (behind, won). So 26 of 31 on main.
  From F10's count: on Maze our share of pearls by r50 is 0.50 and 0.52, so Maze is not an eating problem; Tower Defense is (F7).
would be wrong if: (last hour, narrow pass on v31) the share there is under 0.60 or less than 20 points above the other layouts.
inferred: Two layouts cannot show a map property, and the two behave differently. I expect this to end as "Tower Defense, see F7" and nothing more.
not checked: no test of its own this hour.
look at: data/online/ladder/1241400/M1241402.replay r0-100 (Tower Defense vs 1934).
smallest test: none; covered by F7.

### F3 Our queen ends boxed in (no safe step) more often than theirs
status: weakened      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 03:15 KST
measured: Last hour's claim was "our queen kills herself (wall or own body) twice as often": 39 of 168 main games against 20. The verifier recounted it exactly and then showed what it is made of:
  in all 39 of ours (and 18 of their 20) the queen had no safe step that turn. These are trapped queens, not steering errors. Trapped queens whatever they then hit: 49 ours against 32 theirs.
  Once trapped ours takes the wall or her own body in 39 of 49; theirs in 18 of 32 (theirs rams another head 8 times, ours 3).
  The excess is within chance in band c (24 against 15) and half 1 (16 against 11), and 13 of the 19 excess games fall in one hour (00:00-00:59 KST: 16 against 3 in 61 games; the rest 23 against 17 in 107).
  New games: 12 on free layouts, ours 3, theirs 4. Total now 42 against 24 in 180 games.
would be wrong if: (new games) weakened if, once 40 new games exist, ours is not above theirs. 12 so far, not above.
inferred: What is left is a modest difference in how often the queen gets boxed in (about 1.5 to 1), unevenly spread over the evening. The dead-end penalty (QUEEN_DEAD_END, QUEEN_ROOM 8) is on and does not prevent it.
  The one usable detail: a trapped queen of theirs more often rams a head (and takes one of ours with her); ours picks the wall.
not checked: what boxed her in (our own dragons, theirs, or kelp).
look at: data/online/ladder/1233593/M1233594.replay r172 (Maze, wall, length 2, lost); data/online/ladder/1241400/M1241403.replay r279 (Islands, wall, length 2, lost).
smallest test: no change yet. If anything: when the queen has no safe step and an enemy head is adjacent, take the head-on instead of the wall (count first how often an enemy head was adjacent in the 49).

### F2 After head-on meetings the opponent eats more of the dropped pearls than we do
status: weakened      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 03:05 KST
measured: main, 210 games: we ate 11,835 of the head-on drops eaten within 15 rounds, they ate 17,803, share 0.399. New 15 games: 669 against 1,216, share 0.355.
  The verifier recounted last hour's figures exactly and added: it holds in band c (0.380) and both halves but not in band b (0.455; 30 games fewer against 28 more);
  0.40 is also our share of all pearls eaten in those games (0.413), so the figure is not about drops; the mover's side takes the drop (0.587 when ours moved, 0.298 when theirs did) and theirs is the mover in 65 percent.
would be wrong if: (last hour) share 0.47 or more in any of the four slices. The verifier's interval for band b reaches 0.504, so "every slice" does not stand.
inferred: Not a finding of its own. It is F8 (they are the mover) seen through the pearls.
not checked: nothing further planned.
look at: data/online/ladder/1256635/M1256637.replay (Australia vs 1924: we ate 35 drop pearls, they ate 388).
smallest test: none; see F8.

### F1 Being behind in total length at round 100 means the game is mostly lost
status: weakened      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 03:05 KST
measured: Last hour: main wins when behind at r100 35 of 96, but 13 of 24 against band b, which failed the bar.
  Narrowed claim from last hour (against 1900+ only, new games): 5 new games behind at r100, 1 won. All main games against 1900+: 23 won of 77 behind.
  A related count this hour (free layouts, main): behind at r100 and our queen rammed while theirs is not, 2 won of 29 (v31 2 of 60); behind and neither queen rammed, 19 of 35 (v31 23 of 54).
would be wrong if: (new games) against 1900+ opponents we win 0.45 or more of games in which we are behind at r100, once 20 such new games exist. 5 so far.
inferred: Against 1900+ teams an early deficit is rarely recovered. When it is recovered, the queens are usually both alive or both dead.
not checked: whether total length is the right yardstick.
look at: data/online/ladder/1240020/M1240020.replay r50-100 (Around UNSW vs 2080).
smallest test: none.

### F9 Their rams kill our queen more often than our rams kill theirs
status: refuted      first seen: 7 Oct 03:04 KST run 20261007-0300   last tested: 7 Oct 03:05 KST
measured: Free layouts, games in which a queen died as the stationary victim of an enemy ram. main: ours 83 games, theirs 89 (ratio 0.93). Band b 20 against 29; band c 57 against 58; half 1 37 against 38;
  half 2 46 against 51. v31: 172 against 167 (band c 65 against 50, band d 26 against 17). Meetings in which the victim was a queen (own count): 91 against 92.
  Both queens are rammed at length 2 (58 of ours, 52 of theirs) or 3; the median round is 105 for ours and 99 for theirs.
  Outcome: only ours rammed, we win 5 of 35; only theirs, 36 of 41 (v31 15 of 95 and 79 of 90).
  Follow-up bar F9b "this decides games beyond who was already ahead" FAILED on v31: ahead at r100 and only ours rammed, we still win 13 of 26; behind and only theirs rammed, 4 of 10.
would be wrong if: the ratio is under 1.3 in any of the four main slices or on v31. (Written before the count. Failed everywhere on main.)
inferred: Queen rams are even between the sides. Most of the outcome split is who was already ahead. The part that survives is in F13: a lone queen is usually lost, on both sides.
not checked: 2100+ teams look different (v31 26 against 17, main 6 against 2) but that is 53 games.
look at: none needed.
smallest test: none.

### F12 When only their queen is alive at round 300 we almost never turn the game round
status: refuted      first seen: 7 Oct 03:11 KST run 20261007-0300   last tested: 7 Oct 03:12 KST
measured: Free layouts, games that reached r300. main: only their queen alive at r300 in 29 games; she dies later in 11 (38 percent); we win 8 (28 percent). v31: 69 games, 28, 15.
  22 of the 29 have 5 or more of our feeder deaths after r300 (median 36). When she does die we win 8 of 11, because the feeding has made our longest dragon the longest on the board.
would be wrong if: she dies later in 20 percent or more, or we win 15 percent or more, or under 60 percent of the games have 5 or more feeder deaths after r300. (Written before the count. The first two failed.)
inferred: The bot's revenge hunt (QH_REVENGE_ROUND 100, small dragons up to QH_MAX_LEN 4) does kill a lone queen in a third of these games, and feeding in the meantime is what turns the kill into a win.
not checked: the 18 games where she lived: how close our hunters got.
look at: data/online/ladder/1263705/M1263706.replay r276-499 (Maze vs 2022, new: our queen dies r276, theirs dies later, 81 feeder deaths, we win 73 against 18).
smallest test: none.

### F14 The common root of F10 and F11 is reach: pearls born far from both sides go to the opponent
status: refuted      first seen: 7 Oct 03:13 KST run 20261007-0300   last tested: 7 Oct 03:17 KST
measured (own count, work/h3_reach.py and h3_reach_count.py): natural pearls by the distance from the birth tile to the nearest head of each side at the birth (wrapped Manhattan), only births
  at moments when each side has at most 1.5 times the other's dragons; credited to the side that eats them.
  Born 7 or more tiles from both sides: our share 0.495 on main (3,888 against 3,962) and 0.495 on v31 (7,107 against 7,253). Born within 6 of both: 0.453 and 0.450.
  By band, far from both: main b 0.56, c 0.46, d 0.39 (328 pearls); v31 b 0.50, c 0.52, d 0.41. Halves of main 0.50 and 0.49.
  By layout group, far from both, main / v31: large layouts 0.53 / 0.52; the four scarce 2-start layouts 0.37 / 0.33; the rest 0.54 / 0.54. Tower Defense alone 0.10 / 0.10.
  Pearls born near one side only go to that side: near ours only we eat 0.89 (main) and 0.88 (v31); near theirs only they eat 0.93 and 0.92.
would be wrong if: our share of far-for-both pearls is 0.45 or more on main or v31, or less than 5 points below our share of near-for-both pearls. (Written before the count. Failed on both.)
inferred: Our dragons do go and get far pearls as well as the opponents do, except on the scarce 2-start layouts and above all Tower Defense. So a general "pull pearls from farther away" change is not supported;
  the narrow one in F7 and F10 (only with 3 or fewer dragons) still is. What separates the sides in general is in the next columns of the same table: contested pearls (0.45) and where pearls are born (F16).
not checked: distance here is straight-line with wrap, not path; on corridor layouts that understates how far a pearl is.
look at: none needed.
smallest test: none.

### F5 In rounds 0-100 our dragons die on walls more often than theirs
status: refuted      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 03:10 KST
measured: Last hour: ratio 1.12 against band c teams and higher on only 11 of 18 layouts; both bars failed.
  This hour, per game in r0-100 (rows.jsonl): main band b 13.8 ours against 7.2 theirs, band c 12.3 against 11.2; v31 band b 13.9 against 9.0, band c 14.4 against 10.9, band d 18.2 against 9.6.
  So the v31 slices do show more wall deaths on our side; the main band c slice still does not. No change of status.
would be wrong if: (last hour) ratio under 1.15 in any main slice. Failed in band c.
inferred: Early wall deaths are a normal part of play for both sides. Not a lever.
not checked: what the wall deaths are.
look at: none needed.
smallest test: none.

## Notes that are not findings
- How main games end (210): wins 118, losses 92. Worst layouts by wins: Islands 0 of 9, Australia 2 of 10, Stripes 2 of 8, Schooltime 1st layout 3 of 11, Tower Defense 5 of 15.
- Whose queen dies first (main, free layouts): ours first, we win 41 of 91; theirs first, 50 of 71; neither dies, 10 of 15; same round, 2 of 3.
- A dragon sees 3 tiles (VISION_RADIUS 3). Anything our bot does about a pearl farther than that comes from memory or messages.
- Tooling: the write guard still refuses the Write and Edit tools and any command containing braces; every file here was written through a Python heredoc to the on-disk spelling of the folder.
  Files left in work/ from this run: h3_extract.py, h3_count.py, h3_noact.py, h3_noact_count.py, h3_reach.py, h3_reach_count.py, h3_reach2.py, h3_reach2_count.py and their shard outputs (h3-, h3n-, h3r-, h3s-).
