# Do our dragons waste the opening by not sweeping the board?

1. Verdict on the claim: no. Our dither is the higher one on 12 of 19 layouts and against all three rating bands, but by 3 points (16.3% against 13.2% of blind moved turns), not 45 against 12; and inside a layout our low-dither games eat less, not more (105 pearls by r100 against 125; correlation +0.17, still +0.10 with our dragon count held).
2. The change: no card. Neither a keep-moving rule nor a hot-tile rule. Their hot-tile share is higher on 15 of 19 layouts and tracks pearls inside a layout, but it is the eating counted a second time, and main.cpp already has a hot-tile rule.
3. How sure: fairly sure of the no on sweeping (500 games; the sign is wrong in five cuts, and we already see more of the board than they do on 14 of 19 layouts). Less sure on hot tiles: the dossier measure cannot tell standing by a tile from eating there, and I opened no replay.

Scope: the dossier only (500 main games, 19 layouts, 1000 game-side rows), sliced by three scratch scripts in dossier/work/ (sw_slice.py, sw_crowd.py, sw_maps.py); nothing recounted from replays. Blind turn = a turn that starts with no pearl in the 7 by 7 view; dither = a blind step onto one of the dragon's own last 12 tiles; hot = a turn that starts on or beside a tile where a pearl has already appeared twice. All r0-100 unless said. TD = Tower Defense, PD = Prisoners Dilemma.

## Evidence (all measured)

| What | Ours | Theirs | Where |
|---|---|---|---|
| Dither, share of blind moved turns, 500 games | 16.3% (56,819 of 349,502) | 13.2% (40,543 of 307,399) | sw_slice 1 |
| Same without TD (468 games); without TD and both PD (443) | 15.7%; 15.2% | 13.1%; 13.0% | sw_slice 1 |
| Same, r0-50 only, without TD and both PD | 11.9% | 10.6% | sw_slice 1 |
| By opponent rating: under 1900, 1900-2099, 2100+ | 16.0, 16.3, 17.0 | 13.9, 12.5, 13.2 | summary B |
| Layouts where it is the higher one | 12 (by 3+ points on 7) | 7 (by 3+ points on 3) | summary A |
| The 7 big ones, points: TD +26.5, PD2 +19.8, PD1 +15.0, Schooltime 1 +8.2, Around UNSW +5.9, Islands +5.7, Autarky +4.2 | | | summary A |
| Games in which it is the higher one | 295 | 179 | sw_slice 3 |
| Dither turns as a share of all turns | 7.7% | 5.7% | sw_slice 2 |
| Keeps its direction when blind | 39.0%; lower on 18 of 19 layouts, every band | 50.2% | sw_slice 1, 8 |
| Board seen by r100, by band | 76.4, 76.3, 75.6; higher on 14 of 19 layouts | 70.0, 74.8, 78.0 | summary B, sw_slice 8 |
| Board seen by r100 on TD | 35.0 | 71.6 | summary A |
| Distinct tiles per dragon per 20 blind rounds (15 layouts) | 9.57 | 9.17 | summary C |
| Hot share of all turns | 15.7% | 18.4%; higher on 15 of 19 layouts | sw_slice 2, 8 |
| Hot share by band | 15.8, 15.0, 17.6 | 18.4, 17.1, 20.9 | summary B |

Inside a layout, our games only (measured):

