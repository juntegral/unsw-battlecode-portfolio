# The longest-dragon race: who wins it against us, and how (team 1119; 180 online games of 8 Oct 2026, 500 ladder games, 597 of rank-1's)

1. **The finding.** Nobody wins this race by killing our leader. In 27 of the 28 games we lost on length today no dragon of ours was ever longer than their final longest; the end gap is 31 at the median and above 20 in 21. They pass us for good at round 208 to 374 (median by arm), when our longest is 5 to 7, and then put more length into theirs and start sooner: above 1200 cells WeHaveQuizzes lets 133 and then 285 length die by choice in r300-399 and r400-499 and rank-1 77 and 113, we 62 to 66 and 91 to 96, and we end those games with 29 to 40 dragons alive, 23 to 32 of them further than 15 tiles from our longest, where no rule sends them to it.
2. **The change.** Two switches, both off by default. Card 1, `RALLY_END_FRESH` (test 25): after the feeding round a dragon that may feed and is further than 15 tiles from the leader it knows walks to it; the rally code is in main.cpp and has never been on. Card 2, `LC_FEED_ROUND` (already in the code; test 350): with our queen dead the feeding phase starts at round 350, not 400. No card for protecting the leader from a lower length, none for two long dragons, none for earlier leader rules.
3. **How sure.** High on the anatomy: every game replayed, and the 180 online games recounted with the shared reader (winner, how decided, longest, alive and total at nine rounds, deaths by no valid action by side and century, the class of every game lost on length): 3,896 cells, none differs. Low on games won: by the measured rate (0.2 length reaches the longest for each length that dies by choice) each card would have turned 2 to 5 of the 28, largely the same games (card 1 by the same count: 16 to 22 of the 91 on the ladder), and no game of ours has played either. In 21 of the 28 our total length at the end is under 0.8 of theirs; that is economy, and nothing here touches it.

Labels: [M] measured by my scripts in dossier/work/ (lg_scan.py replays every game: longest, second, alive, total per round, every death of a side's longest with its last two turns, every death by no valid action and who ate its pearls; lg_far.py: distance of every dragon to its side's longest; lg_agg.py, lg_agg2.py, lg_faragg.py, lg_report.py, lg_rally.py, lg_misc.py print the tables; lg_view.py shows replay rounds; lg_check.py is the recount; all 84 race games are in work/lg_games.txt). [C] read from data/online/smoke/agg8-bot/main.cpp, line given. [E] my estimate. Terms: "race game" = decided on longest dragon or total length, or by elimination after both queens died. "Dies by choice" = dies by no valid action with a free tile beside its head (the test of diag-sacrifice). "Leader" = a side's longest dragon. Rounds are the replay's, 0 to 499.
## 1. The race games (job 1)
| arm | games, won | decided: queen / longest / total / elimination (both queens dead first) | race games, won-lost | lost: wiped out / never longer than their final longest / a leader longer than it rammed | they pass for good: median (before r200, r200-399, r400+) | our longest just before | end gap, not wiped (median) |
|---|---|---|---|---|---|---:|---:|
| MAIN | 90, 21 | 34 / 20 / 0 / 36 (20) | 40, 14-26 | 11 / 14 / 1 | r253 (11, 11, 4) | 7 | 40 |
| B7 | 60, 23 | 19 / 19 / 0 / 22 (12) | 31, 17-14 | 4 / 10 / 0 | r374 (6, 4, 4) | 5 | 23 |
| B7Q | 30, 14 | 12 / 6 / 1 / 11 (6) | 13, 8-5 | 2 / 3 / 0 | r208 (2, 3, 0) | 5 | 44 |
- [M] The round they pass for good, 45 lost games: our longest is under 8, no leader yet, in 27; a leader of 8 or more is rammed in 7 (rammer 3 to 7 long from 2 to 4 tiles, in view in 6, none of ours within 5 tiles in 3), splits in 6 (in 4 the head keeps 2 and the rest leaves, lines 750-755), and is out-eaten while intact in 5. One of the 7 rammed leaders was longer than their final longest (1415585: 59 against 43); the other six they out-grew anyway (1422314: 36 against a final 91).
- [M] The live arm's five losses, longest ours:theirs at r100, 200, 300, 400, 499. 1422309 (4096 cells): 4:4, 4:14, 10:19, 17:37, 26:70, passed at r104 with ours at 5. 1422310 (2240): 5:4, 7:6, 3:14, 5:23, 28:59, passed at r208 when our 6 split. 1422314 (4096): 6:9, 13:25, 19:29, 14:44, 24:91, passed at r235 when our 36 was rammed by a 4 from 4 tiles in 4 steps (1 free), in view, one of ours within 5. 1422312 and 1422313 (288 and 512 cells): wiped out at r215 and r78 with no dragon above 7. Its eight wins and the other two arms, game by game with nine rounds each: lg_games.txt.
## 2. How each side grows its longest (job 2)
[M] All games. Per 100 rounds: change of the side's longest; pearls eaten by a dragon that is its side's longest and 8 or more (natural / of team mates dead by choice / of other own dead / of their dead); length that died by choice. No merges exist (rules/movement.md: eating is the only way to grow; rules/death.md: a dead dragon leaves a pearl for every second segment).

