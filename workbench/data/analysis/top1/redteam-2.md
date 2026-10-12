# Red team, round 2: the race footing, "one leader, known to all" and "nobody leaves a pearl for the leader" (sub-session C2)

Written 2026-10-05 for team meow (id 1119). This file tries to break two new candidate rules for our bot and one
correction, by counting everything again from the replays, and then says which of three finalists I would send to
the team. I ran no game and used no network. The words used below are explained right after the table.

## Verdicts

**In short.** The counts of the last close read (`deep-read-5.md`, sub-session A5) reproduce almost to the game.
What they are taken to mean holds up less well in two of three places.

- **Claim A** (the race gap is mostly the economy seen late) is half right. The first red team's footing was biased
  and A5's is fairer, but about half of the gap is still there on A5's own footing: at the top three's conversion our
  143 races would have given about 49 wins instead of 41.
- **Candidate 5** (one leader, known to all) describes something real, mostly in the earlier bot. In today's builds
  the stall after a leader cut is shorter, on maps of 1,200 cells or fewer it is hardly there, and the pearls that
  demonstrably go astray are about 6 a race. I get 1 to 5 games of 401 on the strict reading where A5 gets 6 to 12,
  and one of its three code changes does not do what it says.
- **Candidate 3z** (nobody leaves a pearl lying for the leader) is the best-identified finding of the whole study: a
  step at exactly our own switch round, on both kinds of map, in every run, in no other team, and at exactly 9 cells
  from the leader each dragon names. It costs us a fifth of our natural pearls on the smaller maps and a third on
  the big ones. One of its five supports is wrong as stated: the zone does hand the leader pearls, mostly pearls of
  feeders late in the game, and 7 of our 41 race wins were closer than that. With that part kept it is the candidate
  I would send.

| Item | Verdict | Claimed | What I would defend | The strongest objection | What would settle it |
|---|---|---|---|---|---|
| **Claim A**: "30% against 55% at level length" is mostly the economy; at level potential we win about half | **Holds, weaker than claimed** | most of the gap is the footing; what is left is "small" | About 45% of the first red team's gap is the footing. What is left: at equal potential at round 300 we convert worse than the top three by 0.33 in log-odds (80% range 0 to 0.66), about 8 wins in our 143 races (range 0 to 16), which is +2 points of win rate (0 to +4) | "We win 11 of 23 at level potential" compares us with test4 and WeHaveQuizzes, who are in the same games. Against those two the top three win 11 of 16 at level potential. And half of what is left sits in races we enter with under half the enemy's potential: we won 0 of 48, the top three 5 of 43 | Nothing we can play. More top-three races against test4 and WeHaveQuizzes would (there are 30) |
| **Candidate 5**: one leader, known to all | **Holds, weaker than claimed** | +0.7 to +2.2 points, "most likely a little over +1" (strict 6 to 12 games of 401) | -0.3 to +0.8 points, most likely +0.2 to +0.4 (strict 1 to 5 games) | The 27-round blindness is measured on 82 games of an earlier bot. In today's builds feeding next to the leader is back at its usual rate 10 to 20 rounds after a cut; the 25-round window after a cut grows as fast as a window with no cut (11.4 against 11.1); feeders that die for the 2-long stub are 7.6% of our feeder deaths. The age rule as written lets the old report win again on the next ping, and it invites regional leaders: our two longest dragons are within 12 segments of each other in half to nine tenths of our races | 20 to 60 replays of a build with it: share of feeder deaths for a stub or for a dragon under twice the feeder's length (12% today) must go under 4%; deaths next to another big dragon that is not the longest (39%) must not rise |
| **Candidate 3z**: remove the pearl zone on every map | **Holds** for the behaviour and the economy, more strongly than stated; one of its five supports **does not hold** ("the leader gets nothing from it"); the size in wins **cannot be told** better than a range | no size given | As defined (zone off in every phase): +0.3 to +2 points, most likely about +1. With the zone kept for the pearls of feeders once feeding has started: the same, with less risk | Every extra pearl is worth nothing if it does not convert, and when our economy was raised before it did not (the trade build: +21% length at round 300 on big maps, 0 wins of 12). The zone hands the dragon that ends as our longest 2.4 natural and 3.4 corpse pearls per small-map race that a small dragon had declined (0.9 and 2.2 on big maps); 7 of our 41 race wins were closer than that | 20 big-map and 20 small-map games of a build with it. Free pearl next to the head taken: 51-58% to over 80%; natural pearls per 50 rounds after the switch: 54 to 70 or more on big maps, 31 to 37 or more on the others; the final longest's share of feeder pearls (39% / 25%) must not fall |

**Which one I would send:** candidate 3z, amended so that feeder pearls next to a leader in view stay reserved once
feeding has started. Candidate 1 (take the queen) is as large and surer in sign; it can ride along, because it touches
other code and is read on another number. Candidate 5 I would not send. Section 4 has the table and the reasons.

### Words

- **Queen**: each team's lowest-numbered dragon. At round 500 a living queen beats a dead one.
- **Race**: a game that reaches round 500 with both queens dead. The longest single dragon then wins. We have 143
  such games (41 won), the three top teams 447 (266 won).
- **The top three**: Vibing++ (id 306, rank 1), SSS (91), "forgot to mention" (264). **test4** (19) and
  **WeHaveQuizzes** (87, "WHQ") are the two teams rated just over 2000 that we meet in 313 of our 401 games.
  **Our opponents** = the other side in our 401 games.
- **Small maps / big maps**: 1,200 cells or fewer / more. Only because our own code switches there.
- **Live bot / test builds / earlier bot**: our 401 games are 275 of the released bot of that hour and 126 of test
  builds (stride, passage2, qh31, tc30). In 82 of the live-bot games (ladder of 3 October, the first 31 of 4 October,
  the run "stride-old") the bot's sonar pings can be read; that is the **earlier bot**. Later builds seal their
  pings; I left them sealed and never touched the key.
- **Leader**: a team's longest dragon. **Lineage**: the dragon that is the longest at the end, followed back through
  its splits.
- **Potential**: the longest dragon plus the pearls every other own dragon would drop if it died now (a dead dragon
  of length L drops L/2 pearls, rounded up). It is what the leader would be if the whole team were fed to it without
  loss.
- **Feeding**: small dragons die on purpose next to the leader, which eats their pearls. Our bot's feeders die by
  sending no order ("no order" death). **Feeder death** below means such a death.
