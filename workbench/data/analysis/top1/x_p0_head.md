# Red team: an attack on the four candidate hypotheses (sub-session C)

Written 2026-10-05 for team meow (1119). This file tries to break the four candidates of `hypotheses.md`
(sub-session B) by counting everything again from the replays. The words used in the table are explained right
below it; how the work was done is said after that.

## 1. Verdicts

**In short.** B counted well: almost every count in `hypotheses.md` reproduces, several to the unit. What does not
hold up as well is what the counts are taken to be worth. Candidate 1 survives, at about +1 point of win rate
instead of +1.5 to +2. Candidate 2 survives at about half of its range, and half of that again if it is built from
the code that exists. For candidates 3 and 4 the behaviour is exactly as described and I cannot tell the sign of
the result. None of the four can be judged by wins before the freeze. The largest gap I could count that none of
them works on is the longest-dragon race on the smaller maps (section 2, attack I).

| Candidate | Verdict | B's range | The range I would defend | The strongest objection | What would settle it |
|---|---|---|---|---|---|
| 1. Take the queen | **Holds, weaker than claimed** | +1.5 to +3.2 points, most likely +1.5 to +2 | +0.5 to +2, most likely about +1 (4 to 6 games in 401) | Its small-dragon half has been online twice (56 games a side): chances taken 31% to 95%, rams on her queen 16 to 24 games, her queen alive at the end 19 to 16, certain losses 16 to 15, wins 16 to 17. And a dead enemy queen is worth nothing to us in the lowest economy band, where 41% of the games with an untaken chance are. | No test we can run before the freeze. "Our queen dead, hers alive at round 500" should fall from 18% of games to about 12%; seeing that takes about 300 games a side. In 60 + 60 games only the behaviour can be checked (in-view chances taken 22% to over 90%; games with a chance and no ram 19% to under 3%). |
| 2. Our queen is never spent | **Holds, weaker than claimed** | +0.9 to +2.8 points (strict: 34 games) | +0.3 to +1.5, most likely +0.5 to +1 (2 to 4 games in 401) | A queen of ours that takes the safe step in the same situation is alive at the end of the game in 6 to 9% of cases, the same as one that does not. 25 of the 36 strict flips are against one opponent. Built from the existing pieces the veto would have fired on 51 of the 103 fatal turns. On small maps it lifts a gate the team set on measured local losses. | Only many games: our queen alive at round 500 must rise from 10% to 15% of games (about 250 games a side). In 60 + 60 only the behaviour number can be checked (turns ending in reach by choice: 2.4 per 1,000 queen-rounds to under 0.8) and that wipe-outs on maps of 600 cells or fewer do not rise. |
| 3. No leader before its time | **Cannot be told** (the behaviour holds; the sign of the result is open) | +0.4 to +1.5 | -1.2 to +1.3 | All 12 of our wins on these maps are longest-dragon wins, 10 of them with less total length than the enemy at round 300, won with the leader the round-150 switch builds (7 long at round 150, 24 at round 300). On the maps where the rules start at round 300 our leader is 4 long at round 300 and we lose level games the top three win. The economy gain is inferred. | 20 big-map games a side, as B says, but read on three numbers together: pearl taken 58% to 80%; total length at round 300 from 122 to 140 or more; AND our longest dragon at round 400 not under 15 (19 today). If the third fails the trade is the wrong way round. |
| 4. Do not give way at contact | **Cannot be told** (the behaviour holds; the one trial did not win) | 0 to +2.4, single figure +1 | -0.5 to +1.5 | The tested third tripled our rams, added a fifth to our length at round 300 and won 0 of 12 on the maps it changes (6 of 30 in all against 9.2). The untested two thirds are the rams on which we lose segments today (-0.7 a ram), because our team eats 68% of the pearls of a ram it starts where a top team eats 80%. | The swing per ram we start on the two new rows, on 20 big-map games: it must be above zero. And who eats: our share of the pearls of rams we start must reach 75%. If it stays at 68% the rule only trades dragons. |
| 1 + 2 together | weaker than claimed | +3.1 to +5.3 | +1.2 to +2.5 | The upper half of B's range assumes that a saved queen of ours then lives like a top-three queen. Measured, she is alive at the end 6 to 9% of the time. | as for 1 and 2 |

### Words

- **Queen**: each team's lowest-numbered dragon (id 0 or 1). Both queens move before every other dragon each round.
- **Ram**: a head moves into another head; both dragons die.
- **Reach**: the most steps a dragon can take in one turn: a quarter of its length rounded up is free, each further
  step costs one segment. 1, 2, 3, 5, 6 steps for lengths 2, 3, 4, 5, 6. This is the "plain" reach. Every pearl
  eaten on the way pays for one more step ("pearl-paid" reach); the study's files mostly use the plain one.
- **View**: the 7x7 square around a head.
- **In-view chance**: a turn of a non-queen dragon that starts with the enemy queen's head in its view and a path of
  free cells to it no longer than its reach. Because queens move first, a ram on such a turn cannot be dodged.
- **Safe step**: a one-step move of a queen onto a free cell that no enemy head in her view can reach this round.
  **Queen-round**: one round in which a queen is alive.
- **How a game ends**: by **wipe-out**, or at round 500, where a living queen beats a dead one and the longer living
  queen wins (**queen rule**); with both queens dead the longest single dragon wins (**longest rule**). A **certain
  loss** is a round-500 game with our queen dead and hers alive.
- **Leader**: a team's longest dragon. **Leader rules**: in our bot, from a fixed round on, small dragons leave
  pearls near the leader and dragons longer than 4 stop splitting.
- **Swing** of a ram: pearls of the two corpses eaten by the side that started it, minus the dragon it lost, minus
  the same for the other side; in segments.
- **Economy band**: our total length divided by the enemy's at a given round: under 0.67, 0.67 to 1, 1 to 1.5, over 1.5.
- **Live bot / test builds**: our 401 games against teams rated 2000 or more (map Schooltime left out) are 275 games
  of the released bot and 126 of test builds (stride, passage2, qh31, tc30). 313 are against two teams, test4 and
  WeHaveQuizzes.
- **Strict / realistic**: B's two ways to re-score a played game. Strict changes one event (a queen lives, a queen
  dies) and keeps the final lengths. Realistic gives the changed game our own win rate for games of that kind.
- **Flip**: a played loss that a reading turns into a win.
- **Point**: one percentage point of win rate; one game of our 401 is 0.25 points. We win 112 of 401 (27.9%).
- **80% range**: the range in which the true share lies four times out of five, given the sample.

### How this was done

Every number a candidate's case rests on was counted again with scripts written for this file (`x_*.py`, outputs
in `x_out/`); they use only the replay walker `lib.py` and the game list. Where my number differs from B's, both are
given and the reason. I ran no game. "Measured" means counted on replays by the script named; "inferred" means
arithmetic on played games or a reading of the source. A replay shows positions, orders, deaths, pearls and sonar
rays; it does not show what a bot knew or intended.

Cases were looked at by eye with `story.py` and with `x_eye.py`, which draws the board at the start of one dragon's
own turn (`story.py view` draws the start of the round, before both queens have moved): 28 turns for candidate 1,
19 for candidate 2, 18 for candidate 3 and 16 for candidate 4.

For each candidate the attacks follow the lead's list: A the counts, B cause or consequence, C what happens next,
D sample size, E cross-team, F earlier experiments, G backfire, H the code claim. Attack I, the footing, is one
section for all four, after candidate 4.

## 2. Per candidate

