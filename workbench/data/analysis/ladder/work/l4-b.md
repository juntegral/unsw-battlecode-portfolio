### F20 With the same number of dragons, a third of their heads stand at the tiles that keep giving pearls; a fifth of ours do
status: to-verify      first seen: 7 Oct 04:14 KST run 20261007-0400   last tested: 7 Oct 04:17 KST
measured (own count, work/h8_fountain.py): layouts with 1500 or more open tiles (the five large ones and Slithery Fight). Busy tile = a tile with 8 or more natural pearl births in that game
  (10 to about 120 tiles a game; they give 80 to 93 percent of all births on Around UNSW, Islands and Slithery Fight, about half on Australia and Schooltime 2, a quarter on Schooltime 1).
  Snapshots at the start of rounds 100, 125, ..., 300 in which the two sides are within 10 percent in dragons alive. Share of heads within 2 tiles of a busy tile:
  main: ours 0.212, theirs 0.318 (11,350 and 11,698 heads, 197 snapshots). v31: ours 0.203, theirs 0.317 (17,554 and 18,041 heads, 301 snapshots).
  Standing on a busy tile: 0.054 against 0.080 (main), 0.052 against 0.080 (v31). With a looser cut (5 births): 0.28 against 0.37 and 0.26 against 0.37.
  By layout, ours / theirs, main then v31: Around UNSW 0.16 / 0.27 and 0.16 / 0.31; Slithery Fight 0.27 / 0.37 and 0.26 / 0.37; Schooltime 2 0.29 / 0.43 and 0.36 / 0.41;
  Islands 0.18 / 0.23 and 0.18 / 0.24 (6 and 11 snapshots); Australia 0.17 / 0.18 (4 snapshots) and 0.12 / 0.12 (30 snapshots): nothing there.
  Two other counts of this hour point the same way. F19a (bar failed, reversed): at the same snapshots their heads are closer to each other than ours in 66 of 78 non-tied snapshots on main
  and 104 of 122 on v31 (median distance to the nearest friend). F19b (bar failed): they do not push into our half more than we push into theirs (0.29 against 0.29; 0.30 against 0.30).
would be wrong if: (their share minus ours) under 8 points on main or v31, or positive on fewer than 4 of the 6 layouts in either code (layouts with under 5 balanced snapshots left out).
  Passed: 10.6 and 11.4 points; positive on 5 of 5 counted layouts (main) and 4 of 5 (v31). Written at 04:14 after F19a had come out reversed and with F16 and the team's fountain summary in mind.
inferred: This is the ladder-wide version of the team's fountain count against one opponent, now at equal dragon numbers: they keep dragons parked where pearls reappear, close together; ours are spread
  evenly and do not go into the enemy half any less. It is what F16 (more pearls born beside their heads) and the first half of F11 (their head is nearer in 6 of 10 contested births) are made of.
  main.cpp has no memory of where pearls reappear: nothing in it names a respawn or a fountain, and the pearl pull works on pearls in sight.
not checked: balanced snapshots are mostly two layouts (Around UNSW and Slithery Fight hold 160 of 197 on main), so "layouts with fast tiles" rests on those two plus Schooltime 2; Australia does not show it.
  Busy tiles are defined from the whole game, so a side that camps a tile helps make it busy; a map-only definition needs the hidden respawn gaps. Not split by opponent.
look at: data/online/ladder/1270027/M1270028.replay r100-300 (Around UNSW vs 1851, new: 60 dragons each at r100, pearls 495 against 905 in r101-300, lost);
  data/online/ladder/1249035/M1249035.replay r100-300 (Around UNSW vs 2382); data/online/ladder/1266953/M1266954.replay r100-300 (Slithery Fight vs 1810, new, lost on longest dragon).
smallest test: a new default-off switch (nothing like it exists in main.cpp), say RESPAWN_MEMORY: each dragon remembers tiles where it saw a pearl appear twice within 12 rounds, and a small dragon with no pearl
  in sight is pulled to stay within 2 tiles of the nearest remembered tile that has no friend on it. Pass mark to write first, local games on Around UNSW and Slithery Fight:
  our share of heads within 2 tiles of a busy tile at r150 rises from 0.2 to 0.3 and our pearl share in r101-300 rises above 0.40.