- **Death by choice**: a death that is not a ram, of a dragon that had a free cell next to its head when it gave its
  order (A5's definition, which works for every team).
- **Leader cut**: a split in which a team's longest dragon (8 or longer) keeps 2-3 segments and hands the rest to a
  new dragon with a new id. The 2-3 segments that keep the old id are the **stub**, the new dragon is the **heir**.
- **Record / names**: every dragon of ours remembers one leader (id, length, position) and sends it on its sonar
  pings. A dragon "names" the id in its last readable ping.
- **Switch round**: round 150 on big maps and 300 on small maps (`grow_round` in our code). From then on dragons
  longer than 4 stop splitting and the **pearl zone** applies: a dragon may not take pearls within 9 cells of the
  position of the leader in its record.
- **Pearl turn**: a dragon of 2-4 that is not the queen gives a move order, no enemy head is in its 7x7 view, and a
  pearl lies on a free cell next to its head that has a further free neighbour. **Taken** = its first step eats it.
- **Natural pearl / corpse pearl**: a pearl that a tile produced / one of the pearls a dead dragon left.
- **Point**: one percentage point of win rate. One game of our 401 is 0.25 points. We win 112 of 401 (27.9%).
- **80% range**: the range in which the true value lies four times out of five, given the sample.
- **Strict / cautious reading**: strict changes one thing in a played game and keeps the rest; cautious takes half
  of it or less, because the enemy answers and because not every pearl that could be eaten is.

### How this was done

Every number the three items rest on was counted again with scripts written for this file (`y_*.py`, outputs in
`y_out/`). They use only the replay walker `lib.py` and the game list `games.csv`; I read the other sub-sessions'
scripts only to learn what they had counted. Four walks over the replays: `y_w1.py` (all 1,795 games in which a
study team plays a team rated 2000 or more, both sides: lengths every 5 rounds, every split, every death with what
stood next to it, every pearl eaten), `y_w2.py` (what our dragons name as leader, and what the dragons near every
leader cut do in the next 30 rounds), `y_w3.py` (every pearl turn, by the zone of the true longest dragon and by the
zone the dragon itself names; every pearl declined in a zone and who ate it; natural pearls per dragon-round inside
and outside a zone; how often a leader has no free cell), `y_w4.py` and `y_w4b.py` (every feeder death of ours with
what it died next to). Where my number differs from A5's or the lead's, both are given with the reason.

"Measured" means counted on replays by the script named. "Inferred" means arithmetic on played games or a reading of
the source `mybot2/main.cpp`. A replay shows positions, orders, deaths, pearls and pings. It does not show what a
bot intended.

## 1. Claim A: the footing of the race

**The claim (A5's).** The first red team compared races with level TOTAL length at round 400: on small maps we win
9 of 30 and the top three 22 of 40. A5 says this footing is unfair to a team that feeds late. A 2-long feeder leaves
1 pearl, so a team that has fed has already spent length, and "level at round 400" hides that the enemy was richer.
On potential we win 11 of 23 level races at round 300 and 12 of 24 at round 350. So most of the gap is the economy.

**The strongest argument against it, as its opponent would put it.** "Eleven of 23 is a coin toss against test4 and
WeHaveQuizzes, the two teams on the other side of those same games. It says we are no worse than they are. It does
not say we are as good as the top three, and the top three are the yardstick of this study. Against the same two
opponents the top three win 11 of 16 races at level potential. Put our 143 races on the top three's own curve, on
A5's own footing, and they are worth 49 or 50 wins, not 41. And 'level' is a narrow band: by moving the round or the
measure our share in it goes from 32% to 50%."

What is left after the recount: A5's counts are right to the game and the direction of the correction is right. The
size is about half of what the sentence "mostly the economy" suggests.

### 1a. The recount

`y_a.py` (output `y_out/a.txt`), from the walk `y_w1.py`. A race is counted from each study team's own side; "level"
is own / enemy between 0.8 and 1.25. Cells are won of games.

| | theirs (lead, first red team, A5) | mine |
|---|---|---|
| races, won: meow / top three | 143, 41 / 447, 266 | the same (Vibing++ 152, 99; SSS 141, 82; forgot 154, 85; our live bot 96, 27; test builds 47, 14) |
| level TOTAL length at round 400, small maps: meow / top three | 9 of 30 / 22 of 40 | 9 of 30 / 22 of 40 |
| ... ahead (over 1.25), small maps | 15 of 18 / 77 of 83 | the same |
| ... big maps, behind (0.5-0.8) / level | 6 of 23, 4 of 6 / 17 of 49, 73 of 116 | the same |
| potential at round 300, under 0.5 / 0.5-0.8 / level / over 1.25: meow | 0 of 48 / 20 of 58 / 11 of 23 / 10 of 14 | the same |
| ... top three | 5 of 43 / 18 of 51 / 99 of 169 / 144 of 184 | the same |
| level potential at round 350 / 400: meow | 12 of 24 / 13 of 34 | the same |
| ... top three | 103 of 178 / 89 of 155 | the same |
| level potential, against test4 and WHQ only, round 300 / 350 / 400: meow | 7 of 17 / 10 of 21 / 9 of 30 | the same (test4 4 of 9, 4 of 9, 6 of 17; WHQ 3 of 8, 6 of 12, 3 of 13) |
| ... top three | 11 of 16 / 11 of 13 / 9 of 13 | the same (SSS 8 of 10, 7 of 9, 5 of 7) |
| we enter races below 0.8 of the enemy's potential | 106 of 143 (20 won); median ratio 0.62 | the same |
| inside the first red team's band: total at round 300, ours : enemy | 65.5 : 90.5 (top three 101 : 94) | the same |
| ... games in which the enemy had over 1.25 times our total at round 300 | 17 of 30, won 5 (top three 7 of 40, won 5) | the same |
| final longest / potential at round 300, live bot, small maps | 0.65 | **0.77** (0.65 is the share of the final potential; see section 5) |

By map class and opponent, which A5 does not show (potential ratio at round 300; under 0.5 / 0.5-0.8 / level / over
1.25):

| | small maps | big maps |
|---|---|---|
| meow | 0 of 19 / 12 of 28 / 7 of 17 / 10 of 14 | 0 of 29 / 8 of 30 / 4 of 6 / none |
| meow live bot | 0 of 15 / 5 of 13 / 6 of 16 / 7 of 9 | 0 of 19 / 5 of 20 / 4 of 4 / none |
| meow against test4 | 0 of 4 / 4 of 12 / 2 of 7 / 5 of 6 | 0 of 9 / 4 of 9 / 2 of 2 / none |
| meow against WHQ | 0 of 13 / 7 of 15 / 3 of 7 / 1 of 4 | 0 of 19 / 2 of 15 / 0 of 1 / none |
| our opponents (the same games from the other side) | 1 of 11 / 3 of 3 / 10 of 17 / 35 of 47 | none / none / 2 of 5 / 51 of 60 |
| top three | 4 of 31 / 4 of 16 / 26 of 42 / 73 of 85 | 1 of 12 / 14 of 35 / 73 of 127 / 71 of 99 |
| top three against test4 and WHQ | 0 of 3 / 1 of 2 / 4 of 6 / 4 of 4 | 0 of 1 / 1 of 2 / 7 of 10 / 2 of 2 |

The same for the other footings and rounds the lead asked for (all four bands again):

| | total length at round 400, small maps | big maps | potential at round 350, small maps | big maps | potential at round 400, small maps | big maps |
|---|---|---|---|---|---|---|
| meow | 0 of 20 / 5 of 10 / 9 of 30 / 15 of 18 | 1 of 35 / 6 of 23 / 4 of 6 / 1 of 1 | 1 of 24 / 4 of 17 / 10 of 20 / 14 of 17 | 0 of 32 / 9 of 28 / 2 of 4 / 1 of 1 | 1 of 21 / 5 of 13 / 8 of 27 / 15 of 17 | 0 of 33 / 6 of 24 / 5 of 7 / 1 of 1 |
| our opponents | 2 of 12 / 1 of 6 / 21 of 30 / 25 of 30 | none / 0 of 1 / 2 of 6 / 51 of 58 | 1 of 10 / 2 of 7 / 10 of 20 / 36 of 41 | none / 0 of 1 / 2 of 4 / 51 of 60 | 0 of 10 / 2 of 7 / 19 of 26 / 28 of 35 | none / 0 of 1 / 2 of 7 / 51 of 57 |
| top three | 5 of 39 / 3 of 12 / 22 of 40 / 77 of 83 | 2 of 16 / 17 of 49 / 73 of 116 / 67 of 92 | 4 of 35 / 5 of 13 / 25 of 43 / 73 of 83 | 1 of 13 / 14 of 32 / 78 of 135 / 66 of 93 | 4 of 36 / 4 of 14 / 21 of 40 / 78 of 84 | 1 of 15 / 15 of 43 / 68 of 115 / 75 of 100 |

| all maps | total length at round 400 | potential at round 350 | potential at round 400 |
|---|---|---|---|
| meow against test4 | 1 of 15 / 5 of 13 / 4 of 13 / 7 of 8 | 0 of 14 / 6 of 19 / 4 of 9 / 7 of 7 | 0 of 14 / 5 of 12 / 6 of 17 / 6 of 6 |
| meow against WHQ | 0 of 37 / 5 of 14 / 4 of 17 / 4 of 6 | 1 of 38 / 4 of 19 / 6 of 12 / 2 of 5 | 1 of 37 / 5 of 18 / 3 of 13 / 4 of 6 |
| top three against test4 and WHQ | 0 of 5 / 2 of 2 / 9 of 13 / 8 of 10 | 0 of 4 / 2 of 4 / 11 of 13 / 6 of 9 | 0 of 5 / 1 of 1 / 9 of 13 / 9 of 11 |

The top three meet test4 and WHQ in only 30 races (19 won). Everything said about "the same opponents" rests on
those 30.

### 1b. Is A5 right that the gap is mostly the economy?

Bands of 20 games wobble, so I asked the question with all races at once. For each group I fitted one curve: the
chance of winning a race against the logarithm of own / enemy on a footing (a plain logistic fit, `y_a.py` part 6,
`y_a2.py` part 2). The curve has two numbers. The **edge** is the win chance at a ratio of exactly 1. The slope says
how fast the chance falls when behind.

| Footing | meow: win chance at ratio 1 (80% range) | top three | top three against test4 and WHQ (30 races) | meow's edge minus the top three's, in log-odds (80% range) |
|---|---|---|---|---|
| total length at round 400 (the first red team's) | 43% (36-51) | 57% (54-61) | 67% (53-78) | **-0.60 (-0.93 to -0.27)** |
| potential at round 400 | 47% (39-55) | 56% (52-59) | 64% (50-76) | -0.42 (-0.76 to -0.08) |
| total length at round 300 | 49% (40-58) | 56% (52-59) | 70% (56-81) | -0.34 (-0.67 to 0.00) |
| potential at round 300 (A5's) | 50% (41-59) | 55% (52-59) | 69% (55-80) | **-0.33 (-0.66 to 0.00)** |
| potential at round 350 (A5's) | 51% (42-60) | 56% (52-59) | 68% (54-79) | -0.32 (-0.65 to +0.01) |

Three things follow.

1. **A5's correction is real.** On total length at round 400 our deficit against the top three is 0.60 and clearly
   not zero. On a footing taken before anybody has fed it is 0.33. So 45% of the first red team's gap was the
   footing.
2. **The other 55% is still there, and its range just touches zero.** A deficit of 0.33 at level potential is the
   difference between winning 50% and winning 58%.
3. **"We win about half at level potential" is a statement about test4 and WHQ.** They are the other side of 123 of
   our 143 races, so at a ratio of 1 the two sides must share the wins. The top three do not win half against those
   two: 69% at level potential (range 55 to 80, 30 races), where we win 44% (35 to 54, 123 races).

**What the gap is worth in games.** I put our 143 races on the top three's curve, each race at its own ratio
(`y_a.py` part 7; the range in brackets is what refitting the top three's curve on resampled games gives):

| Footing | our races at the top three's conversion | gap to the 41 we won |
|---|---|---|
| total length at round 400 | 53.5 (49 to 57) | +12.5 |
| potential at round 400 | 49.9 (46 to 54) | +8.9 |
| total length at round 300 | 49.2 (45 to 53) | +8.2 |
| potential at round 300 | 49.5 (45 to 54) | **+8.5** |
| potential at round 350 | 48.9 (45 to 53) | +7.9 |
| the same with the top three's curve against test4 and WHQ only (30 races), potential at round 300 | 56.9 (43 to 69) | +15.9 |
| small maps alone / big maps alone, potential at round 300 | 33.1 of 78 / 17.7 of 65 | +4.1 / +5.7 |
| live bot alone (96 races, 27 won) | 33.1 | +6.1 |

Our own 41 is itself a draw from chance (about 5.7 wins either way, one standard deviation). Together with the
curve's range, **the race gap of its own is about +8 wins, with an 80% range of roughly 0 to +16; in points +2 (0 to
+4).** The first red team said "+10 wins, 2.7 points"; on its footing I get +12.5.

**The first red team's 30 games looked at again.** On the top three's small-map curve those 30 games would give 17.6
wins when read on total length at round 400 and 13.3 when read on potential at round 300. We won 9. So of a gap of
8.6 wins, 4.3 are the footing and 4.3 remain. A5's table inside that band is right (we were at 65.5 against 90.5 at
round 300); the conclusion "mostly" is half.

### 1c. Where the remaining gap sits

`y_a2.py` (output `y_out/a2.txt`): finer bands of own / enemy potential at round 300, all maps.

| potential ratio at round 300 | meow | top three | our races at the top three's rate | gap |
|---|---|---|---|---|
| under 0.35 | 0 of 34 | 2 of 27 = 7% | 2.5 | +2.5 |
| 0.35-0.50 | 0 of 14 | 3 of 16 = 19% | 2.6 | +2.6 |
| 0.50-0.65 | 8 of 29 | 4 of 14 = 29% | 8.3 | +0.3 |
| 0.65-0.80 | 12 of 29 | 14 of 37 = 38% | 11.0 | -1.0 |
| 0.80-1.00 | 6 of 18 | 40 of 70 = 57% | 10.3 | +4.3 |
| 1.00-1.25 | 5 of 5 | 59 of 99 = 60% | 3.0 | -2.0 |
| over 1.25 | 10 of 14 | 144 of 184 = 78% | 11.9 | +1.9 |
| all | 41 of 143 | 266 of 447 | 49.5 | +8.5 |

The gap is not one thing. Five wins sit in the races we enter with under half the enemy's potential, where we have
never won (0 of 48) and the top three sometimes do (5 of 43). Four sit in the band just under level (6 of 18 where
they win 57%). Between 0.5 and 0.8, where 58 of our races are, we convert exactly as they do. So "we lose level races
the top three win" was too simple, and so is "at level potential we win about half".

### 1d. Is potential a fair footing?

Before feeding, yes. After it has started, no; and neither is total length.

Potential counts a 2-long dragon far away as one segment for the leader. What such a pearl is really worth can be
measured: over all 1,028 sides of all race games I fitted the final longest dragon as "a times the longest now plus k
times the pearls the others would drop now" (`y_a.py` part 6):

| round | small maps: a, k | big maps: a, k |
|---|---|---|
| 300 | 0.95, 0.67 | 0.63, 0.40 |
| 350 | 0.88, 0.63 | 0.91, 0.29 |
| 400 | 1.04, 0.49 | 0.85, 0.24 |
| 450 | 1.04, 0.24 | 0.94, 0.13 |

So at round 400 a pearl still walking around in a small dragon is worth half a leader segment on small maps and a
quarter on big maps, for everybody. That is the same fact as "big maps end with 39-49% of potential in the longest".
At round 300 nobody has converted much, so every footing gives the same answer: our edge is 49% on total length, 50%
on potential and 50% on this fitted footing; the top three's is 56%, 55%, 55%. At round 400 the footings part ways:

- total length is unfair to us (the enemy has spent length on feeding, we have not): edge 43%;
- potential is unfair the other way (it counts our unfed dragons in full): edge 47%;
- the fitted footing sits between: edge 52% for us and 53% for the top three, and on it our races are worth 45.9 on
  their curve, a gap of +4.9.

Reading the last line with the +8.5 at round 300: about three or four of the eight wins are lost between rounds 300
and 400 (we start feeding at round 401 on small maps; there the longest holds 24% of our potential at round 400, the
top three's 37%, our opponents' 43%), and about five after round 400, nearly all of them in races in which we are
behind.

One more number against a habit of this study. In the level band our share moves with the footing: 8 of 20 on total
length at round 300, 11 of 23 and 12 of 24 on potential at rounds 300 and 350, 13 of 36 on total length at round
400, 9 of 28 on the fitted footing at round 400 (4 of 21 on small maps). Nobody should quote one of these alone, me
included.

### 1e. What is left of the claim

| | A5 | after the recount |
|---|---|---|
| the counts | 11 of 23, 12 of 24, 106 of 143 below 0.8 | the same, to the game |
| "total length at round 400 is a biased footing" | yes | yes: it explains 45% of the gap (0.60 to 0.33 in log-odds; +12.5 to +8.5 wins) |
| "most of the gap is not in the race" | | the economy is the larger part of why we lose races (106 of 143 start below 0.8), but a race gap of its own of about 8 wins (0 to 16) remains against the top three |
| "at level potential we win about half" | 11 of 23, 12 of 24 | true against test4 and WHQ; the top three win 69% against them at level potential (30 races) |
| where the rest is | "against the best converter" | half in races we enter under half the enemy's potential (0 of 48), half just under level (6 of 18) |

What this means for the candidates: a rule that only improves conversion in races has about 8 wins to play for
(2 points), and at most 16. A5 claims 3 to 9 games for candidate 5, which is between 40% and 110% of everything
there is.

## 2. Candidate 5: one leader, known to all

**The claim (A5's, `deep-read-5.md` section 7).** When our leader cuts itself, the new dragon (the heir) has a new
id. Every team-mate's record still names the old id for a median of 27 rounds, because a longer, older report
outranks a fresher, slightly shorter one. Feeding stalls meanwhile: the longest grows 5.0 per 25-round window with
a cut against 10.8 without. And a quarter of our deaths by choice happen next to no bigger dragon. The rule: fresher
news of a nearly-as-long dragon replaces older news of a longer one; seeing a dragon corrects its recorded length; a
feeder dies only next to a leader it can see is long. Three changes in the record code. Claimed: +0.7 to +2.2
points, "most likely a little over +1" (strict 6 to 12 games of 401, realistic 3 to 9).

**The strongest argument against it, as its opponent would put it.** "The 27 rounds were read off 82 games of a bot
we no longer run. In the builds we run today the leader is fed at its usual rate again 10 to 20 rounds after a cut,
and in the test builds after 5 to 10. The famous 5.0 against 10.8 is half arithmetic: a window with a cut in it has
lost 2 segments per cut by definition, and the window right after a cut, which a 25-round blindness would have to
hit, grows 11.4. On the smaller maps, where the close races are, the heir of a cut grows as fast as Vibing++'s. What
is left is feeders that die for the 2-long stub: one death in thirteen, about four pearls a race. For that the
candidate rewrites the one piece of shared memory the team has, with an age rule that, as written, lets the old
report win again on the very next ping, and that will crown the second dragon in every region where news of the
first is old; our two longest dragons are within 12 segments of each other in most of our races. Per pearl we
already convert as well as test4 and WeHaveQuizzes."

What is left after the attacks below: the mechanism exists, the code reading is right in its main lines, and two of
the three changes are harmless. Its worth is about a third of what is claimed, and the first change needs rewriting
before it does anything. I would defend **-0.3 to +0.8 points, most likely +0.2 to +0.4** (1 to 5 games of 401 on
the strict reading).

### A. The counts

Scripts `y_c5a.py`, `y_c5b.py`, `y_c5c.py` (outputs `y_out/c5a.txt`, `c5b.txt`, `c5c.txt`). Everything that needs
no ping is counted on all games; the belief numbers on the 82 games with readable pings.

| | theirs (A5) | mine |
|---|---|---|
| leader cuts per race from round 395, live bot, small / big maps | 3.8 / 3.9 | 3.9 / 4.0 (test builds 4.4 / 4.5) |
| ... made with a free cell left | 68% / 67% | 66% / 66% |
| ... our opponents; forgot; SSS; Vibing++ (small maps) | 2.3; 4.1; 2.0; 2.6 | 2.6; 4.2; 2.3; 2.7 |
| cuts of the final lineage from round 400, per race: all / with a free cell | 2.7 / 1.7 | 2.7 / 1.7 |
| lost races in which the segments left in those cuts exceed the margin | 10 of 102 (7 by free-cell cuts alone) | 10 (6) |
| growth of the longest per 25-round window from round 400, 10+ other own dragons: a cut in it or in the 25 rounds before / none | 5.0 (291 windows) / 10.8 (91) | 5.0 (294) / 11.1 (88) |
| ... live bot / test builds | 4.5, 11.4 / 6.1, 9.3 | 4.4, 11.9 / 6.1, 9.3 |
| ... against test4 / WHQ / others | 4.9, 11.4 / 5.5, 10.9 / 3.7, 9.6 | 4.7, 12.5 / 5.5, 10.9 / 3.7, 9.6 |
| ... small / big maps | 6.0, 12.4 / 4.3, 8.7 | 6.0, 12.6 / 4.2, 9.2 |
| ... our opponents | 6.0 (216) / 6.9 (156) | 5.9 (219) / 7.0 (153) |
| deaths by choice in races, rounds 300-499, next to no own dragon twice as long within 8 path steps, live bot small / big | 26% / 20% | 27% / 20% (test builds 26% / 16%) |
| ... our opponents; forgot; SSS; Vibing++ | 15 / 11; 8 / 5; 10 / 6; 14 / 10 | 15 / 11; 8 / 5; 10 / 6; 15 / 10 |
| pearls of those deaths eaten by the final lineage, live bot small / big | 36% / 27% | 36% / 26% |
| ... by where the death was: next to the longest / next to nothing, small maps | 70% / 13% | 71% / 11% |
| games with readable pings | 78 | 82 (24 + 31 + 27); 25 of them races, 12 won |
| rounds until half of our dragons name the true longest after a cut: quartiles | 17 / 27 / 36-41 (388 cuts) | 14 / 28 / 46 over 370 cuts; after 88 more cuts it never happens before the game ends |
| samples in rounds 400-494 in which under a quarter name the true longest | 187 of 347 | 211 of 429 |
| growth of the longest in the next 5 rounds: under a quarter name it / a quarter to a half / a half to three quarters / more | +0.42 / +1.85 / +1.51 / +2.00 | +0.40 / +2.06 / +2.10 / +2.10 |
| share of own dragons naming a longest dragon, small maps, rounds 400-424 | 37% | 39% |

**The counts reproduce.** The small differences are definitions (I call a split a leader cut when the dragon was at
least as long as every other own dragon at that moment; I find four more readable games).

### B. Cause or consequence

This is where the candidate is weakest. Five checks, each made so that a stale record would have to show.

**1. Where in time the missing growth sits** (`y_c5a.py` part 2). A5 pools "a cut in the window or in the 25 rounds
before". Split in two:

| growth of the longest per 25-round window (windows) | a cut INSIDE the window | a cut only in the 25 rounds BEFORE | no cut in 50 rounds | inside, with 2 segments per cut given back |
|---|---|---|---|---|
| meow, all races | 3.0 (225) | **11.4 (69)** | 11.1 (88) | 7.0 |
| meow live bot | 2.5 (147) | 10.0 (50) | 11.9 (63) | 6.6 |
| meow test builds | 3.9 (78) | 14.9 (19) | 9.3 (25) | 7.8 |
| meow, earlier bot (readable pings) | 1.5 (37) | 7.1 (14) | 9.7 (23) | |
| our opponents | 4.2 (142) | 8.9 (77) | 7.0 (153) | 7.5 |
| WHQ / test4 (against us) | 3.2 / 5.2 | 10.0 / 7.4 | 7.3 / 8.1 | 6.5 / 8.3 |
| SSS small / big | 1.4 / 1.4 | 4.1 / 5.4 | 6.3 / 6.7 | 5.9 / 4.6 |
| forgot small / big | 8.2 / 3.3 | 11.6 / 5.2 | 5.3 / 4.6 | 12.2 / 6.1 |
| Vibing++ small / big | 6.9 / 3.1 | 10.8 / 7.1 | 5.7 / 8.2 | 10.2 / 5.8 |

- A window that comes right after a cut and has no new cut in it grows as fast as a window with no cut at all:
  11.4 against 11.1. Inside the same game the difference is +0.8 segments (standard error 1.5, 30 games). A blindness
  of 25 rounds after every cut would fall into exactly these windows. It shows only in the earlier bot (7.1 against
  9.7).
- The whole deficit is in windows that contain a cut. Half of it is the cut: such a window holds two cuts on
  average, 2 segments each. With those given back our windows are at 7.0 against 11.1. For our opponents, test4,
  WHQ and SSS on small maps the same sum closes the gap (7.5 against 7.0, 8.3 against 8.1, 6.5 against 7.3, 5.9
  against 6.3). So about 4 segments per such window are missing in our games beyond the cut itself, and that part is
  ours.

**2. The clock after a cut** (`y_c5a.py` part 4, `y_c5f.py`). Deaths by choice within 3 steps of the team's longest
dragon, per 100 team-rounds, by rounds since the team's last leader cut (rounds 400-499 of races, teams with 10+
other dragons). If a record that runs out after 25 rounds held the feeders back, the rate would stay low until 25
and jump.

| rounds since the cut | 0-4 | 5-9 | 10-14 | 15-19 | 20-24 | 25-29 | 30-39 | 40-59 |
|---|---|---|---|---|---|---|---|---|
| meow, earlier bot (25 races) | 3.4 | 9.1 | 8.6 | 13.3 | 22.0 | 25.0 | 26.9 | 22.8 |
| meow, live bot with sealed pings (71) | 6.3 | 9.0 | 11.0 | 20.7 | 22.7 | 21.6 | 30.0 | 37.6 |
| meow, test builds (47) | 6.6 | 16.6 | 25.9 | 24.3 | 26.6 | 31.0 | 16.8 | 23.8 |
| ... deaths next to a stub of the last 26 rounds, live bot | 8.2 | 6.6 | 3.4 | 3.0 | 3.3 | 3.0 | 0.6 | 0.2 |
| our opponents | 6.6 | 9.9 | 8.9 | 11.9 | 7.8 | 10.4 | 8.7 | 6.6 |
| forgot, small maps | 10.5 | 17.1 | 11.7 | 14.4 | 12.2 | 20.0 | 15.5 | 16.1 |
| SSS, small maps | 5.9 | 8.6 | 11.6 | 14.3 | 13.6 | 13.3 | 21.6 | 32.7 |
| Vibing++, small maps | 9.5 | 10.4 | 9.8 | 14.1 | 12.9 | 14.0 | 9.6 | 11.3 |

- The earlier bot does look like a clock: low for 20 rounds, then up. That is the bot the belief numbers come from.
- Today's live bot is back at its usual rate after 15 rounds, the test builds after 10. Something that changed
  between the builds shortened the stall; the pings of those builds are sealed, so I cannot see what (section 6).
- In the first five rounds after a cut more of our feeders die next to the stub (8.2) than next to the heir (6.3).
  That part of A5's story is exact.
- Our rate when nothing is wrong (22 to 30) is two to three times anybody else's, because we feed everything in the
  last hundred rounds. Even 5 to 14 rounds after a cut our leader is fed as fast as WHQ's or Vibing++'s ever is.

**3. The heir itself** (`y_c5g.py`, from the walk `y_w2.py`). Its length t rounds after a leader cut made from
round 395, over the cuts still followed at t (the heir alive and not cut again):

| heir's growth after | 5 rounds | 10 | 15 | 25 |
|---|---|---|---|---|
| meow, earlier bot | +0.5 | +1.2 | +2.9 | +3.6 |
| meow, live bot (sealed), small maps | +0.9 | +2.1 | +2.2 | +4.6 |
| meow, test builds, small maps | +0.7 | +1.5 | +2.8 | +8.6 |
| meow, live bot (sealed), big maps | +0.2 | -0.1 | **-1.3** | +1.1 |
| meow, test builds, big maps | +0.4 | +0.6 | +1.1 | +0.1 |
| forgot, small / big maps | +2.1 / +1.7 | +4.2 / +3.2 | +6.1 / +3.7 | +8.9 / +5.9 |
| SSS, small / big | +0.1 / +0.7 | +0.6 / +2.6 | +1.5 / +4.1 | +3.3 / +6.9 |
| Vibing++, small / big | +1.3 / +1.4 | +2.4 / +2.7 | +3.3 / +3.5 | +6.1 / +5.9 |
| test4 (against us), big maps | +0.6 | +0.3 | +1.4 | -1.3 |

On small maps the heir of today's live bot grows like Vibing++'s and faster than SSS's. **The stall is a big-map
thing**: there our heir is no longer after 20 rounds than at birth, where a top team's has gained 5. test4 has the
same problem on big maps. Our big-map races are lost by a median of 44 segments, so that is not where 5 segments
decide much.

**4. What the feeders near a cut do** (`y_c5b.py` part 5). For every leader cut from round 395 I followed the own
dragons that could feed the heir (at most half its length, within 15 cells of the heir's or the stub's head) for 25
rounds, for the cuts after which the heir did not cut again:

| of those dragons, within 25 rounds | meow live | meow test | our opponents | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|
| died by choice within 3 steps of the heir | 14% | 17% | 13% | 15% | 16% | 8% |
| ... of the stub | 2% | 1% | 0% | 0% | 0% | 1% |
| ... of another own dragon twice their length | 10% | 15% | 12% | 10% | 5% | 4% |
| ... of none of these | 10% | 8% | 11% | 7% | 2% | 9% |
| alive and 3+ cells nearer the heir / nearer the stub / neither | 13 / 4 / 32% | 10 / 0 / 26% | 9 / 1 / 30% | 7 / 1 / 29% | 15 / 5 / 35% | 9 / 3 / 32% |
| of the deaths next to the heir: in the first 10 rounds | 40% | 40% | 63% | 66% | 61% | 62% |

Within 25 rounds as many of our nearby feeders die next to the heir as in any other team. They do it later: 40% in
the first ten rounds against 61-66%. That is a delay of some rounds, made up inside the same 25 rounds. It turns
into a loss when the heir cuts again first, and ours does that sooner than anybody's: 42% of our heirs cut again
within 10 rounds (our opponents 30%, forgot 29%, SSS 37%, Vibing++ 24%). Only 67 of the live bot's 316 leader cuts
from round 395 were followed by 25 quiet rounds.

**5. The pings themselves** (`y_c5e.py`; 196 leader cuts of the earlier bot from round 300 with 4 or more feeders
near). Share of the nearby feeders naming:

| rounds after the cut | 1 | 5 | 10 | 15 | 20 | 25 |
|---|---|---|---|---|---|---|
| the heir | 0% | 4% | 10% | 18% | 30% | 44% |
| the stub | 31% | 37% | 35% | 29% | 22% | 17% |
| another living dragon | 40% | 35% | 42% | 44% | 36% | 28% |
| a dead dragon | 28% | 24% | 14% | 8% | 11% | 11% |

So in the earlier bot A5's mechanism is there to be seen: the heir is named slowly, the stub for a long time. But
look at round 1. **Only 31% of the feeders standing near the leader named it before the cut.** Two thirds named
somebody else or a dead dragon. The team's record is poor at all times, not only after a cut. The same shows in the
growth numbers: in samples with no leader cut at all so far, the longest grows +0.16 per 5 rounds when under a
quarter of the team names it (19 samples) and +2.42 when more do (26). "The team knows its leader" predicts growth,
which is close to saying the same thing twice; "the team forgets it at a cut" is one of several ways of not knowing.

A cut-by-cut comparison of fast and slow naming inside the same game, which the lead asked for, cannot be made: 25
cuts of the earlier bot were followed for 15 rounds after round 395, in 5 of them a quarter of the feeders named the
heir by rounds 5-10 (heir +2.6 in 15 rounds) and in 20 they did not (+2.4). No difference, and no power.

**What the feeders die next to** (`y_w4.py`, `y_c5c.py`; all 4,677 "no order" deaths of ours in races, rounds
300-499). Our bot lets a feeder die when the head of the dragon in its record is in view and within 3 cells in a
straight line. So every death has a target:

| the feeder died for | share | small / big maps | the final lineage ate, of its pearls |
|---|---|---|---|
| the true longest, 3 path steps or fewer away | 42.9% | 54.1 / 34.2% | 66% |
| the true longest, but a wall between (over 3 path steps) | 5.4% | 8.5 / 3.1% | 16% |
| another own dragon at least twice its length | 39.4% | 25.1 / 50.5% | 10% |
| the stub of a cut made in the last 26 rounds | 7.6% | 7.4 / 7.7% | 12% |
| another dragon under twice its length | 4.7% | 4.9 / 4.5% | 8% |

A5's "a quarter die next to no bigger dragon" (which I reproduce with its path-step test) is three different things.
What candidate 5 would stop is the last two rows: **12.3% of feeder deaths, 6.1 pearls a race**, of which the
lineage gets 0.7 today and would get 4.0 if every one of those feeders died next to the true longest instead. One
row is new and is not in the candidate: 5% of our feeders (8.5% on small maps) die within 3 cells of the right
dragon on the wrong side of a wall, because the test counts cells and not steps. And the largest row by far is the
third: four deaths in ten go to a big dragon that is not the longest. The team's log calls that "regions elect
local leaders". Candidate 5 does not work on it.

### C. What happens next

- **The delay is mostly made up; the misdirected pearls are not.** Per race: 4.2 pearls dropped for a fresh stub,
  1.9 for a dragon under twice the feeder's length, 2.8 across a wall, 16.7 for another big dragon.
- **No pile of unused feeders next to our leader at the end.** At the end of a small-map race the live bot has own
  dragons worth a median of 8 pearls within 15 cells of its longest (our opponents 5, forgot 7, SSS 5, Vibing++ 10)
  and 7 units left (4 to 8). On big maps everybody's unfed length is far away (ours 43 pearls beyond 15 cells, the
  others 39 to 86).
- **In the last hundred rounds we convert as fast as anybody.** The longest holds 24% of our potential at round 400
  and 65-71% at the end on small maps; our opponents go from 43% to 77%, the top three from 37% to about 69%.
- **The live bot's leader does grow less after round 400**: 10 on small maps and 14 on big against 15.5 to 24 for
  the others. The test builds grow 21 on small maps. Which change did that is not known; none was in the leader
  code. Whatever candidate 5 repairs, part of it seems to be repaired already in the builds that were tested and
  not released.

### D. Sample size

- Belief: 82 games of the earlier bot, 25 of them races. Leader cuts from round 395 in those races with 25 quiet
  rounds after: 8. Everything said about what dragons "name" rests on that bot.
- All games: 143 races, 589 leader cuts from round 395 (483 with 10+ other dragons), 4,677 feeder deaths. The
  position-only measures (windows, clock, heir growth, targets of feeder deaths) are solid and hold against test4
  and against WHQ separately (windows with a cut inside 2.5 and 3.9, none 12.5 and 10.9).
- Close races: our lost races have margins of 1, 1, 2, 5, 5, 6, 6, 6, 7, 7, 9, 11, ... (median 32.5). Ten games
  decide every strict count in this section.

### E. Cross-team

- **forgot, Vibing++ and WHQ do feed through a cut**: flat clocks, heirs that gain 2.4 to 4.2 in ten rounds.
- **SSS on small maps stalls more than we do** (clock 5.9, 8.6, 11.6 against a later 22 to 33; heir +0.6 after ten
  rounds and +3.3 after 25; windows 1.4 / 4.1 / 6.3) **and is not worse for it**: it wins 23 of 42 small-map races,
  ends with 79% of its potential in the longest, and wins 55% at level potential at round 300 (forgot 56%). SSS cuts
  less often (2.3 leader cuts a race from round 395, ours 3.9) and its feeders die one step from the head. On big
  maps SSS has no stall.
- So a top team with the stall exists and is level with the two that have none. The number that sets us apart from
  all of them is how often our leader cuts and how soon it cuts again, which the candidate leaves alone.

### F. Earlier experiments

From `work/plan.md`:

- **`FEED_LOCAL`** (in the feeding phase a dragon dies next to any visible own head within 2-3 steps that shows
  twice its length): 70, 74 and 69 wins of 152 locally where the base won 76. Rejected. It lowers the bar for whom to
  die next to; candidate 5 raises it. It tells us that feeding local big dragons more does not help, which fits the
  10% the lineage gets of such pearls.
- **"Refuse to feed a leader much shorter than the max leader length ever heard"**: written down as the next step
  on 30 September after three local games in which 24 of 37, 18 of 25 and 29 of 42 feeds went to a non-top leader.
  Never run. It is close to the candidate's third change.
- **Regional leaders**: the team's own note: "Regions on the maze and portal maps elect local leaders because sonar
  is blocked, so feeding fragments." My count agrees: 39% of feeder deaths.
- **Rally** (`RALLY_FRESH`, far dragons walk to the leader): queued, no result in the log.

Nothing in the log contradicts candidate 5 and nothing tests it.

### G. Backfire

- **Regional leaders.** An age rule makes old news of a long dragon lose against fresh news of a shorter one. With
  the proposed 0.5 segments per round and news up to 25 rounds old, any dragon within 12 segments of the leader can
  win a region. Our longest and second longest are within 12 segments in 92%, 66%, 60% and 44% of the live bot's
  small-map races at rounds 400, 425, 450 and 475 (within 5 segments in 58%, 32%, 16%, 20%), and in 71%, 66%, 66%,
  52% on big maps (`y_c5d.py` part 2). The top teams' two longest are much farther apart (SSS's median gap is 18 to
  34 segments, ours 5 to 14). Every feeder death that moves from the longest to another big dragon costs the
  lineage 0.56 of each pearl, and that row is already 39%.
- **The "see it is long" test stops good deaths too.** As written (the feeder must have min(twice its length, 6)
  segments of its target in its view) it would stop the 12% it is meant to stop, and also **28% of today's deaths
  next to the true longest** (628 of 2,263; `y_w4b.py`, `y_c5d.py` part 4), because a feeder three cells in front
  of a head sees little of the body behind it. Those feeders would have to come closer first. A plain "at least 4
  segments in view" would do the same job at less cost; I did not count that variant.
- **Feeders that no longer die** are alive at round 500. The end-state numbers above say we have room for that
  (our leftovers near the leader are ordinary), but it is a cost of the third change, not a gain.
- **A leader that is followed by nobody for a while.** With the age rule as written the record flips between the
  heir and the old id from ping to ping (item H). A feeder that changes its mind every turn walks to neither. Today
  it at least walks to one of them.
- **We have more close wins than close losses.** On small maps 8 of our 29 race wins were won by 5 segments or
  fewer and only 2 of our 49 losses were lost by as little. A change that shifts the final longest by a few
  segments in both directions from game to game has more to lose there than to win.

### H. The code claim

Read: `observe()`, `hear_exact()`, `hear_sighting()`, `leader_priority()`, `expire_leader()`,
`plausible_report()`, `hear_sonar()`, `broadcast_leader()`, `pick_feed_target()`, `feed_len_ok()`, `ready_to_die()`,
`beside_visible_leader()`, `compute_drop_cells()`, `refresh_leader_zone()`, `escape_child_size()`, `is_leader()`.

- **A5's description of the record is right.** A report about the id held replaces it when it is as fresh or
  fresher, also when shorter. A report about another id wins on length alone; age only breaks ties. A sighting can
  raise the recorded length and never lowers it. A record is dropped 26 rounds after its last exact news. In the
  turn of a cut the leader first writes "my id, full length, this round" into its record, then splits, then sends
  that record, so the stale report is stamped with the round of the cut and lives for 25 rounds. Every team-mate
  repeats it on four rays each turn, and a dragon that had learned better takes it back, because for another id only
  the length counts.
- **Change 1 as written does not do what is claimed.** The proposed line is `mine = priority(record) -
  LEADER_AGE_COST * max(0, when - known_leader_round)`: the held record is marked down when the incoming report is
  fresher. Nothing marks the incoming report down when it is the older one. A dragon that has just taken "heir, 32,
  now" and then hears a team-mate repeat "old id, 34, round of the cut" compares 34 with 32 and switches back. Which
  of the two it holds when it decides whom to feed depends on the order of the pings in that turn. The rule has to
  price age on both sides (compare length minus cost times age for both reports), and it then also applies to the
  dragon's own length, which every dragon feeds into its record at the start of each turn: a dragon within 12
  segments of a leader it has not heard from directly for 25 rounds would make itself leader, stop being a feeder
  and get the leader's rules. That is the regional split of item G, inside the rule.
- **The cut itself** is as A5 says: `escape_child_size()` gives the child `length - 2` when the best move leads
  into a pocket of 4 cells or fewer that does not reach the own tail, or when there is no move at all; the queen is
  exempt from the early kind. Any dragon of 4 or more does it, not only the leader.
- **Change 2** (a dragon that sees the whole body of the id in its record corrects the length and remembers that
  correction) is sound and local. It fixes the stub for those who see it.
- **Change 3** is sound in direction; its threshold is too strict (item G).
- **Three things A5 does not say.** (a) The first half of `ready_to_die()` can hardly ever fire: the drop cells lie
  4 to 8 cells ahead of the leader's head and one to the side, and from there the head is outside the feeder's 7x7
  view, which that half requires (a portal in between aside). Our feeders die by the second half,
  `beside_visible_leader()`: head in view, within 3 cells counted straight, walls ignored. That is where the 5%
  deaths across a wall come from. (b) The heir is a new dragon with an empty record. It hears "old id, longer" like
  everybody else, so for up to 25 rounds it does not
  count itself the leader: it does not get the leader's fourfold pearl weight during feeding, and the pearl zone
  around its own stub applies to it. This is my inference from the code; it fits the heir that does not grow on big
  maps. (c) `sonar_enabled` is false on a map wider or taller than 128 cells; no known map is, but it is the one
  map-size condition in the record.
- No toggle exists for any of the three changes. No map-size condition is in them.

### I. The size

A5's own what-ifs recount within one or two games (growth after round 400 times 1.25 / 1.5 / 2: theirs 6 / 12 / 18
lost races that turn, mine 5 / 10 / 17; our final longest +5 / +10 / +15: theirs 4 / 11 / 20, mine 3 / 11 / 20). The
question is which factor to believe. A5 takes "a quarter to a half more growth" from the window contrast. Section
B says half of that contrast is the cut itself and the rest is a delay that is mostly made up. So I derived the size
from what can be counted as lost (`y_c5d.py` part 3). For each of our 102 lost races: the pearls of feeders that
died for a fresh stub or for a dragon under twice their length, what the final lineage got of them, and what it
would have got at the rate of deaths next to the true longest (66%); never above 0.9 of our final potential; the
enemy unchanged.

| Reading | lost races that turn (of 401 games) | live bot | mean gain per lost race |
|---|---|---|---|
| strict: every such pearl reaches the true longest; plus 1.2 segments for every leader cut after round 470 (feeders held back when the game ends) | 5 | 5 | 4.6 segments |
| middle: the stub pearls reach it, half of the others | 2 | 2 | 2.7 |
| cautious: half of the stub pearls reach it | 1 | 1 | 1.1 |
| for scale, not this candidate: the feeders that died across a wall die next to the longest instead | 2 | 2 | 0.9 |

The big-map stall of item B3 adds little to this: up to 5 segments per quiet cut, in races lost by a median of 44.
So: **strict 1 to 5 games of 401 (+0.25 to +1.25 points); with the usual halving for an enemy that answers and
feeders that do not find the leader, about 1 to 2.5 games (+0.2 to +0.6 points).** Against it stands a real chance
of harm from the age rule (regional leaders) and from the strict "see it" threshold, of about the same size. My
range: **-0.3 to +0.8 points, most likely +0.2 to +0.4**, against A5's +0.7 to +2.2.

### What is left of the claim

| | A5 | after the attacks |
|---|---|---|
| the counts | 5.0 against 10.8; 26% / 20%; 27 rounds | all reproduce |
| "feeding stalls for about 25 rounds after a cut" | from the window contrast and the pings of the earlier bot | true of the earlier bot; 15 rounds in today's live bot, 5 to 10 in the test builds; on small maps today's heir grows like Vibing++'s; the window after a cut grows 11.4 against 11.1 |
| "a quarter of our feeders die next to nothing" | 26% / 20% | 12% die for a stub or a short dragon (what the rule stops), 5% across a wall, 39% for another big dragon (the largest loss; not addressed) |
| the three changes | do what is claimed | the second yes; the third yes but it also stops 28% of the good deaths; the first not as written, and with the repair it invites regional leaders |
| games | strict 6 to 12, realistic 3 to 9 | strict 1 to 5, realistic 1 to 2.5 |
| points | +0.7 to +2.2, "a little over +1" | **-0.3 to +0.8, most likely +0.2 to +0.4** |
| what it leaves alone | the cut itself | and that is the larger number: our leader cuts 3.9 to 4.5 times a race from round 395 (others 2.3 to 2.7, forgot 4.2) and its heir cuts again within 10 rounds in 42% of cases |

## 3. Candidate 3z: nobody leaves a pearl lying for the leader

**The claim (the lead's).** From the switch round on (150 on big maps, 300 on small) our small dragons must not take
pearls within 9 cells of the leader in their record. The rule: remove that zone on every map (radius 0) and change
nothing else. The case: (i) after the switch a small dragon of ours takes a free pearl next to it in 49-56% of turns
instead of 80-85%, exactly at our switch, in every run, and no other team's rate moves; (ii) by its own belief it
takes such a pearl in 18-26% of turns inside its leader's zone and in 75-87% outside; (iii) the leader gets nothing
from it; (iv) the team's natural intake falls by a quarter on small maps and a third on big; (v) the big-map leader
that wins our big-map games is built by feeding, not by the zone. No size was put on it.

**The strongest argument against it, as its opponent would put it.** "Three times this team has raised its economy
and three times the wins did not come: stride, +14% locally; the trade build, +21% length at round 300 on big maps
and 0 wins of 12; the switch moved to round 300 on big maps, flat in three local runs. On big maps, where this rule
changes most, we sit at 0.45 of the enemy's length; a third more leaves most of those games in the band in which we
win one game in fourteen. On small maps races are decided by one dragon, and the zone is the one rule that keeps
small dragons off the pearls our feeders drop for it: the dragon that ends as our longest eats 3.4 corpse pearls and
2.4 natural pearls a race that a small dragon had declined, and 7 of our 41 race wins were closer than that. We have
six race wins within 3 segments on small maps and two losses within 5. This rule spends the leader to buy length
nobody has shown we can use."

What is left after the attacks below: supports (i), (ii) and (iv) hold, more sharply than stated; (v) holds;
(iii) does not hold for the pearls of feeders late in the game. The economy gain is large and well identified. The
win gain is inferred. As defined, the rule gains on big maps and risks close wins on small maps; with feeder pearls
kept reserved once feeding has started the risk goes and the gain stays. I would defend **+0.3 to +2 points, most
likely about +1**.

### A. The counts

Walk `y_w3.py`; tables `y_c3a.py`, `y_c3b.py`, `y_c3c.py`, `y_c3d.py` (outputs `y_out/c3a.txt` to `c3d.txt`).

**(i) The free-pearl rate around our switch round** (share of pearl turns taken):

| maps over 1,200 cells, rounds | 130-139 | 140-149 | 150-159 | 160-169 | 170-199 | 200-299 | 300-399 |
|---|---|---|---|---|---|---|---|
| meow live bot (theirs: 84, 84, 64, 60, 58) | 84% | 84% | **64%** | 60% | 60% | 58% | 57% |
| meow test builds | 82% | 79% | 62% | 54% | 60% | 56% | 60% |
| our opponents | 86% | 86% | 85% | 85% | 84% | 85% | 84% |
| forgot / SSS / Vibing++ | 93 / 84 / 90% | 93 / 84 / 90% | 93 / 82 / 89% | 93 / 83 / 89% | 93 / 83 / 90% | 93 / 83 / 89% | 94 / 82 / 82% |

| maps of 1,200 cells or fewer, rounds | 280-289 | 290-299 | 300-309 | 310-319 | 320-349 | 350-399 | 400-449 |
|---|---|---|---|---|---|---|---|
| meow live bot (theirs: 85, 83, 64, 51) | 85% | 83% | **64%** | 51% | 51% | 53% | 45% |
| meow test builds | 86% | 85% | 60% | 50% | 55% | 55% | 48% |
| our opponents | 81% | 81% | 82% | 80% | 79% | 76% | 71% |
| forgot / SSS / Vibing++ | 91 / 82 / 89% | 91 / 82 / 89% | 92 / 81 / 90% | 92 / 81 / 89% | 91 / 79 / 89% | 91 / 80 / 87% | 92 / 77 / 79% |

Each of our eleven runs shows the step (in the 20 rounds after the switch every run is between 44% and 81%, down
from 68-94% in the 20 rounds before). **Reproduced to the point.**

**(ii) By the dragon's own belief** (82 games with readable pings; natural pearls; the zone head is the head of the
id the dragon named one turn before if that head is in its view, else the position it named):

| | small maps, rounds 250-299 | 300-349 | 350-399 | big maps, rounds 100-149 | 150-199 | 200-249 |
|---|---|---|---|---|---|---|
| pearl inside the named leader's zone (theirs after the switch: 26 / 22% and 24 / 19%, all pearls) | 88% | **21%** | 20% | 85% | **25%** | 22% |
| outside it (theirs 87 / 87% and 77 / 77%) | 90% | 89% | 86% | 78% | 75% | 77% |
| the dragon names itself | 90% | 70% | 66% | 92% | 83% | 63% |
| by cells from the pearl to the named zone head: 0-3 / 4-6 / 7-9 / 10-12 / 13-16 / 17+ | 90 / 85 / 86 / 84 / 91 / 93% | 35 / 16 / 19 / **81** / 92 / 96% | 29 / 18 / 20 / 74 / 95 / 96% | 90 / 85 / 79 / 84 / 83 / 72% | 24 / 21 / 31 / **70** / 76 / 79% | 25 / 22 / 21 / 76 / 71 / 79% |

The last row is the cleanest picture in this study: a step between 9 and 10 cells, after the switch and not before.
With all pearls counted, as A5 did, I get 28% and 26% inside on small maps (theirs 26% and 22%).

Two things A5 does not give. Inside-zone turns are **51-56% of all pearl turns on small maps** and 33-38% on big
maps. And the zone of the TRUE longest dragon holds far fewer (32% and 14%), with a much weaker contrast (34% against
55% on small maps). The zones our dragons obey are mostly somewhere else: around the last known place of an id that
is dead or short (section 2: under 40% of our dragons name a longest dragon at any time). Half of what the zone
forbids is forbidden around nobody.

**(iii) What happens to a pearl left in the zone** (pearls a small dragon of ours declined on a pearl turn; readable
games, natural pearls, inside the decliner's own named zone):

| | small maps 300-349 | 350-399 | big maps 150-199 | 200-249 | 250-299 |
|---|---|---|---|---|---|
| such pearls a game | 3.3 | 3.3 | 5.7 | 2.6 | 2.6 |
| eaten in the end by a leader (theirs 12 / 11% and 7 / 17 / 6%) | 26% | 17% | 13% | 11% | 17% |
| by another own dragon of 8+ | 2% | 0% | 2% | 11% | 2% |
| by an own dragon under 8 (theirs 69 / 73% and 69 / 58 / 72%) | 68% | 75% | 70% | 67% | 62% |
| by the enemy (theirs 6 / 2% and 13 / 8 / 12%) | 5% | 4% | 14% | 12% | 17% |
| never | 0% | 5% | 0% | 0% | 2% |
| median rounds until eaten (theirs 9 / 8 and 10 / 7 / 10) | 10 | 8 | 11 | 11 | 10 |
| rounds a tile was blocked by them, summed per game | 45 | 61 | 93 | 44 | 51 |

My "leader" is wider than A5's (the team's longest at that round, or the longest when the pearl was declined, or
the id the decliner named), hence 17-26% against 11-12% on small maps. Either way two thirds go to another small
dragon of ours ten rounds later. The leader's own natural intake does not rise at the switch: 3.2, then 3.2 and 2.2
per 50 rounds on small maps; 4.1, then 3.8, 2.5, 2.4 on big maps (theirs 1.7 to 1.6 and 4.0 to 3.4; theirs are per
game over all games, mine over the games that last through the comparison).

**(iv) The team's natural intake** (per 50 rounds, the same games throughout; `y_c3b.py` part 2):

| | before the switch | first 50 rounds after | next 50 | the other side of the same games |
|---|---|---|---|---|
| small maps, live bot, 99 games that reach round 400 (theirs 20.8 to 15.6, -25%) | 39.5 | 31.0 (-22%) | 29.4 | 51.4, 48.7, 44.4 |
| ... our dragons of 2-4 alone | 36.0 | 26.0 | 23.8 | |
| small maps, test builds, 44 games | 42.2 | 33.6 (-20%) | 35.2 | 51.1, 48.0, 43.1 |
| big maps, live bot, 75 games that reach round 300 (theirs 79.5 to 52.7, -34%) | 81.1 | 54.0 (-33%) | 47.1 | 130.6, 130.8, 127.8 |
| ... our dragons of 2-4 alone | 62.2 | 36.1 | 32.0 | |
| big maps, test builds, 34 games | 78.0 | 48.4 (-38%) | 43.8 | 133.4, 132.6, 133.4 |

In 25-round steps, per 100 dragon-rounds of small dragons, so that a falling unit count cannot be the reason
(`y_c3c.py` part A):

| | 3 steps before | 2 | 1 | 1 after | 2 | 3 | 4 |
|---|---|---|---|---|---|---|---|
| small maps, ours (live bot) | 3.16 | 3.20 | 3.15 | **2.41** | 2.69 | 2.53 | 2.84 |
| ... the other side's small dragons | 2.75 | 2.63 | 2.77 | 2.65 | 2.67 | 2.86 | 2.59 |
| big maps, ours (live bot) | | 2.97 | 2.81 | **1.78** | 1.76 | 1.82 | 1.91 |
| ... the other side's | | 4.04 | 3.61 | 3.52 | 3.26 | 3.17 | 3.21 |

By map (natural pearls per 50 rounds before the switch, and in the two blocks after): weakhold 31.6, 14.0, 12.2
(the other side -18%); Islands 61, 28, 19; Slithery Fight 133, 87, 83 with our units steady at 51 to 57; Around
UNSW 78, 58, 57 with units steady; Maze 59, 47, 50 with units steady; Australia 46, 36, 26; Trauma 21, 15, 12.
Only Portals and Default show no fall beyond the other side's. The fall does not follow the zone's share of the
board (181 cells are 35% of Portals, 30% of weakhold, 16% of Maze, 11% of Slithery Fight, 4% of Around UNSW); it
follows whether the named leaders sit where the food is.

Our total length through the switch, on the same games: small maps 60, 61, 61, 62 at rounds 250, 300, 350, 400
(the other side 95, 99, 99, 95); big maps 109, 126, 125, 122, 122 at rounds 100, 150, 200, 250, 300 (the other
side 152, 207, 260, 300, 327). We stop growing at the switch on both.

**(v) What builds the leader of our big-map wins** (`y_c3c.py` part B; the lineage of the final longest in our 12
big-map race wins, pearls per 50 rounds from round 150 to the end): pearls of own dragons dead by choice 0.0, 2.9,
4.7, 5.0, 6.0, 20.8, 11.2; natural pearls about 2 to 4 throughout. Feeding from round 200 builds it. A5 is right.

### B. Cause or consequence

**How much of the fall is the zone?** Two measures, both on the dragon's own named zone (readable games).

1. *The rate.* If every in-zone pearl turn were taken as often as an out-of-zone turn of the same rounds, the
   free-pearl rate would be 83% and 82% in rounds 300-349 and 350-399 on small maps (it was 85% before the switch
   and is 54% and 50% now): **94% and 92% of the fall comes back.** On big maps 76-78% against 83% before: **72 to
   79% comes back.** Measured on the zone of the true longest dragon the same sum gives 20% and 8-13%, which is why
   the lead's and the first red team's tables ("within 9 cells of the own longest") made the zone look like a part
   of the story. It is nearly all of it; the zones are simply not where the longest dragon is.
2. *The pearls.* Natural pearls eaten by small dragons per game per 50 rounds, by where the dragon stood
   (`y_c3b.py` part 3):

| | small maps: before | after | big maps: before | after |
|---|---|---|---|---|
| inside its named zone | 18.0 | 6.5 | 23.9 | 6.0 |
| outside | 11.2 | 16.8 | 21.6 | 20.8 |
| it names itself | 6.9 | 4.0 | 9.0 | 5.2 |
| per 100 dragon-rounds, inside / outside | 3.83 / 2.00 | 1.49 / 3.20 | 3.97 / 1.71 | 1.27 / 1.64 |

   Before the switch the ground near the named leader is the richest ground (3.8 to 4.0 pearls per 100
   dragon-rounds against 1.7 to 2.0 elsewhere): that is where the fountains are, and where dragons got long. After
   it, the dragons there eat a third of what they ate. On small maps the dragons outside pick up half of what is
   left (+5.6); on big maps nobody does. **The whole fall on small maps is the zone; on big maps about four fifths**
   (17.9 of 22.5). The rest on big maps is dragons that take themselves for the leader and stop harvesting.

**What else changes at that round?**

- *The split stop.* Units do not move in the first 50 rounds after the switch (small maps 24.4 and 24.5; big maps
  48 at round 150, 42 at round 200). The per-dragon rate above falls 20% and 38% in the first 25 rounds. So the first
  step is not the split stop. Later on big maps the unit count falls (37 at round 250) and adds to it.
- *The enemy arriving.* A pearl turn has no enemy head in view by definition, and the other side's intake and
  per-dragon rate do not move at our switch round.
- *Queen-feeding mode.* In those games the record names the queen and the zone lies around her. I did not separate
  them (our queen is alive at round 300 in a seventh of our games).

### C. Does the leader need it?

This is the first red team's objection, and A5's answer to it. Both are partly right.

**Where the final longest dragon's segments come from** (its lineage; all our races; pearls per race per 50 rounds
from round 250 to the end; `y_c3c.py` part B. My natural-pearl row is a lower bound by about one a block, see
section 5; A5's 4.0 / 5.0 / 3.7 / 3.5 / 5.0 for the live bot on small maps is the better number):

| | natural pearls | pearls of own dragons dead by choice | of other own corpses | of enemy corpses |
|---|---|---|---|---|
| small maps, live bot (53 races) | 1.8 / 4.0 / 2.7 / 2.9 / 4.0 | 0.1 / 0.2 / 0.2 / 10.2 / 6.1 | 2.2 / 2.0 / 2.0 / 1.7 / 1.5 | 0.2 / 0.4 / 0.3 / 0.4 / 1.2 |
| small maps, our 29 race wins | 2.2 / 3.2 / 3.9 / 3.6 / 5.8 | 0.1 / 0.3 / 0.4 / 12.6 / 11.0 | 2.6 / 1.9 / 2.3 / 2.4 / 1.4 | 0.3 / 0.2 / 0.4 / 0.7 / 1.7 |
| big maps, live bot (43 races) | 2.2 / 1.5 / 2.5 / 2.4 / 3.4 | 1.7 / 2.6 / 1.7 / 9.0 / 5.6 | 1.2 / 0.9 / 0.9 / 0.5 / 0.6 | 0.8 / 0.7 / 1.0 / 1.1 / 3.7 |
| big maps, our 12 race wins | 2.3 / 1.1 / 2.2 / 1.1 / 4.3 | 4.7 / 5.0 / 6.0 / 20.8 / 11.2 | 1.8 / 1.1 / 1.2 / 0.2 / 1.2 | 0.3 / 1.1 / 0.7 / 0.0 / 1.1 |

Feeding builds the leader, on both kinds of map; natural pearls are 2 to 5 per 50 rounds whatever phase it is.

**Natural pearls: no.** The leader's own natural intake does not rise when the zone starts (item A iii). Leaders of
teams that have no zone eat as many: the other side's longest dragon eats 3.0, 2.9, 2.7 natural pearls per 50 rounds
in our small-map games and 4.6, 4.0, 3.8 in our big-map games.

**Corpse pearls late in the game: yes, somewhat.** The zone also covers the pearls of dead dragons, feeders
included (`y_c3b.py` part 1, `y_c3c.py` part C):

| | small maps | big maps |
|---|---|---|
| corpse pearls declined inside a zone, per game, rounds 400-449 (live bot / test builds) | 3.8 / 4.8 | 3.2 / 3.8 (rounds 400-499) |
| ... eaten in the end by a leader | 39% / 43% | 26% / 33% |
| per race, from the switch to the end: declined natural pearls that the final lineage ate | 2.4 (median 0) | 0.9 |
| ... declined corpse pearls that the final lineage ate | 3.4 (median 2) | 2.2 |
| ... the same in our race wins | 2.9 and 3.8 | 1.5 and 6.5 (median 5) |

So the zone hands the dragon that ends as our longest about 6 pearls a race on small maps and 3 on big maps (8 in
our big-map wins) that a small dragon next to them had left. Against the margins of our 41 race wins:

| our race wins with a margin smaller than | wins |
|---|---|
| the declined natural pearls the lineage ate | 2 |
| those plus the declined corpse pearls it ate | **7** |
| every natural pearl the lineage ate after the switch (an upper bound nobody should use: leaders without a zone eat as many) | 23 |

The seven include 1027970 (Autarky, tied on the longest), 1027973 (weakhold, tied), 1052760 (Around UNSW, won by 2),
990348 (Maze, by 3), 1067916 and 1059085 (Portals, by 5 and 6). Of our 12 big-map wins one is among them. On small
maps 6 of our 29 race wins were won by 3 segments or fewer and 8 by 5 or fewer; of our 49 losses there 2 were lost
by 5 or fewer.

**Does what the small dragons eat come back to the leader?** Partly. A pearl eaten by a small dragon adds about
half a pearl to what the team can feed, and the final lineage gets 39% of feeder pearls on small maps and 25% on big
(section 2). That is 0.2 and 0.12 of a leader segment per pearl by that route; by the other route (final longest =
share of potential in the longest, 0.65 and 0.43, times potential) 0.33 and 0.2. Put together with the extra pearls
of item H:

| net for our final longest, per race | small maps | big maps |
|---|---|---|
| gain through more to feed | +1.6 to +3.3 | +3.6 to +11 |
| loss if the zone is off in every phase and small dragons take a third to four fifths of the declined pearls the lineage eats today | -1.9 to -4.6 | -1.0 to -2.5 |
| ... if only the pearls of dead dragons near a leader stay reserved once feeding has started | -0.8 to -1.9 | -0.3 to -0.7 |

On big maps the leader comes out ahead either way. **On small maps the rule as defined probably makes our final
longest a little shorter, while the team gets 12-16% longer.** That is the wrong trade exactly where our close wins
are. With feeder pearls kept reserved it is about even for the leader, and the team still gets the length.

### D. Backfire

- **Small dragons boxing the leader in once nothing keeps them away.** Counted on every turn of a team's longest
  dragon of 8 or more (`y_c3c.py` part D): with the zone on, our leader has no free cell on 1.7% of its turns on
  small maps in rounds 300-399 and one free cell on 21.9%; of the blocked neighbour cells then, 42% are kelp, 49% its
  own body and 8% a small own dragon; 0.70 small own heads stand within 3 cells of its head. Teams without a zone:
  no free cell 0.4% to 4.8%, small own dragons 5-7% of the blockers, 0.47 to 0.91 small heads within 3 cells. On big
  maps in rounds 150-299: ours 5.3%, 3% and 0.42; the others 0.5-4.3%, 5-8% and 0.37-0.54. **The zone does not keep
  small dragons off our leader's head; there are as many next to it as next to anybody's.** I see no reason to
  expect more boxing in.
- **The leader's growth before feeding.** Its natural intake is what a zone-less leader's is. Not a risk.
- **More dragons near the leader when an enemy rams it.** Not counted. Our leaders of 15-24 are rammed two to
  three times as often as our opponents' today (A5's count), with the zone on.
