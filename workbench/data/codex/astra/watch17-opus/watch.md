# watch17-opus: one17 (21693) live watch

## Verdicts (newest last; all counts [M] from replays unless marked)

### 13:56 KST, after one17-c1 (15 games against Cache me outside): one17 looks fine (15 games)
- 5 wins of 15 (one15-c1 5, one16-c1 3). No timeout in any of our turns, no sudden collapse, wiped 4 times (one15-c1 5, one16-c1 5),
  queen died in 11 games (13, 14), median queen death round 139 (137, 144), never at length 10 or more.
- No queen split from 10+ that leaves her 2 (one15 and one16 together: 4 in 91 games, so 15 games without one is also what chance gives).
- Queen 10+ with an enemy head within 3: 17 round starts in 2 games (Trauma 1532059, Slithery Fight 1532061). She moved on 14,
  split 2 cells off on 3, never stayed; alive 5 rounds later on all 17 (one15 dead within 3 rounds 3 of 57, one16 3 of 25).
- One thing to know, not new: Slithery Fight 1532061 r370 to r379 the queen stands at (41,1) and splits a 2-cell child off seven
  times (15 > 4), then walks into a wall at r380 at length 4. That is the older "not exposed, blocked" branch (main.cpp line 1797,
  `split_off(keep)`), which one16 and one15 also take (after r50, from 10+: one16-p1 25 times, one15-p1 6, one17-c1 4). [C]
  The game was lost on longest dragon, both queens dead; one16 on the same map shed 19 > 2 at r363 and died r476.
- Ranked battle b1532562 against Team SKKU (13:51): 4 wins of 5, queen alive at 78 on Autarky, no timeouts, nothing odd.
  With it: 20 games, 21 mechanism turns, 0 dead within 5 rounds.

