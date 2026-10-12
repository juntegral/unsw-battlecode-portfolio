# How and why our own queen dies (sub-session A4)

Written 2026-10-05 for team meow (1119).

This is the fourth close read of the top-team study. The first three read Vibing++ (`deep-read.md`), SSS and forgot (`deep-read-2.md`) and our economy (`deep-read-3.md`). This one reads our own queen in our own 401 games against teams rated 2000 or higher, next to the queen of our opponent in the same games and the queens of forgot, SSS and Vibing++ in their 1,637 games against such teams. The map Schooltime is left out everywhere, because both queens are sealed in a room there.

**How it was read.** Every replay was walked by `d_class.py`. It stores the board around each queen at the start of her own turn for her last 13 turns, and one row for every turn of the game in which an enemy head was in her view. A second pass, `d_life.py`, stores where each queen and her team stood every round. All counts come from those files (`d_out/cls/`, `d_out/life/`) and from the lead's `q/*.json`, through the script named next to each number. Then 40 of our games were read turn by turn with `d_q.py` (one page per queen: where she was every 25 rounds, every order near the end, the board at her last turns), next to the opponent's queen in the same game and 18 top-team games on the same maps from the same start cell. A replay shows positions, orders, deaths, pearls and sonar rays. It does not show what a bot knew or intended; such sentences are marked "inference". The bot's source (`mybot2/main.cpp`) was read, not run; no game was played. This file is assembled by `d_build.py` from the parts `d_p*.md`; the scripts are `d_*.py` and their outputs are in `d_out/`.

**Words.**
- **Queen**: each team's lowest-id dragon. She moves before every other dragon of her team each round. At round 500 the longer living queen wins, and a living queen of any length beats a dead one.
- **Ram**: a head moves into another head; both dragons die.
- **Reach**: the most steps a dragon can take in one turn: 1, 2, 3, 5, 6 for lengths 2, 3, 4, 5, 6. Each pearl eaten on the way adds one.
- **In view**: inside the 7x7 square around a head.
- **Safe step**: a one-step move that ends on a cell no enemy head in her view can move into this round.
- **In reach**: on a cell that an enemy head in her view can move into this round.
- **Boxed in**: no free cell next to her head at the start of her turn. There is no "stay" order, so a boxed-in dragon that cannot split dies.
- **Tree cell**: a cell from which there is no way round: a dead-end corridor or nook. Found by removing one-exit cells of the kelp-and-portal map again and again. A dragon cannot turn round, so a head that enters a tree cell never comes out.
- **Cut** and **shed**: two ways to split a long dragon. A cut keeps 2 or 3 segments for the parent and gives the rest to the child. A shed gives the child 2 segments from the tail and keeps the rest.
- **Queen-round**: one round in which a queen is alive. Rates "per 1,000 queen-rounds" divide a count by the rounds the group's queens lived, so that a queen living 280 rounds can be compared with one living 140.
- **Live bot / candidates**: our 401 games are eleven runs. The two ladder downloads and the "-old" halves of the smoke pairs are the live bot of that hour (275 games); the "-new" halves are candidates (126 games: stride, passage2, qh31, tc30).
- **Rules on / off**: our queen rules apply only on maps of more than 600 cells (256 of the 401 games). On the six smaller maps she is an ordinary dragon.
- **test4** and **WHQ** (WeHaveQuizzes): the two opponents in 313 of our 401 games. The top three play them too (108 games), which gives a comparison against the same opponents.

## 1. The three findings that matter most

1. **Against the same two opponents our queen is cornered as often as a top-three queen, but she ends a turn inside a visible enemy's reach by her own choice six times as often, and those opponents punish it four times out of five.** Per 1,000 queen-rounds against test4 and WHQ: turns with no safe step 2.5 (ours) against 2.2 (top three); turns that ended in reach although a safe step existed 2.6 against 0.4; rammed on a turn that ended in reach 77% against 67%. Over all 401 games this is 104 queen deaths, a quarter of our games, and 42% of the whole gap between our queen's death rate (6.5 per 1,000 queen-rounds) and the top three's (2.7). In 90 of the 104 a safe step with room behind it, not through a portal, was on the board. One turn before the fatal one almost nothing is wrong: of our rammed queens that had an enemy head in view then, 96% had a safe step and 6% ended in reach. In the code the danger of a cell is a sum term that a pearl can outweigh, and it is weakest for the shortest queen; dragons of 8 or more already have a strict "least exposed cell first" rule, the queen does not.
2. **Three of every ten of her deaths are not rams at all (111 of 362), and most of those come from three code paths of our own.** (a) When she has no free cell and is 4 or longer she keeps 2 segments and gives the rest to a child: 40 such cuts of a queen of 6 or more in 37 games, 907 segments given away, 14 queens dead within a few rounds as a boxed-in 2-long, among them 10 at round 3 on Slithery Fight and fed queens of 57, 32 and 15 segments. SSS and forgot never cut (0 in 1,135 games); they shed 2 from the tail each round and wait. (b) On maps of 600 cells or fewer, where the queen rules are off, the live bot's queen dies at twice the rate (10.7 against 5.0 per 1,000 queen-rounds): she takes a portal step in 27 of the 44 games on small maps that have portals (7 of 175 with rules on), rams an enemy head herself although a free safe cell exists (10 games), and walks down dead-end corridors eating pearls (21 of our 30 terrain deaths are on these maps). (c) In 20 games one of our own dragons stepped head-on onto the only exit of a one-wide passage she was in.
3. **No single queen rule is worth much on its own, because a queen who avoids one death meets the next; and the other half of the difference is not our queen but our hunters.** Of the 102 round-500 losses with both queens dead, 26 followed a death of finding 1. If she had then lived as often as a top-three queen does from that round on, 7 flip; if she stayed exposed to our other kinds of death at our own rates, 2. All four families she controls herself together (findings 1 and 2) give 59, 18 or 9 games of 401 under the same three readings: plus 2 to plus 5 points of win rate on 28%. The mirror number explains the rest: our opponents' queens end a turn inside the reach of one of our heads as often as ours does in theirs (5.4 times per 1,000 queen-rounds, both), but we ram on 16% of those turns and they ram on 71%. Their queens live because we do not take the ram, not because they are better hidden.

## 2. Every queen death, classified (question a)

**How a death gets its kind.** `d_class.py` walks each replay and stores the board at the start of the queen's own turn for her last 13 turns. `d_tab.py` then gives each queen one kind from the board at the start of her **last own turn**:

- **Rammed** (an enemy moved its head into hers). Four kinds, decided by two facts: was the killer's head in her view when her last turn began, and did she have a one-step move that ended outside the reach of every enemy head in her view.
  - *stepped in*: the killer was in view, she began the turn outside every visible reach, a safe step existed, and she ended in reach.
  - *stayed in*: the killer was in view, she began the turn in reach, a safe step existed, and she ended in reach again.
  - *cornered*: the killer was in view and none of her one-step moves ended outside reach.
  - *unseen*: the killer's head was outside her 7x7 view when her last turn began (or it was born by a split after her turn).
- **Boxed in** (she died by her own order with no free cell next to her head). The sub-kind names what stood on the sides that were not kelp and not her own body: a team-mate, an enemy, or nothing (then it is a *terrain dead end* if her head stood on a tree cell, else *own body*).
- **Own ram**: she moved her head into a head herself. A few rare kinds are joined as "other".

The reach model: an enemy of length L can move its head into a cell this round if a path of body-free cells of k steps leads there with k no larger than ceil(L/4) + (L - 2), plus one for each pearl it eats on the way. Bodies are taken where they stand when her turn starts, and her own last segment is taken as gone. Dragons that move between her turn and the enemy's turn are not modelled. Where it can be checked it holds: with the killer in view, the model called the cell she died on safe in 2 of our 220 rams and in 15 of the top three's 603 (the "model miss" row).

The four ram kinds of our 251 rammed queens were counted a second time by a script that shares no code with the first and enumerates every enemy move step by step (`d_recount.py`, `d_out/recount_summary.txt`): killer in view 220, a safe step existed 106, cornered 114, unseen 31, the same as below. The kind differs in 3 games: in two the queen made a two-step move that the recount does not follow, in one a pearl on the enemy's path is counted differently.

None of our 362 queen deaths is a time-out or an illegal order: the kind "no action with a free cell" is empty for us.

Counts are games; the percentage is the share of that group's games. Source: `d_md.py`, output `d_out/md_class.md` (the same numbers in another layout: `d_tab.py`, `d_out/tab.txt`).

| Kind of end | meow, all 401 | meow live bot | meow candidates | our opponents | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|---|
| alive at the end | 39 (10%) | 27 (10%) | 12 (10%) | 162 (40%) | 226 (36%) | 207 (41%) | 134 (27%) |
| rammed: stepped into reach (killer in view, began outside reach, a safe step existed) | 66 (16%) | 40 (15%) | 26 (21%) | 15 (4%) | 22 (3%) | 18 (4%) | 19 (4%) |
| rammed: stayed in reach (killer in view, began inside reach, a safe step existed) | 38 (9%) | 28 (10%) | 10 (8%) | 12 (3%) | 17 (3%) | 20 (4%) | 16 (3%) |
| rammed: cornered (killer in view, no one-step move out of reach) | 114 (28%) | 72 (26%) | 42 (33%) | 67 (17%) | 209 (33%) | 142 (28%) | 125 (25%) |
| rammed: killer's head not in her view at the start of her last turn | 31 (8%) | 23 (8%) | 8 (6%) | 7 (2%) | 70 (11%) | 57 (11%) | 67 (13%) |
| rammed on a cell my reach model called safe | 2 (0%) | 2 (1%) | 0 (0%) | 1 (0%) | 9 (1%) | 3 (1%) | 3 (1%) |
| boxed in: a team-mate's body or head on her last exit | 58 (14%) | 43 (16%) | 15 (12%) | 59 (15%) | 18 (3%) | 22 (4%) | 85 (17%) |
| boxed in: terrain dead end (kelp and her own body) | 30 (7%) | 21 (8%) | 9 (7%) | 37 (9%) | 29 (5%) | 15 (3%) | 21 (4%) |
| boxed in: an enemy body on her last exit (alone or with a team-mate) | 3 (1%) | 3 (1%) | 0 (0%) | 7 (2%) | 5 (1%) | 2 (0%) | 9 (2%) |
| boxed in: only her own body, not a dead end | 0 (0%) | 0 (0%) | 0 (0%) | 7 (2%) | 0 (0%) | 0 (0%) | 0 (0%) |
| she moved her head into a head | 19 (5%) | 16 (6%) | 3 (2%) | 18 (4%) | 19 (3%) | 9 (2%) | 20 (4%) |
| other (portal step onto a body, stride crash, no action with a free cell, team-mate rams her) | 1 (0%) | 0 (0%) | 1 (1%) | 9 (2%) | 8 (1%) | 8 (2%) | 3 (1%) |
| games | 401 | 275 | 126 | 401 | 632 | 503 | 502 |

By run (counts; "-old" runs and the two ladder downloads are the live bot):

| Kind of end | dl-20261003 | dl-20261004 | stride-old | passage2-old | qh31-old | tc30-dev1-old | stride-new | passage2-new | qh31-new | tc30-new | tc30-dev1b-new |
|---|---|---|---|---|---|---|---|---|---|---|---|
| alive | 1 | 15 | 3 | 3 | 4 | 1 | 5 | 2 | 2 | 2 | 1 |
| ram: stepped in | 3 | 17 | 6 | 4 | 6 | 4 | 7 | 7 | 5 | 5 | 2 |
| ram: stayed in | 3 | 18 | 3 | 3 | 1 | 0 | 1 | 3 | 3 | 3 | 0 |
| ram: cornered | 6 | 39 | 10 | 8 | 6 | 3 | 8 | 4 | 11 | 12 | 7 |
| ram: unseen | 1 | 14 | 0 | 6 | 1 | 1 | 2 | 4 | 0 | 1 | 1 |
| ram: model miss | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| boxed: ally body | 3 | 25 | 3 | 3 | 5 | 4 | 4 | 5 | 4 | 2 | 0 |
| boxed: terrain dead end | 3 | 13 | 2 | 1 | 2 | 0 | 1 | 3 | 1 | 1 | 3 |
| boxed: enemy | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| boxed: own body | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| own ram | 2 | 9 | 1 | 0 | 3 | 1 | 0 | 0 | 2 | 1 | 0 |
| other | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| games | 24 | 153 | 28 | 28 | 28 | 14 | 28 | 28 | 28 | 28 | 14 |

