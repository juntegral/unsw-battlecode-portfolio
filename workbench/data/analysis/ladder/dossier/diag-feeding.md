# Feeding: what it buys and what it costs (team 1119, written 7 Oct 2026; 555 main games, 387 reach feeding)

**What it buys and costs.** Of the 387 games that reach feeding we won 200, and 117 of those wins needed growth that came after it began (95 on longest dragon or total length, 22 on the longer queen). Against that: 16 lost games in which a leader longer than their final longest dragon was rammed, and 3 wipe-outs after real feeding.
**The change.** No card. None of the three candidate switches reaches more than 7 lost games, and each stops feeding in games that feeding won.
**How sure.** High that no feeding switch earns a build round: the counts cover every game and the round-401 figures were recounted from rows.jsonl with no difference. Medium on the size of the gain, because every main game feeds and there is no game without it to compare.

Labels: [M] measured by my scripts in dossier/work/. fd_scan.py replays the 555 main games in rows.jsonl (22:00 KST; per-game.jsonl holds 500 of them); fd_agg.py writes one row per game to fd_games.jsonl, which is the per-game table of job 1; fd_start, fd_tab, fd_cost, fd_more, fd_queen, fd_qhaz, fd_esc, fd_eat, fd_margin and fd_dec print the figures; fd_ram.py is the ram scan and the replay viewer; fd_check.py is the recount. [C] read from battlecode/mybot2/main.cpp, line given. [E] my estimate.
Terms: "S" = the first round in which feeding can happen in that game. "Feeder" = one of ours, not the queen, that dies by taking no action after S with a team mate at least twice its length within 10 tiles. "Leader" = our longest dragon at that moment. "Rammed" = an enemy head moved into its head; both die.

## 1. Where feeding starts and how the board stands (job 1)

How S is found [M][C]: the earliest of (a) the first round after 200 in which one of ours starts its turn with 56 or more of ours alive; (b) round 301, if our queen is alive then on a layout above 600 cells or a feeder dies in r301-400 in a round where (a) does not hold; (c) round 401. Check: no feeder dies before round 201 in any game and 82 die in round 201; all 2,919 feeder deaths of r201-300 fall in rounds where (a) holds; of the 1,400 in r301-400 outside such rounds, 1,143 are beside our queen. 168 games end before S; 46 of the 387 never have a feeder.

Medians. The three numbers are dragons, longest, total length. The last column is games won / lost by elimination, on the queen rule, on longest dragon or total length.

| start | games | won-lost | ours at S | ours at the end | theirs at S | theirs at the end | decided by |
|---|---:|---|---|---|---|---|---|
| 56 dragons (median round 201) | 164 | 102-62 | 58.5, 11, 179 | 34.5, 45, 154.5 | 60, 8.5, 162 | 13, 34, 143.5 | 24/0, 13/35, 65/27 |
| live queen, round 301 | 83 | 47-36 | 20, 6, 66 | 5, 25, 53 | 42, 5, 111 | 10, 23, 87 | 4/5, 29/11, 14/20 |
| round 401 | 140 | 51-89 | 16.5, 10, 65 | 4, 20, 46.5 | 22.5, 10, 80 | 9, 24, 77 | 5/7, 2/33, 44/49 |
| all | 387 | 200-187 | 37, 9, 105 | 11, 29, 85 | 42, 8, 113 | 11, 28, 105 | 33/12, 44/79, 123/96 |

- [M] On the rule that would have decided the game at S we were ahead in 195 games (won 142) and behind in 192 (won 58).
- [M] At round 401 with queens level: our longest at least 2 times theirs in 55 games (won 48), 1.25 to 2 times in 33 (26); theirs 1.25 to 2 times ours in 29 (8), at least 2 times in 55 (12).

## 2. What feeding buys (job 2)