### 14:06 KST, after ranked b1533048 (Computers, 2 of 5) and b1533125 (Team SKKU, 3 of 5): one17 looks fine (30 games)
- 30 games: 14 wins; timeouts 0; sudden collapses 0; sheds from 10+ to 2: 0; mechanism turns 25, dead within 3 rounds 0, within 5 rounds 0.
- Watch item: 1533128 Autarky r442 the queen at length 62 walks three free steps north, (19,8) to (19,5), stops next to a 3-cell
  enemy head at (19,4) and is rammed (head-on, the enemy's move). Game still won on longest 20:3 (enemy queen dead earlier).
  Her own cell was 4 away from that head at round start, so my "within 3" filter did not list the turn.
  Whether this went through the changed line cannot be read from the replay. If it did, the path is main.cpp 1824 to 1829
  ("Trapped: for this turn she moves as a plain dragon", `qs_plain`, then `hunt_path`). [E]
  The same kind of death exists before one17: one15 1523634 r391 (queen 44), one15 1526093 r445 (34), one16 1528866 r390 (33):
  each time she steps next to an enemy head and is rammed. Rate: 3 in 91 games before, 1 in 30 now.

### 14:13 KST, after ranked b1531921 (Check Raise, 3 of 5) and b1532570 (Sponge, 0 of 5): one17 looks fine (40 games), one caveat
- 40 games, 17 wins; timeouts 0; collapses 0; sheds from 10+ to 2: 0. Mechanism turns 26, dead within 3 rounds 1 (one15 3 of 57, one16 3 of 25).
- Second long-queen death: 1532574 Around UNSW r319, queen 11 at (29,35) steps one cell west and enemy 534 (3 cells, 4 away)
  sprints five steps, eating a pearl on the way, into her head. Lost on queen length, 0 against 4.
- Both long-queen deaths (this one and 1533128 r442) fit the route the change opens: own cell in an enemy's paid reach, no escape,
  length over 9 so no shed, then line 1813 (one step to a paid tile) or 1824 (plain dragon, hunt_path). [E] not readable from replays.
  Before one17 the same spots ended as a shed to 2: 4 in 91 games (1525842, 1527409, 1528868, 1530575), queen dead one round
  later in 2 of the 4, dead before the end in all 4, all 4 lost. Now: 2 spots in 40 games, queen dead at once in both, 1 lost 1 won.
  Long queen (10+) killed: one15 and one16 3 in 91 games, one17 2 in 40. Too few to call either way.

### 14:32 KST: one17 got no more games (one18, submission 21761, live from about 14:06). One18 first 10 games (b1535044, Preyas, unranked): looks fine
- one18: 4 wins of 10; timeouts 0; collapses 0; sheds from 10+ to 2: 0; 2 mechanism turns, queen alive 20 rounds later on both.
- Third long queen rammed: 1535047 Around UNSW r461, queen 15 steps one cell north, an enemy child split off that round
  (1067, from 798 five cells away) sprints into her head. Lost on longest 40:46, both queens dead.
- Long queen (10+) lost, dead or cut to 2: one15 + one16 7 in 91 games (3 killed, 4 shed to 2); one17 + one18 3 in 50 (3 killed, 0 shed).

### 14:36 KST: one18 looks fine (30 games); one17 looks fine (45 games)
- Added one18 battles b1535543 (test4, 3 of 5), b1535558 (Cybers, 3 of 5), b1535563 (the uncancelables, 2 of 5) and a late
  one17 battle b1533646 (BambooCode, 4 of 5). Timeouts 0, collapses 0, sheds from 10+ to 2: 0 in all.
- One more long queen killed (one17): 1533650 Slithery Fight r279 to r281, a 3-cell enemy 2 away for three rounds, queen 15
  steps one cell each round and at r281 steps to (27,21) right above its head at (27,22). Lost, 0 against 67.
- Dead within 3 rounds of a "queen 10+, enemy within 3" turn: one15 3 of 57, one16 3 of 25, one17 4 of 44, one18 0 of 7.
- Builds with the switch (one17 + one18, 75 games): 4 long queens killed, 0 shed to 2 (5.3%), 1 of those 4 games won.
  Builds without (one15 + one16, 91 games): 3 killed, 4 shed to 2 (7.7%), 0 of those 7 games won.

### 14:45 KST, last: one17 looks fine (45 games); one18 looks fine (35 games); one19 and one20 not judged (0 games on disk)
- one18 added b1535538 (Team SKKU) and b1535553 (Ballers, 1 of 5): 16 wins of 35, timeouts 0, collapses 0, sheds from 10+ to 2: 0,
  no further long queen killed. 1535553 Maze r232 to r251: queen 15 drained to 2 by the older by-2 splits and sheds from 9 or less.
- Final switch count: one17 + one18, 80 games, 4 long queens killed, 0 shed to 2 (5.0%); one15 + one16, 91 games, 3 + 4 (7.7%).
- versions.tsv lists one19 (21827, bot folder 14:33) and one20 (21843) after one18; no game of either reached the disk by 14:44.
- Not checked: whether the changed line itself was reached (the replay does not show which branch ran); head distance is plain
  torus distance, walls and portals ignored.

```
## one17 games: 45 (wins 21)
1531921 live    Stripes         Check Raise       WIN  | q 3 vs q dead, wipe(23:0 dragons), end r144 reason 0 | queen alive len 3 | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1531922 live    Queen Of Spades Check Raise       WIN  | q 4 vs q dead, wipe(37:0 dragons), end r213 reason 0 | queen alive len 4 | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1531923 live    Trophy          Check Raise       LOSS | q dead vs q 9, wipe(0:61 dragons), end r240 reason 0 | queen died r145 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1531924 live    Autarky         Check Raise       WIN  | q dead vs q dead, wipe(42:0 dragons), end r190 reason 0 | queen died r154 at len 3 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1531925 live    Default         Check Raise       LOSS | q dead vs q dead, longest 5:41, end r499 reason 1 | queen died r64 at len 3 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1532047 ne17-c1 weakhold        Cache me outside  LOSS | q dead vs q 4, queen length, end r499 reason 1 | queen died r99 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: no-action 1; reason-4 deaths 1
1532048 ne17-c1 Australia       Cache me outside  LOSS | q dead vs q 13, queen length, end r499 reason 1 | queen died r158 at len 4 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: no-action 51; reason-4 deaths 51
1532049 ne17-c1 Islands         Cache me outside  LOSS | q dead vs q dead, longest 35:58, end r499 reason 1 | queen died r139 at len 3 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: no-action 30; reason-4 deaths 30
1532050 ne17-c1 Maze            Cache me outside  LOSS | q dead vs q 25, queen length, end r499 reason 1 | queen died r216 at len 3 (body) | splits from 10+: none; sheds to 2 from <=9: 2 | odd: no-action 115; reason-4 deaths 115
1532051 ne17-c1 Stripes         Cache me outside  LOSS | q dead vs q dead, wipe(0:22 dragons), end r121 reason 0 | queen died r42 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 1 | odd: none
1532052 ne17-c1 Tower Defense   Cache me outside  LOSS | q dead vs q 4, wipe(0:17 dragons), end r73 reason 0 | queen died r73 at len 3 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1532053 ne17-c1 Around UNSW     Cache me outside  WIN  | q dead vs q dead, longest 50:36, end r499 reason 1 | queen died r136 at len 4 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: no-action 51; reason-4 deaths 51
1532054 ne17-c1 Default         Cache me outside  LOSS | q dead vs q dead, wipe(0:40 dragons), end r449 reason 0 | queen died r147 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 1 | odd: none
1532055 ne17-c1 Queen Of Spades Cache me outside  WIN  | q 2 vs q dead, wipe(30:0 dragons), end r265 reason 0 | queen alive len 2 | splits from 10+: none; sheds to 2 from <=9: 1 | odd: none
1532056 ne17-c1 Schooltime      Cache me outside  WIN  | q 3 vs q 3, longest 46:25, end r499 reason 1 | queen alive len 3 | splits from 10+: none; sheds to 2 from <=9: 1 | odd: no-action 85; reason-4 deaths 85
1532057 ne17-c1 Trophy          Cache me outside  LOSS | q dead vs q dead, wipe(0:63 dragons), end r172 reason 0 | queen died r172 at len 3 (headon) | splits from 10+: none; sheds to 2 from <=9: 1 | odd: none
1532058 ne17-c1 Devil           Cache me outside  WIN  | q dead vs q dead, wipe(45:0 dragons), end r111 reason 0 | queen died r21 at len 4 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1532059 ne17-c1 Trauma          Cache me outside  LOSS | q 30 vs q 33, queen length, end r499 reason 1 | queen alive len 30 | splits from 10+: none; sheds to 2 from <=9: 0 | odd: no-action 16; reason-4 deaths 16
1532060 ne17-c1 Portals         Cache me outside  WIN  | q 3 vs q dead, queen length, end r499 reason 1 | queen alive len 3 | splits from 10+: none; sheds to 2 from <=9: 5 | odd: no-action 34; reason-4 deaths 34
1532061 ne17-c1 Slithery Fight  Cache me outside  LOSS | q dead vs q dead, longest 34:71, end r499 reason 1 | queen died r380 at len 4 (wall) | splits from 10+: r0 25>23 (foe at 16), r1 23>21 (foe at 11), r2 21>19 (foe at 10), r3 19>17 (foe at 11), r4 17>15 (foe at 12), r5 15>13 (foe at 13), r6 13>11 (foe at 14), r7 11>9 (foe at 15), r370 15>13 (foe at 4), r372 14>12 (foe at 1), r373 12>10 (foe at 2), r374 10>8 (foe at 3); sheds to 2 from <=9: 0 | odd: no-action 83; reason-4 deaths 83; dragon 1 still 11 rounds to r11
1532562 live    Autarky         Team SKKU         WIN  | q 78 vs q dead, queen length, end r499 reason 1 | queen alive len 78 | splits from 10+: r341 25>23 (foe at 17), r342 23>21 (foe at 16), r399 56>54 (foe at 19), r438 67>65 (foe at 14), r439 65>63 (foe at 15), r440 63>61 (foe at 14); sheds to 2 from <=9: 0 | odd: no-action 90; reason-4 deaths 90
1532563 live    Trophy          Team SKKU         WIN  | q dead vs q dead, wipe(58:0 dragons), end r91 reason 0 | queen died r43 at len 3 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1532564 live    Devil           Team SKKU         WIN  | q 3 vs q dead, wipe(54:0 dragons), end r199 reason 0 | queen alive len 3 | splits from 10+: none; sheds to 2 from <=9: 2 | odd: none
1532565 live    Tower Defense   Team SKKU         LOSS | q dead vs q dead, wipe(0:29 dragons), end r355 reason 0 | queen died r74 at len 3 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1532566 live    Stripes         Team SKKU         WIN  | q 3 vs q dead, wipe(21:0 dragons), end r117 reason 0 | queen alive len 3 | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1532570 live    Islands         Sponge(Albert and LOSS | q dead vs q dead, longest 19:57, end r499 reason 1 | queen died r165 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 1 | odd: no-action 65; reason-4 deaths 65
1532571 live    Stripes         Sponge(Albert and LOSS | q dead vs q 3, wipe(0:16 dragons), end r120 reason 0 | queen died r108 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 1 | odd: none
1532572 live    Queen Of Spades Sponge(Albert and LOSS | q dead vs q 3, wipe(0:31 dragons), end r178 reason 0 | queen died r166 at len 3 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1532573 live    Autarky         Sponge(Albert and LOSS | q dead vs q 17, wipe(0:63 dragons), end r330 reason 0 | queen died r82 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1532574 live    Around UNSW     Sponge(Albert and LOSS | q dead vs q 4, queen length, end r499 reason 1 | queen died r319 at len 11 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: no-action 81; reason-4 deaths 81
1533048 live    Maze            Computers         LOSS | q dead vs q 78, queen length, end r499 reason 1 | queen died r209 at len 3 (wall) | splits from 10+: none; sheds to 2 from <=9: 3 | odd: no-action 74; reason-4 deaths 74
1533049 live    weakhold        Computers         WIN  | q dead vs q dead, longest 33:18, end r499 reason 1 | queen died r127 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 1 | odd: no-action 36; reason-4 deaths 36
1533050 live    Queen Of Spades Computers         LOSS | q dead vs q 13, queen length, end r499 reason 1 | queen died r111 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: no-action 1; reason-4 deaths 1
1533051 live    Slithery Fight  Computers         LOSS | q dead vs q 33, queen length, end r499 reason 1 | queen died r280 at len 4 (headon) | splits from 10+: r0 25>23 (foe at 16), r1 23>21 (foe at 11), r2 21>19 (foe at 10), r3 19>17 (foe at 11), r4 17>15 (foe at 11), r5 15>13 (foe at 10), r6 13>11 (foe at 9), r7 11>9 (foe at 10); sheds to 2 from <=9: 0 | odd: no-action 117; reason-4 deaths 117; dragon 0 still 11 rounds to r11
1533052 live    Prisoners Dilem Computers         WIN  | q 3 vs q dead, wipe(19:0 dragons), end r94 reason 0 | queen alive len 3 | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1533125 live    Devil           Team SKKU         LOSS | q dead vs q 2, wipe(0:47 dragons), end r181 reason 0 | queen died r61 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1533126 live    Prisoners Dilem Team SKKU         WIN  | q 3 vs q dead, wipe(7:0 dragons), end r62 reason 0 | queen alive len 3 | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1533127 live    Portals         Team SKKU         LOSS | q dead vs q dead, longest 42:61, end r499 reason 1 | queen died r398 at len 2 (own) | splits from 10+: none; sheds to 2 from <=9: 9 | odd: no-action 27; reason-4 deaths 27
1533128 live    Autarky         Team SKKU         WIN  | q dead vs q dead, longest 20:3, end r499 reason 1 | queen died r442 at len 62 (headon) | splits from 10+: none; sheds to 2 from <=9: 1 | odd: no-action 72; reason-4 deaths 72
1533129 live    Stripes         Team SKKU         WIN  | q 3 vs q dead, wipe(15:0 dragons), end r92 reason 0 | queen alive len 3 | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1533646 live    Islands         BambooCode        WIN  | q dead vs q dead, longest 83:12, end r499 reason 1 | queen died r244 at len 8 (headon) | splits from 10+: none; sheds to 2 from <=9: 1 | odd: no-action 82; reason-4 deaths 82
1533647 live    Maze            BambooCode        WIN  | q 77 vs q 6, queen length, end r499 reason 1 | queen alive len 77 | splits from 10+: r361 29>27 (foe at 11), r370 34>32 (foe at 11), r371 32>30 (foe at 10), r372 30>28 (foe at 9), r396 42>40 (foe at 3), r431 59>57 (foe at 4); sheds to 2 from <=9: 2 | odd: no-action 102; reason-4 deaths 102
1533648 live    Schooltime      BambooCode        WIN  | q 3 vs q 3, longest 21:13, end r499 reason 1 | queen alive len 3 | splits from 10+: none; sheds to 2 from <=9: 1 | odd: no-action 31; reason-4 deaths 31
1533649 live    Around UNSW     BambooCode        WIN  | q dead vs q dead, longest 39:23, end r499 reason 1 | queen died r184 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 1 | odd: no-action 38; reason-4 deaths 38
1533650 live    Slithery Fight  BambooCode        LOSS | q dead vs q 67, queen length, end r499 reason 1 | queen died r281 at len 15 (headon) | splits from 10+: r0 25>23 (foe at 16), r1 23>21 (foe at 11), r2 21>19 (foe at 12), r3 19>17 (foe at 12), r4 17>15 (foe at 11), r5 15>13 (foe at 10), r6 13>11 (foe at 9), r7 11>9 (foe at 10); sheds to 2 from <=9: 0 | odd: no-action 118; reason-4 deaths 118; dragon 0 still 11 rounds to r11
## one18 games: 40 (wins 17)
1535044 live    Prisoners Dilem Preyas            LOSS | q dead vs q dead, wipe(0:9 dragons), end r357 reason 0 | queen died r298 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1535045 live    Maze            Preyas            LOSS | q dead vs q dead, longest 37:55, end r499 reason 1 | queen died r102 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: no-action 94; reason-4 deaths 94
1535046 live    Default         Preyas            WIN  | q 3 vs q dead, wipe(58:0 dragons), end r205 reason 0 | queen alive len 3 | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1535047 live    Around UNSW     Preyas            LOSS | q dead vs q dead, longest 40:46, end r499 reason 1 | queen died r461 at len 15 (headon) | splits from 10+: r391 20>18 (foe at 13), r392 18>16 (foe at 14), r393 16>14 (foe at 15), r396 14>12 (foe at 16), r438 22>20 (foe at 11), r439 20>18 (foe at 10), r440 18>16 (foe at 11), r441 16>14 (foe at 12), r442 14>12 (foe at 10); sheds to 2 from <=9: 0 | odd: no-action 75; reason-4 deaths 75
1535048 live    Portals         Preyas            WIN  | q dead vs q dead, longest 26:24, end r499 reason 1 | queen died r376 at len 3 (wall) | splits from 10+: none; sheds to 2 from <=9: 5 | odd: no-action 17; reason-4 deaths 17
1535049 live    Islands         Preyas            WIN  | q dead vs q dead, longest 50:30, end r499 reason 1 | queen died r185 at len 2 (wall) | splits from 10+: none; sheds to 2 from <=9: 1 | odd: no-action 58; reason-4 deaths 58
1535050 live    weakhold        Preyas            WIN  | q dead vs q dead, longest 30:12, end r499 reason 1 | queen died r92 at len 3 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: no-action 25; reason-4 deaths 25
1535051 live    Slithery Fight  Preyas            LOSS | q dead vs q 45, queen length, end r499 reason 1 | queen died r297 at len 3 (headon) | splits from 10+: r0 25>23 (foe at 16), r1 23>21 (foe at 12), r2 21>19 (foe at 12), r3 19>17 (foe at 12), r4 17>15 (foe at 12), r5 15>13 (foe at 11), r6 13>11 (foe at 11), r7 11>9 (foe at 10), r254 10>8 (foe at 6); sheds to 2 from <=9: 1 | odd: no-action 99; reason-4 deaths 99; dragon 0 still 11 rounds to r11
1535052 live    Australia       Preyas            LOSS | q dead vs q dead, longest 24:35, end r499 reason 1 | queen died r70 at len 2 (own) | splits from 10+: none; sheds to 2 from <=9: 1 | odd: no-action 70; reason-4 deaths 70
1535053 live    Stripes         Preyas            LOSS | q dead vs q 2, wipe(0:23 dragons), end r96 reason 0 | queen died r53 at len 3 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1535538 live    Trauma          Team SKKU         WIN  | q 52 vs q 15, queen length, end r499 reason 1 | queen alive len 52 | splits from 10+: none; sheds to 2 from <=9: 0 | odd: no-action 52; reason-4 deaths 52
1535539 live    Default         Team SKKU         LOSS | q dead vs q 10, wipe(0:47 dragons), end r429 reason 0 | queen died r92 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 1 | odd: none
1535540 live    Devil           Team SKKU         WIN  | q 3 vs q dead, wipe(29:0 dragons), end r92 reason 0 | queen alive len 3 | splits from 10+: none; sheds to 2 from <=9: 1 | odd: none
1535541 live    Tower Defense   Team SKKU         LOSS | q dead vs q 11, wipe(0:24 dragons), end r448 reason 0 | queen died r206 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1535542 live    Autarky         Team SKKU         WIN  | q dead vs q dead, wipe(58:0 dragons), end r295 reason 0 | queen died r227 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1535543 live    Tower Defense   test4             LOSS | q dead vs q dead, longest 7:34, end r499 reason 1 | queen died r97 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: no-action 4; reason-4 deaths 4
1535544 live    Slithery Fight  test4             WIN  | q dead vs q dead, longest 57:32, end r499 reason 1 | queen died r312 at len 4 (own) | splits from 10+: r0 25>23 (foe at 16), r1 23>21 (foe at 16), r2 21>19 (foe at 15), r3 19>17 (foe at 15), r4 17>15 (foe at 14), r5 15>13 (foe at 11), r6 13>11 (foe at 12), r7 11>9 (foe at 11); sheds to 2 from <=9: 5 | odd: no-action 121; reason-4 deaths 121; dragon 0 still 11 rounds to r11
1535545 live    weakhold        test4             WIN  | q dead vs q dead, longest 19:8, end r499 reason 1 | queen died r320 at len 3 (wall) | splits from 10+: none; sheds to 2 from <=9: 2 | odd: no-action 18; reason-4 deaths 18
1535546 live    Stripes         test4             WIN  | q dead vs q dead, wipe(27:0 dragons), end r305 reason 0 | queen died r56 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 1 | odd: none
1535547 live    Trophy          test4             LOSS | q dead vs q dead, wipe(0:62 dragons), end r235 reason 0 | queen died r155 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1535553 live    Maze            Ballers           LOSS | q dead vs q 75, queen length, end r499 reason 1 | queen died r251 at len 2 (own) | splits from 10+: r232 15>13 (foe at 4), r233 13>11 (foe at 5), r234 11>9 (foe at 6); sheds to 2 from <=9: 7 | odd: no-action 85; reason-4 deaths 85; dragon 1 still 6 rounds to r238
1535554 live    Around UNSW     Ballers           LOSS | q dead vs q dead, longest 62:78, end r499 reason 1 | queen died r121 at len 4 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: no-action 115; reason-4 deaths 115
1535555 live    Stripes         Ballers           LOSS | q dead vs q dead, wipe(0:21 dragons), end r207 reason 0 | queen died r159 at len 3 (headon) | splits from 10+: none; sheds to 2 from <=9: 1 | odd: none
1535556 live    weakhold        Ballers           WIN  | q 4 vs q dead, wipe(36:0 dragons), end r180 reason 0 | queen alive len 4 | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1535557 live    Schooltime      Ballers           LOSS | q 3 vs q 3, longest 14:22, end r499 reason 1 | queen alive len 3 | splits from 10+: none; sheds to 2 from <=9: 1 | odd: no-action 3; reason-4 deaths 3
1535558 live    weakhold        Cybers            WIN  | q 4 vs q dead, wipe(38:0 dragons), end r195 reason 0 | queen alive len 4 | splits from 10+: none; sheds to 2 from <=9: 1 | odd: none
1535559 live    Slithery Fight  Cybers            LOSS | q dead vs q dead, longest 26:40, end r499 reason 1 | queen died r227 at len 3 (headon) | splits from 10+: r0 25>23 (foe at 16), r1 23>21 (foe at 11), r2 21>19 (foe at 10), r3 19>17 (foe at 11), r4 17>15 (foe at 12), r5 15>13 (foe at 13), r6 13>11 (foe at 14), r7 11>9 (foe at 13); sheds to 2 from <=9: 1 | odd: no-action 35; reason-4 deaths 35; dragon 1 still 11 rounds to r11
1535560 live    Schooltime      Cybers            LOSS | q 3 vs q 3, longest 43:44, end r499 reason 1 | queen alive len 3 | splits from 10+: none; sheds to 2 from <=9: 2 | odd: no-action 86; reason-4 deaths 86
1535561 live    Queen Of Spades Cybers            WIN  | q 7 vs q dead, wipe(35:0 dragons), end r246 reason 0 | queen alive len 7 | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1535562 live    Devil           Cybers            WIN  | q 3 vs q dead, wipe(52:0 dragons), end r122 reason 0 | queen alive len 3 | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1535563 live    Trauma          the uncancelables WIN  | q 46 vs q 18, queen length, end r499 reason 1 | queen alive len 46 | splits from 10+: none; sheds to 2 from <=9: 0 | odd: no-action 28; reason-4 deaths 28
1535564 live    Devil           the uncancelables LOSS | q dead vs q dead, wipe(0:59 dragons), end r260 reason 0 | queen died r260 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 1 | odd: none
1535565 live    Prisoners Dilem the uncancelables WIN  | q 2 vs q dead, wipe(16:0 dragons), end r323 reason 0 | queen alive len 2 | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1535566 live    Default         the uncancelables LOSS | q dead vs q 24, queen length, end r499 reason 1 | queen died r259 at len 3 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: no-action 8; reason-4 deaths 8
1535567 live    Tower Defense   the uncancelables LOSS | q dead vs q 3, wipe(0:9 dragons), end r84 reason 0 | queen died r69 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1536232 live    Slithery Fight  Team SKKU         LOSS | q dead vs q 18, queen length, end r499 reason 1 | queen died r170 at len 4 (headon) | splits from 10+: r0 25>23 (foe at 16), r1 23>21 (foe at 11), r2 21>19 (foe at 12), r3 19>17 (foe at 12), r4 17>15 (foe at 13), r5 15>13 (foe at 11), r6 13>11 (foe at 12), r7 11>9 (foe at 12); sheds to 2 from <=9: 0 | odd: no-action 88; reason-4 deaths 88; dragon 0 still 11 rounds to r11
1536233 live    Queen Of Spades Team SKKU         WIN  | q 3 vs q dead, wipe(25:0 dragons), end r268 reason 0 | queen alive len 3 | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
1536234 live    Islands         Team SKKU         LOSS | q dead vs q dead, total 104:119, end r499 reason 1 | queen died r175 at len 3 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: no-action 50; reason-4 deaths 50
1536235 live    Default         Team SKKU         LOSS | q dead vs q 6, wipe(0:54 dragons), end r364 reason 0 | queen died r61 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 1 | odd: none
1536236 live    Tower Defense   Team SKKU         LOSS | q dead vs q 2, wipe(0:31 dragons), end r233 reason 0 | queen died r97 at len 2 (headon) | splits from 10+: none; sheds to 2 from <=9: 0 | odd: none
## one19 games: 0 (wins 0)
## one20 games: 0 (wins 0)
## one21 games: 0 (wins 0)

## health baselines per version/set (our side)
set                n  win  qdead  timeouts  no-act  r4deaths  still>=6  collapse  splits10+  shed2from10+  shed2from<=9  medLast
one15    live       11    6      6         0     299       299         1         0         11             0             4      194
one15    one15-c1   15    5     13         0     506       506         1         0         10             0            12      499
one15    one15-p1   15    6     10         0     533       533         1         0         15             1             8      499
one15    one15-s1   15    9     11         0     584       584         1         0         10             1             5      499
one16    live        5    0      5         0     241       241         0         0          0             0             3      499
one16    one16-c1   15    3     14         0     637       637         1         0          9             1            16      499
one16    one16-p1   15    6     10         0     564       564         1         0         34             1            14      499
one17    live       30   16     20         0     934       934         2         0         28             0            23      499
one17    one17-c1   15    5     11         0     466       466         1         0         12             0            12      499
one18    live       40   17     28         0    1131      1131         5         0         45             0            33      499

## mechanism: round starts with our queen >= 10 and an enemy head within 3 (torus manhattan)
ver     games  turns  episodes | action: stay  move1  move2+  split(to2)  | dead<=3r  dead<=5r  dead<=20r | per episode: q dead within 3r of any turn
one15      56     57        23 |     0( 0%)    24(42%)    30(52%)    3(2) |    3( 5.3%)    5( 8.8%)    7(12.3%) | 2 of 23 ( 8.7%)
one16      35     25         7 |     0( 0%)     3(12%)     3(12%)   19(2) |    3(12.0%)    4(16.0%)    4(16.0%) | 2 of 7 (28.6%)
one17      45     44        22 |     0( 0%)    28(63%)    12(27%)    4(0) |    4( 9.1%)    4( 9.1%)    9(20.5%) | 2 of 22 ( 9.1%)
one18      40     11         5 |     0( 0%)     6(54%)     5(45%)    0(0) |    0( 0.0%)    0( 0.0%)    0( 0.0%) | 0 of 5 ( 0.0%)
one19       0  no such turns
one20       0  no such turns
one21       0  no such turns

## the same, enemy head within 1 or 2 only (closest spots)
one15   turns   13  shed-to-2   0  dead<=3r   0 ( 0.0%)
one16   turns   20  shed-to-2   0  dead<=3r   1 ( 5.0%)
one17   turns   12  shed-to-2   0  dead<=3r   3 (25.0%)
one18   turns    4  shed-to-2   0  dead<=3r   0 ( 0.0%)

## one17 mechanism turns, listed (game round qlen foe-dist foe-len n3 -> moved split after | +3 +5 +20)
1532059 Trauma       r423  q28  d3 L2   n1 -> mv2 - after 28  | 28 28 28
1532059 Trauma       r426  q28  d3 L2   n1 -> mv2 - after 28  | 28 28 29
1532059 Trauma       r432  q28  d3 L2   n1 -> mv5 - after 28  | 28 28 30
1532059 Trauma       r445  q29  d3 L2   n1 -> mv1 - after 29  | 30 30 30
1532059 Trauma       r446  q29  d1 L2   n1 -> mv1 - after 29  | 30 30 30
1532059 Trauma       r447  q29  d3 L2   n1 -> mv2 - after 30  | 30 30 30
1532059 Trauma       r483  q30  d3 L3   n1 -> mv1 - after 30  | 30 30 over
1532059 Trauma       r484  q30  d3 L3   n1 -> mv1 - after 30  | 30 30 over
1532059 Trauma       r485  q30  d3 L3   n1 -> mv2 - after 30  | 30 30 over
1532061 Slithery Fig r342  q11  d3 L2   n1 -> mv1 - after 11  | 11 11 11
1532061 Slithery Fig r346  q11  d3 L4   n1 -> mv1 - after 11  | 11 12 13
1532061 Slithery Fig r347  q11  d2 L2   n1 -> mv1 - after 11  | 12 12 13
1532061 Slithery Fig r358  q13  d3 L3   n1 -> mv6 - after 11  | 11 11 5
1532061 Slithery Fig r371  q13  d3 L2   n1 -> mv1 - after 14  | 10 6 dead
1532061 Slithery Fig r372  q14  d1 L2   n4 -> mv0 SPLIT after 12  | 8 4 dead
1532061 Slithery Fig r373  q12  d2 L2   n1 -> mv0 SPLIT after 10  | 6 5 dead
1532061 Slithery Fig r374  q10  d3 L2   n1 -> mv0 SPLIT after 8   | 4 6 dead
1532562 Autarky      r370  q40  d3 L3   n1 -> mv1 - after 40  | 41 42 52
1532562 Autarky      r371  q40  d1 L3   n1 -> mv1 - after 41  | 41 42 53
1532562 Autarky      r372  q41  d3 L3   n1 -> mv2 - after 41  | 42 43 54
1532562 Autarky      r499  q77  d3 L3   n1 -> mv1 - after 78  | over over over
1532574 Around UNSW  r319  q11  d3 L2   n1 -> mv1 - after 11  | dead dead dead
1533128 Autarky      r380  q45  d3 L2   n1 -> mv2 - after 46  | 46 46 52
1533128 Autarky      r416  q58  d3 L3   n1 -> mv1 - after 58  | 58 58 60
1533128 Autarky      r417  q58  d3 L3   n1 -> mv3 - after 58  | 58 58 60
1533128 Autarky      r426  q58  d3 L2   n1 -> mv2 - after 58  | 58 58 dead
1533647 Maze         r396  q42  d3 L5   n1 -> mv0 SPLIT after 40  | 40 40 54
1533647 Maze         r397  q40  d3 L5   n1 -> mv6 - after 40  | 40 41 55
1533647 Maze         r416  q54  d3 L3   n1 -> mv3 - after 55  | 56 57 60
1533647 Maze         r425  q58  d3 L2   n2 -> mv1 - after 59  | 59 59 65
1533647 Maze         r428  q59  d2 L3   n1 -> mv1 - after 59  | 59 57 66
1533647 Maze         r429  q59  d2 L3   n1 -> mv1 - after 59  | 57 59 66
1533647 Maze         r430  q59  d2 L3   n1 -> mv1 - after 59  | 57 60 67
1533647 Maze         r432  q57  d3 L3   n1 -> mv1 - after 57  | 60 61 68
1533647 Maze         r481  q77  d3 L2   n1 -> mv1 - after 77  | 77 77 over
1533647 Maze         r482  q77  d3 L2   n1 -> mv1 - after 77  | 77 77 over
1533647 Maze         r483  q77  d3 L2   n1 -> mv1 - after 77  | 77 77 over
1533647 Maze         r488  q77  d3 L2   n1 -> mv1 - after 77  | 77 77 over
1533647 Maze         r489  q77  d3 L3   n1 -> mv1 - after 77  | 77 77 over
1533647 Maze         r493  q77  d2 L4   n1 -> mv1 - after 77  | 77 77 over
1533647 Maze         r497  q77  d3 L7   n1 -> mv1 - after 77  | over over over
1533650 Slithery Fig r279  q15  d2 L3   n1 -> mv1 - after 15  | dead dead dead
1533650 Slithery Fig r280  q15  d2 L3   n1 -> mv1 - after 15  | dead dead dead
1533650 Slithery Fig r281  q15  d2 L3   n1 -> mv1 - after 15  | dead dead dead
1535047 Around UNSW  r369  q16  d3 L17  n1 -> mv4 - after 16  | 16 17 20
1535047 Around UNSW  r437  q22  d1 L10  n1 -> mv1 - after 22  | 18 14 14
1535538 Trauma       r413  q33  d2 L2   n1 -> mv2 - after 33  | 33 33 36
1535538 Trauma       r414  q33  d3 L2   n1 -> mv2 - after 33  | 33 33 36
1535538 Trauma       r415  q33  d2 L2   n1 -> mv1 - after 33  | 33 34 36
1535538 Trauma       r416  q33  d2 L2   n1 -> mv1 - after 33  | 33 34 37
1535553 Maze         r228  q12  d3 L2   n2 -> mv1 - after 12  | 13 13 2
1535553 Maze         r229  q12  d3 L2   n1 -> mv1 - after 12  | 15 11 3
1535553 Maze         r230  q12  d3 L2   n1 -> mv1 - after 13  | 13 9 4
1535553 Maze         r231  q13  d3 L2   n1 -> mv2 - after 15  | 11 7 2
1535563 Trauma       r378  q31  d3 L14  n1 -> mv2 - after 31  | 33 33 36

## sheds from 10+ to 2 in one15/one16 (what one17 removes)
1525842 one15 Trauma       r430 19>2 foe at 3; queen died r431; LOSS
1527409 one15 Trauma       r424 29>2 foe at 3; queen died r486; LOSS
1528868 one16 Slithery Fig r363 19>2 foe at 3; queen died r476; LOSS
1530575 one16 Trauma       r340 11>2 foe at 3; queen died r341; LOSS

set                 n win | queen deaths by reason                       | q death len>=10 | wiped(us) wiped(them) | med q death round | q split-by-2 from 10+ after r50
one15    live       11   6 | {'headon': 5, 'wall': 1}                     |               1 |         2           5 |                86 | 3
one15    one15-c1   15   5 | {'headon': 11, 'own': 1, 'wall': 1}          |               1 |         5           2 |               137 | 2
one15    one15-p1   15   6 | {'headon': 8, 'wall': 1, 'own': 1}           |               0 |         3           3 |               133 | 6
one15    one15-s1   15   9 | {'wall': 2, 'headon': 8, 'body': 1}          |               0 |         2           5 |               152 | 1
one16    live        5   0 | {'own': 1, 'wall': 1, 'headon': 3}           |               0 |         1           0 |               156 | 0
one16    one16-c1   15   3 | {'wall': 1, 'headon': 11, 'own': 2}          |               1 |         5           1 |               144 | 0
one16    one16-p1   15   6 | {'wall': 3, 'headon': 7}                     |               0 |         3           3 |               180 | 25
one17    live       30  16 | {'headon': 18, 'wall': 1, 'own': 1}          |               3 |         6           9 |               165 | 12
one17    one17-c1   15   5 | {'headon': 9, 'body': 1, 'wall': 1}          |               0 |         4           2 |               139 | 4
one18    live       40  17 | {'headon': 22, 'wall': 3, 'own': 3}          |               1 |        10          10 |               175 | 13

## same map, opponent set c1: result / queen (dNNN = died round NNN at len, aNN = alive len) / last round
Around UNSW      W d254@2 eqdead r499         | L d168@4 eqdead r499         | W d136@4 eqdead r499        
Australia        L d127@4 eqdead r499         | L d280@4 eqdead r499         | L d158@4 eq13 r499          
Default          L d230@2 eqdead r271 wipe    | L d128@3 eqdead r279 wipe    | L d147@2 eqdead r449 wipe   
Devil            W d87@3 eqdead r99 wipe      | L d134@3 eqdead r204 wipe    | W d21@4 eqdead r111 wipe    
Islands          L d222@3 eqdead r499         | W d172@3 eqdead r499         | L d139@3 eqdead r499        
Maze             L d101@2 eqdead r499         | L d144@2 eq66 r499           | L d216@3 eq25 r499          
Portals          W d212@2 eqdead r499         | W d193@3 eqdead r499         | W a3 eqdead r499            
Queen Of Spades  L d136@4 eq6 r338 wipe       | W d62@2 eqdead r426 wipe     | W a2 eqdead r265 wipe       
Schooltime       W a3 eq3 r499                | L a3 eq3 r499                | W a3 eq3 r499               
Slithery Fight   L d391@44 eqdead r499        | L d476@2 eqdead r499         | L d380@4 eqdead r499        
Stripes          L d47@3 eqdead r122 wipe     | L d87@2 eqdead r205 wipe     | L d42@2 eqdead r121 wipe    
Tower Defense    L d112@3 eqdead r112 wipe    | L d129@2 eq3 r129 wipe       | L d73@3 eq4 r73 wipe        
Trauma           L a35 eq39 r499              | L d390@33 eq48 r499          | L a30 eq33 r499             
Trophy           L d137@3 eqdead r154 wipe    | L d48@2 eqdead r205 wipe     | L d172@3 eqdead r172 wipe   
weakhold         W d201@3 eqdead r265 wipe    | L d129@2 eq4 r499            | L d99@2 eq4 r499            

## same map, opponent set s1: result / queen (dNNN = died round NNN at len, aNN = alive len) / last round
Around UNSW      W d146@4 eqdead r499         | -                            | -                           
Australia        L d293@2 eqdead r499         | -                            | -                           
Default          W d199@2 eqdead r308 wipe    | -                            | -                           
Devil            W a3 eqdead r154 wipe        | -                            | -                           
Islands          W d87@4 eqdead r499          | -                            | -                           
Maze             L d152@2 eq6 r499            | -                            | -                           
Portals          L d10@3 eq6 r499             | -                            | -                           
Queen Of Spades  W a3 eqdead r213 wipe        | -                            | -                           
Schooltime       W d433@4 eqdead r499         | -                            | -                           
Slithery Fight   L d256@6 eqdead r499         | -                            | -                           
Stripes          L d57@2 eqdead r253 wipe     | -                            | -                           
Tower Defense    W a3 eqdead r220 wipe        | -                            | -                           
Trauma           L d486@8 eq26 r486 wipe      | -                            | -                           
Trophy           W a3 eqdead r47 wipe         | -                            | -                           
weakhold         W d87@2 eqdead r499          | -                            | -                           

## same map, opponent set p1: result / queen (dNNN = died round NNN at len, aNN = alive len) / last round
Around UNSW      L d133@3 eqdead r499         | W d183@2 eqdead r499         | -                           
Australia        L d171@3 eqdead r499         | L d134@2 eqdead r499         | -                           
Default          W a4 eqdead r259 wipe        | W a3 eqdead r152 wipe        | -                           
Devil            W d38@3 eqdead r128 wipe     | W a3 eqdead r168 wipe        | -                           
Islands          W d155@2 eqdead r499         | W d249@2 eqdead r499         | -                           
Maze             W a86 eq2 r499               | L d187@2 eqdead r499         | -                           
Portals          L d288@3 eqdead r499         | W d105@3 eqdead r499         | -                           
Queen Of Spades  L d33@3 eqdead r304 wipe     | L d82@3 eq2 r306 wipe        | -                           
Schooltime       W a3 eq3 r499                | L a3 eq3 r499                | -                           
Slithery Fight   L a14 eq44 r499              | L a23 eq31 r499              | -                           
Stripes          L d79@3 eq3 r103 wipe        | L d90@2 eq2 r90 wipe         | -                           
Tower Defense    L d94@3 eq2 r94 wipe         | L d172@3 eq10 r363 wipe      | -                           
Trauma           L d431@2 eq38 r499           | L d341@2 eq27 r499           | -                           
Trophy           W a3 eqdead r101 wipe        | W a4 eqdead r124 wipe        | -                           
weakhold         L d84@2 eqdead r499          | L d180@3 eqdead r499         | -                           
```
