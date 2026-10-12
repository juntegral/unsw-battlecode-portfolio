## 2. Candidate 5: one leader, known to all

**The claim (A5's, `deep-read-5.md` section 7).** When our leader cuts itself, the new dragon (the heir) has a new
id. Every team-mate's record still names the old id for a median of 27 rounds, because a longer, older report
outranks a fresher, slightly shorter one. Feeding stalls meanwhile: the longest grows 5.0 per 25-round window with
a cut against 10.8 without. And a quarter of our deaths by choice happen next to no bigger dragon. The rule: fresher
news of a nearly-as-long dragon replaces older news of a longer one; seeing a dragon corrects its recorded length; a
feeder dies only next to a leader it can see is long. Three changes in the record code. Claimed: +0.7 to +2.2
points, "most likely a little over +1" (strict 6 to 12 games of 401, realistic 3 to 9).

**The strongest argument against it, as its opponent would put it.** "The 27 rounds were read off 82 games of a bot
we no longer run. In the builds we run today the leader is fed at its usual rate again 10 to 20 rounds after a cut,
and in the test builds after 5 to 10. The famous 5.0 against 10.8 is half arithmetic: a window with a cut in it has
lost 2 segments per cut by definition, and the window right after a cut, which a 25-round blindness would have to
hit, grows 11.4. On the smaller maps, where the close races are, the heir of a cut grows as fast as Vibing++'s. What
is left is feeders that die for the 2-long stub: one death in thirteen, about four pearls a race. For that the
candidate rewrites the one piece of shared memory the team has, with an age rule that, as written, lets the old
report win again on the very next ping, and that will crown the second dragon in every region where news of the
first is old; our two longest dragons are within 12 segments of each other in most of our races. Per pearl we
already convert as well as test4 and WeHaveQuizzes."

What is left after the attacks below: the mechanism exists, the code reading is right in its main lines, and two of
the three changes are harmless. Its worth is about a third of what is claimed, and the first change needs rewriting
before it does anything. I would defend **-0.3 to +0.8 points, most likely +0.2 to +0.4** (1 to 5 games of 401 on
the strict reading).

### A. The counts

Scripts `y_c5a.py`, `y_c5b.py`, `y_c5c.py` (outputs `y_out/c5a.txt`, `c5b.txt`, `c5c.txt`). Everything that needs
no ping is counted on all games; the belief numbers on the 82 games with readable pings.

| | theirs (A5) | mine |
|---|---|---|
| leader cuts per race from round 395, live bot, small / big maps | 3.8 / 3.9 | 3.9 / 4.0 (test builds 4.4 / 4.5) |
| ... made with a free cell left | 68% / 67% | 66% / 66% |
| ... our opponents; forgot; SSS; Vibing++ (small maps) | 2.3; 4.1; 2.0; 2.6 | 2.6; 4.2; 2.3; 2.7 |
| cuts of the final lineage from round 400, per race: all / with a free cell | 2.7 / 1.7 | 2.7 / 1.7 |
| lost races in which the segments left in those cuts exceed the margin | 10 of 102 (7 by free-cell cuts alone) | 10 (6) |
| growth of the longest per 25-round window from round 400, 10+ other own dragons: a cut in it or in the 25 rounds before / none | 5.0 (291 windows) / 10.8 (91) | 5.0 (294) / 11.1 (88) |
| ... live bot / test builds | 4.5, 11.4 / 6.1, 9.3 | 4.4, 11.9 / 6.1, 9.3 |
| ... against test4 / WHQ / others | 4.9, 11.4 / 5.5, 10.9 / 3.7, 9.6 | 4.7, 12.5 / 5.5, 10.9 / 3.7, 9.6 |
| ... small / big maps | 6.0, 12.4 / 4.3, 8.7 | 6.0, 12.6 / 4.2, 9.2 |
| ... our opponents | 6.0 (216) / 6.9 (156) | 5.9 (219) / 7.0 (153) |
| deaths by choice in races, rounds 300-499, next to no own dragon twice as long within 8 path steps, live bot small / big | 26% / 20% | 27% / 20% (test builds 26% / 16%) |
| ... our opponents; forgot; SSS; Vibing++ | 15 / 11; 8 / 5; 10 / 6; 14 / 10 | 15 / 11; 8 / 5; 10 / 6; 15 / 10 |
| pearls of those deaths eaten by the final lineage, live bot small / big | 36% / 27% | 36% / 26% |
| ... by where the death was: next to the longest / next to nothing, small maps | 70% / 13% | 71% / 11% |
| games with readable pings | 78 | 82 (24 + 31 + 27); 25 of them races, 12 won |
| rounds until half of our dragons name the true longest after a cut: quartiles | 17 / 27 / 36-41 (388 cuts) | 14 / 28 / 46 over 370 cuts; after 88 more cuts it never happens before the game ends |
| samples in rounds 400-494 in which under a quarter name the true longest | 187 of 347 | 211 of 429 |
| growth of the longest in the next 5 rounds: under a quarter name it / a quarter to a half / a half to three quarters / more | +0.42 / +1.85 / +1.51 / +2.00 | +0.40 / +2.06 / +2.10 / +2.10 |
| share of own dragons naming a longest dragon, small maps, rounds 400-424 | 37% | 39% |

**The counts reproduce.** The small differences are definitions (I call a split a leader cut when the dragon was at
least as long as every other own dragon at that moment; I find four more readable games).

### B. Cause or consequence

This is where the candidate is weakest. Five checks, each made so that a stale record would have to show.

**1. Where in time the missing growth sits** (`y_c5a.py` part 2). A5 pools "a cut in the window or in the 25 rounds
before". Split in two:

| growth of the longest per 25-round window (windows) | a cut INSIDE the window | a cut only in the 25 rounds BEFORE | no cut in 50 rounds | inside, with 2 segments per cut given back |
|---|---|---|---|---|
| meow, all races | 3.0 (225) | **11.4 (69)** | 11.1 (88) | 7.0 |
| meow live bot | 2.5 (147) | 10.0 (50) | 11.9 (63) | 6.6 |
| meow test builds | 3.9 (78) | 14.9 (19) | 9.3 (25) | 7.8 |
| meow, earlier bot (readable pings) | 1.5 (37) | 7.1 (14) | 9.7 (23) | |
| our opponents | 4.2 (142) | 8.9 (77) | 7.0 (153) | 7.5 |
| WHQ / test4 (against us) | 3.2 / 5.2 | 10.0 / 7.4 | 7.3 / 8.1 | 6.5 / 8.3 |
| SSS small / big | 1.4 / 1.4 | 4.1 / 5.4 | 6.3 / 6.7 | 5.9 / 4.6 |
| forgot small / big | 8.2 / 3.3 | 11.6 / 5.2 | 5.3 / 4.6 | 12.2 / 6.1 |
| Vibing++ small / big | 6.9 / 3.1 | 10.8 / 7.1 | 5.7 / 8.2 | 10.2 / 5.8 |

- A window that comes right after a cut and has no new cut in it grows as fast as a window with no cut at all:
  11.4 against 11.1. Inside the same game the difference is +0.8 segments (standard error 1.5, 30 games). A blindness
  of 25 rounds after every cut would fall into exactly these windows. It shows only in the earlier bot (7.1 against
  9.7).
- The whole deficit is in windows that contain a cut. Half of it is the cut: such a window holds two cuts on
  average, 2 segments each. With those given back our windows are at 7.0 against 11.1. For our opponents, test4,
  WHQ and SSS on small maps the same sum closes the gap (7.5 against 7.0, 8.3 against 8.1, 6.5 against 7.3, 5.9
  against 6.3). So about 4 segments per such window are missing in our games beyond the cut itself, and that part is
  ours.

**2. The clock after a cut** (`y_c5a.py` part 4, `y_c5f.py`). Deaths by choice within 3 steps of the team's longest
dragon, per 100 team-rounds, by rounds since the team's last leader cut (rounds 400-499 of races, teams with 10+
other dragons). If a record that runs out after 25 rounds held the feeders back, the rate would stay low until 25
and jump.