- **The enemy eating what we used to leave.** It already does: 4-5% of the declined natural pearls on small maps and
  12-17% on big maps go to the enemy. With the zone off those are ours.
- **The feeder pearls** (item C). This is the one backfire I could put a number on, and it is the reason for the
  amendment in section 4.

### E. Earlier experiments

From `work/plan.md`. None tested the zone alone.

| trial | what changed | result | what it says about 3z |
|---|---|---|---|
| "GB300" | the whole switch (leader status, zone, split stop) at round 300 instead of 150 on big maps | local, three runs: 30 of 64 against 20 (a base with a known bug, one map four times); 46 of 96 against 48 (+6 -8); 73 of 152 against 76 (+2 -5) | a mirror match: both sides are our bot and neither eats what the other leaves. Nothing |
| "LC200" (`LC_LEAD_ROUND` 200) | the whole switch at round 200 on every map: 100 rounds EARLIER on small maps, 50 later on big | local 52 of 96 (+26 -22); online 19 of 60 against dev test 1 where the base had 23 and another build 24; the weak maps were small ones (Autarky 0 of 6; Default, Devil, Prisoners Dilemma 1 of 6); "REJECT global early leader" | the only online trial that moved the zone, and it moved it the wrong way on the small maps and lost four games of 60. Inside the noise; the direction agrees with 3z |
| `LC_LEAD_MULT` 2 and 3 | the leader's own pearl weight before feeding | 76 and 77 of 152 against 76 | making the leader keener on pearls did nothing; fits "the leader does not use what is reserved for it" |
| card #14 | a unit count instead of the round for the split stop | not in the log; `findings.md`: "no gain locally" | another part of the switch |
| stride; the trade build (tc30) | economy by other means | +14% economy locally and no more wins; +21% total length at round 300 on big maps and 0 wins of 12 online (1.7 expected) | the standing warning: more length has not turned into wins yet. The trade build's two best openings were then lost between rounds 150 and 250, under this zone |

