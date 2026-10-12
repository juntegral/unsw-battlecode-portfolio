## Candidate 3: no leader before its time

**The claim (B's):** the "leader rules" (small dragons leave pearls near the longest own dragon they know of; dragons
longer than 4 stop splitting) start at round 300 on every map, instead of round 150 on maps over 1,200 cells. One
constant. B: +0.4 to +1.5 points.

**The strongest argument against it, as its opponent would put it.** "Every one of the twelve games we have won on
these maps was won on the longest dragon, and in ten of them the enemy had more total length than we did at round
300. The dragon that won them grew from 7 segments at round 150 to 24 at round 300; that is the window this
candidate gives back to the small dragons. On the maps where the same rules already start at round 300 our longest
dragon is 4 long at round 300, and there we lose level games that the top three win. The gain is inferred: nobody has
seen our bot play rounds 150 to 300 on a big map without the switch against a ladder opponent, three local runs of
exactly this change were flat, and where the same games can be followed through the switch a full team of ours still
grows 13% under it while the collapse is in games that were lost by round 150."

What is left: the behaviour claim is right to the turn. The economy claim is plausible for half of the games. The
win claim leaves out what the switch buys, and with that put back in I cannot tell its sign: **between -1.2 and +1.3
points, most likely near zero or slightly above.** It is not the candidate that "could most safely ride along".

### A. The counts

`x_c34.py` walks all 2,478 replays; tables `x_c3a.py` (`x_out/c3a.txt`). The turn counted is B's: a non-queen dragon
of 2 to 4 moves, no enemy head is in its view, and a pearl lies on a free next cell that has a further free
neighbour. Share of such turns on which its first step takes the pearl:

| Maps over 1,200 cells | B: meow live | mine: meow live | mine: our opponents | Vibing++ | SSS | forgot |
|---|---|---|---|---|---|---|
| rounds 0-149 | 83% of 16,079 | 83% of 16,079 | 85% | 89% | 80% | 94% |
| rounds 150-399 | 58% of 18,312 | 58% of 18,312 (59% to round 299, 57% after) | 85% | 86% | 83% | 93% |
| ... the pearl is 0-3 / 4-6 / 7-9 / 10-12 / 13-16 / 17+ cells from the nearest longer own dragon | 50 / 51 / 57 / 65 / 69 / 72% | 51 / 52 / 61 / 70 / 73 / 76% | 82 to 89% | | | |
| ... own length 2 / 3 / 4 | 54 / 57 / 88% | 54 / 57 / 88% | 84 / 83 / 86% | | | |
| in 10-round blocks: rounds 130-139, 140-149, 150-159, 160-169, 170-179 | | 84, 84, **64, 60, 58%** | 86, 86, 85, 85, 84% | top three 90, 89, 89, 89, 89% | | |

| Maps of 1,200 cells or fewer | B: meow live | mine: meow live | our opponents | top three |
|---|---|---|---|---|
| rounds 0-299 | 88% of 28,107 | 88% of 28,107 | 84% | 89% |
| rounds 300-399 | 53% of 8,202 | 53% of 8,202 | 78% | 87% |
| in 10-round blocks: rounds 280-289, 290-299, 300-309, 310-319 | | 85, 83, **64, 51%** | 81, 81, 82, 80% | 88, 88, 88, 88% |

The same turn counts as B's, to the unit. **The fall is real, it comes in the ten rounds after our own switch on
both kinds of map, and nobody else has it.** Units, total length and longest dragon also reproduce (live bot, big
maps, round 150 to 300: 47.2 to 35.9 units, 123 to 122 total, 5.8 to 14.2 longest; top three 55.6 to 58.8, 165 to
206, 8.6 to 18.4).

By eye (`x_pick34.py`, `x_out/c3_eye.txt`): 18 declined pearls after the switch, drawn at the dragon's own turn. In
all 18 a pearl lies on a free next cell with no enemy head in the 7x7 square and the 2-3-long steps elsewhere; in
14 a longer own dragon is within 9 cells of the pearl (a 19-long one cell away in 1063016 round 257; a 4-long two
cells away in 1052760 round 193), in 4 the nearest longer own dragon is 10 to 42 cells away (1045376 round 151: 42
cells). So the zone explains most of it and not all, as B says.

### B. Cause or consequence

