# Close read 5: how the longest-dragon race is won, and why we lose it (sub-session A5)

Written 2026-10-05 for team meow (id 1119). This file answers one question of the top-team study: when a game reaches
round 500 with both queens dead, the longest single dragon wins (a "race" below); we win 41 of 143 such games against
teams rated 2000 or more and the three top teams win 266 of 447. What do the winners do in the last 250 rounds that we
do not, and does a general rule follow?

## 1. The three findings that matter most

Four words are needed here; the full list is under "Words" below. **Potential** is a team's longest dragon plus the
pearls all its other dragons would drop if they died now: what the leader would be if the whole team were fed to it
without loss. **Completeness** is the longest dragon divided by the potential. A **cut** is a split in which the
longest dragon keeps 2 segments and hands the rest to a new dragon with a new id. A dragon **dies by choice** when it
dies with a free cell next to its head and not in a ram; that is how every bot feeds its leader.

**1. Most of the gap is not in the race; the comparison that showed it used the wrong footing. A smaller gap is real.**
The red team compared games with level TOTAL length at round 400 (we win 9 of 30 on small maps, the top three 22 of
40). But a team that has started feeding has already paid for it: a 2-long feeder leaves 1 pearl. In those 30 games of
ours the enemy had 90.5 total length against our 65.5 at round 300 (medians) and was "level" at 400 only because it had
converted; in the top three's 40 games the top team was ahead at 300 (101 against 94). Potential does not have that
flaw. With own potential / enemy potential between 0.8 and 1.25 **at round 300 we win 11 of 23 races, at round 350 12
of 24** (our opponents in those same games 12 of 22 and 12 of 24; the top three 99 of 169 and 103 of 178). What decides
most of our races is that we enter them behind: median ratio 0.62 at round 300, 106 of the 143 races below 0.8 (20
won, the top three 23 of 94 in that state). What is left of the gap: against test4 and WHQ only, at level potential
at round 350, we win 10 of 21 and the top three 11 of 13 (SSS 7 of 9). And one thing nobody does well: on big maps
every team ends with only 39-49% of its potential in its longest dragon (ours 43%, test4 29%), so a race there can be
won by the less scattered team against a richer one (`e_p300.py`, `e_level.py`, `e_p.py`, `e_cdist.py`).

**2. A race is won by one dragon that stays the leader while the team knows which dragon that is. Ours changes id
about three times in the last hundred rounds, as everybody's does; ours is the team that does not notice, for 27
rounds each time.** Feeding is mechanically the same in every bot: small dragons die one to three steps from a much
longer own dragon and half their length drops as pearls. Measured the same way for every team (every death by choice
in a race from round 300 on; `e_dist.py`), our result per pearl is ordinary: the lineage of our final longest eats
39% of those pearls on small maps (our opponents 39%, the top three 45%) and 26% on big maps (16% and 29%). Three
things break the mechanism:
- (a) *The leader changes id.* A long dragon in closed ground runs into pockets; every bot then cuts. Counted on the
  dragon that ends as the longest, from round 400, that is 2.7 cuts a race for us and 1.6-3.3 for the others
  (`e_cutcost.py`); counted on whichever dragon is the longest at the moment, 3.8-4.1 against 1.9-4.1: we are at the
  upper end, not outside. Ours come a little early (1.7 of the 2.7 with a free cell left; when one of our leaders cuts with
  a free cell left, the pocket ahead holds four cells or fewer in 78% of cases on small maps and 65% on big ones;
  `e_cutctx.py`). Each costs 2 segments: in 10 of our 102 lost races the segments left behind from round 400 are more
  than the losing margin (the top three: 25 of 181 losses). Five of our ten are among the 14 losses read (games 5, 6,
  8, 12, 13), one of them by a chain of six cuts in a single round at 35 against 36 with 46 potential against 36
  (game 8, round 478). This part is a cost of long dragons, not a habit of ours, and nothing below tries to remove
  it.
- (b) *The team does not follow.* Every dragon of ours keeps one record of "the leader" and sends it on its sonar
  pings; in 78 of our games those pings can be read. After a cut the old id's last report (longer, up to 25 rounds
  old) outranks the new dragon in every team-mate's record, so the team keeps guarding the pearls of, and waiting
  for, a dragon that is now 2 long or dead: it takes a median of 27 rounds until half of our dragons name the new
  longest (388 cuts). In rounds 400-494 fewer than a quarter name the true longest in 187 of 347 samples; the longest
  then grows 0.4 segments per 5 rounds, against 1.5 to 2.0 when more do. In 25-round windows with a cut our longest
  grows 5.0, without one 10.8 (our opponents: 6.0 and 6.9; the same split holds against test4, against WHQ and
  against everybody else). In game 1 no feeder dies next to our 31-34-long leader for 32 rounds, and five die in the
  two rounds in which the dead leader's record runs out.
- (c) *Feeders die next to nothing.* A quarter of our deaths by choice in a race are within reach of no bigger own
  dragon at all (25% on small maps; our opponents 15%, the top three 10%), and the final longest gets 13% of those
  pearls against 70% when the death is next to the longest (`e_dist.py`).

One more difference exists against our two usual opponents only: test4 and WHQ also feed whole dragons to the
leader. On small maps they drop 26-29 pearls a race from dragons of 5 or longer and give the leader 1.3-1.5 dragons
of 8+ in the last 50 rounds (5 to 7 segments); we drop 5-9 and give 0.3, as rarely as the top three do
(`e_merge.py`). Our rule allows a dragon to feed only a leader it believes to be twice its own length.

The one race of ours read in which the leader kept its id from round 325 to 475 (1023828, against forgot) is also the
one in which 67-88% of the team named it between rounds 325 and 400, all 30 feeders that died next to a bigger dragon
died next to it, it grew 52 in the 50 rounds after round 400, and we won 92 to 84 with less potential
(`e_churn.py`, `e_bel.py`, `e_opp.py`, `e_sum.py`, section 4). And in our level races (potential ratio 0.8-1.25 at
round 350; 12 won, 12 lost) winners and losers both start feeding at round 402-403 and the losers are ahead at round
450 (31 against 27.5); the winners end at 48.5 and the losers at 30, with 6.6 cuts of the final longest from round 400
against 3.6 and 12.5 units left against 5 (`e_wl.py`).

**3. When to start is not what separates winners; every bot runs a clock tied to its unit count, ours is the outlier
at both ends, and the "leader zone" that precedes it feeds the leader nothing.** Start of leader feeding (median): WHQ
round 270 with 56+ units, about 300-335 with fewer; SSS about 300; forgot 300 with 56+ units, about 370 otherwise;
Vibing++ 360 and about 400; test4 about 90 rounds after its own queen dies and never while she lives (in game 22 it
had 406 total length against our 206 at round 400 and lost the race 49 to 69 that way); ours round 200 with 56 units
and 400 otherwise. Vibing++, rank 1, starts as late as we do on small maps and ends with the lowest completeness of
all (0.59; ours 0.65-0.71; WHQ 0.80): it wins races on potential. Completeness falls with team size for every bot
(45+ units at round 400: median 0.56 on small maps, 0.37 on big; 10-19 units: 0.75 and 0.67). And before feeding, our
pearl zone does not do its job: after the switch a small dragon of ours takes a free pearl inside its believed
leader's zone in 18-26% of turns and outside it in 75-87%; the team's natural intake falls by a quarter on small maps
and a third on big ones; the leader of the time eats 2 to 3 natural pearls per 50 rounds in races after the switch
(2.5-2.9 on small maps, 1.6-2.2 on big ones), no more than before it and no more than a top team's leader does
without any zone (2.3-2.8). On big maps our feeding from round 200 spends about 20 segments per 50 rounds for 2 pearls
to the final leader; our longest is 10 at round 200 and 14 at round 400 (`e_e.py`, `e_d.py`, `e_b.py`, `e_cdist.py`).

What follows from it is **candidate 5, "one leader, known to all"** (section 7): the dragon the team feeds keeps its
role through its own cuts (fresher news of a nearly-as-long dragon replaces old news of a longer one), and a dragon
gives its life only next to a leader it can see is long. Strict reading: 6 to 12 of our 102 lost races turn if the
leader's growth after round 400 rises by a quarter to a half (the measured contrast between 25-round windows with
and without a cut is a factor of 2.2); realistic +0.7 to +2.2 points, most likely a little over +1. It moves no
clock and names no map. It is a repair of our own mechanism, not a copy of somebody else's: on the measures above the
top teams are not far ahead of us in the race itself; they arrive with more.

## How it was done

One script (`e_walk.py`) walked 1,795 replays once, both sides of every game: all 401 of our games against 2000+
teams (map Schooltime left out, as everywhere in this study) and all 1,637 game-sides of Vibing++ (id 306), SSS (91)
and "forgot to mention" (264). It writes one file per game (`e_out/w4/<game>.json`) and every table below is read
from those files by a script that is named next to it (a second walk, `e_cutctx.py`, adds the situation at every
leader cut). Then 30 games were read closely with `e_show.py`, `e_feed.py`, `e_cutlist.py`, `story.py` and
`e_belief.py`: 22 of ours (the 14 losses the red team listed, 4 level wins, 4 wins from behind on big maps) and 8 of
the top three in the same kind of game. I ran no game and used no network. "Measured" means counted by a script on
replays; "inference" marks a reading of the bot source or of what a dragon intended. A replay shows positions,
orders, deaths, pearls and sonar pings; it does not show what a bot knew, with one exception that this file uses a
lot: our own bot writes the leader it believes in into its sonar pings, and in 78 of our games those pings can be
read (see "belief" below).

## Words

- **Queen**: each team's lowest-numbered dragon. At round 500 a living queen beats a dead one; with both dead the
  longest single dragon wins. Such a game is called a **race** here. We have 143, the top three 447.
- **Leader**: a team's longest dragon at the start of a round. **Lineage**: the dragon that is the longest at the end
  of the game, followed back in time; where it was born in a split, the lineage continues with its parent.
- **By choice**: a death that is not a ram, of a dragon that had at least one free cell next to its head at the start
  of its own turn (a cell with no body segment on it; kelp and portals respected). **Boxed in**: any other death that
  is not a ram.
- **Feeder**: a dragon that dies by choice within 3 steps of the head of an own dragon at least twice as long. For our
  own bot every `noaction` death is also counted in the tables that say so, wherever it happens, because that is how
  our feeders die: the bot returns without an order when `ready_to_die()` is true. **The dragon fed**: that longer
  dragon. Where teams are compared, the table "The same test for every team" (section 2) uses one definition for all.
- **Potential (P)**: the leader's length plus the pearls every other own dragon would drop if it died now (a dead
  dragon of length L drops ceil(L/2) pearls). It is what the leader would be if the whole team were fed to it without
  loss. Feeding does not change P: a 2-long feeder is worth 1 before and 1 after. A natural pearl adds 1 to P when the
  leader eats it and about half when a small dragon does. **Completeness (c)** = leader / P. The final longest dragon
  is P x c at round 500, so a race is decided by those two numbers.
- **Leader cut**: a split in which the team's longest dragon (8 or longer) keeps 2-3 segments at its head and gives
  the rest to a new dragon with a new id, whose head is the old tail. The part that stays is the **stub**, the new
  dragon the **heir**. Our bot does it when its best move leads into a pocket of 4 cells or fewer
  (`escape_child_size()`), when every move is inside an enemy's reach (the `cornered` split in `act()`), or when it
  has no move at all.
- **Belief**: every dragon of ours remembers one leader: the id, length and position of the longest own dragon it has
  seen or heard of in the last 25 rounds (`known_leader_id`, `SONAR_STALE 25`). After each turn it sends that record on
  four sonar rays (`broadcast_leader()`); a ray reaches the first dragon or kelp in its line. The pearl zone, the
  choice of whom to feed and the "I am the leader" test all read this one record. In the replays of the earlier live
  bot (ladder download of 3 October, the first 31 games of 4 October and the run "stride-old": 83 games, 78 of them in
  the study) the record is readable in the ping value; later builds seal the ping and I did not unseal it (the key is
  in the bot source; copying it into this directory would spread a secret for no gain, since the leader code is the
  same in all builds).
- **Pearl zone**: from round 300 (round 150 on big maps) our small dragons do not take pearls within 9 cells of the
  leader in their record (`LEADER_PEARL_RADIUS 9`).
- **Small maps / big maps**: 1,200 cells or fewer / more. Only because our own code switches there
  (`AGGRESSIVE_MAX_CELLS 1200`); nothing proposed below uses a map size.
- **Live bot / test builds**: 275 of our 401 games were played by the released bot of that hour, 126 by test builds
  (stride, passage2, qh31, tc30). None changed the leader or feeding code. 313 of the 401 are against test4 (id 19)
  and WeHaveQuizzes (id 87, "WHQ").
- **Point**: one percentage point of win rate. One game of our 401 is 0.25 points.

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

### Maps of 1,200 cells or fewer

**Table A1 (maps of 1,200 cells or fewer). The curve.** Round-500 games with both queens dead, all of them. Medians.

| group | games | won | longest at 200 / 250 / 300 / 350 / 400 / 450 / end | enemy's longest at 300 / 400 / end | units 300 / 400 / end | total length 300 / 400 / end | P (potential) 300 / 400 / end | c = longest / P at 400 / 450 / end |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| meow live bot | 53 | 18 | 4 / 4 / 4 / 9 / 10 / 16 / 20 | 6 / 17 / 37 | 26 / 21 / 7 | 65 / 68 / 54 | 40 / 44 / 38 | 0.27 / 0.53 / 0.65 |
| meow test builds | 25 | 11 | 4 / 4 / 4 / 8 / 11 / 21 / 30 | 5 / 20 / 37 | 22 / 21 / 4 | 57 / 78 / 53 | 34 / 50 / 44 | 0.20 / 0.51 / 0.71 |
| our opponents | 78 | 49 | 5 / 4 / 5.5 / 11 / 18.5 / 33.5 / 37 | 4 / 11 / 25 | 33 / 18.5 / 4 | 89.5 / 80 / 65 | 53 / 53 / 52 | 0.43 / 0.65 / 0.77 |
| test4 (vs us) | 29 | 18 | 5 / 4 / 6 / 6 / 13 / 30 / 37 | 4 / 12 / 25 | 33 / 16 / 3 | 90 / 76 / 55 | 53 / 51 / 47 | 0.41 / 0.64 / 0.77 |
| WHQ (vs us) | 39 | 28 | 5 / 5 / 5 / 16 / 28 / 40 / 45 | 4 / 10 / 25 | 33 / 23 / 4 | 95 / 82 / 66 | 57 / 60 / 60 | 0.43 / 0.65 / 0.80 |
| forgot | 65 | 37 | 4 / 5 / 5 / 5 / 16 / 27 / 36 | 5 / 9 / 23 | 24 / 14 / 6 | 68 / 66 / 62 | 42 / 45 / 49 | 0.43 / 0.60 / 0.69 |
| SSS | 42 | 23 | 4 / 4 / 6.5 / 16.5 / 26 / 36 / 38.5 | 4 / 12.5 / 36 | 37.5 / 19 / 6 | 95 / 85 / 66 | 56 / 58.5 / 54.5 | 0.43 / 0.63 / 0.79 |
| Vibing++ | 67 | 47 | 5 / 5 / 6 / 5 / 9 / 25 / 36 | 4 / 9 / 22 | 29 / 25 / 8 | 72 / 78 / 73 | 43 / 49 / 54 | 0.19 / 0.48 / 0.59 |

**Table A2 (maps of 1,200 cells or fewer). The same at level potential** (own P / enemy P at round 400 between 0.8 and 1.25).

| group | games | won | longest at 300 / 350 / 400 / 450 / end | enemy's longest at 300 / 350 / 400 / 450 / end | P at 300 / 400 / end, own : enemy | c at 400 / 450 / end, own : enemy | units at 400 / end, own : enemy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| meow live bot | 18 | 5 | 4 / 11 / 12.5 / 22.5 / 34.5 | 6 / 8.5 / 15.5 / 33 / 40 | 42.5 : 60.5 / 45.5 : 49.5 / 46.5 : 46.5 | 0.22 : 0.33 / 0.51 : 0.67 / 0.59 : 0.78 | 24 : 20.5 / 11 : 4 |
| meow test builds | 9 | 3 | 5 / 10 / 13 / 28 / 28 | 7 / 12 / 16 / 34 / 37 | 34 : 53 / 47 : 51 / 36 : 44 | 0.23 : 0.34 / 0.56 : 0.69 / 0.74 : 0.88 | 18 : 20 / 4 : 2 |
| our opponents | 26 | 19 | 6 / 10 / 15 / 33 / 40 | 5 / 10 / 12.5 / 22.5 / 32.5 | 54 : 39.5 / 49.5 : 46 / 45.5 : 45 | 0.32 : 0.22 / 0.70 : 0.51 / 0.87 : 0.68 | 20 : 20.5 / 3 : 8 |
| test4 (vs us) | 14 | 10 | 7 / 9.5 / 17 / 32.5 / 42 | 5 / 11.5 / 13 / 20.5 / 26.5 | 58.5 : 41.5 / 51.5 : 48 / 46.5 : 42.5 | 0.34 : 0.22 / 0.68 : 0.44 / 0.85 : 0.57 | 17.5 : 22 / 3 : 8.5 |
| WHQ (vs us) | 11 | 9 | 4 / 11 / 12 / 32 / 37 | 4 / 9 / 10 / 23 / 36 | 47 : 33 / 42 : 42 / 44 : 47 | 0.29 : 0.23 / 0.70 : 0.56 / 0.94 : 0.71 | 22 : 20 / 2 : 6 |
| forgot | 14 | 6 | 8 / 15 / 20.5 / 37.5 / 51 | 5 / 10 / 18 / 34 / 42 | 61 : 55.5 / 55.5 : 53 / 58 : 59.5 | 0.39 : 0.35 / 0.58 : 0.56 / 0.67 : 0.72 | 16 : 18 / 10 : 11 |
| SSS | 16 | 9 | 5.5 / 23 / 32 / 37.5 / 43 | 7 / 11.5 / 21 / 30 / 41 | 57 : 56 / 58.5 : 58 / 50 : 56.5 | 0.50 : 0.32 / 0.64 : 0.53 / 0.79 : 0.59 | 19 : 20 / 6.5 : 7.5 |
| Vibing++ | 10 | 6 | 11.5 / 13 / 12.5 / 34 / 40.5 | 5 / 8 / 15 / 22 / 38.5 | 53 : 55 / 63 : 64.5 / 57.5 : 60 | 0.25 : 0.22 / 0.53 : 0.52 / 0.61 : 0.65 | 26.5 : 17 / 11 : 10.5 |

**Table A3 (maps of 1,200 cells or fewer). When it starts and how fast.** Start of leader feeding = first of three feeder deaths within 15 rounds; take-off = first round from which the longest dragon grows by 8+ within 25 rounds.

| group | games | longest first 8 / 15 / 25 long (median round; never) | lineage first 8 / 15 / 25 long | start of leader feeding: quartile / median / quartile (games without) | take-off: median round (never) | growth of the longest in the 50 rounds after take-off | growth of the longest from round 400 to the end |
| --- | --- | --- | --- | --- | --- | --- | --- |
| meow live bot | 53 | 311 (4) / 402 (14) / 423 (25) | 336 (4) / 406 (16) / 426 (26) | 401 / 401 / 406 (9) | 385 (16) | 11 | 10 |
| meow test builds | 25 | 304.5 (1) / 404 (4) / 422.5 (9) | 354 (4) / 407 (6) / 423.5 (9) | 401 / 401 / 408 (3) | 390 (5) | 18.5 | 21 |
| our opponents | 78 | 277 (1) / 358 (7) / 395.5 (14) | 345 (3) / 388 (12) / 410 (18) | 307 / 329 / 375 (13) | 345 (11) | 15 | 24 |
| test4 (vs us) | 29 | 282.5 (1) / 392 (4) / 410 (5) | 386 (2) / 401.5 (5) / 421 (6) | 320 / 354 / 376 (5) | 370 (4) | 16 | 22 |
| WHQ (vs us) | 39 | 209 (0) / 338 (1) / 369 (5) | 323 (0) / 364 (4) / 389 (8) | 295 / 315 / 347 (4) | 312.5 (3) | 14 | 26 |
| forgot | 65 | 279 (3) / 379 (10) / 400 (21) | 374 (4) / 394 (11) / 417 (21) | 370 / 373 / 396 (18) | 355 (14) | 14 | 20 |
| SSS | 42 | 272 (3) / 337 (6) / 370 (11) | 312 (3) / 356.5 (8) / 372 (15) | 302 / 311 / 330 (5) | 315 (8) | 17 | 15.5 |
| Vibing++ | 67 | 165 (2) / 410 (6) / 426.5 (17) | 394 (2) / 424 (8) / 438 (21) | 400 / 403 / 420 (14) | 390 (11) | 18.5 | 20 |

**Table B1 (maps of 1,200 cells or fewer). Where the final longest dragon's length comes from** (its lineage; mean pearls per game in rounds 250-299 / 300-349 / 350-399 / 400-449 / 450-499).