### F. The code claim

Read: the constructor, `refresh_leader_zone()`, `in_leader_pearl_zone()`, `survey_from()`, `look_cell_value()`,
`score_step()`, `is_leader()`, `split_child_size()`, `feeding_phase()`.

- **What reads the zone.** `zone_active` and `zone_head` are read only by `in_leader_pearl_zone()`. That function is
  read in seven places: four in `survey_from()` (a pearl in the zone is no target; it is not counted among the
  pearls ahead; a tile about to produce a pearl is no target; a fountain tile is no target), one in
  `look_cell_value()` (the eight-step look-ahead sees nothing in the zone), two in `score_step()` (no `EAT_BONUS`
  300 for stepping on a zone pearl, and `ZONE_PEARL_PENALTY` 600 for anybody but the leader). So the zone is more
  than "do not step on that pearl": inside it a small dragon does not walk to pearls, fountains or tiles about to
  spawn at all. That is why the per-dragon intake inside falls to a third and not only the rate of pearl turns.
- **Radius 0 does not switch it off entirely.** The test is "distance at most the radius". With 0 the one cell of
  the zone head stays: nothing when the leader is in view (its head is on it), but when it is not, the cell of the
  remembered position, where a pearl may lie (the head cell of a dead leader holds one of its pearls). A radius of
  -1 switches it off; so does an early return in `refresh_leader_zone()`.