| rounds since the cut | 0-4 | 5-9 | 10-14 | 15-19 | 20-24 | 25-29 | 30-39 | 40-59 |
|---|---|---|---|---|---|---|---|---|
| meow, earlier bot (25 races) | 3.4 | 9.1 | 8.6 | 13.3 | 22.0 | 25.0 | 26.9 | 22.8 |
| meow, live bot with sealed pings (71) | 6.3 | 9.0 | 11.0 | 20.7 | 22.7 | 21.6 | 30.0 | 37.6 |
| meow, test builds (47) | 6.6 | 16.6 | 25.9 | 24.3 | 26.6 | 31.0 | 16.8 | 23.8 |
| ... deaths next to a stub of the last 26 rounds, live bot | 8.2 | 6.6 | 3.4 | 3.0 | 3.3 | 3.0 | 0.6 | 0.2 |
| our opponents | 6.6 | 9.9 | 8.9 | 11.9 | 7.8 | 10.4 | 8.7 | 6.6 |
| forgot, small maps | 10.5 | 17.1 | 11.7 | 14.4 | 12.2 | 20.0 | 15.5 | 16.1 |
| SSS, small maps | 5.9 | 8.6 | 11.6 | 14.3 | 13.6 | 13.3 | 21.6 | 32.7 |
| Vibing++, small maps | 9.5 | 10.4 | 9.8 | 14.1 | 12.9 | 14.0 | 9.6 | 11.3 |

