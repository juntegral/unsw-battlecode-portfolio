## 4. The kinds of death, game by game

Board legend: `@` queen of side A, `&` queen of side B, `A` / `B` other heads, `a` / `b` bodies, `*` pearl, `|` and `-` kelp, `O` portal. Rows are y (south is down), columns x. Every board shows the start of the queen's own turn. "#124" is a dragon id. Game numbers refer to the table in section 3.

### 4.1 Rammed after stepping into reach (66 games; games 1 to 7)

**What the board shows.** The killer is in her view, she is outside its reach, at least one step keeps her outside, and she takes a step that does not. The killer is 3 or shorter in 52 of the 66 and never longer than 4. Its ramming move has 2 or more steps in 48 of the 66 (1 / 2 / 3 / 4 / 5 steps: 18 / 23 / 16 / 8 / 1). She ate a pearl on the fatal step in 1 of the 66, so this is not pearl greed. In 56 of the 66 a roomy safe step existed.

**Game 1 (980372, Around UNSW, ladder 3 Oct).** Our queen splits 4 into 2+2 at round 1 and eats nothing in 94 rounds. From round 87 she walks a 2x2 loop: (24,42), (24,43), (25,43), (25,42). An enemy 3-long, #124, comes up from the south-east; it is in her view at round 89 and again from round 92. Round 92: she is at (24,43), it is at (24,46); she steps east (safe). Round 93: it is at (24,45); she steps north (safe). Round 94:

```
     22232425262728
 39   a . . . . . .
 40  |. . . . . . .
     +-+
 41   .|. . . . . .
 42   .|. . @ . . .
 43   .|. . a . . .
     +-+
 44   .|. B . . . .
 45   .|. b . . . .
```

North (25,41) and east (26,42) are 4 steps from #124's head; west (24,42) is 2 steps from it, and a 3-long reaches 2. She steps west, the next cell of her loop. #124 moves `NN` and rams her. Inference from the code: the cell (24,42) costs her 337 points of threat penalty (450 x 0.5 for a 2-long x 1.5 for depth 2), which the other terms of the step score outweighed. Another enemy, #148, had been in her view at rounds 90 and 91 to the north-east; our queen keeps such sightings for three rounds and spreads a growing penalty from them, which may have put the same 337 points on the two safe cells. The replay cannot show that.

**Game 2 (1053773, Australia, ladder).** By round 50 she is 31 path steps from her start with no own head within 4 cells. Two WHQ dragons (a 2-long and a 3-long) keep 3 steps behind her from round 60 to round 74. She walks east along a kelp wall into a corner cell (29,39) whose exits are south, inside the 3-long's reach, and west through a portal. The portal step was safe; our queen rule forbids portal steps, and she steps south. This is the one game of the 66 in which the only roomy safe step was a portal.

**Game 3 (1045200, Devil, ladder, rules off).** She walks east along row 7 to the middle of the map, eats two pearls, splits twice, turns into the centre lane and at round 18 steps from (14,4) to (15,4), the cell next to the head of an enemy 2-long at (16,4). North and south were free and safe. Four of our Devil games end exactly like this at round 18 (section 5d). test4's queen in the same game splits once at round 0 and then walks the loop N, E, S, W on four cells at her start for the whole game; none of our heads ever comes into her view.

**Games 4 and 5 (1053020 Islands, 1044202 Default).** In game 4 she is 24 path steps from her start, has had an enemy head in view in 20 of her last 21 rounds, and has eaten no natural pearl since round 50. In game 5 she has eaten nothing in 149 rounds, has had an enemy head in view in 15 to 17 of every 25 rounds since round 75, and has 0.1 to 0.3 own heads within 4 cells. Five enemy heads stand within 5 cells of her at round 149. She steps north toward a pearl two cells away; a 4-long reaches her there in 4 steps by going round a portal edge and over that pearl (`WSES`). South was out of reach.

**Game 6 (1052762, Queen Of Spades).** From round 25 to round 247 she has an enemy head in view in three rounds out of four (12 to 24 of every 25 rounds) and lives, so she does dodge most of the time. At round 247 she steps east into the reach of a 3-long that needs 4 steps and a pearl on the way.

**Game 7 (1063018, Queen Of Spades, qh31-old).** A fed queen, 17 long, at round 417. Her safe step leads into a pocket of 7 cells, too small for 17 segments; the other step is inside a 3-long's reach. She takes that one and dies. This is not avoidable on the last turn; 10 of the 66 are of this "safe step into a pocket" sort.

