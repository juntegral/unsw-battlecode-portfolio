## What I would change, and what would show it is wrong (question h)

Neither rule names a map or a map size. Both are about behaviour that all three top teams and both of our usual opponents share
and that we alone do not have. One part of the opening rule has already been on the ladder (the trade-on-contact test build);
its numbers are in answer e and are used below as evidence for and against.

### Opening: a small dragon does not give way to an enemy small dragon that is not shorter than itself

In words, three parts:

1. A dragon of 4 or shorter whose turn begins with an enemy head on the next cell rams it when the enemy is at least as long.
   Today (live bot, maps over 1,200 cells) the target must show max(5, own length + 2) segments.
2. It does the same from two or three cells away when it can reach that head in this turn (a charge), and it does it alone.
   Today a target is marked only if the dragon sees at least as many other own heads as enemy heads and the team has 8 units.
3. Cells next to the head of an enemy that is not shorter are not treated as dangerous when choosing where to step or which
   pearl to go for. Today every cell next to a small enemy head carries a penalty, and a pearl is a target only if we reach it
   before any enemy head (within one step for dragons of 4 or shorter).

Part 1 is the test build. What its 12 large-map games say (answer e):
- It works as a rule: 31% of meetings end in a ram (live bot 10%, opponents 30-37%, top three 36-42%).
- It pays in units and length: 52 units against 58 at round 150 where the live bot has 46 against 61; total length 143 against
  191 where the live bot has 121 against 212; at round 300, 42 units and total 147 where the live bot has 35 and 118. On
  Australia and Islands the opening is no longer lost (total length at round 150: 132 against 140 and 123 against 149).
- It does not do what the rule is for. The border stays where it was (57% of rams in our half; 76% of our heads at home; 57
  natural pearls from the enemy's fountains in rounds 0-149 against the opponents' 96 from ours), the opponents eat as much as
  before (335 natural pearls against 336), and it won 0 of 12.
- Why not more: it still suffers 63% of the rams, and two thirds of the rams it suffers are charges. It charges 3.9 times a
  game in rounds 0-149; test4 and WHQ 13.7 times, forgot 8.7, SSS 10.2, Vibing++ 12.9. A dragon that only fights when the
  enemy has walked up to it fights on the enemy's terms and at home.
- The test's own verdict was counted in wins over 30 games (6 against a pooled 9.2, `data/online/smoke/tc30-test-result.txt`).
  Twenty of those 30 games are on maps of 1,200 cells or fewer, where the test build is the live bot, and on the large maps
  our base rate is 12 wins in 99: no count of wins in 8 or 10 games can see this rule. The counts that can, moved.

What supports parts 2 and 3, which have not been on the ladder:
- 69.7 meetings a game on large maps, and beyond them 8.7-13.7 charges a game by everybody but us (`c_ramsteps.py`).
- The side that starts a ram eats 61-78% of the pearls of both corpses (the test build: 65% at meetings, 52% over all rams it
  starts). Stepping away costs 0.37 pearls in the next ten rounds against the enemy that stays, and one in five of the dragons
  that step away is rammed in those ten rounds anyway.
- With an enemy head in view our dragons end the turn farther from it in 34-37% of turns and nearer in 12-13%; everyone else
  22-29% and 15-22%. 76% of our heads are at home in rounds 50-99 against 68-72%, and the fountains of our half feed the
  enemy: 76 pearls in rounds 50-149 against 34 the other way, a third of the whole pearl gap of those rounds. The test build
  left this as it was, which says it is not the ram at a meeting that keeps our dragons at home.
- The exchange as it is now moves about 110 segments a game to the enemy on large maps and 21 on medium ones; test4 and WHQ gain
  68 and 148 from it against us and lose 3 and 9 against the top three, who ram back (`c_rams.py`).