- The earlier bot does look like a clock: low for 20 rounds, then up. That is the bot the belief numbers come from.
- Today's live bot is back at its usual rate after 15 rounds, the test builds after 10. Something that changed
  between the builds shortened the stall; the pings of those builds are sealed, so I cannot see what (section 6).
- In the first five rounds after a cut more of our feeders die next to the stub (8.2) than next to the heir (6.3).
  That part of A5's story is exact.
- Our rate when nothing is wrong (22 to 30) is two to three times anybody else's, because we feed everything in the
  last hundred rounds. Even 5 to 14 rounds after a cut our leader is fed as fast as WHQ's or Vibing++'s ever is.

**3. The heir itself** (`y_c5g.py`, from the walk `y_w2.py`). Its length t rounds after a leader cut made from
round 395, over the cuts still followed at t (the heir alive and not cut again):

| heir's growth after | 5 rounds | 10 | 15 | 25 |
|---|---|---|---|---|
| meow, earlier bot | +0.5 | +1.2 | +2.9 | +3.6 |
| meow, live bot (sealed), small maps | +0.9 | +2.1 | +2.2 | +4.6 |
| meow, test builds, small maps | +0.7 | +1.5 | +2.8 | +8.6 |
| meow, live bot (sealed), big maps | +0.2 | -0.1 | **-1.3** | +1.1 |
| meow, test builds, big maps | +0.4 | +0.6 | +1.1 | +0.1 |
| forgot, small / big maps | +2.1 / +1.7 | +4.2 / +3.2 | +6.1 / +3.7 | +8.9 / +5.9 |
| SSS, small / big | +0.1 / +0.7 | +0.6 / +2.6 | +1.5 / +4.1 | +3.3 / +6.9 |
| Vibing++, small / big | +1.3 / +1.4 | +2.4 / +2.7 | +3.3 / +3.5 | +6.1 / +5.9 |
| test4 (against us), big maps | +0.6 | +0.3 | +1.4 | -1.3 |

On small maps the heir of today's live bot grows like Vibing++'s and faster than SSS's. **The stall is a big-map
thing**: there our heir is no longer after 20 rounds than at birth, where a top team's has gained 5. test4 has the
same problem on big maps. Our big-map races are lost by a median of 44 segments, so that is not where 5 segments
decide much.

**4. What the feeders near a cut do** (`y_c5b.py` part 5). For every leader cut from round 395 I followed the own
dragons that could feed the heir (at most half its length, within 15 cells of the heir's or the stub's head) for 25
rounds, for the cuts after which the heir did not cut again:

| of those dragons, within 25 rounds | meow live | meow test | our opponents | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|
| died by choice within 3 steps of the heir | 14% | 17% | 13% | 15% | 16% | 8% |
| ... of the stub | 2% | 1% | 0% | 0% | 0% | 1% |
| ... of another own dragon twice their length | 10% | 15% | 12% | 10% | 5% | 4% |
| ... of none of these | 10% | 8% | 11% | 7% | 2% | 9% |
| alive and 3+ cells nearer the heir / nearer the stub / neither | 13 / 4 / 32% | 10 / 0 / 26% | 9 / 1 / 30% | 7 / 1 / 29% | 15 / 5 / 35% | 9 / 3 / 32% |
| of the deaths next to the heir: in the first 10 rounds | 40% | 40% | 63% | 66% | 61% | 62% |

Within 25 rounds as many of our nearby feeders die next to the heir as in any other team. They do it later: 40% in
the first ten rounds against 61-66%. That is a delay of some rounds, made up inside the same 25 rounds. It turns
into a loss when the heir cuts again first, and ours does that sooner than anybody's: 42% of our heirs cut again
within 10 rounds (our opponents 30%, forgot 29%, SSS 37%, Vibing++ 24%). Only 67 of the live bot's 316 leader cuts
from round 395 were followed by 25 quiet rounds.

**5. The pings themselves** (`y_c5e.py`; 196 leader cuts of the earlier bot from round 300 with 4 or more feeders
near). Share of the nearby feeders naming:

| rounds after the cut | 1 | 5 | 10 | 15 | 20 | 25 |
|---|---|---|---|---|---|---|
| the heir | 0% | 4% | 10% | 18% | 30% | 44% |
| the stub | 31% | 37% | 35% | 29% | 22% | 17% |
| another living dragon | 40% | 35% | 42% | 44% | 36% | 28% |
| a dead dragon | 28% | 24% | 14% | 8% | 11% | 11% |

So in the earlier bot A5's mechanism is there to be seen: the heir is named slowly, the stub for a long time. But
look at round 1. **Only 31% of the feeders standing near the leader named it before the cut.** Two thirds named
somebody else or a dead dragon. The team's record is poor at all times, not only after a cut. The same shows in the
growth numbers: in samples with no leader cut at all so far, the longest grows +0.16 per 5 rounds when under a
quarter of the team names it (19 samples) and +2.42 when more do (26). "The team knows its leader" predicts growth,
which is close to saying the same thing twice; "the team forgets it at a cut" is one of several ways of not knowing.

A cut-by-cut comparison of fast and slow naming inside the same game, which the lead asked for, cannot be made: 25
cuts of the earlier bot were followed for 15 rounds after round 395, in 5 of them a quarter of the feeders named the
heir by rounds 5-10 (heir +2.6 in 15 rounds) and in 20 they did not (+2.4). No difference, and no power.

**What the feeders die next to** (`y_w4.py`, `y_c5c.py`; all 4,677 "no order" deaths of ours in races, rounds
300-499). Our bot lets a feeder die when the head of the dragon in its record is in view and within 3 cells in a
straight line. So every death has a target:

| the feeder died for | share | small / big maps | the final lineage ate, of its pearls |
|---|---|---|---|
| the true longest, 3 path steps or fewer away | 42.9% | 54.1 / 34.2% | 66% |
| the true longest, but a wall between (over 3 path steps) | 5.4% | 8.5 / 3.1% | 16% |
| another own dragon at least twice its length | 39.4% | 25.1 / 50.5% | 10% |
| the stub of a cut made in the last 26 rounds | 7.6% | 7.4 / 7.7% | 12% |
| another dragon under twice its length | 4.7% | 4.9 / 4.5% | 8% |

A5's "a quarter die next to no bigger dragon" (which I reproduce with its path-step test) is three different things.
What candidate 5 would stop is the last two rows: **12.3% of feeder deaths, 6.1 pearls a race**, of which the
lineage gets 0.7 today and would get 4.0 if every one of those feeders died next to the true longest instead. One
row is new and is not in the candidate: 5% of our feeders (8.5% on small maps) die within 3 cells of the right
dragon on the wrong side of a wall, because the test counts cells and not steps. And the largest row by far is the
third: four deaths in ten go to a big dragon that is not the longest. The team's log calls that "regions elect
local leaders". Candidate 5 does not work on it.