- **Nothing else changes with it.** `grow_round` still decides who counts as leader, the leader's own bans and the
  split stop; feeding is untouched. One thing to know: feeders never get the eating bonus (`!is_feeder()`), zone or
  no zone, and are pulled by the feed target, so with the zone off the dragons that would take the pearls near a
  leader are the non-feeders: too long to feed it, beyond 15 cells of it, or naming somebody else.
- **No toggle.** `LEADER_PEARL_RADIUS` and `ZONE_PEARL_PENALTY` are plain constants. No map-size condition is in the
  rule as stated. What stays map-size dependent after it is the switch round itself (150 or 300), which 3z leaves
  alone on purpose; so the rule starts to act at round 150 on big maps and 300 on the others.
- **The amended form** (section 4) would be: the zone exists only in the feeding phase, only around a leader whose
  head is in the dragon's own view, with a radius of about 4. Our feeders die within 3 cells of the head, so their
  pearls lie inside that. That is three small changes in `refresh_leader_zone()` and one constant. I did not count
  what that exact form does; it is a design read off the counts above.

### G. Cross-team

Nobody else leaves pearls for a leader, in any phase before feeding (`y_c3a.py` part 5, `y_c3d.py`):

| natural pearls taken, pearl within 9 cells of the own longest of 10+ / farther | small maps, rounds 150-299 | 300-399 | big maps, rounds 150-299 | 300-399 |
|---|---|---|---|---|
| meow live bot | (no such leader yet) | 29% / 59% | 48% / 64% | 45% / 64% |
| our opponents | 90% / 89% | 87% / 87% | 83% / 84% | 82% / 85% |
| test4 / WHQ (against us) | 81 / 73%, 91 / 91% | 78 / 70%, 88 / 89% | 72 / 77%, 91 / 89% | 72 / 76%, 89 / 90% |
| forgot | 95% / 94% | 96% / 94% | 95% / 95% | 95% / 95% |
| SSS | 90% / 88% | 80% / 78% | 82% / 82% | 78% / 82% |
| Vibing++ | 91% / 84% | 88% / 83% | 88% / 87% | 80% / 82% |

