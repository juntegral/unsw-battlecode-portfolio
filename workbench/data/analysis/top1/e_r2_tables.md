## 2. The all-games tables

Everything in this section is counted over all races (round-500 games with both queens dead) of the group named, or
over all its games where a line says so. Groups: **meow live bot** (275 games, 96 races), **meow test builds** (126
games, 47 races), **our opponents** (the other side of our 401 games; 143 races), **test4 / WHQ (vs us)** (the two
teams we meet most, counted in their games against us: 49 and 74 races), **forgot / SSS / Vibing++** (all their games
against 2000+ teams: 154 / 141 / 152 races). All numbers are medians per game unless a cell says "mean" or gives a
count. The scripts are in this directory, their outputs in `e_out/`; the full, longer outputs are named under each
table.

### 2.0 The footing: potential, not total length

`e_p300.py` (`e_out/p300.txt`), `e_level.py` (`e_out/level.txt`), `e_p.py` (`e_out/p_potential.txt`, one line per game
of ours in `e_out/p_games.txt`).

**Races won / races, by own P / enemy P at a given round** (all maps):

| group | at round 300: under 0.5 | 0.5-0.8 | 0.8-1.25 | over 1.25 | at round 350: 0.8-1.25 | at round 400: 0.8-1.25 |
|---|---|---|---|---|---|---|
| meow live bot | 0 of 34 | 10 of 33 | 10 of 20 | 7 of 9 | 8 of 15 | 10 of 24 |
| meow test builds | 0 of 14 | 10 of 25 | 1 of 3 | 3 of 5 | 4 of 9 | 3 of 10 |
| meow, all | 0 of 48 | 20 of 58 | **11 of 23** | 10 of 14 | **12 of 24** | 13 of 34 |
| our opponents (same games) | 1 of 11 | 3 of 3 | 12 of 22 | 86 of 107 | 12 of 24 | 21 of 33 |
| forgot | 3 of 21 | 10 of 25 | 29 of 52 | 43 of 56 | 28 of 55 | 29 of 53 |
| SSS | 0 of 8 | 3 of 12 | 39 of 71 | 40 of 50 | 47 of 80 | 34 of 59 |
| Vibing++ | 2 of 14 | 5 of 14 | 31 of 46 | 61 of 78 | 28 of 43 | 26 of 43 |
| top three together | 5 of 43 | 18 of 51 | 99 of 169 | 144 of 184 | 103 of 178 | 89 of 155 |

**The same against test4 and WHQ only** (the opponents we share with the top three), level band 0.8-1.25:

| group | at round 300 | at round 350 | at round 400 |
|---|---|---|---|
| meow, all | 7 of 17 (test4 4 of 9, WHQ 3 of 8) | 10 of 21 (4 of 9, 6 of 12) | 9 of 30 (6 of 17, 3 of 13) |
| top three | 11 of 16 (SSS 8 of 10, Vibing++ 3 of 4, forgot 0 of 2) | 11 of 13 (SSS 7 of 9) | 9 of 13 |

**The red team's band looked at again** (small maps, own / enemy total length at round 400 between 0.8 and 1.25):

| | games, won | total length at round 300, own : enemy | at 350 | at 400 | P at round 300 | games in which the enemy's total at round 300 was over 1.25 times ours |
|---|---|---|---|---|---|---|
| meow | 30, 9 | 65.5 : 90.5 | 69 : 93.5 | 73.5 : 76 | 39.5 : 54 | 17 (won 5); the other 13: won 4 |
| top three | 40, 22 | 101 : 94 | 92 : 95 | 88.5 : 92 | 61.5 : 56 | 7 (won 5); the other 33: won 17 |

Reading. (1) Our races are mostly lost before they start: at round 300 we are under half the enemy's potential in 48
of 143 races (0 won) and at 0.5-0.8 in 58 (20 won; the top three win 18 of 51 from there, the same rate). (2) At level
potential before feeding we win about half (11 of 23, 12 of 24). The "30% against 55%" of the red team compared games in
which we were 27% behind at round 300 with games in which a top team was 10% ahead. (3) A gap remains against the best
converter: against test4, SSS wins 8 of 10 and 7 of 9 level races where we win 4 of 9. Counts under 30; the 80% range
of our 12 of 24 is 37% to 63%.

**How the potential moves and how much of it ends in the longest dragon** (`e_p300.py`, `e_cdist.py`; `e_out/cdist.txt`):

| group | small maps: P at 300 -> 400 -> end | final longest / P at round 300 | completeness at the end | big maps: P at 300 -> 400 -> end | final longest / P at round 300 | completeness at the end |
|---|---|---|---|---|---|---|
| meow live bot | 40 -> 44 -> 38 | 0.65 | 0.65 | 91 -> 82 -> 100 | 0.42 | 0.43 |
| meow test builds | 34 -> 50 -> 44 | 0.79 | 0.71 | 95 -> 93.5 -> 81.5 | 0.36 | 0.43 |
| our opponents | 53 -> 53 -> 52 | 0.75 | 0.77 | 184 -> 199 -> 177 | 0.38 | 0.40 |
| test4 (vs us) | 53 -> 51 -> 47 | 0.70 | 0.77 | 206.5 -> 210 -> 175 | 0.25 | 0.29 |
| WHQ (vs us) | 57 -> 60 -> 60 | 0.86 | 0.80 | 183 -> 208 -> 178 | 0.45 | 0.48 |
| forgot | 42 -> 45 -> 49 | 0.85 | 0.69 | 108 -> 118 -> 113 | 0.53 | 0.49 |
| SSS | 56 -> 58.5 -> 54.5 | 0.73 | 0.79 | 125 -> 134 -> 141 | 0.46 | 0.42 |
| Vibing++ | 43 -> 49 -> 54 | 0.71 | 0.59 | 124 -> 130 -> 160 | 0.46 | 0.39 |

