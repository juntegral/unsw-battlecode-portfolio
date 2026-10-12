# one15 (bot 21583) losses, newest first (loss15-sonnet)

Status 13:25 KST (final). One15 (bot 21583) games on disk: 56 = one15-c1 (Cache me outside 2264, seat A: 5 W / 10 L), one15-p1 (Preyas 2228, seat A: 6 W / 9 L), one15-s1 (Team SKKU 2174, seat A: 9 W / 6 L), ranked b1524544 (the uncancelables 2162, seat A: 2 W / 3 L), ranked b1526090 (Team SKKU 2183, seat B: 3 W / 2 L), 1522669 (tozoman, Autarky, WIN). Total 26 W / 30 L. one16 went live after b1526090 (set one16-c1 is not analysed here); no one15-q1 set exists.
Ranked battles 1522311 / 1522401 / 1522569 / 1522426 are one14 (bot 21497), not one15.
Marks: [M] measured from replay, [E] inferred. "free" = free steps ceil(length/4); "paid" = more steps than that. f0 / f1 = free neighbour cells of her head at the start of her second-last / last turn.
Scripts: l15.py (game summary), early.py (first rounds), r100.py, detect.py (copy of stuck-opus detector, writes here), qexit-opus/qdeath.py scan for queen deaths.

## ONE16 (bot 21651, live since 03:51 UTC) set one16-c1 vs Cache me outside (2265), all seat A: 3 W / 12 L (one15 5 W, one14 7 W on the same team)
Portal check: Portals 1528867 (WIN) queen portal steps r0-99: none (one15 1523633: r4, r8, r64, r70); r100 22 dragons / 59 total vs one15 16 / 44. Stripes 1528858 (LOSS): queen steps at r9 and r13 (one15 1523624: r38, r43); r100 7 / 16 vs one15 1 / 3 (them 8 / 21).
One line per loss (class; r100 us dragons / total vs them):
- 1528859 Tower Defense: starved (r100 1 / 3 vs 27 / 63, 1 natural pearl), queen L2 rammed r129 by L3 (2 steps, paid) from a 1-free cell (f1=1). Out-eaten + rammed from a one-way place.
- 1528863 Schooltime: no queen death (both queens L3, both top dragons 74); lost on total 238 vs 281 at r499; out-eaten from r50 (r100 26 / 70 vs 63 / 173).
- 1528855 Australia: queen L4 rammed r280 by L4 (3 steps, free 1, paid), unseen, open ground (f 3/3/3), their queen dead since r172; out-eaten from r100 (25 / 57 vs 61 / 149). Rammed in the open.
- 1528854 weakhold: SELF-TRAP r129 (queen L2 on a wall, split the turn before, f0 = f1 = 0) in a game we dominated (r100 16 / 38 vs 11 / 26; their total 4 by r300; we ended 75 vs 4 and lost on queen length). Thrown game.
- 1528858 Stripes: queen L2 rammed r87 by L2 (1 step, free) from a 1-free cell, their queen dead since r13; level at r100 (7 / 16 vs 8 / 21), then 1 vs 26 at r200. Rammed from a one-way place.
- 1528865 Devil: queen L3 rammed r134 by L3 (2 steps, paid) from a 1-free cell, their queen dead since r76; behind from r50 (19 vs 40). Rammed from a one-way place.
- 1528864 Trophy: queen L4 alone (no mate within 4) among 6 enemy heads (L2-L7) within 6 for 12 rounds, split 4 to 2 + 2 at r48 and rammed the same round by L3 (2 steps, paid); open (3 free). Rammed in the open, no escort.
- 1528868 Slithery Fight: queen L19 cut to 2 at r363 (foe L56 head at distance 3: another cut like 1525842 / 1527409), rammed r476 as L2 by L4 (2 steps, paid); their queen dead since r26; lost on longest 66 vs 91. Cut then rammed (BUG-like, 3rd game).
- 1528866 Trauma: starved start (r100 7 / 17 vs 25 / 63); queen grew to L33, rammed r390 by L3 (1 step, free, unpaid) from a 1-free cell with her mate 1 away; their queen 48 alive. Rammed from a one-way place.
- 1528861 Default: queen L3 rammed r128 by L3 (3 steps, paid), unseen, open; their queen dead since r66; behind from r50 (25 vs 49). Rammed in the open.
- 1528857 Maze: SELF-TRAP r144 (queen L2 onto her own tail, split the turn before, f0 = f1 = 0), r200 191 vs 93 total, ended 152 vs 94 and lost on queen length (theirs 66). Thrown game.
- 1528860 Around UNSW: queen L4 rammed r168 by L5 (3 steps, free 2, paid), unseen, open; both queens dead at the end; lost the longest dragon 41 vs 42 (one cell). Rammed in the open.
Tally one16: rammed from a one-way place 4, rammed in the open 4, self-trap 2, cut to 2 then rammed 1, no queen death (out-eaten) 1. Queen died in 11 of 12; their queen was already dead when ours died in 5 (Australia, Stripes, Devil, Slithery, Default) and died later in Around UNSW, so those 6 are wins for a surviving queen.
Not seen in one16 that one15 did: a start collapse on Portals (gone). Seen again: queen cut to 2 (3rd game), self-trap (2 games that were crushing wins), starve on Tower Defense (identical 1 / 3).