- [M] Won on longest dragon or total length: 123. Our longest at S was shorter than their final longest in 95 (56 dragons 58 of 65, live queen 11 of 14, round 401 26 of 44), equal in 6, already longer in 22. Counted from round 401 for the 365 games that reach it: shorter 75, equal 5, longer 43 (fd_check.py, from rows.jsonl: the same three numbers).
- [M] In 71 of the 95 the pearls our longest ate from feeders are by themselves the difference: its final length without them is not above their final longest.
- [M] Won on the queen rule: 44. In 22 both queens live to the end, and in all 22 our queen at S was no longer than their final queen. From round 301 the feeding goes to her: 1,840 feeders died beside our queen.
- [M] Feeding our queen when theirs is already dead (34 games, 29 won) is not waste either: with only our queen alive after round 300 on layouts above 600 cells, a queen of 20 or more dies 0.30 times per 100 rounds, a queen of 2 to 4 dies 0.73 times.
- [M] Leader already longer at S than their final longest: 63 of 387, won 57 (33 by elimination, 22 on longest, 2 on the queen). The 6 lost: 4 on longest, one layout, leader rammed in each, with 0, 0, 2 and 22 feeders; 2 on the queen rule.
- [M] Their longest grows too: median 8 at S, 28 at the end. A leader that stays as it was at S loses the rule in most games.

## 3. What feeding costs (job 3)

- [M] Leader deaths. Our longest (15 or more) died 116 times after S, in 83 games (won 36); median round 393, 25 of them in the last 50 rounds. Of the 127 after round 200, 125 were rammed, 1 hit a wall, 1 an enemy body. Games with our longest (10 or more) rammed after S: 128, won 56; games without: 259, won 144.
- [M] The 194 rams in which our leader (8 or more) was the one hit: the rammer is 2 to 5 long in 144, began its turn 1 to 3 tiles away in 148 and paid segments for the lunge in 154. It was inside the leader's 7 by 7 view at the leader's last turn in 107 of 183; the leader took one step on that turn in 90. None of ours was within 5 tiles in 114 of 183. A feeder had died within 10 tiles in the last 10 rounds in 42. Leader length: 8 to 19 in 118, 20 to 39 in 50, 40 or more in 26.
- [M] Rams that decided the game (the leader was longer than their final longest and we lost): 16. 12 lost on longest, 3 by elimination, 1 on the queen rule; in 6 the leader was our queen.
- [M] Wiped out after S: 12 of 387, all after round 400. 8 had 8 dragons or fewer at S and 7 never had a feeder. 3 had 10 or more feeders, all far behind when it began: 13 dragons against 51, 13 against 36, 37 against 62.
- [M] Ended with 3 dragons or fewer: 103 (won 29); 51 of them had 10 or fewer at S. From 20 or more at round 401 down to 3 or fewer: 19 games, won 12.
- [M] Lost though ahead on every rule at S (queen not shorter, longest and total greater): 19 of 118. Leader rammed 11, their queen outlived or outgrew ours 4, out-grown with no leader death 4.
- [M] Lost on longest or total: 96. In 81 we never held a dragon longer than their final longest after S: median 19 against 43 at the end, 15 dragons against 54 at S. Too little to feed with, not too much feeding.

Rammed before its next turn, per 100 turns of a side's longest dragon (10 or more), after S [M] (fd_esc.py). "Short enemy" = 9 long or less.

| | none of its own within 5 tiles | one | two or more |
|---|---:|---:|---:|
| ours, all 60,638 turns | 0.39 | 0.25 | 0.11 |
| ours, a short enemy head within 3 tiles | 1.75 | 1.82 | 0.83 |
| ours, the nearest at 4 to 5 tiles | 0.89 | 0.66 | 0.29 |
| theirs, all 56,166 turns | 0.43 | 0.32 | 0.12 |

Our leader alone, by how many of ours are alive: 10 or fewer 0.29, 11 to 30 0.41, 31 or more 0.45. The size of the team does not protect it; company beside it goes with a third of the rate, on both sides.