**The opponent's queen, and the top three.** Our opponents' queens die this way in 15 of 401 games, the top three in 59 of 1,637 (3 to 4% each). In the top three's 74,030 turns that began outside reach with a safe step, they ended in reach in 138 (0.19%); ours in 81 of 10,705 (0.76%). SSS's queen from our Devil start (T17, T18) dies at rounds 17 and 18 too: Devil is deadly for every queen that walks to the middle (dead before round 50: top three 61 of 114 games, ours 23 of 30).

### 4.2 Rammed after staying in reach (38 games; games 8 to 12)

**What the board shows.** She begins the turn inside a visible enemy's reach, a safe step exists, and she ends in reach again. Here pearls do matter: she ate on the fatal step in 17 of the 38, and ended next to an enemy head in 18.

**Game 8 (1023823, Australia, against forgot).** She is 36 path steps from her start at round 75 (the enemy's start is 40 away) with no own head near. Round 81:

```
     10111213141516
 47   . . . . . . .
 48   . B * @ . . .
 49  O. b . a . . .
 50   . b . . . . B
```

A pearl lies between her head (13,48) and the head of forgot's 3-long #52 at (11,48). East (14,48) is safe. She steps west onto the pearl and #52 rams her with one step. Inference from the code: a pearl on the next cell is worth 300 (`EAT_BONUS`) plus up to 440 (target bonus) to her; the threat penalty of the cell next to a 3-long's head is 450 for a 2-long queen.

**Games 9 and 10 (1045382 Queen Of Spades round 36, 1052754 weakhold round 80).** The same picture: a pearl one step away, inside the reach of a 2-long and a 3-long; she eats it and is rammed.

**Game 11 (1045377, Maze).** At round 196 she is 4 long and splits into 2+2 while a 5-long is in her view (3 cells away, 9 steps by path). At round 197 it has grown to 6 and can reach the pearl west of her in 6 steps; east is safe. She takes the pearl. It rams her with `NNENES`.

**Game 12 (1044201, Around UNSW).** She stays 8 to 9 cells from her start all game. test4 has 62 dragons against our 34 at round 75 and they are in her home. At round 85 a 5-long is 3 cells away; her one safe step is a one-cell dead end. She is in effect cornered; 2 of the 38 are like this.

**The top three.** Inside reach with a safe step, their queens end in reach again in 9% of such turns (173 of 1,837), ours in 19% (68 of 358).

### 4.3 Rammed when cornered (114 games; games 13 to 18)

**What the board shows.** The killer is in view and no one-step move ends outside reach. She had exactly one free step in 56 of the 114 (in 38 of those she began outside reach and her only step led into it), two in 39, three in 16, none in 3. The killer is 3 or shorter in 84. The top three have the same shape (one free step in 255 of 476).

**Game 14 (1044510, Australia): herded along a wall.** A WHQ 2-long, #5, is on the diagonal behind her from round 59. She walks west along a kelp wall; each round her step west is safe and her step south is next to its head; it follows one cell behind on the open side. Round 62:

```
     17181920212223
 11   . . . . . . .
     + + + +-+-+-+-
 12   . . .|@ a . .
     +-+-+-+
 13  |. . . . B b .
```

The wall turns. Her only free cell is (20,13), next to #5's head at (21,13). One 2-long with a reach of 1 was enough, because the wall took her other exits four rounds earlier.

**Game 17 (1053778, Around UNSW).** The same with a wall on one side and one enemy 2-long on the forward diagonal: both her free cells are next to its head.

**Game 13 (1052760, Around UNSW).** At round 43 she steps east toward a group of seven test4 heads she cannot see yet (the nearest is 5 cells away). At round 44 a 5-long is in view 3 steps away and every cell she can step to is inside its reach of 5.

**Game 15 (1053021, Maze).** After building the economy for 40 rounds near her start she crosses the maze westward for 30 rounds, to more than 21 steps from her start with 0.3 own heads near. Three WHQ 3-longs are within 2 to 3 cells when she walks north into a corridor with one way on.

**Game 18 (1027975, Islands).** A queen that did stay home: she farms the pearls at her start for 100 rounds (4 to 5 pearls and 2 to 3 splits per 25 rounds, never more than 7 cells away). At round 187 WHQ dragons arrive there; she steps into a two-exit nook and the second exit is next to an enemy head.

**Game 16 (1052761, Default).** Our team has 2 dragons against 52. Not a queen problem.

**How the corner is made.** Three turns before the ram the later killer was in her view in only 34% of our rammed deaths (top three: 32%); one turn before, in 60%. So most corners close within two turns. What differs between teams is not how often a queen is cornered once an enemy is near (section 5b), but how often an enemy is near.

### 4.4 Rammed by an enemy she could not see (31 games; games 19 to 22)

**What the board shows.** In 28 of the 31 the killer began its ramming move 3 cells (Chebyshev) from the cell she died on: it stood just outside her 7x7 view, 4 cells from her, and her own step brought her inside its range. The killer is 5 or longer in 13, or a 3- or 4-long that ate a pearl on the way. Nothing on her screen warned her: its head had not been in her view in any of her last three turns in all 31.

**Games 20 and 22 (1052766 Trauma, 1045388 Slithery Fight): fed queens that outrun their eyes.** Our queen is fed from round 300 and by round 445 is 34 long (game 20) or 48 long at round 356 (game 22). She then takes six steps every turn (`WNNNWW`, `NENNEE`), all free at that length. In game 20 her sixth step ends next to the head of a test4 2-long that was 4 cells from her when the turn began; in game 22 an 8-long that was 6 cells away rams her with 4 steps. Eight of our 16 rammed queens of 6 or more died right after a move of 3 or more steps.

**Game 19 (1045195, Around UNSW).** At round 53 she is 4 long and splits into 2+2 with a test4 2-long 3 steps away in her view; at round 54 she steps west and a 3-long from 4 cells away rams her in 3 steps over a pearl.

**The top three.** They die this way at our rate (0.49 against 0.55 per 1,000 queen-rounds). It is the price of any queen that moves, and the one kind in which we are not worse.

### 4.5 Boxed in by her own team (58 games; games 23 to 29)

The 58 are four different things: 13 queens that had cut themselves short and died inside the child (a 14th died against an enemy body, game 29), 11 with their own recent split child on the last exit, 20 nose to nose with a team-mate's head, and 14 with another team-mate's body on the last exit.

**a. Cut and stuck (14 games; games 23, 26, 28, 29).** Game 23 (1053032, Slithery Fight) at round 0:

```
      0 1 2 3 4 5 6            round 3:   1 2 3 4 5 6 7
 20  |. a a a a a .                  20   a a a a a . .
 21  |. a a a a a .                  21   a a A @ a . .
 22  |. a a @ a a .                  22   a . . a a . .
 23  |. a a a a a .                  23   a A . . a . .
 24  |. a a a a a .                  24   a a . a a . .
```

Every queen starts this map 25 long, coiled, with no free cell. Ours gives one order: split so that she keeps 2 and the child gets 23. The child's 23 segments are the coil around her. She steps east, north, and at round 3 has the child's body on two sides and a new 2-long's head on the third. She dies there in 10 of our 29 Slithery Fight games; in the other 19 she gets out, 2 long. From the same start cell SSS (T15) and forgot (T16) shed 2 from the tail eleven rounds in a row (25, 23, 21, ... 5, 3), make eleven 2-longs, lose nothing, and walk out 3 long at round 11.

The same order kills fed queens late. Game 29 (990346, Slithery Fight): our queen is 57 long at round 385, walks into a pocket closed by an enemy 17-long's body, cuts 57 into 2+55 and dies at round 386. Team SKKU's queen ends the game 3 long: with our queen alive at any length this is a queen-rule win. Game 26 (1044207, Trauma) at round 457:

```
     40414243444546
 19   . . a a . . .
 20   a a a a . . .
 21   a a a a a a a
 22   a a a @ a a a
 23   a a a a a a .
```

She is 32 long, has been taking six steps a turn inside her own home for 30 rounds, and has wound herself in: all four sides are her own body (segments 23, 25, 1 and 15). She cuts 32 into 2+30 and dies inside the child at round 458. test4's queen ends 36 long. Shedding 2 from the tail would have opened the first of those cells after four rounds, at length 24. Game 28 (1045196, Default): the same at 15 long, round 347.

**b. Her own split child on her exit (11 games; game 24).** Game 24 (1045387, Portals, rules off) at round 9:

```
      1 2 3 4 5 6 7
     + + + +-+-+ +
  4   . . b b & . .
  5   . . . . . . .
     + + + +-+-+ +
  6   . . .|a a|. .
     + + +O+O+ + +
  7   . . .|@ a|. .
     + + + +-+-+ +
  8   . . . . . . .
```

At round 4 she steps through a portal from (28,9) into a kelp room of four cells with a pearl on each. The room lies in the enemy's area (WHQ's queen `&` is two cells north of it) but opens only through that portal. At round 5, 4 long, she splits; the child is born on the far side of the portal, in our home. She eats the other three pearls and is 5 long in a room of 4 cells at round 9. The only way out of (4,7) is north through the portal edge to (28,8), which she cannot see. Her child, which wandered north on the far side, has its tail on (28,8). She steps onto it. Seven games end at this cell at round 9 and four at the mirrored cell at rounds 9 and 10.

