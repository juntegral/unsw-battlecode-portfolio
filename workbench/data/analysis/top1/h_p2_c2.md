## Candidate 2: our queen is never spent

### 1. The claim

**Our queen never ends a move inside the reach of an enemy head she can see while another move exists; she never
rams; and when she has no free cell she gives away two segments from her tail, not all but two.** At every length and
on every map.

"On every map" is part of the change: today the queen rules are switched off on maps of 600 cells or fewer
(`QUEEN_MIN_CELLS`), where she is an ordinary small dragon. This candidate removes that map-size switch for the three
things named, and for nothing else.

### 2. Evidence

All counts in this section are sub-session A4's (`deep-read-4.md`, scripts `d_class.py`, `d_expo.py`, `d_haz.py`,
`d_cut.py`, `d_misc.py`; outputs in `d_out/`), measured on every game; the last two rows and the split into parts are
mine (`h_c2.py`, output `h_out/c2.txt`). A **safe step** is a one-step move that ends on a cell no enemy head in her
view can move into this round. A **queen-round** is one round in which a queen is alive.

| | meow, all builds | meow live bot | our opponents | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|
| From outside reach she steps into it although a safe step exists (share of such turns) | 0.76% | 0.68% | 0.42% | 0.18% | 0.15% | 0.23% |
| Inside reach with a safe step, she ends in reach again | 19% | 17% | 13% | 10% | 8% | 10% |
| Both together, per 1,000 queen-rounds | 2.66 | 2.54 | 1.46 | 0.81 | 0.57 | 1.05 |
| A turn that ends in reach is punished by a ram | 71% | 72% | 16% (by us) | 44% | 47% | 32% |
| Games in which she died on such a turn | 104 of 401 = 26% | 68 of 275 = 25% | 27 of 401 = 7% | 39 of 632 = 6% | 38 of 503 = 8% | 35 of 502 = 7% |
| No free cell and 6 or longer: cuts herself to 2-3 / gives away 2 from the tail | 40 cuts, never the other | (not split by build) | 85 / 109 | 0 / 1,448 | 0 / 394 | 105 / 78 |
| Rams an enemy head herself although a free safe cell exists (games) | 10 | 8 | 1 | 4 | 0 | 5 |
| All queen deaths per 1,000 queen-rounds | 6.5 | 6.3 | 2.2 | 2.8 | 2.1 | 3.4 |
| Own queen alive at the end, in this team's wins / in its losses (`h_c2.py`) | 25% / 4% | 25% / 4% | 55% / 3% | 58% / 7% | 57% / 12% | 37% / 9% |
| Own queen died on such a turn, in wins / in losses | 16% / 30% | 18% / 27% | 3% / 16% | 3% / 11% | 6% / 11% | 5% / 10% |

So does each of the three do it? Never ending in reach by choice: yes, all three, at a quarter to a third of our rate,
and against test4 and WeHaveQuizzes alone at a sixth (0.4 against our 2.6 per 1,000 queen-rounds). Giving away 2
instead of cutting: SSS and forgot always, Vibing++ not (it cuts to 3, and A's read shows it losing won games that
way). Not ramming with the queen: SSS never, the other two almost never.

**The rule works on the turns on which our queen already follows it** (`d_after.py`; measured). Inside a visible
reach with a safe step on the board: when she took it she was rammed that round in 0.3% of 290 turns and within ten
rounds in 24%; when she did not, 56% and 65% of 68 turns. Outside reach with a small enemy within 4 steps: 0.1% and 19%
of 3,887 turns against 83% and 87% of 69.

**What it costs is small and counted.** The rule would change 149 turns of the queen in 401 games (81 steps into
reach, 68 stays in reach). On 21 of them she ate a pearl: one pearl per 19 games.

**Games that show it and its absence.**

- Absent: 980372 round 94 (Around UNSW; our 2-long queen steps west onto the next cell of her little loop, 2 steps from
  a 3-long that reaches 2; north and east were 4 steps from it). 1023823 round 81 (Australia; she takes a pearl that
  lies between her and the head of forgot's 3-long; east was safe). 990346 round 385 (Slithery Fight; our queen is 57
  long, has no free cell, cuts herself to 2 and dies next round; the enemy queen ends the game 3 long, so one living
  queen of any length wins it). All three from `deep-read-4.md`.
- Shown: 1063780 rounds 127-136 (Vibing++'s queen walks away from a small enemy on all seven occasions one comes
  within 3 steps; `deep-read.md`). 1063783 rounds 397-412 (forgot's 42-long queen is boxed in by her own coils, gives
  away 2 a round for 16 rounds, walks out 10 long and ends the game at 29; `deep-read.md`).

