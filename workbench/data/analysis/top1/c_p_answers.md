## Answers to the eight questions

All-games counts are over our games against 2000+ teams with Schooltime left out (large maps: 111 games; medium: 117; small: 173)
and over the games of the three top teams against 2000+ teams (all of them for the `c_agg.py` tables, a spread sample of 50-80
per team for the scripts that walk whole replays; each output file names its sample). "Our opponents" in a table means test4 and
WHQ in their games against us, unless it says "all opponents in our games".

### a. Where does the first gap open?

**It depends on the map; on the large maps it opens at the first contact, not before.** All large-map games, means per game
(`c_agg.py`, `c_out/agg_large_*.txt`):

| rounds | units at round 50 / 100 / 150, meow / test4 / WHQ | natural pearls eaten | dragon-turns | natural pearls per 100 dragon-turns | turns with an enemy head in view, meow |
|---|---|---|---|---|---|
| 0-49 | 29.2 / 33.1 / 33.3 | 71.7 / 76.3 / 80.7 | 995 / 1,060 / 1,070 | 6.6 / 7.0 / 7.2 | 12% |
| 50-99 | 42.7 / 55.9 / 52.7 | 90.9 / 124.7 / 121.8 | 1,902 / 2,345 / 2,255 | 4.7 / 5.4 / 5.3 | 26% |
| 100-149 | 47.0 / 62.3 / 59.4 | 79.0 / 129.4 / 132.9 | 2,315 / 3,079 / 2,880 | 3.3 / 4.2 / 4.6 | 34% |

In rounds 0-49 we eat 6-11% less; in rounds 50-99, when a quarter of our turns have an enemy head in view, 25-27% less; in rounds
100-149 about 40% less. In the games read the first ram between the two teams is at round 52-90 on Australia, 18-27 on Around
UNSW, 20-32 on Islands and 33-42 on Slithery Fight. The table pools the builds; the 99 live games have 42.4 units at round
100 and 46.4 at round 150, the 12 games of the trade-on-contact test build 45.2 and 51.6 (`c_out/bybatch_large.txt`).

**When the unit ratio falls below 0.8 for good** (own units / enemy units below 0.8 from that round to the end of the game;
`c_gap.py`, `c_out/gap_1119.txt`, all 401 games):

| map size | games | rounds 0-49 | 50-99 | 100-149 | 150-199 | 200-299 | 300+ | never |
|---|---|---|---|---|---|---|---|---|
| large | 111 | 5 | 22 | 7 | 7 | 3 | 18 | 49 |
| medium | 117 | 30 | 9 | 4 | 4 | 3 | 11 | 56 |
| small | 173 | 53 | 15 | 2 | 0 | 1 | 9 | 93 |

By map, large: Australia 13 of 28 in rounds 50-99; Islands 4 before round 50, 9 in 50-99, 7 in 100-149, 5 in 150-199; Around UNSW
and Slithery Fight never before round 150 (0 of 53 games), although we win only 11 of those 53: there the units are level (median
ratio 0.94-0.97 at round 150 and 200) and the total length is not (median ratio 0.61 and 0.78 at round 150). By opponent on large
maps: against test4 16 of 42 games are lost in units in rounds 50-99; against WHQ 29 of 44 never, and we win 2 of the 44: the
median total-length ratio against WHQ goes 0.95, 0.78, 0.64, 0.52, 0.45 at rounds 50, 100, 150, 200, 300. Medium and small:
Trauma against test4 (10 of 11 before round 50), Stripes (20 of 29), Tower Defense (14 of 24) and Queen Of Spades (14 of 28,
a map I did not read) are behind before round 50, which is before any ram; on the three I read the fountains are behind a
portal or outside the start room.

**The games read** (`c_qa.py`, `c_out/qa_table.md`; "first ram" = the first ram between the two teams; "the 20 rounds before" are
the two 10-round blocks before the round in which the units, or if they never do, the total length, fall behind for good; a
round after 350 has no block data. "Never" means the ratio was 0.8 or more at the end of the game, which also happens when
the opponent feeds one dragon in the end game and its total shrinks: 1063016 has total length 150 against 333 at round 150
and is "never" behind for good. The run and build of each game are in the table of games read):

<<RAW c_out/qa_table.md 1 32>>

