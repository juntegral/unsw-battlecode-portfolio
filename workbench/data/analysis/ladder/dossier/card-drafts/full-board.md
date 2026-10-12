What we tried: Counted rounds 101 to 200 of the 161 ladder games on layouts above 1200 cells and read the three rules that switch on at round 151 there. On the layout we lose most (1 won of 24) our eating and splitting halve in that one round while the opponents' do not move.
Did it work: Not tested yet, this is a new idea. Card 49 touched two of the three rules and tied them to leader length; this one ties all three to how many dragons we have, and only above 1200 cells.
Who decides now: The loop builds and tests it now; one teammate's OK is needed only before it ships.

### Idea by
AI

### Area
economy

### Claim
Words: the leader rules are the three things that start when the round passes grow_round (150 above 1200 cells, 300 otherwise): a dragon longer than 4 stops splitting, the dragon that knows nobody longer becomes "leader" and stops splitting and trading, and every other dragon stops taking pearls within 9 tiles of that leader. "Skip" = a turn of a non-queen dragon that starts beside a pearl and eats nothing.

On a layout above 1200 cells, when the leader rules start while we hold fewer than 56 dragons, our dragons stop eating and splitting although the board is not full, and the team is no longer refilled as fast as it dies.

Proposal: one switch, LEADER_FULL_UNITS (0 = off, as now; first value 56, the value FEED_CAP_UNITS already uses). When it is above 0 and the layout is above 1200 cells (aggressive is false), the three tests on "round > grow_round" (split_child_size, refresh_leader_zone, is_leader) also need feeding_phase() or our dragon count at 56 or more, checked every turn. Layouts of 1200 cells or fewer are untouched. Feeding, the zone and the pocket rule themselves stay as they are. No map names and no per-map values.

### Evidence
Measured (ladder, live bot, 500 games; scripts and rows in unsw-swarm/data/analysis/ladder/dossier on jun's Mac; the starred rows were recounted a second time by a separate script):
- the layout we lose most, 24 games, per game, rounds 101-150 then 151-200: our splits 42.3 then 16.3 (theirs 59.1 then 54.7)*; our pearls 113.5 then 55.5 (theirs 191 then 200)*; our skip share with no enemy head within 2 tiles 0.30 then 0.53 (theirs 0.24 then 0.27)
- in the 23 of those games that reached round 175: our eating on fast-spawning tiles fell by a quarter or more in 21 (theirs in 1), our splits in 20 (theirs in 6)
- our deaths in rounds 101-150 there are 41.2 a game on a team of 40.5*, so a team that stops splitting empties: about 40 dragons at round 150, 16 at round 300, theirs 61
- all six layouts above 1200 cells: with 56 or more dragons on average in rounds 101-150 we won 40 of 77, with fewer 21 of 84*
- the same step shows at round 301 on two layouts under 1200 cells that we win (skip 0.20 then 0.49, and 0.05 then 0.25), which is why this card leaves those layouts alone

Read from the code (mybot2/main.cpp): grow_round at 467-468; the three tests at 1036, 2341 and 3329; the zone cost at 5055-5060; feeding_phase at 4919-4921.

Against it: 15 of the 24 games were already behind at round 150 and this cannot win those. The one win has the step too. Card 49 on the same phase was flat online (9 of 30 against 9.4). The leader rules exist for a reason: the longer leader at round 300 wins the both-queens-dead ending in 49 of 57 ladder games, and a team that never reaches 56 dragons now starts its leader only at round 400. Our local opponent does not ram or contest tiles like ladder teams, so the local check can miss the situation, as it did for card 49.

### Expected signal
Local games on layouts above 1200 cells, switch at 56 against off, in games where our count at round 150 is under 56: skip share in rounds 151-200 at most 0.35 (ladder 0.53, and 0.30 before round 151); pearls eaten in rounds 151-200 at least 0.9 of rounds 101-150 (ladder 0.52); splits at least 0.8 (ladder 0.41); dragons alive at round 200 not below round 150. A game on a layout of 1200 cells or fewer, and a game that stays at 56 or more dragons from round 151 to round 400, plays move for move as with the switch off. Also report, as the cost side: our longest dragon at round 300 and at the end, on against off.

### What would show it's wrong
The three counts are not met in games that start the phase under 56 dragons (the behaviour has another cause: drop the card, do not tune it). Or they are met and our dragon count at round 300 is still under half of the opponents' (the loss is earlier than this phase). Or our longest dragon at the end is shorter with the switch on and we lose more both-queens-dead endings than with it off (the wait costs the ending the leader phase exists for). Or no local game on a layout above 1200 cells starts the phase under 56 dragons, in which case the check says nothing and that must be reported as "not shown".