Completeness at the end by the side's own unit count at round 400 (all sides of all walked races, potential 20+):
small maps 0.83 / 0.75 / 0.64 / 0.60 / 0.56 for 0-9 / 10-19 / 20-29 / 30-44 / 45-64 units; big maps 0.78 (5 sides) /
0.67 / 0.49 / 0.42 / 0.37. With 45 or more units at round 400, 6% of sides on small maps and 1% on big maps end at 0.75
or more. By map: Portals 0.85, Queen Of Spades 0.73, Tower Defense 0.70, weakhold 0.67, Maze 0.64, Devil 0.64, Autarky
0.59, Default 0.51; Slithery Fight 0.48, Islands 0.47, Australia 0.39, Around UNSW 0.35 (closed, crowded ground
completes; wide open ground does not).

What-ifs on our 102 lost races (`e_p.py`, `e_margin.py`; strict readings, the enemy unchanged):

| what-if | losses that turn |
|---|---|
| our final longest = 0.75 / 0.85 / 0.95 of our own final potential | 19 / 32 / 39 (small maps 2 / 11 / 14; big maps 17 / 21 / 25) |
| both sides complete (more final potential wins) | 12 losses turn, 11 of our 41 wins are lost |
| our final longest +5 / +10 / +15 / +20 segments | 4 / 11 / 20 / 29 |
| our leader's growth after round 400 times 1.25 / 1.5 / 2 | 7 / 17 / 27 (live bot 6 / 13 / 20 of its 69 losses) |
| ... the same, never above 0.9 of our final potential, and only in races with a leader cut after round 395 | 6 / 12 / 18 (live bot 5 / 10 / 14; against test4 2 / 3 / 5, against WHQ 3 / 7 / 11, against others 1 / 2 / 2) |

Median margin of our lost races: 32.5 segments (5 losses by 5 or fewer, 6 by 6-10, 19 by 11-20, 72 by more).

### 2a to 2c. The curve, the sources and the leader, by map class

`e_sum.py` writes the tables below (`e_out/sum_tables.md`). Longer versions: `e_a.py` (`e_out/a_curve.txt`: every 25
rounds, by band of total length at round 400), `e_b.py` (`e_out/b_source.txt`: per 50 rounds, lineage and leader of the
time), `e_c.py` (`e_out/c_leader.txt`), `e_churn.py` (`e_out/churn.txt`), `e_opp.py` (`e_out/opp.txt`), `e_era.py`
(`e_out/era.txt`).

@@include e_out/sum_tables.md@@

Reading of tables A1-A3. On small maps our longest dragon is 4 at round 300, 9-10 at 350-400 and 20 (live bot) at the
end; our opponents' is 5.5, 11, 18.5 and 37. The dragon that ends as our longest first passes 15 at round 406 (live
bot; never in 16 of 53 races) and 25 at round 426 (never in 26); our opponents' passes them at 388 and 410, SSS's at
357 and 372, Vibing++'s at 424 and 438. Leader feeding starts at round 401 for us and Vibing++ (403), 311 for SSS, 315
for WHQ, 354 for test4, 373 for forgot. Once it has taken off, everybody's longest grows 11-18 in 50 rounds; from round
400 to the end ours grows 10 (live bot) and 21 (test builds), the others 15.5 to 26. On big maps our longest is already
10 at round 200 (the round-150 switch and the 56-unit feeding rule) but only 14 at round 400; the others go from 13-30
at round 300 to 36-55 at round 400 (test4, which waits for its queen to die, 18.5 to 24). Terrain beyond the size: the more closed and crowded the ground, the more complete
the feeding of every team (list in 2.0), and the more often our leader cuts itself (Portals 7.6 cuts a race after
round 395, Around UNSW 5.6, Maze 4.2, Slithery Fight 4.2, Australia 2.6, weakhold 2.4, Default 1.2; `e_out/opp.txt`).

Reading of tables B1-B2. The final longest dragon of every team gets 3-5 natural pearls per 50 rounds, whatever the
team does; the difference is made by pearls of own dragons that died by choice. On small maps our lineage gets 0.2 of
those per 50 rounds until round 400 and then 10.2 and 6.1 (live bot); our opponents' gets 4.4 and 8.9 in rounds
300-399 and then 10.9 and 7.9. So in the last hundred rounds we feed as fast as they do; they have a hundred rounds
more. A warning about the feeder rows of table B2: for our bot they count every `noaction` death, also those with no
bigger dragon near, and for the others only deaths within 3 steps of a dragon twice as long, so "the dragon fed eats
54% of ours and 69-78% of theirs" is not like for like. The like-for-like table is the next one ("The same test for
every team"): on it our result per pearl equals our opponents' on small maps and is better than theirs on big maps;
what stands out for us is the share of deaths next to nothing. On big maps everybody's feeding is scattered.

Reading of table C1. Nobody's longest dragon at round 400 is usually the same id as the final longest (3-34%); by
lineage it is in 25-79%. Before round 395 we cut our leader 2.3-3.9 times a race and the others 1.0-3.5; after it we
cut more (3.8-4.1 against 1.9-3.2, forgot's 4.1 on small maps excepted), and two thirds of our cuts are made with a free
cell next to the head (WHQ 5-18%, forgot 7-15%). For us and for SSS a cut halves the leader's growth in the windows
around it on both map classes (for Vibing++ and test4 only on big maps, for forgot and WHQ not at all). Our leaders are
not lost more often than others' in races (0.13 a race on small maps, 0.56 on big ones; our opponents 0.15 and 2.20,
most of theirs boxed in: a leader that does not cut with a free cell left sometimes dies in the pocket).

**Leader cuts and what follows, our races** (`e_churn.py`, `e_opp.py`):

| leader cuts from round 395 | races | won | completeness at the end | longest at round 400 -> end | own P / enemy P at round 400 | units at the end |
|---|---|---|---|---|---|---|
| none | 26 | 5 | 0.71 | 6 -> 10 | 0.20 | 3 |
| 1-2 | 31 | 14 | 0.62 | 13 -> 36 | 0.70 | 8 |
| 3-5 | 47 | 14 | 0.55 | 13 -> 34 | 0.74 | 11 |
| 6 or more | 39 | 8 | 0.44 | 13 -> 30 | 0.80 | 18 |