## One15 set one15-s1 vs Team SKKU (2174), all seat A, 6 losses of 15 (9 wins), done 03:55 UTC

K1. **1527409 Trauma** (1152). [M] eliminated r486: us 0, them 26 / 102.
   Starved start (3 dragons / 14 at r100 vs 8 / 17; eats 9 vs 18), but then grew a queen of L31 by r410 while theirs was L3-4: we led the queen race 31 vs 4 at r400.
   [M] Decisive: r423 split 31 -> 29 + child 2, r424 split 29 -> parent (queen) L2 + child L27, enemy L2-L3 heads at distance 3-6, free 2. She regrew to 8 and was rammed at r486 by dragon 323 (L13, 5 steps, free 4, paid 1), unseen by her and mates; f 2/2/2/3. Their queen alive.
   Class: queen split down to 2 (BUG-like, 2nd game with 1525842), then rammed later. Without the cut the queen race was won.
K2. **1527410 Portals** (512). [M] queen race at r499: ours dead (r10) vs theirs 6 (alive); we held 3 dragons / 60 total, top 41; they 7 / 58.
   Behind on total to r325 (38 vs 48 at r100, 71 vs 84 at r300), ahead from r350 (90 vs 59), 60 vs 58 at the end; no queen from r10.
   [M] Decisive: r10 queen L5 split to L3 + child 2 and on her next move hit the child's tail (reason 2, hit mate id 8 tail); f0 = 0, f1 = 0 (no free cell at either turn start). Their queen alive.
   Class: queen self-trap after a split (the 4th one15 Portals / Maze case; this time at r10, killing a game we led on total).
K3. **1527401 Stripes** (288). [M] eliminated r253: us 0, them 25 / 56.
   Behind from r50 (6 vs 15); 3 dragons / 6 total at r100 (them 9 / 24), eats 10 natural vs 42.
   [M] Decisive: r57 queen L2 rammed by dragon 5 (L3, 1 step, free, not paid), gap 1, seen by her and a mate; f0=1, f1=1, f1a=1 (boxed, 1 free cell).
   Class: out-eaten from the start, queen rammed from a one-way place. Known.
K4. **1527400 Maze** (1152). [M] queen race at r499: ours dead (r152) vs theirs 6 (alive). We had 19 dragons / 163 total / top 40 vs 15 / 59 / 17.
   Ahead from r75 (56 vs 49) and far ahead later (216 vs 93 at r200); our queen stayed L2 from r100.
   [M] Decisive: r152 queen L2, own move, f1 = 0: her last free cell had been closed by our own mate dragon 177 (L2 head); she hit that head (reason 3), both died (f0=2, f0a=1). Their queen (L2-4 all game, 17 grew only at r425) alive.
   Class: queen boxed in by an own mate's head (the 'mate closes the cell' variant of self-trap). Known class, but here it cost a 163 vs 59 game.
K5. **1527398 Australia** (4096). [M] longest at r499: us 47 / 226 / top 25; them 27 / 211 / top 26 (lost by one cell); both queens dead.
   Ahead from r75 (74 vs 45) to r225 (190 vs 153), behind on total from r325 (175 vs 200).
   [M] Decisive: r293 queen L2 rammed by dragon 306 (L3, 2 steps, free 1, paid), gap 2, in her view; f0=3, f0a=1, f1=1, f1a=3 (moved from open ground to a 1-free place a turn earlier). Their queen died at r195, 98 rounds before ours.
   Class: queen rammed from a one-way place (small queen L2 for 190 rounds). Known. A live queen wins this game.