On this map the two homes are not connected at all (from a start cell 240 of the 512 cells can be reached with portals and the enemy's start is not among them; `d_conn.py`), so no hunter can reach a queen: ours is dead in 27 of 27 games, never by a ram; the top three's is alive at the end in 52 of 106. SSS's queen from the same start (T12, T13) does not take the portal, eats no natural pearl in the whole game and does not split before round 100. In T12 she walks to a spot 20 to 25 steps from her start and stays there on 4 to 16 cells per 25 rounds from round 50 to round 300, with 1 to 3 own heads within 4 cells, and is fed to 29 at the end. forgot's queen (T14) sits 1 to 5 cells from her start from round 50 to round 150 with 4 to 5 own heads within 4 cells, eats nothing, and is fed from round 200.

**c. Nose to nose (20 games; games 25, 27).** Game 25 (1045380, Around UNSW) at round 96:

```
     1112131415
 26   . . a . .
 27   . . A . .
     + + + +-+
 28   . a @|. .
     + + +-+
```

At round 95 she steps east into (13,28), a cell with one way on, north. Our 2-long #29 then steps south onto (13,27). At round 96 she has kelp east and south, her own tail west and #29's head north. She dies; #29 eats her pearl. In 12 of the 20 the space around her was open until the last turn. The top three have this too (forgot 8 games of 632, SSS 8 of 503, Vibing++ 34 of 502; ours 20 of 401).

### 4.6 Boxed in a terrain dead end (30 games; games 30 to 33)

**Game 30 (1023828, Maze, against forgot, rules on)** at round 95:

```
     27282930313233
  0   . . a * * . .
     + + + +-+-+-+-
  1  |a A|a @ . * .
     +-+-+-+ +-+-+O
  2   a . .|*|*O.|.
  3  |A . .|* *|*O.
     + + + +-+-+-+
```

East (31,1) is open water. South (30,2) is the mouth of a one-wide corridor with a pearl on every cell: (30,2), (30,3), (31,3), (31,2), then a portal to five more cells that end at a wall. She steps south. From here every turn has one free step, most of them with a pearl on it. She eats seven pearls, splits twice on the way (the children walk back out), reaches the last cell 6 long at round 105, cuts 6 into 2+4 at round 106 and dies at round 107. For any other dragon of ours this is a good trade: seven pearls come out and a 2-long is lost. For the queen it is her life for seven pearls.

**Games 31 to 33 (Portals, Slithery Fight, Prisoners Dilemma).** The same walk: a portal step onto a pearl in a one-cell nook (31, rules off), a corridor of pearls with a 3-long two cells behind her (32), a corridor of three pearls (33). In all four she split or cut inside.

**Counts.** On the turn she entered, she stepped onto a pearl in 16 of the 30 and a roomier free side existed in 21. She ate inside in 26 and split inside in 18. 21 of the 30 are on maps of 600 cells or fewer. The top three die this way at a third of our rate.

### 4.7 She rams an enemy head herself (19 games; games 34 to 36)

In 9 of the 19 she was boxed in and the enemy head was her only side that was not kelp or a body (games 35 and 36: a one-wide corridor with an enemy 2-long coming the other way; kelp, a team-mate's body and an enemy head). In the other 10 she had a free safe cell and chose the ram; all 10 are on maps of 600 cells or fewer, where she is an ordinary small dragon that trades on contact. Game 34 (1053777, Tower Defense): our team has 4 dragons against 33, a WHQ 2-long has followed her through her home room for two rounds, north and west are free and safe, and she steps east into its head. The head she takes with her is 2 or 3 long in all 19. SSS's queen never does this with a free cell (9 own rams, all boxed in).

### 4.8 The 39 queens that lived (games 37 to 40)

Fifteen are on Trauma, where the two homes are separated by portals (the path between the starts is 98 steps); 14 on Trophy, 4 on Default, 3 on Prisoners Dilemma and 1 each on Autarky, Devil and Queen Of Spades, all 24 of them games we won by wipe-out. In game 37 (Trauma) no enemy head came within 8 path steps of her in 500 rounds and she won the game 26 to 25 on queen length. In game 39 (Trophy) the enemy had 5 dragons at round 50 and 1 at round 150. In game 40 (Default) she had an enemy head in view in 52 of the rounds 25 to 100, the nearest one step away, and lived; we won the fight around her. So our queen lives where no hunter comes, or where the hunters die first. Of the 39 games, 24 are wipe-out wins, 4 are round-500 wins and 11 are round-500 losses on Trauma with her queen alive and longer.