Six replays [M] (fd_ram.py view <game> <from> <to>):
1. 1307543 (vs 2127; 36 dragons against 9 at S, their queen dead). Our queen is fed to 40. One enemy of 3 stays 3 to 8 tiles from her for 13 rounds (r466-478) with none of ours, or a single 2-long, within 6 tiles, then lunges 3 tiles. Lost 10 against 25 with 17 of ours alive.
2. 1318769 (vs 1666). Leader 47 to 55 in r486-498. The same enemy of 3 is within 8 tiles in 10 of those 13 rounds and rams from 2 tiles at r498. 44 of ours alive, at most one within 6. Lost 32 against 54.
3. 1336350 (vs 2342). Leader 57 to 68 in r400-411 while being fed, with 3 to 7 enemy heads within 8 tiles every round. Rammed at r411 by a 4 from 3 tiles; two of ours (2 and 3 long) are within 6 and do not go for it. Lost 44 against 50.
4. 1303538 (vs 1927). Queen 54 to 66 in r426-437 while 8 feeders die beside her and our count falls from 18 to 9; enemies of 2 and 3 gather. At r437 she keeps 2 and splits off 64 (main.cpp 628-631), and the 64 is rammed in the same round. Lost 14 against 38.
5. 1243021 (vs 1903). Leader 37, not being fed. One enemy of 5 closes to 7, 5, 5, 5, 3 tiles over five rounds and rams at r426. 41 of ours alive. Lost 30 against 36.
6. 1300343 (vs 2474; 37 dragons against 62 at S). 7 of ours left by r404, queen 46 to 50 with up to 7 enemy heads within 8 tiles and at most one of ours within 6; rammed at r423 by a 12, wiped out at r441. This is the red-team pattern, and the only wipe-out of the 12 with more than 20 dragons at S.

What the feeders do in them: come within 3 tiles, die, and are eaten within a few rounds. None stays. The leader then walks about one tile a turn with a short enemy in view.

## 4. How much of the fed length arrives (job 4)

[M] 341 fed games, 15,158 feeders: 10,236 of them 2 long, 3,910 of them 3 long. Means per fed game:

| start | feeders | length given up | pearls dropped | eaten by the dragon beside | by our longest | by any of ours | by theirs | our longest at S, at the end |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 56 dragons (155) | 75 | 197 | 109 | 56 | 33 | 99 | 4.9 | 12, 50 |
| live queen (73) | 23 | 55 | 31 | 22 | 18 | 28 | 1.3 | 9, 30 |
| round 401 (113) | 17 | 44 | 25 | 13 | 11 | 21 | 0.8 | 11, 26 |
| all (341) | 44 | 116 | 64 | 34 | 23 | 58 | 2.8 | 11, 38 |

- [M] Of 100 length given up, 44 vanish at death (a dead dragon leaves a pearl for every second segment), 30 reach the dragon beside it, 20 reach our longest. Per game the middle half lies between 13 and 31.
- [M] Who eats the 21,932 dropped pearls: the dragon beside 53.5 percent, another of ours 10 or longer 6.1, one 5 to 9 long 7.1, one 2 to 4 long 23.5, theirs 4.3, nobody 5.5. 60 percent of those we eat are eaten within 3 rounds. 1,702 feeders had eaten feeder pearls themselves.
- [M] What our longest eats after S: feeder pearls 7,856, natural pearls 4,635, pearls of our other dead 2,808, of their dead 860.
- [M] Feeding is not what empties the board. Our deaths after S per game: feeders 39 (102 length), walls 37 (83), rammed by them 23 (95), own body 20 (46), a team mate's body 14 (33). 117 splits per game after S refill it. Median 11 dragons at the end, theirs 11.

## Why, in the code

