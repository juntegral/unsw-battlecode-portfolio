## 7. What I would change, what would show it is wrong, and what it is worth (questions h and g)

### 7.1 The one rule: the queen never ends a move inside the reach of an enemy head she can see, if a move outside it exists

**In words.** For the real queen (the lowest own id), at every length and on every map: a cell that an enemy head now in her view can move into this round is taken only when every other legal move is also in reach or leads into a closed space. Pearls, territory, exploration and the route home never outweigh it. If she already stands in reach, leaving it comes before everything, a pearl on the next cell included. If no one-step move is out of reach and she is 3 or longer, a two-step move that costs a segment and ends out of reach is taken.

**Why this one.** It is the largest single piece of the gap (42%), and it is the only kind for which the replay shows the alternative on the board: 104 deaths on a turn with a safe step, 90 of them with a safe step that had room behind it and crossed no portal (live bot: 68 and 59). One turn earlier nothing is wrong yet, so the fix has to act on that turn and nowhere else.

**Against the code** (`mybot2/main.cpp`; read, not run).

- Today the danger of a cell is one term of a sum. In `score_step()` a cell inside the queen's threat map costs `PENALTY_HEAD_RACE 450 x max(0.5, length / 4) x (0.5 + 0.5 x depth) x QUEEN_THREAT_MULT 1.0`. For a 2-long queen that is 225, 337 or 450 points for a cell 3, 2 or 1 steps from a 3-long's head, and the shortest queen pays least. On the other side of the sum a pearl on the next cell is worth `EAT_BONUS 300` plus a target bonus of up to 440; a cell that looks one cell too tight costs `PENALTY_TIGHT 400`.
- The threat map of the queen is built from the heads in view and from "ghosts", heads seen in the last 3 rounds, whose reach grows by one each round. A real head two steps away and a ghost from three rounds ago can put the same number on two cells (inference for game 1; not visible in a replay).
- Dragons of 8 or more already have what the queen lacks. In `pick_direction()`, the block `if (length >= LONG_SAFE_MIN_LENGTH)` gives each candidate cell a level from its exposure and subtracts `LONG_THREAT_VETO` (1e6) per level below the best: the least exposed cell wins whatever the rest of the score says, and `cornered` turns on the paid `sprint_escape`. A queen of 2 or 3 never enters this block.
- On maps of 600 cells or fewer `is_queen()` is false, so she uses the small dragons' threat map (only the cell next to a small enemy head) and, as a trader, no threat penalty at all.

The change, precisely:

```
// pick_direction(), after apply_route(...), before the loop that picks the best score
if (real_queen()) {                      // lowest id: every length, every map size
    // reach_now[c]: can a head in enemy_heads (visible THIS round; no ghosts) move into c this round?
    //   P = visible_parts(id) + 1       (one segment may be outside her view), at least 2
    //   budget = (P + 3) / 4 + P - 2    (free steps plus paid steps)
    //   BFS from that head over cells with enter_time == 0 and over her own tail cell;
    //   stepping onto a pearl adds 1 to the budget; mark every cell reached within the budget
    bool safe = false;
    for k in 0..3:
        if (scored[k] && scores[k] > SCORE_REJECT * 0.5 && !reach_now[dests[k]] && !closed[k]) safe = true;
    if (safe)
        for k in 0..3:
            if (scored[k] && (reach_now[dests[k]] || closed[k])) scores[k] -= LONG_THREAT_VETO;
    cornered = !safe;                    // lets the existing sprint_escape(path, true) look for a paid way out
}
```

Four places must obey the same test or it leaks: `extend_stride()` must not add a step onto a `reach_now` cell and must stop on a cell all of whose neighbours were in her view at the start of the turn (a long queen that takes six free steps ends at the edge of what she saw: games 20 and 22); `split_child_size()` must return 0 for the real queen while an enemy head is in her view (`QUEEN_SPLIT_CLEAR` is 0 today; games 11 and 19; 16 of our 251 rammed queens had split with an enemy head in view within their last three turns); `is_trader()` must be false for the real queen on every map, so that the cell of an enemy head is never a goal (10 own rams with a free safe cell); and the call `cornered && (is_big() || is_queen()) && sprint_escape(path, true)` in `act()` must test `real_queen()`.

**What it would have prevented, and what it would not.**

| Kind of death | cases (live bot) | touched by the rule |
|---|---|---|
| rammed: stepped in | 66 (40) | yes: 56 (35) had a roomy safe step; in 10 (5) the only safe step was a pocket |
| rammed: stayed in | 38 (28) | yes: 36 (26) had a roomy safe step |
| rammed: cornered, where a paid two-step move was safe | 35 (21) | partly, through the paid escape |
| rammed: cornered, the rest | 81 (53) | no |
| rammed: unseen | 31 (23) | no; 6 of them partly, through the stride limit (queens of 17 to 48 that had just moved 3 to 6 steps) |
| boxed in (all sub-kinds) | 91 (67) | no |
| own ram with a free safe cell | 10 (8) | yes, if the queen never trades |
| own ram, boxed in | 9 (8) | no |