Per dragon-round the ground near the own longest dragon is the better ground for every team: on big maps in rounds
150-299 a small dragon within 9 cells of it eats 4.04 natural pearls per 100 rounds for our opponents (3.20
farther), 4.38 for forgot (3.29), 4.51 for Vibing++ (3.86), 3.41 for SSS (3.50). Ours: 1.71 (1.88), and 4.88 (2.41)
before our switch.

One exception, late: from round 400, on small maps, Vibing++'s small dragons take a corpse pearl within 9 cells of
their longest dragon in 64-67% of turns against 79-81% elsewhere (natural pearls on big maps 65% against 75%), and
test4's in 66-70% against 72-75%. That looks like a mild version of "leave the feeder's pearls", in the feeding
phase only. forgot, SSS and WHQ show nothing (83-100%).

### H. What it is worth

**Step 1, the pearls** (`y_c3c.py` part E). For every game: what our small dragons would have eaten from the switch
on had they kept the rate per dragon-round of the 50 rounds before it, with the dragon-rounds they really had.
"Plain" is that; "trend" scales it by how the other side's small dragons' rate moved in the same rounds.

| extra natural pearls per game | plain | trend | as a share of our total length then |
|---|---|---|---|
| small maps, live bot, switch to round 400 (99 games) | +9.9 | +7.7 | +16% / +12% |
| small maps, test builds (44) | +9.4 | +8.8 | +13% / +12% |
| big maps, live bot, switch to round 300 (75 games) | +55.9 | +38.0 | +46% / +31% |
| big maps, live bot, switch to round 400 (72) | +80.6 | +59.7 | +68% / +50% |
| big maps, test builds, switch to round 300 (34) | +51.8 | +33.6 | +43% / +28% |

With the zone's share of the fall from item B (all of it on small maps, four fifths on big): **about +8 to +10
pearls by round 400 on small maps, and +30 to +45 by round 300 on big maps (a quarter to a third more total
length).** More eaters compete for the same pearls and more length means more splits; I counted neither.

**Step 2, the wins.** Our 401 games, by where the rule can act at all (`y_c3d.py`):

| | games | won | can 3z change it? |
|---|---|---|---|
| small maps, over before round 300 | 131 | 61 | no |
| small maps, races | 78 | 29 | a little either way: more to feed, fewer reserved pearls (item C) |
| small maps, our queen dead and hers alive, or queen games | 55 | 4 | hardly: length does not beat a living queen |
| small maps, wiped out or wiping out after round 300 | 26 | 6 | perhaps |
| big maps, races | 65 | 12 | **yes: this is where the pearls are** |
| big maps, our queen dead and hers alive | 33 | 0 | no |
| big maps, wiped out | 13 | 0 | hardly |

Three readings of the big-map races. (a) Our own bands of potential at round 300 moved up by a quarter: about +5.6
wins. (b) The same with the top three's rates in those bands: +4.2. (c) A curve of win on total length over all our
big-map games (`y_c3c.py`): +3.4 wins when half of the trend pearls arrive, +10.5 when all of the plain ones do. On
small maps that curve gives +0.8 to +2.6 wins, and item C takes about as much away again if the zone goes in every
phase.

| | all 401 games | live bot, 275 games |
|---|---|---|
| strict (every pearl arrives, band or curve rates as they are) | +5 to +13 wins | +3 to +9 |
| cautious (half the pearls; races only; the small-map leader pays what item C says) | +1 to +4 wins | +1 to +3 |
| what I would defend | **+1 to +8 wins: +0.3 to +2 points, most likely about +1** | +0.4 to +2 points |

Why I stay at the low half of the strict count: a win rate "for a band" was earned with the bot as it is, the
warning of the first round. The one time our big-map economy was raised by a fifth (the trade build) it won none of
12. And +30% still leaves most big-map games under two thirds of the enemy's length.

**Where it acts and where it does nothing.** It acts in every game that reaches the switch: all 111 big-map games
from round 150, and 159 of our 290 small-map games from round 300. It does nothing in the 131 small-map games that
are over before round 300, which hold 61 of our 112 wins. It cannot turn the 84 games we lose with our queen dead
and hers alive.

### What is left of the claim

