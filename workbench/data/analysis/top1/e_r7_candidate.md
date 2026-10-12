## 7. Candidate 5: one leader, known to all

Written in the seven items of `hypotheses.md`. It is a candidate hypothesis, not a result: nothing here was played.

### 1. The claim

**Once the team feeds a leader, every dragon follows the same one, and follows it through its cuts: when the leader
hands its length to a new dragon, that dragon is the leader for the whole team within a few rounds. And a dragon
gives its life only within reach of a leader that it can see is long.**

In our bot today the first half fails for about 25 rounds after every cut and the second half fails for a quarter of
our deaths by choice. Two things change, both in how a dragon keeps and uses its one record of "the leader":

- **Fresher news of a nearly-as-long dragon replaces older news of a longer one.** Today only length counts, so the
  last report of the old leader (longer by the 2 segments of the stub, up to 25 rounds old) beats every report of
  its heir until it expires.
- **What a dragon sees beats what it remembers.** Today a dragon that stands next to the id in its record dies for
  it if the recorded length is twice its own, even when the dragon in front of it is a 2-long stub or a 5-long that
  was once believed longer.

The rule names no map and no map size, moves no clock, and leaves the leader's cuts, the start of feeding and the
pearl zone as they are.

### 2. Evidence

**What the code does** (read in `mybot2/main.cpp`; line numbers of the copy read on 5 October; not seen in replays).

- Every dragon holds one leader record: `known_leader_id / _len / _round / _pos / _dir`. Each turn it first feeds
  itself into the record (`hear_exact(ct.get_id(), length, round, ...)`, line 1311), then every ping it hears
  (`hear_sonar()` -> `hear_exact()`), then every own head in its 7 x 7 view (`hear_sighting()`, line 1394), and at the
  end of its turn it sends the record on four rays (`broadcast_leader()`, line 1694). A record older than
  `SONAR_STALE` 25 rounds is dropped (`expire_leader()`, line 1600) and reports older than that are not accepted
  (`plausible_report()`).
- `hear_exact()` (line 1609): a report about the id already held replaces it when it is as fresh or fresher, also
  when shorter. A report about another id is taken only when its `leader_priority()` is higher, and that priority is
  the length (plus 1,000 for the queen in a queen game). The age of the two reports is used only to break a tie.
- `hear_sighting()` (line 1645): for the id already held it sets the position and
  `known_leader_len = max(known_leader_len, visible)`; `visible` is the number of segments of that dragon inside the
  view, so a sighting can raise the recorded length and never lower it, and it does not refresh the round. Another
  dragon in view replaces the record only if its visible segments alone exceed the recorded length.
- A cut (`escape_child_size()`, line 1002: the child gets `length - 2`): the stub keeps the old id and from its next
  turn reports itself as 2 long; dragons that hear the stub directly learn it. Everybody else holds "old id, full
  length" until 25 rounds after the last exact news, repeats it on four rays every turn, and so hands it back to any
  dragon that had dropped it: a 12-long local dragon in a record loses to "old id, 34 long, 20 rounds old". The heir
  reports "new id, 32 long, now" and loses the same comparison.
- Whom a dragon feeds: `pick_feed_target()` (line 1878) needs the feeding phase, a record of another id,
  `feed_len_ok()` (own length x `FEED_LEN_RATIO` 2 <= the recorded length) and the recorded place within
  `FEEDER_APPROACH` 15 cells. `ready_to_die()` then needs no enemy head within 4 cells and either a drop cell, or
  `beside_visible_leader()` (line 1916): the head of the recorded ID in view within `FEEDER_DIE_DIST` 3 cells. It is
  the id that must be in view, not a long dragon. The bot then returns without an order (`act()`, line 526, logged
  "FEEDDIE").
- The same record drives the pearl zone (`refresh_leader_zone()`, line 1921) and "I am the leader" (`is_leader()`).

So after a cut the code predicts: feeders near the stub may still die for it; feeders near the heir may not die for
it; and the zone moves to the stub. All three are in the replays.

**What our replays show** (measured; sections 2 and 4).