### C. What happens next

- **The delay is mostly made up; the misdirected pearls are not.** Per race: 4.2 pearls dropped for a fresh stub,
  1.9 for a dragon under twice the feeder's length, 2.8 across a wall, 16.7 for another big dragon.
- **No pile of unused feeders next to our leader at the end.** At the end of a small-map race the live bot has own
  dragons worth a median of 8 pearls within 15 cells of its longest (our opponents 5, forgot 7, SSS 5, Vibing++ 10)
  and 7 units left (4 to 8). On big maps everybody's unfed length is far away (ours 43 pearls beyond 15 cells, the
  others 39 to 86).
- **In the last hundred rounds we convert as fast as anybody.** The longest holds 24% of our potential at round 400
  and 65-71% at the end on small maps; our opponents go from 43% to 77%, the top three from 37% to about 69%.
- **The live bot's leader does grow less after round 400**: 10 on small maps and 14 on big against 15.5 to 24 for
  the others. The test builds grow 21 on small maps. Which change did that is not known; none was in the leader
  code. Whatever candidate 5 repairs, part of it seems to be repaired already in the builds that were tested and
  not released.

### D. Sample size

- Belief: 82 games of the earlier bot, 25 of them races. Leader cuts from round 395 in those races with 25 quiet
  rounds after: 8. Everything said about what dragons "name" rests on that bot.
- All games: 143 races, 589 leader cuts from round 395 (483 with 10+ other dragons), 4,677 feeder deaths. The
  position-only measures (windows, clock, heir growth, targets of feeder deaths) are solid and hold against test4
  and against WHQ separately (windows with a cut inside 2.5 and 3.9, none 12.5 and 10.9).
- Close races: our lost races have margins of 1, 1, 2, 5, 5, 6, 6, 6, 7, 7, 9, 11, ... (median 32.5). Ten games
  decide every strict count in this section.

### E. Cross-team

- **forgot, Vibing++ and WHQ do feed through a cut**: flat clocks, heirs that gain 2.4 to 4.2 in ten rounds.
- **SSS on small maps stalls more than we do** (clock 5.9, 8.6, 11.6 against a later 22 to 33; heir +0.6 after ten
  rounds and +3.3 after 25; windows 1.4 / 4.1 / 6.3) **and is not worse for it**: it wins 23 of 42 small-map races,
  ends with 79% of its potential in the longest, and wins 55% at level potential at round 300 (forgot 56%). SSS cuts
  less often (2.3 leader cuts a race from round 395, ours 3.9) and its feeders die one step from the head. On big
  maps SSS has no stall.
- So a top team with the stall exists and is level with the two that have none. The number that sets us apart from
  all of them is how often our leader cuts and how soon it cuts again, which the candidate leaves alone.

### F. Earlier experiments

From `work/plan.md`:

- **`FEED_LOCAL`** (in the feeding phase a dragon dies next to any visible own head within 2-3 steps that shows
  twice its length): 70, 74 and 69 wins of 152 locally where the base won 76. Rejected. It lowers the bar for whom to
  die next to; candidate 5 raises it. It tells us that feeding local big dragons more does not help, which fits the
  10% the lineage gets of such pearls.
- **"Refuse to feed a leader much shorter than the max leader length ever heard"**: written down as the next step
  on 30 September after three local games in which 24 of 37, 18 of 25 and 29 of 42 feeds went to a non-top leader.
  Never run. It is close to the candidate's third change.
- **Regional leaders**: the team's own note: "Regions on the maze and portal maps elect local leaders because sonar
  is blocked, so feeding fragments." My count agrees: 39% of feeder deaths.
- **Rally** (`RALLY_FRESH`, far dragons walk to the leader): queued, no result in the log.

Nothing in the log contradicts candidate 5 and nothing tests it.

### G. Backfire