| support | the lead | after the attacks |
|---|---|---|
| (i) the rate falls at our switch, in every run, nowhere else | 80-85% to 49-56% | exact: 84% to 64% to 58% on big maps, 83% to 64% to 51% on small, in each of eleven runs |
| (ii) by the dragon's own belief | 18-26% inside, 75-87% outside | 20-25% inside, 75-89% outside, with a step between 9 and 10 cells; and half of all pearl turns on small maps are inside a named zone, most of them around a dead or short dragon |
| (iii) "the leader gets nothing from it" | eats 7-17% of what is left for it; own intake flat | true of natural pearls before feeding. **Not true late:** per small-map race the final lineage eats 3.4 corpse and 2.4 natural pearls that a small dragon had declined; 7 of our 41 race wins were closer |
| (iv) the team's intake falls | 20.8 to 15.6; 79.5 to 52.7 | -22% and -33% on the same games; per small dragon -20% and -38% in the first 25 rounds; the other side flat. The zone is all of it on small maps and four fifths on big |
| (v) the big-map leader is built by feeding | four games read | all 12 big-map wins: feeder pearls 2.9 to 6.0 per 50 rounds from round 200, 32 in the last hundred |
| size | none | +0.3 to +2 points, most likely about +1; the gain is on big maps, the risk on small ones and avoidable |

## 4. The three finalists side by side

Candidate 1 is "any dragon of ours with the enemy queen's head in view and in reach rams her". I did not recount it
in this round; its column is the first red team's (`redteam.md`), which recounted it from the replays.