| | number | where |
|---|---|---|
| rounds after a leader cut until half of our dragons name the new longest (median; quartiles) | 27 (17 to 36-41), 388 cuts | `e_bel.py`, 78 games with readable pings |
| in between, the id most of them name is dead / alive but under half the true longest | 36-44% / 28-34% of samples | `e_bel.py` |
| rounds 400-494: samples in which under a quarter of our dragons name the true longest | 187 of 347 | `e_churn.py` |
| growth of the longest over the next 5 rounds: under a quarter name it / a quarter to a half / a half to three quarters / more | +0.42 / +1.85 / +1.51 / +2.00 | `e_churn.py` |
| ... the same against test4 / WHQ / others (under a quarter; otherwise) | 0.40; 1.45 / 0.35; 2.41 / 0.46; 1.63 | `e_out/opp.txt` |
| dragons that could feed the true longest by our rules, small maps, rounds 400-424 / 425-449 / 450-474 | 5.2 / 3.0 / 1.5; without the belief test 9.3 / 5.2 / 4.1 | `e_bel.py` |
| growth of the longest per 25-round window from round 400 (10+ other dragons): a cut in it or just before / none | 5.0 (291 windows) / 10.8 (91) | `e_churn.py` |
| ... live bot / test builds | 4.5; 11.4 / 6.1; 9.3 | |
| ... against test4 / WHQ / everybody else | 4.9; 11.4 / 5.5; 10.9 / 3.7; 9.6 | |
| ... every run of the live bot separately (ladder 4 October, stride, passage2, qh31) | 4.3; 11.9 / 3.8; 10.4 / 5.1; 9.2 / 5.3; 14.1 | `e_out/era.txt` |
| our deaths by choice in races, rounds 300-499, with no own dragon twice as long within 8 steps | 26% (small maps), 20% (big) | `e_dist.py` |
| the final lineage's share of the pearls: death next to the longest / next to nothing | 70% / 13% (small), 61% / 7% (big) | `e_dist.py` |
| all our `noaction` deaths in races: next to the true longest / another dragon of 8+ / a dragon under 8 / nothing | 42% / 23% / 20% / 15% of 5,559 | `e_bel.py` |

**Us against the others, like for like** (measured; "The same test for every team", section 2; races, rounds 300-499).

| | meow | our opponents | test4 | WHQ | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|---|
| deaths by choice next to no bigger dragon, small / big maps | **26% / 20%** | 15% / 11% | 20% / 17% | 12% / 9% | 8% / 5% | 10% / 6% | 14% / 10% |
| next to the team's longest | 42% / 30% | 42% / 15% | 41% / 13% | 45% / 16% | 51% / 26% | 73% / 52% | 35% / 21% |
| pearls eaten by the final lineage | 36% / 27% (test builds 45% / 24%) | 39% / 16% | 36% / 17% | 40% / 15% | 47% / 26% | 41% / 31% | 46% / 29% |
| growth per 25-round window with a cut / without, small maps | 4.0 / 13.4 (test builds 9.9 / 9.7) | 6.8 / 7.9 | 8.5 / 7.6 | 5.7 / 8.3 | 8.7 / 5.9 | 2.4 / 6.2 | 8.0 / 5.8 |
| ... big maps | 4.8 / 8.6 | 5.5 / 6.3 | 4.8 / 7.7 | 6.2 / 6.7 | 3.8 / 4.6 | 2.8 / 6.6 | 4.5 / 8.2 |
| cuts of the final lineage from round 400, per race | 2.7 | 2.0 | 2.1 | 1.7 | 3.3 | 1.6 | 2.0 |

Read honestly: per pearl we already do as well as test4 and WHQ, and the leader is cut about as often in every team.
What is ours alone is the first row. The window contrast is ours and SSS's on small maps (and several teams' on big
maps); forgot, WHQ and Vibing++ grow as fast around a cut as away from it, so a team whose feeders follow the new id
at once exists. Whether they do it by a better record or by something else cannot be seen.