### F16 With the same number of dragons, more pearls are born beside their dragons than beside ours
status: candidate (the same thing as F20 seen from the pearls; its proposed cause is refuted)      first seen: 7 Oct 03:17 KST   last tested: 7 Oct 04:10 KST
measured (own count, work/h3_reach2.py last hour, work/h4_pass.py this hour): natural pearls born when the sides are within 10 percent in dragons alive, within 6 tiles of their heads only / of ours only.
  Last hour: main 1.37, v31 1.35, carried by Around UNSW (1.72, 1.67) and Slithery Fight (1.44, 1.55); other layouts 0.74 to 1.27.
  This hour, the test of last hour's guess that our feeding from round 200 opens it. By hundred rounds on those two layouts: main r0-99 1.26, r100-199 1.71, r200-299 1.55, r300-399 1.59;
  v31 1.10, 1.67, 2.04, 2.03. The surplus is already there in r100-199, before any feeder death (none happens before r201).
would be wrong if: (03:19, passed) ratio under 1.25 in any of main b, main c, v31 b, v31 c.
  (03:24, counted 04:10) feed-cap bar: the ratio in r200-299 is less than 0.15 above r100-199. FAILED on main (1.55 against 1.71); on v31 it rises but from 1.67, not from under 1.25.
inferred: Feeding at round 200 (FEED_CAP_ROUND, FEED_CAP_UNITS) is not the cause. The gap opens between r100 and r200 on the two layouts where both sides have 50 to 60 dragons. See F20.
not checked: nothing further planned under this number.
look at: as F20.
smallest test: none of its own; see F20. FEED_CAP_UNITS 0 is not supported as a test by this count.

### F18 On Stripes our dragons will not step through a portal onto a pearl; the general versions of this claim are refuted
status: candidate (one layout; two bars for wider versions failed)      first seen: 7 Oct 04:07 KST run 20261007-0400   last tested: 7 Oct 04:17 KST
measured (own counts, work/h5_decline.py and work/h7_pocket.py; a chance = a dragon turn that starts with a pearl on a free tile next to its head; passed up = it eats nothing that turn):
  General claim "we pass up adjacent pearls more than opponents do in r0-100": FAILED. main 0.203 against their 0.243 (29,539 and 31,816 chances); v31 0.199 against 0.229. We pass up fewer.
  Narrower claim "it is the bot's pocket rule (POCKET_CAP 48, POCKET_DIV 2, POCKET_PENALTY 1000)": FAILED. Where that rule applies we pass up 0.337 against their 0.358 (main) and 0.327 against 0.364 (v31);
  without Stripes 0.27 against 0.39 in both codes. On Portals, where three quarters of the pearls are born in rooms of 4 tiles or fewer, we pass up 0.31 against 0.43.
  What is left is Stripes (24 by 12, 2 starting dragons of length 2, 86 to 88 percent of pearls born in kelp-closed rooms of 3 or 4 tiles that are entered only through a portal):
  r0-100, all chances: main 0.69 against 0.25 (366 and 447 chances, 9 games); v31 0.62 against 0.21 (978 and 1,144, 26 games). Opponents under 1900: 0.77 against 0.22 (main), 0.62 against 0.25 (v31); 1900+: 0.66 against 0.25, 0.62 against 0.16.
  r0-199, the pearl is one step away through a portal into such a room: main 0.906 against 0.395 (385 and 301 chances); v31 0.867 against 0.375 (1,175 and 856).
  The pearl is in such a room and no portal step is needed (the dragon is already inside): 0.06 against 0.11 and 0.05 against 0.13. So ours eat once inside; they do not go in.
  By length on Stripes (main): length 2 passes up 0.84 (theirs 0.33), length 3 0.64 (0.10), length 4 or more 0.29 (0.26).
  Results on Stripes: every game ends by elimination (35 of 35); we are the side eliminated in 7 of 9 main games and 17 of 26 v31 games; in the 7 lost main games pearls by r50 are 1 to 8 for us and 10 or more for them in 6.