| group | natural pearls | pearls of own dragons dead by choice | pearls of other own corpses (boxed in, rammed) | pearls of enemy corpses | segments left behind in leader cuts | whole team: natural pearls eaten | whole team: length of dragons dead by choice |
| --- | --- | --- | --- | --- | --- | --- | --- |
| meow live bot | 4.0 / 5.0 / 3.7 / 3.5 / 5.0 | 0.1 / 0.2 / 0.2 / 10.2 / 6.1 | 2.2 / 2.0 / 2.0 / 1.7 / 1.5 | 0.2 / 0.4 / 0.3 / 0.4 / 1.2 | 0.0 / 0.7 / 1.4 / 2.3 / 3.7 | 45.7 / 36.7 / 35.8 / 25.0 / 22.5 | 7 / 4 / 4 / 49 / 27 |
| meow test builds | 5.4 / 2.2 / 4.2 / 3.6 / 4.0 | 0.0 / 0.1 / 0.4 / 13.6 / 10.4 | 2.8 / 2.8 / 2.4 / 2.2 / 0.8 | 0.1 / 0.2 / 0.2 / 0.3 / 0.3 | 0.3 / 0.6 / 1.4 / 2.4 / 3.7 | 52.6 / 41.6 / 44.2 / 30.2 / 23.4 | 4 / 3 / 3 / 56 / 35 |
| our opponents | 3.0 / 3.6 / 3.6 / 4.4 / 5.0 | 0.9 / 4.4 / 8.9 / 10.9 / 7.9 | 2.3 / 2.2 / 2.1 / 1.6 / 1.3 | 0.2 / 0.2 / 0.2 / 0.5 / 0.4 | 0.2 / 0.8 / 1.5 / 1.9 / 2.8 | 55.5 / 50.6 / 46.3 / 31.5 / 22.1 | 10 / 25 / 46 / 50 / 30 |
| test4 (vs us) | 3.0 / 4.0 / 4.2 / 5.1 / 5.1 | 0.1 / 1.4 / 8.1 / 10.7 / 8.6 | 2.7 / 2.2 / 2.1 / 1.1 / 1.0 | 0.3 / 0.2 / 0.1 / 0.2 / 0.7 | 0.1 / 0.2 / 1.0 / 1.8 / 4.5 | 56.4 / 54.1 / 49.8 / 26.0 / 18.9 | 3 / 13 / 60 / 45 / 26 |
| WHQ (vs us) | 3.1 / 3.7 / 3.2 / 3.5 / 4.3 | 1.6 / 7.2 / 9.5 / 12.0 / 8.2 | 2.1 / 2.6 / 2.2 / 1.8 / 1.6 | 0.2 / 0.2 / 0.2 / 0.6 / 0.2 | 0.1 / 1.3 / 1.8 / 1.9 / 1.3 | 58.3 / 52.0 / 45.6 / 34.5 / 21.3 | 17 / 38 / 41 / 58 / 34 |
| forgot | 3.9 / 3.5 / 4.5 / 5.3 / 7.0 | 0.4 / 0.6 / 7.8 / 8.6 / 6.0 | 2.0 / 2.6 / 2.7 / 2.4 / 3.3 | 0.2 / 0.4 / 0.4 / 0.7 / 0.8 | 0.1 / 0.8 / 0.9 / 2.7 / 4.8 | 45.7 / 46.9 / 40.2 / 33.9 / 27.8 | 5 / 7 / 29 / 31 / 20 |
| SSS | 3.0 / 2.0 / 2.2 / 2.1 / 2.7 | 0.1 / 6.6 / 7.9 / 7.5 / 6.9 | 2.1 / 1.5 / 1.6 / 0.8 / 1.1 | 0.2 / 0.2 / 0.5 / 0.3 / 0.3 | 0.0 / 0.4 / 1.5 / 1.5 / 0.9 | 55.9 / 47.4 / 44.9 / 30.3 / 22.9 | 3 / 35 / 33 / 36 / 26 |
| Vibing++ | 3.5 / 3.7 / 4.3 / 5.1 / 6.8 | 0.8 / 1.6 / 2.2 / 10.3 / 6.1 | 2.0 / 2.0 / 2.0 / 1.8 / 1.9 | 0.2 / 0.1 / 0.3 / 0.5 / 0.5 | 0.4 / 0.6 / 0.9 / 2.1 / 1.8 | 68.1 / 66.8 / 64.6 / 50.3 / 47.0 | 7 / 9 / 9 / 39 / 22 |

**Table B2 (maps of 1,200 cells or fewer). Feeders from round 250.**

| group | feeders a game | mean length | pearls dropped a game | eaten by the dragon fed | by other own dragons | by the enemy | by nobody | the dragon fed is the team's longest | is under 10 long | path steps to the fed dragon's head: 1 / 2 / 3 / more or none | nearest enemy head (median cells) | final lineage's gain per feeder segment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| meow live bot | 28.2 | 2.43 | 38.5 | 54% | 36% | 3.4% | 7% | 52% | 45% | 5% / 23% / 40% / 33% | 9 | 0.23 |
| meow test builds | 30.9 | 2.52 | 43.5 | 59% | 34% | 1.9% | 5% | 54% | 43% | 5% / 27% / 40% / 28% | 9 | 0.29 |
| our opponents | 32.8 | 2.88 | 53.2 | 71% | 26% | 0.9% | 2% | 60% | 32% | 20% / 39% / 42% / 0% | 8 | 0.24 |
| test4 (vs us) | 26.9 | 3.32 | 49.9 | 69% | 29% | 1.1% | 1% | 60% | 42% | 10% / 39% / 51% / 0% | 8 | 0.24 |
| WHQ (vs us) | 40.1 | 2.67 | 60.5 | 73% | 25% | 0.8% | 2% | 61% | 28% | 25% / 38% / 37% / 0% | 8 | 0.24 |
| forgot | 22.3 | 2.71 | 34.5 | 78% | 21% | 0.4% | 1% | 67% | 20% | 14% / 36% / 49% / 0% | 9 | 0.28 |
| SSS | 40.5 | 2.47 | 54.2 | 77% | 21% | 0.9% | 1% | 83% | 22% | 65% / 25% / 10% / 0% | 8 | 0.27 |
| Vibing++ | 15.4 | 2.65 | 23.1 | 77% | 20% | 0.8% | 1% | 63% | 29% | 12% / 41% / 47% / 0% | 10 | 0.29 |

**Table C1 (maps of 1,200 cells or fewer). Who the leader is and whether it lasts.**

| group | longest at round 400 is the final longest: same id / same lineage | at round 450 | leader cuts a game, rounds 300-394 / 395-499 | of the cuts from 395: made with a free cell | growth of the longest per 25 rounds from 400 (10+ other dragons left): windows with a cut in them or just before / without (number of windows) | longest dragon (15+) died: per game (rammed / boxed in / by choice / own ram) | leader at 400 / 450: cells to the nearest enemy head | steps it took per 25 rounds at 400 / 450 | end: second longest / longest | units at the end |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| meow live bot | 15% / 60% | 28% / 81% | 2.3 / 3.8 | 68% | 4.0 / 13.4 (83 / 38) | 0.13 (6 / 0 / 0 / 1) | 7 / 9 | 53 / 59 | 0.33 | 7 |
| meow test builds | 12% / 56% | 32% / 88% | 3.5 / 4.0 | 66% | 9.9 / 9.7 (42 / 13) | 0.04 (1 / 0 / 0 / 0) | 6 / 9 | 65 / 79 | 0.37 | 4 |
| our opponents | 12% / 62% | 41% / 79% | 2.6 / 2.3 | 40% | 6.8 / 7.9 (80 / 54) | 0.15 (3 / 3 / 6 / 0) | 6 / 9 | 38 / 41 | 0.27 | 4 |
| test4 (vs us) | 3% / 59% | 31% / 76% | 2.7 / 2.4 | 70% | 8.5 / 7.6 (27 / 17) | 0.10 (1 / 2 / 0 / 0) | 5 / 9 | 38 / 36 | 0.29 | 3 |
| WHQ (vs us) | 18% / 64% | 54% / 85% | 2.8 / 2.0 | 18% | 5.7 / 8.3 (41 / 34) | 0.21 (1 / 1 / 6 / 0) | 7 / 9 | 35 / 41 | 0.23 | 4 |
| forgot | 5% / 52% | 11% / 72% | 1.0 / 4.1 | 15% | 8.7 / 5.9 (82 / 16) | 0.22 (12 / 0 / 0 / 0) | 7 / 7 | 52 / 56 | 0.30 | 6 |
| SSS | 31% / 79% | 55% / 81% | 1.6 / 2.0 | 93% | 2.4 / 6.2 (53 / 47) | 0.24 (5 / 0 / 1 / 4) | 7.5 / 7.5 | 40 / 41 | 0.15 | 6 |
| Vibing++ | 6% / 42% | 30% / 76% | 3.4 / 2.6 | 61% | 8.0 / 5.8 (119 / 65) | 0.33 (7 / 2 / 9 / 4) | 7 / 8 | 43 / 52 | 0.39 | 8 |

### Maps over 1,200 cells

**Table A1 (maps over 1,200 cells). The curve.** Round-500 games with both queens dead, all of them. Medians.

| group | games | won | longest at 200 / 250 / 300 / 350 / 400 / 450 / end | enemy's longest at 300 / 400 / end | units 300 / 400 / end | total length 300 / 400 / end | P (potential) 300 / 400 / end | c = longest / P at 400 / 450 / end |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| meow live bot | 43 | 9 | 10 / 13 / 13 / 14 / 14 / 23 / 35 | 25 / 38 / 69 | 52 / 45 / 20 | 151 / 138 / 150 | 91 / 82 / 100 | 0.24 / 0.34 / 0.43 |
| meow test builds | 22 | 3 | 9 / 10.5 / 14 / 12.5 / 14.5 / 24 / 27.5 | 23.5 / 48.5 / 66.5 | 53 / 45 / 18.5 | 156 / 152 / 118.5 | 95 / 93.5 / 81.5 | 0.24 / 0.35 / 0.43 |
| our opponents | 65 | 53 | 15 / 17 / 24 / 37 / 43 / 59 / 68 | 14 / 14 / 31 | 61 / 46 / 13 | 320 / 337 / 275 | 184 / 199 / 177 | 0.22 / 0.31 / 0.40 |
| test4 (vs us) | 20 | 14 | 15 / 17 / 18.5 / 20.5 / 24 / 32.5 / 51 | 16.5 / 15.5 / 37 | 63 / 61.5 / 27.5 | 368.5 / 370 / 295.5 | 206.5 / 210 / 175 | 0.12 / 0.17 / 0.29 |
| WHQ (vs us) | 35 | 33 | 15 / 18 / 30 / 47 / 55 / 68 / 83 | 11 / 12 / 29 | 60 / 44 / 9 | 320 / 340 / 275 | 183 / 208 / 178 | 0.29 / 0.36 / 0.48 |
| forgot | 89 | 48 | 6 / 10 / 13 / 29 / 41 / 52 / 55 | 12 / 27 / 49 | 61 / 32 / 11 | 175 / 183 / 156 | 108 / 118 / 113 | 0.35 / 0.45 / 0.49 |
| SSS | 99 | 59 | 13 / 16 / 18 / 33 / 41 / 49 / 56 | 13 / 32 / 50 | 61 / 52 / 31 | 210 / 201 / 210 | 125 / 134 / 141 | 0.29 / 0.38 / 0.42 |
| Vibing++ | 85 | 52 | 13 / 14 / 15 / 19 / 36 / 46 / 57 | 12 / 27 / 45 | 60 / 40 / 20 | 208 / 209 / 248 | 124 / 130 / 160 | 0.27 / 0.35 / 0.39 |

**Table A2 (maps over 1,200 cells). The same at level potential** (own P / enemy P at round 400 between 0.8 and 1.25).

| group | games | won | longest at 300 / 350 / 400 / 450 / end | enemy's longest at 300 / 350 / 400 / 450 / end | P at 300 / 400 / end, own : enemy | c at 400 / 450 / end, own : enemy | units at 400 / end, own : enemy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| meow live bot | 6 | 5 | 25.5 / 39.5 / 47 / 42.5 / 56.5 | 18.5 / 19.5 / 26 / 36.5 / 44 | 141 : 172 / 165.5 : 171 / 195.5 : 140.5 | 0.28 : 0.14 / 0.24 : 0.25 / 0.29 : 0.29 | 56.5 : 49.5 / 47 : 23 |
| our opponents | 7 | 2 | 19 / 21 / 26 / 38 / 49 | 27 / 46 / 48 / 43 / 58 | 162 : 138 / 161 : 164 / 131 : 191 | 0.14 : 0.29 / 0.27 : 0.25 / 0.32 : 0.30 | 49 : 57 / 19 : 47 |
| test4 (vs us) | 3 | 1 | 16 / 18 / 23 / 33 / 52 | 24 / 46 / 48 / 43 / 55 | 184 : 138 / 199 : 167 / 157 : 201 | 0.13 : 0.29 / 0.21 : 0.25 / 0.34 : 0.28 | 49 : 55 / 19 : 47 |
| forgot | 39 | 23 | 15 / 30 / 46 / 55 / 60 | 12 / 19 / 28 / 33 / 49 | 109 : 108 / 118 : 121 / 113 : 149 | 0.34 : 0.22 / 0.43 : 0.27 / 0.48 : 0.37 | 33 : 53 / 11 : 23 |
| SSS | 43 | 25 | 17 / 30 / 38 / 46 / 55 | 14 / 24 / 34 / 46 / 51 | 120 : 118 / 128 : 131 / 131 : 145 | 0.27 : 0.26 / 0.35 : 0.36 / 0.40 : 0.40 | 52 : 46 / 29 : 20 |
| Vibing++ | 33 | 20 | 18 / 20 / 37 / 48 / 57 | 14 / 25 / 31 / 36 / 47 | 129 : 106 / 128 : 120 / 169 : 124 | 0.29 : 0.28 / 0.37 : 0.33 / 0.39 : 0.42 | 40 : 49 / 20 : 18 |

**Table A3 (maps over 1,200 cells). When it starts and how fast.** Start of leader feeding = first of three feeder deaths within 15 rounds; take-off = first round from which the longest dragon grows by 8+ within 25 rounds.

| group | games | longest first 8 / 15 / 25 long (median round; never) | lineage first 8 / 15 / 25 long | start of leader feeding: quartile / median / quartile (games without) | take-off: median round (never) | growth of the longest in the 50 rounds after take-off | growth of the longest from round 400 to the end |
| --- | --- | --- | --- | --- | --- | --- | --- |
| meow live bot | 43 | 0 (0) / 211 (5) / 290.5 (13) | 256 (0) / 346 (7) / 425 (14) | 201 / 212 / 342 (7) | 215 (10) | 9 | 14 |
| meow test builds | 22 | 0 (0) / 190 (3) / 217 (7) | 211 (1) / 273 (5) / 451 (9) | 202 / 227 / 300 (4) | 215 (5) | 13 | 9.5 |
| our opponents | 65 | 0 (0) / 139 (0) / 267 (0) | 196 (0) / 276 (1) / 352 (2) | 270 / 271 / 321 (2) | 260 (2) | 12 | 25 |
| test4 (vs us) | 20 | 0 (0) / 143.5 (0) / 317.5 (0) | 167.5 (0) / 307 (1) / 419 (2) | 268 / 328 / 383 (2) | 187.5 (2) | 8.5 | 25.5 |
| WHQ (vs us) | 35 | 0 (0) / 153 (0) / 267 (0) | 203 (0) / 272 (0) / 294 (0) | 270 / 270 / 271 (0) | 260 (0) | 13 | 28 |
| forgot | 89 | 122 (0) / 251 (0) / 322 (0) | 298 (0) / 326 (2) / 354 (6) | 300 / 303 / 345 (1) | 270 (0) | 14 | 18 |
| SSS | 99 | 96 (0) / 198 (0) / 303.5 (1) | 220 (0) / 280 (2) / 323 (9) | 207 / 277 / 300 (0) | 285 (0) | 12 | 19 |
| Vibing++ | 85 | 23 (0) / 160 (0) / 364 (1) | 177 (0) / 330 (1) / 380 (5) | 353 / 360 / 364 (3) | 337.5 (1) | 16 | 19 |

**Table B1 (maps over 1,200 cells). Where the final longest dragon's length comes from** (its lineage; mean pearls per game in rounds 250-299 / 300-349 / 350-399 / 400-449 / 450-499).

| group | natural pearls | pearls of own dragons dead by choice | pearls of other own corpses (boxed in, rammed) | pearls of enemy corpses | segments left behind in leader cuts | whole team: natural pearls eaten | whole team: length of dragons dead by choice |
| --- | --- | --- | --- | --- | --- | --- | --- |
| meow live bot | 3.1 / 2.0 / 2.6 / 2.8 / 4.1 | 1.7 / 2.6 / 1.7 / 9.0 / 5.6 | 1.2 / 0.9 / 0.9 / 0.5 / 0.6 | 0.8 / 0.7 / 1.0 / 1.1 / 3.7 | 1.1 / 1.9 / 2.5 / 2.0 / 2.9 | 52.6 / 47.4 / 47.2 / 47.8 / 52.5 | 18 / 20 / 20 / 48 / 40 |
| meow test builds | 2.8 / 3.1 / 1.1 / 2.8 / 4.5 | 1.9 / 2.7 / 2.7 / 6.0 / 7.5 | 1.4 / 1.5 / 0.4 / 0.4 / 1.4 | 0.2 / 0.5 / 0.3 / 2.2 / 2.5 | 1.5 / 2.5 / 2.5 / 1.7 / 2.8 | 52.7 / 51.4 / 48.9 / 44.4 / 44.4 | 17 / 23 / 21 / 54 / 44 |
| our opponents | 4.2 / 3.0 / 3.6 / 3.5 / 4.7 | 4.0 / 7.3 / 7.4 / 11.3 / 12.3 | 3.0 / 1.2 / 1.6 / 1.9 / 1.6 | 0.5 / 0.4 / 0.2 / 0.6 / 0.6 | 2.2 / 1.6 / 2.0 / 1.9 / 2.4 | 127.7 / 123.1 / 114.9 / 94.8 / 65.5 | 64 / 100 / 120 / 147 / 110 |
| test4 (vs us) | 3.4 / 1.9 / 2.6 / 2.8 / 4.7 | 0.2 / 0.3 / 3.6 / 8.7 / 13.6 | 2.5 / 0.7 / 1.5 / 2.4 / 1.4 | 0.5 / 0.3 / 0.1 / 1.0 / 1.3 | 2.0 / 1.3 / 1.6 / 1.5 / 3.1 | 113.6 / 104.0 / 100.3 / 79.3 / 63.4 | 8 / 16 / 82 / 99 / 109 |
| WHQ (vs us) | 4.4 / 3.4 / 3.4 / 3.7 / 4.9 | 7.1 / 12.9 / 9.7 / 13.0 / 12.7 | 2.9 / 1.1 / 1.3 / 1.6 / 1.6 | 0.5 / 0.2 / 0.1 / 0.4 / 0.3 | 1.8 / 1.9 / 2.0 / 1.9 / 1.6 | 134.7 / 135.5 / 123.7 / 102.9 / 56.1 | 109 / 156 / 143 / 184 / 127 |
| forgot | 4.4 / 3.6 / 4.0 / 4.4 / 4.8 | 0.1 / 8.1 / 8.6 / 7.9 / 6.7 | 2.7 / 2.5 / 2.3 / 2.2 / 2.9 | 0.8 / 0.7 / 1.1 / 0.8 / 1.3 | 0.6 / 0.9 / 1.8 / 3.3 / 3.0 | 94.0 / 91.4 / 80.8 / 65.1 / 52.4 | 4 / 51 / 64 / 61 / 41 |
| SSS | 2.1 / 1.8 / 1.8 / 2.2 / 2.2 | 2.3 / 9.8 / 8.4 / 10.5 / 11.5 | 1.3 / 0.7 / 0.9 / 1.1 / 0.4 | 0.6 / 0.2 / 0.5 / 0.5 / 0.4 | 0.9 / 0.6 / 1.3 / 1.7 / 1.9 | 105.3 / 98.1 / 96.8 / 81.1 / 69.7 | 31 / 67 / 52 / 62 / 59 |
| Vibing++ | 3.5 / 3.8 / 4.7 / 4.6 / 3.9 | 0.1 / 1.1 / 9.7 / 9.5 / 9.5 | 3.3 / 3.3 / 2.2 / 1.7 / 1.7 | 0.8 / 0.7 / 1.0 / 1.2 / 1.0 | 1.7 / 1.5 / 1.4 / 1.8 / 2.1 | 120.1 / 114.4 / 92.9 / 79.0 / 82.4 | 7 / 12 / 69 / 57 / 48 |

**Table B2 (maps over 1,200 cells). Feeders from round 250.**

| group | feeders a game | mean length | pearls dropped a game | eaten by the dragon fed | by other own dragons | by the enemy | by nobody | the dragon fed is the team's longest | is under 10 long | path steps to the fed dragon's head: 1 / 2 / 3 / more or none | nearest enemy head (median cells) | final lineage's gain per feeder segment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| meow live bot | 45.6 | 2.66 | 67.3 | 60% | 28% | 7.3% | 4% | 36% | 39% | 4% / 27% / 46% / 22% | 9 | 0.16 |
| meow test builds | 52.6 | 2.59 | 75.4 | 59% | 32% | 4.1% | 4% | 33% | 44% | 3% / 27% / 48% / 21% | 9 | 0.14 |
| our opponents | 93.3 | 3.07 | 159.1 | 76% | 20% | 2.6% | 1% | 19% | 20% | 19% / 37% / 44% / 0% | 10 | 0.09 |
| test4 (vs us) | 43.5 | 3.95 | 93.2 | 76% | 18% | 4.2% | 2% | 16% | 27% | 9% / 38% / 53% / 0% | 9 | 0.10 |
| WHQ (vs us) | 131.1 | 2.91 | 212.8 | 77% | 20% | 1.9% | 1% | 19% | 19% | 21% / 36% / 42% / 0% | 10 | 0.09 |
| forgot | 51.6 | 2.81 | 82.0 | 84% | 14% | 1.0% | 0% | 35% | 19% | 14% / 36% / 50% / 0% | 11 | 0.15 |
| SSS | 73.4 | 2.87 | 113.7 | 72% | 24% | 2.8% | 1% | 57% | 19% | 63% / 23% / 14% / 0% | 10 | 0.19 |
| Vibing++ | 30.0 | 3.24 | 53.7 | 76% | 20% | 2.7% | 2% | 35% | 24% | 14% / 41% / 45% / 0% | 11 | 0.19 |

**Table C1 (maps over 1,200 cells). Who the leader is and whether it lasts.**