**Winners against losers of level races** (measured; `e_wl.py`, `e_out/wl.txt`; own potential / enemy potential at
round 350 between 0.8 and 1.25; medians, means for the last five columns).

| | sides | leader feeding starts | longest at 350 / 400 / 450 / end | share of potential in the longest at the end | units at the end | cuts of the final lineage from round 400: all / with a free cell | deaths by choice, rounds 300-499 | next to the longest / next to nothing | pearls to the final lineage |
|---|---|---|---|---|---|---|---|---|---|
| meow, won | 12 | 402 | 11 / 14.5 / 27.5 / 48.5 | 0.79 | 5 | 3.6 / 2.2 | 52 | 40% / 20% | 39% |
| meow, lost | 12 | 403 | 13 / 13 / **31 / 30** | 0.62 | 12.5 | **6.6 / 4.1** | 57 | 38% / 19% | 36% |
| our opponents, won | 12 | 308 | 12.5 / 26.5 / 45.5 / 62 | 0.84 | 2.5 | 2.9 / 1.3 | 64 | 45% / 8% | 42% |
| our opponents, lost | 12 | 358 | 10.5 / 15.5 / 37.5 / 30 | 0.74 | 4 | 1.9 / 0.9 | 46 | 39% / 13% | 28% |
| top three, won | 103 | 306.5 | 25 / 38 / 53 / 69 | 0.50 | 18 | 2.4 / 1.2 | 70 | 45% / 7% | 38% |
| top three, lost | 75 | 306.5 | 26 / 35 / 43 / 38 | 0.43 | 14 | 2.2 / 1.2 | 59 | 42% / 7% | 23% |

Our level races are decided in the last 50 rounds, and not by the clock: winners and losers both start at round
402-403; at round 450 the losers are ahead (31 against 27.5); then the winners add 21 and the losers lose 1. The
losers' final lineage is cut 6.6 times from round 400 against 3.6, and they end with 12.5 units against 5. For the
top three the same split shows as "who ate the pearls": the losers' final lineage got 23% of them, the winners' 38%,
with the same start and the same number of cuts. Twelve games a side for ours: the difference in cuts (6.6 against
3.6) is large, the rest is within what twelve games can give by chance.

**Games that show it and its absence** (section 4).

- Absent. 1027971 (Portals, against WHQ), rounds 400-490: the leader cuts at round 400 with 11 feeders ready; at
  rounds 410 and 420 nobody names the true longest and 11-12 of 13-14 name the 2-long stub; again from round 450 to
  474 (a dead id, 25 long). We lead 23 to 21 at round 440 and lose 19 to 30. 1027819 (Maze, against test4), rounds
  421-453: no feeder dies next to our 31-34-long leader for 32 rounds; five die in rounds 453-454, their last ping
  naming the dead `#606`, 34 long, 25 rounds old. Same game, round 401: the first feeder dies four steps from a
  9-long with a ping naming `#499`, 15 long, which is 2 long. 1045374 (weakhold, against WHQ), rounds 406-499: 21 of
  28 deaths by choice next to no bigger dragon; level at round 450 (24 to 25), lost 25 to 31.
- Shown. 1023828 (Maze, against forgot, won 92 to 84 with less potential): `#265` keeps its id from round 325 to
  489; 67-88% of our dragons name it at rounds 325-400; all 30 feeders that die next to a bigger dragon in rounds
  400-449 die next to it; 25 to 77 in 50 rounds. 1046530 (SSS against test4): `#770` one id from round 346 to the
  end, 48 of 51 deaths by choice next to it, 53 of 62 pearls eaten by it. 1044512 (WHQ against us): `#302` one id
  from round 351 to 431, 44 of 60 deaths by choice next to it.