Is the fall the switch, or the state of the game at that point? The switch (`x_c3a.py` part 2). After it the rate
is 60% in the games we won and 58% in the games we lost (big maps), 56% and 52% on the others; it is between 48
and 62% in every economy band that holds more than one game. And the same bot on the smaller maps keeps eating at 86% through rounds 150 to 299. B's reading
holds.

### C. What happens next: what the switch costs, and what it buys

**What it costs is less clear than B's table suggests.** B infers +12 to +24% total length at round 300 from two
comparisons. Following the same games through the switch (`x_c3stall.py`, `x_out/c3stall.txt`):

| Live bot, maps over 1,200 cells, games that reach round 300 | units at 150 / 200 / 300 (the enemy's) | total length at 150 / 200 / 300 (the enemy's) | longest at 150 / 300 |
|---|---|---|---|
| 56 or more units at round 150 (36 games) | 60 / 58 / 53 (59 / 61 / 61) | 164 / 178 / 185 (205 / 237 / 285) | 7 / 20 |
| fewer (39 games) | 37 / 28 / 20 (62 / 62 / 62) | 91 / 75 / 63 (209 / 282 / 365) | 4 / 9 |
| top three, all their big-map games | 56 / 58 / 59 | 165 / 185 / 207 | 9 / 19 |

"Our total length stands still from round 150 to 300" is the average of two different things. With a full team we
still grow 13% under the leader rules (the top three 25%, our opponents in those games 39%); with 37 units against
62 we are being overrun and lose a third of our length whatever the small dragons eat. For the first half B's +12
to +24% is possible; for the second I see no reason to expect it.

A second check: on the smaller maps the same rules switch on at round 300 and our total length does not fall
afterwards (61, 61, 62 at rounds 300, 350, 400 on the same games; our opponents 99, 99, 95; `x_c3stall.py`). And B's premise that
before the switch we grow "half as fast as the others" on those maps (+20% against +41% and +47%) comes from means
over different sets of games at each round; on the same games it is +24% against +29% and +27%.

**What it buys is the dragon our big-map wins are won with** (`x_c3wins.py`, `x_race2.py`; outputs
`x_out/c3wins.txt`, `x_out/race2.txt`). Our 12 wins on these maps, medians, ours against the enemy's:

| Round | units | total length | longest dragon | wins in which ours is the longer |
|---|---|---|---|---|
| 150 | 60 : 62 | 163 : 227 | 7 : 12 | 3 |
| 200 | 59 : 62 | 177 : 260 | 13 : 15 | 5 |
| 300 | 55 : 62 | 207 : 302 | 24 : 20 | 7 |
| 400 | 56 : 54 | 215 : 270 | 27 : 27 | 5 |
| end | | | 69 : 39 | 12 |

All 12 are round-500 games with both queens dead. In 10 of the 12 the enemy had more total length at round 300.
B's sentence "our wins there are the games in which the economy held, not games in which an early leader was built
at its cost" is half of it: they are games in which we kept 55 to 60 units, and in which a leader built from round
150 on was level with or ahead of the enemy's by round 300 although the enemy had half as much length again.

How much of those wins is the early leader? Two readings.

- **By the margins.** The 12 were won by 1, 2, 11, 19, 20, 23, 41, 41, 42, 47, 53 and 62 segments. Most of the
  final length is fed in after round 400 (27 to 69 in the last hundred rounds, from 55 own units). A leader 6
  segments shorter at round 300 costs the two closest wins, 15 shorter costs three. In 9 of the 12 we also had 56
  units at round 200, so the early-feeding rule (`FEED_CAP_ROUND 200`, 56 units) was feeding that leader from round
  200; B's change list moves that rule to round 300 as well, or ties the leader rules to it, and the two options
  differ by exactly this.
- **By fit** (`x_race3.py`, `x_out/race3.txt`). A fit of win on the two ratios (total length, longest dragon) over
  our 65 both-dead big-map games gives the longest dragon a weight; the same fit over every team in the data gives it
  none at round 300 and a small one at round 400. Priced on our 65 games: total length +15% with the leader as it is
  now, +2 to +3 wins; with the leader halfway to what it is on the smaller maps, 0 to +2; with the leader as short
  as there, **-5 to +2**. For +25%: +3 to +5, +1 to +4, -4 to +4.

B's +1.8 to +6.0 wins is the first of those three cases: it re-scores the games with "our own win rate for the band
they land in", and those rates were earned with the leader the switch builds.