**What a safe step is worth, measured on the turns on which she did take it** [`d_after.py`, `after.txt`]. In the same two close situations, our queen's fate by what she did:

| Situation at the start of her turn | she ended | turns | rammed that round | rammed within 3 rounds | rammed within 10 rounds |
|---|---|---|---|---|---|
| inside a visible reach, a safe step exists | outside reach | 290 | 0.3% | 7% | 24% |
| | in reach | 68 | 56% | 62% | 65% |
| outside reach, a small enemy head within 4 steps, a safe step exists | outside reach | 3,887 | 0.1% | 8% | 19% |
| | in reach | 69 | 83% | 84% | 87% |

After the safe step a top-three queen is rammed within 10 rounds in 24% and 15% of the same situations, so there our queen is already like them. The rule turns a death of 65 to 87% into one of 19 to 24%: about three quarters of the 104 queens are alive ten rounds later, and the rest are cornered in the same encounter.

**What it costs.** She ate a pearl on 21 of the 149 turns that ended in reach by choice, in 401 games: one pearl per 19 games. No split is lost. The CPU cost is one small search per visible enemy head on the queen's turn only.

**What would show it is wrong.** On the next ladder or smoke games against test4 and WHQ, with `d_class.py` and `d_expo.py` run on the new replays:

1. Turns that end in reach although a safe step existed must fall from 2.6 per 1,000 queen-rounds to under 0.8 (the top three: 0.4 to 0.8). If they do not, the code does not do what the rule says; look for the path that bypasses it (stride, split, portal fallback, trade).
2. "Stepped in" plus "stayed in" must fall from 26% of games to under 8%.
3. Queen deaths per 1,000 queen-rounds should fall from about 6.4 to about 5.1, and the share of queens alive at round 300 should rise from 15% to about 22%. If 1 and 2 hold and the death rate does not move, the deaths have moved to "cornered" (cornered turns would rise from 2.8 to above 4 per 1,000 queen-rounds): then the rule only delays and the second rule below is the one that matters.
4. Natural pearls eaten by the queen per 100 rounds in rounds 0 to 99 should stay within 10% of 4.7 and 3.3.

Wins are not a test of this rule. Its own worth is 2 to 7 games in 401 (readings 3 and 2 of question g), far inside the noise of a 28-game smoke pair. It should be judged on points 1 to 3 and shipped together with the repairs of 7.3.

**The closest thing the team tried, and why the ladder may differ.** The closest are "never step into reach" as tried locally: `QUEEN_THREAT_MULT` 3 and 6, `QUEEN_GUARD_RADIUS` 3 and the lethal veto inside the `QUEEN_BRAIN` planner (`work/plan.md`: "Threat x3/x6 and guard 3 do not cut rams (rammed 9-12)" on 24 local games; the planner lost games by paying segments and boxing itself in). Three reasons the ladder result can differ:

- The multipliers are still sums. A 2-long queen at x6 pays 1,350 to 2,700 for a threatened cell, as much as three to seven cells of `PENALTY_TIGHT`, so a safe cell that looks a little cramped still loses. The rule here is an order of preference, not a bigger number.
- The local opponents are our own older bots. Our bot makes about one multi-step ram per game in rounds 0 to 149 on large maps; its ladder opponents make 13.5 (`findings.md` 6c). 48 of the 66 "stepped in" kills on the ladder were moves of 2 or more steps, 25 of 3 or more. A sparring bot that does not charge cannot reward a queen for staying out of charge range.
- Locally the queen is alive at the end in 11 to 20% of games whatever is switched on, because she dies boxed in and by her own rams there, which this rule does not touch. The same will be true on the ladder for those kinds; that is what 7.3 is for.

It may also not differ: the top three, who almost never end a turn in reach by choice, are still cornered 2.9 times per 1,000 queen-rounds and die of it. The rule buys the difference between 6.5 and about 5, not the difference between 6.5 and 2.7.

### 7.2 Second-best rule: after the hand-over the queen stays where her team is

