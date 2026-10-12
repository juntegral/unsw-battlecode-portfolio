# Red team, round 2: the race footing, "one leader, known to all" and "nobody leaves a pearl for the leader" (sub-session C2)

Written 2026-10-05 for team meow (id 1119). This file tries to break two new candidate rules for our bot and one
correction, by counting everything again from the replays, and then says which of three finalists I would send to
the team. I ran no game and used no network. The words used below are explained right after the table.

## Verdicts

**In short.** The counts of the last close read (`deep-read-5.md`, sub-session A5) reproduce almost to the game.
What they are taken to mean holds up less well in two of three places.

- **Claim A** (the race gap is mostly the economy seen late) is half right. The first red team's footing was biased
  and A5's is fairer, but about half of the gap is still there on A5's own footing: at the top three's conversion our
  143 races would have given about 49 wins instead of 41.
- **Candidate 5** (one leader, known to all) describes something real, mostly in the earlier bot. In today's builds
  the stall after a leader cut is shorter, on maps of 1,200 cells or fewer it is hardly there, and the pearls that
  demonstrably go astray are about 6 a race. I get 1 to 5 games of 401 on the strict reading where A5 gets 6 to 12,
  and one of its three code changes does not do what it says.
- **Candidate 3z** (nobody leaves a pearl lying for the leader) is the best-identified finding of the whole study: a
  step at exactly our own switch round, on both kinds of map, in every run, in no other team, and at exactly 9 cells
  from the leader each dragon names. It costs us a fifth of our natural pearls on the smaller maps and a third on
  the big ones. One of its five supports is wrong as stated: the zone does hand the leader pearls, mostly pearls of
  feeders late in the game, and 7 of our 41 race wins were closer than that. With that part kept it is the candidate
  I would send.

| Item | Verdict | Claimed | What I would defend | The strongest objection | What would settle it |
|---|---|---|---|---|---|
| **Claim A**: "30% against 55% at level length" is mostly the economy; at level potential we win about half | **Holds, weaker than claimed** | most of the gap is the footing; what is left is "small" | About 45% of the first red team's gap is the footing. What is left: at equal potential at round 300 we convert worse than the top three by 0.33 in log-odds (80% range 0 to 0.66), about 8 wins in our 143 races (range 0 to 16), which is +2 points of win rate (0 to +4) | "We win 11 of 23 at level potential" compares us with test4 and WeHaveQuizzes, who are in the same games. Against those two the top three win 11 of 16 at level potential. And half of what is left sits in races we enter with under half the enemy's potential: we won 0 of 48, the top three 5 of 43 | Nothing we can play. More top-three races against test4 and WeHaveQuizzes would (there are 30) |
| **Candidate 5**: one leader, known to all | **Holds, weaker than claimed** | +0.7 to +2.2 points, "most likely a little over +1" (strict 6 to 12 games of 401) | -0.3 to +0.8 points, most likely +0.2 to +0.4 (strict 1 to 5 games) | The 27-round blindness is measured on 82 games of an earlier bot. In today's builds feeding next to the leader is back at its usual rate 10 to 20 rounds after a cut; the 25-round window after a cut grows as fast as a window with no cut (11.4 against 11.1); feeders that die for the 2-long stub are 7.6% of our feeder deaths. The age rule as written lets the old report win again on the next ping, and it invites regional leaders: our two longest dragons are within 12 segments of each other in half to nine tenths of our races | 20 to 60 replays of a build with it: share of feeder deaths for a stub or for a dragon under twice the feeder's length (12% today) must go under 4%; deaths next to another big dragon that is not the longest (39%) must not rise |
| **Candidate 3z**: remove the pearl zone on every map | **Holds** for the behaviour and the economy, more strongly than stated; one of its five supports **does not hold** ("the leader gets nothing from it"); the size in wins **cannot be told** better than a range | no size given | As defined (zone off in every phase): +0.3 to +2 points, most likely about +1. With the zone kept for the pearls of feeders once feeding has started: the same, with less risk | Every extra pearl is worth nothing if it does not convert, and when our economy was raised before it did not (the trade build: +21% length at round 300 on big maps, 0 wins of 12). The zone hands the dragon that ends as our longest 2.4 natural and 3.4 corpse pearls per small-map race that a small dragon had declined (0.9 and 2.2 on big maps); 7 of our 41 race wins were closer than that | 20 big-map and 20 small-map games of a build with it. Free pearl next to the head taken: 51-58% to over 80%; natural pearls per 50 rounds after the switch: 54 to 70 or more on big maps, 31 to 37 or more on the others; the final longest's share of feeder pearls (39% / 25%) must not fall |