**The reverse experiment is already in our games.** On maps of 1,200 cells or fewer the rules start at round 300,
which is what this candidate asks for everywhere. There, in round-500 games with both queens dead and total length
level at round 400, we win 9 of 30 and the top three 22 of 40; our longest dragon is 5, 12 and 28 long at rounds
300, 400 and the end, the enemy's 7, 16 and 39. On the big maps at level length we won 4 of 6 with a leader of 27,
46 and 58. Small numbers, different maps; but it is the only place where the proposed setting can be seen at work,
and it does not look like the better one for the end game.

### D. Sample size

- The behaviour: 16,000 to 28,000 turns a cell. Not in doubt.
- The games: 111 big-map games (77 live), 12 wins (9 live). Any statement about wins on these maps rests on 12
  games, B's and mine alike. Six of the 12 wins are on Around UNSW, five on Slithery Fight, one on Australia.
- It acts on 5 of the 15 known maps. What share of the qualifier's maps is over 1,200 cells is not known.
- By opponent the fall is the same (it is our own clock).

### E. Cross-team

Nobody else stops eating. But the three top teams also end up with a leader: 9 to 19 between rounds 150 and 300 on
big maps, with 59 units and total length up 25%. They get both; we get the leader and lose the growth. So the lesson
from them is not "no leader until round 300" but "a leader that does not cost the small dragons their pearls".
forgot is the cleanest case: its small dragons eat 93 to 94% of such pearls in every phase and its longest dragon is
still 18 long at round 300.

### F. Earlier experiments

- The same change ("GB300"), three local runs: 30 wins of 64 against 20 on one big map on a build with a known bug;
  46 of 96 against 48, with the one big map in the set at +2 -5; 73 of 152 against 76. Flat.
- The switch at round 200 on every map ("LC200", later on big maps, earlier on small): 52 of 96 against 48 locally,
  then 19 of 60 online against dev test 1 where the base had 23 and the feed-earlier build 24. Inside the noise,
  on the old map pool. The team's note then: an early leader is "easy to snipe on open maps"; it rejected the early
  leader on small maps and kept round 150 on big ones.
- Card #14 (a unit count instead of the round for the split stop): no local change.
- Do they contradict the candidate? No. Do they support it? No. Local games between two copies of our bot cannot
  show a rule whose cost is paid to an opponent that eats what we leave.

### G. Backfire

Counted above: 2 or 3 of our 12 big-map wins sit within the margin the leader could lose; with B's first option for
the early-feeding rule (move it to round 300) all 9 wins that had 56 units at round 200 lose a hundred rounds of
feeding. Against that, the 53 big-map losses with both queens dead were lost by a median of 48 segments (26 against
74), so a little more economy does not turn many of them.

### H. The code claim

Read: the constructor, `is_leader()`, `refresh_leader_zone()`, `in_leader_pearl_zone()`, `score_step()`,
`survey_from()`, `split_child_size()`, `feeding_phase()`, `hear_exact()`, `hear_sighting()`.

- B's description is right. `grow_round` is 300 on maps of 1,200 cells or fewer and 150 above, `LC_LEAD_ROUND`
  overrides it, and it is read in the three places named. After it, a pearl within 9 cells (Manhattan) of the
  longest own dragon a dragon knows of loses `EAT_BONUS`, costs `ZONE_PEARL_PENALTY 600` and is not a target; any
  dragon longer than 4 stops splitting; a dragon that knows no longer one is "leader" and stops trading and
  harvesting.
- "The longest own dragon it knows of" can be one segment longer than itself, which is why 2-longs and 3-longs stop
  eating next to 3- and 4-longs (54% with a 3-4-long as the nearest longer dragon). That is the part of the rule
  that looks like a bug, and it could be fixed without moving the round: a leader zone only around a dragon of, say,
  8 or more. I did not count what that would do.
- The `FEED_CAP_ROUND` point is real, and it matters more than B's one sentence gives it (item C).
- No map name is left in it. After the change `grow_round` has no map-size condition.

### What is left of the claim

| | B | after the attacks |
|---|---|---|
| the behaviour | 83% to 58% at our switch, nobody else | the same, to the turn |
| total length at round 300 on big maps | +12 to +24% (inferred) | possible in the half of the games in which we have a full team; unknown in the other half |
| wins | +1.8 to +6.0 of 401 | -5 to +5: the low half if the later leader loses the longest-dragon race it now wins |
| points | +0.4 to +1.5 | **-1.2 to +1.3; cannot be told** |
| "the one that could most safely ride along with another card" | | no: it is the one candidate whose sign I cannot give |