**The earlier trials** (`work/plan.md`; section 5g). None tried this. The team wrote the diagnosis twice ("belief
goes stale"; "feeds to a non-top believed leader: 24/37, 18/25, 29/42"; next step "refuse to feed a leader much
shorter than the max leader length ever heard") and then tested clocks: feeding from round 330 or 300 (70 and 69 of
152 locally against 76; online 24 of 60 against 23), `FEED_EARLY_ROUND` (73, 74), `FEED_LOCAL` (dying next to any
visible dragon twice as long: 70, 74, 69 of 152 against 76), the leader round at 200 (19 of 60 online against 23).
`FEED_LOCAL` is the nearest relative of this candidate's second half and came out flat to slightly negative
locally; it differs in the point that matters (any big dragon, not the leader), and a local mirror on a rich board
is a weak judge of the last 100 rounds (the log: "top 39 at r400, total 220").

### 3. Mechanism

Under the longest rule the final length is potential times completeness. The rule adds nothing to potential. It
raises completeness in the phase in which our races are decided: each cut (2.7 a race from round 400) now costs 2
segments plus about 25 rounds in which the dragons that could feed the leader do not: in rounds 400-424 on small
maps 9.3 dragons are close and short enough and 5.2 pass the belief test; in rounds 450-474 4.1 and 1.5. With the
record following the heir those dragons die next to it instead of waiting or dying next to the stub; with the
"see it is long" test the quarter of deaths that now drop pearls next to nothing (13% to the leader) is spent next
to the leader (70%) or not spent. The pearls that reach the leader are worth one segment each; the same pearls
eaten by a small team-mate are worth half again later, if it ever feeds.

### 4. Expected effect

**(a) Games.** A record rule cannot be re-scored game by game from replays. Three counts bound it (`e_p.py`,
`e_margin.py`, `e_cutcost.py`; our 102 lost races, the enemy unchanged):

| what-if | lost races that turn | live bot (69 lost) | against test4 / WHQ / others (32 / 61 / 9 lost) |
|---|---|---|---|
| the leader's growth after round 400 times 1.25 / 1.5 / 2, never above 0.9 of our final potential, only races with a cut after round 395 | 6 / 12 / 18 | 5 / 10 / 14 | 2, 3, 5 / 3, 7, 11 / 1, 2, 2 |
| our final longest +5 / +10 / +15 segments | 4 / 11 / 20 | | |
| for scale, not this rule's effect: the segments left in the lineage's own cuts from round 400 given back | 10 | 9 | 6 / 4 / 0 |

The measured contrast is a factor 2.2 between windows with and without a cut, and three quarters of our windows
after round 400 are "with a cut" (291 of 382). I take a quarter to a half more growth as the strict range, because
feeders are finite and part of the contrast is selection: **strict 6 to 12 games of 401 (5 to 10 of the live bot's
275)**. Realistic: between half of the low end and three quarters of the high end survive a real opponent and the
cases in which the feeders were missing for other reasons: **3 to 9 games; +0.7 to +2.2 points on our 27.9%, most
likely a little over +1** (live bot: 2.5 to 7.5 games, +0.9 to +2.7 on 28.0%). It cannot be much more: 106 of our
143 races start under 0.8 of the enemy's potential and are mostly lost before the leader matters.

**(b) Where it acts.** Round-500 games with both queens dead (143 of 401), from the first cut after feeding starts:
the last 100 rounds on small maps, the last 300 on big maps when the 56-unit rule fires. Nothing changes before
feeding, in wipe-outs, or while a queen is fed (her id never changes hands by a cut with a free cell, and her record
carries the 1,000 bonus).

**(c) Against each opponent.** The window contrast and the belief contrast hold against test4, against WHQ and
against everybody else separately (table above). The what-if turns 2-5 of 32 lost races against test4 and 3-11 of
61 against WHQ. At level potential at round 350 we win 4 of 9 against test4 and 6 of 12 against WHQ today (SSS 7 of
9 against test4); counts this small have an 80% range of about plus or minus 20 points.

**(d) With the four existing candidates.**

- **Candidate 1 (take the queen)** makes more races: a dead enemy queen with ours dead too is a longest-dragon game.
  Sub-session B scored those new races with our present win rates per band. This rule raises those rates, so the two
  multiply rather than overlap; candidate 1 stays first.
- **Candidate 2 (our queen is never spent)** makes fewer races and more queen games. No shared code. The queen is
  already exempt from the early cut (`is_queen() && !no_move` in `escape_child_size()`), which is the reason her
  feeding does not show this problem.