| group | longest at round 400 is the final longest: same id / same lineage | at round 450 | leader cuts a game, rounds 300-394 / 395-499 | of the cuts from 395: made with a free cell | growth of the longest per 25 rounds from 400 (10+ other dragons left): windows with a cut in them or just before / without (number of windows) | longest dragon (15+) died: per game (rammed / boxed in / by choice / own ram) | leader at 400 / 450: cells to the nearest enemy head | steps it took per 25 rounds at 400 / 450 | end: second longest / longest | units at the end |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| meow live bot | 9% / 53% | 23% / 79% | 3.1 / 3.9 | 67% | 4.8 / 8.6 (111 / 28) | 0.56 (24 / 0 / 0 / 0) | 8 / 9 | 60 / 58 | 0.57 | 20 |
| meow test builds | 14% / 50% | 23% / 55% | 3.9 / 4.1 | 69% | 3.1 / 8.9 (55 / 12) | 0.59 (12 / 0 / 0 / 1) | 6.5 / 8 | 72 / 72 | 0.62 | 18.5 |
| our opponents | 22% / 42% | 32% / 58% | 2.5 / 2.5 | 37% | 5.5 / 6.3 (136 / 102) | 2.20 (51 / 81 / 7 / 4) | 9 / 11 | 34 / 38 | 0.72 | 13 |
| test4 (vs us) | 10% / 25% | 15% / 40% | 3.5 / 2.8 | 82% | 4.8 / 7.7 (51 / 29) | 2.45 (22 / 26 / 0 / 1) | 7 / 11.5 | 37 / 41 | 0.71 | 27.5 |
| WHQ (vs us) | 34% / 54% | 51% / 77% | 1.6 / 2.1 | 5% | 6.2 / 6.7 (60 / 61) | 1.57 (11 / 38 / 4 / 2) | 9 / 11 | 33 / 36 | 0.72 | 9 |
| forgot | 6% / 56% | 16% / 66% | 1.9 / 3.2 | 7% | 3.8 / 4.6 (235 / 72) | 1.04 (90 / 1 / 2 / 0) | 9 / 9 | 63 / 63 | 0.62 | 11 |
| SSS | 20% / 67% | 39% / 79% | 1.3 / 1.9 | 98% | 2.8 / 6.6 (196 / 187) | 1.13 (89 / 14 / 7 / 2) | 9 / 9 | 42 / 44 | 0.45 | 31 |
| Vibing++ | 13% / 64% | 26% / 78% | 2.6 / 2.3 | 65% | 4.5 / 8.2 (200 / 114) | 1.48 (80 / 23 / 15 / 6) | 10 / 11 | 56 / 56 | 0.61 | 20 |

### The footing: potential and completeness, all maps

| group | round-500 games with both queens dead | won | own P / enemy P at 300 / 400 / end (median) | won with P ratio at round 400 under 0.5 | 0.5-0.8 | 0.8-1.0 | 1.0-1.25 | over 1.25 | c at the end, own : enemy, in the 0.8-1.25 games |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| meow live bot | 96 | 27 | 0.62 / 0.65 / 0.72 | 0 of 37 | 7 of 23 | 7 of 17 | 3 of 7 | 10 of 12 | 0.52 : 0.72 |
| meow test builds | 47 | 14 | 0.60 / 0.69 / 0.64 | 1 of 17 | 4 of 14 | 0 of 4 | 3 of 6 | 6 of 6 | 0.73 : 0.90 |
| meow (all) | 143 | 41 | 0.62 / 0.67 / 0.68 | 1 of 54 | 11 of 37 | 7 of 21 | 6 of 13 | 16 of 18 | 0.59 : 0.79 |
| our opponents | 143 | 102 | 1.62 / 1.49 / 1.48 | 0 of 10 | 2 of 8 | 6 of 11 | 15 of 22 | 78 of 91 | 0.80 : 0.59 |
| test4 (vs us) | 49 | 32 | 1.61 / 1.38 / 1.29 | 0 of 5 | 0 of 1 | 2 of 5 | 9 of 12 | 21 of 26 | 0.76 : 0.54 |
| WHQ (vs us) | 74 | 61 | 1.83 / 1.99 / 1.86 | 0 of 2 | 2 of 4 | 4 of 5 | 6 of 7 | 48 of 55 | 0.93 : 0.68 |
| forgot | 154 | 85 | 1.02 / 1.00 / 0.94 | 2 of 22 | 8 of 28 | 15 of 27 | 14 of 26 | 46 of 51 | 0.51 : 0.38 |
| SSS | 141 | 82 | 1.13 / 1.13 / 1.07 | 0 of 11 | 5 of 16 | 13 of 28 | 21 of 31 | 43 of 55 | 0.45 : 0.44 |
| Vibing++ | 152 | 99 | 1.29 / 1.25 / 1.50 | 3 of 18 | 6 of 13 | 8 of 11 | 18 of 32 | 64 of 78 | 0.40 : 0.45 |
| top three | 447 | 266 | 1.14 / 1.12 / 1.13 | 5 of 51 | 19 of 57 | 36 of 66 | 53 of 89 | 153 of 184 | 0.48 : 0.42 |

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

## 3. The games read

30 games: all 14 losses the red team listed (lost with at least level total length at round 400: five on Maze, five on
Portals, three on weakhold, one on Slithery Fight), four level races we won, four big-map races we won from behind, and
eight top-team wins of level races on small maps (three each for SSS and Vibing++, two for forgot; four of the eight
against test4 or WHQ). In every game both sides were read. "Run" is the batch our bot's game belongs to: `dl-...` are
ladder downloads (the live bot of that hour), `-old` halves of smoke pairs are the live bot, `-new` halves are test
builds. Table by `e_gamestab.py` (`e_out/games_read.md`); "own" is the team the game was read for.

| # | game | map | cells | run | why read | read for | opponent (elo) | result | total length at 300 / 400 / end, own : enemy | longest at 300 / 400 / end | potential at 300 / 400 / end | units at the end | queens died (own, enemy) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1027819 | Maze | 1152 | stride-old | lost with level or more total length at round 400 | meow | test4 (2133) | lost | 140 : 157 / 136 : 131 / 156 : 154 | 4 : 8 / 13 : 58 / 32 : 77 | 84 : 92 / 85 : 99 / 99 : 117 | 27 : 11 | r248, r326 |
| 2 | 1044512 | Maze | 1152 | dl-20261004 | lost with level or more total length at round 400 | meow | WeHaveQuizzes (2157) | lost | 135 : 147 / 133 : 130 / 127 : 137 | 4 : 9 / 10 : 52 / 74 : 87 | 80 : 85 / 79 : 93 / 104 : 115 | 16 : 8 | r153, r244 |
| 3 | 1063241 | Maze | 1152 | qh31-test-old | lost with level or more total length at round 400 | meow | WeHaveQuizzes (2135) | lost | 126 : 145 / 157 : 143 / 133 : 130 | 4 : 14 / 16 : 38 / 81 : 87 | 74 : 86 / 97 : 95 / 109 : 110 | 13 : 7 | r194, r187 |
| 4 | 1068052 | Maze | 1152 | tc30-test-new | lost with level or more total length at round 400 | meow | WeHaveQuizzes (2180) | lost | 127 : 158 / 153 : 136 / 131 : 121 | 4 : 22 / 10 : 30 / 66 : 94 | 73 : 98 / 89 : 89 / 101 : 109 | 12 : 4 | r165, r171 |
| 5 | 1058146 | Maze | 1152 | passage2-test-old | lost with level or more total length at round 400 | meow | test4 (2176) | lost | 132 : 154 / 137 : 105 / 118 : 145 | 4 : 6 / 13 : 36 / 49 : 56 | 77 : 93 / 83 : 73 / 89 : 103 | 22 : 10 | r142, r278 |
| 6 | 1027971 | Portals | 512 | stride-old | lost with level or more total length at round 400 | meow | WeHaveQuizzes (2087) | lost | 45 : 67 / 62 : 51 / 56 : 30 | 4 : 5 / 13 : 10 / 19 : 30 | 29 : 42 / 39 : 34 / 40 : 30 | 12 : 1 | r121, r237 |
| 7 | 1045202 | Portals | 512 | dl-20261004 | lost with level or more total length at round 400 | meow | test4 (2233) | lost | 69 : 95 / 71 : 65 / 37 : 66 | 4 : 7 / 10 : 20 / 28 : 41 | 43 : 58 / 44 : 46 / 33 : 54 | 4 : 3 | r156, r83 |
| 8 | 1058858 | Portals | 512 | passage2-test-new | lost with level or more total length at round 400 | meow | test4 (2176) | lost | 53 : 83 / 75 : 75 / 33 : 37 | 5 : 12 / 15 : 23 / 22 : 37 | 31 : 53 / 50 : 52 / 28 : 37 | 6 : 1 | r90, r49 |
| 9 | 1063251 | Portals | 512 | qh31-test-old | lost with level or more total length at round 400 | meow | WeHaveQuizzes (2135) | lost | 55 : 66 / 72 : 60 / 58 : 40 | 5 : 4 / 10 : 11 / 9 : 37 | 33 : 40 / 44 : 40 / 36 : 39 | 13 : 2 | r62, r342 |
| 10 | 1063682 | Portals | 512 | qh31-test-new | lost with level or more total length at round 400 | meow | test4 (2131) | lost | 46 : 91 / 86 : 84 / 53 : 46 | 5 : 10 / 9 : 11 / 16 : 33 | 29 : 55 / 52 : 51 / 36 : 40 | 9 : 2 | r9, r134 |
| 11 | 1029033 | weakhold | 600 | stride-new | lost with level or more total length at round 400 | meow | WeHaveQuizzes (2087) | lost | 65 : 34 / 44 : 39 / 12 : 65 | 5 : 5 / 14 : 16 / 4 : 26 | 39 : 22 / 30 : 29 / 8 : 46 | 4 : 4 | r70, r89 |
| 12 | 1045374 | weakhold | 600 | dl-20261004 | lost with level or more total length at round 400 | meow | WeHaveQuizzes (2157) | lost | 94 : 43 / 59 : 24 / 49 : 33 | 4 : 4 / 14 : 17 / 25 : 31 | 54 : 24 / 39 : 21 / 37 : 32 | 7 : 2 | r129, r52 |
| 13 | 1058363 | weakhold | 600 | passage2-test-old | lost with level or more total length at round 400 | meow | WeHaveQuizzes (2155) | lost | 73 : 39 / 64 : 30 / 44 : 47 | 4 : 4 / 13 : 14 / 16 : 18 | 41 : 23 / 41 : 22 / 32 : 33 | 10 : 5 | r82, r74 |
| 14 | 1029032 | Slithery Fight | 1701 | stride-new | lost with level or more total length at round 400 | meow | WeHaveQuizzes (2087) | lost | 206 : 245 / 236 : 209 / 189 : 131 | 47 : 37 / 49 : 93 / 82 : 113 | 138 : 154 / 152 : 154 / 140 : 122 | 23 : 2 | r3, r249 |
| 15 | 1023828 | Maze | 1152 | dl-20261004 | level race we won | meow | forgot to mentio (2269) | won | 134 : 161 / 129 : 123 / 126 : 150 | 5 : 8 / 25 : 51 / 92 : 84 | 80 : 97 / 85 : 92 / 110 : 120 | 6 : 7 | r107, r154 |
| 16 | 1053031 | Portals | 512 | dl-20261004 | level race we won | meow | WeHaveQuizzes (2157) | won | 50 : 66 / 65 : 65 / 51 : 33 | 5 : 4 / 10 : 12 / 42 : 33 | 30 : 41 / 41 : 42 / 47 : 33 | 3 : 1 | r51, r276 |
| 17 | 1063672 | Maze | 1152 | qh31-test-new | level race we won | meow | test4 (2131) | won | 131 : 172 / 139 : 114 / 134 : 81 | 4 : 6 / 16 : 30 / 76 : 64 | 76 : 98 / 86 : 77 / 106 : 73 | 8 : 3 | r152, r163 |
| 18 | 1067916 | Portals | 512 | tc30-test-new | level race we won | meow | test4 (2093) | won | 57 : 97 / 57 : 50 / 57 : 44 | 5 : 7 / 20 : 23 / 49 : 44 | 34 : 59 / 39 : 39 / 53 : 44 | 3 : 1 | r24, r141 |
| 19 | 1053032 | Slithery Fight | 1701 | dl-20261004 | big map, won from behind | meow | WeHaveQuizzes (2157) | won | 183 : 302 / 187 : 249 / 145 : 161 | 11 : 22 / 21 : 55 / 92 : 50 | 108 : 173 / 113 : 159 / 121 : 106 | 12 : 9 | r3, r278 |
| 20 | 1059086 | Slithery Fight | 1701 | passage2-test-new | big map, won from behind | meow | WeHaveQuizzes (2172) | won | 181 : 251 / 174 : 258 / 146 : 220 | 18 : 23 / 16 : 50 / 82 : 41 | 110 : 145 / 104 : 157 / 117 : 132 | 10 : 11 | r3, r166 |
| 21 | 1053383 | Around UNSW | 4096 | dl-20261004 | big map, won from behind | meow | test4 (2233) | won | 209 : 318 / 256 : 382 / 291 : 308 | 31 : 20 / 71 : 23 / 96 : 49 | 130 : 182 / 175 : 215 / 201 : 184 | 47 : 27 | r126, r348 |
| 22 | 1063675 | Around UNSW | 4096 | qh31-test-new | big map, won from behind | meow | test4 (2131) | won | 207 : 362 / 206 : 406 / 199 : 397 | 21 : 16 / 45 : 21 / 69 : 49 | 122 : 199 / 137 : 223 / 141 : 229 | 23 : 40 | r171, r362 |
| 23 | 1046530 | Portals | 512 | ladder | top-team win of a level race, small map | SSS | test4 (2171) | won | 101 : 106 / 71 : 70 / 60 : 24 | 6 : 7 / 40 : 35 / 56 : 24 | 62 : 65 / 56 : 54 / 58 : 24 | 2 : 1 | r285, r77 |
| 24 | 1054770 | Maze | 1152 | ladder | top-team win of a level race, small map | SSS | test4 (2189) | won | 154 : 160 / 124 : 130 / 115 : 128 | 8 : 14 / 55 : 25 / 80 : 52 | 95 : 98 / 95 : 83 / 98 : 92 | 7 : 9 | r207, r165 |
| 25 | 1051292 | Maze | 1152 | ladder | top-team win of a level race, small map | SSS | forgot to mentio (2269) | won | 184 : 157 / 107 : 129 / 146 : 147 | 10 : 6 / 54 : 29 / 92 : 73 | 111 : 94 / 84 : 87 / 121 : 113 | 12 : 11 | r211, r88 |
| 26 | 1069890 | Maze | 1152 | ladder | top-team win of a level race, small map | Vibing++ | WeHaveQuizzes (2195) | won | 146 : 143 / 169 : 138 / 166 : 147 | 12 : 20 / 13 : 46 / 77 : 77 | 89 : 88 / 101 : 94 / 124 : 113 | 18 : 8 | r344, r99 |
| 27 | 1055103 | Maze | 1152 | ladder | top-team win of a level race, small map | Vibing++ | Quaker Qubits (2005) | won | 137 : 116 / 149 : 130 / 129 : 124 | 13 : 4 / 7 : 5 / 51 : 21 | 86 : 71 / 88 : 78 / 94 : 75 | 18 : 15 | r54, r54 |
| 28 | 1061101 | weakhold | 600 | ladder | top-team win of a level race, small map | Vibing++ | horse (2194) | won | 39 : 59 / 47 : 42 / 43 : 42 | 4 : 3 / 7 : 18 / 30 : 19 | 24 : 31 / 28 : 31 / 37 : 31 | 3 : 7 | r117, r360 |
| 29 | 1046978 | Queen Of Spades | 875 | ladder | top-team win of a level race, small map | forgot | test4 (2171) | won | 24 : 40 / 37 : 37 / 35 : 23 | 6 : 4 / 13 : 10 / 27 : 12 | 17 : 26 / 26 : 25 / 31 : 18 | 3 : 2 | r79, r109 |
| 30 | 1058793 | Portals | 512 | ladder | top-team win of a level race, small map | forgot | Kamikaze (2019) | won | 85 : 90 / 70 : 59 / 66 : 61 | 6 : 4 / 32 : 30 / 54 : 44 | 51 : 56 / 53 : 46 / 61 : 53 | 4 : 4 | r112, r141 |

A warning about this list before the stories: games 1-14 were chosen because we lost them with as much length as the
enemy. They show what a lost conversion looks like, and it looks bad in every one of them; they do not show how often
it happens. Section 2.0 does: at level potential before feeding we win about half.

## 4. Per game: the two leaders from round 250

How to read these. `#61` is a dragon id; `(37,3)` a cell (x east, y south, the board wraps). "13 -> 33" is the longest
dragon's length at the two rounds named. "Cut" = the leader keeps 2 and hands the rest to a new id. "P" = potential,
"c" = completeness (longest / P). All numbers are from `python3 e_show.py <game> 250 [--step 10] [--deaths]` and
`python3 e_cutlist.py <game> 390`; boards from `python3 story.py view <game> <round> <x> <y> <radius>` (start of the
round; `A`/`B` heads, `a`/`b` bodies, `*` pearl, `|` and `-` kelp, `O` portal). Belief lines exist only for games whose
sonar is readable (marked).

### Our 14 losses with level total length at round 400

**1. 1027819, Maze, run stride-old (live bot, sonar readable), against test4. Lost 32 to 77.**
- Round 300: 55 units against 49, P 84 against 92, longest 4 against 8. test4's longest is its queen `#0`, 8 long at
  (8,13), with 38 of its 49 heads within 15 cells of her (112 of its 157 segments): the team sits around its home.
- Our zone phase: the dragon that will lead, `#61`, is 3 long at round 325, 8 at 330, 12 at 340 and 16 at 345, all
  inside the box x 37-41, y 0-7 (`story.py track 1027819 61 5`). At the start of round 346 its head is at (37,3), at
  the bottom of a column it has just come down (it moved south three cells in round 345): kelp on its west side, its
  own body north and east, one free cell south, (37,4), and behind that cell the head of a 2-long of ours, `#494`,
  coming up the same column:

  ```
  round 346 start, centre (37,4); rows are y, columns x; A head, a body (all ours here), b enemy body
       333435363738394041
       +-+-+-+-+-+-+-+-+-
    0   . .|* .|a a . . *
       +-+ +-+ + + + + +
    1   .|. . .|a a . . .
       +O+-+-+ + + + + +
    2  |* . .|.|a a . a .
       +-+ +O+ + + + + +
    3  O.|.|.|.|A a . A .        <- the A at (37,3) is our leader #61, 16 long; its body runs up column 37,
       + + + + + + + + +            down column 38 and ends at (41,6)
    4  |.|.|A a|. a . . .
       + + +-+-+ + + + +
    5  |.|AO. .|A a . . .        <- the A at (37,5) is #494, 2 long, moving north
       +O+-+-+ + + + + +
    6   b|. . .|a a a a a
  ```
  It cuts: 16 -> 2 + 14, the 14 go to `#499` with its head at the old tail, (41,6). `#494` steps into (37,4); in round
  347 the 2-long `#61` moves east into the child's body and dies. At round 350, 30 of our 50 dragons that ping still
  say `#61`, 16 long (it is dead); none says `#499`.
- Round 376: `#499` (15) cuts again with two free cells (15 -> 2 + 13, child `#568`). At round 400, 32 of 45 say `#499`
  at 15; it is 2 long and alive.
- Round 401, feeding begins by the clock. The first feeder, `#454` (3 long), dies at (46,14) four steps from `#346`, a
  9-long; its last ping said `#499`, 15 long, news 24 rounds old. The second, `#579` (2), dies at (24,3) next to a
  5-long; test4 eats its pearl. Round 404: the leader `#568` (14) cuts with two free cells (child `#606`, 12).
- Rounds 411-420: 24 dragons die by choice, 15 of them one to three steps from `#606`, 4 next to `#346` (12-16 long), 2
  next to an 8-10-long, 3 next to nothing. `#606` goes 12 -> 25 in those ten rounds and is 34 at round 427.
- Rounds 427, 432, 437: three cuts in ten rounds (34 -> 2 + 32, 33 -> 2 + 31, 33 -> 2 + 31; ids `#622`, `#627`, `#634`;
  one, none and one free cell). From round 421 to 452 seven dragons die by choice: two are the 2-long stubs the cuts
  left behind, the other five die next to a 5-long, a 13-long or nothing. The lineage gets no feeder pearl for 32 rounds
  while it is 31-34 long and has 13 own heads within 15 cells (round 450). At round 450, 9 of 21 still say `#606`, 34
  long; it has been dead since round 428.
- Round 453: four feeders die in one round and a fifth in 454, four of the five next to `#346` (21 long, our second
  longest, 2-7 cells from the leader), one next to the leader `#634` (31); of their 9 pearls the leader eats 4. The
  last ping of the four of round 453 said `#606`, 34 long, news 25 rounds old: the first round
  on which our code treats a leader record as expired (`SONAR_STALE 25`). Inference: they had been waiting for a dead
  34-long, and the 31-long next to them could not replace it in their record because 31 is less than 34.
- Six more leader cuts from round 477 to 499 (three with no free cell) take the longest from 39 to 32.
- test4: its queen runs into herself at round 326, 3 long. Feeding starts at round 350-353 next to its home: `#340`
  and `#511` (3 long) die at (4,22) and (2,19), two steps from `#450` (8 long). `#450`: 8 -> 34 (round 375) -> 58 (400)
  -> 82 (425); 36 feeders with 100 segments in rounds 350-399, 60 pearls, 44 eaten by `#450`; from round 357 to 399, 27
  of its 36 deaths by choice are one to three steps from `#450`. Units 50 -> 37 -> 16 -> 9. Its cuts come late (round 430,
  448, five in round 465, eight in round 491, one at 496) and cost it 94 -> 77 in the last ten rounds.
- Decided: between rounds 350 and 425. Final P 99 against 117, c 0.32 against 0.66; 27 units of ours left, 11 of
  theirs. test4 started 50 rounds earlier with its team already at home and fed one id for 80 rounds.

**2. 1044512, Maze, ladder 4 October (live bot), against WHQ. Lost 74 to 87.**
- WHQ (queen dead since round 244) has 62 units at round 250 and 56 at 275; its first feeders die at round 271 next to
  `#303` (7 long, at (39,9)), which reaches 20, cuts at round 297 with no free cell, and whose 18-long child `#517`
  dies without an order at (42,7) at round 298; its 9 pearls go to other WHQ dragons. At round 333 our 3-long `#595`
  rams WHQ's longest of the time (13) at (24,11) with a 2-step move and we eat its 7 pearls.