By round band (rounds 0-49 / 50-99 / 100-299 / 300+), deaths only:

| Kind of death | meow, all 401 | meow live bot | our opponents | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|
| ram: stepped in | 15 / 22 / 26 / 3 | 10 / 14 / 15 / 1 | 3 / 5 / 7 / 0 | 5 / 7 / 9 / 1 | 8 / 4 / 6 / 0 | 5 / 5 / 8 / 1 |
| ram: stayed in | 7 / 11 / 19 / 1 | 6 / 8 / 13 / 1 | 6 / 3 / 2 / 1 | 8 / 5 / 4 / 0 | 5 / 2 / 9 / 4 | 8 / 2 / 5 / 1 |
| ram: cornered | 22 / 33 / 50 / 9 | 13 / 24 / 30 / 5 | 5 / 15 / 35 / 12 | 43 / 59 / 85 / 22 | 25 / 24 / 64 / 29 | 25 / 27 / 56 / 17 |
| ram: unseen | 5 / 2 / 18 / 6 | 4 / 1 / 13 / 5 | 0 / 1 / 3 / 3 | 10 / 17 / 14 / 29 | 6 / 6 / 23 / 22 | 9 / 15 / 22 / 21 |
| ram: model miss | 0 / 1 / 0 / 1 | 0 / 1 / 0 / 1 | 0 / 0 / 0 / 1 | 2 / 4 / 1 / 2 | 1 / 1 / 0 / 1 | 0 / 0 / 0 / 3 |
| boxed: ally body | 23 / 13 / 18 / 4 | 15 / 10 / 14 / 4 | 1 / 6 / 35 / 17 | 4 / 1 / 8 / 5 | 0 / 0 / 10 / 12 | 28 / 16 / 31 / 10 |
| boxed: terrain dead end | 2 / 11 / 16 / 1 | 0 / 6 / 14 / 1 | 1 / 3 / 21 / 12 | 2 / 9 / 6 / 12 | 0 / 2 / 5 / 8 | 3 / 5 / 11 / 2 |
| boxed: enemy | 1 / 1 / 0 / 1 | 1 / 1 / 0 / 1 | 1 / 2 / 2 / 2 | 1 / 1 / 3 / 0 | 2 / 0 / 0 / 0 | 3 / 4 / 2 / 0 |
| boxed: own body | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 / 0 / 6 / 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| own ram | 5 / 6 / 8 / 0 | 4 / 4 / 8 / 0 | 1 / 4 / 12 / 1 | 5 / 6 / 8 / 0 | 0 / 2 / 5 / 2 | 5 / 10 / 5 / 0 |
| other | 0 / 0 / 1 / 0 | 0 / 0 / 0 / 0 | 1 / 1 / 2 / 5 | 0 / 2 / 1 / 5 | 0 / 0 / 5 / 3 | 1 / 0 / 1 / 1 |
| all deaths | 80 / 100 / 156 / 26 | 53 / 69 / 107 / 19 | 19 / 40 / 125 / 55 | 80 / 111 / 139 / 76 | 47 / 41 / 127 / 81 | 87 / 84 / 141 / 56 |

By queen rules (meow; rules are on when the map has more than 600 cells) and by map size:

| Kind of end | all runs, rules on (256 games) | all runs, rules off (145) | live bot, rules on (175) | live bot, rules off (100) | 600 cells or fewer | 601-1,500 | over 1,500 |
|---|---|---|---|---|---|---|---|
| alive | 35 (14%) | 4 (3%) | 25 (14%) | 2 (2%) | 4 | 35 | 0 |
| ram: stepped in | 38 (15%) | 28 (19%) | 23 (13%) | 17 (17%) | 28 | 15 | 23 |
| ram: stayed in | 30 (12%) | 8 (6%) | 23 (13%) | 5 (5%) | 8 | 17 | 13 |
| ram: cornered | 84 (33%) | 30 (21%) | 50 (29%) | 22 (22%) | 30 | 48 | 36 |
| ram: unseen | 27 (11%) | 4 (3%) | 20 (11%) | 3 (3%) | 4 | 10 | 17 |
| ram: model miss | 2 (1%) | 0 (0%) | 2 (1%) | 0 (0%) | 0 | 2 | 0 |
| boxed: ally body | 28 (11%) | 30 (21%) | 21 (12%) | 22 (22%) | 30 | 12 | 16 |
| boxed: terrain dead end | 9 (4%) | 21 (14%) | 8 (5%) | 13 (13%) | 21 | 5 | 4 |
| boxed: enemy | 1 (0%) | 2 (1%) | 1 (1%) | 2 (2%) | 2 | 0 | 1 |
| boxed: own body | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 0 | 0 | 0 |
| own ram | 2 (1%) | 17 (12%) | 2 (1%) | 14 (14%) | 17 | 1 | 1 |
| other | 0 (0%) | 1 (1%) | 0 (0%) | 0 (0%) | 1 | 0 | 0 |

Her length at death, and for rams the killer's length and the steps of its ramming move (meow, all runs; in brackets the top three together):

| Kind of death | n | her length 2 / 3 / 4 / 5 / 6+ | killer's length 2 / 3 / 4 / 5-9 / 10+ | killer's steps 1 / 2 / 3 / 4 / 5+ |
|---|---|---|---|---|
| ram: stepped in | 66 (59) | 45 / 15 / 2 / 1 / 3 (29 / 26 / 2 / 0 / 2) | 27 / 25 / 14 / 0 / 0 (16 / 35 / 8 / 0 / 0) | 18 / 23 / 16 / 8 / 1 (15 / 33 / 10 / 1 / 0) |
| ram: stayed in | 38 (53) | 14 / 17 / 7 / 0 / 0 (25 / 22 / 2 / 0 / 4) | 11 / 21 / 3 / 3 / 0 (4 / 29 / 12 / 7 / 1) | 17 / 12 / 3 / 5 / 1 (13 / 14 / 15 / 7 / 4) |
| ram: cornered | 114 (476) | 54 / 44 / 7 / 4 / 5 (206 / 184 / 23 / 4 / 59) | 38 / 46 / 15 / 13 / 2 (150 / 222 / 48 / 38 / 18) | 44 / 40 / 14 / 11 / 5 (203 / 163 / 58 / 22 / 30) |
| ram: unseen | 31 (194) | 9 / 13 / 0 / 1 / 8 (37 / 56 / 11 / 4 / 86) | 1 / 12 / 5 / 12 / 1 (25 / 40 / 35 / 70 / 24) | 3 / 0 / 14 / 7 / 7 (29 / 29 / 52 / 30 / 54) |
| ram: model miss | 2 (15) | 0 / 0 / 1 / 1 / 0 (6 / 5 / 1 / 0 / 3) | 0 / 2 / 0 / 0 / 0 (0 / 7 / 2 / 4 / 2) | 0 / 1 / 0 / 1 / 0 (0 / 3 / 6 / 2 / 4) |
| boxed: ally body | 58 (125) | 28 / 22 / 2 / 6 / 0 (64 / 56 / 1 / 2 / 2) | - | - |
| boxed: terrain dead end | 30 (65) | 19 / 11 / 0 / 0 / 0 (35 / 28 / 0 / 1 / 1) | - | - |
| boxed: enemy | 3 (16) | 2 / 1 / 0 / 0 / 0 (11 / 5 / 0 / 0 / 0) | - | - |
| own ram | 19 (48) | 16 / 3 / 0 / 0 / 0 (22 / 26 / 0 / 0 / 0) | - | - |
| other | 1 (19) | 1 / 0 / 0 / 0 / 0 (5 / 4 / 1 / 0 / 9) | - | - |

What the game became (meow, all runs; in brackets the live bot): won by wipe-out / lost by wipe-out / round 500 won / round 500 lost with her queen dead too / round 500 lost with her queen alive:

| Kind of end | games | wipe-out won | wipe-out lost | round 500 won | round 500 lost, both queens dead | round 500 lost, her queen alive |
|---|---|---|---|---|---|---|
| alive | 39 (27) | 24 (16) | 0 (0) | 4 (3) | 0 (0) | 11 (8) |
| ram: stepped in | 66 (40) | 8 (5) | 26 (19) | 4 (3) | 14 (3) | 14 (10) |
| ram: stayed in | 38 (28) | 4 (4) | 16 (9) | 2 (2) | 12 (11) | 4 (2) |
| ram: cornered | 114 (72) | 20 (14) | 35 (22) | 8 (4) | 29 (21) | 22 (11) |
| ram: unseen | 31 (23) | 0 (0) | 7 (4) | 4 (3) | 14 (11) | 6 (5) |
| ram: model miss | 2 (2) | 0 (0) | 1 (1) | 0 (0) | 0 (0) | 1 (1) |
| boxed: ally body | 58 (43) | 8 (6) | 3 (2) | 14 (10) | 17 (11) | 16 (14) |
| boxed: terrain dead end | 30 (21) | 1 (0) | 6 (5) | 8 (5) | 8 (6) | 7 (5) |
| boxed: enemy | 3 (3) | 0 (0) | 1 (1) | 0 (0) | 0 (0) | 2 (2) |
| own ram | 19 (16) | 2 (2) | 8 (7) | 0 (0) | 8 (6) | 1 (1) |
| other | 1 (0) | 0 (0) | 0 (0) | 1 (0) | 0 (0) | 0 (0) |
| all | 401 (275) | 67 (47) | 103 (70) | 45 (30) | 102 (69) | 84 (59) |

**The same deaths as rates** (`d_haz.py`, `d_out/haz.txt`). Shares of games flatter a short-lived queen: one that lives 280 rounds has twice the time to meet each kind of death as one that lives 140. "Stepped or stayed in" joins the two avoidable kinds; "cornered" includes the model misses; "boxed by bodies" joins team-mate, enemy and own body.

| Deaths per 1,000 queen-rounds | all | rammed: stepped or stayed in | rammed: cornered | rammed: unseen | boxed by bodies | boxed: terrain | own ram | mean rounds alive |
|---|---|---|---|---|---|---|---|---|
| meow, all 401 games | 6.47 | 1.86 | 2.07 | 0.55 | 1.09 | 0.54 | 0.34 | 139 |
| meow live bot (275) | 6.31 | 1.73 | 1.88 | 0.59 | 1.17 | 0.53 | 0.41 | 143 |
| ... rules on (175) | 4.98 | 1.53 | 1.73 | 0.66 | 0.73 | 0.27 | 0.07 | 172 |
| ... rules off (100) | 10.68 | 2.40 | 2.40 | 0.33 | 2.62 | 1.42 | 1.53 | 92 |
| meow against test4 and WHQ only (313) | 6.46 | 1.93 | 2.04 | 0.60 | 1.10 | 0.48 | 0.28 | 139 |
| our opponents (401) | 2.15 | 0.24 | 0.61 | 0.06 | 0.66 | 0.33 | 0.16 | 278 |
| forgot (632) | 2.79 | 0.27 | 1.50 | 0.48 | 0.16 | 0.20 | 0.13 | 230 |
| SSS (503) | 2.12 | 0.27 | 1.04 | 0.41 | 0.17 | 0.11 | 0.06 | 277 |
| Vibing++ (502) | 3.42 | 0.33 | 1.19 | 0.62 | 0.87 | 0.20 | 0.19 | 214 |
| top three together (1,637) | 2.73 | 0.29 | 1.25 | 0.49 | 0.36 | 0.17 | 0.12 | 240 |
| top three against test4 and WHQ only (108) | 2.96 | 0.28 | 1.46 | 0.61 | 0.28 | 0.28 | 0.00 | 229 |

Our queen dies 6.5 times per 1,000 rounds she is alive, a top-three queen 2.7 times. The gap of 3.7 splits like this: stepped or stayed in 1.57 (42% of the gap; our rate is 6.4 times theirs), cornered 0.82 (22%; 1.7 times), boxed by bodies 0.73 (20%; 3 times, though Vibing++ is as bad as we are), terrain dead ends 0.37 (10%; 3 times), own rams 0.22 (6%; 3 times), unseen rams 0.06 (none: the same rate). Against the same two opponents the picture is the same (6.46 against 2.96; stepped or stayed in 1.93 against 0.28).

**The boxed-in deaths by what blocked her** (`d_box.py`, `d_out/box.txt`):