- **Candidate 3 (no leader before its time)** moves the big-map switch from round 150 to 300. This read supports it
  from the other side: the zone gives the leader nothing on either map class (12% of the pearls left for it on small
  maps, 7-17% on big ones; the leader's natural intake does not rise at the switch), while the team's intake falls
  by a quarter and a third. And it answers the red team's worry that our big-map wins, all won on the longest
  dragon, might need the early leader: in the four read (section 4, games 19-22) the leader was built by feeding
  from round 201-204 with 56-60 units (three games) or after round 400 (one), not by the zone; in the median big-map
  race our longest is 10 at round 200 and 14 at round 400. One condition, which B already named: when the switch
  moves to 300 the 56-unit feeding rule must still give the fed dragon the leader's no-split rule, or the team
  feeds a dragon that splits. The two candidates touch different lines and can ride together; I would still test
  them one at a time.
- **Candidate 4 (do not give way at contact)** is independent. It leaves fewer units late, and small teams complete
  better (0.75-0.83 of potential in the longest with under 20 units at round 400 against 0.56-0.60 with 30 or more,
  small maps).

### 5. What changes in `mybot2/main.cpp`

No toggle exists for any of it. Three places, all in the leader record and the feeder test:

1. **`hear_exact()` (and the comparison in `hear_sighting()`): age counts.** When a report about another id is
   compared with the record, the record's length is reduced by a constant per round of age difference, for instance
   `mine = leader_priority(known_leader_id, known_leader_len) - LEADER_AGE_COST * max(0, when - known_leader_round)`
   with `LEADER_AGE_COST` about 0.5: an heir that is 2 shorter is taken four rounds after the cut instead of 25,
   and a living leader, whose own pings keep its record fresh around it, is not displaced. New constant; one line in
   each function.
2. **`hear_sighting()`: seeing the whole dragon corrects the record.** When the id in the record is in view with
   fewer segments than recorded and its whole body is inside the view (a helper: every visible segment's follower is
   visible or it is the tail, as `extend_trail_from_vision()` does for the own body), set `known_leader_len =
   visible` and `known_leader_round = round`. The corrected record then spreads by the existing same-id branch of
   `hear_exact()`. To stop the old report coming back from a dragon that has not heard, keep the id and round of the
   last correction (two ints) and ignore older reports of that id.
3. **`ready_to_die()` / `beside_visible_leader()`: the feeder must see length.** Next to `leader_in_vision()` add
   `visible_parts(known_leader_id) >= min(FEED_LEN_RATIO * length, FEED_SEE_MIN)` with `FEED_SEE_MIN` about 6: a
   2-3-long feeder must count 4-6 segments of the dragon it dies for. A stub fails, a real leader three cells away
   does not. `feed_len_ok()` stays as it is (the queen bonus path included).

Not part of the candidate, listed because the same read gives each a number (each would need its own test, and the
first depends on the candidate: a dragon cannot merge into a leader it does not know):

- **Whole dragons feed the leader at the end** (`FEED_LEN_RATIO` 2 -> 1 from some late round on, for dragons that
  can reach it in time). This is the one thing test4 and WHQ do in the race that we do not: 26-29 pearls a race from
  dragons of 5+ on small maps against our 5-9; 1.3-1.5 dragons of 8+ given to the leader in the last 50 rounds
  against our 0.3; their final lineage eats 57-64% of those pearls (section 2, `e_merge.py`). The winner did it in 5
  of the 14 losses read. Under the longest rule it always pays if the pearls are eaten (L1 + half of L2 is more
  than L1); what it costs is the second dragon as a reserve if the leader is rammed afterwards (3.8 times per 1,000
  rounds for a leader of 15-24 after round 400). In 38 of our 102 lost races our longest plus half of all the rest
  beats the enemy's longest; +5 / +10 segments turn 4 / 11. The top three do not do this on small maps (0.2-0.6 a
  race), so it is a rule read off our opponents, not off the protagonists.