(The "none" row is the races in which we had almost nothing left: a leader of 6.) Growth of the longest dragon per
25-round window from round 400, windows that start with 10 or more other own dragons:

| | windows with a leader cut in them or in the 25 rounds before: mean growth (windows) | without: mean growth (windows) |
|---|---|---|
| meow, all races | 5.0 (291) | 10.8 (91) |
| meow live bot / test builds | 4.5 (194) / 6.1 (97) | 11.4 (66) / 9.3 (25) |
| meow against test4 / against WHQ / against everybody else | 4.9 (103) / 5.5 (142) / 3.7 (46) | 11.4 (31) / 10.9 (42) / 9.6 (18) |
| meow on small maps / big maps | 6.0 (125) / 4.3 (166) | 12.4 (51) / 8.7 (40) |
| meow, earlier bot (readable sonar) / stride and later | 3.0 (50) / 5.4 (241) | 9.5 (24) / 11.3 (67) |
| our opponents | 6.0 (216) | 6.9 (156) |
| forgot / SSS / Vibing++ (small maps) | 8.7 (82) / 2.4 (53) / 8.0 (119) | 5.9 (16) / 6.2 (47) / 5.8 (65) |

One cell does not show it: the test builds on small maps (9.9 with a cut in 42 windows, 9.7 without in 13).

**What our dragons believe** (`e_bel.py`, `e_out/bel.txt`; the 78 study games with readable sonar: 56 on small maps, 22
on big ones; a sample = one look every 5 rounds at every own dragon but the longest):

| small maps, rounds | 250-299 | 300-324 | 325-349 | 350-374 | 375-399 | 400-424 | 425-449 | 450-474 | 475-499 |
|---|---|---|---|---|---|---|---|---|---|
| own dragons whose believed leader is the true longest | 4% | 16% | 32% | 28% | 34% | 37% | 34% | 31% | 28% |
| ... is a dead dragon | 51-55% | 49% | 26% | 37% | 27% | 19% | 36% | 36% | 34% |
| ... is dead or under half the true longest's length | 66-72% | 65% | 53% | 60% | 59% | 54% | 57% | 61% | 65% |
| samples in which at least half believe the true longest | 4% | 26% | 35% | 32% | 39% | 48% | 50% | 46% | 39% |
| dragons that could feed it by our rules (believe it, within 15 cells, at most half its length) | 0.4 | 2.0 | 4.6 | 3.9 | 4.6 | 5.2 | 3.0 | 1.5 | 1.2 |
| ... the same without the belief test | 6-7 | 7.5 | 9.2 | 9.5 | 10.2 | 9.3 | 5.2 | 4.1 | 3.7 |

On big maps 18-47% believe the true longest from round 175 on, and at least half do in 14-41% of the samples. After a
leader cut (leader 8+, from round 150; 161 cuts on small maps, 227 on big ones) half of the team believes the true
longest again after a median of 27 and 27.5 rounds (quartiles 17 and 36-41); in the samples in between the most
believed id is dead in 36-44% and alive but under half the true longest in 28-34%. Growth of the longest over the next
5 rounds, rounds 400-494, 10+ senders (`e_churn.py`): under a quarter believe it: +0.42 (187 samples; any growth in
40%); a quarter to a half: +1.85 (40); a half to three quarters: +1.51 (41); more: +2.00 (79). Against test4 0.40 and
1.45, against WHQ 0.35 and 2.41, against others 0.46 and 1.63 (under a quarter / otherwise; `e_out/opp.txt`).

**Whom our feeders die next to** (all `noaction` deaths of ours in the 401 games, no sonar needed; `e_bel.py`):

| | deaths | next to the team's true longest | next to another own dragon of 8+ | next to an own dragon under 8 | no own dragon twice as long within 8 steps |
|---|---|---|---|---|---|
| small maps | 3,640 (12.6 a game) | 53% | 9% | 17% | 21% |
| big maps | 4,895 (44.1 a game) | 35% | 29% | 25% | 11% |
| races, all maps | 5,559 (38.9 a race) | 42% | 23% | 20% | 15% |
| ... of their pearls the final lineage ate | | 60% | 14% | 9% | 7% |
| ... the enemy ate | | 2% | 4% | 4% | 12% |

**The same test for every team** (`e_dist.py`, `e_out/dist.txt`). Every death by choice in a race, rounds 300-499,
sorted by what was within 3 path steps of the dying head: the team's longest dragon of that moment; else another own
dragon at least twice as long; else such a dragon 4-8 steps away; else nothing. Pearls: who ate them in the end;
"final lineage" = the dragon that ends as the team's longest, followed back through its splits.

| small maps | races | deaths by choice per race | next to the longest | next to another dragon twice as long | such a dragon at 4-8 steps | nothing | pearls dropped per race | eaten by the final lineage | by other own dragons | by the enemy | by nobody |
|---|---|---|---|---|---|---|---|---|---|---|---|
| meow live bot | 53 | 33.2 | 42% | 16% | 17% | **26%** | 46.8 | 36% | 52% | 4.7% | 7% |
| meow test builds | 25 | 37.0 | 44% | 16% | 15% | **25%** | 54.9 | 45% | 45% | 2.8% | 7% |
| our opponents | 78 | 45.6 | 42% | 26% | 16% | 15% | 84.5 | 39% | 55% | 2.3% | 4% |
| test4 (vs us) | 29 | 41.6 | 41% | 25% | 14% | 20% | 80.4 | 36% | 59% | 2.4% | 2% |
| WHQ (vs us) | 39 | 52.2 | 45% | 26% | 18% | 12% | 95.2 | 40% | 53% | 2.3% | 5% |
| forgot | 65 | 27.3 | 51% | 25% | 17% | 8% | 48.6 | 47% | 50% | 0.6% | 2% |
| SSS | 42 | 47.0 | 73% | 14% | 3% | 10% | 70.5 | 41% | 54% | 1.6% | 3% |
| Vibing++ | 67 | 27.0 | 35% | 18% | 33% | 14% | 44.2 | 46% | 49% | 1.3% | 4% |

