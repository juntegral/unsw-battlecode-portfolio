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