- WHQ's real feeding starts at round 351 into `#302`, 7 long at that moment and not the longest (that is `#618`, 11
  long, 20 cells away): 7 -> 12 (358) -> 23 (369) -> 33 (380) -> 52 (400, at (40,12)) -> 65 (425). From round 351 to
  410 sixty WHQ dragons die by choice, every one of them by giving no order (the same way ours do): 51 within three
  steps of a dragon twice their length, 44 of those next to `#302`, and 34 of the 60 at exactly three steps. Of their
  83 pearls the dragon they died next to eats 58, other WHQ dragons 24, we eat 1. The ground is open and the feeders
  stand in a ring:

  ```
  round 366 start, centre (42,9); B head, b body, all WHQ; no kelp in view
       383940414243444546
    5   . . b b . . B b .
    6   . . * b b b b . .
    7   . b B . * . b B .
    8   . b . * . B b b B        <- the B at (43,8) is #302, 18 long
    9   . B . B . . . b .        <- the B at (41,9) is #376 (2 long): gives no order this round and dies
   10   B b . b . . . . .
   11   b B . . . B b . B        <- the B at (43,11) is #198 (2 long): the same
   12   b . . . . b B . b
   13   B . b B . . . . .
  ```
  Thirteen small WHQ heads are in this 9 x 9 view; two die this round, each three cells from the leader's head, and it
  eats a pearl of an earlier feeder at (42,7). The dragon that is fed is cut once in the whole race (round 431, 66 -> 2
  + 64, no free cell). A 32-long second dragon dies without an order next to it at round 485 (12 of its 16 pearls
  eaten): 68 -> 87. 8 units at the end.
- We: our longest goes 4 -> 10 in the hundred rounds of the zone (4, 4, 7, 7, 10 at rounds 300-400, a different id at
  every sample). Feeding from round 401 is fast here: `#622` 10 -> 36 (425, at (8,17)) -> 56 (450) -> 71 (475). In
  rounds 400-449, 58 of our dragons die by choice: 41 within three steps of a dragon twice their length (38 of those
  next to the longest), 5 at four to eight steps, 12 next to nothing; of 77 pearls the dragon they died next to eats
  45, other own dragons 29. Cuts at rounds 458, 480, 485, 494, 499 (the last four with no free cell). 16 units left.
- Decided by the 50 rounds between the two starts: 10 against 52 at round 400, 56 against 68 at round 450. P 80:85 at
  round 300, 104:115 at the end; c 0.71 against 0.76. A race lost on potential and on the clock, not on scatter.

**3. 1063241, Maze, run qh31-test-old (live bot), against WHQ. Lost 81 to 87.**
- WHQ feeds from round 270 (first: two 2-longs at (4,16) and (3,17) next to `#340`, a 4-long). Early on it feeds
  whatever bigger dragon is near: of 56 deaths by choice in rounds 270-349, 51 are within three steps of a dragon twice
  as long but only 17 of those next to the team's longest; at round 325 it has two dragons of 14. Then one takes over:
  27 (350, `#690` at (2,14)) -> 39 (375); four cuts in rounds 382-407 (three with no free cell) hold it at 38-43; 53
  (450) -> 75 (475) -> 87. The end is made of middle-sized dragons: from round 451 to 466 five WHQ dragons of 5, 6, 7,
  9 and 18 long die without an order four to ten cells from the leader, and it eats 21 of their 24 pearls (the
  18-long, `#744`, at (4,23) at round 466: 8 of 9). 7 units at the end.
- We: the zone builds 18 by round 350 (`#669` at (37,6)); cuts at rounds 350 (no free cell) and 365 put it back to
  14-16. Feeding from round 401: 30 feeders in 25 rounds, `#740` 16 -> 48 (425, at (38,7)) -> 70 (450); one cut (round
  441, 62 -> 2 + 60). At round 450 we lead the race 70 to 53. Then it stops: one feeder in rounds 450-474; of our 9
  remaining dragons 3 are within 15 cells of the leader (12 segments; the team's median path distance to it is 26
  steps), the others do not come and grow instead (team total 101 -> 133, second longest 13). 78 against 75 at round
  475, final 81 against 87.
- Decided in the last 50 rounds: P 109 against 110, c 0.74 against 0.79. WHQ's middle-sized dragons died next to its
  leader; ours stood more than 15 cells away. Inference from our code: nothing brings them (`RALLY_FRESH 0`; a dragon
  only walks to the leader from within `FEEDER_APPROACH 15` cells).

**4. 1068052, Maze, run tc30-test-new (test build), against WHQ. Lost 66 to 94.**
- WHQ feeds from round 270 (first: `#244` and `#394`, 3 long, at (43,0) and (44,2) next to `#72`, 10 long) and has 24
  by round 298. That lineage then cuts three times in 13 rounds (rounds 298, 300, 310: 24 -> 22 -> 20 -> 18, two of
  them with no free cell), and at round 311 the 18-long `#609` has no free cell at (43,4) and dies; its 9 pearls go to
  other WHQ dragons. Rebuilt: 12 (350) -> 29 (375, `#595` at (45,12)) -> 30 (400, after a cut with no free cell) -> 47
  (425) -> 76 (450) -> 83; in rounds 350-449, 43 of its 64 deaths by choice are within three steps of the longest. A
  21-long, `#846`, dies without an order three steps from it at (44,14) at round 481 (10 of 11 pearls eaten): 94. 4
  units at the end, c 0.86.
- We: longest 4, 9, 9, 8, 10 at rounds 300-400. In the zone phase our longest dragon cuts itself nine times between
  rounds 337 and 406 at lengths of 9 to 12, seven of the nine with a free cell. From round 401: 28 feeders by round
  425; `#708`, 7 long at round 400 and not the longest, goes 7 -> 29 (425, at (4,22)) -> 62 (450, at (12,15)). Then
  nine cuts in 49 rounds (round 451 with two free cells, eight more with none): 62 -> 63 -> 66, while 16-18 dragons
  with 50-65 segments stand around, 4-6 of them within 15 cells; 17 die by choice in the last 50 rounds, 2 of them
  within three steps of the longest.
- Decided from round 425 on: 29 against 47, 62 against 76 at round 450, then +4 against +18. P 89:89 at round 400,
  101:109 at the end; c 0.65 against 0.86.

**5. 1058146, Maze, run passage2-test-old (live bot), against test4. Lost 49 to 56.**
- test4 does nothing until round 376 (its queen ran into herself at round 278): no death by choice in rounds 250-349.
  Then 37 in 24 rounds, every one by running into itself, 125 segments; the first at (39,11) and (39,5) next to a
  4-long, the third at (43,7) two steps from `#84` (7 long). `#84`: 7 (round 378) -> 36 at round 400 (at (38,8));
  units 55 -> 15 in 25 rounds. It stalls at 39 for 50 rounds; then a 31-long second dragon, `#706`, kills itself three
  cells from it at (45,14) at round 453 and the leader eats 13 of the 16 pearls: 51 by round 459, 55, 56. 10 units at
  the end, 56 / 27 / 17.
- We: `#547` 5 (350) -> 9 (375) -> 13 at round 400 (at (9,17)) -> 40 at round 425 (at (1,21)): 30 deaths by choice in
  rounds 400-424, 20 of them within three steps of it. Cuts at rounds 445, 447, 452, 465, 493, 497 (three with no free
  cell): 48 -> 44 -> 41 -> 49. For those 75 rounds 23-26 of our dragons with 57-94 segments stand by, and they do die:
  39 deaths by choice in rounds 425-499 (104 segments, 57 pearls), but 20 of the 39 next to nothing and 8 next to the
  longest; the dragon they died next to eats 17 pearls, other own dragons 24, test4 5, nobody 8. An 18-long of ours
  dies without an order next to the leader at round 485 (5 of 9 pearls eaten).
- Decided after round 425: we had the higher potential at round 400 (83 against 73) and at round 425 the longer
  dragon (40 against 39). Final c 0.55 against 0.54: both sides scattered; they merged one big dragon into the leader
  and we fed the floor.

**6. 1027971, Portals, run stride-old (live bot, sonar readable), against WHQ. Lost 19 to 30.**
- Round 390: our leader `#500` is 10 long, 16 of our 17 other dragons believe it, 11 of them (30 segments) are within
  15 cells and short enough to feed it. Everything is ready.
- Round 400, one round before feeding starts: `#500` (13) stands at (20,5) with kelp on its west side, its own body
  south, and two free cells, north (20,4) and east (21,5); a 2-long of ours, `#694`, is next to it at (21,4):

  ```
  round 400 start, centre (20,5); A head, a body, all ours; * pearl, | - kelp, O portal
       161718192021222324
       + + + + + + +-+-+
    3  |. . . a a a|* *|.
       + + +-+-+ + +-+-+
    4  |. .|* *|. A aOa a        <- the A at (21,4) is #694, 2 long
       + + +-+-+ + + + +
    5  |. .|* *|A . . A .        <- the A at (20,5) is our leader #500, 13 long; the A at (23,5) is #678, 3 long
       + + +-+-+ + +-+-+
    6  |. . .O. a .|*O*|a
       +-+ + + + + + + +
    7   *|. . . a .|* *|a
  ```
  It cuts: 13 -> 2 + 11 (child `#696`, head at (24,11)). At round 401 `#694` steps to (21,5) and gives the feeder order
  there, next to a leader that is now 2 long; its pearl goes to `#605`, a 9-long eight steps away. `#696` cuts again at
  round 404 (12 -> 2 + 10, one free cell). At rounds 410 and 420, 12 of 13 and 11 of 14 of our dragons still say `#500`,
  13 long (it is 2); by our rules none of them can feed anybody. At round 430 seven of 13 say the new longest, `#605`,
  and it goes 15 -> 23 in ten rounds (seven feeders die one or two steps from it in rounds 426-440, one of them an
  8-long). At round 440 we lead the race 23 to 21.
- Round 449: `#605` (25) cuts with one free cell. At rounds 450, 460 and 470 the team says `#605`, 25 long (it is 2
  long, then dead: 12 of 13, 9 of 9, 12 of 12 pinging dragons); the new ids cut four more times (rounds 456, 460, 467,
  474: 23 -> 17; three of the four with a free cell). Round 480: seven of 11 say `#747` (20); it cuts at 482 and its
  child at 489, both with two free cells; at round 490, 11 of 12 say `#747`, 23 long, and it is 3.
- Our deaths by choice from round 400: 35 (96 segments, 53 pearls). 19 are within three steps of a dragon twice their
  length, 11 of those next to the longest; the dragon they died next to eats 22 pearls, other own dragons 23.
- WHQ's first steady feeders die at round 414-420 ((11,5), (10,7), (7,2), two or three steps from `#707`, 9-13 long)
  with 15 units on the board; `#707` goes 9 -> 24 by round 458 and is cut once (round 459, no free cell). Its last two
  dragons of 9 and 10 die without an order next to the leader at rounds 461 and 497. One dragon of 30 at the end.
- Decided after round 440. P 39 against 34 at round 400, 40 against 30 at the end; c 0.47 against 1.00. At ten
  samples from round 400 to 490, at least half of our dragons named the true longest at four (rounds 400, 430, 440,
  480) and not one of them did at the other six.

**7. 1045202, Portals, ladder 4 October (live bot), against test4. Lost 28 to 41.**
- test4 (queen dead since round 83) has the higher potential before anybody feeds: P 58 against 43 at round 300, 57
  against 46 at rounds 350 and 375. It feeds from round 321 (first: `#537`, 3 long, at (26,2), three steps from the
  7-long `#676`), slowly at first: 29 deaths by choice in rounds 300-399, all but one by running into itself, 17 of
  them within three steps of its longest. `#870`: 7 (375) -> 20 (400, at (25,7)) -> 32 (425) -> 38 (450) -> 41; one cut
  (round 430) and one odd split at round 472 (44 into 35 + 9; the 9-long kills itself eight rounds later). 12 units
  at round 400, 3 at round 425 and at the end.
- We: the zone leader is 13 at rounds 350-375 (`#851`, then `#1008`, both at (7,7)) through six leader cuts between
  rounds 322 and 376, and 10 at round 400 (`#1017` at (5,8)). Potential at round 400: 44 against 46, level; longest 10
  against 20. Then our feeding burst loses potential instead of converting it: P 44 -> 29 between rounds 400 and 425
  while the longest stays at 10 (cuts at rounds 402, 409, 422). In the last hundred rounds 35 of our dragons die by
  choice (100 segments, 55 pearls): 22 within three steps of a dragon twice their length, but only 8 of those next to
  the longest; the dragon they died next to eats 21 pearls, the longest 10 more, other own dragons 17, nobody 7. A
  pearl eaten by a dragon that is not the leader is halved again when that dragon dies. Then 16 (450), 21 (475), 28;
  4 units at the end.
- Decided between rounds 375 and 425. Final P 33 against 54, c 0.85 against 0.76: we finished cleaner than test4 and
  lost on the potential we had burnt.

**8. 1058858, Portals, run passage2-test-new (test build), against test4. Lost 22 to 37.**
- test4 (queen dead since round 49) feeds a little from round 316 and ends as one dragon: 12 (300) -> 17 (350) -> 23
  (400, `#956` at (31,10)) -> 24 (425) -> 27 (450); an 18-long, `#987`, kills itself two cells from the leader at
  (21,4) at round 455 and the leader eats all 9 pearls: 36 at round 475, 37 at the end, alone on the board from
  round 457.
- We: 15 at round 400 (`#936` at (6,4)), cuts at 405 and 412, 16 at 425, 31 at 450 (`#981` at (10,3)): at round 450 we
  lead the race 31 to 27. In rounds 400-449, 16 of our dragons die by choice, 14 of them within three steps of a
  dragon twice their length, and 18 more (43 segments) die boxed in: P 50 -> 36 -> 40.
- Round 478. We have three dragons: the leader `#990` (35), `#988` (12) and `#981` (9); test4 has one of 36. Our
  potential is 46 against 36. The leader has come down a one-cell-wide column eating natural pearls at (15,3) and
  (15,5); ahead of it are one free cell and a two-cell pearl pocket:

  ```
  round 478 start; A head, a body, all ours; * pearl, | - kelp, O portal
        4 5 6 7 8 910111213141516
       +-+-+-+-+-+-+-+-+-+-+-+-+-
    0   a a a a|* *|. . . a a a|.
       + + + + + + + + + + + + +
    1   aO. . a|*O*|a a a a .|a|.
       +-+-+ + +-+-+ + +-+-+ + +
    2  |*O*|. a aOa a .|* *|.|a|.
       +-+-+ + + + + + +-+-+ + +
    3  |* *|. . a a . .|*O*|.|a|.
       +-+-+ + +-+-+ + +-+-+ + +
    4   a a a .|* *|a a . . .|a|.
       + + + + +-+-+ + + + + + +
    5   a a a A|*O*|. a aOA .|A|.     <- A at (15,5): the leader #990, 35 long; its tail end is at (6,4)
       +-+-+ + +-+-+ + +-+-+ + +         A at (7,5): #988, 12 long; A at (13,5): #981, 9 long
    6  |* *|. a .O. . .|* *|.|.|.
       +O+ + + + + + + + + + + +-
    7  |* *|a a . . . .|*O*|.|* *
  ```
  It cuts, 35 -> 2 + 33, and the child's head appears at the old tail, (6,4). The child cuts at once, 33 -> 2 + 31,
  and its child appears at (15,3); and so on, six cuts in the same round with the head jumping between the two ends
  ((6,4), (15,3), (5,5), (15,1), (4,4), (14,0)): 35 -> 23 in one round, six 2-long stubs left behind. The enemy's only
  dragon is at (27,2), twelve columns away.
- After that: one more cut at round 493 (24 -> 2 + 22); the 12-long splits itself at round 479; in rounds 450-499 nine
  of our dragons die by choice, two of them within three steps of a dragon twice their length, and of their 22 pearls
  the dragon they died next to eats 1, other own dragons 10, nobody 11. Final 22, P 28.
- Decided at round 478, by our own leader. P 50:52 at round 400; c 0.79 against 1.00.

**9. 1063251, Portals, run qh31-test-old (live bot), against WHQ. Lost 9 to 37.** The extreme case. From round 395 to
499 our longest dragon cuts itself 19 times, about every five rounds, at lengths of 9 to 16, and 15 of the 19 times it
has a free cell (two free cells in nine of them). Longest at rounds 400 / 425 / 450 / 475 / end: 10, 16, 9, 9, 9; we
end with dragons of 9, 9 and 8 and 13 units. In those hundred rounds 39 of our dragons die by choice (100 segments, 55
pearls): 27 within three steps of a dragon twice their length, but that dragon is the team's longest for only 8;
whichever dragon they died next to eats 23 pearls, other own dragons 25. WHQ's queen is its leader until she is cut at
round 341 (15 long, no free cell) and dies a round later; it starts feeding at round 364 ((11,5), one step from
`#644`, 5 long) and feeds that one id to the end with no cut at all: 9 (375) -> 11 (400) -> 22 (425) -> 32 (450) -> 37;
of its 23 feeders 13 die within three steps of it and it eats 34 of their 47 pearls. 2 units at the end. P 44 against
40 at round 400 and 48 against 42 at round 425 in our favour; final P 36 against 39; c 0.25 against 0.95.

**10. 1063682, Portals, run qh31-test-new (test build), against test4. Lost 16 to 33.**
- test4 (queen dead since round 134) feeds from round 293 and has a leader of 26 by round 368 (`#461`). That leader
  is no model either: it is cut with no free cell at (5,10), and the 24-long child then stands still at (21,6) for six
  rounds and sheds a 2-long piece of tail in each of them (24 -> 12 by round 374; `story.py track 1063682 461,902 1`).
  Rebuilt: 11 (400) -> 16 (425) -> 30 (450) -> 28 (475) -> 33; 2 units at the end (33 and 13).
- We: 14 at round 325 (`#725`), then twelve leader cuts between rounds 337 and 409 at lengths of 9 to 16 (ten of them
  with a free cell) and a longest of 10, 8, 9 at rounds 350 / 375 / 400. Feeding from round 412: `#854` 15 (425) -> 20
  (430) -> 23 (435), against test4's 16, 18 and 24 at those rounds. Then cuts at rounds 436, 438, 450, 457, 467, 487, 491 (23 ->
  21 -> 19 -> 17, 18 -> 16, 20 -> 18 -> 16 -> 14; five of the seven with a free cell). In the last hundred rounds 44 of our
  dragons die by choice (116 segments, 64 pearls): 25 within three steps of a dragon twice their length, 12 of those
  next to the longest; the dragon they died next to eats 24 pearls, other own dragons 35. 9 units at the end.
- P 52:51 at round 400, 36:40 at the end; c 0.44 against 0.82.

**11. 1029033, weakhold, run stride-new (test build), against WHQ. Lost 4 to 26.** Not a feeding story until the end.
At round 300 we have 27 units and 65 total length against 13 and 34 (P 39:22). From the zone switch on our team stops
eating: 40 natural pearls in rounds 250-299, then 16, 9 and 3 per 50 rounds (WHQ: 34, 27, 24, 24) while 15-20 of our
dragons a block still die boxed in; total 65 -> 44 by round 400 and P 39 -> 30, while WHQ's P goes 22 -> 29. Our
leader `#311` goes 9 (350) -> 13 (375) -> 14 (400, at (23,13)) -> 17, cuts at round 409 with two free cells (17 -> 2 +
15), its children cut at 418 and 436, and the heir `#397` (14) is rammed at (16,6) at round 448 by a 3-long with a
2-step move. Five rounds earlier our 8-long `#384` had rammed WHQ's 16-long leader at (17,6) after a 7-step sprint;
WHQ's own dragons ate all 8 pearls and it rebuilt to 28 in 30 rounds (then cut itself to 26 with two free cells at
round 475). 5 units and 12 segments left to us at round 450; WHQ ends with 26, 18 and 17.

**12. 1045374, weakhold, ladder 4 October (live bot), against WHQ. Lost 25 to 31.** At round 300: 41 units and 94
total against 19 and 43 (P 54:24). Then the same starvation: 47 natural pearls in rounds 250-299, 26, and 4 in rounds
350-399; total 94 -> 59 by round 400 (P 39:21). The leader `#194` is 12 at round 350 and 14 at rounds 375 and 400, at
(21-23,13-14); the rest of the team is a median 42-44 path steps away from it (the map is a ring of corridors).
Feeding from round 406 is blind: of 28 deaths by choice from round 400 to the end (74 segments, 40 pearls), 21 are next
to no dragon twice their length at all (at (11,14), (9,0), (12,0), (16,5), (13,14) ... with the longest 9 to 23 cells
away), 5 are within three steps of one and 3 of those next to the longest; the dragon they died next to eats 4
pearls, the longest 2 more, other own dragons 23, nobody 9. The leader still reaches 24 by round 450 (`#381` at
(24,1), 10 natural pearls), level with WHQ's 25. Then it cuts itself four times in 15 rounds (455, 462, 465, 469: 24
-> 16), every time with a free cell, as it had three times at rounds 417-425. Final 25 and 14. WHQ is down to 8 units
at round 375, feeds one dragon from round 353 (4 -> 17 by 400; 11 feeders, all one or two steps from it, 13 of 13
pearls eaten by it), is a single dragon of 34 by round 475 and ends 31 after two cuts with no free cell. c 0.68
against 0.97.

**13. 1058363, weakhold, run passage2-test-old (live bot), against WHQ. Lost 16 to 18.** P 41 against 23 from round
300 to 400 (33 units against 16). Leader `#328`: 10 (350) -> 13 (400, at (23,12)) -> 17 (425); it cuts twice at rounds
436-437 (20 -> 18 -> 16, with one and two free cells) and the heir `#432` (16) is rammed at (18,6) at round 439 by a
2-long with a 2-step move; WHQ eats 6 of the 8 pearls. One round earlier a 9-long of ours had killed itself at (18,5),
three cells from a WHQ 2-long. Total 64 -> 46 -> 20 between rounds 400 and 450. Of our 14 deaths by choice from round
400 on, none is within three steps of the longest and 8 are next to nothing. A new leader, `#378`, then goes from 3 to
20 in under 20 rounds (round 469), ahead of WHQ's 17, and cuts itself three times in the last 31 rounds (469, 475,
480: 20 -> 18, 19 -> 17, 17 -> 15; the first two with a free cell). 16 at the end against 18: the three cuts cost 6.
WHQ ends with two dragons of 18 and 17; its own leader was cut four times after round 400, every time with no free
cell. In two of these three weakhold games (11 and 13) three leaders died by a ram in the same passage, (16-18,6).