| side (games) | longest at r200, 300, 400, 499 | r300-399: change; eaten; died by choice | r400-499: change; eaten; died by choice | fed pearls to the longest per length died, r400+ |
|---|---|---|---|---:|
| ours MAIN (90) | 6.2, 7.2, 10.0, 17.9 | +4.0; 3.5 / 2.8 / 2.1 / 1.0; 11 | +12.8; 6.3 / 9.6 / 2.7 / 1.4; 42 | 0.23 |
| ours B7 (60) | 7.4, 10.4, 14.7, 28.6 | +6.3; 2.6 / 5.2 / 2.5 / 0.4; 43 | +21.9; 5.4 / 17.1 / 3.3 / 0.3; 79 | 0.22 |
| ours B7Q (30) | 7.0, 11.3, 16.0, 26.1 | +6.4; 2.8 / 4.2 / 2.0 / 0.3; 36 | +15.9; 5.9 / 14.3 / 4.4 / 0.5; 83 | 0.17 |
| WeHaveQuizzes (90) | 7.6, 11.5, 24.2, 41.2 | +18.9; 3.4 / 17.6 / 2.1 / 0.7; 90 | +27.9; 7.1 / 23.1 / 1.6 / 0.6; 198 | 0.12 |
| Big Bobs Bots (90) | 4.4, 4.7, 8.8, 18.7 | +5.6; 3.4 / 4.1 / 2.3 / 0.4; 31 | +15.4; 5.9 / 12.9 / 1.7 / 0.6; 137 | 0.09 |
| rank-1 (597) | 7.1, 9.7, 17.3, 30.0 | +11.4; 4.2 / 8.1 / 2.9 / 0.8; 44 | +20.5; 7.8 / 16.8 / 2.7 / 1.0; 84 | 0.20 |
| ours, ladder (500) | 6.7, 9.3, 14.4, 24.1 | +7.2; 3.7 / 4.6 / 2.4 / 0.9; 23 | +14.9; 5.6 / 12.5 / 2.7 / 1.1; 64 | 0.20 |

[M] Games that reach round 499, by size. Each cell: length died by choice in r300-399, r400-499; longest at r300, 400, 499; alive r400 > r499; total length r400 > r499.

