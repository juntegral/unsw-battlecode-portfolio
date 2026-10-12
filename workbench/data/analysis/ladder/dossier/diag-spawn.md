# Rank-1 is beside the tile when the pearl comes; ours is standing on it (team 1119; 500 main ladder games, 597 of rank-1's; written 8 Oct 2026)

1. **What rank-1 does at spawn tiles that we do not.** It does not stay longer after a meal than ours, and its dragons at fast tiles are not the ones that get rammed. It has a head within 1 step of the tile in the round the pearl is born at 17.6% of births against our 10.1% (rounds 101-300, tiles of every speed, 15 of 19 layouts) and eats in the birth round 18.8% against 9.1%. The one step that differs: a head beside an empty tile whose countdown shows 1 steps onto that tile in 73.3% of our cases and 26.8% of rank-1's (13.5% on tiles that spawn rarely), and a tile with a body on it does not spawn.
2. **The change.** One switch, SPAWN_CLEAR (default off): a dragon does not step onto an empty tile whose countdown is at or below its own length (4 at most); it steps beside it and eats the pearl once it is there.
3. **How sure.** Sure of the fault: all 1,097 games, ours the higher on all 19 layouts (62 to 86%), a recount by another method gives 62.7% against 19.9%, and our scoring lines predict it. Sure it costs pearls: 40.9 spawn attempts a game end under a body of ours that came onto the empty tile. Less sure of the size, about 10 to 15 more natural pearls a game on the 243 we eat (estimate). It does not close the gap at fast tiles: rank-1 spends a third more of its dragon-time there and I could not tie that to a line.

Labels: [M] measured by my scripts in dossier/work/: sp_scan.py (one record per natural pearl birth of rounds 0-300 in all 1,097 games), sp_class.py (tile classes from 304 games; same class as the rebuilt maps of local/maps2 and maps3 on 2,105 of 2,281 spawning tiles, the rest nearly all tiles not seen to spawn), sp_agg.py (tables, kept in sp_agg.txt), sp_tick.py and sp_tickagg.py (spawn attempts seen through the mirror tile, sp_tickagg.txt), sp_recount.py (the recount), sp_view.py (replay frames). [C] read from battlecode/mybot2/main.cpp, line given. [E] my estimate.
Terms: "a / b (k/n)" = ours / rank-1 as the mean over layouts, each layout once (layouts where rank-1 is the higher, of those that have the case). Steps are counted along open edges and portals. Tile classes are by measured rounds between spawn attempts (free round starts per birth). "Countdown 1" = the tile tries to spawn at the start of the next round (local/maps2/semantics.json). A tile and its mirror share one countdown (rules/pearls.md), so a pearl born on one dates the attempt on the other: 652,271 such attempts, none where the tile was free and nothing was born.

## 1. Where the heads are when a pearl is born (job 1) [M]