| Cut | Result | Where |
|---|---|---|
| Our dither against our pearls by r100, layout mean removed | +0.17 (dossier D, reproduced); +0.22 without TD; +0.08 with dither from r0-50 only | sw_slice 4 |
| Same with our dragon-turns held (crowding) | +0.10; r0-50 dither +0.02 | sw_crowd |
| r0-50 dither against r51-100 pearl share, r0-50 pearl share held | +0.01 | sw_slice 5 |
| Halves by our dither inside each layout | low half 105.4 pearls, share 0.465, 119 of 232 won; high half 124.5, 0.521, 135 of 232 | sw_slice 6 |
| Layouts where the low-dither half has the higher pearl share | 8 of 19 (r0-50 dither: 9 of 17) | sw_slice 6 |
| Dither in won against lost games | higher in the won games on 12 of 19 layouts | summary D |
| Our keeps-direction against our pearls | -0.33 (-0.18 with dragon-turns held): our straighter games eat less | sw_slice 4, sw_crowd |
| Our hot share against our pearls | +0.57 (+0.57 with dragon-turns held); high half has the higher pearl share on 17 of 19 layouts; 146 against 115 of 242 won | sw_slice 4, 6 |
| Hot gap in r0-50 against pearl share in r51-100 | +0.46; -0.02 once the r0-50 pearl share is held (our hot alone: +0.25, then +0.07) | sw_slice 5 |
| Hot gap on the 5 layouts with no fast tile at all against the 14 with some | -3.7 against -1.3 points (r101-300: -7.0 against -6.5); rank correlation of fast supply with the gap +0.25 | sw_maps |
| The 4 layouts where our hot share is the higher one | we eat 0.56 to 0.69 of the pearls on all four | sw_maps |

Read with it: the 45 against 12 of the first count is the walled start room (TD 44.7 against 18.2) and nothing like it exists elsewhere. What is general is that ours turn more often (39 against 50). That does not cost ground: we see more board on 14 layouts and cover as many new tiles per blind dragon. And it does not go with fewer pearls in our own games in any cut. The hot-tile gap is as large where no tile spawns fast, so it is not dragons parked at fountains; it follows who is eating.

## The code (main.cpp, read from the code)

- Nothing within 7 steps: the pearl pull 2 x (260 - 40 x steps) is zero (346-348, 3260-3265, 5021-5023). Left are FAR_GAIN, 2 a step toward the nearest pearl, soon tile, hot tile or unseen tile (261-262, 5037-5046), and the unseen bonus, at most 52 (374, 5028). EXPLORE_GAIN is 0 (264, 5034-5036).
- The step is then decided by room and territory, 1.5 each a tile (335-336, 4971-4976), less the cramped terms with PENALTY_NO_TAIL 600 (375, 4987-4989). No term knows the last direction and no list of visited tiles exists beyond the body (trail, 1395-1399). NO_REVERSE is in the file and off; it only stops the survey counting back through the tile the head leaves (240, 4957). Estimate: with the score built new every turn and turning free, this is why ours keep direction less on 18 layouts. It is not what holds them on TD; that is CENTER_PULL and the no-tail penalty (losses/early-growth.md).
- Hot tiles are already in the bot (F20 says there is no such memory; that is wrong). A tile is hot once this dragon has seen its countdown at 4 or less twice, 6 to 25 rounds apart, and is dropped when seen above 8 (352-355, 1575-1597). Pull 1.2 x (260 - 40 x (steps + wait)), only if no friend is nearer and we are at most 1 step behind the nearest enemy (356-357, 2969-2973, 5025-5027); a hot tile in range also turns CENTER_PULL off (5061-5063).
- That memory is per dragon and a split child starts empty (439; rules/splitting.md:11, rules/overview.md:13). Estimate: a young dragon has to watch a tile through two cycles before the rule does anything for it. Not counted.

## The card (a record of a negative result; nothing to build)

title: Keep-moving rule and hot-tile parking: counted on 500 ladder games, neither earns a switch
slug: sweep check
What we tried: Nothing built. Sliced the dossier (500 main games, 19 layouts, both sides) by layout, rating band, halves inside a layout, lag and dragon count, and read the code that moves a dragon with nothing in range.
Did it work: No. The dither gap is general but 3 points wide and has the wrong sign for a cost; the hot-tile gap is real but cannot be told from eating.

### Area
Rounds 0 to 100, dragons with no pearl in view, all layouts.