| side (games at or under 1200; above) | at or under 1200 cells | above 1200 cells | above 1200: dragons beyond 15 tiles of the longest, r400 > r499 |
|---|---|---|---|
| ours B7 (18; 20) | 23, 65; 4.7, 12.0, 29.9; 30 > 13; 93 > 72 | 66, 91; 24.1, 30.9, 56.4; 50 > 29; 177 > 194 | 37 > 23 |
| ours B7Q (9; 10) | 11, 69; 4.8, 12.7, 28.7; 28 > 6; 89 > 56 | 62, 96; 26.0, 32.1, 47.9; 56 > 40; 190 > 215 | 42 > 32 |
| WeHaveQuizzes (24; 30) | 58, 93; 10.1, 33.2, 57.3; 26 > 6; 104 > 99 | 133, 285; 21.7, 40.9, 71.9; 52 > 13; 318 > 271 | 40 > 10 |
| Big Bobs Bots (30; 27) | 20, 67; 5.1, 10.6, 21.1; 29 > 12; 84 > 66 | 47, 215; 7.8, 14.9, 35.7; 59 > 35; 247 > 218 | 44 > 24 |
| rank-1 (167; 178) | 21, 63; 11.9, 18.8, 41.1; 28 > 12; 96 > 92 | 77, 113; 16.2, 35.1, 56.3; 38 > 21; 211 > 241 | 27 > 16 (every tenth game) |
- [M] When it starts. Half of WeHaveQuizzes' games have their fifth death by choice by r345 (at or under 1200 cells) and r366 (above); rank-1 above 1200 cells lets 66 of its 77 die in r350-399. Ours steps up at round 400 exactly: per 25 rounds 1 to 7 before and 20 to 23 after at or under 1200 cells, 12 to 19 and 27 to 30 above (B7, B7Q).
- [M] Who is fed. Ours in r400-499: 90 to 92% of feeders die within 3 tiles of a team mate at least twice as long, our longest in 44 to 51%; mean length 2.4 to 2.6. WeHaveQuizzes: mean 4.5, 16% are 6 or longer, the mate is their longest in 25%: it feeds several long dragons where they stand (second longest at the end above 1200 cells 44; ours 23 to 27, rank-1 33). Rank-1: mean 3.6.
- [M] The 56 rule leaks. Above 1200 cells B7 and B7Q feed all through r200-399 (62 to 90 length per 100 rounds); of those pearls the longest eats 20 to 23% and short dragons 52 to 63% (r400-499: 29 to 36% and 28 to 33%; rank-1 then: 29% and 22%, with 42% to other long dragons). A lead, not a card: I found no single line that fixes it.
- [C] Our rules. `grow_round` is 300 at or under 1200 cells and 150 above (487-488): from then a dragon longer than 4 does not split (1060) and the longest dragon a dragon knows of is leader and never splits (1048, 3407-3409); in B7 and B7Q both wait above 1200 cells while under 56 are alive (`LEADER_FULL_UNITS`, 3403-3405). `feeding_phase` (5002-5005): after `feed_round` = `ENDGAME_ROUND` 400 (492), 300 once a live queen has called it (542-547), or after round 200 while 56 are alive (`FEED_CAP_UNITS`, `FEED_CAP_ROUND`). A feeder is a non-queen at most half the leader's length and within 15 tiles of it (2333-2340, 4995-5000).
## 3. Our longest dragon's deaths (job 3)
- [M] Online, three arms: 127 deaths at 8 or longer, 118 of them rammed. The rammer is 4 long, takes 3 steps and starts 3 tiles away (medians); it is 2 to 5 long in 104 and pays segments for the lunge in 96; none of ours is within 5 tiles in 70. Our dragon is 12.5 long at round 288 (medians); 24 fall after round 400. Ladder: 341 deaths, 318 rammed.
- "Card-54 ring" = tiles an enemy head inside the leader's 7 by 7 view reaches with its free steps plus one paid step. "Full ring" = the same with every step it can pay. Counted on the leader's last turn before the ram. "Decisive" = the leader was longer than their final longest and we lost a race game.

| leader at least | online: rammed (with a last-turn record) | rammer in view | a tile outside the card-54 ring existed; on both last turns | leader stood inside that ring with such a tile beside it | same, full ring | decisive | ladder: rammed (record) | in view | stood inside the card-54 ring with a clean tile; full ring | decisive rams; avoidable, card-54 ring / full ring |
|---:|---|---:|---|---:|---:|---:|---|---:|---|---|
| 8 | 118 (111) | 60 | 82; 74 of 105 | 8 | 19 | 1 | 318 (301) | 183 | 53; 69 | 18; 1 / 3 |
| 12 | 69 (65) | 34 | 48; 46 of 64 | 5 | 12 | 1 | 197 (185) | 108 | 30; 39 | 17; 1 / 3 |
| 16 | 38 (35) | 19 | 24; 24 of 35 | 2 | 6 | 1 | 109 (99) | 67 | 19; 24 | 16; 1 / 3 |
| 20 | 25 (23) | 14 | 16; 16 of 23 | 2 | 4 | 1 | 77 (70) | 44 | 13; 14 | 14; 1 / 3 |
| 31 | 14 (13) | 7 | 10; 10 of 13 | 0 | 1 | 1 | 41 (37) | 26 | 9; 8 | 9; 1 / 2 |
- [M] The rule nearly always has a clean tile to offer and the leader is nearly always standing on one already: it would have changed the last move in 8 of 111 rams online and 53 of 301 on the ladder. The others come from out of view (51 of 111) or from further than free steps plus one (96 of 118 paid for the lunge).
- [C] The live bot keeps further off than card 54 already: from length 8 (322, 5441-5469) a tile inside an enemy's ring loses to a less exposed one, and that ring is the enemy's visible parts, plus 2 when we are 15 or longer, up to 6 steps (2505-2512).
- [M] Per 100 leader turns at 8 or longer the leader ends inside the full ring of an enemy head within 12 tiles, seen or not, 2.2 times (B7), 2.7 (B7Q), 6.7 (MAIN), rank-1 2.4, WeHaveQuizzes 1.6; it is rammed before its next turn 0.19, 0.23, 0.57, rank-1 0.24, WeHaveQuizzes 0.09.
## 4. What each option would have turned on the final board (job 4)
| option | online: of 28 lost on length, not wiped out | ladder: of 91 | price |
|---|---|---|---|
| protect the leader from a lower length (card-54 ring from 8) [M] | 0 (the one decisive ram came from out of view) | 1 (3 with the full ring) | none measured |
| keep two long dragons (the longest halved) [M] | 0 | 2 | 9 of our 18 wins on length online, 65 of 113 on the ladder |
| leader rules earlier [E] | 0 | not counted | without feeding the longest gains 1 to 4 per 100 rounds (MAIN r200-399); diag-islands has the price |
| feed 50 rounds earlier (card 2) [E] | 2 to 5 | not counted | 50 rounds of trades (line 2717) |
| far feeders walk in (card 1) [E] | 3 to 5 | 16 to 22 | untested code |