K6. **1527411 Slithery Fight** (1701). [M] longest at r499: us 28 / 112 / top 21; them 19 / 224 / top 66; both queens dead.
   Ahead to r125 (203 vs 155), level to r225, behind from r325 (205 vs 218).
   [M] Decisive: r256 queen L6 rammed by dragon 884 (L9, 8 steps, free 3, paid), gap 6, not in her view but in a mate's; f 3/3/3/2 (open). Their queen died at r145, 110 rounds earlier: a live queen wins.
   Class: queen rammed in the open by a paid sprint, unseen. Known.

## One15 ranked battle b1526090 vs Team SKKU (2183), seat B, 2 losses of 5 games (done 03:41 UTC = 12:41 KST)

S1. **1526090 Australia** (4096). [M] longest at r499: us 50 dragons / 231 total / top 18; them 25 / 173 / top 28; both queens dead.
   We led on total from r75 (74 vs 50) to the end and lost on the longest dragon (18 vs 28).
   [M] Decisive: r86 queen L3 rammed by dragon 62 (L3, 1 step, free, not paid), gap 1, in her view; f0=1, f0a=2, f1=2, f1a=2 (not boxed). Their queen (L2-3) was alive until about r310-325 (3 at r300, 0 at r325): a live queen of ours would have won.
   Class: queen rammed in the open, tiny queen (L3). Known.
S2. **1526093 Slithery Fight** (1701). [M] queen race at r499: ours dead (r445) vs theirs 16 (alive); us 16 / 106 / top 46, them 16 / 222 / top 49.
   Ahead to r250 (287 vs 177), behind from r375 (199 vs 221).
   [M] Decisive: r445 queen L34 rammed by dragon 1670 (L5, 3 steps, free 2, paid 1), gap 3, not in her view or a mate's; f0=2, f1=2, f1a=2 (open). With the queen alive at 34 vs 16 the game is ours on queen length.
   Class: queen rammed in the open by a paid sprint, unseen (a L34 queen taken by an L5). Known.

## One15 set one15-p1 vs Preyas (2228), all seat A, 9 losses of 15 (folder live-one1/b1525830, done 03:32 UTC)
(one14 on the same set lost 11, one13 lost 11.) Queen = our queen; "dead" = her death round.

P1. **1525842 Trauma** (1152). [M] queen race at r499: ours dead (r431) vs theirs 38; us 3 dragons / 8 total, them 21 / 128.
   Behind from r75 (17 vs 38), r100 22 vs 62 (9 vs 28 dragons). Our queen grew to L21 by r400 (theirs 20).
   [M] Decisive: r430 the L19 queen, on a cell with 1 free neighbour and two L3 enemy heads at distance 3-4, SPLIT: parent (queen) L2, child L17. r431 the L2 queen was rammed by dragon 331 (L3, 1 step, free, not paid), gap 2. Their queen alive.
   Class: queen split then rammed (the split left the queen with 2 of 19 cells). Only game of this class so far.
P2. **1525835 Tower Defense** (512). [M] eliminated r94: us 0, them 17 / 44.
   2 dragons / 5 total from r0 to r75, 1 pearl eaten all game vs 46 for them.
   [M] Decisive: starved start; r94 queen L3 rammed by dragon 11 (L3, 2 steps, free 1, paid), gap 2, in her view; f0=2, f1=2, f1a=2 (open). Their queen alive.
   Class: out-eaten from the start, queen rammed in the open. Known (4th game with this map starved in one15/one14/one13).
P3. **1525834 Stripes** (288). [M] eliminated r103: us 0, them 24 / 54.
   Behind from r25 (7 vs 15), r75 13 vs 36, 1 dragon / 3 at r100.
   [M] Decisive: r79 queen L3 died on a wall on her own move: f0=1, f0a=0, f1=0, no split. Their queen alive.
   Class: queen self-trap (moved into a 0-free-cell dead end, then hit the wall). Known class, no enemy involved.
