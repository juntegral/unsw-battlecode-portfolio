## Candidate 2: our queen is never spent

**The claim (B's):** our queen never ends a move inside the reach of an enemy head she can see while another move
exists; she never rams; and when she has no free cell she gives away two segments from her tail ("sheds") instead
of keeping two and giving away the rest ("cuts"). On every map, also the small ones where the queen rules are off
today. B: +0.9 to +2.8 points (strict reading: 34 games).

**The strongest argument against it, as its opponent would put it.** "A queen saved on this turn is not a queen
alive at round 500. We can see what happens to our queen when she does take the safe step in the very same
situation: she is not rammed that round, and then she is dead within 50 rounds six times out of ten and alive at
the end of the game in 6 to 9% of cases, the same as when she did not take it. The 34 'flips' need her alive at
round 500. Twenty-five of them are against one opponent. A third of the deaths it counts are on small maps, where
the team measured that queen rules lose the fight and switched them off for that reason, and where our queen is
alive at the end in 4 of 145 games whatever she does. Every earlier attempt to protect her cost games, locally and
online. And as B wants it coded, from the pieces that exist, the rule is blind to pearl-paid steps and to the part
of an enemy that lies outside her view."

What is left: the counts are right, the rule is sound as a rule, and its three parts are not equal. I would defend
**+0.3 to +1.5 points (1 to 6 games in 401), most likely about +0.5 to +1**, the low end if it is built from the
existing pieces, and I would not switch it on for maps of 600 cells or fewer without a test of its own.

### A. The counts

Script `x_c2.py` walks all 2,478 replays and stores every turn of either queen that starts with an enemy head in
her view; tables: `x_c2a.py` (`x_out/c2a.txt`), `x_c2b.py`, `x_c2c.py`, `x_c2cut.py`. My first model used the plain
reach and called 42 of our queen's fatal cells "safe"; the reason is the pearl-paid step (candidate 1, item A). With
pearl-paid steps in the model, as A4 has them, the counts agree:

| | B / A4 | mine (pearl-paid reach) | mine, plain reach |
|---|---|---|---|
| our queen's deaths: rammed after stepping into reach / staying in reach, a safe step on the board | 66 / 38 = 104 | 67 / 39 = 106 | 67 / 17 = 84 |
| rammed, cornered (no safe step) | 114 | 114 | 94 |
| rammed on a cell the model calls safe | 2 | 0 | 42 |
| rammed by an enemy outside her view / boxed in / she rams | 31 / 91 / 19 | 31 / 91 / 19 | the same |
| avoidable rams, live bot / our opponents / forgot / SSS / Vibing++ | 68 / 27 / 39 / 38 / 35 | 70 / 26 / 40 / 38 / 34 | 55 / 28 / 32 / 35 / 31 |
| turns that end in reach by her own choice, per 1,000 queen-rounds: meow / opponents / top three | 2.66 / 1.46 / 0.6 to 1.1 | 2.45 / 1.34 / 0.5 to 0.9 | 1.94 / 1.16 / 0.4 to 0.8 |
| the same against test4 and WeHaveQuizzes only: meow / top three | 2.6 / 0.4 | 2.35 / 0.36 | |
| such a turn is punished by a ram that round: our queen / theirs / top three | 71% / 16% / 32 to 47% | 76% / 19% / 48 to 53% | |
| turns the rule would change in 401 games, and pearls eaten on them | 149, 21 | 138, 22 | 109, 22 |
| a boxed-in queen of 6 or more cuts / sheds: meow, forgot, SSS, Vibing++ | 40 / 0, 0 / 1,448, 0 / 394, 105 / 78 | 39 / 0, 0 / 1,448, 0 / 394, 104 / 74 (+31 other) | |
| all queen deaths per 1,000 queen-rounds: meow / opponents / forgot / SSS / Vibing++ | 6.5 / 2.2 / 2.8 / 2.1 / 3.4 | 6.4 / 2.1 / 2.8 / 2.1 / 3.4 | |

("Queen-round" = one round in which a queen is alive. "Safe step" = a one-step move onto a free cell that no enemy
head in her view can reach this round. My "ends in reach" is measured on the real board after her move, A4's on the
board at the start of her turn; that is the small difference in the rates.) **The behaviour gap reproduces**: our
queen ends a turn in a visible reach by choice three to four times as often as a top-three queen, six times as often
against the same two opponents, and it is punished three times out of four.

By eye (`x_c2pick.py`, `x_eye.py`, `x_out/c2_eye.txt`), 19 turns. Of seven "stepped in" deaths: in three the killer
needed a pearl-paid step (1059073 round 133: our 2-long queen steps beside a pearl that lies between her and a
2-long; 1063016 round 59: two pearls in a row; 1053387 round 90); in two the only "safe" cell was a pocket (1068052
round 165: a one-cell dead end; 1029037 round 72: three cells); two were plain steps next to a head with open water
elsewhere (1058154 round 18, 1063767 round 153). Two cuts: 1044523 and 990346, both round 0 on Slithery Fight (below).

### B and C. Cause or consequence, and what happens next

**The safe step works for one round and not for the game** (`x_c2b.py` part 1, `x_out/c2b.txt`). Same situation,
our queen, by what she did:

| Situation at the start of her turn | she ended | turns | rammed that round | rammed within 10 rounds | dead of anything within 50 rounds | alive at the end of the game |
|---|---|---|---|---|---|---|
| inside a visible reach, a safe step exists | outside reach | 288 | 0% | 23% | 59% | **9%** |
| | in reach | 56 | 70% | 80% | 80% | 9% |
| outside reach, a small enemy within 4 steps, a safe step exists | outside reach | 922 | 0.1% | 27% | 64% | **6%** |
| | in reach | 80 | 82% | 88% | 91% | 4% |

The first three number columns are A4's table that B quotes (0.3% / 24% against 56% / 65%; mine agree). The last
two are new. On maps of 600 cells or fewer the queen that took the safe step was dead within 50 rounds in 88 to 99%
of cases and alive at the end in 1 of 142. A top-three queen in the same situation after the safe step: dead within
50 rounds in 57 to 61%, alive at the end in 17 to 19%. So the rule turns a death this round into a death a few dozen
rounds later by one of the routes it does not touch, which are already the larger part of her deaths: cornered
(114 of our 362), boxed in (91) or rammed by an enemy she cannot see (31).

**What that makes of the 34 flips** (`x_c2b.py` part 3). My recount of B's table, with the deaths the three parts
touch:

| Part | deaths | in wipe-outs | in round-500 wins | in round-500 losses, her queen alive | in round-500 losses, both dead (flip if ours lives) | expected flips if she then lives as often as our own queen alive at that round | as a top-three queen |
|---|---|---|---|---|---|---|---|
| never end in a visible reach | 106 (B: 104) | 55 | 6 | 19 | 26 (B: 26) | 4.9 | 12.9 |
| shed 2, never cut | 24 (B: 14) | 2 | 8 | 8 | 6 (B: 4) | 0.7 | 2.3 |
| never ram | 10 | 6 | 0 | 0 | 4 (B: 4) | 0.7 | 2.0 |
| all three | 140 (B: 128) | 63 | 14 | 27 | **36 (B: 34)** | 6.3 (B: 3.7) | 17.2 (B: 11.1) |

My two "expected" columns use one survival curve for all games (our queen alive at round 100 is alive at the end
in 15% of games, at round 200 in 26%; a top-three queen in 46% and 56%) and are cruder than B's, which splits by
economy and map size; B's lower numbers are the better ones. The direct measurement is lower still: queens of ours
that took the safe step were alive at the end 6 to 9% of the time. On that, the core rule is worth **26 x 0.06 to
0.09 = about 2 games in 401**, which is A4's own low reading (2.4) and B's low end (2.6). I see no reason to expect
more than that from this rule alone; the high end needs her to "live like a top-three queen", and nothing in the
candidate makes her do that.

**Economy does not explain the gap away, but it bounds the gain.** 60 of the 104 deaths came with our team under
two thirds of the enemy's length (B's own count). The comparison against the same two opponents (ours 2.35 turns by
choice per 1,000 queen-rounds, the top three's 0.36) is the cleanest one there is, and it holds.

**Allies near her do not change what happens at contact** (`x_c2c.py` part 2). With an enemy head within 3 steps, a
2-3-long queen of ours is rammed that round in 10 / 12 / 13 / 19% of turns with 0 / 1 / 2 / 3 or more own heads
within 6 steps; the top three's in 6 to 12% whatever the number. More own dragons near our queen go with more rams,
not fewer (they also take her exits). B was right to drop "defenders near the queen".

### D. Sample size

- 106 deaths in 401 games is a solid count (80% range 24 to 29% of games). The flips are not: **25 of the 36 strict
  flips are against WeHaveQuizzes, 8 against test4** (`x_c2b.py`, last two blocks). Against test4 our queen dies this
  way just as often (45 deaths against 40), but test4's queen is usually alive at the end, so a living 2-long queen
  of ours would still lose on queen length. The candidate's value against test4 hangs on candidate 1.
- By map size: 28 strict flips on maps over 600 cells, 8 on smaller ones (where 37 of the 50 deaths are in
  wipe-outs).
- Live bot only: 97 deaths, 19 strict flips (B: 87 and 19).
- Against the top three there is no count (21 games).

### E. Cross-team

- **Never ending in reach by choice:** all three, at a third to a quarter of our rate. Holds.
- **Shed, do not cut:** SSS and forgot always shed; Vibing++ cuts (it keeps 3, we keep 2) and is rank 1. New here
  (`x_c2c.py` part 1): after its 104 cuts Vibing++'s queen is dead within 20 rounds in 17% and it wins 63% of those
  games; after its 44 sheds, 20% and 84%; SSS and forgot after a shed: dead within 20 rounds in 6 to 8%. After our
  39 cuts she is dead within 5 rounds in 44%. So shedding is the better habit, and Vibing++ is somewhat worse off
  when it cuts, but it is not what makes or breaks a top team.
- **This part is mostly one map's opening** (`x_c2cut.py`, `x_out/c2cut.txt`). 29 of our 39 cuts are round 0 to 5
  on Slithery Fight, where the queen starts as a 25-long coil with no free cell. We keep 2 and give 23 to a child;
  SSS and forgot shed 2 a round; Vibing++ keeps 3; test4 splits in half; **WeHaveQuizzes does exactly what we do
  (keeps 2) and its queen is not dead by round 100 in any of its 12 games on that map**. Ours is dead by round 10 in
  13 of 47 games there (all opponents) and never alive at the end; SSS's is alive at the end in 16 of 43, forgot's in
  23 of 35. So the cut is not what kills her there; being left 2 long in the middle of her own team is. The ten
  later cuts are queens of 6 to 61 long; one is a certain thrown win (990346: 57 long at round 385, dead the next
  round, the enemy queen ends 3 long), 1069661 (36 long, dead 22 rounds later, her queen dead at the end) is a
  possible one, three were won anyway.
- **Never ramming:** SSS never does, the others almost never. Our 17 queen rams on small maps came in games of which
  we won 1 (`x_c2b.py` part 5). Holds, and costs nothing visible.

### F. Earlier experiments

From `work/plan.md` (all local, against our own older bots) and the smoke records:

- A bigger number instead of an order: threat x3 and x6, guard radius 3: "do not cut rams (rammed 9-12)" in 24
  games. This is the nearest thing to the candidate and it failed for the reason B gives (a sum, not an order).
- A separate queen planner with a "never in reach" veto: 69 to 71 wins of 156 where the base won 95; the queen
  alive at the end in 7 to 10 games instead of 4; "queen protection costs 11-26 wins and buys 2-5 queen wins". It did
  much more than the veto. What transfers is the second half of the sentence: even a queen that was protected at
  every step was alive at the end in 7 to 12 of 156 games.
- **The queen rules on small maps.** With the minimal queen rules on every map the local sets went from 16 to 13
  and from 11 to 7 wins on small maps; letting the queen trade again did not bring them back ("queen rules cost on
  small maps ..., not via trading"). `QUEEN_MIN_CELLS 600` exists because of this. B's change list makes
  `map_threats()`, `threat_at()`, `is_trader()`, the split test and the paid escape use `real_queen()`: on small maps
  that is most of what the gate switches off, except the portal ban. B says so under risks. I rate it higher: it is
  the one place where this candidate contradicts a measured result of the team's own.
- **Online: qn23**, the "queen does not walk into traps" build (another rule; recounted in `x_c1f.py`): 8 wins of 42
  against a live rate near 28%, our queen alive at the end in 2, and against test4 and WeHaveQuizzes the team's own
  count is 3 wins of 30 with her median death at round 87 against 114. Too small to blame the rule, but it is the
  only queen-safety rule that has been online and it did not help the queen.
- Too small to say / tested something else: all of the above. None is this veto on the normal step chooser.

### G. Backfire

- **A queen that refuses a pearl:** she ate a pearl on 22 of the 138 turns the rule would change, 12 of them before
  round 100. One pearl per 18 games. Not a cost.
- **A queen that flees into a dead end:** on 20 of the 138 turns the only safe step was a pocket or a portal step
  (room under 8 cells), and on 13 of the 106 fatal ones. B's veto skips closed cells, so these become "cornered",
  not saved.
- **A queen that stops fighting on small maps:** 44 of the 138 turns, 36 of the 106 deaths and all 10 own rams are on
  maps of 600 cells or fewer. There 85 of our 145 games end by wipe-out (we win 30 of them), the queen is one of a
  handful of dragons, and she is alive at the end in 4 games whatever she does (`x_small.py`). A rule that makes her
  step away there takes a fighter out of a fight that decides six games in ten, and a queen-rule win almost never
  pays it back. The count that could show harm does not exist: nobody has played it.
- **Giving away 2 a round inside her own coil** makes eleven 2-long children next to her head on Slithery Fight
  instead of one 23-long. SSS and forgot do it and lose nothing; whether our small dragons then step onto her last
  exit, as they do in 20 games today, cannot be seen in a replay of the other behaviour.

### H. The code claim

Read: `pick_direction()` (the `LONG_SAFE_MIN_LENGTH` block), `score_step()`, `map_threats()`, `threat_at()`,
`stride_reach_map()`, `spread_kill()`, `queen_margin()`, `sprint_escape()`, `escape_child_size()`,
`split_child_size()`, `is_trader()`, `is_queen()`, `real_queen()`.

- B's description of today's code is right: for the queen the danger of a cell is one term of a sum
  (`PENALTY_HEAD_RACE` scaled by her length, smallest for a 2-long) and a pearl can outweigh it; dragons of 8 or
  more get an order of preference (`LONG_THREAT_VETO`), the queen does not; `escape_child_size()` returns
  `length - 2` when no cell is enterable.
- **The pieces B wants to reuse do not compute "every cell an enemy head can move into", and the difference is half
  of the candidate.** `stride_reach_map()` gives each enemy a reach from `visible_parts(id)`, the number of its
  segments inside her 7x7 view, and `spread_kill()` counts plain steps. Missing: pearl-paid steps, and the part of an
  enemy that lies outside her view (the killer was only partly in her view in 70 of our 220 rams by a seen enemy; a
  3-long showing 2 or 1 segments in 29 of them). I replayed our queen's turns against four reach models
  (`x_c2vis.py`, `x_c2vis2.py`, `x_out/c2vis.txt`). She moved onto a cell in reach although a free cell out of reach
  existed on 136 turns in 401 games and was rammed that round on 103 of them. A veto would have fired on:

  | reach model | of the 136 turns | of the 103 fatal ones | turns it changes in all | of them false alarms |
  |---|---|---|---|---|
  | true length, pearl-paid steps (the study's "safe step") | 136 | 103 | 136 | 0 |
  | true length, plain steps | 96 | 71 | | |
  | **the existing pieces: visible parts, plain steps** | **62** | **51** | 68 | 0 |
  | the same with one unseen segment assumed (A4's suggestion) | 67 | 59 | 220 | 150 |

  When it fires, the cells it allows are truly safe (61 of 62). But built as B describes it sees half of the deaths
  the candidate is credited with. Guessing one more segment recovers little and triples the turns it changes. To get
  the whole count the team would have to write a reach test that follows pearls and guesses lengths, which is new
  code and not "the pieces exist".
- **It is not "one block".** B lists five more places that must change, and three of them (`map_threats()`,
  `threat_at()`, `is_trader()`) change how the queen scores every step on small maps, not only the three things
  named. That is the hidden map-size condition of this candidate: the rule itself has none, but applying it on small
  maps means lifting most of `QUEEN_MIN_CELLS`.
- `escape_child_size()`: returning 2 for the real queen when no move exists is a one-line change and does what B
  says.

### What is left of the claim

| | B | after the attacks |
|---|---|---|
| the behaviour gap | 2.66 against 0.6 to 1.1 per 1,000 queen-rounds; 104 deaths | 2.45 against 0.5 to 0.9; 106 deaths |
| games that end differently | 34 strict, 3.7 to 11.1 realistic | 36 strict; about 2 to 6 realistic, and 25 of the 36 against one opponent |
| points | +0.9 to +2.8 | **+0.3 to +1.5** |
| the three parts | one candidate | the veto: sound, worth about 2 games with a perfect reach test and about 1 as B would code it (it fires on 51 of the 103 fatal turns); never ram: free, 0 to 1 game; shed not cut: mostly the Slithery Fight start, plus one or two thrown wins in 400 games |
| on small maps | "part of the change" | untested, against the team's own local result, in the games we are closest to winning |