| big maps | races | deaths by choice per race | next to the longest | next to another dragon twice as long | such a dragon at 4-8 steps | nothing | pearls dropped per race | eaten by the final lineage | by other own dragons | by the enemy | by nobody |
|---|---|---|---|---|---|---|---|---|---|---|---|
| meow live bot | 43 | 46.9 | 30% | 36% | 14% | 20% | 70.6 | 27% | 58% | **10.5%** | 5% |
| meow test builds | 22 | 51.7 | 28% | 41% | 15% | 16% | 79.0 | 24% | 64% | 7.5% | 5% |
| our opponents | 65 | 113.6 | 15% | 58% | 17% | 11% | 260.0 | 16% | 75% | 5.3% | 4% |
| test4 (vs us) | 20 | 59.8 | 13% | 57% | 13% | 17% | 163.8 | 17% | 75% | 6.0% | 2% |
| WHQ (vs us) | 35 | 151.5 | 16% | 59% | 16% | 9% | 333.5 | 15% | 74% | 4.5% | 5% |
| forgot | 89 | 64.9 | 26% | 50% | 18% | 5% | 121.5 | 26% | 72% | 1.8% | 1% |
| SSS | 99 | 78.6 | 52% | 38% | 4% | 6% | 130.3 | 31% | 64% | 3.9% | 2% |
| Vibing++ | 85 | 53.1 | 21% | 35% | 35% | 10% | 103.1 | 29% | 65% | 3.7% | 2% |

The final lineage's share of the pearls by where the death was (next to the longest / another dragon twice as long /
4-8 steps / nothing): meow 70% / 18% / 21% / 13% on small maps and 61% / 11% / 13% / 7% on big ones; the top three
61% / 24% / 45% / 18% and 53% / 13% / 26% / 10%; our opponents 59% / 20% / 34% / 18% and 43% / 8% / 14% / 12%.

Reading. (1) Per pearl we are where our opponents are on small maps (39% to the final lineage, both) and ahead of
them on big maps (26% against 16%); the top three are at 45% and 29%. So accuracy is not what test4 and WHQ have over
us. (2) What they have is volume: 80-95 pearls a race dropped by choice on small maps against our 47-55, and 164-334
against 71-79 on big maps. Multiplied out, the final lineage gets 17-25 segments from deaths by choice in rounds
300-499 with us, 29-38 with test4 and WHQ, 20-29 with the top three (small maps); table B1 shows where the difference
sits: in rounds 300-399 our lineage gets 0.4 pearls of this kind and theirs 9.5-16.7 (SSS 14.5, forgot 8.4, Vibing++
3.8); in rounds 400-499 we get 16.3 and they 14.4-20.2. (3) Our own outlier is the last column of the left block: a
quarter of our deaths by choice are next to no bigger own dragon (others 8-20%), and those pearls are nearly lost to
the leader (13%). On big maps the enemy eats one in ten of our pearls (others one in 17 to 55).

**How close a feeder dies, and what the distance is worth** (`e_dist.py`, first part; deaths by choice from round 250
within 3 path steps of an own dragon at least twice as long; all study games):

| | feeders | dies at 1 / 2 / 3 steps | the dragon fed eats, of the pearls of those at 1 / 2 / 3 steps | the dragon fed is the team's longest |
|---|---|---|---|---|
| meow live bot, small maps | 1,667 | 5% / 33% / 61% | 90% / 78% / 74% | 72% |
| meow test builds, small maps | 868 | 6% / 36% / 58% | 81% / 76% / 72% | 73% |
| our opponents, small maps | 4,367 | 18% / 39% / 43% | 84% / 73% / 66% | 61% |
| WHQ (vs us), small maps | 2,195 | 26% / 38% / 37% | 85% / 74% / 69% | 60% |
| forgot, small maps | 6,727 | 13% / 37% / 50% | 89% / 79% / 70% | 70% |
| SSS, small maps | 7,209 | 64% / 26% / 10% | 84% / 68% / 44% | 77% |
| Vibing++, small maps | 2,751 | 10% / 41% / 49% | 83% / 74% / 71% | 61% |
| meow live bot, big maps | 2,300 | 5% / 35% / 60% | 79% / 75% / 69% | 44% |
| forgot, big maps | 9,678 | 14% / 36% / 50% | 93% / 84% / 78% | 33% |
| SSS, big maps | 10,367 | 63% / 24% / 13% | 80% / 66% / 45% | 54% |
| Vibing++, big maps | 4,064 | 14% / 41% / 45% | 81% / 71% / 68% | 33% |

A pearl dropped one step from the dragon it is meant for is eaten by that dragon 79-93% of the time, at three steps
63-78% (SSS 44-45%), for every team. We die at three steps six times in ten and at one step one time in twenty
(`FEEDER_DIE_DIST 3`); SSS dies at one step two times in three. And when one of our dragons does die within reach of a
bigger one, that one is the team's longest as often as for the top three (72% on small maps): the aiming is fine when
there is something to aim at.

**Who is fed to the leader: small feeders or whole dragons** (`e_merge.py`, `e_out/merge.txt`; the same deaths by
choice in races, rounds 300-499, by the length of the dragon that died; pearls per race):