[E] Card 1 is counted per game as 0.2 times the length of our dragons that may feed and stand further than 15 tiles from the longest at round 400 (lg_rally.py; online 3 with the 16 to 30 tile band only and 5 with all, ladder 16 and 22). Card 2: our leader gains 6 to 12 in r450-499, the tail rate that 50 more rounds would add; 2 lost games have a gap up to 6 and 5 up to 12.
## Why, in the code
- [M][C] Far dragons stay out. 1422309 (64 by 64, lost 26 to 70). r400: our longest #617 (17) at (60,18), 56 others, 9 within 15 tiles, 47 of length 2 to 7 at 16 to 54 tiles. r499: our longest #794 (26) at (54,45), 55 others, again 9 within 15 tiles; our total is 230 in 56 dragons, theirs 228 in 13 (70, 45, 22, 19, 16). Line 2338: further than `feeder_approach` (15, line 48) a dragon is no feeder. Line 606: the branch that would send it is dead while `rally_fresh` is 0 (254, 498), and it is 0 in every source I have (agg6, agg7, agg8, sr51, um47d, bl17594).
- [M] How they do it, same game, r418-423: their #538 grows 44 to 47. #626 (2 long) dies by no action at (36,21), 4 tiles from its head at (33,22); #615 (3) and #712 (2) die at (38,18) and (36,18), in the column it is walking up from (36,22). #712 had been split off #631 (8 into 6 + 2) at r418: a medium dragon sheds 2-long children that die in the leader's path.
- [M][C] The ram that cost the live arm its lead, 1422314 r232-235: our #405 (36) is at (8,55), (9,55), (9,53), (10,53) on four turns with their #289 at 3 to 4 tiles in view. At r235 #289 (4 long, one free step) goes (9,56), (10,56), (10,55), (10,54), (10,53) and eats the pearls on (10,56) and (10,54) on the way, which pay for the lunge. Lines 743-756: a cornered long dragon sprints only if `sprint_escape` finds a path, else splits; with 9 free steps a turn it took one or two. Their final longest was 91: the ram did not decide the game.
- [C] After `feed_round` no trade is started (2717), and from it `board_short()` is false (3404), so on a board under 56 above 1200 cells the leader rules also begin there.
## The cards
title: Far feeders walk to the leader in the endgame
slug: endgame rally
### Claim
New `RALLY_END_FRESH` (0 = as now; test 25, the age at which leader news is dropped, `SONAR_STALE`). After `feed_round` the existing `rally_ready()` route (606-608, 4986-4993) is on: a non-queen at most half the known leader's length and further than 15 tiles from its last known position walks there, then feeds as now. Claim: above 1200 cells the length standing far from the leader at the end reaches it instead.
### Evidence
Above 1200 cells the length that may feed within 15 tiles of our longest drains in r400-499 (31 to 18, B7) while the same beyond 15 tiles does not (89 to 96, B7; 99 to 107, B7Q). Dragons beyond 15 tiles at the end: ours 23 and 32, rank-1 16, WeHaveQuizzes 10. In 6 of the 28 lost games our total at the end is at least theirs.
### Expected signal
Above 1200 cells, on against off on the same maps and seeds, counted with lg_far.py and lg_faragg.py: length that may feed beyond 15 tiles at round 499 at most 60 (now 96 to 107); alive at round 499 at most 25 (29 to 40); length dying by choice in r400-499 at least 140 (91 to 96); the longest's share of those pearls not under 25% (29 to 36%); our longest at round 499 up by 10 or more (48 to 56). At or under 1200 cells little moves (27 to 30 such length at round 400). At 0 the replays are identical.
### What would show it's wrong
The far length does not fall: the dragons know no leader or the route finds no path, the mechanism fails, not the idea. It falls and the longest does not grow (its share under 20%): the pearls go to other long and short dragons. The leader is rammed more (above 0.4 per 100 leader turns; now 0.19 to 0.23), or wins by elimination or on the queen fall.
```diff
@@ 254  constexpr int RALLY_FRESH = 0;
+constexpr int RALLY_END_FRESH = 0;   // 0 = off; test 25
@@ 606
-        if (rally_fresh > 0 && route_target < 0 && rally_ready()) {
+        if ((rally_fresh > 0 || RALLY_END_FRESH > 0) && route_target < 0 && rally_ready()) {
@@ 4986  bool rally_ready() const {
+        int const fresh = RALLY_END_FRESH > 0 && round > feed_round ? RALLY_END_FRESH : rally_fresh;
-        if ((QH_SCOUT && qh_on) || ... round - known_leader_round > rally_fresh ||
+        if (fresh <= 0 || (QH_SCOUT && qh_on) || ... round - known_leader_round > fresh ||
```
title: The feeding phase starts at round 350
slug: feed 350
### Claim
`LC_FEED_ROUND` (line 256, read at 492) stays 0 by default; the test arm sets 350, so `feed_round` is 350 instead of `ENDGAME_ROUND` 400. Games with a live queen keep 300 (545-547). Claim: with our queen dead the leader is fed 50 rounds longer and is longer at round 400 and at the end. Diff: line 256, `constexpr int LC_FEED_ROUND = 0;` to `350` in the test build only.
### Evidence
The timelines of section 2: both stronger teams build their leader before round 400 (longest at round 400: WeHaveQuizzes 33 and 41, rank-1 19 and 35, B7 and B7Q 12 to 13 and 31 to 32, by size). Our own games that fed from round 300 because the queen lived (ladder, 55 full games): longest 9.2 at r300, 26.8 at r400, 38.7 at the end, against 7.9, 12.3 and 32.9 in the 94 that began at 400.
### Expected signal
Games with our queen dead by round 300: length dying by choice in r350-399 at least 30 at or under 1200 cells (now 4 to 13) and at least 45 above (30 to 31); longest at round 400 at least 18 at or under 1200 cells (12.0 to 12.7); longest at round 499 up by 6 or more on the same maps and seeds. Games with a live queen at round 300 unchanged.
### What would show it's wrong
The longest is up at round 400 and not at 499: the stock within 15 tiles is used up, card 1 first. Total length at round 499 falls by more than the longest gains. Fewer enemy dragons die to us in r350-400 or fewer wins by elimination (trades stop at `feed_round`). Above 1200 cells under 56 alive, the eating and splitting step of diag-islands appears at round 351.
## Against it
- [M] The gap is mostly total length. In 21 of the 28 our total at the end is under 0.8 of theirs; above 1200 cells WeHaveQuizzes holds 318 at round 400 against our 177 to 190. And B7's longest above 1200 cells already equals rank-1's (56.4 against 56.3), with rank-1 leaving as much length that may feed far from its leader as we do (112 against 96 to 107 at round 499, every tenth game). The two cards reach the 6 or 7 games in which we had the length.
- [E] 0.2 is the rate of feeders that were already near. Walkers arrive late and eat on the way, and on a 64 by 64 board there are three or four local leaders (1422309 r499: 26, 22, 17, 12), so the far length is shared out. [C] The rally branch has never run online; it needs the survey to reach the leader's last position (2996) and news at most 25 rounds old.
- [M] A longer leader is a bigger loss when rammed. Decisive rams are 1 game of 180 today and 13 of 500 on the ladder; they can only rise with more length in one dragon, and section 3 finds no rule that stops them.
- [M] Card 2's own-data support compares different games (queen alive against queen dead), and on the ladder the games that fed from round 300 won the race less often (11 of 19 against 46 of 69).
- [M] Two opponents, 15 layouts, one day. Both cards hit the same few games (1403640, 1408551, 1426398 in both counts).
