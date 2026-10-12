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