| Boxed in by | meow, all | live bot | live, rules on | live, rules off | our opponents | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|---|---|
| cut and stuck: she cut herself from 6 or more to 2-3 and died boxed in | 14 | 11 | 11 | 0 | 10 | 0 | 0 | 4 |
| her own recent split child on her last exit (not a cut) | 11 | 7 | 1 | 6 | 8 | 1 | 0 | 16 |
| nose to nose: a team-mate's HEAD on her last exit | 20 | 17 | 8 | 9 | 23 | 8 | 8 | 34 |
| another team-mate's body segment on her last exit | 14 | 9 | 2 | 7 | 20 | 9 | 14 | 31 |
| an enemy body on her last exit | 2 | 2 | 0 | 2 | 5 | 5 | 2 | 9 |
| her own body only, not a dead end | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 |
| terrain dead end (tree cell) | 30 | 21 | 8 | 13 | 37 | 29 | 15 | 21 |
| all | 91 | 67 | 30 | 37 | 110 | 52 | 39 | 115 |
| ... one of her sides was a portal edge (the cell behind it is outside her view) | 29 | 19 | 0 | 19 | 14 | 3 | 19 | 18 |

For the terrain dead ends, the turn on which the free space around her fell under 12 cells: she stepped onto a pearl in 16 of our 30, a roomier free side existed in 21, she ate inside in 26 and split inside in 18. For "nose to nose", the space was open until the very last turn in 12 of 20: the team-mate stepped in front of her after her move.

**How good was the safe step she did not take** (`d_ramdet.py`, `d_out/ramdet.txt`). "Roomy" = not a tree cell and at least her length + 2 body-free cells behind it.

| Stepped or stayed in | deaths | a roomy safe step existed | ... and it did not cross a portal | the only safe step led into a pocket | the only roomy safe step crossed a portal |
|---|---|---|---|---|---|
| meow, all | 104 | 92 | 90 | 12 | 2 |
| meow live bot | 68 | 61 | 59 | 7 | 2 |
| top three | 112 | 75 | 71 | 37 | 4 |

## 3. Games read

Forty of our games, chosen from the classification so that every kind of death with 15 or more cases has at least three games on different maps. All 40 are games of the live bot: 38 from the two ladder downloads and 2 from "-old" runs. The candidates are covered by the counts of sections 2 and 5, not by close reads. Each was read with `d_q.py` for our queen and for the opponent's queen in the same game. "Our start" is the cell our queen starts on; the top-team games in the second table were picked on the same map from the same start cell against test4 or WHQ where such a game exists. Generated by `d_games.py` (`d_out/md_games.md`).

| # | game | map (cells) | run | our start | opponent | result | our queen | the opponent's queen in the same game |
|---|---|---|---|---|---|---|---|---|
| 1 | 980372 | Around UNSW (4096) | dl-20261003 | (20, 42) | 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿 | won at round 500 (longest) | rammed: stepped in, round 94, 2 long | boxed in: terrain dead end, round 259, 2 long |
| 2 | 1053773 | Australia (4096) | dl-20261004 | (39, 44) | WeHaveQuizzes | lost at round 500 (queen rule) | rammed: stepped in, round 74, 3 long | alive, 127 long |
| 3 | 1045200 | Devil (512) | dl-20261004 | (3, 5) | test4 | lost by wipe-out | rammed: stepped in, round 18, 2 long | alive, 2 long |
| 4 | 1053020 | Islands (2240) | dl-20261004 | (10, 7) | WeHaveQuizzes | lost at round 500 (longest) | rammed: stepped in, round 145, 3 long | boxed in by a team-mate, round 203, 8 long |
| 5 | 1044202 | Default (1024) | dl-20261004 | (0, 0) | test4 | lost by wipe-out | rammed: stepped in, round 149, 2 long | alive, 3 long |
| 6 | 1052762 | Queen Of Spades (875) | dl-20261004 | (5, 11) | test4 | lost by wipe-out | rammed: stepped in, round 247, 4 long | alive, 2 long |
| 7 | 1063018 | Queen Of Spades (875) | qh31-old | (5, 11) | test4 | won at round 500 (longest) | rammed: stepped in, round 417, 17 long | own ram, round 146, 2 long |
| 8 | 1023823 | Australia (4096) | dl-20261004 | (39, 44) | forgot to ment | lost at round 500 (queen rule) | rammed: stayed in, round 81, 3 long | alive, 19 long |
| 9 | 1045382 | Queen Of Spades (875) | dl-20261004 | (5, 11) | WeHaveQuizzes | lost at round 500 (longest) | rammed: stayed in, round 36, 3 long | rammed: unseen, round 259, 2 long |
| 10 | 1052754 | weakhold (600) | dl-20261004 | (2, 3) | test4 | lost at round 500 (longest) | rammed: stayed in, round 80, 3 long | boxed in: terrain dead end, round 210, 2 long |
| 11 | 1045377 | Maze (1152) | dl-20261004 | (43, 8) | WeHaveQuizzes | lost at round 500 (longest) | rammed: stayed in, round 197, 3 long | boxed in: terrain dead end, round 325, 2 long |
| 12 | 1044201 | Around UNSW (4096) | dl-20261004 | (43, 21) | test4 | lost at round 500 (longest) | rammed: stayed in, round 85, 3 long | boxed in by a team-mate, round 299, 3 long |
| 13 | 1052760 | Around UNSW (4096) | dl-20261004 | (20, 42) | test4 | won at round 500 (longest) | rammed: cornered, round 44, 2 long | boxed in by a team-mate, round 293, 3 long |
| 14 | 1044510 | Australia (4096) | dl-20261004 | (24, 19) | WeHaveQuizzes | lost at round 500 (longest) | rammed: cornered, round 62, 2 long | rammed: unseen, round 86, 2 long |
| 15 | 1053021 | Maze (1152) | dl-20261004 | (43, 8) | WeHaveQuizzes | lost at round 500 (longest) | rammed: cornered, round 117, 2 long | boxed in by a team-mate, round 227, 7 long |
| 16 | 1052761 | Default (1024) | dl-20261004 | (31, 31) | test4 | lost by wipe-out | rammed: cornered, round 289, 2 long | alive, 3 long |
| 17 | 1053778 | Around UNSW (4096) | dl-20261004 | (20, 42) | WeHaveQuizzes | lost at round 500 (longest) | rammed: cornered, round 56, 3 long | boxed in by a team-mate, round 355, 2 long |
| 18 | 1027975 | Islands (2240) | stride-old | (45, 7) | WeHaveQuizzes | lost at round 500 (longest) | rammed: cornered, round 189, 2 long | boxed in: terrain dead end, round 348, 2 long |
| 19 | 1045195 | Around UNSW (4096) | dl-20261004 | (43, 21) | test4 | lost at round 500 (longest) | rammed: unseen, round 54, 2 long | boxed in by a team-mate, round 170, 4 long |
| 20 | 1052766 | Trauma (1152) | dl-20261004 | (4, 15) | test4 | lost at round 500 (queen rule) | rammed: unseen, round 445, 34 long | alive, 39 long |
| 21 | 1053379 | Islands (2240) | dl-20261004 | (45, 7) | test4 | lost by wipe-out | rammed: unseen, round 133, 2 long | alive, 75 long |
| 22 | 1045388 | Slithery Fight (1701) | dl-20261004 | (3, 22) | WeHaveQuizzes | lost at round 500 (queen rule) | rammed: unseen, round 356, 48 long | alive, 94 long |
| 23 | 1053032 | Slithery Fight (1701) | dl-20261004 | (3, 22) | WeHaveQuizzes | won at round 500 (longest) | boxed in by a team-mate, round 3, 2 long | rammed: unseen, round 278, 5 long |
| 24 | 1045387 | Portals (512) | dl-20261004 | (31, 10) | WeHaveQuizzes | lost at round 500 (queen rule) | boxed in by a team-mate, round 9, 5 long | alive, 46 long |
| 25 | 1045380 | Around UNSW (4096) | dl-20261004 | (20, 42) | WeHaveQuizzes | lost at round 500 (longest) | boxed in by a team-mate, round 96, 2 long | boxed in: terrain dead end, round 101, 16 long |
| 26 | 1044207 | Trauma (1152) | dl-20261004 | (43, 8) | test4 | lost at round 500 (queen rule) | boxed in by a team-mate, round 458, 2 long | alive, 36 long |
| 27 | 1053380 | Maze (1152) | dl-20261004 | (4, 15) | test4 | lost at round 500 (queen rule) | boxed in by a team-mate, round 206, 2 long | alive, 56 long |
| 28 | 1045196 | Default (1024) | dl-20261004 | (0, 0) | test4 | won at round 500 (longest) | boxed in by a team-mate, round 348, 2 long | rammed: cornered, round 394, 6 long |
| 29 | 990346 | Slithery Fight (1701) | dl-20261003 | (3, 22) | Team SKKU | lost at round 500 (queen rule) | boxed in by an enemy body, round 386, 2 long | alive, 3 long |
| 30 | 1023828 | Maze (1152) | dl-20261004 | (4, 15) | forgot to ment | won at round 500 (longest) | boxed in: terrain dead end, round 107, 2 long | boxed in: terrain dead end, round 154, 2 long |
| 31 | 1044208 | Portals (512) | dl-20261004 | (0, 5) | test4 | lost at round 500 (longest) | boxed in: terrain dead end, round 108, 2 long | boxed in: terrain dead end, round 320, 3 long |
| 32 | 1045203 | Slithery Fight (1701) | dl-20261004 | (59, 4) | test4 | lost at round 500 (queen rule) | boxed in: terrain dead end, round 211, 2 long | alive, 65 long |
| 33 | 1023830 | Prisoners Dilemma (512) | dl-20261004 | (3, 6) | forgot to ment | lost by wipe-out | boxed in: terrain dead end, round 91, 2 long | alive, 2 long |
| 34 | 1053777 | Tower Defense (512) | dl-20261004 | (26, 11) | WeHaveQuizzes | lost at round 500 (longest) | own ram, round 162, 2 long | rammed: cornered, round 197, 2 long |
| 35 | 1053772 | weakhold (600) | dl-20261004 | (2, 3) | WeHaveQuizzes | lost at round 500 (longest) | own ram, round 70, 2 long | own ram, round 167, 3 long |
| 36 | 993428 | Around UNSW (4096) | dl-20261003 | (20, 42) | horse | lost at round 500 (longest) | own ram, round 226, 2 long | boxed: own body, round 278, 16 long |
| 37 | 1045201 | Trauma (1152) | dl-20261004 | (43, 8) | test4 | won at round 500 (queen rule) | alive, 26 long | alive, 25 long |
| 38 | 1044521 | Trauma (1152) | dl-20261004 | (43, 8) | WeHaveQuizzes | lost at round 500 (queen rule) | alive, 38 long | alive, 58 long |
| 39 | 1044205 | Trophy (625) | dl-20261004 | (20, 9) | test4 | won by wipe-out | alive, 2 long | rammed: cornered, round 78, 2 long |
| 40 | 1045381 | Default (1024) | dl-20261004 | (31, 31) | WeHaveQuizzes | won by wipe-out | alive, 2 long | rammed: cornered, round 249, 2 long |

| # | game | map (cells) | team read | its start | opponent | result | its queen |
|---|---|---|---|---|---|---|---|
| T1 | 1046537 | Around UNSW (4096) | SSS | (20, 42) | test4 | won at round 500 (longest) | boxed in by a team-mate, round 472, 2 long |
| T2 | 1055129 | Around UNSW (4096) | Vibing++ | (20, 42) | test4 | won at round 500 (queen rule) | alive, 52 long |
| T3 | 1054798 | Around UNSW (4096) | Vibing++ | (43, 21) | test4 | lost at round 500 (longest) | rammed: unseen, round 438, 40 long |
| T4 | 1046528 | Australia (4096) | SSS | (39, 44) | test4 | won at round 500 (queen rule) | alive, 35 long |
| T5 | 1046526 | Maze (1152) | SSS | (43, 8) | test4 | won at round 500 (queen rule) | alive, 93 long |
| T6 | 1051826 | Islands (2240) | SSS | (10, 7) | test4 | won at round 500 (longest) | rammed: unseen, round 368, 4 long |
| T7 | 1046534 | Default (1024) | SSS | (31, 31) | test4 | won at round 500 (longest) | rammed: unseen, round 438, 3 long |
| T8 | 1046539 | weakhold (600) | SSS | (2, 3) | test4 | won by wipe-out | alive, 2 long |
| T9 | 1046535 | Tower Defense (512) | SSS | (5, 4) | test4 | won by wipe-out | alive, 2 long |
| T10 | 1054786 | Trauma (1152) | SSS | (43, 8) | test4 | won at round 500 (queen rule) | alive, 32 long |
| T11 | 1046991 | Trauma (1152) | forgot | (43, 8) | test4 | won at round 500 (queen rule) | alive, 46 long |
| T12 | 1054774 | Portals (512) | SSS | (31, 10) | test4 | won at round 500 (queen rule) | alive, 29 long |
| T13 | 1051825 | Portals (512) | SSS | (31, 10) | test4 | lost at round 500 (longest) | boxed in: terrain dead end, round 341, 3 long |
| T14 | 1062234 | Portals (512) | forgot | (0, 5) | WeHaveQuizzes | won at round 500 (queen rule) | alive, 28 long |
| T15 | 1046531 | Slithery Fight (1701) | SSS | (3, 22) | test4 | won at round 500 (queen rule) | alive, 45 long |
| T16 | 1046988 | Slithery Fight (1701) | forgot | (3, 22) | test4 | lost at round 500 (queen rule) | alive, 16 long |
| T17 | 1064308 | Devil (512) | SSS | (3, 5) | test4 | won by wipe-out | rammed: stepped in, round 17, 2 long |
| T18 | 1046541 | Devil (512) | SSS | (3, 5) | test4 | won by wipe-out | rammed: stayed in, round 18, 3 long |