**14. 1029032, Slithery Fight (1,701 cells), run stride-new (test build), against WHQ. Lost 82 to 113.**
- We feed from round 201 (56 units). `#929`: 21 (250, at (9,7)) -> 34 -> 47 (300, at (0,24)). Then nothing for 100
  rounds: 47, 51, 52, 49 at rounds 325-400 through seven ids. Two things happen in those hundred rounds. The leader
  cuts itself six times (rounds 308, 344, 351, 364, 385, 394; four with a free cell): 12 segments. And of 43 deaths by
  choice (110 segments, 60 pearls) 23 are within three steps of a dragon twice their length but only 8 of those next
  to the longest; the dragon they died next to eats 24 pearls, other own dragons 36. From round 400: 61 feeders in 50
  rounds (160 segments, 86 pearls, 55 eaten by the dragon they died next to), 53 (425) -> 67 (450) -> 79 (475); cuts at
  405, 472 and 494; 82. Even then the dragon next to the feeder is the longest in only 20 of 61 cases from round 400
  on; three own dragons of 14, 26 and 14 die without an order (rounds 404, 460, 477) and the leader eats 3 of their 27
  pearls. 23 units and 189 segments at the end.
- WHQ's queen is its leader until round 248 (23 long; cut, and she dies a round later). The child `#942` is the same id
  from round 250 to the end with no cut: 21 -> 37 (300) -> 62 (350) -> 93 (400, at (52,10)) -> 106 (450) -> 113. From
  round 250 to 399, 115 WHQ dragons die by choice, all without an order, 102 of them within three steps of a dragon
  twice their length (49 of those next to the longest), and the dragon they died next to eats 143 of 189 pearls. A
  second WHQ dragon grows to 70 and dies without an order at (59,11) at round 495, six cells from our leader's head;
  none of its 35 pearls is eaten by anybody in the last five rounds.
- Decided between rounds 300 and 400: P 138:154, 152:154, and 140:122 at the end in our favour; c 0.59 against 0.93.

### Four level races we won

**15. 1023828, Maze, ladder 4 October (live bot, sonar readable), against forgot. Won 92 to 84.** The control case.
Our leader `#265` keeps its id from round 325 to 475: 8 (325, at (1,22)) -> 13 -> 20 -> 25 (400, at (9,21)) -> 47 (425)
-> 77 (450) -> 91 (475); one cut after round 395. Share of our dragons that believe it: 35 of 51 at round 325, 35 of 40
at 350, 32 of 45 at 375, 28 of 42 at 400; 23-30 dragons with 52-76 segments could feed it at every sample. From round
401: 40 feeders in 50 rounds (93 segments, 52 pearls: 37 eaten by it, 9 by other own dragons, 6 by nobody); all 30
that die within three steps of a dragon twice their length die next to the longest. 6 units at the end, c 0.84.
forgot starts at round 364 ((41,8) and (39,5), two and three steps from `#289`, 6 long): 20 at 375, 51 at 400 (at
(38,10)), and then four cuts, three of them with no free cell (rounds 408, 429, 471, 491); 84 at the end with dragons
of 27 and 25 beside it, c 0.70. We had less potential all game (80:97 at round 300, 85:92 at 400, 110:120 at the end)
and won on completeness. This is what our feeding looks like when the leader keeps its id.

**16. 1053031, Portals, ladder 4 October (live bot), against WHQ. Won 42 to 33.** P 41:42 at round 400. Ours: 10 (400,
`#662` at (24,11)) -> 21 (425) -> 21 (450) -> 31 (475) -> 42 through five cuts (rounds 421, 434, 441, 469, 478; three
with two or three free cells; they cost 10); 13 feeders in the last 50 rounds, 17 of their 21 pearls eaten by the
dragon they died next to; 3 units at the end, c 0.89. WHQ (queen dead at round 276) feeds slowly from round 374, has
12, 16 and 22 at rounds 400 / 425 / 450, merges its last two dragons of 13 and 11 at rounds 462 and 468 and is a
single dragon of 32 by round 475 with nothing left to eat: 33. We won with the cuts because WHQ had run out of
material (P 39 against 34 at round 450).

**17. 1063672, Maze, run qh31-test-new (test build), against test4. Won 76 to 64.** test4 feeds from round 318 and
builds `#485` to 30 by round 400 (at (35,10)). At round 405 that leader cuts with two free cells, and a round later
the 28-long child has no free cell at (39,5) and dies (14 pearls: 12 to other test4 dragons, 2 to us); with it and
ten other boxed-in deaths test4 loses 54 segments in rounds 400-449 (P 77 -> 50). `#604` then goes 31 -> 46 -> 64 and
stops there, with 3 units left. Ours: longest 4, 5, 5, 7 at rounds 300-375 and 16 at round 400 (`#690` at (6,19)).
From round 401: 37 feeders in 50 rounds, but spread: `#690` reaches 29, cuts at 422, its children at 428 and 449
(27, 28 at rounds 425 / 450), and meanwhile another dragon, `#221`, 3 long at round 400, is fed to 22 by round 450
and 58 by round 475 (at (3,22)); it wins the race with 76 while the first lineage ends at 30. Of 71 deaths by choice
from round 400 on, 43 are within three steps of a dragon twice their length and 24 of those next to the longest. 8
units at the end, c 0.72 against 0.88; P 86 against 77 at round 400.

**18. 1067916, Portals, run tc30-test-new (test build), against test4. Won 49 to 44.** P 39:39 at round 400. Ours: 12
(350) -> 17 (375) -> 20 (400, `#964` at (10,8)) through three cuts with a free cell (rounds 378, 384, 399), one more at
round 420 (32 -> 2 + 30), and then `#972` keeps its id for the last 80 rounds: 31 (425) -> 44 (450) -> 47 -> 49. Of
14 deaths by choice from round 400 on, 11 are within three steps of a dragon twice their length and 10 of those next
to the longest. 3 units at the end, c 0.92. test4 feeds from round 320: 23 (400) -> 35 -> 39 -> 44, one cut (round 417,
no free cell), a single dragon by round 475 with nothing left.

### Four big-map races we won from behind

**19. 1053032, Slithery Fight, ladder 4 October (live bot), against WHQ. Won 92 to 50** with P 113 against 159 at
round 400. We feed from round 202 (26 feeders by 250, `#369` 24 long), lose that leader to a ram at round 266 (27
long, hit at (31,10) by a 5-long with a 5-step move; WHQ eats 9 of its 14 pearls), cut the next ones five times
between rounds 308 and 379 and hold 21, 19, 21 at rounds 350 / 375 / 400. Then `#1476` keeps its id for the 50 rounds
that matter: 21 -> 42 (425) -> 72 (450); 42 deaths by choice in those rounds, 39 within three steps of a dragon twice
their length, 35 of those next to the longest; 48 of 71 feeder pearls eaten by it. One cut at round 450 with three
free cells (72 -> 2 + 70), then 79, 92. WHQ feeds from round 270 and has 55 at round 400, but in several dragons: of
121 WHQ deaths within three steps of a bigger dragon only 32 are next to its longest; its leader is cut seven times
after round 380, every time with no free cell; a 34-long and a 36-long die at rounds 465 and 492 with 7 of their 35
pearls reaching the leader; and at round 498 our 10-long `#1716` rams its 63-long leader at (43,11) with a 5-step
move. It ends with 50, 40 and 26. c 0.76 against 0.47.

**20. 1059086, Slithery Fight, run passage2-test-new (test build), against WHQ. Won 82 to 41** with P 104 against 157
at round 400. Ours: 15-22 from round 200 to 400 through seven ids (51-54 units, so this build does not feed before
round 400); then `#1333` keeps its id for the last hundred rounds: 16 -> 36 (425) -> 56 (450) -> 66 -> 82, with 30 and
32 feeders per 50 rounds and 71 of their 95 pearls eaten by it. WHQ feeds from round 271 but into many dragons (of 133
deaths within three steps of a bigger dragon, 22 are next to its longest) and has 50 / 40 / 35 at round 400. Then it
loses them one by one: a 40-long is rammed at (30,8) at round 403 by our 6-long `#1178` with a 5-step move (we eat 17
of its 20 pearls), a 23-long by our 11-long at round 435, and three of its own big dragons die without an order
(30 long at round 402, 32 at 418, and at round 472 its 65-long leader at (38,23), one round after its third cut with
no free cell in 20 rounds; another WHQ dragon eats 29 of the 33 pearls). 67 at round 450, 39 at 475, and 41, 36 and 34
at the end with 220 segments on the board. c 0.70 against 0.31.

**21. 1053383, Around UNSW (4,096 cells), ladder 4 October (live bot), against test4. Won 96 to 49** with total length
256 against 382 at round 400. We have 60 units at round 200 and 52-56 after that; the first feeders die at round 204
((3,16) and (1,17), three steps from `#329`, 13-14 long). That leader cuts at round 252 with three free cells; the
next one, `#188`, keeps its id from before round 300 to round 438 and grows about 20 per 50 rounds: 31 (300, at
(46,15)) -> 53 -> 71 (400) -> 85 -> 96, fed by 15-25 feeders per 50 rounds; its natural pearls: 0-11 per 50 rounds.
test4's queen dies at round 348; its longest dragon (23) is rammed at (11,1) at round 401 by our 13-long `#494` with
a 5-step move; its first feeders die at round 427. 49 at the end with 27 units and 308 segments unused. c 0.48
against 0.27.

**22. 1063675, Around UNSW, run qh31-test-new (test build), against test4. Won 69 to 49** with total 206 against 406
at round 400. Ours: 17 (200) -> 22 -> 21 -> 28 -> 45 (400, `#655` at (53,20)) -> 42 -> 69, through 13 leader cuts from
round 250 on, 11 of them with a free cell (five between rounds 405 and 444 hold it at 42-46 for 50 rounds). test4
(queen dead at round 362) has a longest of 16-27 until round 450, loses two leaders boxed in (28 long at round 263, 23
at round 425), starts feeding at round 438 and ends with 49, 32 and 27, 40 units and 397 segments. c 0.49 against
0.21.

In all four the opponent threw the race away (test4 by waiting for its queen and then having no leader, WHQ by ending
with three leaders and losing others to our rams and to deaths without an order). In three of the four our leader had
50 or more rounds with one id while feeders died next to it; in the fourth (22) it cut itself 13 times and won
because test4 was worse.

### Eight top-team wins of level races on small maps

**23. 1046530, Portals, SSS against test4. SSS won 56 to 24.** SSS's queen dies at round 285; its first feeders die
at round 306-307 ((20,3), (21,3), (21,4), one or two steps from `#617`, 7-8 long): 9 feeders by round 325 (`#617` 6 ->
15). That leader cuts twice with free cells (rounds 341 and 346), and then `#770` is one id from round 346 to the end
with no cut: 18 (350) -> 28 -> 40 (400, at (21,11)) -> 47 -> 49 -> 56. From round 300 on 51 SSS dragons die by choice
(120 segments, 62 pearls): every one of them within three steps of a dragon twice its length, 36 of the 51 at one
step, 48 next to the longest; it eats 53 of the 62 pearls (85%). A steady 3-12 per 25 rounds, never a burst. 2 units
at the end, c 0.97. test4 feeds from round 320 and has 35 at round 400; that leader, `#723`, has no free cell at
(27,8) at round 400 with an SSS 2-long on the next cell and dies (16 of its 18 pearls go to other test4 dragons);
test4 ends as one dragon of 24.

**24. 1054770, Maze, SSS against test4. SSS won 80 to 52.** SSS (queen dead at 207) starts at round 301 ((38,8),
(38,9), (38,11), one or two steps from `#349`, 5-10 long): 20 feeders in 25 rounds and 22 in the next, `#349` 8 -> 24
(325) -> 45 (350, at (35,8)). It cuts at round 360 with a free cell (46 -> 2 + 44) and no feeder dies for the next 15
rounds; then the child `#663` is one id to round 496: 44 (375) -> 55 (400) -> 70 -> 79 -> 79. Of 76 deaths by choice
from round 300, 73 are within three steps of a dragon twice their length (41 at one step) and 67 next to the longest.
7 units at the end, c 0.82. test4 starts at round 383 (25 at 400, 51 at 425, 64 at 475) and ends 52 with dragons of 19
and 15.

**25. 1051292, Maze, SSS against forgot. SSS won 92 to 73.** SSS starts at round 318 ((46,21) and (45,21), one and two
steps from `#569`, 5 long): `#569` 11 (325, at (42,18)) -> 29 -> 41 -> 54 (400) -> 57, the same id for 110 rounds, 9-22
feeders per 25 rounds until round 400; two cuts with free cells (rounds 431 and 463), 73 (450), 75 (475), 92. Of 91
deaths by choice from round 300, 87 are within three steps of a bigger dragon (54 at one step), 76 next to the
longest. c 0.76. forgot starts at round 369: 11 (375) -> 29 (400) -> 31 -> 57 (450) -> 69 -> 73, four cuts with no free
cell; c 0.65. P 111:94 at round 300, 84:87 at 400 (SSS has spent more by then), 121:113 at the end.

**26. 1069890, Maze, Vibing++ against WHQ. Vibing++ won on total length, longest 77 to 77.** Vibing++ (queen dead at
344) does not feed until round 400: longest 12-16, and that longest cuts itself eleven times between rounds 305 and
386 at 14-16 long, ten of the eleven with a free cell (the same habit as ours; it costs them 2 segments each time and
nothing else, because nobody is feeding yet). First feeders at round 400-401 ((46,6), (42,7), (43,6), three steps
from `#966`, 9-10 long). Then 20 feeders in 25 rounds and a leader that eats on the move (22 natural pearls in rounds
400-449): 13 -> 47 (425, at (37,18)) -> 71 (450) -> 77, one id from round 400 to 468. In rounds 400-449, 50 Vibing++
dragons (116 segments) die boxed in, and no feeder by the test used here dies between rounds 425 and 449 while the
leader goes from 47 to 71 (what it eats then are natural pearls and the pearls of boxed-in team-mates). It ends with 18 units and 166
segments, c 0.62. WHQ feeds from round 272, has 46 at round 400 and 79 at 450, cuts five times with no free cell in
rounds 462-483 (82 -> 76) and ends 77 with a second dragon of 42 unmerged, c 0.68. Neither side finished.

**27. 1055103, Maze, Vibing++ against Quaker Qubits. Vibing++ won 51 to 21.** Before feeding, Vibing++'s longest cuts
itself 19 times between rounds 302 and 399 at 8-15 long (12 with a free cell) and is 7 at round 400. First feeders at
round 403: 7 -> 25 (425, at (10,11)) -> 31 -> 38 -> 51 through three more cuts, with 18 units and 129 segments left
(c 0.54). Quaker Qubits does not feed before round 485: longest 21, 15 units. A win on having a leader at all.

**28. 1061101, weakhold, Vibing++ against horse. Vibing++ won 30 to 19.** Vibing++ (11-20 units, P 20-29) starts at
round 430 ((14,11), two steps from `#456`, 11 long): `#456` 7 (400, at (24,13)) -> 11 -> 23 (450) -> 25 -> 30, one id
and no cut for the last hundred rounds; 3 units at the end, c 0.81. horse feeds its queen from round 307; she is cut
at round 359 (17 long, no free cell) and dies a round later; its later leader is cut 22 more times (12 with no free
cell), seven of them between rounds 485 and 496: 35 -> 19.

**29. 1046978, Queen Of Spades (875 cells), forgot against test4. forgot won 27 to 12.** Two small teams (8-16 units).
forgot starts at round 370: 7 (375) -> 13 (400); that leader is rammed at (20,31) at round 409 by a 4-long with a
2-step move; another dragon goes 10 (425) -> 17 -> 23 -> 27, 3 units at the end, c 0.87. test4 ends with two dragons of
12 and 11 that never merge.

**30. 1058793, Portals, forgot against Kamikaze. forgot won 54 to 44.** forgot starts at round 370 with 37 units: 10
(375, at (11,0)) -> 32 (400) -> 40 -> 41 -> 55 -> 54 through seven cuts after round 400, all with no free cell; 4 units
at the end, c 0.89. Kamikaze starts about ten rounds earlier (15 at 375, 30 at 400) and stalls at 31-36 for 75 rounds
with 5-10 units standing by; 44 at the end.

What the eight have in common: in the 50-100 rounds in which the race is made, the dragon that is fed either keeps its
id (SSS in all three games, Vibing++ in all three) or is cut only when it has no free cell (forgot); the feeders die
one to three steps from that dragon (SSS: at one step, two times in three); and SSS and forgot end with 2-7 units.
Vibing++ does not finish (18 units left in two of three games) and wins anyway. What they do not have in common is the
start: round 301-318 for SSS, 370 for forgot, 400-430 for Vibing++.

## 5. Answers to the nine questions

Every number here is in a table of section 2 or in the output file named; "measured" unless marked "inference".
Medians per race unless a line says otherwise. Small maps = 1,200 cells or fewer.

### a. The leader's curve

**When each team starts and how fast it grows** (tables A1, A3; `e_a.py` gives the same every 25 rounds from 150 and
by band of total length at round 400 in `e_out/a_curve.txt`).

| small maps | longest at 300 / 350 / 400 / 450 / end | the final longest's lineage first 8 / 15 / 25 long (round) | leader feeding starts (round) | growth in the 50 rounds after take-off | growth from 400 to the end | units at 300 / 400 / end | share of potential in the longest at 400 / 450 / end |
|---|---|---|---|---|---|---|---|
| meow live bot | 4 / 9 / 10 / 16 / 20 | 336 / 406 / 426 | 401 | 11 | 10 | 26 / 21 / 7 | 0.27 / 0.53 / 0.65 |
| meow test builds | 4 / 8 / 11 / 21 / 30 | 354 / 407 / 423.5 | 401 | 18.5 | 21 | 22 / 21 / 4 | 0.20 / 0.51 / 0.71 |
| test4 (vs us) | 6 / 6 / 13 / 30 / 37 | 386 / 401.5 / 421 | 354 | 16 | 22 | 33 / 16 / 3 | 0.41 / 0.64 / 0.77 |
| WHQ (vs us) | 5 / 16 / 28 / 40 / 45 | 323 / 364 / 389 | 315 | 14 | 26 | 33 / 23 / 4 | 0.43 / 0.65 / 0.80 |
| forgot | 5 / 5 / 16 / 27 / 36 | 374 / 394 / 417 | 373 | 14 | 20 | 24 / 14 / 6 | 0.43 / 0.60 / 0.69 |
| SSS | 6.5 / 16.5 / 26 / 36 / 38.5 | 312 / 356.5 / 372 | 311 | 17 | 15.5 | 37.5 / 19 / 6 | 0.43 / 0.63 / 0.79 |
| Vibing++ | 6 / 5 / 9 / 25 / 36 | 394 / 424 / 438 | 403 | 18.5 | 20 | 29 / 25 / 8 | 0.19 / 0.48 / 0.59 |

On big maps: our longest is 10 / 13 / 14 / 14 / 23 / 35 at rounds 200 / 300 / 350 / 400 / 450 / end with feeding from
round 212 (median); WHQ 15 / 30 / 47 / 55 / 68 / 83 from round 270; test4 15 / 18.5 / 20.5 / 24 / 32.5 / 51 from round
328; forgot 6 / 13 / 29 / 41 / 52 / 55 from 303; SSS 13 / 18 / 33 / 41 / 49 / 56 from 277; Vibing++ 13 / 15 / 19 / 36 /
46 / 57 from 360. Share of potential in the longest at the end: 0.43 (ours), 0.48, 0.29, 0.49, 0.42, 0.39.

- **Share of the team's total length in the longest dragon at the end** (median; `e_out/c_leader.txt`): small maps
  51% (live bot), 57% (test builds), 64% (test4), 68% (WHQ), 53% (forgot), 68% (SSS), 44% (Vibing++); big maps 29%,
  28%, 17%, 32%, 33%, 28%, 25%. At round 400 on small maps, median longest over median total: 10 of 68 for us, 28 of
  82 for WHQ, 26 of 85 for SSS.
- **Start.** Three kinds of clock. Early: WHQ (315 small, 270 big) and SSS (311, 277). Middle: test4 (354, 328) and
  forgot (373, 303). Late: Vibing++ (403, 360) and we (401; 212 on big maps, where the 56-unit rule fires).
- **Speed once started.** The same for everybody: 11-18.5 segments in the 50 rounds after take-off. In the last
  hundred rounds the live bot's longest grows 10 and everybody else's 15.5-26, the test builds' 21.
- **By band of total length at round 400** (`a_curve.txt`, `c_leader.txt`): in level games on small maps (0.8-1.25)
  we win 9 of 30 (the red team's count: our longest 12 at round 400 and 28 at the end against the enemy's 16 and 39);
  the top three win 22 of 40. That band is a biased footing (section 2.0): at level POTENTIAL at round 300 or 350 we
  win 11 of 23 and 12 of 24. With level potential at round 400 (table A2, small maps, live bot, 18 races, 5 won) our
  longest is 12.5 / 22.5 / 34.5 at rounds 400 / 450 / end against the enemy's 15.5 / 33 / 40, and we end with 11 units
  against 4.
- **Terrain beyond the size.** Closed, crowded ground completes; open ground does not: final share of potential in the
  longest, all sides: Portals 0.85, Queen Of Spades 0.73, Tower Defense 0.70, weakhold 0.67, Maze 0.64; Slithery Fight
  0.48, Islands 0.47, Australia 0.39, Around UNSW 0.35. And the more closed the ground, the more our leader cuts
  itself: Portals 7.6 cuts a race after round 395, Around UNSW 5.6, Maze 4.2, Slithery Fight 4.2, Australia 2.6,
  weakhold 2.4, Default 1.2 (`e_out/opp.txt`).

### b. Where the leader's length comes from

Lineage of the final longest, small maps, pearls per race in rounds 250-299 / 300-349 / 350-399 / 400-449 / 450-499
(table B1):