- `LEADER_PEARL_RADIUS` 9 -> 0 (no pearl zone on any map): the leader loses about one pearl per 50 rounds, the team
  gains 5 (small maps) to 27 (big) per 50 rounds; three of the 14 losses read (weakhold) are zone starvation.
- `FEEDER_DIE_DIST` 3 -> 1 or 2: the dragon fed eats 90% of the pearls dropped one step away, 78% at two, 74% at three.
- `RALLY_FRESH` 0 -> 15-25: dragons beyond 15 cells never come; our level losers end with 12.5 units, the winners 5.

### 6. What would show it is wrong

Countable on 20-60 new replays (about a third are races) with the scripts named; today's value -> what the rule
must reach:

1. Growth of the longest per 25-round window from round 400, windows with a leader cut against windows without
   (`e_churn.py`): 5.0 against 10.8 -> within 2 of each other. **If the two stay apart, the record was not the
   cause and the rule is worth nothing.**
2. Deaths by choice in races, rounds 300-499, with no own dragon twice as long within 8 steps (`e_dist.py`): 26% on
   small maps, 20% on big -> under 12%. Next to the team's longest: 42% / 30% -> over 55% / 40%.
3. The final lineage's share of those pearls (`e_dist.py`): 36% (live bot, small maps) -> 45% or more.
4. Share of potential in the longest at the end, small maps (`e_cdist.py`): 0.65 -> 0.75; units at the end 7 -> 5 or
   fewer.
5. If the test build's pings can be read (they are sealed; the team has the key, or the bot can log its record):
   rounds until half the team names the new longest after a cut (`e_bel.py`): 27 -> under 8; samples in rounds
   400-494 with under a quarter naming the true longest: 54% -> under 20%.
6. Must not get worse: deaths by choice next to another dragon twice as long that is not the longest (16% small,
   36-41% big; this is where an age cost that is too high would show, as regional leaders); the longest of 15+ rammed
   per 1,000 rounds (3.8-4.6 after round 300); the enemy's share of our feeders' pearls (4.7% small, 10.5% big).

A win test is out of reach: +1.5 points on 27.9% needs about 14,000 games a side for four chances in five (+1
point: 32,000); inside races alone (29% to 34%) about 1,300 races a side, which is some 3,800 games.

### 7. Known risks

- **The comparison with other teams does not carry it.** Per pearl we convert as well as test4 and WHQ today; the
  gain is inferred from contrasts inside our own games (windows with and without a cut, samples with and without a
  shared belief). Those are correlations: a leader cuts when it is crowded, and a crowd may fail to feed for other
  reasons. SSS shows the same halving around a cut and wins 58% of its races.
- **The belief numbers are from 78 games of the earlier live bot**, the only ones whose pings can be read. The
  record code in today's source is as described and the window contrast is in every later live run, but nobody has
  seen a belief in a later build.
- **The test builds do not show the contrast on small maps** (9.9 with a cut in 42 windows, 9.7 without in 13) and
  end at 0.71 of potential where the live bot ends at 0.65. Small counts; if it is real, part of the gain is already
  there.
- **An age cost can split the team**: far dragons hold old news of the true leader and would switch to a shorter
  dragon nearby. The team has seen that failure ("regions elect local leaders"). Number 6 above watches it; the
  constant is the knob.
- **Fewer blind deaths are fewer deaths.** A dragon that no longer dies next to nothing is still alive at round
  500 unless it finds the leader, and we do not bring far dragons in (`RALLY_FRESH 0`).
- **The ceiling.** 48 of our 143 races start under half the enemy's potential (none won) and 58 at 0.5-0.8 (20 won,
  the same rate as the top three from there). A race rule works on what is left.
- **Counts.** The level bands hold 9 to 24 of our games; winners against losers 12 a side. 313 of our 401 games are
  against two opponents; what is said above holds against each, with fewer games each.
- **Big maps.** Everybody ends there with 39-49% of potential in the longest and several leaders; our leader is
  rammed in one race in two. The rule acts longer there (feeding from round 200) but on a mechanism that is
  scattered for every team.