Game 29 is a "cut and stuck" death in the table of section 2: the queen cut herself from 57 to 2 while boxed in by an enemy body and died the next round.

## 4. The kinds of death, game by game

Board legend: `@` queen of side A, `&` queen of side B, `A` / `B` other heads, `a` / `b` bodies, `*` pearl, `|` and `-` kelp, `O` portal. Rows are y (south is down), columns x. Every board shows the start of the queen's own turn. "#124" is a dragon id. Game numbers refer to the table in section 3.

### 4.1 Rammed after stepping into reach (66 games; games 1 to 7)

**What the board shows.** The killer is in her view, she is outside its reach, at least one step keeps her outside, and she takes a step that does not. The killer is 3 or shorter in 52 of the 66 and never longer than 4. Its ramming move has 2 or more steps in 48 of the 66 (1 / 2 / 3 / 4 / 5 steps: 18 / 23 / 16 / 8 / 1). She ate a pearl on the fatal step in 1 of the 66, so this is not pearl greed. In 56 of the 66 a roomy safe step existed.

**Game 1 (980372, Around UNSW, ladder 3 Oct).** Our queen splits 4 into 2+2 at round 1 and eats nothing in 94 rounds. From round 87 she walks a 2x2 loop: (24,42), (24,43), (25,43), (25,42). An enemy 3-long, #124, comes up from the south-east; it is in her view at round 89 and again from round 92. Round 92: she is at (24,43), it is at (24,46); she steps east (safe). Round 93: it is at (24,45); she steps north (safe). Round 94:

```
     22232425262728
 39   a . . . . . .
 40  |. . . . . . .
     +-+
 41   .|. . . . . .
 42   .|. . @ . . .
 43   .|. . a . . .
     +-+
 44   .|. B . . . .
 45   .|. b . . . .
```

North (25,41) and east (26,42) are 4 steps from #124's head; west (24,42) is 2 steps from it, and a 3-long reaches 2. She steps west, the next cell of her loop. #124 moves `NN` and rams her. Inference from the code: the cell (24,42) costs her 337 points of threat penalty (450 x 0.5 for a 2-long x 1.5 for depth 2), which the other terms of the step score outweighed. Another enemy, #148, had been in her view at rounds 90 and 91 to the north-east; our queen keeps such sightings for three rounds and spreads a growing penalty from them, which may have put the same 337 points on the two safe cells. The replay cannot show that.

**Game 2 (1053773, Australia, ladder).** By round 50 she is 31 path steps from her start with no own head within 4 cells. Two WHQ dragons (a 2-long and a 3-long) keep 3 steps behind her from round 60 to round 74. She walks east along a kelp wall into a corner cell (29,39) whose exits are south, inside the 3-long's reach, and west through a portal. The portal step was safe; our queen rule forbids portal steps, and she steps south. This is the one game of the 66 in which the only roomy safe step was a portal.

**Game 3 (1045200, Devil, ladder, rules off).** She walks east along row 7 to the middle of the map, eats two pearls, splits twice, turns into the centre lane and at round 18 steps from (14,4) to (15,4), the cell next to the head of an enemy 2-long at (16,4). North and south were free and safe. Four of our Devil games end exactly like this at round 18 (section 5d). test4's queen in the same game splits once at round 0 and then walks the loop N, E, S, W on four cells at her start for the whole game; none of our heads ever comes into her view.

**Games 4 and 5 (1053020 Islands, 1044202 Default).** In game 4 she is 24 path steps from her start, has had an enemy head in view in 20 of her last 21 rounds, and has eaten no natural pearl since round 50. In game 5 she has eaten nothing in 149 rounds, has had an enemy head in view in 15 to 17 of every 25 rounds since round 75, and has 0.1 to 0.3 own heads within 4 cells. Five enemy heads stand within 5 cells of her at round 149. She steps north toward a pearl two cells away; a 4-long reaches her there in 4 steps by going round a portal edge and over that pearl (`WSES`). South was out of reach.

**Game 6 (1052762, Queen Of Spades).** From round 25 to round 247 she has an enemy head in view in three rounds out of four (12 to 24 of every 25 rounds) and lives, so she does dodge most of the time. At round 247 she steps east into the reach of a 3-long that needs 4 steps and a pearl on the way.

**Game 7 (1063018, Queen Of Spades, qh31-old).** A fed queen, 17 long, at round 417. Her safe step leads into a pocket of 7 cells, too small for 17 segments; the other step is inside a 3-long's reach. She takes that one and dies. This is not avoidable on the last turn; 10 of the 66 are of this "safe step into a pocket" sort.

**The opponent's queen, and the top three.** Our opponents' queens die this way in 15 of 401 games, the top three in 59 of 1,637 (3 to 4% each). In the top three's 74,030 turns that began outside reach with a safe step, they ended in reach in 138 (0.19%); ours in 81 of 10,705 (0.76%). SSS's queen from our Devil start (T17, T18) dies at rounds 17 and 18 too: Devil is deadly for every queen that walks to the middle (dead before round 50: top three 61 of 114 games, ours 23 of 30).

### 4.2 Rammed after staying in reach (38 games; games 8 to 12)

**What the board shows.** She begins the turn inside a visible enemy's reach, a safe step exists, and she ends in reach again. Here pearls do matter: she ate on the fatal step in 17 of the 38, and ended next to an enemy head in 18.

**Game 8 (1023823, Australia, against forgot).** She is 36 path steps from her start at round 75 (the enemy's start is 40 away) with no own head near. Round 81:

```
     10111213141516
 47   . . . . . . .
 48   . B * @ . . .
 49  O. b . a . . .
 50   . b . . . . B
```

A pearl lies between her head (13,48) and the head of forgot's 3-long #52 at (11,48). East (14,48) is safe. She steps west onto the pearl and #52 rams her with one step. Inference from the code: a pearl on the next cell is worth 300 (`EAT_BONUS`) plus up to 440 (target bonus) to her; the threat penalty of the cell next to a 3-long's head is 450 for a 2-long queen.

**Games 9 and 10 (1045382 Queen Of Spades round 36, 1052754 weakhold round 80).** The same picture: a pearl one step away, inside the reach of a 2-long and a 3-long; she eats it and is rammed.

**Game 11 (1045377, Maze).** At round 196 she is 4 long and splits into 2+2 while a 5-long is in her view (3 cells away, 9 steps by path). At round 197 it has grown to 6 and can reach the pearl west of her in 6 steps; east is safe. She takes the pearl. It rams her with `NNENES`.

**Game 12 (1044201, Around UNSW).** She stays 8 to 9 cells from her start all game. test4 has 62 dragons against our 34 at round 75 and they are in her home. At round 85 a 5-long is 3 cells away; her one safe step is a one-cell dead end. She is in effect cornered; 2 of the 38 are like this.

**The top three.** Inside reach with a safe step, their queens end in reach again in 9% of such turns (173 of 1,837), ours in 19% (68 of 358).

### 4.3 Rammed when cornered (114 games; games 13 to 18)

**What the board shows.** The killer is in view and no one-step move ends outside reach. She had exactly one free step in 56 of the 114 (in 38 of those she began outside reach and her only step led into it), two in 39, three in 16, none in 3. The killer is 3 or shorter in 84. The top three have the same shape (one free step in 255 of 476).

**Game 14 (1044510, Australia): herded along a wall.** A WHQ 2-long, #5, is on the diagonal behind her from round 59. She walks west along a kelp wall; each round her step west is safe and her step south is next to its head; it follows one cell behind on the open side. Round 62:

```
     17181920212223
 11   . . . . . . .
     + + + +-+-+-+-
 12   . . .|@ a . .
     +-+-+-+
 13  |. . . . B b .
```

The wall turns. Her only free cell is (20,13), next to #5's head at (21,13). One 2-long with a reach of 1 was enough, because the wall took her other exits four rounds earlier.

**Game 17 (1053778, Around UNSW).** The same with a wall on one side and one enemy 2-long on the forward diagonal: both her free cells are next to its head.

**Game 13 (1052760, Around UNSW).** At round 43 she steps east toward a group of seven test4 heads she cannot see yet (the nearest is 5 cells away). At round 44 a 5-long is in view 3 steps away and every cell she can step to is inside its reach of 5.

**Game 15 (1053021, Maze).** After building the economy for 40 rounds near her start she crosses the maze westward for 30 rounds, to more than 21 steps from her start with 0.3 own heads near. Three WHQ 3-longs are within 2 to 3 cells when she walks north into a corridor with one way on.

**Game 18 (1027975, Islands).** A queen that did stay home: she farms the pearls at her start for 100 rounds (4 to 5 pearls and 2 to 3 splits per 25 rounds, never more than 7 cells away). At round 187 WHQ dragons arrive there; she steps into a two-exit nook and the second exit is next to an enemy head.

**Game 16 (1052761, Default).** Our team has 2 dragons against 52. Not a queen problem.

**How the corner is made.** Three turns before the ram the later killer was in her view in only 34% of our rammed deaths (top three: 32%); one turn before, in 60%. So most corners close within two turns. What differs between teams is not how often a queen is cornered once an enemy is near (section 5b), but how often an enemy is near.

### 4.4 Rammed by an enemy she could not see (31 games; games 19 to 22)

**What the board shows.** In 28 of the 31 the killer began its ramming move 3 cells (Chebyshev) from the cell she died on: it stood just outside her 7x7 view, 4 cells from her, and her own step brought her inside its range. The killer is 5 or longer in 13, or a 3- or 4-long that ate a pearl on the way. Nothing on her screen warned her: its head had not been in her view in any of her last three turns in all 31.

**Games 20 and 22 (1052766 Trauma, 1045388 Slithery Fight): fed queens that outrun their eyes.** Our queen is fed from round 300 and by round 445 is 34 long (game 20) or 48 long at round 356 (game 22). She then takes six steps every turn (`WNNNWW`, `NENNEE`), all free at that length. In game 20 her sixth step ends next to the head of a test4 2-long that was 4 cells from her when the turn began; in game 22 an 8-long that was 6 cells away rams her with 4 steps. Eight of our 16 rammed queens of 6 or more died right after a move of 3 or more steps.

**Game 19 (1045195, Around UNSW).** At round 53 she is 4 long and splits into 2+2 with a test4 2-long 3 steps away in her view; at round 54 she steps west and a 3-long from 4 cells away rams her in 3 steps over a pearl.

**The top three.** They die this way at our rate (0.49 against 0.55 per 1,000 queen-rounds). It is the price of any queen that moves, and the one kind in which we are not worse.

### 4.5 Boxed in by her own team (58 games; games 23 to 29)

The 58 are four different things: 13 queens that had cut themselves short and died inside the child (a 14th died against an enemy body, game 29), 11 with their own recent split child on the last exit, 20 nose to nose with a team-mate's head, and 14 with another team-mate's body on the last exit.

**a. Cut and stuck (14 games; games 23, 26, 28, 29).** Game 23 (1053032, Slithery Fight) at round 0:

```
      0 1 2 3 4 5 6            round 3:   1 2 3 4 5 6 7
 20  |. a a a a a .                  20   a a a a a . .
 21  |. a a a a a .                  21   a a A @ a . .
 22  |. a a @ a a .                  22   a . . a a . .
 23  |. a a a a a .                  23   a A . . a . .
 24  |. a a a a a .                  24   a a . a a . .
```

Every queen starts this map 25 long, coiled, with no free cell. Ours gives one order: split so that she keeps 2 and the child gets 23. The child's 23 segments are the coil around her. She steps east, north, and at round 3 has the child's body on two sides and a new 2-long's head on the third. She dies there in 10 of our 29 Slithery Fight games; in the other 19 she gets out, 2 long. From the same start cell SSS (T15) and forgot (T16) shed 2 from the tail eleven rounds in a row (25, 23, 21, ... 5, 3), make eleven 2-longs, lose nothing, and walk out 3 long at round 11.

The same order kills fed queens late. Game 29 (990346, Slithery Fight): our queen is 57 long at round 385, walks into a pocket closed by an enemy 17-long's body, cuts 57 into 2+55 and dies at round 386. Team SKKU's queen ends the game 3 long: with our queen alive at any length this is a queen-rule win. Game 26 (1044207, Trauma) at round 457:

```
     40414243444546
 19   . . a a . . .
 20   a a a a . . .
 21   a a a a a a a
 22   a a a @ a a a
 23   a a a a a a .
```

She is 32 long, has been taking six steps a turn inside her own home for 30 rounds, and has wound herself in: all four sides are her own body (segments 23, 25, 1 and 15). She cuts 32 into 2+30 and dies inside the child at round 458. test4's queen ends 36 long. Shedding 2 from the tail would have opened the first of those cells after four rounds, at length 24. Game 28 (1045196, Default): the same at 15 long, round 347.

**b. Her own split child on her exit (11 games; game 24).** Game 24 (1045387, Portals, rules off) at round 9:

```
      1 2 3 4 5 6 7
     + + + +-+-+ +
  4   . . b b & . .
  5   . . . . . . .
     + + + +-+-+ +
  6   . . .|a a|. .
     + + +O+O+ + +
  7   . . .|@ a|. .
     + + + +-+-+ +
  8   . . . . . . .
```

At round 4 she steps through a portal from (28,9) into a kelp room of four cells with a pearl on each. The room lies in the enemy's area (WHQ's queen `&` is two cells north of it) but opens only through that portal. At round 5, 4 long, she splits; the child is born on the far side of the portal, in our home. She eats the other three pearls and is 5 long in a room of 4 cells at round 9. The only way out of (4,7) is north through the portal edge to (28,8), which she cannot see. Her child, which wandered north on the far side, has its tail on (28,8). She steps onto it. Seven games end at this cell at round 9 and four at the mirrored cell at rounds 9 and 10.