What would show it is wrong (on the ladder against test4 and WHQ, large maps, against the test build's numbers as the base;
local games against our own bots cannot show it, because two teams that both step away never meet like this):
- Charges stay under 6 a game in rounds 0-149 or the share of rams we start stays under 40% (test build: 3.9 and 37%). Then
  the head count and the unit minimum were not what held the dragons back, and part 2 is not built yet.
- We start 45% or more of the rams and still eat under 35% of the ram pearls (test build 33%, top three 47-50%). Then the
  pearls are lost for another reason (who stands behind the rammer) and the trades only cost us dragons.
- Natural pearls from the enemy's fountains in rounds 0-149 stay under 65 (live 49, test build 57, top three 81-86), or the
  share of rams in our half stays at 57-58%. Then part 3 does not move the border and the rule fails at what it is for.
- Units at round 100 fall below the live bot's 42 (test build 45). We make fewer new dragons per pearl than they do (4.1
  pearls eaten per split at 4 against 3.3 in rounds 0-99; answer b, point 4), so an even trade may cost us more than it costs
  them.
- More games lost by wipe-out (today 103 of our 427 games against 2000+ teams, Schooltime included; `findings.md`).
Limits. The queen is excluded. Local numbers matter for everybody: a top-three rammer's team eats 31-34% of the pearls when
the enemy has three or more heads more within 8 steps and 87-89% when it has three or more itself (we 16% and 75%), so "charge
only when not outnumbered by three" is a refinement to try second; A2 found that forgot holds back in that way before round
100 against the queen.

Not a general rule, but countable on one map type: **split as soon as a dragon is 4, also inside a dead end and while
"harvesting"** (the child is born at the tail, on the way the parent came in). Support: on Slithery Fight we shed 125 times a
game in rounds 0-99 and split at 4 only 65 times (our opponents 56 and 120); in the live game read we eat as many natural
pearls as WHQ there (456 against 447) and lose 272 dragons boxed against 205; SSS eats a quarter fewer pearls than we do,
loses 77 dragons boxed and has more total length at round 150 than we have (200 against 176). forgot and SSS split at 4 and
5 in the same corridors. On the other maps our sheds are no more than our opponents'. It would be wrong if the boxed deaths
on that map rose above today's 243 a game in rounds 0-150 without the units rising, or if the 2-long children were lost at
the corridor mouth (count deaths within 5 rounds of birth).

### Mid-game: no switch by the clock: until the team starts to feed one dragon, every dragon eats the pearl next to it and splits at 4

In words: drop the two things that change at `grow_round` (round 150 on large maps, 300 on the others): the reservation of pearls
within 9 cells of the leader for the leader, and the ban on growth splits of dragons longer than 4. If a switch is wanted, tie
it to the state the feeding phase already uses (the unit count, or the start of feeding), not to the round or the map.

This is the rule I would test first now, on top of the trade-on-contact build. That build shows the opening can be held on
the two maps where the live bot collapses, and that the games are then lost between round 150 and round 300.

What supports it:
- A small dragon with a free pearl next to its head eats it in 81-82% of turns before round 150 and 59-61% after; within 9
  cells of our longest dragon 44%. The opponents in our games: 81-85% all game; forgot 89-91%, SSS 70-80%, Vibing++ 83-89%.
  On medium and small maps the same drop comes at round 300. It is the same in both builds (82% to 59%, 83% to 62%).
- Ordinary splits fall from 32 to 15 per 50 rounds at round 150; the top three make 33-59 and keep 25-31 two-longs and 20-24
  three-to-four-longs until round 300; our 2-longs eat half as much as theirs per dragon-round after the switch (1.25 against
  2.5-3.3).
- The dragons the rule is meant to grow do not grow: our longest dragon at round 300 is 15 on large maps against 16-21 for the
  top three and 24 for our opponents (`findings.md`); the 5-9-longs shed two segments every 15 rounds and are rammed.