### Claim
Measured: our dragons turn more than the opponents' on 18 of 19 layouts and re-tread their own tiles a little more on 12, against every rating band. Measured: it costs neither ground nor pearls in any cut of our own games. Estimate: a rule that keeps a dragon moving on has no gap to close outside the walled start room, which the stall release card (losses/early-growth.md) already covers. Measured: the hot-tile share goes with pearls at the same time and adds nothing about later pearls. Estimate: a second hot-tile rule on top of main.cpp:1575-1597 would be a guess.

### Evidence
- Measured: dither 16.3% against 13.2%; 15.2% against 13.0% without the three layouts that carry it; 11.9% against 10.6% in r0-50.
- Measured: inside a layout the low-dither half eats 105 pearls by r100 and wins 119 of 232; the high half 125 and 135. Correlation +0.17, +0.10 with dragon count held, +0.01 with a lag.
- Measured: board seen by r100 is ours on 14 of 19 layouts; 9.57 against 9.17 new tiles per blind dragon per 20 rounds.
- Measured: hot share 15.7% against 18.4%, theirs on 15 of 19 layouts; +0.57 with our pearls inside a layout, -0.02 with a lag once earlier pearls are held; the gap is no smaller on the 5 layouts without a fast tile.
- From the ledger: F41 (refuted) had the same reversed straight-walking number on seven layouts; the F20 verifier found no link from our heads at busy tiles to our pearl share and none to wins.

### Expected signal
Estimate, if this verdict is right: in the next 100 main games the low-dither half inside a layout again does not out-eat the high half (pearl share 0.47 against 0.52 now), and our board seen stays the higher one on most layouts. For hot tiles the next step is a count, not a build: one local game per layout class with the idle log line that already prints dist_hot (main.cpp:596-598; on when IDLE_LOG is above 0, printed for a dragon that has not grown for that many rounds), giving the share of those turns in r0-100 in which the dragon knows any hot tile, split by dragon age.

### What would show it's wrong
- A local pair, same seeds, with any momentum term (a small cost for changing direction when the pearl, soon and hot bonuses are all zero) that raises pearls by r100 on at least 12 of the 19 layouts: then turning does cost and the within-layout cuts were hiding it.
- Within layout and with dragon count held, the correlation of our dither with our pearls drops below -0.10 on new games (now +0.10).
- The dist_hot count shows our dragons know a hot tile in under 5 percent of turns on layouts where a third of their heads stand by a busy tile and a fifth of ours (Around UNSW, Slithery Fight: F20): then the existing rule is nearly idle, and passing the marks to a split child, or marking a tile on one sighting, becomes a card.
- Our board seen falls below theirs on most layouts in new games.

## Against it

- Measured: in the 165 games where we are behind in total length at r100 (119 lost, 72 percent; 98 of 304 otherwise) our dither is 18.7% against their 13.5%, and 17.1% without TD, against 15.2% in the other games. Two points more dither in the games that matter is in the direction of the claim. It can as well be an effect of being behind (few dragons, nothing in view).
- Every cut here is a correlation inside our own games. None of them is a test of a rule; a keep-moving rule could still help in a way these cuts cannot see, for instance by reaching far pearls first (F14). The opponents are a mix of bots and nearly all of them walk straighter than we do.
- Measured: F41 found us the later side to the first meal in 170 of 283 games on the 2-dragon-start layouts, by two to four rounds. A small effect of this kind is below what the dossier can show.
- The hot-tile verdict rests on a measure that is circular by construction: I did not count the bot's own hot marks, and the estimate that split children lose them is unmeasured. If one of the two had to be built today I would take neither and spend the round on the count above; the stall release card stands before both.
- Not done: no replay was opened (the brief stops at a no). Not checked: that main.cpp on disk is the build that played as main on the ladder.
- Housekeeping: the guard refused plain writes because the project path is stored in decomposed Unicode; the files were written through the reviewed Python route with the path spelled that way, as the early-growth run did.