- **Regional leaders.** An age rule makes old news of a long dragon lose against fresh news of a shorter one. With
  the proposed 0.5 segments per round and news up to 25 rounds old, any dragon within 12 segments of the leader can
  win a region. Our longest and second longest are within 12 segments in 92%, 66%, 60% and 44% of the live bot's
  small-map races at rounds 400, 425, 450 and 475 (within 5 segments in 58%, 32%, 16%, 20%), and in 71%, 66%, 66%,
  52% on big maps (`y_c5d.py` part 2). The top teams' two longest are much farther apart (SSS's median gap is 18 to
  34 segments, ours 5 to 14). Every feeder death that moves from the longest to another big dragon costs the
  lineage 0.56 of each pearl, and that row is already 39%.
- **The "see it is long" test stops good deaths too.** As written (the feeder must have min(twice its length, 6)
  segments of its target in its view) it would stop the 12% it is meant to stop, and also **28% of today's deaths
  next to the true longest** (628 of 2,263; `y_w4b.py`, `y_c5d.py` part 4), because a feeder three cells in front
  of a head sees little of the body behind it. Those feeders would have to come closer first. A plain "at least 4
  segments in view" would do the same job at less cost; I did not count that variant.
- **Feeders that no longer die** are alive at round 500. The end-state numbers above say we have room for that
  (our leftovers near the leader are ordinary), but it is a cost of the third change, not a gain.
- **A leader that is followed by nobody for a while.** With the age rule as written the record flips between the
  heir and the old id from ping to ping (item H). A feeder that changes its mind every turn walks to neither. Today
  it at least walks to one of them.
- **We have more close wins than close losses.** On small maps 8 of our 29 race wins were won by 5 segments or
  fewer and only 2 of our 49 losses were lost by as little. A change that shifts the final longest by a few
  segments in both directions from game to game has more to lose there than to win.

### H. The code claim

Read: `observe()`, `hear_exact()`, `hear_sighting()`, `leader_priority()`, `expire_leader()`,
`plausible_report()`, `hear_sonar()`, `broadcast_leader()`, `pick_feed_target()`, `feed_len_ok()`, `ready_to_die()`,
`beside_visible_leader()`, `compute_drop_cells()`, `refresh_leader_zone()`, `escape_child_size()`, `is_leader()`.

- **A5's description of the record is right.** A report about the id held replaces it when it is as fresh or
  fresher, also when shorter. A report about another id wins on length alone; age only breaks ties. A sighting can
  raise the recorded length and never lowers it. A record is dropped 26 rounds after its last exact news. In the
  turn of a cut the leader first writes "my id, full length, this round" into its record, then splits, then sends
  that record, so the stale report is stamped with the round of the cut and lives for 25 rounds. Every team-mate
  repeats it on four rays each turn, and a dragon that had learned better takes it back, because for another id only
  the length counts.
- **Change 1 as written does not do what is claimed.** The proposed line is `mine = priority(record) -
  LEADER_AGE_COST * max(0, when - known_leader_round)`: the held record is marked down when the incoming report is
  fresher. Nothing marks the incoming report down when it is the older one. A dragon that has just taken "heir, 32,
  now" and then hears a team-mate repeat "old id, 34, round of the cut" compares 34 with 32 and switches back. Which
  of the two it holds when it decides whom to feed depends on the order of the pings in that turn. The rule has to
  price age on both sides (compare length minus cost times age for both reports), and it then also applies to the
  dragon's own length, which every dragon feeds into its record at the start of each turn: a dragon within 12
  segments of a leader it has not heard from directly for 25 rounds would make itself leader, stop being a feeder
  and get the leader's rules. That is the regional split of item G, inside the rule.
- **The cut itself** is as A5 says: `escape_child_size()` gives the child `length - 2` when the best move leads
  into a pocket of 4 cells or fewer that does not reach the own tail, or when there is no move at all; the queen is
  exempt from the early kind. Any dragon of 4 or more does it, not only the leader.
- **Change 2** (a dragon that sees the whole body of the id in its record corrects the length and remembers that
  correction) is sound and local. It fixes the stub for those who see it.