P4. **1525843 Portals** (512). [M] longest at r499: us 4 / 38 / top 22; them 5 / 60 / top 24; both queens dead.
   Level to r50 (32 vs 35 total), behind from r75 (36 vs 51; 41 vs 66 at r100); our top dragon only 4-5 until r325.
   [M] Decisive: r288 queen L3 died on her own body (reason 1, own move) one turn after a split of L5: f0=0, f1=0, hit own body. Their queen (L22 at r400) died about r425, 140 rounds after ours.
   Class: queen self-trap after a split (known; 3rd one15 Portals/Maze case). A live queen would have won on queen length.
P5. **1525838 Queen Of Spades** (875). [M] eliminated r304: us 0, them 40 / 97.
   Behind from r25 (13 vs 16), r100 25 vs 34, slow decline from r225.
   [M] Decisive: r33 queen L3 on her own move rammed a foe L2 head (reason 3) with f1=0: that head had closed her last free cell (f0=2, f0a=1). Both died. Their queen alive. No queen for the next 270 rounds.
   Class: queen boxed in by a small foe head, traded. Known (qexit R0 / boxed).
P6. **1525844 Slithery Fight** (1701). [M] queen race at r499: ours 14 (alive) vs 44 (alive); us 28 / 183 / top 53; them 17 / 268.
   Ahead at r50 (112 vs 104), behind from r75 (146 vs 164), 209 vs 269 at r200.
   [M] Decisive: our queen stayed L3-4 from r25 to r300 while theirs grew from r200 (5) to 63 (r475). Our queen's length at r325 11, r350 4 (split), r425 15, r450 2, r499 14.
   Class: lost the queen race with the queen alive (queen kept short, then split down). Not a death. Known.
P7. **1525831 Australia** (4096). [M] longest at r499: us 24 / 144 / top 27; them 29 / 335 / top 39; both queens dead.
   Level to r75 (65 vs 64), behind from r100 (77 vs 111), r200 97 vs 270.
   [M] Decisive: r171 queen L3 rammed by dragon 65 (L4, 3 steps, free 1, paid), gap 3, seen by her and a mate; f0=3, f1=3 (open). Their queen had died at r160, 11 rounds earlier: a live queen would have won.
   Class: queen rammed in the open by a paid sprint, small queen. Known.
P8. **1525830 weakhold** (600). [M] longest at r499: us 2 / 20 / top 13; them 7 / 68 / top 24; both queens dead.
   Level to r100 (34 vs 37), behind from r125 (42 vs 52).
   [M] Decisive: r84 queen L2 rammed by dragon 66 (L2, 1 step, free, not paid), gap 1, not seen; f0=2, f1=3, f1a=2 (open). Their queen L2 lived until r388 (killed by our L3 dragon).
   Class: queen rammed in the open (queen L2 for 80 rounds). Known.
P9. **1525836 Around UNSW** (4096). [M] longest at r499: us 44 / 259 / top 35; them 26 / 391 / top 52; both queens dead.
   Out-eaten early: 41 vs 61 at r25, 77 vs 145 at r50 (31 vs 60 dragons), 114 vs 270 at r100.
   [M] Decisive: r133 queen L3 rammed by dragon 275 (L8, 2 steps, free 2, not paid), gap 2, unseen; f0=3, f1=3 (open). Their queen (L6) died about r240, 110 rounds after ours.
   Class: out-eaten from r25 (big map), queen rammed in the open. Known.

## One15 ranked battle b1524544 vs the uncancelables (2162), seat A, 3 losses of 5 games (done 03:21 UTC = 12:21 KST)

A. **1524545 Portals** (512 cells). [M] decided by queen at r499: theirs 80 (1 dragon, 80 total) vs ours dead; we held 5 dragons / 52 / top 41.
   We led from the start: r100 16 dragons / 42 total vs 4 / 11, eats 183 vs 5; they sat at 3 dragons / 9 until r125. Behind on queen from r31, behind on total from about r425 (58 vs 65).
   [M] Decisive: r29 queen L5 left (19,6) through its west portal into cell (12,3) (walls N, S, W, only the portal edge back onto her own body); r30 she split 5 into 3 + 2; r31 she died on a wall (reason 0, own move, L3, f0=0, f1=0). Their queen was alive and grew to 80 in 1-dragon form from r325.
   Class: queen self-trap in a portal cul-de-sac (known class, see tally; 2nd one15 game after Maze 1523623). She chose a move into a cell with no way on.