Reading. In the five Australia and Islands games against test4 the fall is at round 73-125. In the 20 rounds before it test4
eats 1.7-2.1 times our natural pearls in three of the five (22 against 38, 18 against 37, 20 against 35) and more corpse pearls
in four; in the three Islands games 9-10 of our dragons die in rams in those 20 rounds (rammed or ramming). In the three large-map games
of the test build against WHQ the units never fall behind for good and the total length does at round 170-249, in 20 rounds in
which WHQ eats 2-3 times our natural pearls (17 against 49, 19 against 37, 19 against 43) and in two of the three rams 7 and 12
of our dragons. On Trauma against test4, Tower Defense and Stripes it comes before any ram, in rounds in which we eat nothing.
A unit ratio "for good" that falls after round 390 (Around UNSW, Slithery Fight) is the end game, not the economy: on those
maps look at the total length.

**Does the gap decide the game?** Large maps, games that reached round 300 (`c_endstate.py`, `c_out/endstate_<team>.txt`):

| | meow | forgot | SSS | Vibing++ |
|---|---|---|---|---|
| games that reached round 300 | 109 | 158 | 139 | 127 |
| own total length below the opponent's at round 300 | 108 | 82 | 48 | 40 |
| wins among those | 11 = 10% | 29 = 35% | 24 = 50% | 16 = 40% |
| level or ahead at round 300 | 1 | 76 | 91 | 87 |
| wins among those | 1 | 52 = 68% | 68 = 75% | 61 = 70% |

We are behind in all 97 losses and in 11 of our 12 wins; all 12 wins are on the longest dragon. On medium maps we are behind at
round 300 in 66 of 84 games and win 11 of them (17%), and win 14 of the 18 others; on small maps 55 of 75, 6 wins (11%), and
8 of the 20 others (most small-map games end by wipe-out before round 300). The gap of this file is there in nearly every
game; what it costs depends on the end game, where the top three recover a third to a half of the games in which they are
behind and we a tenth.

### b. With the same pearls on offer, why do we eat fewer?

First what it is not. **Our dragons are not slower when left alone.** A natural pearl that appears within 6 steps of one of our
heads with no enemy head within 6 steps is eaten after 3.8 rounds in rounds 0-49, 2.6 in 50-99 and 2.7 in 100-149; test4's
dragons need 3.4, 3.0, 3.2 and WHQ's 3.4, 3.1, 2.9; forgot 2.9, 2.6, 2.6; SSS 3.0, 2.6, 2.7; Vibing++ 2.4, 2.0, 1.9
(`c_agg.py`). With a pearl in view and nobody else as near, our dragons eat or end nearer in 64-67% of turns, test4's in 66-69%,
WHQ's in 66-69%. **And we do not lose more dragons in dead ends**: boxed deaths in rounds 0-149 on large maps are 82 for us, 78
for test4, 85 for WHQ, 95 for forgot, 67 for SSS and 103 for Vibing++.

**Where the pearls are lost** (large maps, rounds 50-149, pearls per game; `c_out/agg_large_50_99.txt` and `_100_149.txt`):

| income | meow | test4 against us | WHQ against us | gap to the two | share of the gap |
|---|---|---|---|---|---|
| natural, on fountains of the enemy's half | 34 | 76 | 76 | -42 | 33% |
| corpse pearls of own dragons | 89 | 117 | 118 | -29 | 22% |
| natural, on fountains of the own half | 106 | 128 | 128 | -22 | 17% |
| natural, on other tiles | 30 | 51 | 51 | -21 | 16% |
| corpse pearls of enemy dragons | 15 | 31 | 29 | -15 | 12% |
| all pearls | 274 | 402 | 402 | -128 | |
| segments lost (all deaths and paid steps) | 222 | 259 | 263 | we lose 39 fewer | |

Close to half of the gap (the fountains of the enemy's half and the enemy's corpses, 45%) is made in the other half or at the
border. The corpse pearls of own dragons (22%) follow partly from the opponents having more to recycle (they lose 259-263
segments, we 222) and partly from who gets to a corpse first (point 2 below). The causes the brief lists, ranked, with their
counts:

1. **Dragons standing off from enemy heads (the largest).** Large maps, rounds 0-300 (`c_avoid.py`, `c_out/avoid_*_large*.txt`): a
   meeting (a turn of a dragon of 4 or shorter that begins with an enemy head of 4 or shorter on the next cell) happens 69.7
   times a game to us. Over all our games we ram in 12% (18% when shorter than the enemy, 13% at the same length, 5% when
   longer) and step away in 88%. By build: the live bot (99 games, 6,994 meetings) rams in 10% (14 / 11 / 5); the
   trade-on-contact test build (12 games, 739 meetings) in 31% (49 / 36 / 7). Our opponents in the same games ram in 36%
   (62 / 33 / 22), forgot in 37% (63 / 36 / 26), SSS in 42% (86 / 41 / 24), Vibing++ in 36% (56 / 37 / 25). In the ten rounds after
   one of ours steps away it eats 0.33 pearls and the enemy it left eats 0.70; 20% of them are rammed in those ten rounds all
   the same (an opponent that steps away from the live bot: 8%; from the test build: 18%). With an enemy head in view (not next
   to it) our dragons end the turn farther from it in 34-37% of turns and nearer in 12-13%; everyone else 22-29% and 15-22%
   (`c_agg.py`).
   *Charges.* A meeting is not where most rams come from. Of the 22.9 rams a game that our opponents make in rounds 0-149, 41%
   are made from the next cell and 59% with a move of two or more steps; forgot 58% and 42% (of 20.8), SSS 45% and 55% (of
   18.6), Vibing++ 43% and 57% (of 22.6) (`c_ramsteps.py`, `c_out/ramsteps_large.txt`, from the head-on records of every game).
   The live bot makes 5.1 rams a game in those rounds, 81% from the next cell: 1.0 charge a game against 13.7 for our
   opponents and 8.7-12.9 for the top three. The test build makes 13.8 rams, 3.9 of them charges. Our bot can charge
   (`ram_path()` searches up to four steps for a marked target); what it lacks is targets: an enemy head is marked only when
   the dragon sees at least as many other own heads as enemy heads, the team has 8 units and the target is long enough
   (`mark_trade_targets()`).
   *Consequences that can be counted:* 76% of our heads are in our own half in rounds 50-99 (the others 68-72%); 58% of all rams in our games happen in
   our half (top three 47-48%, `c_front.py`); natural pearls that appear with only an enemy head within 8 steps outnumber those
   with only one of ours 17,097 to 13,282 in rounds 0-99, 20,464 to 9,621 in rounds 100-199 and 51,326 to 18,982 after round
   200 (`c_contest.py`, 111 games; for forgot the two numbers are 47,666 and 52,173 over the whole game, for SSS 47,635 and
   44,619).
2. **The pearls of the dead go to the other side.** Large maps, whole game (`c_rams.py`, `c_ramlocal.py`): 20.8 rams made and 65.1
   suffered per game; segments lost in them 296 for us and 332 for the enemy; pearls of those corpses eaten: we 109, the enemy
   255. Counted pearl by pearl (39,590 pearls of 9,540 rams): we eat 28%, the enemy 67%, 5% lie for 20 rounds. By the number
   of other heads within 8 steps of the ram: three or more enemy heads more than ours (28% of the rams): we eat 7%; one or two
   more (25%): 15%; the same number (14%): 26%; one or two more of ours (18%): 45%; three or more (15%): 67%. forgot, SSS and
   Vibing++ in the same five classes: 16-19%, 30-32%, 47-49%, 67-69%, 81-83%, and 47-50% overall. With the top three's
   shares in each class and our own mix of classes we would eat 44-45%: being outnumbered more often explains 3-5 points of
   our 20-point shortfall, and what our dragons do with the same numbers around them explains the rest. By build
   (`c_rambatch.py`, `c_out/rambatch_1119_large.txt`): the live bot eats 27% (82 rams a game, 22% of them started by us; 47%
   of the pearls of the rams we start and 19% of the others), the test build 33% (116 rams a game, 37% started by us; 52%
   and 21%). Starting more rams raises the share because the starter eats more; it does not change what happens to the
   pearls of the rams the enemy starts, and those are still two rams in three. With a ram-corpse
   pearl at the same distance from one of our heads and an enemy head we get it in 35% of cases, forgot in 47%, SSS in 52%
   (`c_contest.py`). Rule in our bot (inference from the source): a pearl is a target only if we reach it strictly before any
   enemy head, or, for dragons of 4 or shorter, within one step of the enemy's distance; and cells next to a small enemy head
   carry a penalty of 225-450 against 520-820 for a pearl. The team's own log (`plan.md`) found the same against one opponent
   (34% of ram pearls against calc) and a relaxed corpse rule changed nothing in local games.
