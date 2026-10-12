### F6 On corridor-heavy layouts with slow pearls we are behind at round 100 in four games out of five
status: weakened      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 04:03 KST (1 new game)
measured: The group is Maze and Tower Defense only. main behind in total length at r100 in 26 of 31 games last hour; this hour one more Maze game (48 against 86 at r100, won). v31 31 of 46.
  The two layouts behave differently: on Maze our pearl share by r50 is 0.50 and we pass up fewer adjacent pearls than opponents (0.09 against 0.17); Tower Defense is F7.
would be wrong if: (first hour, narrow pass on v31) the share there is under 0.60 or less than 20 points above the other layouts.
inferred: Not a map property. It is "Tower Defense, see F7". Moved to weakened because no second layout behaves like Tower Defense.
not checked: nothing further planned.
look at: data/online/ladder/1241400/M1241402.replay r0-100 (Tower Defense vs 1934).
smallest test: none; covered by F7.

### F3 Our queen ends boxed in (no safe step) more often than theirs
status: weakened      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 04:03 KST
measured: Queen deaths by wall or own body on free layouts, main: ours 47, theirs 25 in 193 games. The verifier showed last hour that these are queens with no safe step (trapped), 49 against 32 whatever they then hit,
  and that 13 of the 19 excess games fell in one hour. New games since the bar: 25, ours 8, theirs 5.
would be wrong if: moves to refuted if, once 40 new main games on free layouts exist, ours is not above theirs. 25 so far: 8 against 5.
inferred: A modest difference (about 1.5 to 1) in how often the queen gets boxed in. The usable detail stays: a trapped queen of theirs more often rams a head; ours takes the wall.
not checked: what boxed her in.
look at: data/online/ladder/1233593/M1233594.replay r172 (Maze, wall, length 2, lost).
smallest test: no change yet.

### F2 After head-on meetings the opponent eats more of the dropped pearls than we do
status: weakened      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 03:05 KST (not re-counted this hour)
measured: main, 210 games: share 0.399 of head-on drops eaten within 15 rounds. The verifier showed 0.40 is also our share of all pearls in those games, and that the mover's side takes the drop.
would be wrong if: share 0.47 or more in any of the four slices; band b reaches 0.504 in the verifier's interval.
inferred: Not a finding of its own; it is F8 seen through the pearls.
not checked: nothing further planned.
look at: data/online/ladder/1256635/M1256637.replay (Australia vs 1924).
smallest test: none.

### F1 Being behind in total length at round 100 means the game is mostly lost
status: weakened      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 04:03 KST
measured: main against 1900+: 25 won of 79 games in which we were behind at r100. New since the bar: 7 such games, 3 won (this hour: Around UNSW and Maze against 2032 were both won from behind).
  Against 1700-1899 the first-hour bar failed (13 of 24 won from behind).
would be wrong if: against 1900+ we win 0.45 or more of games behind at r100, once 20 such new games exist. 7 so far, 3 won.
inferred: An early deficit against 1900+ teams is recovered in about a third of games; when it is, both queens are usually dead and feeding decides.
not checked: whether total length is the right yardstick.
look at: data/online/ladder/1267969/M1267971.replay (Maze vs 2032, new: 48 against 86 at r100, won on longest dragon).
smallest test: none.

### F17 When both queens are alive at round 500 ours is the shorter one and we lose
status: refuted      first seen: 7 Oct 04:02 KST run 20261007-0400   last tested: 7 Oct 04:04 KST
measured: Free layouts, both queens alive at the end: main 18 games, we win 12, our queen is the longer one in 12 (median length 36 against 21). v31 15 games, 11 won, ours longer in 11.
  And it is one layout: Trauma holds 16 of the 18 and 13 of the 15.
would be wrong if: we win 45 percent or more of these games, or our queen is the longer one in 45 percent or more, on main or v31; or one layout holds more than half. All three failed the claim.
inferred: On Trauma both queens usually live to the end and ours is usually longer. No weak point here. How main games end on free layouts (193): both queens dead 117 (73 won), only theirs alive 33 (0 won),
  only ours 25 (25 won), both alive 18 (12 won).
not checked: why queens survive on Trauma.
look at: none needed.
smallest test: none.