- [C] 4919-4922: feeding_phase() is round > feed_round, or round > 200 with 56 or more alive (69-70). 472: feed_round is 400. 522-527 with 3332-3334: from round 300 a live queen on more than 600 cells sets queen_game (QUEEN_SAFE_SPAN 0 makes the test always true) and feed_round becomes 300; 1695 and 1817-1820 pass that on by sonar; 1775-1780: in a queen game the queen outranks every dragon as leader.
- [C] 2296-2324: a feeder is a non-queen within 15 tiles of the leader it knows and at most half its length (4912-4917), while more than 3 of ours live (47). 4924-4935 with 551-554: on a drop cell or within 3 tiles of the leader, with no enemy head within 4 tiles of itself, it returns without an action, which kills it.
- [C] 1422, 1746-1771, 1737-1741: "the leader" is the longest dragon this dragon has seen or heard of in 25 rounds, so a team has several. 241 with 586-588: RALLY_FRESH is 0, so nobody further than 15 tiles walks to one. That is why the dragon beside eats 53.5 percent and our longest 35.6.
- [C] 2667: no trades after feed_round. 1028, 1037: a leader never splits and the others only at length exactly 4.
- [C] What guards a leader today: 5083-5084 doubles its penalty for tiles an enemy head can reach; 2611-2613 with 2684-2694 sends a short dragon at an enemy head within 6 tiles of a team mate showing 10 parts. 228 with 5124-5130: LEADER_GUARD_ROUNDS, off, would keep a leader 6 tiles from enemy heads in the last N rounds. I found no record that it was tested.

## No card

- **Feed only while the leader is not ahead by a margin.** [M] At round 401 with queens level our longest is at least 2 times theirs in 55 games and we lose 7. In 23 of the 55 their final longest passes what ours was at round 401, and 18 of those are wins that the growth after round 401 made. At 3 times: 28 games, 1 lost, 9 such wins. [C] A dragon cannot know their final length, and what it can measure (the parts of an enemy inside a 7 by 7 view, 3312-3319) is below the truth, so the rule stops early.
- **Keep more than 3.** [M] It reaches the 3 wipe-outs with real feeding, all lost from far behind. Games that fall from 20 or more dragons to 3 or fewer are won 12 of 19, and a leader on its own is rammed no less often with 31 or more of ours alive than with 10 or fewer (0.45 against 0.29).
- **Split again when the leader dies.** [M] The next longest is 0.60 of the dead leader at the median (under half in 43 of 116) and [C] takes over by the 25-round rule that is already there. Splitting cuts the dragons the longest-dragon rule then needs, and half the deaths come after round 393.
- **A lead, not a card.** [E] The cost that is measured is a leader left alone with a short enemy in view. It reaches 16 games in 387. "The last two feeders beside a leader stay alive" has the best support of anything here (the rate table), and LEADER_GUARD_ROUNDS is already in the code. I do not put either up: the table is a correlation; 15 of our 121 wins on longest dragon are by 3 or less and two feeders kept are about 3 pearls a leader; in replay 3 two of ours stood beside the leader and did nothing.

## Against it

- [M] 16 lost games with a rammed leader that was the longest on the board are 4 percent of the games that reach feeding, the size other cards claim. In 9 of them none of ours was within 5 tiles, and in 4 of those 9 we had 13 to 55 dragons alive.
- [M] We lost from ahead on every rule in 19 of 118 games, one in six.
- [M] The red-team bot won 7 of its 17 this way (report.md, W2). On the ladder it is 3 games, but ladder teams thin out as we do (median 11 dragons at the end). An opponent that holds 57 to 60 dragons to the end, as that bot does, is not in this sample.
- [M] Feeding is lossy: 20 of 100 length reaches our longest and a quarter of the dropped pearls go to other short dragons of ours. Better routing would be worth more than any switch above; I did not find one line that does it.
- [E] "Needed the growth" is not "needed the feeders". Natural pearls are 29 percent of what our longest eats after S, and with the 56 rule S is round 201, so 300 rounds of other play sit inside "after S". The strict count is 71 wins plus the 22 queen games, not 117.
- [M] 18 layouts in 30 hours of ladder play. Nothing here is from an unseen map, and no main game runs without feeding.