3. **Fewer dragons.** 19% fewer dragon-turns than test4 in rounds 50-99 and 25% fewer in 100-149. It is a result of 1 and 2
   and of the next point, and then a cause: per 100 dragon-turns we eat 86-88% of what they eat in rounds 50-99 and 73-79% in
   100-149, so in rounds 50-99 about two thirds of the natural-pearl gap is the number of dragons and one third the rate; in
   100-149 half and half.
4. **Fewer new dragons per pearl, on one map by a form of our own.** Large maps, rounds 0-99, per game (`c_midall.py`): splits by
   a dragon of exactly 4 (the split that makes a new 2-long forager and keeps the parent): meow 56, all opponents in our games
   85, forgot 107, SSS 75, Vibing++ 81. Splits in which a dragon of 5 or more keeps only its front two segments and leaves the
   rest ("shed"; the front part is in a dead end and dies): meow 39, opponents 22, forgot 9, SSS 16, Vibing++ 27. We eat 4.1
   pearls for every split at 4, our opponents about 3.3, forgot 2.8. By map the shed excess is Slithery Fight alone (125 sheds
   a game against 56 for our opponents; 65 splits at 4 against 120); on Australia, Islands and Around UNSW our sheds are 1, 7
   and 17 a game against 8, 3 and 17, and the fewer splits at 4 there (32, 67, 58 against 60, 78, 81) follow the fewer
   pearls. On medium and small maps there is no difference in sheds (5 against 5-6 a game). Rule in our bot behind the
   Slithery Fight form: no split while "harvesting" a dead end.
5. **Dragons kept back by a rule.** (i) After round 150 on large maps (300 on the others) a pearl within 9 cells of the leader
   is not to be eaten by other dragons: answer f. (ii) Pearls behind a portal: on Stripes the two best fountains of each half
   are in a pocket whose door is a portal. forgot's queen, from the same start cell as ours, is through the door at round 8
   and eats at rounds 10 and 11; ours is next to the door at round 7, goes through at round 18 in one of the two games read
   and not at all in the other (per-map notes). I first read this as the queen's portal ban; that is wrong, the ban is off on
   maps of 600 cells or fewer. Which rule holds her back I could not determine. (iii) Narrow places: on Maze we have eaten from 9.7 of
   the 19 fountains of our half by round 140 and WHQ from 18.1 of its 19; over all large maps we have eaten from 62% of the
   fountain tiles of our half by round 150, our opponents from 80% of theirs, the top three from 69% (`c_tilesall.py`).
6. **Dragons lost by a step they could have not taken.** Non-ram deaths with a free cell next to the head, rounds 0-149, large
   maps: 6.4 per game for us (15 segments), 2.2 for our opponents; 6.3 of ours are steps through a portal onto a body on the
   far side (4.3 onto a team-mate, 2.0 onto an enemy). On Islands it is 18.4 per game (`c_freedeaths.py`).
7. **Idle dragons.** Dragons that have not eaten for 20 rounds: 19 of 41 at round 90 (47%) and 25 of 46 at round 140 (54%); test4
   20 of 52 (39%) and 31 of 62 (49%); WHQ 20 of 50 and 25 of 59 (39%, 42%). A smaller difference than I expected; the per-map
   notes have two examples (the camper on Islands, the queen on Stripes).
8. **Dragons in each other's way: no.** We crowd less than anyone: an own second head within 2 steps of an eaten pearl 14 times
   per game in rounds 50-99 against 27-35 for everybody else, and 81% of our heads have an own head within 6 steps against
   80-89%.
9. **Each dragon slower to the pearl: no** (see the top of this answer), until round 150; after it, yes (answer f).

### c. Spread

**Our children leave the parent as far as anybody's; what we do not do is enter the other half.** Large maps, rounds 0-149, all
games (`c_agg.py`): path distance between parent and child five rounds after a split: meow 6.2, test4 6.1, WHQ 6.4, forgot 6.1,
SSS 5.7, Vibing++ 5.9; after ten rounds 8.0, 8.7, 8.5, 8.8, 7.9, 8.1. Share of the child's steps in its first ten rounds that
go onto cells no own head had visited: 21%, 21%, 20%, 20%, 18%, 18%; of the parent's: 21%, 22%, 20%, 20%, 19%, 18%. I see no
rule in any team that sends the child "away" or towards unvisited cells: the child's head is the old tail, so its first steps go
back along the parent's trail in every team, and four of five steps of both parent and child are on cells the team has
visited. (A2's 6.4-7.3 against 4.0-5.3 on Australia was forgot against Vibing++ in one game; over all games forgot and Vibing++
are 6.1 and 5.9.)