| | from dragons of 2-4 | 5-7 | 8-14 | 15+ | the final lineage's share of the pearls of 2-4 / 5-7 / 8-14 / 15+ | rounds 450-499, dragons of 8+: deaths per race, pearls, lineage's share | races with a death by choice of a 15+ |
|---|---|---|---|---|---|---|---|
| meow live bot, small maps | 41.9 | 2.7 | 1.9 | 0.3 | 36% / 33% / 41% / 29% | 0.30, 1.5, 33% | 2 of 53 |
| meow test builds, small | 46.2 | 4.5 | 3.4 | 0.8 | 45% / 42% / 50% / 37% | 0.40, 2.3, 43% | 2 of 25 |
| test4 (vs us), small | 51.1 | 14.5 | 11.0 | 3.8 | 27% / 46% / 52% / 80% | 1.28, 8.2, 64% | 9 of 29 |
| WHQ (vs us), small | 68.9 | 7.1 | 10.2 | 9.0 | 37% / 40% / 50% / 45% | 1.49, 11.5, 57% | 18 of 39 |
| forgot, small | 35.2 | 9.4 | 2.5 | 1.5 | 46% / 51% / 44% / 65% | 0.17, 1.1, 38% | 9 of 65 |
| SSS, small | 53.9 | 9.0 | 7.0 | 0.6 | 44% / 35% / 30% / 11% | 0.62, 3.3, 39% | 2 of 42 |
| Vibing++, small | 35.3 | 4.3 | 2.1 | 2.4 | 47% / 49% / 37% / 37% | 0.28, 2.2, 27% | 11 of 67 |
| meow live bot, big maps | 56.8 | 5.7 | 5.7 | 2.4 | 26% / 26% / 30% / 31% | 0.65, 4.0, 25% | 8 of 43 |
| our opponents, big | 136.1 | 24.5 | 39.8 | 59.6 | 12% / 14% / 17% / 23% | 4.34, 40.5, 24% | 60 of 65 |
| forgot, big | 82.6 | 20.6 | 8.7 | 9.6 | 24% / 29% / 27% / 34% | 0.81, 5.6, 36% | 46 of 89 |
| SSS, big | 86.0 | 19.0 | 15.6 | 9.6 | 32% / 32% / 28% / 24% | 1.27, 8.4, 29% | 54 of 99 |
| Vibing++, big | 65.2 | 15.7 | 12.1 | 10.0 | 24% / 34% / 37% / 42% | 1.40, 10.2, 41% | 40 of 85 |

Reading. In small feeders we are not behind anybody: 42-46 pearls a race from dragons of 2-4 against the top three's
35-54. What our two usual opponents add is whole dragons: on small maps test4 and WHQ drop 26-29 pearls a race from
dragons of 5 or longer and their final lineage eats about half of them; we drop 5-9. In the last 50 rounds they
give the leader 1.3-1.5 dragons of 8+ a race (8-11.5 pearls, 57-64% eaten by the final lineage, so 5 to 7 segments);
we 0.3 (under one segment), as rarely as the top three do on small maps (0.2-0.6). On big maps everybody but us does
it: 18-100 pearls a race from dragons of 8+ against our 8. In our code a dragon may feed only a leader it believes
to be twice its own length (`FEED_LEN_RATIO 2`), so an 8-long needs a 16-long leader and an 18-long a 36-long. Other
bots kill big dragons with the suicide order too: `noaction` deaths of dragons of 15+ in all study games: 15 in
our 401 games, 312 in WHQ's 159 against us, 211 in forgot's 632, 298 in Vibing++'s 502, 53 in SSS's 503, none with
the replay's time-out flag in ours or the top three's (`e_tle.py`); test4's run into themselves instead.

**The direct cost of the leader's own cuts** (`e_cutcost.py`, `e_out/cutcost.txt`; counted on the lineage of the final
longest, so a chain of cuts within one round counts in full; "voluntary" = the dragon that started the cut, or the
chain, had a free cell next to its head):

| group | races | cuts of the final lineage from round 400, per race: all / voluntary | segments left behind per race: all / voluntary | lost races | ... in which the segments left behind from round 400 are more than the margin | ... the voluntary ones alone | from round 440: all / voluntary |
|---|---|---|---|---|---|---|---|
| meow live bot | 96 | 2.7 / 1.8 | 5.5 / 3.5 | 69 | 9 | 6 | 7 / 5 |
| meow test builds | 47 | 2.7 / 1.7 | 5.4 / 3.4 | 33 | 1 | 1 | 1 / 1 |
| meow, all | 143 | 2.7 / 1.7 | 5.4 / 3.5 | 102 | **10** | **7** | 8 / 6 |
| our opponents | 143 | 2.0 / 0.8 | 4.1 / 1.6 | 41 | 1 | 0 | 1 / 0 |
| test4 (vs us) | 49 | 2.1 / 1.5 | 4.2 / 3.1 | 17 | 0 | 0 | 0 / 0 |
| WHQ (vs us) | 74 | 1.7 / 0.2 | 3.4 / 0.5 | 13 | 1 | 0 | 1 / 0 |
| forgot | 154 | 3.3 / 0.3 | 6.6 / 0.6 | 69 | 14 | 5 | 11 / 4 |
| SSS | 141 | 1.6 / 1.6 | 3.2 / 3.1 | 59 | 4 | 4 | 2 / 2 |
| Vibing++ | 152 | 2.0 / 1.2 | 3.9 / 2.5 | 53 | 7 | 3 | 3 / 0 |

Our ten: 1027971 (19 to 30, 7 cuts), 1044201 (51 to 52, 5 cuts, Around UNSW), 1044208 (42 to 43, 5 cuts), 1044522 (33
to 39, 9 cuts), 1045374 (25 to 31, 7 cuts), 1058146 (49 to 56, 6 cuts), 1058149 (45 to 50, 5 cuts, Around UNSW),
1058363 (16 to 18, 3 cuts), 1058858 (22 to 37, 10 cuts, six of them in round 478), 1063023 (25 to 37, 8 cuts). It is a
strict what-if (the 2-long stub is worth a pearl again if it is fed back; a cut with no free cell had no alternative
but death), and it is a cost every team pays in close races (the top three in 25 of their 181 losses). Ours is the
highest rate of voluntary cuts next to SSS's and test4's. An heir rarely dies at once (within one round of the cut in
0-3.1% of cuts for every team, ours 1.6-2.0%; `e_heir.py`, `e_out/heir.txt`), and it cuts again within three rounds
in 10-13% of our cuts (others 7-26%).

**What the situation is at a cut** (`e_cutctx.py`, `e_out/cutctx.txt`; one more walk over all 1,795 games; every leader
cut from round 250 in all study games, chains within a round included; "room" = cells reachable from the free cells
next to the head without crossing a body):

