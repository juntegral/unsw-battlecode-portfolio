## Ranking

Expected points are the realistic ranges of each candidate's item 4, on our 27.9% against teams rated 2000 or more.
"Strict" is added where a game-by-game count exists. All four name a behaviour number that can be counted on 20 to 60
new replays; none can be judged by wins in a 30:30 test.

| Candidate | Strongest evidence in one line | Expected points | How sure | How hard to build | How testable | Depends on |
|---|---|---|---|---|---|---|
| **1. Take the queen** | All three top teams ram a queen in view and reach every time with small dragons (two of them with any dragon); we take 22% of 446 such turns, our opponents 86% of theirs on our queen; 25 of our losses had such a turn and a living enemy queen at the end | **+1.5 to +3.2**, most likely +1.5 to +2 (strict 6-13 games of 401, 7 by the count I trust most) | Behaviour: very sure, the code path exists and a narrower build reached 8 of 9. Wins: fairly sure of the low end | One constant (`QUEEN_HUNT`, exists) and one condition | 60 + 60 games give 50 chances a side: 22% must become 90% | Nothing |
| **2. Our queen is never spent** | In 104 of our 401 games (26%; top three 6-8%) our queen died on a turn with a safe step on the board; when she takes the safe step she is rammed within ten rounds in 19-24% of cases, otherwise 65-87% | **+0.9 to +2.8** (strict 34 games) | Behaviour: fairly sure. Value: wide, it hangs on whether a saved queen then survives | One new block in `pick_direction()`, seven conditions, one constant | 60 games give 60 queen deaths: 2.6 turns in reach by choice per 1,000 queen-rounds must fall under 0.8 | Nothing; worth more with 1 (+1.8 wins) |
| **3. No leader before its time** | Our small dragons take a free pearl beside them in 83% of turns before our own switch round and 58% after it, on both kinds of map; nobody else's rate moves; our total length stands still from round 150 to 300 on big maps | **+0.4 to +1.5** (no strict count) | Behaviour: very sure. Size of the gain: inferred, not measured | One constant (`LC_LEAD_ROUND`, exists) plus `FEED_CAP_ROUND` | 20 big-map games a side: 58% must become 80%, total length at round 300 121 must become 140 | Nothing |
| **4. Do not give way at contact** | With the numbers on their side all three top teams ram nine in ten same-length small enemies on the next cell and six to eight in ten shorter ones; we 15% and 2% on big maps; the exchange moves about 90 segments a game to our opponents there | **0 to +2.4**, single figure +1 | Behaviour and economy: sure for the tested third. Wins: unsure, the one online trial won 6 of 30 against 9.2 | Conditions and constants in `mark_trade_targets()` and `ram_path()` | 20 big-map games a side: rams made 7.5 a game must become 45, swing per ram must stay above +0.8 | 3 (the trial lost its lead under the leader switch) |

**The one I would pick: candidate 1, take the queen.** All three top teams follow it with small dragons almost
without exception (186 of 186, 155 of 155, and forgot 136 of 139 from round 100 on), our own opponents use it against
us four times as often as we use it against them, the reason we do not is one switch in the code that the team
turned off itself, the turn it acts on cannot fail (the queen has already moved), the cost is counted (88% of the
dragons it would spend are dead by the end of the game anyway), and of everything here it has the narrowest gap
between the cautious and the generous reading. It is not the largest gap we have. It is the one most likely to be
real.

**Second: candidate 2, our queen is never spent.** It addresses the largest piece of the conversion gap on the
footing (our queen alive at the end as often as a top-three queen would be +22.7 wins; this rule's own part of that
is 3.7 to 11.1). It is second and not first because every earlier attempt to protect the queen cost games locally,
because it is new code in several places, and because its value depends on what happens to her afterwards. In
expected points the two are close; candidate 1 is the surer and by far the cheaper.

**One candidate or two?** Candidates 1 and 2 are one idea seen from two sides: a queen that ends a turn inside the
reach of an enemy head dies, so theirs is rammed whenever she does and ours never does when she has a choice. Both
queens end such a turn equally often (5.4 times per 1,000 rounds each); they use 71% of ours and we use 16% of
theirs. The state the two rules aim at together, "our queen alive and hers dead at round 500", is 1 of our 401 games
and 177 of the top three's 1,637, every one of them a win. Together they are worth 49-54 strict and 12.3-21.4
realistic wins, +3.1 to +5.3 points, more than the two alone.

I still keep them as two candidates, and the pick is the first alone, for three reasons. They change different
dragons through different code (a switch that exists; a new block). Their ways of failing differ: if candidate 1
fails, nothing happens; if candidate 2 fails, the queen boxes herself in or the team loses the fight on a small map.
And one card should be readable: with both in one build a flat result could not be traced to either. Their
behaviour numbers do not interfere, so once candidate 1's number has moved, candidate 2 can be tested on top of it.

**If build time decides.** The freeze for new submissions is 8 October, 20:00 KST (the team's loop rules). By cost the order
is 1 (a switch), 3 (a constant), 4 (conditions in two functions), 2 (a new block and seven conditions). Candidate 3
changes only games on maps over 1,200 cells and only rounds 150-299, so it is the one that could most safely ride
along with another card; I would still test one thing at a time.

**What would change my mind.**

- Away from candidate 1: if new replays show the chances taken at 90% and the enemy queen still alive at the end in
  38% or more of games, the chances were on queens that die anyway; or if the red team shows that the both-dead
  games it creates are ones we lose more often than our band rates say (the hard strict count, 6 games or +1.5
  points, is the floor I would then use; below +1 point I would rather take candidate 3, which costs one constant).
- To candidate 2 first: if the aim is the largest possible gain rather than the surest, and there is evidence that
  a queen saved from one ram survives the next against test4 and WeHaveQuizzes (for instance queen deaths per 1,000
  queen-rounds falling from 6.5 to under 5 in a first smoke run).
- To candidates 3 and 4 as a pair: if a rerun of the trade-on-contact build together with the leader switch at
  round 300 holds its round-150 lead to round 300 (total length at least 170 where the live bot has 121). The
  economy is the larger gap overall (+61 wins on the footing against +34 for conversion); what is missing is a rule
  shown to close a known part of it.