**In words.** Once the team has 8 or more dragons, the real queen keeps within about 8 path steps of her start cell, or failing that within sight of at least one own head, and prefers a cell with three or four open sides to one with one or two. (Eight dragons is where every team's queen has halved her eating: section 5c.) In code this is the existing `QG_HOME_RADIUS` / `QG_HOME_PENALTY` term of `score_step()`, switched by unit count instead of `queen_guard()`, with a penalty per cell large enough to beat the far-target terms.

**Evidence.** It is correlational, which is why it is second. A short queen of ours is rammed 1.8 times per 1,000 rounds within 5 cells of her start, 3.0 at 6 to 10, 5.5 at 11 to 15 and 8 beyond; she spends 44% of her rounds beyond 10 cells. 157 of the 228 rams of our short queens began more than 10 cells out. With no own head within 6 steps she is rammed 9.7 times per 1,000 rounds (rounds 50 to 149), with three or more 2.2, and the same slope holds for all five groups. test4's queen, which walks four cells at one spot from round 1, dies 3.1 times per 1,000 rounds against the top three's hunters. If our queen had spent her far rounds at her near rate, about 100 of those 157 rams would not have happened; that is an upper estimate, because where the enemy overruns our home the near rate rises too (games 12 and 18).

**What it would not touch.** Boxed-in deaths; they would rise if she is kept in a crowd, unless the cut is repaired and team-mates stop stepping onto her last exit (20 nose-to-nose deaths).

**Cost.** Small after the hand-over: with 8 or more dragons she eats 2.9 natural pearls per 100 rounds, about 1.5 pearls per 50 rounds.

**What would show it is wrong.** Her ram rate within 10 cells of her start rising above 4 per 1,000 rounds (hunters now find her there), her boxed-in rate rising above 2 per 1,000 rounds, or units at round 100 falling.

**Closest tried.** The safe zone (card #16) and `QG_HOME_RADIUS`, tried locally without a gain in survival. Locally nobody hunts her, so being far from home costs nothing there; on the ladder it costs a factor of four.

### 7.3 Two repairs that are not rules about where she goes

**Repair 1: a boxed-in queen sheds, she never cuts.** In `escape_child_size()`, when no cell is enterable, the child gets `length - 2` and the queen keeps 2. For the real queen return 2 (the child is the two tail segments) and repeat next round. Evidence [`d_cut.py`, `cut.txt`; `d_shed.py`, `shed.txt`]: our 10 late cuts of a queen of 6 or more left her alive five rounds later in 3 cases (mean length 25 before, 2 after); forgot's 207 shedding episodes of a boxed-in queen of 6 or more left her alive in 184 (88%), 21 long on average after 5.6 rounds. On Slithery Fight it removes the round-3 death (10 of 29 games) and leaves her 3 long with eleven children instead of 2 long with one. Card #25 (`QUEEN_WAIT`) could not fire for this reason: by the time it looks she has already been cut to 2. It would have saved a 57-long queen against a 3-long one (game 29).

**Repair 2: the queen-only bans hold on every map.** Three things our queen may not do with the rules on are what kills her with the rules off: portal steps (27 of 44 games; the Portals pattern, 11 deaths), trades (10 own rams with a free safe cell) and walking down dead-end corridors to eat (21 of the 30 terrain deaths are on small maps). The 600-cell gate was set because protecting the queen cost local games on small maps; these three bans protect nothing, they only stop her from spending herself. The team's own record has `QUEEN_PORTAL_ALL` rejected on one bad Stripes result of 8 games; on the ladder the live bot's queen on those six maps dies at 10.7 per 1,000 rounds and is alive at the end in 2 of 100 games. For the terrain part the test is "tree cell": the queen does not step onto a cell from which the map she knows has no way round, whatever lies on it.

### 7.4 What it is worth

The table is in section 5g. In short, for all 401 games (27.9% won):

- The one rule alone: 26 games under the strict reading, 7.4 if she then lives like a top-three queen, 2.4 if every other kind of death stays at our rate. Plus 0.6 to 1.9 points of win rate.
- All four families she controls herself (the rule, both repairs, and the team-mate deaths): 59 / 18.3 / 8.7 games. Plus 2 to 5 points.
- All 362 deaths: 102 / 30.4 / 8.2 games. The strict 25 points are not on offer.
- The live bot alone gives the same points: +5.1 / +1.5 / +0.5 for the rule, +13.5 / +4.3 / +2.0 for the four families, +25.1 / +7.6 / +2.0 for all.
- Outside this count: three losses with her queen alive in which our fed queen was already longer when she died than hers at the end (57 against 3, 28 against 5, 27 against 19). Repair 1 and the stride limit of the rule cover the first two.

The reason the numbers are small is in section 5b: a queen that is no longer rammed on this turn is cornered a few turns or a hundred rounds later, because test4 and WHQ ram an exposed queen 77% of the time and reach her 5 times per 1,000 rounds. The same table says where the larger number is. Their queens are exposed to us just as often, and we take 16% of those rams. That is the lead's finding 3 in `findings.md` seen from the other side, and it is not a queen rule.