B. **1524544 Trophy** (625 cells). [M] eliminated r194: us 0, them 63 / 166.
   Level to r25 (14 vs 13 total), behind from r50 (18 vs 26), r100 11 / 27 vs 24 / 61.
   [M] Decisive: r78 queen L2 rammed by dragon 43 (L3, 1 step, free 1, not paid), gap 1, in her view; f0=3, f0a=1, f1=1. Their queen had died at r20, so a live queen would have won on queen length.
   Class: queen rammed from a one-way place (she moved from 3 free cells to 1 a turn earlier). Known.
C. **1524548 Tower Defense** (512 cells). [M] eliminated r183: us 0, them 35 / 84.
   2 dragons / 4 total until r50, eats 0 for us vs 79 for them by r100 (17 vs 79 events).
   [M] Decisive: starved start; r53 queen L2 rammed by dragon 4 (L3, 2 steps, free 1, paid), gap 2, in her view; f0=2, f1=2, f1a=3 (not boxed). Their queen was alive then (dead by r75).
   Class: out-eaten from the start (3rd game on this map with 1-4 dragons at r100), then queen rammed in the open. Known.

## One15 losses vs Cache me outside (2264), all seat A, all with their queen alive when we lost ours or already dead

1. **1523634 Slithery Fight** (1701 cells). [M] decided by longest dragon at r499: us 15 dragons / 160 total / top 53, queen dead; them 26 / 208 / top 78, queen dead since r42.
   We were ahead on total until r375 (200 vs 181) and had the only queen: L44 at r391. Behind for good from r400 (177 vs 193).
   [M] Decisive: r391 our queen L44 was rammed by their dragon 1478 (L3 at turn start, 4 steps, free 1, paid), gap 4, not in her own view but in a mate's view; f0=3, f1=3, f1a=1 (she moved into a 1-free place). Their queen was already dead, so a surviving queen would have won on queen length.
   Class: queen rammed by a small dragon via a paid sprint, after she stepped into a one-free-cell place (queen rammed from a one-way place). Known class (qexit). Not new.
2. **1523622 Islands** (2240 cells). [M] longest at r499: us 25 / 110 / top 18; them 35 / 226 / top 44; both queens dead.
   Out-eaten from r50 (59 vs 80), 34 vs 53 dragons at r100.
   [M] Decisive: r222 queen L3 rammed by dragon 462 (L20, 7 steps, free 5, paid 2), gap 5, in her view; f0=1, f1=3, f1a=1. Their queen had died at r57.
   Class: queen rammed from a one-way place (out-eaten start, then queen too short to escape). Known.
3. **1523630 Trophy** (625 cells). [M] eliminated r154: us 0, them 54 dragons / 131.
   Behind from r50 (22 vs 45), r100 31 vs 93.
   [M] Decisive: r137 queen L3 rammed by dragon 137 (L3, 2 steps, free 1, paid), gap 2, in her view and a mate's; f0=1, f1=1, f1a=2. Their queen dead since r90.
   Class: out-eaten from round 50, queen rammed from a one-way place. Known.
4. **1523621 Australia** (4096 cells). [M] longest at r499: us 29 / 152 / top 38; them 38 / 295 / top 80; both queens dead (ours r127, theirs about r225).
   Behind from r25 (30 vs 46); 31 vs 58 dragons at r100.
   [M] Decisive: r127 queen L4 rammed by dragon 175 (L9, 6 steps, free 3, paid 3), gap 6, not in her view, in a mate's; f0=1, f1=1, f1a=1. Their queen was alive then.
   Class: queen rammed from a one-way place (unseen). Known.
5. **1523632 Trauma** (1152 cells). [M] decided by queen at r499: ours 35 (alive) vs theirs 39; us 3 dragons / 41, them 40 / 167.
   Behind from r25 (8 vs 14), no pearl eaten until r60 (eats 0 / 20 at r40, 8 / 96 at r100).
   [M] Decisive: starved start. r100: 3 dragons / 10 total vs 25 / 62. The queen later grew from 3 (r300) to 35, lost the queen race by 4.
   Class: out-eaten from the start (no queen death). Not the starving switch: see the r100 line. Known class, but the worst start of the set (one14 on the same map and opponent: 14 dragons / 32 at r100).
6. **1523627 Default** (1024 cells). [M] eliminated r271: us 0, them 63 / 160.
   Even at r25 (21 vs 20 total), behind from r50 (24 vs 35), 12 vs 20 dragons at r100.
   [M] Decisive: r230 queen L2 rammed by dragon 103 (L4, 3 steps, free 1, paid), gap 3, in her view; f0=3, f1=3 (open ground). Their queen dead since r67.
   Class: queen rammed in the open by a paid sprint, small queen (L2) for 230 rounds. Known (queen hunt).