**Which one I would send:** candidate 3z, amended so that feeder pearls next to a leader in view stay reserved once
feeding has started. Candidate 1 (take the queen) is as large and surer in sign; it can ride along, because it touches
other code and is read on another number. Candidate 5 I would not send. Section 4 has the table and the reasons.

### Words

- **Queen**: each team's lowest-numbered dragon. At round 500 a living queen beats a dead one.
- **Race**: a game that reaches round 500 with both queens dead. The longest single dragon then wins. We have 143
  such games (41 won), the three top teams 447 (266 won).
- **The top three**: Vibing++ (id 306, rank 1), SSS (91), "forgot to mention" (264). **test4** (19) and
  **WeHaveQuizzes** (87, "WHQ") are the two teams rated just over 2000 that we meet in 313 of our 401 games.
  **Our opponents** = the other side in our 401 games.
- **Small maps / big maps**: 1,200 cells or fewer / more. Only because our own code switches there.
- **Live bot / test builds / earlier bot**: our 401 games are 275 of the released bot of that hour and 126 of test
  builds (stride, passage2, qh31, tc30). In 82 of the live-bot games (ladder of 3 October, the first 31 of 4 October,
  the run "stride-old") the bot's sonar pings can be read; that is the **earlier bot**. Later builds seal their
  pings; I left them sealed and never touched the key.
- **Leader**: a team's longest dragon. **Lineage**: the dragon that is the longest at the end, followed back through
  its splits.
- **Potential**: the longest dragon plus the pearls every other own dragon would drop if it died now (a dead dragon
  of length L drops L/2 pearls, rounded up). It is what the leader would be if the whole team were fed to it without
  loss.
- **Feeding**: small dragons die on purpose next to the leader, which eats their pearls. Our bot's feeders die by
  sending no order ("no order" death). **Feeder death** below means such a death.
- **Death by choice**: a death that is not a ram, of a dragon that had a free cell next to its head when it gave its
  order (A5's definition, which works for every team).
- **Leader cut**: a split in which a team's longest dragon (8 or longer) keeps 2-3 segments and hands the rest to a
  new dragon with a new id. The 2-3 segments that keep the old id are the **stub**, the new dragon is the **heir**.
- **Record / names**: every dragon of ours remembers one leader (id, length, position) and sends it on its sonar
  pings. A dragon "names" the id in its last readable ping.
- **Switch round**: round 150 on big maps and 300 on small maps (`grow_round` in our code). From then on dragons
  longer than 4 stop splitting and the **pearl zone** applies: a dragon may not take pearls within 9 cells of the
  position of the leader in its record.
- **Pearl turn**: a dragon of 2-4 that is not the queen gives a move order, no enemy head is in its 7x7 view, and a
  pearl lies on a free cell next to its head that has a further free neighbour. **Taken** = its first step eats it.
- **Natural pearl / corpse pearl**: a pearl that a tile produced / one of the pearls a dead dragon left.
- **Point**: one percentage point of win rate. One game of our 401 is 0.25 points. We win 112 of 401 (27.9%).
- **80% range**: the range in which the true value lies four times out of five, given the sample.
- **Strict / cautious reading**: strict changes one thing in a played game and keeps the rest; cautious takes half
  of it or less, because the enemy answers and because not every pearl that could be eaten is.

### How this was done

Every number the three items rest on was counted again with scripts written for this file (`y_*.py`, outputs in
`y_out/`). They use only the replay walker `lib.py` and the game list `games.csv`; I read the other sub-sessions'
scripts only to learn what they had counted. Four walks over the replays: `y_w1.py` (all 1,795 games in which a
study team plays a team rated 2000 or more, both sides: lengths every 5 rounds, every split, every death with what
stood next to it, every pearl eaten), `y_w2.py` (what our dragons name as leader, and what the dragons near every
leader cut do in the next 30 rounds), `y_w3.py` (every pearl turn, by the zone of the true longest dragon and by the
zone the dragon itself names; every pearl declined in a zone and who ate it; natural pearls per dragon-round inside
and outside a zone; how often a leader has no free cell), `y_w4.py` and `y_w4b.py` (every feeder death of ours with
what it died next to). Where my number differs from A5's or the lead's, both are given with the reason.

"Measured" means counted on replays by the script named. "Inferred" means arithmetic on played games or a reading of
the source `mybot2/main.cpp`. A replay shows positions, orders, deaths, pearls and pings. It does not show what a
bot intended.