| | Candidate 1: take the queen | Candidate 5: one leader, known to all | Candidate 3z: no pearl zone |
|---|---|---|---|
| **What is measured, and how solid** | We take 99 of 435 such chances (23%); Vibing++ 265 of 266, SSS 250 of 252, forgot 253 of 451; our opponents 197 of 228 on our queen. Solid, holds in every run. Its small-dragon half was online twice (56 games a side): chances taken 15 of 49 to 19 of 20, games with a ram on her queen 16 to 24, her queen alive at the end 19 to 16, wins 16 to 17 | Our leader cuts 3.9 to 4.5 times a race from round 395 and its heir cuts again within 10 rounds in 42% of cases. 12% of our feeder deaths are for a stub or a short dragon, 39% for a big dragon that is not the longest. In the earlier bot the feeders near a cut name the heir slowly (44% after 25 rounds). Solid as counts; the pings are from 82 games of an earlier bot | A step in the free-pearl rate at our own switch round (84% to 64% to 58%; 83% to 64% to 51%), in each of eleven runs, in no other team; by the dragon's own belief 20-25% inside the zone and 75-89% outside with a step between 9 and 10 cells; natural pearls per small dragon -20% and -38% in the first 25 rounds with the other side flat. The most solid measurement in the study |
| **What is inferred** | That the extra kills change how games end: 6 games by reading the 25 games concerned one by one; 3 to 11 by comparing games inside our own record, zero not excluded | That feeders who no longer die for a stub then reach the true leader; that an age rule does not split the team by region; that the stall after a cut costs length rather than time | That 8 to 10 more pearls by round 400 on small maps and 30 to 45 by round 300 on big maps turn into wins; that small dragons would take a third to four fifths of the pearls the leader gets from the zone today |
| **The range I would defend** | +0.5 to +2 points, most likely about +1 (the first round's) | -0.3 to +0.8, most likely +0.2 to +0.4 | +0.3 to +2, most likely about +1; strict count +5 to +13 wins of 401 |
| **Chance of harm, and how much** | Small. The first round could not build a way to lose more than a game or two in 400 | About one in three of a small net loss (up to -0.5 points): regional leaders from the age rule, good feeder deaths stopped by the "see it" test | As defined, about one in five of a net loss of up to a point, through close small-map race wins (7 of 41 were closer than the pearls the zone handed the winner). With feeder pearls kept reserved, about one in ten |
| **Size of the change in the code** | One switch that exists (`QUEEN_HUNT`) and one condition (`real_queen()` in `mark_hunt_targets()`) | Three places in the record and feeder code, no toggle; the first needs a redesign (the age term must price both reports and the dragon's own length) | One constant (`LEADER_PEARL_RADIUS` 9 to -1; 0 leaves one cell). Amended: three lines in `refresh_leader_zone()` and the constant |
| **What would show it working on 20 to 60 new replays** | In-view chances taken: 22% to over 90%. Games with a chance and no ram: 19% to under 3% | Feeder deaths for a stub or a dragon under twice the feeder's length: 12% to under 4%. Must not rise: deaths next to another big dragon (39%). The final lineage's share of feeder pearls: 36-39% to 45% on small maps. The beliefs themselves cannot be read in a sealed build | Free pearl next to the head taken after the switch: 51-58% to over 80% (thousands of turns in 20 games). Natural pearls per 50 rounds after the switch: 54 to 70 or more on big maps, 31 to 37 or more on small. Total length at round 300 on big maps: 122 to 150 or more. Must not fall: the final lineage's share of feeder pearls (39% small, 25% big); our longest at round 400 and at the end |
| **Do all three top teams do it?** | Vibing++ and SSS all of it; forgot with dragons of 2-3 from round 100 on | Cannot be seen. forgot, Vibing++ and WHQ feed through a cut; SSS stalls as we do and is level with them | None of the three has a zone, nor test4 or WHQ: their small dragons take 72-96% of the natural pearls near their own long leader before round 400. (Vibing++ and test4 hold back a little on corpse pearls near the leader after round 400.) |
| **Where it acts** | In the 44% of games in which one of our heads gets her in view and reach; not when we are far behind | In races (143 of 401) after feeding starts; mostly on big maps | In every game that reaches the switch round: all big-map games from round 150, 159 of 290 small-map games from round 300; nothing in the 131 games over before round 300 |

### Which one I would send

**Candidate 3z, in this form:**

> Until the team starts to feed one dragon, nobody leaves a pearl for anybody. Once feeding has started, a small
> dragon leaves the pearls within a few cells of a leader it can see, and no others.

In code terms that is: the pearl zone exists only in the feeding phase, only around a leader whose head is in the
dragon's own view, with a small radius (our feeders die within 3 cells of the head, so about 4). No map name and no
map size is in it. The switch round, the split stop, who counts as leader and the start of feeding stay as they
are. If the team wants the lead's plain version (radius off in every phase), that is one constant; it gains the same
on big maps and puts some close small-map wins at risk.

Why this one and not candidate 1, which I rank second and close:

1. **It is the only finalist that works on the larger gap.** Section 1 says the race gap of its own is most likely
   worth about 8 wins, and that we enter 106 of our 143 races below 0.8 of the enemy's potential. A rule that only
   converts better has a ceiling; 3z raises what there is to convert, by a quarter to a third on big maps.
2. **It is identified, not correlated.** The effect appears at round 150 on one kind of map and at round 300 on the
   other, on the round our own code switches, in every run, and at exactly 9 cells. Nothing else in this study has
   that. Candidate 1's behaviour gap is as clear, but for its effect on results the two online trials of its tested
   half moved the behaviour and not the end state.
3. **Nobody good does what we do.** Every team we looked at eats next to its leader; for all of them the ground
   near the long dragon is the best ground on the board.
4. **It is small, and it can be read in 20 games.** One constant in the plain form, three lines more in the
   amended one. The rate goes from a half to four fifths or it does not. The risk has its own number in the same
   replays (the leader's share of feeder pearls).
5. **Its size is not smaller than candidate 1's**: +1 most likely for both; the strict counts are +5 to +13 wins
   here against 6 to 13 for candidate 1 in sub-session B's count and 6 in the first red team's.

What it is not: a sure thing. Its sign in wins is less certain than candidate 1's. If the team wants the candidate
that cannot hurt, that is still candidate 1.

**The most likely way it disappoints.** It does what it says and the wins do not move. The free-pearl rate jumps to
85%, we are a quarter longer at round 300 on big maps, and then the extra dragons meet an enemy that rams in 35% of
meetings where we ram in 8%, and that eats two thirds of the pearls of those rams (sub-session A3). The length
flows across the border as it did for the trade build, which was a fifth longer at round 300 and won none of 12. On
small maps the team gets longer and the leader no longer; races there are decided by the leader. And in a 30-game
test a gain of one point is 0.3 wins, so even a real gain will look like nothing.

The second most likely: the plain version is built, the leader loses the feeder pearls small dragons used to leave,
and two or three close small-map races flip the wrong way while the big-map gain is too thin to show.

### Two together?

- **Candidate 1 with 3z: safe.** They touch different code (the hunt path at the top of a turn; the pearl scoring),
  they act in different places (a queen in view; pearls after the switch round) and each is read on its own
  number (chances taken; free-pearl rate and natural intake), so a build with both can still be checked for both.
  What is lost is only the win attribution, and neither can be judged by wins in 30 or 60 games anyway. One small
  interaction to know: candidate 1 spends about 5 segments a game on rams; 3z adds 10 to 50.
- **Candidate 5 with 3z: no.** Both change how feeder pearls reach the leader, and the number that guards each of
  them is the same (the final lineage's share of feeder pearls). Candidate 5 moves the zone to the heir; 3z removes
  or shrinks the zone. A flat or bad result could not be traced. 3z in the amended form also removes one harm of the
  stale record on its own: a zone that only exists around a leader in view cannot sit around a stub's remembered
  place or keep the heir off its own pearls.
- **Candidate 1 with candidate 5: safe**, and not worth a card for what candidate 5 brings.

### What I would tell the team with it

- Check the leader's side first, not last: our longest at round 400 and at the end, and the share of feeder pearls
  the final longest eats, on small maps. If those hold and the pearl rate is at 80%, the rule is doing what it
  should whatever the win count says.
- Do not expect it on the maps where we are overrun before the switch (Islands, Australia: units falling from 38
  to 17 and from 38 to 28 in the hundred rounds after it). It needs dragons to eat with. The maps to watch are the
  ones where our unit count holds: Slithery Fight, Around UNSW, Maze, weakhold.
- The same counts point at three smaller repairs that are not this card: a feeder should count steps and not cells
  to the leader (5% of our feeders, 8.5% on small maps, die on the wrong side of a wall and the leader gets 16% of
  those pearls instead of 66%); a feeder should not die for a dragon of which it sees fewer than four segments (12%
  of feeder deaths); and the leader cuts too often (3.9 to 4.5 times a race from round 395, the heir again within
  10 rounds in 42% of cases), which nobody has looked into.

## 5. Corrections

Numbers and sentences in `deep-read-5.md`, `redteam.md`, `hypotheses.md` and `findings.md` that my recount could not
reproduce, or that are right as counts and wrong as statements. Where a count of mine and theirs agree within a
game or a point it is in the tables of sections 1 to 3 and not repeated.

| Where | It says | I find | Why |
|---|---|---|---|
| `deep-read-5.md` 2.0 and section 6, "final longest / potential at round 300", live bot, small maps | 0.65 (forgot 0.85, Vibing++ 0.71) | **0.77** (forgot 0.89, Vibing++ 0.72); test builds 0.79, our opponents 0.75 and SSS 0.73 as given | 0.65 is the live bot's share of its FINAL potential, which stands in the next column. On this measure the live bot is not behind our opponents or SSS (`y_a2.py` part 3) |
| `deep-read-5.md` section 1 and 8.1 | "most of the gap is not in the race"; the race gap of its own "is small" | on potential at round 300 our races are worth 49.5 wins at the top three's conversion against the 41 we won: +8.5 (80% range about 0 to +16); the edge at equal potential is 0.33 lower in log-odds (0 to 0.66) | "11 of 23" compares us with the other side of the same games (`y_a.py`, `y_a2.py`) |
| `redteam.md` attack I | at 0.8 or better on total length at round 400 "+10 wins, 2.7 points" | on that footing +12.5 wins by the top three's curve, +13.5 band by band; on a footing before feeding +8 | total length at round 400 counts a team that has fed as poorer than it is; A5's point, which holds for 45% of the gap |
| `deep-read-5.md` section 1 and 7 | after a cut "a median of 27 rounds until half of our dragons name the new longest (388 cuts)" | 458 cuts in 82 readable games; in 370 it happens before the game ends (quartiles 14 / 28 / 46 rounds), in 88 it never does. Of the feeders standing near the cut 44% name the heir after 25 rounds, and only 31% named the leader BEFORE the cut | the same count with four more games; the second number is new (`y_misc.py`, `y_c5e.py`) |
| `deep-read-5.md` section 1 and 7 | "in 78 of our games those pings can be read" | 82 (ladder of 3 October 24, 4 October 31, stride-old 27) | my test: 500 or more leader pings, 95% of them plausible |
| `deep-read-5.md` section 1 (b), 7.3, 7.4 | each cut costs "about 25 rounds of feeding"; growth 5.0 against 10.8 "with a cut" | the 25-round window after a cut grows 11.4 against 11.1 with no cut; the deficit is in windows that contain a cut (3.0), and half of it is the 2 segments per cut. Feeding next to the longest is back after 20 rounds in the earlier bot, 15 in today's live bot, 10 in the test builds | A5 pooled "a cut in the window or in the 25 rounds before" (`y_c5a.py`, `y_c5f.py`) |
| `deep-read-5.md` section 1 (c), 6, 7 | "a quarter of our deaths by choice are within reach of no bigger own dragon" (26% / 20%), meaning feeders die next to nothing | the count reproduces (27% / 20%). By the bot's own test: 7.6% of feeder deaths are for a fresh stub, 4.7% for another dragon under twice the feeder's length, 5.4% for the true longest across a wall, 39% for a big dragon that is not the longest | the path-step test puts deaths across a wall and deaths of other kinds under "nothing" (`y_c5c.py`) |
| `deep-read-5.md` 7.5, change 1 | the age term `max(0, when - known_leader_round)` makes the heir win "four rounds after the cut instead of 25" | as written the held record is marked down only against a fresher report; an older report of a longer id is not marked down and wins again when a team-mate repeats it | reading of `hear_exact()` |
| `deep-read-5.md` 7.5, change 3 | "a real leader three cells away" passes the "see it is long" test | 28% of today's deaths next to the true longest would fail it (628 of 2,263) | a feeder in front of the head sees little of the body (`y_w4b.py`) |
| `deep-read-5.md` 7.4 | strict 6 to 12 games of 401 | A5's own what-ifs recount to 5 / 10 / 17 (theirs 6 / 12 / 18) and 3 / 11 / 20 (theirs 4 / 11 / 20); from the pearls that demonstrably go astray: 1 to 5 | two of our lost races were lost by exactly 5; the rest is section 2 I |
| `deep-read-5.md` 2d and 5d | of the pearls left in the zone the leader eats "12% / 11%" (small maps) and "7 / 17 / 6%" (big) | 26% / 17% and 13 / 11 / 17% | I count as leader the team's longest at that round, the longest when the pearl was declined, or the id the decliner named |
| the brief's support (iii) for 3z; `deep-read-5.md` 5d "It does what the code says and nothing for the leader" | the leader gets nothing from the zone | true of natural pearls before feeding. Per race the final lineage eats 2.4 natural and 3.4 corpse pearls that a small dragon had declined in a zone on small maps (0.9 and 2.2 on big; 1.5 and 6.5 in our big-map wins); 7 of our 41 race wins had a smaller margin | the zone also covers the pearls of feeders (`y_c3c.py` part C) |
| `findings.md` 6c, `hypotheses.md` candidate 3, `redteam.md` | the fall is "also there far from the own longest dragon ... so a remembered leader position or another rule is involved too"; "the zone explains most of it and not all" | by the dragon's own named zone the zone is 92-94% of the fall of the rate on small maps and 72-79% on big; the zones lie around the id each dragon names, which is the true longest for under 40% of them | readable pings (`y_c3a.py` part 3) |
| `hypotheses.md` candidate 3 and `redteam.md` | total length at round 300 on big maps would be "+12 to +24%" higher; "possible in the half of the games in which we have a full team" | at the small dragons' own before-switch rate per dragon-round, with the dragon-rounds they really had: +31% to +46% for everything that changes at the switch, about four fifths of it the zone | a per-dragon count, so it holds in the games in which our unit count falls too (`y_c3c.py` part E) |
| `deep-read-5.md` 7.4 (d), on candidate 3 | "the zone gives the leader nothing on either map class" and the two candidates "can ride together" | see two rows up; and candidate 5 and 3z should not be tested together (section 4) | |
| `deep-read-5.md` table B1, natural pearls of the final lineage | 4.0 / 5.0 / 3.7 / 3.5 / 5.0 per 50 rounds (live bot, small maps) | mine are about one lower per block (1.8 / 4.0 / 2.7 / 2.9 / 4.0) | not a correction: I credit a 25-round block to the lineage by who it was at the block's middle and lose pearls around cuts. Theirs is the better number; the other three columns agree exactly |

## 6. What I could not determine

1. **What any of the rules does in a real game.** I ran none. Every size in this file is arithmetic on games that
   were played.
2. **Whether more pearls become more wins for our bot.** The pearls of 3z are measured (a step at our own switch
   round). The wins are read off bands and curves that were earned with the bot as it is, and the one time our
   big-map economy was raised by a fifth it won 0 of 12. This is the open question of the candidate I would send.
3. **What small dragons would do with the pearls of feeders if the zone were gone.** Today they leave 3.8 to 4.8 of
   them a game in rounds 400-449 on small maps and the leader gets about 40% of those. Whether they would take a
   third of them or four fifths decides whether the plain version of 3z costs the small-map leader 2 segments or 5.
   Feeders themselves never get the eating bonus, so it depends on how many of the dragons near a leader are not
   feeders; I did not count that.
4. **What the exact amended form does** (a zone only in the feeding phase, only around a leader in view, radius
   about 4). It is read off the counts, not counted.
5. **Why today's builds recover faster after a leader cut than the earlier bot** (20 rounds, 15, and 5 to 10 in
   the test builds). The log says none of the builds changed the leader or feeding code; their pings are sealed and
   I left them sealed. The belief numbers of candidate 5 therefore describe a bot we no longer run, and I cannot say
   how stale the record is in the current one.
6. **Whether the heir of a cut really takes its own stub for the leader**, as the code says it should (a new
   dragon with an empty record hears the old report like everybody else). The heir's own pings would show it; I
   followed the feeders near a cut, not the heir.
7. **Whether fast naming of the heir makes it grow faster, inside the same game.** 25 usable cuts in the readable
   games, 5 of them "fast". No power.
8. **What the other teams know.** A replay shows that forgot, Vibing++ and WHQ feed through a cut and that SSS does
   not; it does not show a record. Vibing++'s and test4's small dragons take fewer corpse pearls near their leader
   late in the game; whether that is a rule or feeders on their way to die cannot be seen.
9. **How many spawns a blocked tile costs.** Spawn intervals are hidden. Declined pearls block their tiles for 45
   to 93 tile-rounds per game per 50 rounds; on a fountain that is several pearls, elsewhere none.
10. **Queen-feeding games.** When our queen is fed, the record names her and the zone lies around her. 3z would
    remove that too. Our queen is alive at round 300 in about a seventh of our games and both queens are alive at
    the end in 14; I did not separate those games, and the amended form (zone kept in the feeding phase) leaves them
    as they are.
11. **Why the zone was put in, and why 9 cells.** Not in `work/plan.md`, which starts on 29 September.
12. **Whether the race gap against the top three is real or 30 games.** Against test4 and WHQ the top three win 69%
    at level potential and we 44%; their side of that is 30 races.
13. **Why we never win from under half the enemy's potential** (0 of 48; the top three 5 of 43). Five of the eight
    wins of section 1 sit there. I did not read those five games.
14. **Why our leader cuts so often, and its heir again so soon.** It is the number that separates us most from
    every other team in the last hundred rounds, and no candidate works on it.
15. **Anything about maps nobody has seen.** 3z gains most on maps over 1,200 cells (5 of the 15 known maps) and
    wherever the fountains lie near where our long dragons grow.

## 7. Counts I made

All scripts are in this directory and are my own; they use `lib.py` (the replay walker) and `games.csv`, and none
plays a game. Outputs are in `y_out/`. Filter everywhere: opponents rated 2000 or more, map Schooltime left out. I
read `e_belief.py` for the layout of a readable ping and the other sub-sessions' scripts to learn what they counted.
No key or derived value was copied anywhere; sealed pings were counted as unreadable and left alone.

**Walks of the replays**

| Script | What it counts | Output |
|---|---|---|
| `y_lib.py`, `y_r.py` | Shared helpers: the game filter and runs, a small logistic fit, the loader for walk 1, lineage of the final longest | |
| `y_w1.py` | All 1,795 games with a study side, both sides. Every 5 rounds from round 100: units, total length, longest and second longest, potential, potential within 15 cells of the longest, queen. Every split; for splits of a dragon of 6+ the free cells at its head and the longest other own dragon. Every death from round 100 with the free cells at its head when it gave its order, the longest other own dragon, all own heads within 8 path steps, the nearest enemy head. Every corpse pearl eaten (eater, dead dragon). Natural pearls per dragon and 25 rounds, by the leader of the time and by length class | `y_out/w1/<game>.json` |
| `y_w2.py` | The same games. For our side in readable games, every round from 150: how many own dragons name a longest dragon, a dead id, a living dragon under half the longest, themselves; how many could feed the longest by geometry and name it. For every leader cut of either side from round 150: free cells, room in front of the stub, own heads near; the own dragons that could feed the heir near the cut, followed for 30 rounds (distance to heir and stub, how and where they died, and in readable games what they named each round); the heir's length each round; why the follow-up ended | `y_out/w2/<game>.json` |
| `y_w3.py` | The same games, both sides. Every pearl turn, by 25 rounds, own length, distance from the pearl to the true longest and its length class, distance to the zone head the dragon itself named (readable games), natural or corpse pearl; the same per 10 rounds. Every pearl declined inside a zone and its fate (who ate it, after how many rounds, how often it was declined). Dragon-rounds of small dragons and natural pearls they ate, inside and outside the true zone and the named zone. Natural pearls by eater class, inside and outside the zone. Every turn of a team's longest dragon of 8+: free cells, what blocks, small own heads near | `y_out/w3/<game>.json` |
| `y_w4.py` | Our 401 games: every feeder ("no order") death of ours from round 150 with the id, length and age it named one turn before (readable games), that dragon's true length, distance, path steps and whether it was in view; the true longest; the longest own head in view within 3 cells | `y_out/w4/<game>.json` |
| `y_w4b.py` | Our 401 games: for every feeder death, how many segments of the dragon it died next to were inside its own view | `y_out/w4b/<game>.json` |
| `y_dbg.py`, `y_dbg2.py`, `y_dbg3.py`, `y_peek.py`, `y_env.py` | Checks: event order around deaths and splits, my board-occupancy mirror against the walker's bodies, the direction code of recorded moves, the game filter (401 / 503 / 502 / 632 game-sides), the Python in use | |

**Tables**

| Script | What it counts | Output |
|---|---|---|
| `y_a.py` | Claim A: races and wins by group; won of games by own / enemy total length at round 400 and by potential at rounds 300, 350, 400, by map class and against test4 and WHQ; total length at rounds 250 and 300; the first red team's band looked at again; a logistic fit per group and footing (the edge at ratio 1, the slope); a fitted footing (final longest from longest and rest); our races on the top three's curve with a resampling range; the level band on nine footings; share of potential in the longest | `y_out/a.txt` |
| `y_a2.py` | Claim A: fine bands of the potential ratio with our races at the top three's rates; a pooled fit with a term for our side; medians of final longest over potential; who has converted by round 400; our level races by map and opponent | `y_out/a2.txt` |
| `y_c5a.py` | Candidate 5 from positions: leader cuts per race and phase, with a free cell; cuts of the final lineage and lost races they would turn; growth of the longest per 25-round window with a cut inside / only before / none, by build, run, opponent, map class, team, leader length, and inside the same game; deaths by choice by what stood within 3 and 8 steps and who ate the pearls; the clock after a cut; the longest around a cut | `y_out/c5a.txt` |
| `y_c5b.py` | Candidate 5 from the pings and the cut follow-ups: readable games per run; what our dragons name per 25 rounds; rounds until half name the longest after a cut; growth by the share naming it, with cuts taken out and by rounds since the cut; what the feeders near a cut do within 25 rounds, per team; the heir's growth; how soon the heir cuts again | `y_out/c5b.txt` |
| `y_c5c.py` | What our feeders die next to: the true longest (within 3 steps, or across a wall), another big dragon, a fresh stub, a short dragon; who ate the pearls; by map class, build, opponent and map | `y_out/c5c.txt` |
| `y_c5d.py` | Candidate 5's size and backfire: unfed length near and far from the longest at the end; the gap between our two longest dragons during feeding; lost races that turn under three readings of the misdirected pearls; A5's what-ifs recounted; margins of our races; the "see it is long" test on today's deaths | `y_out/c5d.txt` |
| `y_c5e.py` | The naming curve after a cut on every leader cut of the readable games from round 300; when half of the feeders first name the heir; fast against slow naming | `y_out/c5e.txt` |
| `y_c5f.py` | The earlier bot against today's builds: the clock after a cut and the three kinds of window for readable games, sealed live-bot games and test builds | `y_out/c5f.txt` |
| `y_c5g.py` | The heir's growth 3 to 25 rounds after a leader cut, per team and map class, and by whether the cut was made with a free cell | `y_out/c5g.txt` |
| `y_c3a.py` | Candidate 3z: the free-pearl rate around the switch per team, build and run; inside against outside the zone by belief and by the true longest, natural and corpse pearls, by distance; how much of the fall comes back with the zone off; by map; other teams near their own longest | `y_out/c3a.txt` |
| `y_c3b.py` | Candidate 3z: the fate of pearls declined in a zone; natural pearls per 50 rounds by team, leader and length class on the same games, next to the other side; pearls per 100 dragon-rounds inside and outside the zone before and after the switch; by map | `y_out/c3b.txt` |
| `y_c3c.py` | Candidate 3z: natural pearls per 25 rounds and per small dragon around the switch; where the final lineage's segments come from in our races and race wins; declined pearls the lineage ate, against the margins of our wins; the leader boxed in, per team and phase; extra pearls at the before-switch rate per dragon-round; our win curve on total length and the wins on it | `y_out/c3c.txt` |
| `y_c3d.py` | Small dragons near their own longest, every team: natural pearls per 100 dragon-rounds inside and outside 9 cells; our 401 games by map class, ending and whether they reach the switch | `y_out/c3d.txt` |
| `y_misc.py` | Rounds until half name the longest with and without the cuts after which it never happens; margins by map class; growth of the longest after round 400 by build and run | `y_out/misc.txt` |
| `y_build.py`, `y_mdcheck.py` | Assembles this file from `y_p0_head.md` to `y_p6_unknown.md`; checks its tables and the file names in it | `redteam-2.md` |

Checks against earlier numbers. `y_w1.py` reproduces game 1 of A5's reading list to the unit (1027819: total length
140 : 157, 136 : 131, 156 : 154; longest 4 : 8, 13 : 58, 32 : 77; potential 84 : 92, 85 : 99, 99 : 117). `y_a.py`
reproduces every count of A5's footing tables and the first red team's race table. `y_c5a.py` reproduces A5's
window, cut and death tables within a few windows or one point; `y_c5b.py` the belief table within two points.
`y_c3a.py` reproduces the first red team's 10-round blocks around both switch rounds exactly (84, 84, 64, 60 and 85,
83, 64, 51).