- **Change 3** is sound in direction; its threshold is too strict (item G).
- **Three things A5 does not say.** (a) The first half of `ready_to_die()` can hardly ever fire: the drop cells lie
  4 to 8 cells ahead of the leader's head and one to the side, and from there the head is outside the feeder's 7x7
  view, which that half requires (a portal in between aside). Our feeders die by the second half,
  `beside_visible_leader()`: head in view, within 3 cells counted straight, walls ignored. That is where the 5%
  deaths across a wall come from. (b) The heir is a new dragon with an empty record. It hears "old id, longer" like
  everybody else, so for up to 25 rounds it does not
  count itself the leader: it does not get the leader's fourfold pearl weight during feeding, and the pearl zone
  around its own stub applies to it. This is my inference from the code; it fits the heir that does not grow on big
  maps. (c) `sonar_enabled` is false on a map wider or taller than 128 cells; no known map is, but it is the one
  map-size condition in the record.
- No toggle exists for any of the three changes. No map-size condition is in them.

### I. The size

A5's own what-ifs recount within one or two games (growth after round 400 times 1.25 / 1.5 / 2: theirs 6 / 12 / 18
lost races that turn, mine 5 / 10 / 17; our final longest +5 / +10 / +15: theirs 4 / 11 / 20, mine 3 / 11 / 20). The
question is which factor to believe. A5 takes "a quarter to a half more growth" from the window contrast. Section
B says half of that contrast is the cut itself and the rest is a delay that is mostly made up. So I derived the size
from what can be counted as lost (`y_c5d.py` part 3). For each of our 102 lost races: the pearls of feeders that
died for a fresh stub or for a dragon under twice their length, what the final lineage got of them, and what it
would have got at the rate of deaths next to the true longest (66%); never above 0.9 of our final potential; the
enemy unchanged.

| Reading | lost races that turn (of 401 games) | live bot | mean gain per lost race |
|---|---|---|---|
| strict: every such pearl reaches the true longest; plus 1.2 segments for every leader cut after round 470 (feeders held back when the game ends) | 5 | 5 | 4.6 segments |
| middle: the stub pearls reach it, half of the others | 2 | 2 | 2.7 |
| cautious: half of the stub pearls reach it | 1 | 1 | 1.1 |
| for scale, not this candidate: the feeders that died across a wall die next to the longest instead | 2 | 2 | 0.9 |

The big-map stall of item B3 adds little to this: up to 5 segments per quiet cut, in races lost by a median of 44.
So: **strict 1 to 5 games of 401 (+0.25 to +1.25 points); with the usual halving for an enemy that answers and
feeders that do not find the leader, about 1 to 2.5 games (+0.2 to +0.6 points).** Against it stands a real chance
of harm from the age rule (regional leaders) and from the strict "see it" threshold, of about the same size. My
range: **-0.3 to +0.8 points, most likely +0.2 to +0.4**, against A5's +0.7 to +2.2.

### What is left of the claim

| | A5 | after the attacks |
|---|---|---|
| the counts | 5.0 against 10.8; 26% / 20%; 27 rounds | all reproduce |
| "feeding stalls for about 25 rounds after a cut" | from the window contrast and the pings of the earlier bot | true of the earlier bot; 15 rounds in today's live bot, 5 to 10 in the test builds; on small maps today's heir grows like Vibing++'s; the window after a cut grows 11.4 against 11.1 |
| "a quarter of our feeders die next to nothing" | 26% / 20% | 12% die for a stub or a short dragon (what the rule stops), 5% across a wall, 39% for another big dragon (the largest loss; not addressed) |
| the three changes | do what is claimed | the second yes; the third yes but it also stops 28% of the good deaths; the first not as written, and with the repair it invites regional leaders |
| games | strict 6 to 12, realistic 3 to 9 | strict 1 to 5, realistic 1 to 2.5 |
| points | +0.7 to +2.2, "a little over +1" | **-0.3 to +0.8, most likely +0.2 to +0.4** |
| what it leaves alone | the cut itself | and that is the larger number: our leader cuts 3.9 to 4.5 times a race from round 395 (others 2.3 to 2.7, forgot 4.2) and its heir cuts again within 10 rounds in 42% of cases |