The difference is at team level. Cells visited by round 90 and 140: meow 752 and 1,123; test4 895 and 1,400; WHQ 787 and 1,242;
forgot 908 and 1,369; SSS 821 and 1,223; Vibing++ 677 and 1,072. Squares of the 8x8 grid with an own head at round 90:
22.9 / 28.6 / 26.4 / 26.3 / 24.7 / 20.5. Own heads in the own half in rounds 50-99: 76% / 68% / 71% / 71% / 72% / 69%. Natural
pearls eaten on fountains of the enemy's half in rounds 0-149: 50 / 99 / 99 / 81 / 85 / 86 (`c_out/agg_large_0_149.txt`). On
Around UNSW the difference is the whole gap (27 against 109-122 pearls from the other half). Vibing++
spreads least of the top three and has the fewest units at round 100 (42), as A found.

How the others get there: by not turning back when an enemy head is near (answer b, point 1), not by a different split. The
trade-on-contact test build did not get there: 76% of its heads are in the own half in rounds 0-149 against the live bot's
78%, and it eats 57 natural pearls on the enemy's fountains against 49 (`c_out/bybatch_large.txt`). Ramming at a meeting is
one thing; walking towards an enemy head is another, and the test build changed only the first.

### d. Dead ends and pockets

**The top teams lose as many small dragons this way as we do or more; nobody avoids the cell where a team-mate died.**
Boxed deaths in rounds 0-150, about 12 games per team and map (`c_deadcells.py`, `c_out/deadcells.txt`):

| map | meow | our opponents | forgot | SSS | Vibing++ | share of boxed deaths on a cell where a team-mate had died before, same order |
|---|---|---|---|---|---|---|
| Australia | 14 | 40 | 32 | 40 | 42 | 53% / 61% / 57% / 73% / 68% |
| Islands | 20 | 28 | 41 | 50 | 32 | 52% / 43% / 41% / 58% / 46% |
| Around UNSW | 45 | 54 | 88 | 92 | 87 | 57% / 40% / 60% / 66% / 51% |
| Slithery Fight | 243 | 207 | 262 | 88 | 288 | 81% / 68% / 72% / 45% / 74% |
| Trauma | 16 | 31 | 29 | 29 | 35 | 67% / 59% / 60% / 73% / 67% |
| Maze | 32 | 53 | 41 | 45 | 67 | 58% / 55% / 51% / 67% / 60% |
| weakhold | 37 | 41 | 20 | 26 | 74 | 77% / 71% / 35% / 71% / 74% |
| Tower Defense | 0.5 | 13 | 17 | 6 | 11 | 0% / 9% / 14% / 17% / 25% |
| Stripes | 3 | 24 | 16 | 18 | 31 | 26% / 70% / 50% / 69% / 71% |
| Portals | 123 | 43 | 110 | 54 | 42 | 74% / 50% / 46% / 58% / 56% |

We have fewer than our opponents on eight of the ten maps (not on Slithery Fight and Portals), mostly because we have fewer
dragons or do not go in. The one team with a visibly lower number where it matters is SSS on Slithery Fight: 88 against
207-288, 45% on repeat cells against 68-81%, 9.6 deaths on its most used cell against 17-28. In the game read (1051824) 99
of SSS's 170 splits are at length 4 and 37 at length 5, and only 24 are by dragons of 6-8 that keep their front two segments
(ours in 1067917: 236). Whether SSS also remembers the cell I cannot tell.
What is particular to us is the form on Slithery Fight: 125 sheds a game in rounds 0-99 there against 56 for our opponents,
so most of our 243 boxed deaths on that map are the 2-long front parts of sheds (answer b, point 4). On Portals, where we
have the most boxed deaths of the five (123), the form is the ordinary one: 2-3-longs dying on fountain cells.

### e. Contact