| | natural pearls | own dragons dead by choice | other own corpses | enemy corpses | left behind in its own cuts |
|---|---|---|---|---|---|
| meow live bot | 4.0 / 5.0 / 3.7 / 3.5 / 5.0 | 0.1 / 0.2 / 0.2 / **10.2 / 6.1** | 2.2 / 2.0 / 2.0 / 1.7 / 1.5 | 0.2 / 0.4 / 0.3 / 0.4 / 1.2 | 0.0 / 0.7 / 1.4 / 2.3 / 3.7 |
| test4 (vs us) | 3.0 / 4.0 / 4.2 / 5.1 / 5.1 | 0.1 / 1.4 / **8.1** / 10.7 / 8.6 | 2.7 / 2.2 / 2.1 / 1.1 / 1.0 | 0.3 / 0.2 / 0.1 / 0.2 / 0.7 | 0.1 / 0.2 / 1.0 / 1.8 / 4.5 |
| WHQ (vs us) | 3.1 / 3.7 / 3.2 / 3.5 / 4.3 | 1.6 / **7.2 / 9.5** / 12.0 / 8.2 | 2.1 / 2.6 / 2.2 / 1.8 / 1.6 | 0.2 / 0.2 / 0.2 / 0.6 / 0.2 | 0.1 / 1.3 / 1.8 / 1.9 / 1.3 |
| forgot | 3.9 / 3.5 / 4.5 / 5.3 / 7.0 | 0.4 / 0.6 / **7.8** / 8.6 / 6.0 | 2.0 / 2.6 / 2.7 / 2.4 / 3.3 | 0.2 / 0.4 / 0.4 / 0.7 / 0.8 | 0.1 / 0.8 / 0.9 / 2.7 / 4.8 |
| SSS | 3.0 / 2.0 / 2.2 / 2.1 / 2.7 | 0.1 / **6.6 / 7.9** / 7.5 / 6.9 | 2.1 / 1.5 / 1.6 / 0.8 / 1.1 | 0.2 / 0.2 / 0.5 / 0.3 / 0.3 | 0.0 / 0.4 / 1.5 / 1.5 / 0.9 |
| Vibing++ | 3.5 / 3.7 / 4.3 / 5.1 / 6.8 | 0.8 / 1.6 / 2.2 / **10.3 / 6.1** | 2.0 / 2.0 / 2.0 / 1.8 / 1.9 | 0.2 / 0.1 / 0.3 / 0.5 / 0.5 | 0.4 / 0.6 / 0.9 / 2.1 / 1.8 |

- Natural pearls: 3-5 per 50 rounds for every leader, with or without a pearl zone. Paid steps: 0.0 for every team.
  Enemy corpses: under 1.5.
- The difference is feeding. Split by time it sits before round 400: in rounds 400-499 our lineage gets 16.3
  pearls of dragons dead by choice and the others 14.4-20.2; in rounds 300-399 ours gets 0.4 and theirs 8.4-16.7
  (Vibing++ 3.8). Split by what is fed it sits in the whole dragons (two bullets down).
- The team's cost: dragons dead by choice per 50 rounds have a summed length of 49 and 27 (ours, rounds 400-449 and
  450-499), 50 and 30 (our opponents), 31-39 and 20-26 (top three). Per segment a feeder spends, the final lineage
  gains 0.23 (live bot), 0.29 (test builds), 0.24 (our opponents), 0.27-0.29 (top three) on small maps and 0.16 / 0.14 /
  0.09 / 0.15-0.19 on big maps (table B2). Half is lost by the rule of the game; the other quarter is pearls that
  somebody else eats.
- Who eats the pearls of a death by choice, like for like (rounds 300-499, "The same test for every team" in section
  2): final lineage 39% (ours), 39% (our opponents), 45% (top three) on small maps; other own dragons 50-55%; the
  enemy 4.0% of ours (4.7% for the live bot) against 2.3% and 1.2%; nobody 7% against 4% and 3%.
- What is fed: in small feeders we match everybody (42-46 pearls a race from dragons of 2-4 on small maps; the top
  three 35-54; test4 and WHQ 51 and 69). test4 and WHQ add whole dragons: 26-29 pearls a race from dragons of 5 or
  longer against our 5-9 (top three 9-17), about half of them eaten by the final lineage; for our opponents together
  that is 10.7 of the 15.7 segments by which their lineage's intake from deaths by choice exceeds the live bot's
  (`e_merge.py`). On big maps everybody but us does it (38-124 pearls a race from dragons of 5+; ours 14-18).
- How far from the head: we die at three steps in 61% of cases and at one step in 5%; SSS at one step in 64%; the
  others at one step in 10-26%. The dragon fed eats 79-93% of the pearls of a feeder that died one step away, 66-84%
  at two steps and 63-78% at three (SSS 44-45% at three).
- Nearest enemy head when a feeder dies: median 8-11 cells for every team (9 for ours). The enemy's share of the
  pearls rises steeply only when its head is within 4 cells (15% of ours then) or 5-8 cells (8%); 48% of our feeders
  die with an enemy head within 8 cells, 34-41% of the others' (section 2h).

### c. Who the leader is and whether it lasts

| small maps | longest at round 400 is the final longest: same id / same lineage | at round 450 | cuts of the final lineage from round 400: all / with a free cell | longest of 15+ died, per race (how) | per 1,000 rounds with such a leader | steps it takes per 25 rounds at 400 / 450 | natural pearls it eats per 25 rounds at 400 / 450 | second longest / longest at the end | units at the end |
|---|---|---|---|---|---|---|---|---|---|
| meow live bot | 15% / 60% | 28% / 81% | 2.7 / 1.8 | 0.13 (6 rammed, 1 it rammed) | 2.2 | 53 / 59 | 1.5 / 2.3 | 0.33 | 7 |
| meow test builds | 12% / 56% | 32% / 88% | 2.7 / 1.7 | 0.04 (1 rammed) | 0.6 | 65 / 79 | 1.8 / 1.3 | 0.37 | 4 |
| test4 (vs us) | 3% / 59% | 31% / 76% | 2.1 / 1.5 | 0.10 (2 boxed in, 1 rammed) | 1.2 | 38 / 36 | 1.0 / 0.9 | 0.29 | 3 |
| WHQ (vs us) | 18% / 64% | 54% / 85% | 1.7 / 0.2 | 0.21 (6 by choice, 1 rammed, 1 boxed in) | 1.5 | 35 / 41 | 0.3 / 1.8 | 0.23 | 4 |
| forgot | 5% / 52% | 11% / 72% | 3.3 / 0.3 | 0.22 (12 rammed, 2 by an own dragon) | 2.0 | 52 / 56 | 2.2 / 1.7 | 0.30 | 6 |
| SSS | 31% / 79% | 55% / 81% | 1.6 / 1.6 | 0.24 (5 rammed, 4 it rammed, 1 by choice) | 2.0 | 40 / 41 | 0.2 / 0.6 | 0.15 | 6 |
| Vibing++ | 6% / 42% | 30% / 76% | 2.0 / 1.2 | 0.33 (7 rammed, 9 by choice, 4 it rammed, 2 boxed in) | 3.5 | 43 / 52 | 3.1 / 2.1 | 0.39 | 8 |

(`e_c.py`, `e_cutcost.py`, `e_cx.py` prints the rows side by side from `e_out/c_leader.txt`.)

- **Does it last?** By id, no, for anybody: the longest dragon of round 400 is the final longest in 3-31% of races. By
  lineage it is in 42-79% (ours 56-60%); at round 450 in 72-88%. The longest of round 300 is the final longest's
  ancestor in 9% of our races on small maps: the zone phase does not pick the dragon that will lead.
- **How it is lost.** A leader of 15+ dies in 0.04-0.33 races on small maps and 0.56-2.45 on big ones. Ours die only
  by rams (30 of 31 on small and big maps together for the live bot; the rammer is 2-4 long in 20 of 30); our
  opponents' die mostly boxed in on big maps (81 of 143; WHQ 38 of 55; test4 26 of 49), which ours never do. Per
  1,000 rounds with such a leader ours die at 2.2 (small) and 3.4 (big); test4's at 1.2 and 9.3, WHQ's 1.5 and 5.3,
  forgot's 2.0 and 4.9, SSS's 2.0 and 4.4, Vibing++'s 3.5 and 6.0. Median length lost 16-42; 25-30 rounds later the
  team's longest is 14-24 again (a second dragon takes over, or a new one is built: 3 to 20 in under 20 rounds in
  game 13).
- **Where it lives.** The same place for everybody: 9-15 cells from the own queen's start at round 400 (ours 9), with
  23-31 of 41 cells within four steps free (ours 28), the nearest enemy head 5-7.5 cells away at round 400 and 7-9 at
  round 450. Portals separate it from the enemy's start in a fifth to a half of the small-map races for every
  team. None of the three top teams hides its leader better than we do.
- **How much it moves, and whether it eats on its own.** Ours moves most: 53-59 steps per 25 rounds (test builds
  65-79) against 35-41 for test4, WHQ and SSS; forgot's and Vibing++'s move like ours (52-56, 43-52). It also eats
  the most natural pearls with Vibing++'s and forgot's (1.5-3.2 per 25 rounds; SSS's 0.2-0.7, test4's 0.9-1.5).
  SSS's leader stands and is fed; ours and Vibing++'s walk and eat (`LEADER_ENDGAME_PEARL_MULT 4`; inference from the
  source for ours). In game 8 that walk took our 35-long into a one-wide dead end for two pearls.
- **One leader or several.** Small maps: one. Second longest / longest at the end is 0.15 (SSS) to 0.39 (Vibing++),
  ours 0.33. Big maps: several, for everybody but SSS: 0.57-0.62 (ours), 0.72 (our opponents), 0.62 (forgot), 0.61
  (Vibing++), 0.45 (SSS); WHQ ends big-map races with 83 / 60 / 41. In 38 of our 102 lost races our final longest plus
  half of the rest of our length would have beaten the enemy's final longest (28 of the live bot's 69); for the top
  three that is 22 of 67 losses on small maps and 87 of 114 on big ones. Nobody finishes on big maps.

### d. Our two switches as natural experiments

Tables in section 2d (`e_d.py`).

1. **The leader zone.** It does what the code says and nothing for the leader. After the switch a small dragon of
   ours takes a free pearl inside its believed leader's zone in 26% / 22% of turns (small maps, rounds 300-349 /
   350-399) and 24% / 19% (big maps, rounds 150-199 / 200-249); outside the zone 87% / 87% and 77% / 77%. Of the
   pearls left lying in the zone the leader eats 12% / 11% (small) and 7% / 17% (big); an own dragon under 8 eats
   69-73% and 58-69% of them a median 7-10 rounds later; the enemy 2-6% and 8-13%; 6-12% lie for 30 rounds. The
   leader's own natural intake does not rise at the switch (1.7 to 1.6 a game on small maps, 4.0 to 3.4 on big). The
   team's falls from 20.8 to 15.6 a game on small maps and from 79.5 to 52.7 on big maps. On weakhold, where the
   zone's 181 cells are a third of the board, it starves the team: 40 natural pearls in rounds 250-299, then 16, 9
   and 3 (game 11); 47, 26 and 4 (game 12); total length 94 to 59 in a hundred rounds with nobody feeding.
2. **Feeding.** The start is where the code puts it: at round 201-224 when we had 56 units at round 200 (35 of 35
   live-bot games), at 302-375 in queen-feeding mode (20 of 27), at 401-405 otherwise. Early and late starts are
   therefore different kinds of game (the early ones are our richest), and a comparison inside a band has 6 games
   against 17: early 3 won, longest 15 / 58.5 / 75.5 at rounds 400 / 450 / end; late 2 won, 11 / 21 / 28. It shows
   that our feeding can build a 75-long when it has 54 units to spend, not that the start caused it.
3. **Which mechanism builds our leader.** Feeding, and only feeding. Small maps, lineage: the zone phase (rounds
   300-399) brings 8.7 natural pearls, 0.4 feeder pearls and 4.0 pearls of other own corpses in a hundred rounds and
   loses 2.1 in cuts; the feeding phase brings 8.5, 16.3 and 3.2 and loses 6.0. Big maps: from round 250 to 399 the
   lineage gets 1.7-2.6 feeder pearls per 50 rounds out of 18-20 segments of dragons dead by choice, and our longest
   is 10 at round 200 and 14 at round 400.

### e. The trigger of the others

Table in section 2e (`e_e.py`). It is a clock in every bot, tied to the own unit count in four of five.

