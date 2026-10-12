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
