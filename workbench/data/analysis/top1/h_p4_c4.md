## Candidate 4: do not give way at contact

### 1. The claim

**A dragon of 4 or shorter that sees at least as many heads of its own team as enemy heads rams any enemy dragon of 4
or shorter whose head it can reach this turn: longer, same length or shorter. Alone or outnumbered, it rams only one
that is longer than itself.** On every map.

"On every map" is part of the change: today the trade rule has a map-size switch (`AGGRESSIVE_MAX_CELLS 1200`) that
all but forbids such rams on larger maps.

### 2. Evidence

**The lead's and A3's numbers** (`findings.md` 6c, `out2/recount3.txt`; measured). On maps over 1,200 cells the live
bot rams in 8% of meetings (an enemy head on the next cell, both dragons 4 or shorter); our opponents 35%, SSS 41%,
Vibing++ 33%, forgot 35%. It starts 22% of the rams of its games (top three 48-57%) and eats 29% of the pearls rams
leave (49-52%). On smaller maps it rams at meetings like everyone (34% against 31%).

**New here: who rams what, and with whom around** (`h_c4walk.py`, 791 games walked: all 401 of ours and 492 of the
top three; output `h_out/c4walk.txt`; measured). A chance is a turn of a non-queen dragon of 4 or shorter that starts
with the head of an enemy non-queen dragon of 4 or shorter in its view and reachable this turn. "Not outnumbered" =
other own heads in its 7x7 view at least as many as enemy heads there. Share of chances that end in its ram, with the
enemy head on the next cell / 2-3 free steps away:

| Maps over 1,200 cells | meow live bot | tc30 build | our opponents | Vibing++ | SSS | forgot |
|---|---|---|---|---|---|---|
| not outnumbered, enemy longer | 16% / 12% | 87% / 58% | 91% / 83% | 89% / 90% | 98% / 90% | 98% / 83% |
| not outnumbered, enemy same length | 15% / 9% | 87% / 66% | 72% / 55% | 90% / 87% | 98% / 84% | 91% / 57% |
| not outnumbered, enemy shorter | 2% / 0% | 3% / 0% | 48% / 29% | 68% / 55% | 63% / 44% | 78% / 46% |
| alone or outnumbered, enemy longer | 3% / 0% | 4% / 0% | 46% / 42% | 42% / 41% | 93% / 59% | 55% / 20% |
| alone or outnumbered, enemy same length | 3% / 0% | 5% / 0% | 12% / 5% | 19% / 21% | 5% / 0% | 13% / 5% |
| alone or outnumbered, enemy shorter | 3% / 0% | 3% / 0% | 10% / 2% | 6% / 5% | 3% / 0% | 9% / 3% |
| rams made this way, per game | 7.5 | 27.6 | 43.9 | 58.6 | 55.0 | 57.7 |

| Maps of 1,200 cells or fewer | meow live bot | our opponents | Vibing++ | SSS | forgot |
|---|---|---|---|---|---|
| not outnumbered, enemy longer | 88% / 82% | 77% / 56% | 92% / 88% | 98% / 94% | 94% / 58% |
| not outnumbered, enemy same length | 89% / 76% | 64% / 50% | 87% / 83% | 98% / 93% | 83% / 65% |
| not outnumbered, enemy shorter | 11% / 0% | 42% / 27% | 64% / 51% | 83% / 58% | 61% / 45% |
| alone or outnumbered, enemy longer | 11% / 0% | 52% / 34% | 43% / 37% | 83% / 42% | 47% / 26% |
| alone or outnumbered, enemy same length | 9% / 0% | 14% / 6% | 24% / 18% | 16% / 0% | 16% / 9% |
| alone or outnumbered, enemy shorter | 10% / 0% | 12% / 3% | 11% / 6% | 8% / 0% | 11% / 3% |
| rams made this way, per game | 8.3 | 10.8 | 12.7 | 12.2 | 11.0 |

So does each of the three do it? Yes, all three, and both of our usual opponents, on both kinds of map: with the
numbers on their side they ram nearly every small enemy head they can reach, a shorter one in half to four fifths of
the cases; alone, they ram a longer one about half the time and hardly anything else. This is the same head count
our own rule uses (`TRADE_LOCAL_EDGE`). **So the top teams do not "ram alone"; A3's proposal to drop the head count is
not what they do.** What they do and we do not is three things: the same rule on big maps (our switch), shorter
targets when not outnumbered (19 of their 57 rams a game on big maps, 3.6 of 12 on the others; we: 0.2), and longer
targets when alone (4 a game; we: 0.2).

