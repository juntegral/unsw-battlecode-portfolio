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