| small maps | games | cuts (per game) | made with a free cell | of those: room 4 or less / 5-8 / 9-20 / more | of those: an enemy head within 3 cells / 4-6 / farther | of those: the 2-long stub dies within 3 rounds / in 4-10 / is alive after 10 rounds | cuts with no free cell: the heir is born with no free cell either |
|---|---|---|---|---|---|---|---|
| meow live bot | 198 | 528 (2.7) | 57% | 76% / 5% / 3% / 15% | 26% / 29% / 45% | 28% / 20% / 48% | 11% of 227 |
| meow test builds | 92 | 290 (3.2) | 62% | 81% / 8% / 3% / 8% | 25% / 26% / 50% | 23% / 31% / 42% | 12% of 111 |
| test4 (vs us) | 112 | 271 (2.4) | 53% | 75% / 1% / 1% / 23% | 25% / 28% / 47% | 39% / 14% / 47% | 10% of 127 |
| WHQ (vs us) | 115 | 276 (2.4) | 30% | 33% / 17% / 4% / 46% | 32% / 30% / 38% | 24% / 24% / 51% | 1% of 194 |
| forgot | 471 | 681 (1.4) | 20% | 59% / 10% / 4% / 28% | 23% / 32% / 45% | 48% / 19% / 30% | 5% of 543 |
| SSS | 364 | 725 (2.0) | 87% | 78% / 5% / 3% / 14% | 28% / 24% / 48% | 25% / 29% / 44% | 25% of 97 |
| Vibing++ | 375 | 971 (2.6) | 61% | 62% / 16% / 10% / 12% | 21% / 29% / 51% | 37% / 21% / 42% | 6% of 377 |

On big maps: 8.1 cuts a game for the live bot (61% with a free cell; room 4 or less in 65% of those and over 20 in
31%), test4 8.6, Vibing++ 7.7, forgot 5.6 (7% with a free cell), WHQ 5.2 (15%), SSS 4.8 (92%).

Reading. Everybody's leader is cut, 2.0 to 3.2 times a game on small maps (forgot 1.4) and 5 to 9 on big ones. A cut
"with a free cell" is in three cases out of four a cut a few rounds early: the pocket ahead holds four cells or
fewer (ours 76-81%, SSS 78%, test4 75%). Only WHQ and forgot wait for the last cell. So the number and the timing
of our cuts are at the upper end of ordinary (2.7-3.2 a game against 1.4-2.6 here; 3.8-4.1 a race against 1.9-4.1 in
table C1; 2.7 against 1.6-3.3 on the final lineage); what follows a cut in our team is not ordinary (the belief
table above).

### 2d. Our two switches

`e_d.py` (`e_out/d_switch.txt`). The turn counted is the one sub-session B and the red team used: a non-queen dragon of
2-4 moves, no enemy head is in its 7x7 view, and a pearl lies on a free next cell that has a further free neighbour.

**The leader zone** (live bot; all its games on those maps, any ending). Share of such turns on which the pearl is taken:

| small maps (switch at round 300), rounds | 200-249 | 250-299 | 300-349 | 350-399 | 400-449 | 450-499 |
|---|---|---|---|---|---|---|
| all such turns | 85% of 5,062 | 85% of 3,901 | 54% of 4,117 | 53% of 4,085 | 45% of 3,930 | 52% of 2,322 |
| the pearl within 9 cells of the true leader (5+) / farther | 82 / 81% | 84 / 82% | 36 / 59% | 39 / 59% | 35 / 48% | 36 / 58% |
| by the dragon's own belief (readable games): every such pearl inside the believed leader's zone | 84% of 885 | 85% of 560 | **26% of 705** | **22% of 760** | 20% of 683 | 20% of 411 |
| ... a pearl outside the believed zone | 86% of 516 | 86% of 388 | 87% of 501 | 87% of 502 | 76% of 523 | 85% of 296 |
| ... it believes it is the leader itself | 83% | 86% | 78% | 72% | 73% | 73% |
| team: natural pearls eaten per game | 24.1 | 20.8 | 15.6 | 14.7 | 9.6 | 7.9 |
| the leader of the time: natural pearls per game | 2.0 | 1.7 | 1.6 | 1.0 | 1.5 | 1.9 |
| our opponents in those games: pearl taken | 83% | 81% | 80% | 76% | 71% | 61% |

| big maps (switch at round 150), rounds | 100-149 | 150-199 | 200-249 | 250-299 | 300-349 | 350-399 |
|---|---|---|---|---|---|---|
| all such turns | 84% of 5,145 | 61% of 4,121 | 58% of 3,678 | 58% of 3,629 | 58% of 3,333 | 56% of 3,551 |
| inside the believed leader's zone | 83% of 656 | **24% of 431** | 19% of 331 | 18% of 410 | 23% of 358 | 25% of 326 |
| outside the believed zone | 81% of 739 | 77% of 636 | 77% of 563 | 80% of 619 | 75% of 654 | 79% of 711 |
| team: natural pearls eaten per game | 79.5 | 52.7 | 45.9 | 45.7 | 41.6 | 41.6 |
| the leader of the time: natural pearls per game | 4.0 | 3.4 | 2.5 | 2.2 | 1.6 | 2.0 |
| splits per game | 56.5 | 30.3 | 28.8 | 31.2 | 30.2 | 28.0 |
| our opponents: pearl taken; natural pearls per game | 86%; 131.6 | 84%; 131.6 | 85%; 128.9 | 84%; 124.7 | 85%; 117.9 | 83%; 109.7 |

The other teams' take rates do not move at those rounds (forgot 90-94% throughout, SSS 77-86%, Vibing++ 87-90% until
round 350 and 70-79% after it). **What became of the pearls left lying** (live bot):

| | small maps, rounds 300-349 / 350-399 / 400-449 | big maps, rounds 150-199 / 200-249 / 250-299 |
|---|---|---|
| pearls left lying, per game | 4.3 / 3.9 / 5.1 | 11.3 / 11.4 / 10.2 |
| ... inside the believed zone, per game (readable games) | 1.1 / 1.0 / 1.2 | 2.4 / 1.8 / 1.9 |
| of those: eaten in the end by the leader | 12% / 11% / 30% | 7% / 17% / 6% |
| by another own dragon of 8+ | 2% / 2% / 2% | 1% / 11% / 1% |
| by an own dragon under 8 | 69% / 73% / 52% | 69% / 58% / 72% |
| by the enemy | 6% / 2% / 2% | 13% / 8% / 12% |
| by nobody within 30 rounds | 11% / 12% / 14% | 10% / 6% / 9% |
| rounds it lay before it was eaten (median) | 9 / 8 / 6 | 10 / 7 / 10 |