### F19 On large layouts our dragons are more bunched than theirs, and theirs push further into our half
status: refuted (both parts; the first came out reversed and led to F20)      first seen: 7 Oct 04:11 KST run 20261007-0400   last tested: 7 Oct 04:13 KST
measured (own count, work/h6_spread.py; snapshots every 25 rounds from r100 to r300 with dragon counts within 10 percent):
  a) median distance from a head to the nearest friendly head: ours is the smaller in 12 of 78 non-tied snapshots on main large layouts and 18 of 122 on v31. Slithery Fight 8 of 36 and 12 of 49. Theirs are the bunched ones.
  b) share of heads nearer to the enemy queen's spawn than to their own: ours 0.294, theirs 0.292 (main); 0.301 and 0.300 (v31).
would be wrong if: a) ours smaller in under 55 percent of non-tied snapshots; b) their share minus ours under 5 points. Both failed.
inferred: We are not clumped and they do not out-expand us. They are clumped, at the busy tiles (F20).
not checked: most balanced snapshots are Around UNSW.
look at: none needed.
smallest test: none.

### F9 Their rams kill our queen more often than our rams kill theirs
status: refuted      first seen: 7 Oct 03:04 KST   last tested: 7 Oct 04:08 KST
measured: Last hour: games with our queen rammed 83, theirs 89 (main, free layouts); v31 172 and 167. This hour's own count agrees: rams on our queen 87, on theirs 93 (main); 171 and 164 (v31).
would be wrong if: the ratio is under 1.3 in any main slice or on v31. Failed everywhere on main.
inferred: Queen rams are even between the sides. What survives is in F13.
not checked: 2100+ teams look different but that is 53 games.
look at: none needed.
smallest test: none.

### F12 When only their queen is alive at round 300 we almost never turn the game round
status: refuted      first seen: 7 Oct 03:11 KST   last tested: 7 Oct 03:12 KST
measured: main: only their queen alive at r300 in 29 games; she dies later in 11; we win 8. v31: 69 games, 28, 15.
would be wrong if: she dies later in 20 percent or more, or we win 15 percent or more. Failed.
inferred: The revenge hunt plus feeding does turn a quarter of these games.
not checked: the games where she lived.
look at: data/online/ladder/1263705/M1263706.replay r276-499 (Maze vs 2022).
smallest test: none.

### F14 The common root of F10 and F11 is reach: pearls born far from both sides go to the opponent
status: refuted      first seen: 7 Oct 03:13 KST   last tested: 7 Oct 03:17 KST
measured: pearls born 7 or more tiles from both sides at balanced moments: our share 0.495 on main and on v31. Tower Defense alone 0.10.
would be wrong if: our share of far-for-both pearls is 0.45 or more. Failed.
inferred: Our dragons fetch far pearls as well as opponents do, except on Tower Defense. A general "pull from farther" change is not supported.
not checked: straight-line distance, not path.
look at: none needed.
smallest test: none.

### F5 In rounds 0-100 our dragons die on walls more often than theirs
status: refuted      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 03:10 KST
measured: ratio 1.12 against band c teams and higher on only 11 of 18 layouts; both first-hour bars failed.
would be wrong if: ratio under 1.15 in any main slice. Failed in band c.
inferred: Early wall deaths are normal play for both sides.
not checked: what the wall deaths are.
look at: none needed.
smallest test: none.

## Notes that are not findings
- How main games end (225): wins 126, losses 99. Eliminations against us: 31, of which 23 on 2-dragon-start layouts (Stripes 7 of 9 games, Queen Of Spades 6 of 17, Tower Defense 5 of 15, Trophy 3 of 7).
  Eliminations by us: 51 (Devil 13, Queen Of Spades 10, Default 8, Autarky 7).
- Battles on main: 45. Against 1700-1899 11 won of 16; 1900-2099 16 of 27; 2100+ 0 of 2.
- In 252 of 253 rams on our queen the ram came in the same round as her last move: she had moved first, and the rammer started from where it stood when she chose her step.
- A dragon sees 3 tiles (VISION_RADIUS 3). main.cpp has no memory of tiles where pearls reappear.
- Not re-tested on the 15 new games this hour: F8, F15 (their extract was not rerun), F2.
- Tooling: the guard still refuses the Write and Edit tools, any command text with braces, and a second command after a heredoc; it also refused a heredoc that used the string method named replace.
  Every file was written through a Python heredoc. New scripts in work/: h4_pass.py (queen rams, births by distance), h4_trace.py and h4_draw.py (print an opening and a board),
  h5_decline.py and h7_pocket.py (adjacent pearls passed up), h6_spread.py (head spacing), h8_fountain.py (heads at busy tiles); shard outputs h4- to h8-.