**What such a ram is worth to the side that starts it** (`h_c4pearls.py`, same games, output `h_out/c4pearls.txt`;
measured). Swing = (pearls of the two corpses eaten by the starter's team minus its dragon's length) minus the same
for the other team, in segments per ram, on maps over 1,200 cells:

| Kind of ram | top three | our opponents | meow live bot | tc30 build |
|---|---|---|---|---|
| not outnumbered, victim longer | +2.5 | +3.2 | +2.3 | +2.8 |
| not outnumbered, victim same length | +1.6 | +2.2 | +1.1 | +1.0 |
| not outnumbered, victim shorter | +1.1 | +1.4 | -0.7 (31 rams) | (5 rams) |
| alone or outnumbered, victim longer | +0.4 | +1.2 | -0.8 (34 rams) | (7 rams) |
| alone or outnumbered, victim same length / shorter | -0.2 / -1.1 | +0.7 / 0.0 | -1.0 / -2.1 | |
| all rams it starts: number per game x swing = segments per game | 65 x 1.15 = +75 | 52 x 1.77 = +92 | 8.6 x 0.52 = +4.5 | 29 x 1.19 = +34 |

The top three ram exactly where the swing is positive for them and hold back where it is negative. In our big-map
games the opponent gains 92 segments a game from the rams it starts and we gain 4.5 from ours. For scale: our total
length at round 300 on those maps is 121 and theirs 327. On the smaller maps the two numbers are 9 for us and 14 for
them.

**Wins against losses.** For the top three on big maps this does not separate wins from losses (Vibing++ starts 73
such rams a game in wins and 68 in losses; all three together 64 and 67): among them it is what everybody does. For
us it does: 15 a game in our 9 big-map wins, 8 in the 68 losses (`h_out/c4pearls.txt`); partly cause, partly the
consequence of having the numbers.

**Near our queen** (`h_c4.py`; measured). A small enemy that comes within 4 steps of the own queen is rammed by one
of her team in 1.7% of cases on big maps and 4.9% on the others for the live bot; 9-20% and 13-15% for the top three,
18% and 12% for our opponents. Nobody escorts a queen (`deep-read-2.md`); these are ordinary contact rams that happen
near her.

**Games that show it and its absence** (the pairs table of `deep-read-3.md`, same opponent, same map, same side).
Absent: 1063240 (Islands, live bot against WeHaveQuizzes): 6 of 84 meetings rammed, 6 rams made and 32 suffered in
rounds 0-149, 47 units against 61 at round 150, wiped out at round 449. Shown: 1068051 (the tc30 build, same
pairing): 11 of 40 meetings, 22 rams made and 29 suffered, 60 units against 39 at round 150; and 1051826 (SSS on the
same map against test4, a win).

**The trial that exists: tc30** (online, `tc30-test-result.txt`, `deep-read-3.md`). The build removed the map-size
switch for one test only: on big maps a target showing at least the attacker's own length is enough (the live bot
asks for max(5, own length + 2)). It kept the head count and the 8-unit minimum.

- Behaviour: as the first table shows, it rams like the top three where it is not outnumbered and the enemy is not
  shorter (87%), and as little as the live bot in every other case.
- Economy on big maps: rams started 29 a game instead of 9, swing +34 segments a game instead of +4.5, units at round
  150 52 instead of 47, total length at round 300 147 instead of 121 (+21%). What the opponent gains from its own rams
  did not change (91 a game against both builds).
- Wins: 6 of 30 against the live bot's 9.2. On big maps 0 of 12, where our own win rates for the bands it reached
  predict 1.7 (`h_c4.py`).
- Local (`work/plan.md`): the same idea ("TRADE_EVEN") no gain; dropping the head count ("TLE0") 60 wins of 118 where
  the base had 68, against a rushing copy of our bot.

**Tested:** the first of the three differences, online, with the behaviour and the economy moving as counted here and
the wins not. **Not tested:** shorter targets when not outnumbered, longer targets when alone, and all of it together
with candidate 3.

### 3. Mechanism

Through the economy. A ram kills one dragon on each side; what differs is who eats the pearls of the two corpses, and
the side that starts the ram with friends around eats 70-85% of them. A dragon that steps away instead eats 0.33
pearls in the next ten rounds against 0.70 for the enemy it left, and is rammed anyway in one case in five
(`deep-read-3.md`). On big maps this exchange is the largest single flow between the teams: about 90 segments a game
to the enemy. More units and length move games up the bands of the footing section; more of our dragons ramming near
our own queen also takes away some of the enemies that corner her.

### 4. Expected effect

**(a) Games.** No strict reading. Realistic, by parts, as total length at round 300 on maps over 1,200 cells and our
own win rate per band (`h_econ.py`):