would be wrong if: (04:07) our pass-up rate / theirs under 1.5 on main or v31, or above 1.25 on fewer than 60 percent of layouts. FAILED: 0.84 and 0.87; 4 of 18 and 4 of 19 layouts.
  (04:13) pocket bar: under 2 times theirs on pocket chances, or under 1.5 times without Stripes. FAILED: 0.94 and 0.90; 0.71 without Stripes.
  The Stripes numbers were looked at after both failures; nothing about them was predicted. That is why this is a candidate about one layout and not a finding about a map property.
inferred: On Stripes a short dragon of ours circles outside a portal for tens of rounds with a pearl one step behind it. In score_portal_step() a portal step is rejected outright when the exit is unknown
  (exit below 0), when the mouth is fresh, when portal_guarded() and the exit is not safe, and otherwise costs PORTAL_LEAP_PENALTY 150; the queen never takes a portal (QUEEN_NO_PORTAL true), and she is one of our two
  starting dragons there. Which of these fires on Stripes and not on Portals is not known; on Portals the same step is taken more often than by opponents (0.44 passed up against 0.59).
  The map property would be "the pearls are in small rooms behind a portal and each side starts with 2 short dragons", but one layout cannot show a property.
not checked: which branch of score_portal_step() refuses the step (needs the bot run on the replay, or a local game with a print); why Portals differs (3 starting dragons of length 3; rooms of 1, 2 and 4 tiles).
look at: data/online/ladder/1254072/M1254072.replay r10-45 (Stripes vs 2030: our dragon 2 circles tiles 17,7 17,8 18,8 18,7 for 35 rounds; the west edge of 17,8 is a portal edge and a pearl sits one step behind it every time it passes;
  their dragon enters the matching room at r9, eats two, splits, and repeats at r30 and r43). work/h4_trace.py and work/h4_draw.py print the trace and the board.
smallest test: no switch yet. First one local game on Stripes with a debug line in score_portal_step() saying which return fired for a non-queen dragon at a portal with a pearl behind it.
  If it is the unknown-exit or guard branch, the test is a default-off switch that lets a dragon of length 2 or 3 take a portal whose exit tile holds a pearl. Pass mark to write first: our pearls by r50 on Stripes rise from 4 to at least 10.

### F8 The opponent is the one who rams in two thirds of head-on meetings
status: confirmed (verifier: holds)      first seen: 7 Oct 03:06 KST   last tested: 7 Oct 03:43 KST (verifier); not re-counted on the 15 new games this hour
measured (own count last hour, recounted exactly by the verifier): share of cross-team head-on meetings in which their dragon was the mover: main 0.657 (8,313 meetings, 210 games); band b 0.701; band c 0.630;
  half 1 0.639; half 2 0.671; v31 0.675 (16,491 meetings). Above 0.5 for 22 of 24 opponents (v31 40 of 43) and in 129 of 181 main games that are not level.
  Verifier: not a head-count effect (we have half the living dragons) and not our short dragons standing in the way (0.67 where both are longer than 2). The layout matters: 0.32 to 0.82;
  the five large layouts and Slithery Fight hold 61 percent of the meetings, all at 0.65 or more; on Prisoners Dilemma 1 and 2, Autarky, Devil and weakhold it is at or under one half.
  Cost, two bars written first, both FAILED last hour: we lose less length than they do (ratio 0.90, interval 0.86 to 0.94), and teams that ram more do not beat us more (rank correlation +0.01 main, -0.37 v31).
would be wrong if: their mover share under 0.58 in any of band b, band c, half 1, half 2 or on v31; or above 0.5 for fewer than 70 percent of opponents. Passed, recounted.
inferred: Opponents take the one-for-one head-on far more readily than we do; main.cpp allows a ram only by a dragon of length 4 or less against a target of at least 5 parts or its own length plus 2
  (TRADE_TARGET_MIN_PARTS 5, TRADE_EVEN false, TRADE_MIN_UNITS 8, TRADE_LOCAL_EDGE 1). No count shows that this costs us games. The layouts where they ram most are the layouts of F20 and F11, so the
  rams may be how they clear our dragons off the busy tiles; that is a guess.