So the zone works as written (26% against 87%) and gives the leader one pearl in eight of what is left for it; seven in
ten are eaten later by another small dragon of ours, the rest lies there or goes to the enemy. The team's natural
intake falls by a quarter on small maps at round 300 (20.8 to 15.6 a game; in races 47.9 to 38.2) and a third on big
maps at round 150 (79.5 to 52.7), where the split stop of the same switch also halves the splits.

**Feeding** (`e_d.py` part 2, `e_e.py`). Our feeding starts when the code says: of the live bot's 186 games that reach
round 300, 35 had 56 units at round 200 and all 35 have a start, three quarters of them by round 224 (quartiles 201 /
205 / 224); of the 27 small-map games with our queen alive at round 300, 24 have a start, 20 of them between rounds 302
and 375 (queen-feeding mode); the rest start at 401-405. Because
the start is set by the state, "early against late in the same band" compares different kinds of game, and the cells
are small; for what it is worth, live bot, small maps, total length at round 300 between 0.67 and 1 of the enemy's:
start before 300 (the 56-unit rule) 6 games, 3 won, longest 4.5 / 15 / 58.5 / 75.5 at rounds 300 / 400 / 450 / end
with 54 units at round 300; start at 400 or later 17 games, 2 won, longest 5 / 11 / 21 / 28 with 23 units. The
comparison that can be made cleanly is "who starts first" (2h below). Which mechanism builds our leader, round for
round (live bot, lineage, pearls per race in rounds 250-299 / 300-349 / 350-399 / 400-449 / 450-499): small maps,
natural 4.0 / 5.0 / 3.7 / 3.5 / 5.0, feeders 0.1 / 0.2 / 0.2 / 10.2 / 6.1, other own corpses 2.2 / 2.0 / 2.0 / 1.7 / 1.5;
big maps, natural 3.1 / 2.0 / 2.6 / 2.8 / 4.1, feeders 1.7 / 2.6 / 1.7 / 9.0 / 5.6. The zone phase adds one pearl per 50
rounds to the leader on small maps and none on big ones; feeding builds it.

### 2e. What starts the others' feeding

`e_e.py` (`e_out/e_trigger.txt`; one line per game in `e_out/e_trigger_games.txt`). Start of leader feeding = the first
of three leader-feeder deaths within 15 rounds (the fed dragon is not the queen). Games that reach round 300.

| team | games; with a start | start: quartile / median / quartile | 56+ units at round 200 | 30-55 units | under 30 units | big maps | small maps | own queen alive at the start |
|---|---|---|---|---|---|---|---|---|
| meow live bot | 186; 105 | 216 / 401 / 405 | 201 / 205 / 224 (35 of 35 games) | 331 / 401 / 405 | 402 / 405 / 422 | 201 / 212 / 319 | 401 / 403 / 411 | 13% |
| meow test builds | 82; 52 | 240 / 401 / 408 | 202 / 213 / 277 | 300 / 401 / 405 | 401 / 408 / 412 | 204 / 240 / 405 | 401 / 404 / 408 | 4% |
| WHQ (vs us) | 104; 91 | 270 / 276 / 316 | **270 / 271 / 272** (53 of 53) | 295 / 303 / 325 | 314 / 334 / 374 | 270 / 270 / 271 | 292 / 314 / 334 | 37% |
| WHQ (vs top three) | 15; 12 | 272 / 324 / 331 | 271 / 272 / 307 | 270 / 315 / 324 | 331 / 332 / 408 | 271 / 307 / 315 | 324 / 325 / 332 | 33% |
| test4 (vs us) | 106; 61 | 318 / 350 / 381 | 268 / 327 / 374 | 320 / 354 / 378 | 376 / 382 / 392 | 266 / 327 / 383 | 321 / 375 / 381 | 38% |
| test4 (vs top three) | 51; 26 | 295 / 323 / 392 | 270 / 315 / 406 | 320 / 342 / 411 | 376 / 378 | 270 / 295 / 323 | 321 / 376 / 392 | 12% |
| forgot | 400; 309 | 302 / 359 / 373 | **300 / 303 / 344** (162 of 162) | 362 / 371 / 377 | 373 / 381 / 437 | 300 / 303 / 330 | 369 / 372 / 382 | 50% |
| SSS | 334; 291 | 274 / 301 / 315 | 221 / 287 / 302 | **301 / 307 / 332** | 301 / 303 / 321 | 207 / 274 / 300 | 301 / 307 / 332 | 65% |
| Vibing++ | 322; 236 | 339 / 363 / 401 | **337 / 360 / 368** | 344 / 369 / 402 | 364 / 403 / 421 | 338 / 360 / 364 | 344 / 401 / 419 | 39% |

Against the other candidate states:
- **The own queen's death.** Only test4 moves with it: median start 293 / 354 / 391 when she died in rounds 100-199 /
  200-299 / 300-399, never before round 258; with her alive at round 400 it fed a leader in 21 of 56 games and
  otherwise feeds her (queen-feeding starts at round 402-428). The others start with their queen alive in 33-65% of
  games and their start does not move with her death (SSS: 301 / 300 / 293 / 302 for a queen dead before 100 / in
  100-199 / in 200-299 / in 300-399; forgot 313 / 335 / 361 / 370 follows its unit count, not her).
- **The enemy queen's death.** No bot's start moves with it by more than its unit count explains (SSS 293 / 301 / 307
  for an enemy queen dead before 200 / in 200-349 / alive at 350; Vibing++ 363 / 360 / 390).