**Trials that exist.** None of this exact rule. What came near it, all local, all against our own bots
(`work/plan.md`):

- A larger number instead of an order: `QUEEN_THREAT_MULT` 3 and 6 and `QUEEN_GUARD_RADIUS` 3 "do not cut rams
  (rammed 9-12)" in 24 games.
- A separate planner for the queen with a "never in reach" veto inside it (`QUEEN_BRAIN`): the queen lived in 7-10 of
  156 games instead of 4, and the team won 69-71 where the base won 95. The note: "queen protection costs 11-26 wins
  and buys 2-5 queen wins". That planner also paid segments to move, searched five steps ahead and scored room; it was
  not this one veto on the normal step chooser.
- Switching the existing queen rules on for small maps cost local wins (small maps 13 against 16 and 7 against 11),
  which is why `QUEEN_MIN_CELLS 600` exists.
- Online, the "no trap" build qn23 (card #23, another rule): boxed-in deaths 15 of 45 against 52 of 215 for the live
  bot, no gain. Card #25 (`QUEEN_WAIT`) never fired, because the cut had already made her 2 long.

### 3. Mechanism

A living queen at round 500 beats a dead one, at any length. 143 of our 401 games (36%) end at round 500 with both
queens dead, and we lose 102 of them; in every one of those a living queen of ours wins outright. In the 73 games that
end with ours dead and hers alive, a living queen of ours is at least a queen-length game, and with candidate 1 a win.
The three parts stop her from dying on turns on which the board offered something better:

- a move out of reach existed (104 deaths),
- two segments would have bought a round and kept the rest of her (14 deaths that follow a cut, 40 cuts in all),
- a free safe cell existed and she rammed instead (10 deaths, all on maps where the rules are off).

### 4. Expected effect

**(a) Games that end differently** (`h_c2.py` part 3 and `h_joint.py`; inferred from played games). "Top-three
survival" and "our own other rates" are the two realistic readings of the footing section.

| Part | deaths (maps over / up to 600 cells) | strict | realistic: top-three survival | realistic: our own other rates |
|---|---|---|---|---|
| never end a move in a visible reach | 104 (68 / 36) | 26 | 8.6 | 2.6 |
| give away 2, never cut | 14 (14 / 0) | 4 | 1.4 | 0.4 |
| never ram | 10 (0 / 10) | 4 | 1.2 | 0.0 |
| **the candidate (all three), meow 401 games** | 128 (82 / 46) | **34** | **11.1** | **3.7** |
| the candidate, live bot 275 games | 87 (57 / 30) | 19 | 6.4 | 2.1 |

The strict count is high because it lets the saved queen live to round 500. Of the 128 deaths 60 are in games that
ended by wipe-out (nothing changes), 11 in round-500 wins, 34 in round-500 losses with the enemy queen dead (each
flips if ours lives) and 23 in round-500 losses with hers alive.

**(b) In points:** realistic +0.9 to +2.8 (strict +8.5). Live bot +0.8 to +2.3. The low end says: she no longer dies
this way but stays as exposed to being cornered and to unseen sprinters as she is today. The high end says she then
lives like a top-three queen, which this rule alone does not make her.

**(c) Where it acts.** On turns with an enemy head in her view: one round in five. Two thirds of the deaths it
touches are on maps where the queen rules are on today, one third where they are off. It does nothing against the
kinds of death it does not name: cornered with no move out of reach (114 games), rammed by an enemy she could not see
(31), a team-mate on her last exit (31), a terrain dead end (30). And nothing in the 170 games that end by wipe-out.

**(d) With the other candidates.** It needs none first. With candidate 1 it more than adds (see candidate 1, item 4d):
together 49-54 strict and 12.3-21.4 realistic wins, +3.1 to +5.3 points. Candidates 3 and 4 do not touch the queen;
candidate 4 would put more of our dragons' rams near her (item 2 there).

### 5. What changes in `mybot2/main.cpp`

- **New block in `pick_direction()`**, after `apply_route(...)`, for `real_queen()`: mark every cell that an enemy
  head visible this round can move into this turn. The pieces exist: `stride_reach_map()`, `spread_kill()` and
  `queen_margin()` already compute exactly that for the queen's multi-step moves (a cell is in reach when
  `queen_margin(cell) <= 0`); the block must use heads seen this round only, not the three-round "ghosts". If any
  scored, not-closed direction is out of reach, subtract `LONG_THREAT_VETO` from every direction that is not; if none
  is, set `cornered = true`. This is the order that dragons of 8 or more already have (`LONG_SAFE_MIN_LENGTH` block);
  today the queen's danger is one term of a sum, `PENALTY_HEAD_RACE 450 x max(0.5, length / 4) x ...`, smallest for
  the shortest queen, which a pearl (`EAT_BONUS 300` plus target bonus) outweighs.