not checked: whether the meetings they start are at busy tiles (the count planned last hour was not done; F20's busy-tile definition can now be reused for it).
look at: data/online/ladder/1256635/M1256637.replay r91-200 (Australia vs 1924: 88 meetings, they are the mover in 97 percent);
  data/online/ladder/1240862/M1240862.replay r34-100 (Slithery Fight vs 1814: 105 meetings, 91 percent, and we won).
smallest test: no change yet. Count first: share of the meetings they start that are within 2 tiles of a busy tile, against the meetings we start.

### F15 Our "no action" deaths are feeder deaths and they work; this is not a fault
status: confirmed (verifier: holds)      first seen: 7 Oct 02:09 KST (as a note)   last tested: 7 Oct 03:43 KST (verifier); not re-counted on the 15 new games
measured (own count last hour, recounted exactly): main 5,895 deaths in 210 games, none before round 201; 92.8 percent within 8 tiles of one of our dragons at least twice as long; of 8,565 pearls dropped
  our side ate 80.4 percent within 15 rounds, the opponent 3.3 percent. Same in both rating bands. v31: 10,326 deaths; 93.0, 79.4 and 3.5 percent.
  Verifier: a rule and not a crash (every one is a plain no-action reply in the dragon's own turn, one of our heads within 3 tiles in all of them, no enemy head within 3 in any).
  Two limits it adds: we get back 0.445 of the length given up (a body drops one pearl per two segments); and it is no edge, opponents' own no-action deaths are eaten by their side at 0.84.
would be wrong if: fewer than 80 percent within 8 tiles of an own dragon twice as long; our side eats under 70 percent of the drop; the opponent eats more than 15 percent. Passed, recounted.
inferred: ready_to_die() in main.cpp doing what it was written to do. The team's question "deliberate or a fault" is answered: deliberate.
not checked: whether feeding is the right call in each game (it wins the both-queens-dead games: 73 of 117 on main).
look at: data/online/ladder/1246505/M1246508.replay r300-499 (Maze vs 1776: 93 feeder deaths after r300, our longest ends at 85 against 29, won).
smallest test: none needed.

### F4 Teams rated 2100+ are ahead of us by round 100 because they eat more, not because they split earlier or kill more of ours
status: candidate      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 03:10 KST (no new game against 2100+ this hour)
measured: v31, 48 games against 2100+: dragons alive at r100 24.0 against 30.9; deaths in r0-100 40.0 ours against 42.0 theirs; splits by r100 59.3 against 68.2; pearls in r0-100 134 against 174.
  main, 9 games: alive 23.7 against 41.0, deaths 36.6 against 45.6, pearls 125 against 212. Against bands b and c the same numbers are level. 5th split round differs by 1 (F4b failed last hour).
  By layout (v31, share of pearls by r100 against 2100+): Stripes 0.07, Tower Defense 0.08, Trauma 0.18, Australia 0.27, Schooltime 2 0.27, Queen Of Spades 0.31, Around UNSW 0.36, Islands 0.39; level elsewhere.
  main has still 10 games against 2100+ (1 won, 2 battles lost). Nothing new this hour.
would be wrong if: in the next 10 main games against 2100+ we are behind at r100 in 5 or fewer. None arrived.
inferred: The top teams are the strongest case of F7, F18, F10 (the 2-start openings) and of F11 and F20 (large layouts), not a separate thing. On large layouts our r101-300 share falls with rating: 0.38, 0.31, 0.26 (main).
not checked: the F20 count has not been split by opponent rating; it should be (bar for next hour in state.json).
look at: data/online/ladder/1249035/M1249035.replay r0-100 (Around UNSW vs 2382: pearls 141 against 392 by r100).
smallest test: none of its own.

