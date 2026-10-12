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