**When an enemy small dragon arrives, ours give way and theirs do not.** The counts are in answer b, points 1 and 2. In one place
(Around UNSW, 1067909, the test build, the centre at rounds 22-30): four of ours and three of test4's die; one of ours rams a
5-long with a two-step move, two are rammed within a round of eating a pearl, by test4 dragons that charge three steps over
pearls to reach them, and one dies boxed by its own child, whose own steps then lead west, away from the pearls. test4's
survivors split on the 25 or so pearls still lying there. From round 30 on 85% of our heads are in our half.

Price of a ram not made (large maps, rounds 0-300, `c_avoid.py`): after stepping away our dragon eats 0.33 pearls in ten rounds
and the enemy it left 0.70, a swing of 0.37 pearls, and it is rammed anyway in 20% of cases (a top-three dragon that steps away:
22-26%; an opponent of ours that steps away from us: 9%). Price of a ram made: one dragon each; the pearls of both corpses go
61% to us when we start it at a meeting (2,423 pearls; live bot 59%, test build 65%) and 74% to the enemy when they do (5,107
pearls); for forgot, SSS and Vibing++ the rammer's team gets 68-70%. At equal lengths a ram is therefore worth about one pearl
to the side that starts it, and with the shorter dragon more; our dragons take it 13% of the time at equal length and 18% when
shorter (live bot 11% and 14%, test build 36% and 49%), the top three 36-41% and 56-86%.
Ground: in rounds 50-149 our opponents eat 76 natural pearls on the fountains of our half and we 34 on theirs.

Our rule (source): a dragon of 4 or shorter may ram only when there are at least as many own other heads in its view as enemy
heads (`TRADE_LOCAL_EDGE`), the team has 8 units, and, on maps over 1,200 cells and below the unit cap, the target shows at least
max(5, own length + 2) segments. A lone 2-long facing a lone 2-long therefore never rams on any map, and on a large map the
live bot rams no 2-4-long. The test build drops the third condition (a target of the own length is enough) and keeps the
other two.

**The test build on the ladder, game by game** (`c_pairs.py`, `c_out/pairs_large.md`). The run of the test build and a run of
the live bot 80 minutes earlier each played test4 and WHQ once on every large map, from the same side:

<<RAW c_out/pairs_large.md 1 18>>

Over all its 12 large-map games against the live bot's 99 (`c_bybatch.py`, `c_out/bybatch_large.txt`; four of the 12 are
against "dev test 1"):

| means per game | live bot (99) | test build (12) | their opponents (live / test build games) |
|---|---|---|---|
| meetings in rounds 0-149, share rammed | 35.3, 9% | 27.4, 31% | 26.6, 34% / 27.4, 33% |
| rams made : suffered, rounds 0-149 | 5.1 : 22.9 | 13.8 : 22.5 | |
| pearls of ram corpses eaten, rounds 0-149 | 28 | 47 | 65 / 71 |
| natural pearls eaten, rounds 0-149 | 239 | 262 | 336 / 335 |
| of them on fountains of the other half | 49 | 57 | 99 / 96 |
| own heads in the own half, rounds 0-149 | 78% | 76% | |
| units at round 100 / 150 / 200 / 300 | 42 / 46 / 41 / 35 | 45 / 52 / 48 / 42 | 54 / 61 / 62 / 62 and 51 / 58 / 61 / 59 |
| total length at round 150 / 300 | 121 / 118 | 143 / 147 | 212 / 331 and 191 / 291 |
| games won | 12 | 0 | |