On this map the two homes are not connected at all (from a start cell 240 of the 512 cells can be reached with portals and the enemy's start is not among them; `d_conn.py`), so no hunter can reach a queen: ours is dead in 27 of 27 games, never by a ram; the top three's is alive at the end in 52 of 106. SSS's queen from the same start (T12, T13) does not take the portal, eats no natural pearl in the whole game and does not split before round 100. In T12 she walks to a spot 20 to 25 steps from her start and stays there on 4 to 16 cells per 25 rounds from round 50 to round 300, with 1 to 3 own heads within 4 cells, and is fed to 29 at the end. forgot's queen (T14) sits 1 to 5 cells from her start from round 50 to round 150 with 4 to 5 own heads within 4 cells, eats nothing, and is fed from round 200.

**c. Nose to nose (20 games; games 25, 27).** Game 25 (1045380, Around UNSW) at round 96:

```
     1112131415
 26   . . a . .
 27   . . A . .
     + + + +-+
 28   . a @|. .
     + + +-+
```

At round 95 she steps east into (13,28), a cell with one way on, north. Our 2-long #29 then steps south onto (13,27). At round 96 she has kelp east and south, her own tail west and #29's head north. She dies; #29 eats her pearl. In 12 of the 20 the space around her was open until the last turn. The top three have this too (forgot 8 games of 632, SSS 8 of 503, Vibing++ 34 of 502; ours 20 of 401).

### 4.6 Boxed in a terrain dead end (30 games; games 30 to 33)

**Game 30 (1023828, Maze, against forgot, rules on)** at round 95:

```
     27282930313233
  0   . . a * * . .
     + + + +-+-+-+-
  1  |a A|a @ . * .
     +-+-+-+ +-+-+O
  2   a . .|*|*O.|.
  3  |A . .|* *|*O.
     + + + +-+-+-+
```

East (31,1) is open water. South (30,2) is the mouth of a one-wide corridor with a pearl on every cell: (30,2), (30,3), (31,3), (31,2), then a portal to five more cells that end at a wall. She steps south. From here every turn has one free step, most of them with a pearl on it. She eats seven pearls, splits twice on the way (the children walk back out), reaches the last cell 6 long at round 105, cuts 6 into 2+4 at round 106 and dies at round 107. For any other dragon of ours this is a good trade: seven pearls come out and a 2-long is lost. For the queen it is her life for seven pearls.

**Games 31 to 33 (Portals, Slithery Fight, Prisoners Dilemma).** The same walk: a portal step onto a pearl in a one-cell nook (31, rules off), a corridor of pearls with a 3-long two cells behind her (32), a corridor of three pearls (33). In all four she split or cut inside.

**Counts.** On the turn she entered, she stepped onto a pearl in 16 of the 30 and a roomier free side existed in 21. She ate inside in 26 and split inside in 18. 21 of the 30 are on maps of 600 cells or fewer. The top three die this way at a third of our rate.

### 4.7 She rams an enemy head herself (19 games; games 34 to 36)

In 9 of the 19 she was boxed in and the enemy head was her only side that was not kelp or a body (games 35 and 36: a one-wide corridor with an enemy 2-long coming the other way; kelp, a team-mate's body and an enemy head). In the other 10 she had a free safe cell and chose the ram; all 10 are on maps of 600 cells or fewer, where she is an ordinary small dragon that trades on contact. Game 34 (1053777, Tower Defense): our team has 4 dragons against 33, a WHQ 2-long has followed her through her home room for two rounds, north and west are free and safe, and she steps east into its head. The head she takes with her is 2 or 3 long in all 19. SSS's queen never does this with a free cell (9 own rams, all boxed in).

### 4.8 The 39 queens that lived (games 37 to 40)

Fifteen are on Trauma, where the two homes are separated by portals (the path between the starts is 98 steps); 14 on Trophy, 4 on Default, 3 on Prisoners Dilemma and 1 each on Autarky, Devil and Queen Of Spades, all 24 of them games we won by wipe-out. In game 37 (Trauma) no enemy head came within 8 path steps of her in 500 rounds and she won the game 26 to 25 on queen length. In game 39 (Trophy) the enemy had 5 dragons at round 50 and 1 at round 150. In game 40 (Default) she had an enemy head in view in 52 of the rounds 25 to 100, the nearest one step away, and lived; we won the fight around her. So our queen lives where no hunter comes, or where the hunters die first. Of the 39 games, 24 are wipe-out wins, 4 are round-500 wins and 11 are round-500 losses on Trauma with her queen alive and longer.

## 5. Answers to the eight questions

Each count names its script and output file in brackets. All scripts are in this directory; outputs are in `d_out/`.

### a. Every death, classified

The tables are in section 2 [`d_md.py`, `md_class.md`; `d_haz.py`, `haz.txt`; `d_box.py`, `box.txt`]. In one paragraph:

- Of our 362 queen deaths, 251 are rams, 91 are boxed-in deaths, 19 are her own rams and 1 is a portal step onto a body. Of the rams, 104 happened on a turn on which a safe step existed and she ended in reach (66 stepped in, 38 stayed in), 114 when cornered, 2 on a cell the model called safe, and 31 by an enemy she could not see.
- By round band (0-49 / 50-99 / 100-299 / 300+): all deaths 80 / 100 / 156 / 26. The avoidable rams are spread over the first three bands (22 / 33 / 45 / 4); the boxed-in deaths by a team-mate are heaviest in the opening (23 / 13 / 18 / 4) because of two patterns (question d); terrain dead ends come later (2 / 11 / 16 / 1).
- Live bot against candidates: the shares are the same within noise (alive 10% and 10%; stepped or stayed in 25% and 29%; cornered 26% and 33%; boxed by a team-mate 16% and 12%). No candidate changed how the queen dies.
- Rules on against rules off (live bot, deaths per 1,000 queen-rounds): all 5.0 against 10.7; boxed by bodies 0.7 against 2.6; terrain 0.3 against 1.4; own rams 0.07 against 1.5; avoidable rams 1.5 against 2.4; cornered 1.7 against 2.4.
- Her length at death is 2 or 3 in 314 of the 362 (2 long: 188, 3 long: 126). The killer is 3 or shorter in 183 of the 251 rams and 4 long in 37; its ramming move had one step in 82, two in 76, three or more in 93.
- What the games became: section 2, last table. 102 of the 362 are round-500 losses with both queens dead.

### b. Avoidable or not

[`d_b.py`, `b.txt`; `d_expo.py`, `expo.txt`; `d_ramdet.py`, `ramdet.txt`]

**The last six turns before a ram** (251 of ours, 797 of the top three; first number ours, second the top three):

| Her own turn, counted back from the ram | last | 2nd last | 3rd last | 4th last | 5th last | 6th last |
|---|---|---|---|---|---|---|
| an enemy head in her view | 94% / 84% | 75% / 73% | 65% / 68% | 61% / 61% | 55% / 58% | 52% / 54% |
| the later killer in her view | 88% / 76% | 60% / 55% | 41% / 39% | 34% / 32% | 28% / 25% | 25% / 22% |
| free one-step moves (mean) | 2.1 / 1.9 | 2.3 / 2.1 | 2.3 / 2.2 | 2.4 / 2.3 | 2.4 / 2.2 | 2.4 / 2.3 |
| safe one-step moves (mean, turns with an enemy in view) | 0.8 / 0.4 | 1.8 / 1.5 | 2.0 / 1.7 | 2.1 / 1.9 | 2.1 / 1.8 | 2.2 / 1.9 |
| a safe step existed (of turns with an enemy in view) | 51% / 28% | 96% / 91% | 99% / 96% | 100% / 96% | 99% / 95% | 98% / 96% |
| she ended in reach (of those turns) | 93% / 89% | 6% / 9% | 1% / 5% | 1% / 4% | 1% / 4% | 2% / 3% |
| she ended in reach although a safe step existed (of those turns) | 44% / 17% | 2% / 2% | 0% / 1% | 1% / 1% | 0% / 1% | 1% / 1% |

Everything is decided on the last turn. On it our queen had a safe step in half of her rammed deaths and a top-three queen in a quarter of hers.

**Shares of the rammed deaths with a way out:**

| | meow, all (251 rams) | live bot (165) | our opponents (102) | forgot (327) | SSS (240) | Vibing++ (230) | top three (797) |
|---|---|---|---|---|---|---|---|
| last turn: killer in view and a safe step existed | 106 (42%) | 70 (42%) | 28 (27%) | 48 (15%) | 41 (17%) | 38 (17%) | 127 (16%) |
| ... she ended in reach although a roomy safe step that crossed no portal existed | 90 (36%) | 59 (36%) | - | - | - | - | 71 (9%) |
| last turn: killer in view, safe only by paying segments for a longer move | 35 (14%) | 21 (13%) | 16 (16%) | 60 (18%) | 34 (14%) | 13 (6%) | 107 (13%) |
| in one of her last three turns she ended in reach although a safe step existed | 107 (43%) | 71 (43%) | 32 (31%) | 46 (14%) | 41 (17%) | 37 (16%) | 124 (16%) |
| in one of her last three turns the killer was in view and a safe step existed | 185 (74%) | 122 (74%) | 85 (83%) | 213 (65%) | 133 (55%) | 132 (57%) | 478 (60%) |

**Every turn of every game with an enemy head in view** (not only the fatal ones), per 1,000 queen-rounds:

| | meow, all | live bot | meow against test4 / WHQ | our opponents | forgot | SSS | Vibing++ | top three | top three against test4 / WHQ |
|---|---|---|---|---|---|---|---|---|---|
| share of her rounds with an enemy head in view | 20.2% | 20.5% | 20.3% | 17.0% | 20.7% | 17.9% | 21.1% | 19.8% | 20.5% |
| A. outside reach, safe step exists: she ends in reach (share of such turns) | 0.76% | 0.68% | 0.77% | 0.42% | 0.18% | 0.15% | 0.23% | 0.19% | 0.06% |
| A. the same per 1,000 queen-rounds | 1.45 | 1.32 | 1.49 | 0.67 | 0.35 | 0.27 | 0.46 | 0.35 | 0.12 |
| B. in reach, safe step exists: she ends in reach again (share of such turns) | 19% | 17% | 21% | 13% | 10% | 8% | 10% | 9% | 11% |
| B. the same per 1,000 queen-rounds | 1.22 | 1.22 | 1.08 | 0.79 | 0.46 | 0.31 | 0.59 | 0.44 | 0.28 |
| C. no safe step (cornered), per 1,000 queen-rounds | 2.77 | 2.39 | 2.48 | 3.92 | 3.07 | 2.16 | 3.54 | 2.88 | 2.15 |
| all turns that end in reach, per 1,000 queen-rounds | 5.44 | 4.94 | 5.05 | 5.39 | 3.88 | 2.73 | 4.59 | 3.67 | 2.55 |
| ... of which by her own choice (A + B) | 2.66 | 2.54 | 2.57 | 1.46 | 0.81 | 0.57 | 1.05 | 0.79 | 0.40 |
| rammed on a turn that ended in reach | 71% | 72% | 77% | 16% | 44% | 47% | 32% | 40% | 67% |

Three things follow. Our queen sees an enemy head as often as anyone (one round in five). She is cornered as often as the top three. She ends in reach by choice 3.4 times as often as they do, and 6.4 times as often against the same two opponents. And a turn in reach costs her life 71% of the time (77% against test4 and WHQ), because those two take the ram; they take it 67% of the time against the top three as well. By map size the "by choice" rate is 3.3 (ours) against 0.6 (top three) on large maps, 1.3 against 0.5 on medium, 4.4 against 1.3 on small [`d_expo_size.py`, `expo_large.txt` and so on].

**Does she step nearer to a visible small enemy head?** Turns with an enemy head of 4 or shorter in view on which a nearer and a farther one-step move both existed; share on which she took the nearer one, by the path distance to that head:

| Distance to the small enemy head | meow live, rules on | meow live, rules off | our opponents | forgot | SSS | Vibing++ | top three against test4 / WHQ |
|---|---|---|---|---|---|---|---|
| 2 steps | 14 of 365 (4%) | 15 of 56 (27%) | 5% | 2% | 3% | 2% | 2% |
| 3 steps | 75 of 784 (10%) | 74 of 154 (48%) | 12% | 5% | 7% | 16% | 14% |
| 4 steps | 271 of 906 (30%) | 59 of 88 (67%) | 12% | 5% | 8% | 32% | 13% |
| 5 or more | 344 of 855 (40%) | 184 of 286 (64%) | 23% | 47% | 20% | 37% | 33% |
| all | 24% | 57% | 16% | 19% | 12% | 27% | 22% |

With the rules on she behaves like the top three at 2 and 3 steps and like Vibing++ (whose queen is longer: 4.9 on average in rounds 100 to 149) at 4 steps; SSS and forgot keep away at 4 steps in 92 to 95% of such turns. With the rules off she walks toward a small enemy head half the time at any distance. Only 5% of her nearer steps ate a pearl.

### c. How she lives

[`d_life.py`; `d_c.py`, `c_all.txt`, `c_large.txt`, `c_medium.txt`, `c_small.txt`; `d_where.py`, `where_all.txt`; `d_where2.py`, `where_r50_150.txt`]

Per 50 rounds, all maps (the live bot's queen; "q / team" = the queen against the other heads of her team, or for pearls against the whole team per dragon-round):

| | rounds | meow live | our opponents | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|
| natural pearls per 100 rounds, q / team | 0-49 | 4.7 / 7.2 | 4.9 / 7.6 | 4.6 / 7.6 | 4.1 / 6.7 | 4.7 / 8.1 |
| | 50-99 | 3.3 / 4.9 | 3.6 / 5.7 | 3.2 / 5.8 | 2.4 / 5.3 | 4.2 / 6.2 |
| | 100-149 | 2.2 / 3.6 | 2.4 / 4.3 | 1.3 / 4.2 | 1.6 / 4.2 | 2.3 / 4.8 |
| | 150-199 | 1.4 / 2.9 | 2.0 / 3.8 | 1.1 / 3.8 | 1.6 / 3.7 | 1.7 / 4.5 |
| path distance from her start, q / team | 0-49 | 9.4 / 17.4 | 8.3 / 19.4 | 11.4 / 18.7 | 9.5 / 19.4 | 10.5 / 20.1 |
| | 50-99 | 14.7 / 19.8 | 12.7 / 22.6 | 15.0 / 21.4 | 12.3 / 23.1 | 16.9 / 23.2 |
| | 100-149 | 14.3 / 21.0 | 13.6 / 24.0 | 11.8 / 22.2 | 12.7 / 23.7 | 18.4 / 24.9 |
| | 150-199 | 14.1 / 22.2 | 14.4 / 25.2 | 9.7 / 23.2 | 13.0 / 24.0 | 19.2 / 26.1 |
| share of rounds on the enemy's side, q / team | 50-99 | 17% / 21% | 13% / 24% | 20% / 23% | 8% / 24% | 16% / 23% |
| | 100-149 | 15% / 21% | 11% / 26% | 13% / 21% | 7% / 22% | 14% / 23% |
| rounds with an enemy head in her view | 50-99 | 23% | 18% | 25% | 19% | 23% |
| | 100-149 | 26% | 21% | 23% | 21% | 26% |
| enemy heads within 4 cells, q / team | 100-149 | 0.29 / 0.34 | 0.22 / 0.28 | 0.28 / 0.31 | 0.25 / 0.29 | 0.30 / 0.28 |
| enemy heads within 8 cells, q / team | 50-99 | 1.10 / 1.32 | 1.00 / 1.16 | 1.26 / 1.24 | 1.02 / 1.20 | 1.21 / 1.20 |
| | 100-149 | 1.65 / 1.64 | 1.33 / 1.32 | 1.45 / 1.48 | 1.29 / 1.44 | 1.40 / 1.39 |
| own heads within 4 cells of her | 100-149 | 1.22 | 1.52 | 1.66 | 1.74 | 1.36 |
| | 150-199 | 1.33 | 1.80 | 1.87 | 2.18 | 1.54 |
| her splits per 100 rounds | 0-49 | 3.6 | 3.6 | 4.4 | 4.9 | 3.2 |
| | 100-149 | 1.6 | 1.2 | 1.0 | 1.0 | 1.1 |
| her mean length | 100-149 | 2.5 | 3.0 | 2.7 | 2.6 | 4.9 |
| different cells her head used per 25 rounds | 100-149 | 19.4 | 16.4 | 17.6 | 18.1 | 18.6 |

**Is our queen a forager like any other dragon of ours?** No, and neither is anyone's, but ours is more of one than SSS's or forgot's. She eats half to two thirds of what an average dragon of our team eats (SSS's queen 38 to 61% of her team's rate, forgot's 29 to 60%); in rounds 100 to 149 that is 2.2 natural pearls per 100 rounds against 1.6 and 1.3. She is nearer to her start than her team (14.7 against 19.8 cells in rounds 50-99), but less so than SSS's queen is (12.3 against 23.1). Averaged over all maps, the five queens are close in every row of the table. The larger differences are in three places:

- **Large maps.** In rounds 50 to 199 the live bot's queen has an enemy head in view in 22%, 26% and 22% of her rounds; SSS's 11%, 10%, 11%; our opponents' 10%, 12%, 11%; forgot's 17%, 12%, 11%. Enemy heads within 8 cells of her: 0.97, 1.29, 1.30 (ours) against 0.53, 0.51, 0.61 (SSS) and 0.61, 0.80, 0.77 (our opponents). Her distance from her start grows from 15 to 19 to 22 cells; SSS's from 13 to 15 to 16; forgot's falls from 18 to 15 to 12 [`c_large.txt`].
- **Company.** Our queen has 1.2 to 1.3 own heads within 4 cells in rounds 100 to 199; SSS's has 1.7 to 2.2. For every team the ram rate of a short queen falls steeply with company (rounds 50 to 149, rams per 1,000 queen-rounds with 0 / 1-2 / 3 or more own heads within 6 path steps): ours 9.7 / 4.4 / 2.2; forgot 5.3 / 3.0 / 1.4; SSS 3.1 / 2.1 / 1.0; Vibing++ 4.9 / 3.5 / 0.7; our opponents 2.4 / 0.6 / 0.1. She is alone in 28% of those rounds, SSS's queen in 21% [`where_r50_150.txt`].
- **Distance from home.** Rams per 1,000 queen-rounds of a queen 4 or shorter by distance from her start cell (0-5 / 6-10 / 11-15 / 16-25 / 26 or more cells; all rounds): ours 1.8 / 3.0 / 5.5 / 8.1 / 8.6; SSS 0.8 / 1.6 / 1.7 / 2.9 / 2.5; forgot 1.1 / 2.4 / 4.8 / 4.5 / 4.0; our opponents 0.6 / 0.6 / 1.4 / 1.6 / 1.4. She spends 44% of her rounds more than 10 cells out, SSS's queen 45%: the time is the same, the price is three times higher [`where_all.txt`]. The gradient holds inside each round band (rounds 50 to 149: 3.0 / 4.2 / 5.5 / 8.2 / 5.3).

Two more states make every short queen die faster, ours most [`where_all.txt`]: a cell with one or two open sides (ours 7.6 rams and 9.0 other deaths per 1,000 rounds, against 3.7 and 0.8 on a cell with four open sides; SSS 3.9 and 2.3 against 1.4 and 0.2), and an enemy head within 8 path steps five rounds earlier (ours 10.5 rams per 1,000 rounds with one such head, 18.8 with two or more, 1.3 with none; SSS 6.9, 12.2, 0.4).

**When does a top queen stop foraging forward, and is there a hand-over?** There is no switch at a round in any of the five teams. Every queen begins as the mother of her team: in rounds 0 to 49 she eats 4 to 5 natural pearls per 100 rounds and splits 3 to 5 times per 100 rounds. The taper follows the size of the team (natural pearls and mother splits per 100 rounds while the team has 1-3 / 4-7 / 8-15 / 16-31 dragons at the start of the 50-round block):

| | 1-3 dragons | 4-7 | 8-15 | 16-31 |
|---|---|---|---|---|
| meow live | 4.1 pearls, 2.7 splits | 4.5, 2.5 | 2.9, 1.8 | 2.7, 1.2 |
| SSS | 4.1, 2.7 | 2.6, 1.9 | 2.4, 1.4 | 2.3, 0.9 |
| forgot | 5.1, 3.2 | 3.6, 2.3 | 2.3, 1.2 | 2.1, 0.7 |
| Vibing++ | 5.1, 3.2 | 4.3, 1.1 | 3.3, 1.4 | 2.3, 0.5 |
| our opponents | 4.2, 2.5 | 4.0, 2.2 | 2.1, 1.3 | 2.4, 1.2 |

SSS's queen hands over first: with 4 to 7 dragons in the team she already eats 2.6, ours 4.5. After the first enemy head has come into her view every queen eats about half of what she ate before (ours 4.0 then 2.5; SSS 3.1 then 1.8; forgot 3.9 then 2.0). So ours has the same hand-over as the others in what she eats and how often she splits. What she does not have is the second half of it: staying where her team is. In the SSS and forgot games read, the queen keeps to one area for hundreds of rounds (T1: 1 to 17 path steps from her start, T4: 1 to 19, T5: 2 to 14, T14: 1 to 5; in T12 one spot 20 to 25 steps out) and from round 100 mostly has 1 to 5 own heads within 4 cells; in ours she is 20 to 36 steps out by round 75 to 100 with fewer than one (games 2, 4, 8, 15, 25).

### d. The opening deaths

[`d_open.py`, `open.txt`]

80 of our queens die before round 50 (20% of games; top three 13%; our opponents 5%). By kind: boxed in by her own team 23, cornered 22, stepped in 15, stayed in 7, unseen 5, own ram 5, terrain 2, enemy body 1. By map: Devil 23 of 30 games, Stripes 13 of 29, Portals 12 of 27, Slithery Fight 10 of 29, Trophy 9 of 28, Around UNSW 5, Queen Of Spades 4, Autarky 2, Islands 2; none on the other seven maps. 28 of the 80 are five repeating patterns:

| Pattern | games | rounds | what happens | the general state |
|---|---|---|---|---|
| Slithery Fight, cell (4,21) or its mirror | 10 (7 live) | 3 | She starts 25 long with no free cell, cuts to 2 + 23, steps east, north, and is closed in by the child's body and a new 2-long's head (section 4.5a) | a boxed-in queen of 4 or more gives her length away and stays in the box |
| Portals, cell (4,7) | 7 (5 live) | 9 | Portal step at round 4 into a 4-cell pearl room, split at round 5, three more pearls, 5 long in 4 cells; the exit behind the portal holds her child's tail (section 4.5b) | she grows longer than the room she is in, and its only exit is a cell she cannot see |
| Portals, cell (27,8) (the mirrored start) | 4 (2 live) | 9-10 | the same | the same |
| Devil, cell (15,4) | 4 (3 live) | 18 | She walks to the centre lane and steps onto the cell next to an enemy 2-long's head (game 3) | steps next to a visible enemy head with two safe steps free; rules off |
| Devil, cell (16,9) | 3 (1 live) | 23-27 | She eats pearls along the centre lane, splitting 4 into 2+2 once or twice on the way, and is cornered by a 3- or 4-long one or two steps away | forages and splits in the contested middle |

The other 52 are single cases: 16 on Devil, 13 on Stripes, 9 on Trophy, 5 on Around UNSW, 4 on Queen Of Spades, 2 each on Islands and Autarky, 1 on Portals. On Devil and Trophy the top three die as early as we do (dead before round 50 in 54% and 34% of their games; ours 77% and 32%). The excess over the top three is on Portals (12 of 27 against 3 of 106), Slithery Fight (10 of 29 against 0 of 104) and Stripes (13 of 29 against 25 of 98).

### e. Queen rules on and off

[`d_haz.py`, `haz.txt`; `d_e.py`, `e.txt`; `d_f.py`, `f.txt`; `d_misc.py`, `misc.txt`; `d_pairs.py`, `pairs.txt`]

**What a replay shows of the switch** (live bot):

| | rules on (175 games, maps over 600 cells) | rules off (100 games) |
|---|---|---|
| queens that take a portal step, on maps that have portals | 7 of 175, none before round 20 | 27 of 44, 24 of them before round 20 |
| her own rams with a free safe cell | 0 | 8 (10 with the candidates) |
| she steps nearer to a small enemy head 2 / 3 steps away | 4% / 10% | 27% / 48% |
| she ends on the cell next to an enemy head from outside reach (share of such turns) | 1 of 5,506 | 10 of 2,116 |
| rounds on a 4-cell loop | 0.3% | 11.2% |
| small intruders within 4 steps that she rams herself | 2 of 712 | 14 of 141 |
| queens alive at round 200 that split after it | 6 of 52 (7 splits, all with no free cell; 5 of them cuts from 15 to 61 segments; `d_late.py`) | 3 of 6 |
| deaths per 1,000 queen-rounds | 5.0 | 10.7 |
| alive at the end | 25 of 175 (14%) | 2 of 100 |

So the rules that are on do what they say (no portals, no trades, no late growth splits) and halve her death rate. They do not touch the two largest kinds: with the rules on she still dies at 1.5 per 1,000 queen-rounds by stepping or staying in reach and at 1.7 cornered (top three: 0.3 and 1.3). And one thing gets worse with the rules on: all 11 "cut and stuck" deaths of the live bot are on rules-on maps, because the cut is an escape split that the queen rules do not block.

**passage2 (old against new, 28 pairs by opponent and map).** The new queen died earlier in 16 pairs and later in 11; median death round 136 (old) and 106 (new); dead before round 100: 9 and 13. Kinds old / new: stepped in 4 / 7, boxed by her own team 3 / 5, terrain 1 / 3, cornered 8 / 4, unseen 6 / 4. That points the way the team's note says, but 28 pairs cannot carry it: the qh31 pair shows the same shift (earlier in 16, later in 10; median 117 and 92) with a change that has nothing to do with passages, and stride shows none (13 and 13).

**qn23, the "queen no trap" candidate** (45 games in `../../online/smoke/qn23-test-new`, not in `games.csv`; walked with `d_extra.py`). Against the live bot's 215 games against the same three opponents: boxed-in deaths 15 of 45 (33%) against 52 of 215 (24%); per 1,000 queen-rounds 2.1 against 1.6. Terrain dead ends went up (8 of 45 against 15 of 215), boxed by her own team stayed (7 of 45; 16% and 17%), her own rams went to 0 (10 of 215 before). Two things in its replays: on Around UNSW the queen dies at round 5 in all three games, boxed in by her own split child in a nook right after a split; and on Slithery Fight she no longer dies at round 3 in its three games, but in two of them she is cut from 13 and from 66 segments to 2 late in the game and dies boxed in at rounds 371 and 410. The candidate did not reduce the deaths it was built for.

### f. Found and survived

[`d_f.py`, `f.txt`; `d_f2.py`, `f2.txt`; `d_t4.py`, `t4.txt`]

**Seen.** An episode is a run of rounds with an enemy head in her view. Every team's queen is seen in 88 to 98% of its games, 3.1 to 4.2 times per 100 queen-rounds (ours 3.7), for 5 to 7 rounds at a time. So ours is found as often as the others. What differs is the outcome:

| | meow, all | live, rules on | live, rules off | our opponents | forgot | SSS | Vibing++ | test4 against the top three |
|---|---|---|---|---|---|---|---|---|
| episodes per game | 5.1 | 6.3 | 3.7 | 9.5 | 7.4 | 8.7 | 7.7 | 6.5 |
| ended with her rammed | 11.5% | 10.0% | 12.6% | 2.6% | 6.3% | 4.7% | 5.4% | 7.1% |
| ended with her dead another way | 3.5% | 1.0% | 10.8% | 1.7% | 1.2% | 0.8% | 2.0% | 2.2% |
| episodes with an enemy within 3 steps, per 100 queen-rounds | 1.02 | 1.09 | 0.87 | 0.73 | 0.64 | 0.48 | 0.68 | 0.53 |
| ... of those ended with her rammed | 33% | 25% | 46% | 12% | 27% | 25% | 24% | 31% |

An enemy comes within 3 steps of our queen 1.5 to 2 times as often per round as of a top-three queen, and such an episode ends with a ram 1.3 times as often.

**Small intruders** (an enemy of 4 or shorter that comes within 4 path steps of the living queen; from the lead's `q/*.json` episodes):

| | meow, all | live, rules on | our opponents | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|
| intruders per game | 3.0 | 4.1 | 4.7 | 3.5 | 2.8 | 3.4 |
| it rammed the queen | 17.0% | 12.1% | 4.9% | 11.5% | 11.6% | 9.4% |
| one of her team rammed it | 3.7% | 3.7% | 13.6% | 13.5% | 16.6% | 12.1% |
| ... when 3 or more own heads were within 6 steps | 9.4% | 8.3% | 26.9% | 26.0% | 30.4% | 23.5% |
| it rammed another of her dragons | 5.2% | 5.6% | 3.3% | 7.0% | 6.2% | 5.2% |
| it left | 56% | 65% | 62% | 49% | 53% | 48% |

An intruder near a top-three queen is rammed by one of her team three to four times as often as one near ours. No team escorts its queen (A2 found that); this is ordinary contact trading that happens to take place near her, and ours does little of it (`deep-read-3.md`).

**Circling.** A queen is "on a loop" in a round if her head used 4 or fewer cells in the 12 rounds ending there.

| | rounds on a loop | queens with a loop of 20 or more rounds | loop rounds with an enemy head in view | rammed within 3 rounds of being on a loop |
|---|---|---|---|---|
| test4 against meow | 25.2% | 84 of 154 | 184 | 0 |
| test4 against the top three | 22.1% | 44 of 78 | 86 | 1 |
| SSS on weakhold | 46.2% | 21 of 28 | 338 | 2 |
| SSS, all maps | 5.2% | 42 of 503 | 1,216 | 17 |
| forgot | 2.4% | 44 of 632 | 534 | 8 |
| Vibing++ | 2.4% | 20 of 502 | 1,577 | 5 |
| meow live, rules on | 0.3% | 0 of 175 | 21 | 2 |
| meow live, rules off | 11.2% | 15 of 100 | 258 | 2 |

So the teammate's idea is what test4 does in every game: split once at round 0 or 1, then walk N, E, S, W on four cells at length 2 (game 3). SSS does it on weakhold and Portals. Against the top three, who ram a queen in view every time, test4's queen is alive at the end in 21 of 78 games and dies 3.1 times per 1,000 queen-rounds (rams 2.1): half our rate, and at the level of the top three's own queens. Only 1 of her 38 rammed deaths against them came within three rounds of the loop, 4 more within 20 rounds; 24 of the 38 are cornered deaths away from the loop.

**Can a 2-long queen on a loop be caught? From the rules:**

- She moves before every enemy. An enemy with a reach of r rams her only if its head is within r free steps of hers after her move.
- One 2-long (reach 1). At the start of her turn its head can be on the cell next to hers. One of her four sides is her own tail, one is that head, and the two others are two steps from that head, never next to it. If one of those two is free she steps there and is out of reach. One 2-long alone can never catch a 2-long queen in open water. It needs kelp, a body or a second dragon to take those two cells (game 14: a wall took them).
- One 3-long (one free step, one paid). If she steps straight away each round the distance after her move never shrinks: it closes one step free, she opens one. It catches her only if she steps toward it or sideways, or has no step away.
- Two 2-longs catch her in the open when they stand on the two cells diagonally ahead of her head: each covers the cell in front and one flank. One on a forward diagonal with kelp or a body on the other flank does the same (game 17).
- On a strict 4-cell loop her next cell is known. Any dragon that stands next to that cell after she has stepped onto it rams her, so one 2-long is enough if she keeps looping. If she leaves the loop when a head comes within two or three steps, the rules above apply and one small dragon is not enough.
- A dragon of 5 or more reaches 5 cells and can ram from outside her view; no loop helps against it.

**Checked against cases.** One more game was read for this, 1054795 (Default, test4 against Vibing++): test4's queen walks W, N, E, S on (4..5, 14..15) from round 120 to 146. At round 147 a Vibing++ 3-long comes into view 3 steps east. She breaks the loop: north, then west, both safe. At round 149 she steps south, back onto her loop cell (4,14), two steps from the 3-long, and is rammed with `WW`; north and west were safe. So the loop itself did not kill her; coming back to it did. In our games no hunter of ours ever tested a test4 loop: 184 loop rounds with one of our heads in view, no ram.

### g. What it is worth

[`d_worth.py`, `worth.txt`]

Only one kind of game can flip without changing anything else on the board: a round-500 loss in which both queens are dead. Had ours been alive, the queen rule gives us the game. There are 102 such losses (69 for the live bot). Three readings:

1. **Strict.** She does not die that way and then lives to the end: the game flips.
2. **Top-three survival.** She does not die that way, and from that round on she lives as often as a top-three queen that is alive at that round, on that map-size class and in that economy band (own / enemy total length at that round: under 0.67, 0.67 to 1, 1 to 1.5, over 1.5). For example a top-three queen alive at round 100 lives to the end in 19% of games when her team is under 0.67, 38% at 0.67 to 1, 47% at 1 to 1.5 and 60% above; on large maps 29% over all bands.
3. **Our own other deaths.** She does not die that way but stays exposed to every other kind of death at our own rates for that map-size class and round band.

| Family of death | deaths | reading 1: flips | reading 2: expected flips | reading 3: expected flips | points of win rate (1 / 2 / 3) |
|---|---|---|---|---|---|
| rammed: stepped or stayed in | 104 | 26 | 7.4 | 2.4 | +6.5 / +1.9 / +0.6 |
| rammed: cornered | 116 | 29 | 8.4 | 4.1 | +7.2 / +2.1 / +1.0 |
| rammed: unseen | 31 | 14 | 3.7 | 0.9 | +3.5 / +0.9 / +0.2 |
| boxed in by bodies | 61 | 17 | 5.1 | 0.4 | +4.2 / +1.3 / +0.1 |
| boxed in: terrain | 30 | 8 | 3.3 | 0.4 | +2.0 / +0.8 / +0.1 |
| own ram | 19 | 8 | 2.4 | 0.0 | +2.0 / +0.6 / +0.0 |
| all | 362 | 102 | 30.4 | 8.2 | +25.4 / +7.6 / +2.0 |
| the four she controls herself (first, fourth, fifth, sixth row) together, with only cornered and unseen rams left in reading 3 | 214 | 59 | 18.3 | 8.7 | +14.7 / +4.6 / +2.2 |

The live bot alone (275 games, 77 won): stepped or stayed in 14 / 4.0 / 1.3 games; cornered 21 / 6.3 / 3.1; unseen 11 / 2.6 / 0.7; boxed by bodies 11 / 3.4 / 0.4; terrain 6 / 2.6 / 0.2; own ram 6 / 1.8 / 0.0; all 69 / 20.8 / 5.6 (+25.1 / +7.6 / +2.0 points); the four she controls together 37 / 11.9 / 5.5 (+13.5 / +4.3 / +2.0).

Reading 1 is an upper bound nobody will reach. Reading 3 is so low because a queen saved at round 85 on Around UNSW has a 1% chance to see round 500 at our present death rates. The honest range for all four of her own families together is plus 2 to plus 5 points of win rate on 28%.

Not in these counts: three round-500 losses with her queen alive in which our queen, when she died, was already longer than her queen at the end: game 29 (990346: ours 57 at round 385, hers 3), 990234 (Trauma: ours 28 at round 460, hers 5) and 1053389 (Trauma: ours 27 at round 424, hers 19). The first is a cut; the second is a fed queen cornered by a 5-long right after her own five-step move; the third is a fed queen rammed by a 4-long she could not see. Each is a win thrown away within the last 120 rounds.

### h. The rule

See section 7.

## 6. Our queen against the others

One row per behaviour. "meow" is all 401 games unless a cell says live bot or rules on / off. Rates are per 1,000 queen-rounds unless a cell says otherwise. The source of each row is the table of section 5 named in the last column.

| Behaviour | meow | our opponents | forgot | SSS | Vibing++ | source |
|---|---|---|---|---|---|---|
| Queen deaths per 1,000 queen-rounds | 6.5 | 2.2 | 2.8 | 2.1 | 3.4 | 2 |
| Alive at round 300 (of games that reach it) / at the end | 15% / 10% | 61% / 40% | 52% / 36% | 65% / 41% | 49% / 27% | `haz.txt` |
| Rounds with an enemy head in her view | 20% | 17% | 21% | 18% | 21% | 5b |
| ... on large maps, rounds 50-149 | 22-26% (live) | 10-12% | 17-12% | 11-10% | 14-22% | 5c |
| Ends a turn in reach although a safe step exists | 2.7 | 1.5 | 0.8 | 0.6 | 1.1 | 5b |
| From outside reach, steps into it (share of such turns) | 0.76% | 0.42% | 0.18% | 0.15% | 0.23% | 5b |
| In reach with a safe step, stays in reach (share of such turns) | 19% | 13% | 10% | 8% | 10% | 5b |
| Takes a pearl that lies inside a visible enemy's reach | yes: she ate on 19 of her 68 stay-in turns (games 8-11) | 26 of 88 | 8 of 67 | 8 of 43 | 12 of 63 | `expo.txt` |
| Steps nearer to a small enemy head 3 / 4 steps away | 10% / 30% (rules on), 48% / 67% (rules off) | 12% / 12% | 5% / 5% | 7% / 8% | 16% / 32% | 5b |
| Cornered turns (no safe step) | 2.8 | 3.9 | 3.1 | 2.2 | 3.5 | 5b |
| A turn that ends in reach is punished by a ram | 71% | 16% (by us) | 44% | 47% | 32% | 5b |
| Rammed by an enemy she could not see | 0.55 | 0.06 | 0.48 | 0.41 | 0.62 | 2 |
| Boxed in with 6 or more segments: what she does | cuts to 2 (40 cuts in 37 games; never sheds with no free cell) | cuts (85 in 63 games) and sheds (109) | sheds 2 from the tail (1,448 times); 0 cuts | sheds (394); 0 cuts | cuts to 3 (105 in 86 games), sheds 78 | `cut.txt` |
| Dies boxed in by bodies (her own team's in 58 of our 61) | 1.1 (cut and stuck 14, own child 11, nose to nose 20, a team-mate's body 14) | 0.7 | 0.16 | 0.17 | 0.87 | 2 |
| Dies in a terrain dead end | 0.54; ate inside in 26 of 30 | 0.33 | 0.20 | 0.11 | 0.20 | 2, 4.6 |
| Takes portal steps (queens that ever did, maps with portals) | 4% with rules on; 61% with rules off, 24 of 27 before round 20 | 13% | 4%, none before round 20 | 7%, none before round 20 | 27% | 5e |
| Rams an enemy head herself with a free safe cell | 10 games, all rules off | 1 | 4 | 0 | 5 | `misc.txt` |
| Walks a loop of 4 cells | 0.3% of rounds with rules on, 11% with rules off | 12% (test4 25%; WHQ 1.5%) | 2.4% | 5.2% (weakhold 46%) | 2.4% | 5f |
| Path distance from her start, rounds 50-99, queen / other heads | 14.7 / 19.8 (live) | 12.7 / 22.6 | 15.0 / 21.4 | 12.3 / 23.1 | 16.9 / 23.2 | 5c |
| Rams of a short queen by distance from her start (0-5 / 11-15 / 16-25 cells) | 1.8 / 5.5 / 8.1 | 0.6 / 1.4 / 1.6 | 1.1 / 4.8 / 4.5 | 0.8 / 1.7 / 2.9 | 1.0 / 3.4 / 3.9 | 5c |
| Own heads within 4 cells, rounds 100-149 / 150-199 | 1.2 / 1.3 (live) | 1.5 / 1.8 | 1.7 / 1.9 | 1.7 / 2.2 | 1.4 / 1.5 | 5c |
| Rams of a short queen with 0 / 3 or more own heads within 6 steps, rounds 50-149 | 9.7 / 2.2 | 2.4 / 0.1 | 5.3 / 1.4 | 3.1 / 1.0 | 4.9 / 0.7 | 5c |
| A small intruder within 4 steps of her is rammed by one of her team | 3.7% | 13.6% | 13.5% | 16.6% | 12.1% | 5f |
| Natural pearls per 100 rounds, rounds 0-49 / 100-149 | 4.7 / 2.2 (live) | 4.9 / 2.4 | 4.6 / 1.3 | 4.1 / 1.6 | 4.7 / 2.3 | 5c |
| Her splits per 100 rounds, rounds 0-49 / 100-149 | 3.6 / 1.6 (live) | 3.6 / 1.2 | 4.4 / 1.0 | 4.9 / 1.0 | 3.2 / 1.1 | 5c |
| Her mean length, rounds 100-199 | 2.5 | 3.2 | 2.7 | 2.6 | 5.3 | `e.txt` |
| Queens of 6 or more lost: rammed / cut to 2-3 and dead boxed in | 16 / 17 (10 at round 3, 3 in dead ends, 4 fed queens late) | 21 / 24 | 63 / 0 | 24 / 0 | 67 / 12 | `misc.txt` |
| Splits with an enemy head in view within 3 turns of being rammed | 16 of 251 rams | 11 of 102 | 23 of 327 | 14 of 240 | 19 of 230 | `misc.txt` |

Reading the table down: in what she eats, how often she splits, how far she goes on average and how often she is seen, our queen is an ordinary 2-3-long queen like SSS's or forgot's. She differs in five rows: she ends turns in reach by choice, she takes pearls in reach, she cuts herself when boxed in, she has less company, and nobody near her rams the intruder. With the rules off she is a different animal: she walks toward small enemy heads, trades herself for a 2-long, and takes portals at once.

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

## 8. Where `findings.md` or the earlier deep reads look wrong or thin

1. **`findings.md` section 4, "28% die boxed in or by their own crash".** Correct as a count (111 of 401: 91 boxed in, 19 own rams, 1 portal step). But it is not one thing. It is five with five different fixes: cut and stuck 14, her own split child on the exit 11, a team-mate's head on the exit 20, a team-mate's body on the exit 14, terrain dead end 30; and of the 19 own rams 9 were forced (boxed in with an enemy head as the only side) and 10 were trades with a free safe cell.
2. **`findings.md` section 1 and the brief, "102 round-500 losses with both queens dead: each would have been a queen-rule win had ours lived".** True as an upper bound. A queen that avoids the death she died of still has to live to round 500: with a top-three queen's survival from that round on, 30 of the 102 flip; with our own death rates for the other kinds, 8 (section 5g). The count also misses three losses with her queen alive in which our fed queen was longer when she died than hers at the end.
3. **`deep-read-2.md` finding 2, "a queen survives because of where she lives, not because of what happens when an enemy arrives".** For our queen both halves are true and the second is the larger measured one. Averaged over all maps our queen is nearly as close to her start as SSS's (14.7 against 12.3 cells in rounds 50-99), eats somewhat more (2.2 against 1.6 natural pearls per 100 rounds in rounds 100-149), and has an enemy head in view about as often (20% against 18% of rounds). Where she lives shows on large maps (an enemy head in view in 22-26% of rounds against 10-11%) and in the price she pays for distance (8 rams per 1,000 rounds beyond 15 cells against 3 for SSS). But on the turn an enemy is in view she ends in reach by choice 3.4 times as often as the top three (6.4 times against the same opponents), and that is 104 deaths.
4. **`findings.md` section 4, "once a small enemy is 2 steps away, a top-three queen is rammed that round about as often as ours; the difference is how often one gets that close".** Agrees with this read, with one addition: about half of the "getting that close" is her own step (2.7 of her 5.4 turns in reach per 1,000 rounds are by choice; 0.8 of 3.7 for the top three).
5. **`findings.md` section 4, "queens are not parked".** True on average (17 to 21 different cells per 25 rounds for every team). Not true for test4, whose queen walks a 4-cell loop in a quarter of her rounds and has a loop of 20 or more rounds in 128 of 232 games, nor for SSS on weakhold (46% of rounds) and Portals. Those are the queens of our most frequent opponent and of a top-three team, and they are almost never rammed on the loop (1 of 38 rams of test4's queen by the top three).
6. **The brief on card #25, "`QUEEN_WAIT` never fired because she is 2-3 long when boxed in".** She is 2 long when it looks because the escape split has just cut her to 2: 39 of our 40 cuts were made with no free cell, 36 of them from 10 or more segments (`d_cut.py`).
7. **`findings.md` section 4, "Portals: boxed by a body at rounds 9-10 at length 4-5 in 11 games".** The body is the tail of her own split child, standing on the far side of a portal on the one cell she cannot see (section 4.5b). The homes on Portals are not connected at all: from a start cell 240 of the 512 cells can be reached with portals, and the enemy's start is not among them (`d_conn.py`, `conn.txt`). So every queen death there is self-made: ours 27 of 27, the top three's 54 of 106.
8. **The team's note that passage2 "got our queen killed online".** The 28 pairs point that way (the new queen died earlier in 16 pairs, later in 11) but cannot carry it: the qh31 pair, which changed nothing about passages, shows the same shift (16 and 10).
9. **qn23 (`../../online/smoke/qn23-analysis/summary.md`).** Its table shows "other body (ally)" deaths going from 9 to 0. With the board around her classified, boxed-in deaths did not fall (15 of 45 against 52 of 215): the candidate moved them to walls and her own body (terrain dead ends 8 of 45 against 15 of 215) and added a round-5 death on Around UNSW in all three games. That summary also says the count of safe steps "could not be measured"; `d_class.py` measures it.
10. **`deep-read-3.md` and `findings.md` 6c on contact.** One more consequence of "our small dragons do not ram at contact": a small intruder within 4 steps of our queen is rammed by one of our dragons in 3.7% of cases, against 12 to 17% for the top three and 13.6% for our opponents. Nobody escorts, but ordinary trading near her does the escort's work for the others.

## 9. Things I could not determine from replays

- **Why she took the step she took.** A replay has no scores. That the threat penalty lost to a pearl (games 8 to 11) or to a ghost of an enemy seen three rounds earlier (game 1) is read from `main.cpp`, not seen. The same goes for the queen's belief about a cell behind a portal (game 24) and for the room her survey saw in the corridor of game 30.
- **What she knew of the terrain.** "Tree cell" is computed on the whole map. Her bot knows only the edges that have been inside some turn's 7x7 view. In game 30 the corridor was in view when she stepped in; I did not check that for all 30 terrain deaths.
- **Whether a team-mate saw her.** In the 20 nose-to-nose deaths the other dragon's head was next to her exit; whether its bot had her head in its own view and stepped there anyway is likely (she was within two cells) but not checked per case.
- **The reach of dragons that move between her turn and the killer's.** The reach model takes bodies where they stand at the start of her turn. It called the fatal cell safe in 17 of 823 checked rams (2%), so it is good enough for counts, not for single close calls.
- **The effect of the rule.** Sections 7.1 and 5g are arithmetic on games that were played. What a queen that steps away meets next can only be estimated from the turns on which she did step away (`after.txt`); a real answer needs games.
- **Which build played which ladder game.** The two ladder downloads are "the live bot of that hour"; more than one live build may be in them. The "-old" runs agree with them in every table, so I pooled them.
- **Intent of opponents.** Whether test4's queen leaves her loop because of the enemy head (the one case read, 1054795, looks like it) or for another reason is not in the replay. Likewise whether WHQ's two dragons in game 2 were following our queen or grazing beside her.
- **Local results.** The team's local tests of queen toggles are quoted from `work/plan.md`; I did not see those replays.