| | 56+ units at round 200 | 30-55 units | under 30 units | moves with the own queen's death? |
|---|---|---|---|---|
| WHQ | round 270-272 (53 of 53 games) | 295 / 303 / 325 | 314 / 334 / 374 | no |
| SSS | 221 / 287 / 302 | 301 / 307 / 332 | 301 / 303 / 321 | no (301 / 300 / 293 / 302 by the queen's death round) |
| forgot | 300 / 303 / 344 (162 of 162) | 362 / 371 / 377 | 373 / 381 / 437 | no |
| Vibing++ | 337 / 360 / 368 | 344 / 369 / 402 | 364 / 403 / 421 | no |
| test4 | 268 / 327 / 374 | 320 / 354 / 378 | 376 / 382 / 392 | yes: 293 / 354 / 391 for a queen dead in rounds 100-199 / 200-299 / 300-399; never before round 258; while she lives it feeds her |
| meow | 201 / 205 / 224 | 331 / 401 / 405 | 402 / 405 / 422 | only through queen-feeding mode |

(Quartile / median / quartile.) Not triggers for anybody: the enemy queen's death, the distance of the nearest enemy
head to the leader (6-9 cells before and at the start), the enemy's longest dragon (8-15 at the start, any). Whether
they test the unit count or the map size cannot be told from replays; both give this table. Between their queen's
death and the start they do not gather (13-20 own heads within 15 cells of the longest, 50 rounds before the start
and at it) and they keep eating (86-106 natural pearls per 50 rounds). SSS's and WHQ's first feeders die next to a
dragon of 4-10 (games 3, 4, 23, 24, 25): they do not wait for a leader to exist; the feeding makes it.

### f. The close read

Stories in section 4. What the winners of the 14 lost races did that we did not, counted over the 14:

- **Started earlier: 11 of 14** (by 25 to 130 rounds; not games 6, 11, 14).
- **Kept the fed dragon's id.** The opponent's fed dragon kept one id for 80 rounds or more while it was fed in 8 of
  the 14 (games 1, 2, 4, 5, 7, 8, 9, 14: for instance rounds 325-430 in game 1, 351-431 in game 2, 248-499 in game
  14); ours was cut 3 to 19 times from round 395 in 13 of the 14 (twice in game 3), and with a free cell in most (15
  of 19 in game 9, 7 of 7 in game 12).
- **Merged the second dragon in the last 50 rounds: 5 of 14** (a 32-long at round 485 in game 2, 18 at 466 in game 3,
  21 at 481 in game 4, 31 at 453 in game 5, 18 at 455 in game 8; 8-13 of its 9-16 pearls eaten by the leader each
  time). We did it once (game 5, 18-long, 5 of 9 pearls) and failed three times in game 14 (3 of 27 pearls).
- **Fed where the leader was.** In game 12, 21 of our 28 deaths by choice were next to no bigger dragon; in game 5,
  20 of 39 after round 425; in game 9, 8 of 39 were next to the longest. WHQ in game 12: 11 of 11 within two steps
  of its longest.
- We were **level or ahead in the longest dragon at some round after 425 and still lost in 7 of 14** (games 3, 5, 6,
  8, 10, 12, 13). In five of the seven the segments our lineage left behind in its own cuts from round 400 are more
  than the margin (5, 6, 8, 12, 13); in game 3 nine dragons stood more than 15 cells away with 52 segments; in game
  10 it was cuts and feeders dying elsewhere.
- **Not different:** speed once started (game 2: our 10 to 56 in 50 rounds against WHQ's 7 to 52 in 50), natural
  pearls, losses of feeder pearls to the enemy (1-3 pearls a game in these 14), leader deaths (two of ours rammed, in
  games 11 and 13, at the same passage where we rammed WHQ's).
- **The other seven** were not lost in the last 75 rounds: potential or clock (1, 2, 4, 7, 14), no leader over 16 at
  any time (9), starved in the zone and then rammed (11).

And the eight wins of ours read: in six the opponent threw the race away (test4 waited for its queen or had no
leader in 21 and 22; test4 lost a 28-long boxed in after a cut in 17; WHQ ended with three leaders, lost big dragons
to our rams and to deaths without an order in 19 and 20; WHQ ran out of material in 16); in one we simply fed one id
for 150 rounds (15).

### g. The earlier trials

From `work/plan.md` (29 September to 2 October; the log has no entry called card #14 or card #22; what is known of
those two is one line each in `findings.md` section 7: "#14 split stop (no gain locally)", "#22 late feeding").

| trial | what was changed | where | result | what the replays say now |
|---|---|---|---|---|
| "ENDGAME 350" | `ENDGAME_ROUND` 400 -> 350 | local, v41 against v41, 96 games | 48 of 96, "neutral, because v41-vs-v41 is symmetric" | a mirror match cannot show a clock: both sides move |
| v46 | `ENDGAME_ROUND` 400 -> 330 | online, 50 games against five top teams and 60 against dev test 1 | 10-40 where v41 had 20-30; games decided before round 330, with identical code, went 6-18 against 11-14, "opponent drift or variance, not v46"; dev test 1 24 of 60 against 23 | no evidence either way; the old bot, the old map pool |
| ef1 | `LC_FEED_ROUND` 330 ("F330"), 300 ("F300"), 330 with `FEEDER_APPROACH` 25 ("F330A") | local against v52, 152 games | 70, 69, 68 where the base won 76 ("early feeding is locally negative again") | in a local game both teams reach "top 39 at round 400, total 220" (the log's own note); an earlier start spends units that are worth more as eaters on a rich board. And the leader it feeds is the same leader: cut 2.7 times a race and unknown to the team for 27 rounds after each cut. More feeding rounds are more rounds of that |
| fe1 | `FEED_EARLY_ROUND` 300 / 250 (dragons up to a set length may feed before the phase), `LC_LEAD_MULT` 2 / 3 | local against v52 | 73, 74, 76, 77 of 152 against 76 | neutral; same reading |
| fl1 | `FEED_LOCAL` 2 / 3: in the feeding phase a dragon dies when a visible own head within 2-3 steps has at least twice its length (not the leader: any) | local against v52 | 70, 74, 69 against 76 | this is the test "die next to a big dragon you can see" in its loosest form, and it feeds local dragons: on the same footing that is what our opponents do on big maps (58% of deaths next to a dragon that is not the longest) for 16% of the pearls to the final lineage against our 26%. A rule that sends pearls to any big dragon is not the rule proposed here |
| rl1 | `RALLY_FRESH` 15 / 25 (dragons farther than `FEEDER_APPROACH` walk to the leader's last known place) | queued 30 September | no result in the log | the log's own reason for it stands: "v41 has RALLY_FRESH=0, so dragons more than FEEDER_APPROACH (15) from the leader never go to it. That is why many small dragons remain at the end". Game 3 was lost that way (9 dragons, 6 beyond 15 cells, 52 segments, margin 6) |
| gb1, q2, sw7 | `LEADER_GROW_ROUND_BIG` 150 -> 300 ("GB300") | local | 30 of 64 against 20 (buggy base); 46 of 96 against 48; 73 of 152 against 76 | candidate 3's subject; the zone's cost is on the ladder, where the enemy eats what we leave (8-13% of the pearls left in the zone on big maps) |
| lc1, v47, as1 | `LC_LEAD_ROUND` 200 on every map (leader, zone and split stop at round 200) | local 52 of 96 against 48; online 19 of 60 against dev test 1 where the base had 23-24; with assassins 44 of 96 | "REJECT global early leader" (the user: fewer expanding dragons, one dragon that is easy to snipe) | agrees with section 2d: the zone phase costs a fifth to a third of the natural intake and gives the leader one pearl per 50 rounds; and with 2h: an early leader of 15-24 is rammed 6.9 times per 1,000 rounds before round 300 against 3.8 after 400 |
| q2 | "BOOT10", "BOOT16" (most likely `FEED_BOOT_LEN` 10 / 16; the log gives only the labels) | local | 43 and 40 of 96 against 48 | rejected by the team; not looked at here |
| LG5k | leader guard | local | 50 of 96 (+5 -3) | too few flips to say |
| be1-be4 | `BIG_ESCAPE_STEPS`, `BIG_ESCAPE_LATE`, `BIG_TRUE_REACH` (a long dragon sprints out of an enemy's reach) | local, four batches, also against a leader-hunting sparring bot | all neutral or negative; "big head-on victims are mostly NOT the leader (second dragons)" | agrees: in races our leader of 15+ dies in 0.13 (small) and 0.56 (big) races, less often than our opponents' on big maps |
| QF3, SF300 (v58, v59) | `QUEEN_GAME_FEED_ROUND` 300, `QUEEN_SAFE_ROUND` 300 (feed a living queen from round 300) | local +11 -4 and +15 -5; adopted | in the live bot | outside this read (queen alive) |
| eg1 | `ENDGAME_ROUND` 350 / 450 | queued 2 October | no result in the log | - |

The team's own diagnosis in the same log is close to this report's and was never turned into a trial: "feeders feed
non-top leaders ... 65% of v42 feeds and 50% of v41 feeds go to a non-top dragon. Leader info splits by region";
"believed length < own length*2 is already a rule, but belief goes stale"; "feeds to a non-top believed leader:
24/37, 18/25, 29/42"; "NEXT: ... refuse to feed a leader much shorter than the max leader length ever heard"; "our
consolidation effectively starts at r430-450; theirs at r350-400"; "growth after r400 is equal. The gap exists AT
r400: they are ahead in r300-400"; "top-3 at r499 e.g. 53/43/34 vs 64/28/7 ... FEED_LEN_RATIO 2 keeps big dragons
from feeding; regions elect separate leaders". No trial touched the three things candidate 5 names: the leader's own
cuts, the stale record after a cut, and dying next to nothing.

**Does what is seen now explain the neutral results of the earlier-start trials?** Partly, and only as an inference.
(1) They were local mirror games on a rich board, where the gap that the ladder shows in rounds 300-399 does not
exist. (2) The one online trial was swamped by drift. (3) An earlier start does not repair what loses the level races
we lose (seven of 14 lost after being level or ahead at round 425 or later). (4) "The enemy eats the pearls" is not
the explanation: 4.7% of the pearls of our deaths by choice on small maps go to the enemy. "The feeders die too far
away or next to the wrong dragon" is half of one: a quarter of our deaths by choice are next to nothing, and of the
rest 61% are three steps from the dragon they feed.

### h. The risks, counted

Tables in section 2h (`e_h.py`), `e_out/cutcost.txt`, `e_out/heir.txt`.

- **An early, long leader is rammed more often, for everybody.** Per 1,000 rounds with a leader of 15-24: 4-7 before
  round 300 against 1-4 after (ours 6.9 / 4.6 / 3.8 for rounds 150-299 / 300-399 / 400-499; our opponents' 3.1 / 1.2 /
  1.2; forgot's 5.2 / 1.6 / 3.7; SSS's 5.9 / 2.0 / 0.9; Vibing++'s 4.3 / 2.6 / 2.1). Ours is rammed two to three times
  as often as our opponents' at every stage; the rammer is 2-4 long in 38 of 62 cases. At 3-4 per 1,000, a leader
  that exists for 100 rounds is rammed in one game in three.
- **What early feeding costs.** Units halve in 50-100 rounds (forgot 52.5 -> 30 -> 19, Vibing++ 56 -> 34 -> 27, our
  opponents 61 -> 46 -> 31; SSS less: 60 -> 51 -> 45), natural intake falls by a tenth to a third (forgot 86 -> 74 ->
  63 per 50 rounds), potential stays flat (97 -> 99.5 -> 101).
- **Does the first starter lose more on wipe-outs or the queen rule?** No. Top-three sides that start at least 25
  rounds before the other side win 352 of 531 games (66%) and 25 of 30 wipe-outs; when the other side starts first
  they win 142 of 288 (49%). For our sides 32 of 111 against 10 of 102. Not a clean effect of the start: the richer
  team has more units and its clock runs earlier.
- **How much of our feeding goes to the enemy.** 5.1% of our feeders' pearls (live bot; test builds 3.5%; our
  opponents 1.8%; forgot 0.6%; SSS 2.1%; Vibing++ 1.7%). 15% when an enemy head is within 4 cells of the dying feeder
  (5% of our feeders), 8% at 5-8 cells (43%), 2% at 9-15, under 1% farther. On big maps, on the like-for-like count,
  10.5% (others 1.8-6.0%). "Our late feeding often feeds the opponent" is one pearl in twenty on small maps and one
  in ten on big ones; seven times as many go to another small dragon of ours.
- **The leader's own cuts as a risk, and whether to forbid the early one.** A cut costs 2 segments (5.4 a race from
  round 400; more than the margin in 10 of our 102 lost races) and, in our team, about 25 rounds of feeding. Making
  the leader wait until it has no free cell, as forgot and WHQ do (0.3 and 0.2 early cuts a race), is not supported
  by what was counted: in three of four of our early cuts the pocket ahead holds four cells or fewer, so the cut
  would come a few rounds later anyway; and waiting is safe for forgot (one leader of 15+ lost boxed in, in 154
  races) but not for WHQ (one in 39 races on small maps, 38 in 35 races on big ones, in its games against us), for a
  reason a replay shows only as the death. Our leaders of 15+ never die boxed in. The candidate leaves the cut as it
  is and repairs what follows it.
- **The heir.** After a leader cut the child dies within one round in 1.6-2.0% of our cuts (0-3.1% for the others)
  and cuts again within three rounds in 10-13% (7-26%). A same-round chain of three or more cuts of the final lineage
  happened in 3 of our 143 races and in 13 of the top three's 447 (from round 350; `e_out/cutcost.txt`).

### i. The rule

Section 7. In one sentence: the team feeds one dragon; that dragon keeps the role through its own cuts (the team follows the new id within a few
rounds); and a dragon gives its life only next to a leader it can see is long.

## 6. The race, us against the others

One row per behaviour. Races only (round-500 games with both queens dead) unless a row says "all games". "s / b" =
small maps (1,200 cells or fewer) / big maps. meow = live bot, with the test builds in brackets where they differ.
Our opponents = the other side of our own races (test4 and WHQ are 123 of the 143). Sources: the tables of section 2.

| behaviour | meow | our opponents | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|
| races, won | 96, 27 (47, 14) | 143, 102 | 154, 85 | 141, 82 | 152, 99 |
| own potential / enemy potential at round 300 (median) | 0.62 (0.60) | 1.62 | 1.02 | 1.13 | 1.29 |
| races won at level potential (0.8-1.25) at round 300 / 350 | 11 of 23 / 12 of 24 (all builds) | 12 of 22 / 12 of 24 | 29 of 52 / 28 of 55 | 39 of 71 / 47 of 80 | 31 of 46 / 28 of 43 |
| ... against test4 and WHQ only, at round 350 | 10 of 21 | - | - | 7 of 9 | 11 of 13 for the three together |
| what starts leader feeding | 56 units after round 200, else round 400 | WHQ: units (270 / 303 / 334); test4: its queen's death + about 90 rounds | units (303 / 371 / 381) | round 300, earlier with a full team on big ground | units (360 / 369 / 403) |
| leader feeding starts, median round, s / b | 401 / 212 | 329 / 271 | 373 / 303 | 311 / 277 | 403 / 360 |
| longest at 300 / 400 / end, s | 4 / 10 / 20 (4 / 11 / 30) | 5.5 / 18.5 / 37 | 5 / 16 / 36 | 6.5 / 26 / 38.5 | 6 / 9 / 36 |
| longest at 300 / 400 / end, b | 13 / 14 / 35 | 24 / 43 / 68 | 13 / 41 / 55 | 18 / 41 / 56 | 15 / 36 / 57 |
| final lineage first 15 long (median round), s | 406 | 388 | 394 | 356.5 | 424 |
| growth of the longest in the 50 rounds after take-off, s | 11 (18.5) | 15 | 14 | 17 | 18.5 |
| growth of the longest from round 400 to the end, s / b | 10 / 14 (21 / 9.5) | 24 / 25 | 20 / 18 | 15.5 / 19 | 20 / 19 |
| share of potential in the longest at the end, s / b | 0.65 / 0.43 (0.71 / 0.43) | 0.77 / 0.40 | 0.69 / 0.49 | 0.79 / 0.42 | 0.59 / 0.39 |
| final longest / potential at round 300, s / b | 0.65 / 0.42 (0.79 / 0.36) | 0.75 / 0.38 | 0.85 / 0.53 | 0.73 / 0.46 | 0.71 / 0.46 |
| units at 300 / 400 / end, s | 26 / 21 / 7 | 33 / 18.5 / 4 | 24 / 14 / 6 | 37.5 / 19 / 6 | 29 / 25 / 8 |
| final lineage: natural pearls per 50 rounds (rounds 300-499), s | 3.5-5.0 | 3.6-5.0 | 3.5-7.0 | 2.0-2.7 | 3.7-6.8 |
| final lineage: pearls of own dragons dead by choice, rounds 300-399 / 400-499, s | 0.4 / 16.3 (0.5 / 24.0) | 13.3 / 18.8 | 8.4 / 14.6 | 14.5 / 14.4 | 3.8 / 16.4 |
| deaths by choice per race, rounds 300-499, s / b | 33 / 47 | 46 / 114 | 27 / 65 | 47 / 79 | 27 / 53 |
| ... pearls they drop per race, s / b | 47 / 71 (55 / 79) | 85 / 260 | 49 / 122 | 71 / 130 | 44 / 103 |
| ... share of those pearls the final lineage eats, s / b | 36% / 27% (45% / 24%) | 39% / 16% | 47% / 26% | 41% / 31% | 46% / 29% |
| ... share the enemy eats, s / b | 4.7% / 10.5% (2.8% / 7.5%) | 2.3% / 5.3% | 0.6% / 1.8% | 1.6% / 3.9% | 1.3% / 3.7% |
| ... died within 3 steps of the team's longest, s / b | 42% / 30% | 42% / 15% | 51% / 26% | 73% / 52% | 35% / 21% |
| ... died with no own dragon twice as long within 8 steps, s / b | **26% / 20%** | 15% / 11% | 8% / 5% | 10% / 6% | 14% / 10% |
| pearls per race from dragons of 5+ that die by choice, rounds 300-499, s / b | 4.9 / 13.8 (8.7 / 17.5) | 25.5 / 123.9 | 13.4 / 38.9 | 16.6 / 44.2 | 8.8 / 37.8 |
| dragons of 8+ that die by choice in rounds 450-499, per race, s / b | 0.30 / 0.65 (0.40 / 0.86) | 1.24 / 4.34 | 0.17 / 0.81 | 0.62 / 1.27 | 0.28 / 1.40 |
| a feeder dies 1 / 2 / 3 steps from the dragon it feeds (all games), s | 5% / 33% / 61% | 18% / 39% / 43% | 13% / 37% / 50% | 64% / 26% / 10% | 10% / 41% / 49% |
| the dragon fed eats, of pearls dropped 1 / 3 steps away (all games), s | 90% / 74% | 84% / 66% | 89% / 70% | 84% / 44% | 83% / 71% |
| how a feeder dies | gives no order | WHQ: gives no order; test4: runs into itself | gives no order | gives no order (some run into themselves) | not looked at |
| cuts of the final lineage from round 400, per race: all / with a free cell | 2.7 / 1.8 | 2.0 / 0.8 | 3.3 / 0.3 | 1.6 / 1.6 | 2.0 / 1.2 |
| lost races in which the segments left in those cuts exceed the margin | 9 of 69 (1 of 33) | 1 of 41 | 14 of 69 | 4 of 59 | 7 of 53 |
| growth of the longest per 25 rounds from round 400: windows with a cut / without, s | 4.0 / 13.4 (9.9 / 9.7) | 6.8 / 7.9 | 8.7 / 5.9 | 2.4 / 6.2 | 8.0 / 5.8 |
| ... the same, b | 4.8 / 8.6 (3.1 / 8.9) | 5.5 / 6.3 | 3.8 / 4.6 | 2.8 / 6.6 | 4.5 / 8.2 |
| after a cut, rounds until half the team names the new longest (median) | 27 (388 cuts, readable games) | cannot be seen | cannot be seen | cannot be seen | cannot be seen |
| longest at round 400 is the final longest, same id / lineage, s | 15% / 60% | 12% / 62% | 5% / 52% | 31% / 79% | 6% / 42% |
| longest of 15+ dies, per race, s / b | 0.13 / 0.56 (0.04 / 0.59) | 0.15 / 2.20 | 0.22 / 1.04 | 0.24 / 1.13 | 0.33 / 1.48 |
| ... how, s and b together | 30 rammed, 1 it rammed | 54 rammed, 84 boxed in, 13 by choice, 4 in rams of its own | 102 rammed, 1 boxed in, 2 by choice, 2 by an own dragon | 94 rammed, 14 boxed in, 8 by choice, 6 in rams of its own | 87 rammed, 25 boxed in, 24 by choice, 10 in rams of its own |
| leader of 15-24 rammed per 1,000 rounds with one, rounds 150-299 / 300-399 / 400-499 (all games) | 6.9 / 4.6 / 3.8 | 3.1 / 1.2 / 1.2 | 5.2 / 1.6 / 3.7 | 5.9 / 2.0 / 0.9 | 4.3 / 2.6 / 2.1 |
| the leader at round 400: steps per 25 rounds; natural pearls per 25 rounds, s | 53; 1.5 (65; 1.8) | 38; 0.7 | 52; 2.2 | 40; 0.2 | 43; 3.1 |
| the leader at round 400: cells to the nearest enemy head; to its own queen's start, s | 7; 9 | 6; 9.5 | 7; 15 | 7.5; 11.5 | 7; 15 |
| second longest / longest at the end, s / b | 0.33 / 0.57 | 0.27 / 0.72 | 0.30 / 0.62 | 0.15 / 0.45 | 0.39 / 0.61 |
| units at the end, s / b | 7 / 20 (4 / 18.5) | 4 / 13 | 6 / 11 | 6 / 31 | 8 / 20 |
| lost races in which the final longest plus half of the rest would have beaten the enemy's longest, s / b | 10 of 35 / 18 of 34 (3 of 14 / 7 of 19) | 10 of 29 / 12 of 12 | 12 of 28 / 29 of 41 | 4 of 19 / 31 of 40 | 6 of 20 / 27 of 33 |
| a "leader zone" (small dragons leave pearls near the leader) | yes: take rate 26% inside, 87% outside | no (83% falling slowly to 71% by round 449, no step) | no (90-94%) | no (77-86%) | no (87-90% until round 350, 70-79% after) |
| side that starts leader feeding first by 25+ rounds wins (all games) | 32 of 111; when second 10 of 102 | 92 of 102; 79 of 111 | top three together: 352 of 531; 142 of 288 | | |

How to read the table in a few lines. Where the others differ from each other (start, speed, how many leaders, how
near the feeders die, whether whole dragons are fed) they differ as much as they differ from us, and the rank-1 team
is the one most like us. Where all of them differ from us: we arrive with 0.62 of the enemy's potential; a quarter
of our deaths by choice are next to nothing; our leader's growth halves around its own cuts (SSS's does too); we run
a pearl zone. Where our two usual opponents differ from us and from the top three on small maps: they feed whole
dragons to the leader late. And the first item of that list is the one that decides most races.

## 7. Candidate 5: one leader, known to all

Written in the seven items of `hypotheses.md`. It is a candidate hypothesis, not a result: nothing here was played.

### 1. The claim

**Once the team feeds a leader, every dragon follows the same one, and follows it through its cuts: when the leader
hands its length to a new dragon, that dragon is the leader for the whole team within a few rounds. And a dragon
gives its life only within reach of a leader that it can see is long.**

In our bot today the first half fails for about 25 rounds after every cut and the second half fails for a quarter of
our deaths by choice. Two things change, both in how a dragon keeps and uses its one record of "the leader":

- **Fresher news of a nearly-as-long dragon replaces older news of a longer one.** Today only length counts, so the
  last report of the old leader (longer by the 2 segments of the stub, up to 25 rounds old) beats every report of
  its heir until it expires.
- **What a dragon sees beats what it remembers.** Today a dragon that stands next to the id in its record dies for
  it if the recorded length is twice its own, even when the dragon in front of it is a 2-long stub or a 5-long that
  was once believed longer.

The rule names no map and no map size, moves no clock, and leaves the leader's cuts, the start of feeding and the
pearl zone as they are.

### 2. Evidence

**What the code does** (read in `mybot2/main.cpp`; line numbers of the copy read on 5 October; not seen in replays).

- Every dragon holds one leader record: `known_leader_id / _len / _round / _pos / _dir`. Each turn it first feeds
  itself into the record (`hear_exact(ct.get_id(), length, round, ...)`, line 1311), then every ping it hears
  (`hear_sonar()` -> `hear_exact()`), then every own head in its 7 x 7 view (`hear_sighting()`, line 1394), and at the
  end of its turn it sends the record on four rays (`broadcast_leader()`, line 1694). A record older than
  `SONAR_STALE` 25 rounds is dropped (`expire_leader()`, line 1600) and reports older than that are not accepted
  (`plausible_report()`).
- `hear_exact()` (line 1609): a report about the id already held replaces it when it is as fresh or fresher, also
  when shorter. A report about another id is taken only when its `leader_priority()` is higher, and that priority is
  the length (plus 1,000 for the queen in a queen game). The age of the two reports is used only to break a tie.
- `hear_sighting()` (line 1645): for the id already held it sets the position and
  `known_leader_len = max(known_leader_len, visible)`; `visible` is the number of segments of that dragon inside the
  view, so a sighting can raise the recorded length and never lower it, and it does not refresh the round. Another
  dragon in view replaces the record only if its visible segments alone exceed the recorded length.
- A cut (`escape_child_size()`, line 1002: the child gets `length - 2`): the stub keeps the old id and from its next
  turn reports itself as 2 long; dragons that hear the stub directly learn it. Everybody else holds "old id, full
  length" until 25 rounds after the last exact news, repeats it on four rays every turn, and so hands it back to any
  dragon that had dropped it: a 12-long local dragon in a record loses to "old id, 34 long, 20 rounds old". The heir
  reports "new id, 32 long, now" and loses the same comparison.
- Whom a dragon feeds: `pick_feed_target()` (line 1878) needs the feeding phase, a record of another id,
  `feed_len_ok()` (own length x `FEED_LEN_RATIO` 2 <= the recorded length) and the recorded place within
  `FEEDER_APPROACH` 15 cells. `ready_to_die()` then needs no enemy head within 4 cells and either a drop cell, or
  `beside_visible_leader()` (line 1916): the head of the recorded ID in view within `FEEDER_DIE_DIST` 3 cells. It is
  the id that must be in view, not a long dragon. The bot then returns without an order (`act()`, line 526, logged
  "FEEDDIE").
- The same record drives the pearl zone (`refresh_leader_zone()`, line 1921) and "I am the leader" (`is_leader()`).

So after a cut the code predicts: feeders near the stub may still die for it; feeders near the heir may not die for
it; and the zone moves to the stub. All three are in the replays.

**What our replays show** (measured; sections 2 and 4).

| | number | where |
|---|---|---|
| rounds after a leader cut until half of our dragons name the new longest (median; quartiles) | 27 (17 to 36-41), 388 cuts | `e_bel.py`, 78 games with readable pings |
| in between, the id most of them name is dead / alive but under half the true longest | 36-44% / 28-34% of samples | `e_bel.py` |
| rounds 400-494: samples in which under a quarter of our dragons name the true longest | 187 of 347 | `e_churn.py` |
| growth of the longest over the next 5 rounds: under a quarter name it / a quarter to a half / a half to three quarters / more | +0.42 / +1.85 / +1.51 / +2.00 | `e_churn.py` |
| ... the same against test4 / WHQ / others (under a quarter; otherwise) | 0.40; 1.45 / 0.35; 2.41 / 0.46; 1.63 | `e_out/opp.txt` |
| dragons that could feed the true longest by our rules, small maps, rounds 400-424 / 425-449 / 450-474 | 5.2 / 3.0 / 1.5; without the belief test 9.3 / 5.2 / 4.1 | `e_bel.py` |
| growth of the longest per 25-round window from round 400 (10+ other dragons): a cut in it or just before / none | 5.0 (291 windows) / 10.8 (91) | `e_churn.py` |
| ... live bot / test builds | 4.5; 11.4 / 6.1; 9.3 | |
| ... against test4 / WHQ / everybody else | 4.9; 11.4 / 5.5; 10.9 / 3.7; 9.6 | |
| ... every run of the live bot separately (ladder 4 October, stride, passage2, qh31) | 4.3; 11.9 / 3.8; 10.4 / 5.1; 9.2 / 5.3; 14.1 | `e_out/era.txt` |
| our deaths by choice in races, rounds 300-499, with no own dragon twice as long within 8 steps | 26% (small maps), 20% (big) | `e_dist.py` |
| the final lineage's share of the pearls: death next to the longest / next to nothing | 70% / 13% (small), 61% / 7% (big) | `e_dist.py` |
| all our `noaction` deaths in races: next to the true longest / another dragon of 8+ / a dragon under 8 / nothing | 42% / 23% / 20% / 15% of 5,559 | `e_bel.py` |

**Us against the others, like for like** (measured; "The same test for every team", section 2; races, rounds 300-499).

| | meow | our opponents | test4 | WHQ | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|---|
| deaths by choice next to no bigger dragon, small / big maps | **26% / 20%** | 15% / 11% | 20% / 17% | 12% / 9% | 8% / 5% | 10% / 6% | 14% / 10% |
| next to the team's longest | 42% / 30% | 42% / 15% | 41% / 13% | 45% / 16% | 51% / 26% | 73% / 52% | 35% / 21% |
| pearls eaten by the final lineage | 36% / 27% (test builds 45% / 24%) | 39% / 16% | 36% / 17% | 40% / 15% | 47% / 26% | 41% / 31% | 46% / 29% |
| growth per 25-round window with a cut / without, small maps | 4.0 / 13.4 (test builds 9.9 / 9.7) | 6.8 / 7.9 | 8.5 / 7.6 | 5.7 / 8.3 | 8.7 / 5.9 | 2.4 / 6.2 | 8.0 / 5.8 |
| ... big maps | 4.8 / 8.6 | 5.5 / 6.3 | 4.8 / 7.7 | 6.2 / 6.7 | 3.8 / 4.6 | 2.8 / 6.6 | 4.5 / 8.2 |
| cuts of the final lineage from round 400, per race | 2.7 | 2.0 | 2.1 | 1.7 | 3.3 | 1.6 | 2.0 |

Read honestly: per pearl we already do as well as test4 and WHQ, and the leader is cut about as often in every team.
What is ours alone is the first row. The window contrast is ours and SSS's on small maps (and several teams' on big
maps); forgot, WHQ and Vibing++ grow as fast around a cut as away from it, so a team whose feeders follow the new id
at once exists. Whether they do it by a better record or by something else cannot be seen.

**Winners against losers of level races** (measured; `e_wl.py`, `e_out/wl.txt`; own potential / enemy potential at
round 350 between 0.8 and 1.25; medians, means for the last five columns).

| | sides | leader feeding starts | longest at 350 / 400 / 450 / end | share of potential in the longest at the end | units at the end | cuts of the final lineage from round 400: all / with a free cell | deaths by choice, rounds 300-499 | next to the longest / next to nothing | pearls to the final lineage |
|---|---|---|---|---|---|---|---|---|---|
| meow, won | 12 | 402 | 11 / 14.5 / 27.5 / 48.5 | 0.79 | 5 | 3.6 / 2.2 | 52 | 40% / 20% | 39% |
| meow, lost | 12 | 403 | 13 / 13 / **31 / 30** | 0.62 | 12.5 | **6.6 / 4.1** | 57 | 38% / 19% | 36% |
| our opponents, won | 12 | 308 | 12.5 / 26.5 / 45.5 / 62 | 0.84 | 2.5 | 2.9 / 1.3 | 64 | 45% / 8% | 42% |
| our opponents, lost | 12 | 358 | 10.5 / 15.5 / 37.5 / 30 | 0.74 | 4 | 1.9 / 0.9 | 46 | 39% / 13% | 28% |
| top three, won | 103 | 306.5 | 25 / 38 / 53 / 69 | 0.50 | 18 | 2.4 / 1.2 | 70 | 45% / 7% | 38% |
| top three, lost | 75 | 306.5 | 26 / 35 / 43 / 38 | 0.43 | 14 | 2.2 / 1.2 | 59 | 42% / 7% | 23% |

Our level races are decided in the last 50 rounds, and not by the clock: winners and losers both start at round
402-403; at round 450 the losers are ahead (31 against 27.5); then the winners add 21 and the losers lose 1. The
losers' final lineage is cut 6.6 times from round 400 against 3.6, and they end with 12.5 units against 5. For the
top three the same split shows as "who ate the pearls": the losers' final lineage got 23% of them, the winners' 38%,
with the same start and the same number of cuts. Twelve games a side for ours: the difference in cuts (6.6 against
3.6) is large, the rest is within what twelve games can give by chance.

**Games that show it and its absence** (section 4).

- Absent. 1027971 (Portals, against WHQ), rounds 400-490: the leader cuts at round 400 with 11 feeders ready; at
  rounds 410 and 420 nobody names the true longest and 11-12 of 13-14 name the 2-long stub; again from round 450 to
  474 (a dead id, 25 long). We lead 23 to 21 at round 440 and lose 19 to 30. 1027819 (Maze, against test4), rounds
  421-453: no feeder dies next to our 31-34-long leader for 32 rounds; five die in rounds 453-454, their last ping
  naming the dead `#606`, 34 long, 25 rounds old. Same game, round 401: the first feeder dies four steps from a
  9-long with a ping naming `#499`, 15 long, which is 2 long. 1045374 (weakhold, against WHQ), rounds 406-499: 21 of
  28 deaths by choice next to no bigger dragon; level at round 450 (24 to 25), lost 25 to 31.
- Shown. 1023828 (Maze, against forgot, won 92 to 84 with less potential): `#265` keeps its id from round 325 to
  489; 67-88% of our dragons name it at rounds 325-400; all 30 feeders that die next to a bigger dragon in rounds
  400-449 die next to it; 25 to 77 in 50 rounds. 1046530 (SSS against test4): `#770` one id from round 346 to the
  end, 48 of 51 deaths by choice next to it, 53 of 62 pearls eaten by it. 1044512 (WHQ against us): `#302` one id
  from round 351 to 431, 44 of 60 deaths by choice next to it.

**The earlier trials** (`work/plan.md`; section 5g). None tried this. The team wrote the diagnosis twice ("belief
goes stale"; "feeds to a non-top believed leader: 24/37, 18/25, 29/42"; next step "refuse to feed a leader much
shorter than the max leader length ever heard") and then tested clocks: feeding from round 330 or 300 (70 and 69 of
152 locally against 76; online 24 of 60 against 23), `FEED_EARLY_ROUND` (73, 74), `FEED_LOCAL` (dying next to any
visible dragon twice as long: 70, 74, 69 of 152 against 76), the leader round at 200 (19 of 60 online against 23).
`FEED_LOCAL` is the nearest relative of this candidate's second half and came out flat to slightly negative
locally; it differs in the point that matters (any big dragon, not the leader), and a local mirror on a rich board
is a weak judge of the last 100 rounds (the log: "top 39 at r400, total 220").

### 3. Mechanism

Under the longest rule the final length is potential times completeness. The rule adds nothing to potential. It
raises completeness in the phase in which our races are decided: each cut (2.7 a race from round 400) now costs 2
segments plus about 25 rounds in which the dragons that could feed the leader do not: in rounds 400-424 on small
maps 9.3 dragons are close and short enough and 5.2 pass the belief test; in rounds 450-474 4.1 and 1.5. With the
record following the heir those dragons die next to it instead of waiting or dying next to the stub; with the
"see it is long" test the quarter of deaths that now drop pearls next to nothing (13% to the leader) is spent next
to the leader (70%) or not spent. The pearls that reach the leader are worth one segment each; the same pearls
eaten by a small team-mate are worth half again later, if it ever feeds.

### 4. Expected effect

**(a) Games.** A record rule cannot be re-scored game by game from replays. Three counts bound it (`e_p.py`,
`e_margin.py`, `e_cutcost.py`; our 102 lost races, the enemy unchanged):

| what-if | lost races that turn | live bot (69 lost) | against test4 / WHQ / others (32 / 61 / 9 lost) |
|---|---|---|---|
| the leader's growth after round 400 times 1.25 / 1.5 / 2, never above 0.9 of our final potential, only races with a cut after round 395 | 6 / 12 / 18 | 5 / 10 / 14 | 2, 3, 5 / 3, 7, 11 / 1, 2, 2 |
| our final longest +5 / +10 / +15 segments | 4 / 11 / 20 | | |
| for scale, not this rule's effect: the segments left in the lineage's own cuts from round 400 given back | 10 | 9 | 6 / 4 / 0 |

The measured contrast is a factor 2.2 between windows with and without a cut, and three quarters of our windows
after round 400 are "with a cut" (291 of 382). I take a quarter to a half more growth as the strict range, because
feeders are finite and part of the contrast is selection: **strict 6 to 12 games of 401 (5 to 10 of the live bot's
275)**. Realistic: between half of the low end and three quarters of the high end survive a real opponent and the
cases in which the feeders were missing for other reasons: **3 to 9 games; +0.7 to +2.2 points on our 27.9%, most
likely a little over +1** (live bot: 2.5 to 7.5 games, +0.9 to +2.7 on 28.0%). It cannot be much more: 106 of our
143 races start under 0.8 of the enemy's potential and are mostly lost before the leader matters.

**(b) Where it acts.** Round-500 games with both queens dead (143 of 401), from the first cut after feeding starts:
the last 100 rounds on small maps, the last 300 on big maps when the 56-unit rule fires. Nothing changes before
feeding, in wipe-outs, or while a queen is fed (her id never changes hands by a cut with a free cell, and her record
carries the 1,000 bonus).

**(c) Against each opponent.** The window contrast and the belief contrast hold against test4, against WHQ and
against everybody else separately (table above). The what-if turns 2-5 of 32 lost races against test4 and 3-11 of
61 against WHQ. At level potential at round 350 we win 4 of 9 against test4 and 6 of 12 against WHQ today (SSS 7 of
9 against test4); counts this small have an 80% range of about plus or minus 20 points.

**(d) With the four existing candidates.**

- **Candidate 1 (take the queen)** makes more races: a dead enemy queen with ours dead too is a longest-dragon game.
  Sub-session B scored those new races with our present win rates per band. This rule raises those rates, so the two
  multiply rather than overlap; candidate 1 stays first.
- **Candidate 2 (our queen is never spent)** makes fewer races and more queen games. No shared code. The queen is
  already exempt from the early cut (`is_queen() && !no_move` in `escape_child_size()`), which is the reason her
  feeding does not show this problem.
- **Candidate 3 (no leader before its time)** moves the big-map switch from round 150 to 300. This read supports it
  from the other side: the zone gives the leader nothing on either map class (12% of the pearls left for it on small
  maps, 7-17% on big ones; the leader's natural intake does not rise at the switch), while the team's intake falls
  by a quarter and a third. And it answers the red team's worry that our big-map wins, all won on the longest
  dragon, might need the early leader: in the four read (section 4, games 19-22) the leader was built by feeding
  from round 201-204 with 56-60 units (three games) or after round 400 (one), not by the zone; in the median big-map
  race our longest is 10 at round 200 and 14 at round 400. One condition, which B already named: when the switch
  moves to 300 the 56-unit feeding rule must still give the fed dragon the leader's no-split rule, or the team
  feeds a dragon that splits. The two candidates touch different lines and can ride together; I would still test
  them one at a time.
- **Candidate 4 (do not give way at contact)** is independent. It leaves fewer units late, and small teams complete
  better (0.75-0.83 of potential in the longest with under 20 units at round 400 against 0.56-0.60 with 30 or more,
  small maps).

### 5. What changes in `mybot2/main.cpp`

No toggle exists for any of it. Three places, all in the leader record and the feeder test:

1. **`hear_exact()` (and the comparison in `hear_sighting()`): age counts.** When a report about another id is
   compared with the record, the record's length is reduced by a constant per round of age difference, for instance
   `mine = leader_priority(known_leader_id, known_leader_len) - LEADER_AGE_COST * max(0, when - known_leader_round)`
   with `LEADER_AGE_COST` about 0.5: an heir that is 2 shorter is taken four rounds after the cut instead of 25,
   and a living leader, whose own pings keep its record fresh around it, is not displaced. New constant; one line in
   each function.
2. **`hear_sighting()`: seeing the whole dragon corrects the record.** When the id in the record is in view with
   fewer segments than recorded and its whole body is inside the view (a helper: every visible segment's follower is
   visible or it is the tail, as `extend_trail_from_vision()` does for the own body), set `known_leader_len =
   visible` and `known_leader_round = round`. The corrected record then spreads by the existing same-id branch of
   `hear_exact()`. To stop the old report coming back from a dragon that has not heard, keep the id and round of the
   last correction (two ints) and ignore older reports of that id.
3. **`ready_to_die()` / `beside_visible_leader()`: the feeder must see length.** Next to `leader_in_vision()` add
   `visible_parts(known_leader_id) >= min(FEED_LEN_RATIO * length, FEED_SEE_MIN)` with `FEED_SEE_MIN` about 6: a
   2-3-long feeder must count 4-6 segments of the dragon it dies for. A stub fails, a real leader three cells away
   does not. `feed_len_ok()` stays as it is (the queen bonus path included).

Not part of the candidate, listed because the same read gives each a number (each would need its own test, and the
first depends on the candidate: a dragon cannot merge into a leader it does not know):

- **Whole dragons feed the leader at the end** (`FEED_LEN_RATIO` 2 -> 1 from some late round on, for dragons that
  can reach it in time). This is the one thing test4 and WHQ do in the race that we do not: 26-29 pearls a race from
  dragons of 5+ on small maps against our 5-9; 1.3-1.5 dragons of 8+ given to the leader in the last 50 rounds
  against our 0.3; their final lineage eats 57-64% of those pearls (section 2, `e_merge.py`). The winner did it in 5
  of the 14 losses read. Under the longest rule it always pays if the pearls are eaten (L1 + half of L2 is more
  than L1); what it costs is the second dragon as a reserve if the leader is rammed afterwards (3.8 times per 1,000
  rounds for a leader of 15-24 after round 400). In 38 of our 102 lost races our longest plus half of all the rest
  beats the enemy's longest; +5 / +10 segments turn 4 / 11. The top three do not do this on small maps (0.2-0.6 a
  race), so it is a rule read off our opponents, not off the protagonists.
- `LEADER_PEARL_RADIUS` 9 -> 0 (no pearl zone on any map): the leader loses about one pearl per 50 rounds, the team
  gains 5 (small maps) to 27 (big) per 50 rounds; three of the 14 losses read (weakhold) are zone starvation.
- `FEEDER_DIE_DIST` 3 -> 1 or 2: the dragon fed eats 90% of the pearls dropped one step away, 78% at two, 74% at three.
- `RALLY_FRESH` 0 -> 15-25: dragons beyond 15 cells never come; our level losers end with 12.5 units, the winners 5.

### 6. What would show it is wrong

Countable on 20-60 new replays (about a third are races) with the scripts named; today's value -> what the rule
must reach:

1. Growth of the longest per 25-round window from round 400, windows with a leader cut against windows without
   (`e_churn.py`): 5.0 against 10.8 -> within 2 of each other. **If the two stay apart, the record was not the
   cause and the rule is worth nothing.**
2. Deaths by choice in races, rounds 300-499, with no own dragon twice as long within 8 steps (`e_dist.py`): 26% on
   small maps, 20% on big -> under 12%. Next to the team's longest: 42% / 30% -> over 55% / 40%.
3. The final lineage's share of those pearls (`e_dist.py`): 36% (live bot, small maps) -> 45% or more.
4. Share of potential in the longest at the end, small maps (`e_cdist.py`): 0.65 -> 0.75; units at the end 7 -> 5 or
   fewer.
5. If the test build's pings can be read (they are sealed; the team has the key, or the bot can log its record):
   rounds until half the team names the new longest after a cut (`e_bel.py`): 27 -> under 8; samples in rounds
   400-494 with under a quarter naming the true longest: 54% -> under 20%.
6. Must not get worse: deaths by choice next to another dragon twice as long that is not the longest (16% small,
   36-41% big; this is where an age cost that is too high would show, as regional leaders); the longest of 15+ rammed
   per 1,000 rounds (3.8-4.6 after round 300); the enemy's share of our feeders' pearls (4.7% small, 10.5% big).

A win test is out of reach: +1.5 points on 27.9% needs about 14,000 games a side for four chances in five (+1
point: 32,000); inside races alone (29% to 34%) about 1,300 races a side, which is some 3,800 games.

### 7. Known risks

- **The comparison with other teams does not carry it.** Per pearl we convert as well as test4 and WHQ today; the
  gain is inferred from contrasts inside our own games (windows with and without a cut, samples with and without a
  shared belief). Those are correlations: a leader cuts when it is crowded, and a crowd may fail to feed for other
  reasons. SSS shows the same halving around a cut and wins 58% of its races.
- **The belief numbers are from 78 games of the earlier live bot**, the only ones whose pings can be read. The
  record code in today's source is as described and the window contrast is in every later live run, but nobody has
  seen a belief in a later build.
- **The test builds do not show the contrast on small maps** (9.9 with a cut in 42 windows, 9.7 without in 13) and
  end at 0.71 of potential where the live bot ends at 0.65. Small counts; if it is real, part of the gain is already
  there.
- **An age cost can split the team**: far dragons hold old news of the true leader and would switch to a shorter
  dragon nearby. The team has seen that failure ("regions elect local leaders"). Number 6 above watches it; the
  constant is the knob.
- **Fewer blind deaths are fewer deaths.** A dragon that no longer dies next to nothing is still alive at round
  500 unless it finds the leader, and we do not bring far dragons in (`RALLY_FRESH 0`).
- **The ceiling.** 48 of our 143 races start under half the enemy's potential (none won) and 58 at 0.5-0.8 (20 won,
  the same rate as the top three from there). A race rule works on what is left.
- **Counts.** The level bands hold 9 to 24 of our games; winners against losers 12 a side. 313 of our 401 games are
  against two opponents; what is said above holds against each, with fewer games each.
- **Big maps.** Everybody ends there with 39-49% of potential in the longest and several leaders; our leader is
  rammed in one race in two. The rule acts longer there (feeding from round 200) but on a mechanism that is
  scattered for every team.

## 8. Where `findings.md`, `hypotheses.md`, `redteam.md` or the earlier deep reads look wrong or thin

1. **The footing of the race gap (`redteam.md` section 1; repeated in my brief).** "At equal economy the gap stays on
   small maps: with own / enemy total length at round 400 between 0.8 and 1.25 we win 9 of 30, the top three 22 of
   40." Total length at round 400 is not the economy once somebody has fed: a 2-long feeder leaves 1. In those 30
   games of ours the enemy had 90.5 against our 65.5 at round 300 (potential 54 against 39.5) and had caught down to
   us by converting; in 17 of the 30 the enemy had over 1.25 times our total at round 300. In the top three's 40
   games the top team was ahead at round 300 (101 against 94). On potential, which feeding does not change, we win
   11 of 23 level races at round 300 and 12 of 24 at round 350. The sentence "the largest countable gap that no
   candidate works on is the longest-dragon race" should read: the race is where the economy gap is paid; a gap of
   its own is small (our rate at level potential is about 50%, the top three's 58-59%; against test4 and WHQ only, 10
   of 21 against 11 of 13).
2. **"After round 400 both grow by about 20" (`hypotheses.md`, "Not proposed").** The others do (15.5-26 in the
   median race); our live bot's longest grows 10 on small maps and 14 on big ones, the test builds' 21 and 9.5. And
   "it has been tried directly" covers only the clock (rounds 330 and 300); what breaks after the clock starts was
   not tried. B's ceiling for the whole race gap (+6.9 wins of 268 games on the total-length bands) agrees with mine
   on potential (+4 to +9.5 of 401), so dropping it then was fair.
3. **"Our late feeding often feeds the opponent" (`findings.md` section 7, the team's note).** On the same count for
   every team the enemy eats 4.7% of the pearls of our deaths by choice on small maps and 10.5% on big ones (others
   0.6-2.4% and 1.8-6.0%). It is two to eight times the others' share and still one pearl in ten at most; seven times
   as many of our pearls go to another small dragon of ours. It happens when an enemy head is within 8 cells of the
   dying feeder (15% within 4 cells, 8% at 5-8), and our rule asks only for more than 4.
4. **"Top teams ... feed from about round 300" (`findings.md` section 7).** SSS and WHQ do, and forgot with a full
   team. Vibing++, rank 1, starts at round 360 with a full team and at 370-400 otherwise, and test4 waits for its
   queen to die. The start does not sort the teams by strength.
5. **"About 2.6 segments spent per segment it gains" (`deep-read-2.md`).** That is the gain of the dragon fed at the
   moment. Followed to the end of the game, the dragon that wins the race gains one segment per 3.4-4.3 spent on
   small maps (0.23-0.29 per feeder segment) and one per 5-11 on big maps (0.09-0.19): of the pearls dropped, the
   final longest's lineage eats 36-47% on small maps and 15-31% on big ones, for every team; the rest goes to
   dragons that do not end as the longest.
6. **"forgot starts at about round 200-225, SSS at about 200-300" (`deep-read-2.md`, as quoted in my brief).** For a
   leader that is not the queen: forgot at round 300 with 56 or more units and about 370 otherwise (median 359 over
   309 games), SSS at 301 (221-302 only with a full team, on big ground). The earlier rounds are queen feeding.
7. **Candidate 3's open risk (`hypotheses.md`): "all our wins on these maps are longest-dragon wins, so an earlier
   leader may be part of some of them."** It is not the zone that builds the big-map leader. After the switch the
   leader of the time eats 1.6-3.4 natural pearls per 50 rounds, fewer than before it (4.0); of the pearls our small
   dragons leave in the zone the leader gets 7-17%; our longest is 10 at round 200 and 14 at round 400. What builds
   it in the four wins read is feeding from round 201-204 with 56-60 units, and the leader's not splitting. So
   candidate 3 keeps those wins if the fed dragon still stops splitting once feeding starts (B's own caveat).
8. **The pearl rate after the switch, "56% instead of 80%" (`findings.md` 6c, `hypotheses.md` candidate 3).** It is
   a mixture. By the dragon's own belief (readable games) it takes a pearl inside its believed leader's zone in
   18-26% of turns and outside it in 75-87%. B's "slope with distance, not a step at 9 cells" is the remembered
   position: B inferred it, the pings show it.
9. **"None of the test builds changed the leader or feeding rules" (my brief).** True of the rules as far as the log
   says, but the test builds end small-map races at 0.71 of potential against the live bot's 0.65, grow 21 against
   10 after round 400, and do not show the cut contrast there (9.9 and 9.7; 42 and 13 windows). Either 25 races are
   too few, or a movement change (their leader takes 65-79 steps per 25 rounds against 53-59) matters to the race.
   Nobody has compared the builds' races; I only counted them.
10. **The list of 14 "losses with at least level total length at round 400" (`x_out/race.txt`).** A good reading
    list, a bad sample: by potential the enemy was clearly ahead at round 300 in four of them (1045202 43:58,
    1058858 31:53, 1063682 29:55, 1027971 29:42) and we were clearly ahead in three (the weakhold games, 39:22,
    54:24, 41:23). Seven of the 14 were lost after being level or ahead in the longest dragon after round 425; the
    other seven were not conversion losses in that sense.
11. **Cards #14 and #22.** `findings.md` lists them as known to the team; `work/plan.md` has no entry for either
    (it ends on 2 October with v61). Whatever "late feeding (card #22)" tested is not in anything I could read.
12. **Thin in every earlier file, including the brief:** a team's own second and third dragons. The team's log
    notes that the top teams "often keep a big 2nd dragon too"; nobody counted what happens to it. On small maps
    test4 and WHQ feed it to the leader late (1.3-1.5 dragons of 8+ a race in the last 50 rounds) and the top three
    mostly do not (0.2-0.6); on big maps everybody ends with several (second / longest 0.45-0.72).

## 9. Things I could not determine from replays

- **What any other bot knows.** A replay shows that forgot, WHQ and Vibing++ keep feeding around a cut and that
  SSS does not; it does not show whether they follow a record, a sighting or nothing at all (SSS's feeders die one
  step from the head, which needs no memory). The same for their clock: unit count or map size give the same table.
- **Our own dragons' beliefs after the "stride" run.** Later builds seal the ping. The key is in the bot source; I
  did not copy it here. Everything said about belief rests on 78 games of the earlier live bot (56 on small maps),
  plus the reading of today's source, in which the record code is as described.
- **Which rule made a given cut.** A replay gives the free cells, the room ahead and the distance of the nearest
  enemy head at a cut; it does not say whether the bot cut because of a pocket (`escape_child_size()`), because it
  was in an enemy's reach (the `cornered` split) or while harvesting. Nor what would have happened without the cut.
- **Why a given feeder died where it did**, in the sealed games: the record it held is not visible. In the readable
  games only its last ping is, one turn old.
- **Whether WHQ's big dragons that die by the suicide order are a rule or an accident.** 312 dragons of 15+ in 159
  games, 11 of them the team's longest at that moment (the 65-long of game 20, the 18-long of game 2), no time-out
  flag on any but 5. Most are eaten by a team-mate; some are not (the 70-long of game 14).
- **Whether the test builds really convert better on small maps** (0.71 against 0.65, no cut contrast) or 25 races
  happen to say so, and if it is real, which change did it.
- **What the earlier trials `rl1` (rally) and `eg1` (`ENDGAME_ROUND` 350 / 450) gave:** queued in the log, no result
  recorded. What cards #14 and #22 tested in detail: not in the log.
- **What the rule does to wins.** Nothing here was played. The size of candidate 5 is inferred from contrasts
  inside our own games, and the one comparison across teams that could have carried it (per-pearl conversion) shows
  no gap to our opponents.
- **The cost of an age rule for the record on big maps**, where news of the true leader is old for most of the team:
  whether far dragons would switch to regional leaders more than they already do (36-41% of our deaths by choice
  there are next to a bigger dragon that is not the longest). Only a played test can say.
- **What a dragon would have done had it not died for a stub**: walked to the true leader, or stood still. The
  count of "dragons that could feed without the belief test" (9.3 against 5.2 in rounds 400-424) is geometry, not
  behaviour.
- **Terrain beyond closed and open.** Completeness by map (Portals 0.85 to Around UNSW 0.35) and cuts by map are
  measured on 15 maps; which property of the ground drives them (corridor width, the size of the home region,
  portals between regions) I did not separate, and the qualifier maps are new.
- **Pearl spawn intervals**, hidden in the replay: whether a pearl left lying in the zone cost the tile a spawn is
  inferred from the rule ("a pearl appears only on an empty tile"), not seen.