Natural births of rounds 101-300 (183,256 in our games, 253,633 in rank-1's), each followed to the end of its game.

| Rounds between attempts (tiles a game) | A head within 1 step at birth % | A head within 2 steps in each of the 3 rounds before % | Eaten by the side in the birth round % | Wait when the side eats, rounds | The side eats % |
|---|---|---|---|---|---|
| 1, every round (11) | 1.4 / 7.2 (10/13) | 39.0 / 61.0 (10/13) | 3.1 / 13.7 (10/13) | 12.1 / 6.1 (0/13) | 42.0 / 62.2 (11/13) |
| 1.5 to 8 (16) | 11.5 / 25.5 (7/8) | 21.3 / 38.9 (7/8) | 9.3 / 22.9 (6/8) | 6.4 / 4.8 (1/8) | 41.4 / 59.6 (7/8) |
| 8 to 25 (9) | 15.4 / 23.5 (6/7) | 24.0 / 31.5 (4/7) | 13.0 / 22.6 (6/7) | 5.0 / 2.6 (0/7) | 46.1 / 57.1 (6/7) |
| 25 to 80 (21) | 16.3 / 22.8 (11/13) | 21.0 / 26.5 (11/13) | 13.8 / 21.4 (11/13) | 9.0 / 3.6 (1/13) | 41.3 / 55.4 (11/13) |
| 80 or more (223) | 16.8 / 24.2 (14/18) | 17.9 / 25.2 (15/18) | 15.4 / 23.0 (14/18) | 8.0 / 5.5 (4/18) | 46.1 / 56.7 (14/18) |
| all | 10.1 / 17.6 (15/19) | 25.3 / 36.5 (15/19) | 9.1 / 18.8 (15/19) | 8.4 / 5.0 (1/19) | 43.5 / 57.1 (15/19) |
| all, rounds 0-100 | 6.3 / 10.2 (17/19) | 21.5 / 29.5 (17/19) | 6.0 / 10.8 (14/19) | 29.5 / 19.3 (2/19) | 46.8 / 53.4 (12/19) |

- Within 1 step in each of the 3 rounds before: 10.2 / 16.3 (15/19). A dragon must move every turn, so it can hold 1 step only by going over the tile or by splitting; the 2-step column is the one that shows standing by.
- Who eats (all, 101-300): the side 43.5 / 57.1, nobody 3.8 / 2.6, the opponent the rest. Where the eater was at birth: within 1 step 21.6 / 28.4, 2 steps 16.1 / 20.8, more than 6 steps 33.5 / 24.4 (3/19).
- The other side of the same games: our opponents have a head within 1 step at 13.8% of births, rank-1's opponents 11.3%. We are below our own opponents.
- The gap is as wide on tiles that spawn every 25 rounds or less often, where our hot-tile rule cannot act, as on fast ones. It is not a fast-tile matter.

## 2. After the meal, heads per cluster, the countdown (job 2) [M]

| After a natural pearl is eaten on the tile, rounds 101-300 | Stays within 2 steps for 8 rounds % | Goes 3 or more away, back within 12 % | Leaves % | Dies within 8 rounds % | Of the next 8 round starts within 1 step; within 2 |
|---|---|---|---|---|---|
| every round (18,115 and 43,230 meals) | 1.5 / 2.4 | 3.4 / 2.4 | 11.7 / 14.8 | 83.5 / 80.4 | 2.7 / 2.8; 3.4 / 3.5 |
| 1.5 to 8 (21,649 and 34,525) | 7.0 / 9.0 | 19.9 / 18.9 | 35.7 / 31.9 | 37.4 / 40.1 | 2.8 / 2.9; 4.2 / 4.4 |
| 8 to 25 (9,042 and 16,857) | 7.0 / 6.1 | 19.9 / 18.0 | 50.7 / 49.5 | 22.3 / 26.4 | 2.8 / 2.6; 4.2 / 4.0 |

- The same on both teams: neither stays, neither circles. The every-round tiles lie in dead-end rows and the dragon that eats there dies there four times in five on both sides (ours on a wall or its own body, 216 per 1000 dragon-rounds at a cluster; rank-1's by an illegal split, 189). The same dragon eats the next pearl of a fast tile within 12 rounds in 15.2 / 13.3.
- Heads per cluster of fast tiles (every round and 1.5 to 8; tiles within 2 steps of each other), rounds 101-300: a cluster has at least one head within 2 steps in 22.9 / 34.9 of rounds (12/15), and two or more in 13.5 / 25.4 of those (11/15). Heads within 2 steps at a birth, all tiles: none 75.9 / 62.7, one 18.9 / 25.6, two or more 5.2 / 11.7 (16 and 17 of 19). Dragon-rounds within 1 step of a cluster: 5.7 / 7.7 (12/19); rank-1 also has 5,615 dragon-rounds a game in rounds 101-300 against our 5,060.

What both do with the countdown, rounds 0-300, every attempt whose mirror tile got its pearl; pooled, all tile classes:

| The tile is empty | Ours | Rank-1 | Our opponents | Rank-1's opponents |
|---|---|---|---|---|
| Head beside it, countdown 1: steps onto it % | 73.3 (8,430 of 11,503) | 26.8 (4,776 of 17,793) | 47.8 | 32.0 |
| Head beside it, countdown 2: steps onto it % | 53.4 (4,892 of 9,156) | 26.8 | 43.9 | 36.3 |
| Head 2 steps away, countdown 2: the pearl is born % | 48.5 | 86.1 | 71.4 | 80.7 |
| Head 2 steps away, countdown 1: beside it at birth % | 61.3 | 76.7 | 66.7 | 68.7 |
| Beside it at birth: eats in the birth round % | 80.8 | 87.1 | 78.6 | 78.9 |
| Beside at countdown 1, stepped back: eats it the round after birth % | 29.5 | 56.1 | 42.7 | 51.0 |
| Attempts a game that met the side's body after a step onto the empty tile (head on it + body over it) | 18.7 + 22.2 | 9.2 + 20.1 | 12.1 + 22.3 | 9.0 + 19.4 |
| The same per 100 pearls born, tiles of 25 rounds or more | 16.5 | 5.1 | 11.3 | 8.1 |
| The same per 100 pearls born, tiles of 1.5 to 25 rounds | 18.0 | 19.8 | 19.0 | 13.6 |

- By layout the first row is 61.6 to 85.5 for ours and 0 to 53.4 for rank-1; ours is the higher on all 19. By tile class, ours / rank-1: 1.5 to 8 rounds 74.7 / 49.8, 8 to 25 65.0 / 40.4, 25 to 80 71.5 / 23.2, 80 or more 75.6 / 13.5. Rank-1 keeps off the tiles where a lost attempt costs most. By length of the dragon: 2 long 73.5 / 21.6, 3 long 78.0 / 30.8, 4 long 39.3 / 24.1, longer 67.6 / 35.5.
- Pearls born a game on tiles that do not spawn every round: 397 / 457 (17/19). Of all attempts on tiles of 80 rounds or more, 76.5% are born in our games and 87.7% in rank-1's (18/18).
- Recount (sp_recount.py, every 8th game, 138 games; whole-board snapshots, grid neighbours, walls ignored): 62.7% (1,074 of 1,712) against 19.9% (531 of 2,666); opponents 36.3 and 27.6. Births of rounds 101-300 with a focal head on a grid neighbour: 12.2% against 23.4%.
- Replays (sp_view.py): 1250697 rounds 60-65, ours of length 2 circles the 2 by 2 block that holds tile (18,2) for five rounds, is on the tile at round 65 when it tries to spawn, and walks off. 1332077: the same tile (11,31) is stepped on at countdown 1 in rounds 73, 117, 149 and 165; 26 such steps by ours in that game, none by the opponent. 1051267 (rank-1) rounds 189-192: a dragon of 2 walks along a row, turns beside (23,3) in the round its pearl is born and eats it that round.

## 3. Are the dragons at spawn tiles the ones that get rammed? (job 5) [M]

- No. Rammed by the other team per 1000 dragon-rounds, rounds 101-300: a dragon in its third round or more within 1 step of one fast cluster, rank-1 0.87 (119 in 137,369; layout mean 0.47), ours 1.19 (0.92); a dragon elsewhere 2.93 and 3.24. Rounds 0-100: 0.71 and 1.21 against 2.72 and 2.81.
- Such rounds are 2.6 / 3.8 of all dragon-rounds (12/19) and the dragon is 3.7 / 3.4 long. What ends it is the dead end of section 2, the same on both sides.
- The switch below adds no waiting. Ours already stand by: in 25.3% of births one of ours had been within 2 steps for 3 rounds. It changes where the last step goes.

## 4. Why, in the code

- [C] 5236-5251: each of the four steps is scored as score_step(destination) plus look_gain(destination). 4964 with 2904: the survey starts on the destination with steps = 1.
- [C] Soon rule, 2961-2967, 349, 351, 3260-3266: a seen tile with countdown c counts when c is at most steps + 6, at distance max(steps, c), worth 0.45 x (260 - 40 x distance). Head beside the tile, c = 1: the step onto the tile is distance 1, 99 points; any other step reaches it at step 3, 63 points.
- [C] Hot rule, 2969-2973, 357: the same distance at weight 1.2: 264 against 168. Look-ahead, 3205-3209, 225-227: a tile counts as half a pearl when c is from 1 to t, t being the step that reaches it; t = c is the arrival one round early, the one that blocks. Onto the tile now 40, the path that comes back at step 3: 29.
- [C] 5021-5033 takes the largest bonus; 5055-5057 adds EAT_BONUS only for a pearl. No line subtracts for a tile that is about to spawn. The tile wins by 47 points (soon and look), 107 with a hot mark, against 1.5 a tile of room (335-336). [M] It fits: 73% at countdown 1; 53% at countdown 2, where soon gives the tile +18 and look gives the way round +29; and 39% at length 4, where ours splits instead of moving (1028, 1048).
- The other rules the brief names. [C] Pull ends at 6.5 steps (3260-3266): [M] from 4 to 6 steps three rounds before, ours is within 2 steps at birth in 26.9 and rank-1 in 31.6; small. [C] Nearest team-mate (2930-2932, 2969): [M] two or more of our heads within 2 steps at 5.2% of births against 11.7%; this fits the rule and fits simply having fewer dragons there, and I did not separate the two. [C] Mark wiped above countdown 8 (1594-1596): [M] the gap is as wide where no mark can exist. [C] Leader zone (2339-2363, 57, 468): [M] at births within 9 tiles of our longest dragon after round 100 a head of ours is within 1 step in 14.9% (all births 10.1) and we eat 63.4% (43.5); no sign. [C] A split child starts blank (436-444): [M] 41.0 / 44.7 of eaters split off under 15 rounds before, on fast tiles 52.3 / 47.4; no sign.

## 5. The card

title: Do not stand on a tile that is about to spawn (default-off SPAWN_CLEAR)
slug: spawn clear

### Claim
[M] A dragon of ours beside an empty tile steps onto it in the round before it would spawn in 73% of cases, rank-1 in 27%, and the pearl is then not born. [C] Proposal: add "constexpr bool SPAWN_CLEAR = false;", "constexpr int SPAWN_CLEAR_MAX = 4;" and "constexpr double SPAWN_CLEAR_PENALTY = 300.0;". In score_step, beside the EAT_BONUS lines (main.cpp 5055-5057): when SPAWN_CLEAR is on, the destination holds no pearl, was seen this round, its countdown is from 0 to min(length, SPAWN_CLEAR_MAX), and the dragon is not a feeder and not the leader, subtract SPAWN_CLEAR_PENALTY. One condition, nothing else changes. A dragon of length L lies on a tile for the L round starts after its head enters, so a countdown of L or less is an attempt that fails (rules/pearls.md, rules/execution-order.md). 300 is what a pearl on the step is worth (EAT_BONUS, line 99) and is below every safety term (enemy head 450, no tail 600, queen guard 1500). Switch name: SPAWN_CLEAR.

### Evidence
- [M] Head beside the empty tile at countdown 1: 73.3% of ours step on (8,430 of 11,503), 26.8% of rank-1's; at countdown 2: 53.4% against 26.8%. From 2 steps away with 2 rounds to go the pearl is born in 48.5% of our cases and 86.1% of rank-1's (18/18 layouts).
- [M] Every layout (61.6 to 85.5%), every dragon length that moves, both windows; our opponents 47.8%, rank-1's opponents 32.0%. Recount by another method: 62.7% against 19.9%.
- [M] 40.9 attempts a game end under a body of ours that came onto the empty tile (18.7 the head itself, 22.2 the body behind it), against 29.2 for rank-1 with a third more dragon-time at tiles. On tiles of 25 rounds or more, where the next attempt is far off: 16.5 per 100 born against 5.1.
- [C] The three bonuses of section 4 all peak on the tile and nothing subtracts. [M] When ours is beside the tile at birth it eats the pearl that round in 80.8%.
- [M] Replays 1250697 (rounds 60-65) and 1332077 (tile 11,31, four times).

### Expected signal
[E] sp_tick.py and sp_tickagg.py run on any replays of ours and name no map. Head beside an empty tile at countdown 1 steps on: 73% to under 30% (rank-1 27%); at countdown 2: 53% to under 30%; from 2 steps away at countdown 2 the pearl is born: 48% to 80% or more (rank-1 86%); attempts ended by our own empty step: 41 a game to under 25, and 16.5 per 100 born to 6 or less on tiles of 25 rounds or more (rank-1 5.1). About 15 more pearls born a game beside our heads and 10 to 15 more eaten (4 to 6% of our natural pearls of rounds 0-300). The marks of the brief move less: births with a head of ours within 2 steps 24.1% to about 27%, wait 8.4 to about 8.0 rounds, and "within 1 step at birth" hardly at all, since a dragon that steps back is 2 steps away when the pearl comes.

### What would show it's wrong
- The step-on rate at countdown 1 stays above 50%: the penalty loses to room and territory, or the steps come from a path that does not pass score_step (stride, escape, harvest).
- The rate falls and pearls born a game on tiles that do not spawn every round do not rise, or our natural pearls eaten by round 100 and 300 do not rise on the same seeds: the steps we stop were not the ones that cost.
- Our deaths on walls, our own body or another body rise by more than a tenth per 1000 turns: the detour is paid for in safety.
- The leader or a feeder walks differently: the switch reached code it should not.

## 6. Against it

- [M] Size. 18.7 head-on-tile kills a game against rank-1's 9.2; at rank-1's rates the countdown-1 and countdown-2 moments (23.0 and 18.3 a game) give about 15 more births. We eat 243 natural pearls a game born in rounds 0-300 and rank-1 345 (other opponents). This is a tenth of that distance, not the gap.
- [M] At fast tiles, the brief's subject, it separates nothing: rank-1 steps onto tiles of 1.5 to 8 rounds half the time (49.8%) and loses as many attempts per 100 born there as we do (19.8 against 18.0). What rank-1 has there is presence, a third more dragon-time and twice the share of births with two heads near, and nothing in this count says which line of ours would give that. No card for it.
- [M] A saved pearl is not an eaten pearl. When ours steps back today it eats the pearl the next round in 29.5% (rank-1 56.1%), later in 47.6% and the other side in 8.4%. [E] Those are the cases where our scoring already wanted something else; a dragon that wanted the tile should come back for the pearl, but that is not measured.
- [M] Stepping on is common: our opponents 47.8%, rank-1's opponents 32.0%. Nothing here links it to results. [E] sweep.md and the F20 verifier found no link from heads at busy tiles to wins; this card claims pearls, not wins.
- [M] What the mirror shows is a floor: an attempt is seen only when the mirror tile was free and got its pearl, so kills on both tiles of a pair, and per-game counts, are too low; rates use attempts on the same footing.
- [E] The penalty keeps a short dragon off up to four tiles around it for a round or two. In a one-wide passage it has no other step and the rule does nothing; where room is tight 300 may tip a choice the room terms had right.
- Not checked: that main.cpp on disk is the build that played (the replays behave as these lines say); the countdown as a bot reads it comes from the rule text and the engine probe, not from a bot log (the range starts at 0 to cover a reading one lower); the leader zone uses the true longest dragon, not what each dragon believes; no build has run and no local pair was played.
- Housekeeping: the Write tool was refused for this folder (path spelling), so the scripts and this file went through the Python route. The second sp_tick pass was stopped once by the 10-minute background limit and run again to the end. Left in work/: sp_*.py, sp_tiles.json, sp_f-*.jsonl (about 48 MB), sp_k-*.jsonl, sp_t-*.jsonl, sp_agg.txt, sp_tickagg.txt and three small test files. Nothing else was written.