- In the test build's games with a won opening (1068050, 1068051: 60 units at round 150 against 33 and 39, total length 207
  against 84 and 170 against 91) the collapse begins in the 50 rounds after the switch and the total length is behind by
  round 249 and 213. Over the test build's three games each on Australia and Islands the units go from 47 at round 150 to 41
  and to 18 at round 300 while the opponents' go from 52 to 56 and from 55 to 58.

What would show it is wrong:
- The rate at which a small dragon eats a free pearl next to it stays under 75% in rounds 150-299 on large maps. Then the
  reservation was not the cause.
- Units at round 200 and 300 on large maps stay at 41 and 35 (48 and 42 on top of the test build), and natural pearls in
  rounds 150-200 at about 52 (`findings.md` section 2).
- The longest dragon at round 300 falls below 15, or our share of wins in games decided by the longest dragon falls below
  today's 29% (41 of 143, `findings.md` section 1). All 12 of our large-map wins are of that kind, so this is the number that
  could get worse.

### What this read says about the ideas already tried

| idea | tried | what the replays say |
|---|---|---|
| Trade on contact (`TRADE_CONTACT`, the tc30 test) | on the ladder, 30 games; counted as 6 wins against 9.2 | Supported as far as it goes, and it does not go far enough. On the large maps, the only ones it changes, it rams like everybody at a meeting and is 5 units and 20 segments better at round 150; it does not charge, does not move the border and won none of 12. The win count that judged it cannot see a rule that acts on 5 of 15 maps, on which we win one game in eight. |
| "Always trade evenly" (`TRADE_EVEN`) and the variants without the local head count | locally: no gain; without the local head count worse against a rushing copy of our bot | Not tested on the ladder. What the ladder shows is what keeping the head count leaves undone: the test build charges 3.9 times a game against 9-14 for everybody else and suffers two rams in three. A local opponent that steps away nine times in ten does not punish stepping away, so the local result says little about test4 and WHQ. |
| A stronger fear of small enemies (`SMALL_THREAT_MULT`) | locally neutral | Contradicted: we already give way far more than anyone (90% of meetings against 58-64%; farther from an enemy head in view in 34% of turns against 22-28%). |
| A relaxed contest for corpse pearls (`CORPSE_SLACK`) | locally no change (share 49-50%) | The ladder deficit is real and large (28% of ram pearls against 47-50% for the top three), and mostly not explained by being outnumbered. A mirror match is 50% by symmetry and cannot show it. |
| State-based split stop (card #14) | locally no change: our bot reaches 60 units either way | Supported: on the ladder we have 47 units at round 150 on large maps and 36-38 on Australia and Islands, so the round-150 stop bites there; the same switch also stops small dragons from eating, which the card did not touch. |
| Splitting while harvesting (`HARVEST_SPLIT`) | locally neutral | Supported for Slithery Fight only (125 sheds a game against 56); on the other maps our sheds are not more than our opponents'. |
| Far-pearl attraction (`FAR_GAIN 2`) | in the live bot | No evidence either way: with no pearl in view our dragons step onto new cells as often as our opponents' (19% against 17-18% of turns in rounds 50-99). |
| Stride (free sprint steps) | locally +14% economy, no more wins | Sprinting does not separate the teams: forgot makes 10 moves of two or more steps per 50 rounds in rounds 50-99 and eats the most of the three top teams in rounds 0-99; SSS and Vibing++ make 38-43, WHQ 40-87. |
| Queen never uses portals (`QUEEN_NO_PORTAL`) | in the live bot | No evidence in the games read. On Stripes, where I first blamed it, the queen rules are off (288 cells; they need more than 600 or a closed home) and the queen does go through the portal in 1068053; she is simply ten rounds later than forgot's. |
| Queen hunt (`QH_SCOUT`, the qh31 test) and "passage2" | on the ladder, 28 games each | Not economy rules; their large-map games look like the live bot's in every count of `c_out/bybatch_large.txt` (ram rate at meetings 10-11%, units at round 150 42-45 against 62-63). |