7. **1523628 Queen Of Spades** (875 cells). [M] eliminated r338: us 0, them 51 / 124.
   Level to r125 (43 vs 31 total, 15 vs 12 dragons), behind for good about r150 after the queen died (31 vs 39).
   [M] Decisive: r136 queen L4 rammed by dragon 41 (L4, 4 steps, free 1, paid 3), gap 4, not in her or a mate's view; f0=3, f1=3 (open). Their queen alive. Then 200 more rounds without a queen.
   Class: queen rammed, unseen, from open ground. Known.
8. **1523625 Tower Defense** (512 cells). [M] eliminated r112: us 0, them 25 / 60.
   Never ate: 2 dragons / 4 total from r0 to r75, eats 0 vs 70 natural pearls for them by r100.
   [M] Decisive: dragons wandered (20 distinct head cells in 20 rounds) with the nearest pearl 35-40 steps away at r0; r46-58 dragon 1 circled the block (19-20, 1-3) at 1-3 steps from a pearl pocket at x=16-18 for 12 rounds (not eaten by anyone, born r0-r43). Queen rammed r112 (L3 by an L4, 2 steps, free 1, paid; f0=1, f1=1) when their queen was dead since r65.
   Class: out-eaten from the start (no pearls found), then queen rammed from a one-way place. Same loss in one13 (r67) and one14 on this map. Known.
9. **1523624 Stripes** (288 cells). [M] eliminated r122: us 0, them 25 / 55.
   Behind from r25 (8 vs 12 total), r50 3 vs 18; 1 dragon / 3 at r100.
   [M] Decisive: r47 queen L3 rammed by dragon 20 (L2, 2 steps, free 1, paid), gap 2, in her and a mate's view; f0=1, f1=1, f1a=2. Their queen had died at r16.
   Class: queen rammed from a one-way place. Known. One13 and one14 also lost this map at r100 with 1-4 dragons.
10. **1523623 Maze** (1152 cells). [M] longest at r499: us 17 dragons / 129 / top 49; them 14 / 119 / top 53; both queens dead.
   We were ahead on total all game (92 vs 70 at r100) and lost by 4 cells of longest dragon.
   [M] Decisive: r101 queen L2 died on her own move into her own tail: r96-r99 she ate 3 pearls east along a 1-wide dead-end row (23-25, 22) with walls N and S, at r100 she split (L4 into 2 + 2, split0=1) with the end wall E, so f0=0, f1=0, no way out. Their queen L47 was killed by our dragon (L3, 2 steps) at r360; ours was dead 260 rounds earlier.
   Class: queen boxed in, self-inflicted (queen enters a dead-end row for pearls and splits there). Known class (see tally).