- **Five places must obey the same test or the rule leaks:** in `act()`, `cornered && (is_big() || is_queen()) &&
  sprint_escape(path, true)` and the length test inside `sprint_escape()` must use `real_queen()`; `map_threats()` and
  `threat_at()` choose the queen's danger map by `is_queen()` and must use `real_queen()`, or the paid escape will not
  see the same danger on small maps; `split_child_size()` must return 0 for the real queen while an enemy head is
  near (`QUEEN_SPLIT_CLEAR` is 0 today; 16 of our 251 rammed queens had split with an enemy in view within their last
  three turns); `is_trader()` must test `!real_queen()` instead of `!is_queen()`. `extend_stride()` already treats
  `real_queen()` separately (`stride_caution()` returns 2) and needs no change.
- **`escape_child_size()`**: when `no_move` and `real_queen()`, return `unswbc::Constants::MIN_SIZE` (the child is the
  two tail segments) instead of `length - 2`.
- **Toggles.** None for this rule. `QUEEN_THREAT_MULT 1.0`, `QUEEN_GUARD_RADIUS 0`, `QUEEN_PESSIMIST false` and
  `QUEEN_BRAIN false` are the earlier attempts and stay as they are. `QUEEN_MIN_CELLS 600` stays for the other queen
  rules (portals, the split round, feeding).
- Size: one new block of about thirty lines, seven conditions, one constant.

### 6. What would show it is wrong

Counted on new replays against test4 and WeHaveQuizzes with `d_class.py`, then `d_expo.py`, `d_tab.py`, `d_cut.py`:

1. Turns that end in reach although a safe step existed: from 2.6 per 1,000 queen-rounds to under 0.8 (top three
   0.6-1.1). If not, the code does not do what the rule says; look for the path around it (stride, split, trade).
2. Games in which she dies on such a turn: from 26% to under 8%. Cuts of a queen of 6 or more: from 40 in 401 games
   to none. Own rams with a free safe cell: none.
3. Queen deaths per 1,000 queen-rounds: from 6.5 to about 5; alive at round 300 from 15% to about 22%. **If 1 and 2
   hold and this does not move, the deaths have moved to "cornered" (cornered turns would rise from 2.8 to above 4 per
   1,000 queen-rounds): then the rule only delays her death and is worth the low end.**
4. Cost check: natural pearls eaten by the queen in rounds 0-99 within 10% of today's 4.7 and 3.3 per 100 rounds;
   units at round 100 not lower; wipe-out losses (26% of games today) not higher.

Wins: expected 0.3 to 0.8 wins in 30. Not a win test. Sixty games give about 60 queen deaths, enough for points 1-3.

### 7. Known risks

- **Every earlier attempt to protect the queen lost games locally**, and the 600-cell switch exists because of it. The
  rule here is narrower than all of them (it changes 149 turns in 401 games), but on small maps the team fight
  decides most games (59% of our games there end by wipe-out) and this has not been tried there.
- **A queen saved once meets the next danger.** Against these opponents a turn in reach is punished 71% of the time
  and she is cornered 2.8 times per 1,000 queen-rounds without any choice of hers. That is why the realistic range
  starts at +0.9 points.
- **The safe step can be a bad step.** In 12 of the 104 deaths the only safe step led into a pocket; the rule skips
  closed cells, but it may trade a ram for a boxed-in death in some of the others.
- **The reach test can be wrong.** A head in view may belong to a longer dragon than its visible part shows; dragons
  that move between her turn and the enemy's are not modelled (A4's model called the fatal cell safe in 2% of rams).
- **Giving away 2 a round makes a small dragon each round** inside her own coils. SSS and forgot do exactly this on
  the coiled 25-long start of one map and lose nothing, but our team-mates step onto her last exit (20 "nose to nose"
  deaths), which this candidate does not fix.
- Confounder I could not remove: 60 of the 104 deaths came with our total length under two thirds of the enemy's
  and 19 dragons of ours on the board against 31 (`h_c2.py` part 2b). Where the team is being overrun, a queen saved
  this round may have nowhere to go the next.