- The tested part gave +21% (measured on 12 games): +2.4 to +5.3 wins in 401 by the band arithmetic. The trial itself
  won none of 12.
- The untested parts, inferred from the swing table: shorter targets when not outnumbered would add up to 20 rams a
  game, worth +1.1 each to the top three and between -0.7 and 0 to us in the few cases we have, plus whatever it
  saves when our longer dragon is not rammed first by the shorter enemy (the opponents make 13.5 such rams a game on
  us at +1.2 to +3.2 each). Somewhere between nothing and another +25 segments.
- Together +21% to +45%: +2.4 to +10 wins in 401; live bot +2.0 to +7.

**(b) In points:** the arithmetic says +0.6 to +2.4. Because the only trial won fewer games, my range is **0 to +2.4,
single figure +1**.

**(c) Where it acts.** Nine tenths of it on maps over 1,200 cells (111 of 401 games), from the first contact (round
20-90) to the end. On the other maps only the "shorter target" and "alone against a longer one" parts are new (about 4
more rams a game). It does nothing where the teams never touch.

**(d) With the other candidates.** It needs candidate 3: the trial's two best openings were lost between rounds 150
and 250 under the leader switch. It overlaps with nothing. It helps candidate 2 a little (rams near our queen) and
candidate 1 not at all.

### 5. What changes in `mybot2/main.cpp`

- `mark_trade_targets()`. Today: `normal_ok` needs `round <= feed_round`, a unit minimum (`TRADE_MIN_UNITS 8`, or
  `AGGRESSIVE_TRADE_MIN_UNITS 1` on maps up to 1,200 cells) and the head count (`TRADE_LOCAL_EDGE 1`); `worth` is
  `parts >= length` on maps up to 1,200 cells and `parts >= max(TRADE_TARGET_MIN_PARTS 5, length + 2)` on larger ones.
  New, for an enemy head showing 4 parts or fewer: if the head count holds, mark it whatever its length; if it does
  not hold, mark it when `parts > length`. No `aggressive` in either test, unit minimum 1 everywhere.
- `ram_path()`: `min(sprint_reach(), aggressive ? AGGRESSIVE_RAM_MAX_STEPS : RAM_MAX_STEPS)` becomes one value.
- Toggles that exist: `TRADE_EVEN` (false) makes `worth` the small-map test on every map, which is the tested part;
  nothing exists for shorter targets or for "alone against a longer one".
- What else must obey: `is_trader()` already keeps out dragons longer than 4, leaders and the queen. `score_step()`
  drops the fear of enemy heads for a trader and adds `TRADE_REWARD 2500 - TRADE_DECAY 80 x distance` towards a marked
  head, so every newly marked head also pulls the dragon towards it from several cells away; that is what makes a
  ram from two or three cells away (a "charge"), and it is also how a wrong mark would drag dragons around.
- Size: two conditions in one function, one in another, two constants.

### 6. What would show it is wrong

Counted on new replays with `h_c4walk.py`, `h_c4pearls.py` and the lead's `recount3.py`:

1. The first table's cells for us must reach, on both kinds of map: not outnumbered 85% / 60% for longer and same
   length, 60% / 45% for shorter; alone against a longer one 40%. Rams made this way on big maps from 7.5 a game to
   at least 45.
2. Swing per ram we start must stay above +0.8 overall (tc30: +1.19). **If the new kinds of ram come in below zero
   for us, as our few cases today suggest, they cost dragons and the rule is wrong for our bot as it is.**
3. What the opponent gains from its own rams on big maps must fall below 92 segments a game. In the tc30 trial it
   did not (91).
4. Units at round 100 not under 42 and at round 150 at least 52 on big maps (tc30's level); wipe-out losses not above
   today's 26% of games.

Wins: 0 to 0.7 expected in 30. Not a win test.

### 7. Known risks

- **The one online trial of its first part won fewer games** (6 against 9.2 of 30; 0 of 12 on the maps it changes).
  That is inside the noise, and the economy did move, but it is the only win evidence and it points the wrong way.
- **The same rams are worth less to us than to the top three.** Where we do start rams with the numbers on our side
  our team eats 68% of the pearls, theirs 78%; on shorter victims 55% against 84% (31 cases). The rule copies when
  they ram, not what happens afterwards.
- **We replace dragons more slowly**: 4.1 pearls eaten per split at length 4 against 3.3 for our opponents
  (`deep-read-3.md`), so an even trade costs us more.
- **Small maps are decided by wipe-out** (59% of our games on maps of 600 cells or fewer); more trades there can end
  games sooner in either direction.
- "Not outnumbered" is my count on the replay's 7x7 squares. The top teams may use another test that only looks like
  it.