- **The unit count.** Four of the five tie the clock to it, more units meaning earlier: WHQ 270 at the cap, about 303
  with 30-55, 334 below; forgot 300 and about 370; Vibing++ 360 and about 400; SSS 300, earlier with a full team on
  big ground; ours 200 and 400. A map-size switch would give the same table; the replay cannot tell which of the two
  they test. Units at the start: 60+ in 51 of WHQ's 91 starts, 124 of forgot's 309, 159 of SSS's 291.
- **No enemy near the leader / the enemy's longest.** Not a trigger for anybody: the nearest enemy head is a median 6-9
  cells from the longest dragon 50 rounds before the start, 25 rounds before and at the start, for every team; the
  enemy's longest at the start is 8-15 (median) and its spread is as wide as the unit counts allow.
- **Between the queen's death and the start** the teams do not gather: own heads within 15 cells of the longest dragon
  50 / 25 / 0 rounds before the start: forgot 15 / 14 / 13, SSS 18 / 19 / 18, Vibing++ 17 / 15.5 / 15, WHQ 18 / 17 /
  16, test4 18 / 20 / 15, ours 17 / 15 / 14.5. They keep eating (natural pearls per 50 rounds before the start: forgot
  88 / 83 / 86, SSS 89 / 90 / 88, Vibing++ 102 / 106 / 101; `e_out/h_risk.txt`).

So it is a clock in every bot, set by the unit count (or the map size) in four of them and by the queen in one.

### 2h. The risks, counted

`e_h.py` (`e_out/h_risk.txt`); all study games of the group, any ending.

**The team's longest dragon rammed by an enemy, per 1,000 rounds in which the team had a leader of that length:**

| group | leader 15-24: rounds 150-299 / 300-399 / 400-499 | leader 25-39 | leader 40+ | the rammer was 2-4 / 5-9 / 10+ long |
|---|---|---|---|---|
| meow live bot | 6.9 / 4.6 / 3.8 | 4.8 / 2.4 / 2.9 | - / 4.5 / 2.7 | 38 / 21 / 3 |
| meow test builds | 3.9 / 2.5 / 2.4 | 5.3 / 0 / 4.1 | - / 0 / 2.8 | 12 / 8 / 1 |
| our opponents | 3.1 / 1.2 / 1.2 | 2.5 / 0.8 / 1.1 | 0 / 0 / 1.3 | 31 / 20 / 14 |
| forgot | 5.2 / 1.6 / 3.7 | 6.1 / 1.2 / 2.3 | 0 / 1.0 / 2.1 | 110 / 45 / 10 |
| SSS | 5.9 / 2.0 / 0.9 | 3.3 / 1.7 / 2.3 | 3.6 / 2.1 / 1.9 | 81 / 53 / 5 |
| Vibing++ | 4.3 / 2.6 / 2.1 | 3.5 / 1.5 / 2.0 | 0 / 0 / 2.0 | 90 / 32 / 4 |

An early leader is rammed more often by everybody (4-7 per 1,000 rounds before round 300 against 1-4 after); ours is
rammed two to three times as often as our opponents' at every stage. At 3-4 per 1,000, a leader that exists for 100
rounds is rammed in about one game in three.

**Who starts leader feeding first** (one row per game; "first" = at least 25 rounds before the other side, or alone):

| | this side first: games, won | of them races: won | the other side first: games, won | of them races: won | wipe-outs when first: won |
|---|---|---|---|---|---|
| top-three sides | 531, 352 (66%) | 169 of 238 | 288, 142 (49%) | 65 of 141 | 25 of 30 |
| meow sides | 111, 32 (29%) | 26 of 56 | 102, 10 (10%) | 10 of 74 | 3 of 4 |
| our opponents' sides | 102, 92 (90%) | 64 of 74 | 111, 79 (71%) | 30 of 56 | 9 of 9 |

The first starter wins more races for every group (71% against 46%, 46% against 14%, 86% against 54%) and does not
lose more on wipe-outs or the queen rule. It is not a clean effect of the start: the richer team has more units and
its clock runs earlier.

**What feeding costs** (round-500 games with a start between rounds 150 and 425, medians at the start / 50 / 100
rounds later): units, forgot 52.5 / 30 / 19, SSS 60 / 51 / 45, Vibing++ 56 / 34 / 27, our opponents 61 / 46 / 31;
potential, forgot 97 / 99.5 / 101, SSS 102 / 98 / 105, Vibing++ 110.5 / 108 / 120, our opponents 120 / 124 / 128;
natural pearls eaten in the 50 rounds before, forgot 86 / 74 / 63, SSS 88 / 84 / 78, Vibing++ 101 / 82 / 65.5. Feeding
halves the units in 50-100 rounds, costs a tenth to a third of the natural intake and leaves the potential flat. (Our
own row is not comparable across the columns: our early starts are our richest games.)

**Feeder pearls eaten by the enemy** (all feeders from round 150):

| group | feeders a game | pearls eaten by the enemy | enemy head within 4 cells when the feeder dies (share of feeders): enemy ate | 5-8 cells | 9-15 cells | farther |
|---|---|---|---|---|---|---|
| meow live bot | 22.1 | 5.1% | (5%) 15.4% | (43%) 8.0% | (45%) 2.2% | (8%) 0.6% |
| meow test builds | 23.3 | 3.5% | (5%) 17.6% | (40%) 5.8% | (41%) 1.2% | (14%) 0.0% |
| our opponents | 26.6 | 1.8% | (3%) 8.3% | (36%) 2.9% | (42%) 1.1% | (18%) 0.5% |
| forgot | 18.2 | 0.6% | (2%) 1.5% | (32%) 1.0% | (45%) 0.4% | (21%) 0.1% |
| SSS | 30.5 | 2.1% | (6%) 7.8% | (35%) 3.5% | (44%) 1.0% | (15%) 0.3% |
| Vibing++ | 11.8 | 1.7% | (11%) 5.0% | (30%) 2.9% | (44%) 0.7% | (15%) 0.7% |

"Our late feeding often feeds the opponent" is one pearl in twenty: two to eight times the others' share, almost all of
it when an enemy head is within 8 cells (our rule asks only for more than 4). Seven times as many of our feeders'
pearls go to another small dragon of our own.