## Tally by class, ALL 30 one15 losses (10 Cache me outside + 3 uncancelables + 9 Preyas + 2 SKKU ranked + 6 SKKU test set); 26 wins (incl. tozoman); the only seat-B losses are the 2 ranked SKKU games
- queen rammed from a one-way place: 9 (1523634, 1523622, 1523630, 1523621, 1523625, 1523624, 1524544, 1527401, 1527398)
- queen rammed in the open (2+ free cells): 10 (1523627, 1523628, 1524548, 1525835, 1525831, 1525830, 1525836, 1526090, 1526093, 1527411)
- queen cut to 2 by her own split, then rammed: 2 (1525842, 1527409; both Trauma) BUG-like
- queen boxed in / self-trap (own move, f1 = 0): 7 (1523623 Maze, 1524545 Portals, 1525843 Portals, 1525834 Stripes, 1527410 Portals r10, 1527400 Maze closed by an own mate's head; 1525838 QoS closed by a foe L2 head, traded)
- lost the queen race with the queen alive: 2 (1523632 Trauma 35 vs 39, 1525844 Slithery 14 vs 44)
- Queen died in 28 of 30 losses [M]. Their queen was already dead when ours died in 10 of them (1523634, 1523622, 1523630, 1523625, 1523624, 1523627, 1524544, 1525831, 1527398 r195 vs 293, 1527411 r145 vs 256) and died later in 6 more (1523623, 1523621, 1525830, 1525836, 1525843, 1526090).
- Self-trap detail: KNOWN, not new: own-turn queen deaths on wall / own body / other body with f1=0 are 16/59 (one11), 7/56 (one12), 22/133 (one13), 9/38 (one14) of queen deaths (qexit-opus rows, deduped; script selftrap.py), many on Portals.
- out-eaten, queen alive, lost the queen race: 1 (1523632 Trauma)
- 7 of the 13: their queen was already dead when ours died (1523634, 1523622, 1523630, 1523625, 1523624, 1523627, 1524544).
- Older tally of the first 10 only, kept below.

## Tally by class (one15, first 10 losses, all one opponent)
- queen rammed from a one-way place (f1 = 1 or moved into one): 6 (1523634, 1523622, 1523630, 1523621, 1523625, 1523624)
- queen rammed in the open (3 free cells, f1a >= 3 or unseen): 2 (1523627, 1523628)
- queen boxed in / self-trapped: 1 (1523623)
- out-eaten, queen alive, lost the queen race: 1 (1523632)
- Overlap [M]: 5 of the 9 queen deaths came after we were already behind on total (Islands, Trophy, TD, Stripes, Australia). In 6 of the 10 losses their queen was dead BEFORE ours (1523634 r42, 1523622 r57, 1523630 r90, 1523625 r65, 1523624 r16, 1523627 r67): with our queen alive at r499 each of them would be a win on queen length [E, from the rule that a dead queen counts 0]. In all 8 rammed queen deaths the attacker paid for extra steps (steps used above ceil(L/4)) [M].
- No long dragon was rammed as the decisive event; no rule firing backwards; no illegal action found.

## Bug / new check
- BUG-like, 1 game: Maze queen split with 0 free cells in a dead-end row (above). Not in two games, so no alarm.
- Circling in front of a reachable pearl without eating (detector pattern c, 15+ rounds, no enemy near): 25 episodes in 8 of 15 one15-c1 games, all by L2-3 dragons, none by the queen [M]. Examples: 1523634 id27 r5-23 (L3), 1523629 ids 92 / 120 r364-378. Not decisive in any loss; this is stuck-opus territory.
- Not found: dragons standing still (pattern b) in any loss.

## First 100 rounds on the four maps (one15-c1 vs one14-c1 vs one13-c1, same opponent; us dragons / total length at r100)
- Queen Of Spades: one15 16 / 39 (them 14 / 32), one14 3 / 6, one13 7 / 18: fine, switch removal worked here.
- Australia: one15 31 / 75 (them 58 / 141), one14 22 / 54, one13 15 / 38: better than before, still half of theirs.
- Trophy: one15 13 / 31 (them 38 / 93), one14 won before r100, one13 18 / 43: not starved by the pearl count (51 natural pearls eaten) but behind by a factor three.
- Trauma: one15 3 / 10 (them 25 / 62), eats 7 / 74, one14 14 / 32, one13 5 / 13: NOT fixed against Cache me outside, worse than one14. Against Preyas (same map) one15 9 / 22 vs one14 7 / 16 vs one13 6 / 14 (them 28 / 62): better, still a third of theirs.
- Against Preyas (r100 dragons / total): QoS one15 10 / 25 vs one14 3 / 6; Australia 30 / 77 vs 24 / 61; Trophy 58 / 135 (win) vs one14 2 / 5; Trauma 9 / 22.
- Against Team SKKU (s1, seat A, r100 dragons / total, from the game tables): Australia 46 / 118 (them 27 / 63), Trauma 3 / 14 (them 8 / 17), QoS and Trophy won. Ranked SKKU (seat B) Australia 38 / 97 (them 36 / 88). So Trauma stays the one map where one15 starts with 3 dragons whoever the opponent is (c1 3 / 10, s1 3 / 14, p1 9 / 22).
- Tower Defense and Stripes again: p1 TD 2 dragons / 5 total until r94 and 1 pearl eaten in the whole game; p1 Stripes 1 / 3 at r100.

## Not one15 (one14, bot 21497), context only
- 1522311 Around UNSW, Quaker Qubits (2091), seat B: lost on queen length r499, ours 6 vs theirs 32; our queen stayed at 4 until r350 while our total was ahead (304 vs 156).
- 1522402, 1522403, 1522405 (Sponge), 1522573 (WeLikCoding), and SKKU set 1522426 losses are one14 too.