Reading. The rule did what it says (31% of meetings end in a ram, the opponents' rate) and nothing else changed in the
code. It is worth about 5 units and 20 segments at round 150 and 7 units and 30 segments at round 300 on average, nearly all
of it on Australia and Islands (the eight pairs above: total length at round 150 goes from 128, 63, 108, 66 to 207, 107, 170,
102 there; on Around UNSW from 155 and 150 to 204 and 156; on Slithery Fight from 176 and 134 down to 143 and 113). It does
not move the border, it does not make the opponents eat less, and it wins nothing. That last count is weak evidence either
way: 0 of 12 against 12 of 99 is what chance gives one time in five when the true rate is the same, and all 12 wins of the
live bot are longest-dragon wins (11 of them from behind in total length at round 300), 6 on Around UNSW, 5 on Slithery Fight
and 1 on Australia, which is to say they are end-game wins and mostly on the two maps where trading on contact gains least.

### f. The round-150 switch on large maps

**Three things change at round 150, and each can be counted.**

1. *Small dragons stop eating pearls next to them.* A dragon of 2-4 that is not its team's longest, with a pearl on a free cell
   next to its head, a way out behind the pearl, no enemy head within two steps of the pearl and no team-mate next to it
   (`c_adj.py`, `c_zone2.py`; 111 games):

| eats it, % of such turns | rounds 0-99 | 100-149 | 150-199 | 200-299 | 300-399 | 400+ |
|---|---|---|---|---|---|---|
| meow | 81 | 82 | 61 | 59 | 59 | 56 |
| meow, pearl within 9 cells of our longest dragon (5+) | 83 | 81 | 44 | 41 | 42 | 39 |
| meow, pearl within 9 cells of another own dragon of 5+ | 85 | 80 | 56 | 56 | 58 | 56 |
| meow, no own dragon of 5+ within 9 cells | 80 | 82 | 67 | 66 | 65 | 62 |
| all opponents in our games | 81 | 85 | 85 | 84 | 81 | 78 |
| all opponents, pearl within 9 cells of their longest dragon | 80 | 85 | 84 | 83 | 75 | 73 |

   forgot is at 89-91% in every phase, SSS at 70-80%, Vibing++ at 83-89% until round 300. On medium and small maps, where our
   switch is at round 300, our rate is 84-85% in rounds 150-299 and 53% and 63% after round 300 (opponents 74% and 77%). That
   is 235 such turns a game in rounds 150-299 on large maps and about 94 pearls not taken at once; half of them we eat later,
   a tenth the enemy eats, four tenths still lie there ten rounds later. Rule (source):
   after `grow_round` a pearl within 9 cells of the leader the dragon knows of carries a penalty of 600 and no eating bonus
   for anyone but the leader. The table fits it: the drop is at round 150 exactly and is deepest near the longest dragon; that
   it is also there with no long dragon near may be a leader position the dragon remembers (inference).
2. *Splitting stops.* Ordinary splits per game in rounds 150-199 (`c_midall.py`): meow 15, all opponents in our games 24, forgot 59,
   SSS 33, Vibing++ 53; in rounds 100-149 ours were 32. Our dragons of 5 and more make 0.1 ordinary splits per game in rounds
   150-199 (forgot 14.5, Vibing++ 3.1, our opponents 6.5).
3. *The dragons of 5 and more become prey.* Per game, rounds 150-299: 3.4-3.6 dragons of 5-9 and 0.3-1.4 of 10+ alive at a
   time; they move two or more steps in 61-71% of their turns, eat 5.8-8.8 natural pearls per 100 dragon-rounds, shed their
   front two segments 42 times (once per 15 rounds per dragon), and are rammed 4.3 times (34 segments). Per dragon-round our
   5-9-longs are rammed about 5 times as often as those of our opponents in rounds 150-199 (1.3 a game of 3.4 alive against
   0.9 of 12.3; theirs are safe because we do not ram), 1.5-1.8 times as often as forgot's and Vibing++'s, and as often as
   SSS's.

**The switch is the same in both builds.** It is the same code, and the counts agree: the eating rate of the first table falls
from 82% in rounds 50-149 to 59% in rounds 150-299 in the live bot's 99 games and from 83% to 62% in the test build's 12
(`c_out/adj_1119_large_notc.txt`, `c_out/adj_1119_large_tc.txt`). The live bot's units go 46, 41, 35 at rounds 150, 200, 300
and the test build's 52, 48, 42, while their opponents stay at 58-62 (`c_out/bybatch_large.txt`). In the two games the test
build had won by round 150 (1068050 and 1068051, 60 units against 33 and 39) the total length is behind by round 249 and 213.

**What the 2-longs do after the switch.** Natural pearls per 100 dragon-rounds, large maps (`c_midall.py`):

| | r50-99 | r100-149 | r150-199 | r200-249 | r250-299 |
|---|---|---|---|---|---|
| meow, 2-long | 3.0 | 2.0 | 1.25 | 1.3 | 1.4 |
| all opponents in our games, 2-long | 4.0 | 2.9 | 2.5 | 2.3 | 2.3 |
| forgot / SSS / Vibing++, 2-long (r50-99, r150-199, r250-299) | 4.7 / 3.4 / 5.1 | | 2.8 / 2.8 / 3.3 | | 2.5 / 2.5 / 2.9 |
| meow, 3-4-long | 6.7 | 4.2 | 2.5 | 2.8 | 3.1 |
| all opponents, 3-4-long | 7.3 | 4.9 | 4.2 | 4.0 | 4.1 |
| meow, dragons alive: 2 / 3-4 / 5-9 / 10+ | 23 / 13 / 1 / 0 | 27 / 17 / 2 / 0 | 24 / 16 / 3 / 0.3 | 21 / 13 / 4 / 1 | 20 / 12 / 4 / 1 |
| all opponents, dragons alive | 26 / 17 / 2 / 0 | 27 / 24 / 6 / 1 | 22 / 24 / 12 / 3 | 20 / 22 / 16 / 5 | 19 / 19 / 16 / 8 |

**One game, 1068051 (Islands against WHQ), rounds 140-220, dragon by dragon:** in the per-map notes. In short: of 28 dragons of 5 or
more, 9 are rammed by 2-4-longs, 8 shed in a dead end, and the rest roam the whole board at two steps a turn eating 0-9
pearls each in 80 rounds; the fountains they left are eaten from less (a pearl lies on 42-69% of our fountain tile-rounds
after round 150 against 22-40% before).

**The top teams' 5-9-longs in rounds 150-300.** forgot has 3.5-4.2 of them at a time and they split in the ordinary way 11-14
times per 50 rounds (ours 0); SSS has 6.2-6.9, which shed 21-22 times per 50 rounds and are rammed 2.3-2.6 times; Vibing++
4.3-6.4, 23 sheds. All three keep 25-31 dragons of length 2 and 20-24 of length 3-4 through round 300 (we 20-24 and 12-16). The
opponents in our games hold 12-16 dragons of 5-9 and 3-8 of 10+ from round 150; against the top three test4 and WHQ have
6-11 and 0.5-3.5 (`c_out/midall_*_vs19_87.txt`).

**Why the natural intake halves:** fewer dragons (units 47 at round 150, 42 at 200, 36 at 300 over all 111 games), each small one eating
half as much (1.25-1.4 against 2.3-2.5 for 2-longs), of which the declined pearls are the countable part, and the border moving
further into our half (natural pearls appearing with only an enemy head within 8 steps: 2.1 times those with only ours in rounds
100-199, 2.7 times after round 200).

### g. test4 and WeHaveQuizzes against the top three

Against the top three the two are ordinary (large maps, 21 games of test4 and 4 of WHQ, `c_agg.py` and `c_rams.py`): test4 has
52 units at round 100 and 60 at round 150 (forgot 52 and 58, SSS 54 and 58), eats 285 natural pearls in rounds 0-149 (forgot 322,
SSS 315, Vibing++ 305) and gains nothing from rams (swing -3 segments per game; against us +68; WHQ -9 and +148). What they do
that the top three do not, or less:

- **test4 has few boxed deaths in the first 50 rounds** (13-14 per game; forgot 21, Vibing++ 20, SSS 12, we 18).
- **WHQ sprints.** Moves of two or more steps in rounds 50-99: WHQ 40 against us and 87 against the top three, test4 25 and 9,
  forgot 10, SSS 43, Vibing++ 38, we 3. WHQ pays 6 segments per 50 rounds for it, we none before round 150.
- **Both eat on the other half's fountains from the start** (23 pearls in rounds 0-49 against us; forgot 23, SSS 20, Vibing++ 22;
  we 16), and against us they take 1.4-1.6 times as much there as against the top three in rounds 50-149 (76 against 47-56).
- **Both charge, as the top three do.** Rams made with a move of two or more steps in rounds 0-149: 13.7 a game against us and
  12.4 against the top three (forgot 8.7, SSS 10.2, Vibing++ 12.9; `c_ramsteps.py`). The difference between their games
  against us and against the top three is not what they do but what comes back: the top three make 19-23 rams a game in
  those rounds (over all their opponents), the live bot 5.
- **WHQ consolidates early and by suicide orders**, like forgot: 30-62 non-ram deaths with a free cell per 50 rounds from round 250
  in the two games read to round 350, and one dragon of 70-138 at the end of our large-map losses. test4 mostly keeps 50-64
  units to the end.
- What the top three do that the two do not: forgot splits its 5-9-longs (answer f); SSS and Vibing++ ram the queen at any
  length (A's and A2's finding). I found nothing in the opening that only the top three do.

### h. One rule for the opening, one for the mid-game

In the section "What I would change".
