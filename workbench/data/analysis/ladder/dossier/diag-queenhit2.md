# The queen keeps 3 and is still rammed: what is left, on the new build's own games
Sample: new build `agg8-q1`, 30 games, 5,380 queen turns, 22 queen deaths (13 head-on hits, 5 wall, 1 own body, 3 as the mover), 8 alive at the end. Beside it main `agg7-m1` + `agg7-m2` (60 games, 10,739 turns, 49 deaths, 34 hits) and this morning's table (45 games). `agg8-q2` and `agg7-m3` had not arrived. **M** = measured (`work/q2_*.py` on the replays), **C** = read from `data/online/smoke/agg8-bot/main.cpp` (line), **E** = estimate. Every count is M unless marked.
## 1. Three lines
1. **What still kills her.** 8 boxed hits (5 with her 2 long and a clean tile two or three steps off that she could not pay for, 3 with her 3 long and no clean tile inside her paid reach), 5 rams of four or five steps onto a tile the ring called clean, 6 dead ends with no enemy head in reach (wall 5, own body 1), 3 runs into a head. QS_KEEP_LEN removed the split as the road to 2 (14 of main's 23 two-long hit deaths; 1 of 8 now, a wait split) but not being 2 when hunted: 6 of the 8 two-long hit deaths came by a paid sprint from 3 (4 of them with a clean single step open), 1 by the split at line 638, and after a paid sprint she never grew back (0 of 7). Her turns at length 2 fell from 41.8% to 9.3%, her boxed turns at length 2 only from 23.5 to 21 per 30 games.
2. **Change.** No card. Counted on the outcome (a death the switch turns into an open escape on paper), nothing reaches a quarter of the 22: more open sides 4 (5 changed moves), no paid sprint below 3 with a clean step open 1, no split at 638 below 3 1, a short team mate near her 0. Keep 4 reaches 6 on paper, but that is the same paper count that gave keep 3 ten of 19 this morning and then moved boxed deaths from 10 to 8 per 30 games, and 9 of 11 paid escapes from a boxed turn ended in her death within ten turns.
3. **How sure.** Causes, lengths and the road to each length: high (they agree with the other tool's `online/agg7-games.json`, checked game by game for the 8 two-long hit deaths). Box and escape flags: my re-implementation of her view and rings, medium. "No card": medium-high for the four candidates as specified; 30 games, 15 layouts, 2 opponents.
## 2. Classes (exclusive; her last own turn), beside this morning's
| class | morning 45 games (m1 + sr51) | main 60 games (m1 + m2) | new 30 games (q1) | new: her length 2 / 3 / 4+ |
|---|---:|---:|---:|---|
| no clean tile: stepped on the pay tile | 11 | 12 | 3 | 1 / 2 / 0 |
| no clean tile: only hit tiles | 8 | 8 | 5 | 4 / 1 / 0 |
| rammer outside her 7 by 7 | 3 | 5 | 1 | 1 / 0 / 0 |
| rammer a child split off after her turn | 1 | 2 | 0 | |
| ring too small: pearls eaten on the way | 3 | 3 | 3 | 2 / 0 / 1 |
| ring too small: head cut by the view edge | 1 | 4 | 1 | 0 / 0 / 1 |
| **head-on hits** | **27** | **34** | **13** | 8 / 3 / 2 |
| her own move: wall | 7 | 10 | 5 | 1 / 4 / 0 |
| her own move: own body (morning: + 1 other body) | 3 | 3 | 1 | 1 / 0 / 0 |
| her own move: ran into a head | 1 | 2 | 3 | 2 / 1 / 0 |
| alive at the end | 7 | 11 | 8 | |
- Per 30 games, main to new: boxed hits 10 to 8, other hits 7 to 5, deaths by her own move 7.5 to 9. E: at 30 games none of the three differs from main beyond chance (hits 13 of 30 against 34 of 60).
- How she came to 2 (the 8 two-long hit deaths): a paid sprint with a clean single step open 4 (9, 23, 43 and 67 turns before the hit; `sprint_escape()`, C 779 and 743, let in for a 3-long queen at 2864), the paid escape from a boxed turn 2 (6 and 8 turns before; C 642), the split at 638 with heads three steps off 1 (1 turn before; C: the new rule only blocks it when a paid escape exists), a wait split 1 (C 695, `QW_MIN_LENGTH` 4). Start of the game 0, forced split (649, 685) 0. On main: split 14, sprint with a clean step open 5, paid escape 4.
- The 8 boxed hits. Clean single step: 0 of 8. Paid escape open and not taken: 0 of 8. Two long with a clean seen tile two steps off 4, three steps off 1; three long with no clean tile within four steps 2, the nearest four steps off 1. What closed the box: two or more enemy heads with kelp on at most one side 5, kelp on two or more sides 3, a team mate's body 0 (main, 20 boxed: 8, 8, 4). Own heads within 3 tiles at the 13 hits: none 11, one 1, two 1; within 5: none 7, one 4, two or more 2. Rammer: seen on her last turn 12 of 13; 2 long 4, 3 long 4, 4 long 3, 5 long 2; steps 1: 5, 2: 1, 3: 2, 4: 4, 5: 1.
- Boxed turns (a ring on a tile, no clean step): new 31 (her length 2: 21, hit that round 5; 3 or more: 10 = 4 paid sprints, none hit that round; 2 splits at 638, both dead the next turn; 4 with neither, 3 hit). Main 62 (2 long: 47, 18 hit; 3 or more: 15, 3 hit).
- Wall and own body (6): on the last turn none had a tile to enter (kelp on three sides and her body 4, a team mate's head or body on the last side 2) and no enemy head was in reach in any. A mistake with a free tile open was not on the last turn but 1 to 8 turns before, when she left a tile that was not a pocket untaken (1, 3, 4, 6, 7, 8 turns). In 3 the last act with any choice was the wait split inside the dead end (C 695: the child leaves by the tail, the queen stays in front). A team mate stood on one of her four sides in the last three turns in 4 of 6 (main 7 of 13; on all her turns 3.3%). Boards of 600 cells or fewer: 12 such deaths in 30 games, larger boards 7 in 60 (both arms; C: `is_queen()` 3411 gates the queen's dead-end terms 5081-5092 and her ban from pocket harvests 1173 by `QUEEN_MIN_CELLS` 166).
- Ran into a head (3): herded by two 2-long heads into a kelp pocket, the head the only side left (1421766); the turn after the 638 split (1421777); a two-step sprint into the enemy queen, 3 against 3, which is the trade the code asks for (1422312; C 622, 3760).

| game | board | round, cause, her length | how she came to that length | last turn: what was open, what closed it | own heads within 3 / 5 |
|---|---|---|---|---|---|
| 1421767 | 64x64 | r85 hit, 2 | paid escape r77 | no clean step; clean tile 2 steps off; 2 heads (2 long), kelp 1 | 0 / 0 |
| 1421771 | 32x16 | r104 hit, 3 | wait split r100, ate 1 | no clean step, none within 4 steps; kelp 2, 4 heads, own tile in reach | 0 / 0 |
| 1421772 | 64x64 | r74 hit, 3 | routine split r21 | pay tiles and a closed pocket; clean open tile 4 steps off; rammer 4 long walked 3 | 0 / 0 |
| 1421773 | 32x32 | r118 hit, 2 | sprint with a clean step open r75 | clean tile 2 steps off; heads on both flanks for 5 turns, then kelp ahead | 0 / 1 |
| 1421776 | 25x25 | r54 hit, 2 | paid escape r48 | clean tile 2 steps off; 4 heads, no kelp | 0 / 0 |
| 1422313 | 32x16 | r74 hit, 3 | wait split r69, ate 1 | none within 4 steps; kelp 2; rammer 4 long walked 3 | 0 / 0 |
| 1422315 | 32x32 | r137 hit, 2 | sprint with a clean step open r70 | clean tile 3 steps off; 2 heads, kelp 1, own tile in reach | 2 / 2 |
| 1422316 | 25x35 | r105 hit, 2 | split at 638 r104 (4 to 2) | clean tile 2 steps off; kelp 2, 2 heads | 0 / 1 |
| 1421768 | 56x40 | r356 hit, 2 | sprint with a clean step open r347 | took a clean step; rammer 4 long walked 4 over a pearl | 0 / 0 |
| 1422314 | 64x64 | r81 hit, 2 | sprint with a clean step open r58 | clean step towards the head; rammer 3 long walked 4 | 0 / 1 |
| 1422319 | 32x16 | r59 hit, 4 | routine split r31, ate 1 | clean step towards the head; rammer 3 long walked 4 | 0 / 4 |
| 1422309 | 64x64 | r110 hit, 4 | routine split r104, ate 1 | clean step towards the head; rammer 5 long, cut by the view edge, walked 4 | 0 / 0 |
| 1422322 | 63x27 | r284 hit, 2 | wait split r262 | clean step; rammer 5 long outside her view walked 5 | 1 / 1 |
| 1421769 | 48x24 | r83 wall, 3 | wait split r81, ate 1 | no tile: kelp 3; last tile that was not a pocket 7 turns before | 0 / 0 |
| 1421779 | 32x16 | r139 wall, 3 | wait split r109, ate 1 | no tile: kelp 3; team mate's head beside her 2 of 3 turns | 1 / 3 |
| 1422308 | 40x15 | r157 wall, 3 | wait split r116, ate 1 | no tile: kelp 2, team mate's head on the last side | 1 / 3 |
| 1422310 | 56x40 | r109 wall, 2 | wait split r106 | no tile: kelp 3; team mate's body beside her the turn before | 0 / 3 |
| 1422311 | 48x24 | r113 wall, 3 | wait split r111, ate 1 | no tile: kelp 3; last tile that was not a pocket 8 turns before | 1 / 4 |
| 1422321 | 32x16 | r10 own body, 2 | split with no tile to enter r9 | no tile: kelp 2, her own new child on the last side | 0 / 0 |
| 1421766 | 40x15 | r77 into a head, 2 | paid escape r70 | kelp 2, own body, the head | 0 / 0 |
| 1421777 | 32x16 | r27 into a head, 2 | split at 638 r26 (4 to 2) | kelp 2, own body, the head | 1 / 5 |
| 1422312 | 24x12 | r58 into the enemy queen, 3 | routine split r46 | a clean step was open; she sprinted two steps into the enemy queen | 1 / 1 |
## 3. The turns before the box closes
- Standing tile, an enemy head within 3 steps, hit that round: kelp on two or more sides new 2 of 11, main 9 of 30; one side 3 of 96, 6 of 147; none 2 of 158, 8 of 237 (morning: 8 of 38, 6 of 124, 5 of 224). The tile she stands on still matters.
- The step. She steps to a tile with fewer open sides than the one she leaves while a clean (unringed, not a closed pocket) tile with more open sides was open, and is hit within 3 turns: head within 3 steps new 1 of 15, main 1 of 27; within 4: 3 of 32, 3 of 50; within 5: 3 of 39, 3 of 65. When she had a clean alternative and took the widest: within 3: 3 of 101, 7 of 171; within 4: 3 of 146, 17 of 314; within 5: 6 of 203, 20 of 429. Both arms, head within 5: 6 of 104 against 26 of 632; on main alone the narrowing step is not worse (4.6% against 4.7%). She is on the narrow tile mostly because nothing wider was clean.
- Team mates. Head within 3 steps, hit that round: no own head within 3 tiles new 6 of 239, main 17 of 329; one 0 of 24, 4 of 60; two or more 1 of 2, 2 of 25. Both arms: none 23 of 568 (4.0%), one or more 7 of 111 (6.3%). A short (3 or less) own head within 2 tiles: 4 of 48 against 26 of 631. A team mate's body kept her end tile out of a rammer's true reach on 1 turn in each arm (2 of 16,119 turns).
- Paid sprints. From a boxed turn at length 3: new 3, main 8; hit that round 0 and 1; hit within ten turns 2 and 5; dead within ten turns by any cause 3 and 6. With a clean single step open at length 3: new 4 (no enemy head within 5 steps at 2 of them), main 9; hit within 3 turns 0 and 1; later dead 2 long by a hit 4 and 5. Single clean steps at length 3 with a head 2 or 3 steps off: hit within 3 turns 0 of 31 and 3 of 96. The sprint buys nothing that shows and costs the segment the boxed escape needs.
## 4. The card(s)
**No card.** Outcome counts on the new build's 22 deaths (13 hits); a quarter is 6 (4 of the hits).
| candidate | main.cpp | deaths it would have changed | cost: fires with nothing following | verdict |
|---|---|---|---|---|
| head within N steps: take the clean tile with more open sides | 5410-5436 | N 3: a move changes in the last 3 turns of 3 deaths (1 hit); N 5: 5 (3 hits; one of the 5 is the trade with the enemy queen) | 33 and 66 per 30 games (main: 37 and 87 per 60 for 1 and 3 deaths) | under a quarter; no effect of the step on main |
| no paid sprint below 3 while a clean step is open | 2864, 743, 779 | she is 3 instead of 2 at 4 hit deaths; an escape opens on paper in 1 (1421773) | 4 fires, none followed by a hit within 3 turns as played | under |
| no split at 638 that leaves her below 3 | 638 | 2 fires, both dead the next turn; an escape opens on paper in 1 (1422316) | 0 | under |
| keep 4 instead of 3 | 137, 1057 | on paper 6 of the 8 boxed hits | routine splits 64 to 40 per 30 games on paper | paper only, see section 1; E: 1 to 2 deaths per 30 games |
| a short team mate stays within 2 tiles | none does this | 0: no lower hit rate with a mate near, and a mate on her side before 11 of 19 dead-end deaths | not built | no |
- Guard constants (C). `QUEEN_DEFEND_RADIUS` 0 (118, used 2736): a mate trades with an enemy head near her; it does not bring a mate to her. `QB_W_ESCORT` 0.0 (229, 3630-3638): she scores tiles near mates, only inside `QUEEN_BRAIN` (205, false). `QUEEN_GIVE_WAY` 0 (203, 5093-5102): the opposite, mates keep off the tiles near her. `QUEEN_GUARD_RADIUS` 0 and `QG_GUARD_RADIUS` 5 behind `QUEEN_GUARD_CELLS` 0 (112, 182, 178; 5194-5210): she keeps away from enemy heads. The one that was played: give-way 2 with `QUEEN_ALLY_BLOCK` (label gw3), 5 of 15 against live 6.0 of 15 and 3 of 15 against 3.5 of 15 (read from `data/online/smoke/gw3-*-result.txt`). No record of the others being on in DECISIONS.md, docs, research or versions.
- Nearest miss, not a card: a floor that completes QS_KEEP_LEN (both middle rows). 6 fires per 30 games; she is 3 or more instead of 2 at 6 of the 22 deaths (5 hits, 1 own move); the outcome changes on paper in 2. If a build goes out anyway it can ride along default off (not compiled; hunk numbers are `agg8-bot/main.cpp` lines):
```diff
@@ 137 @@ after constexpr int QS_KEEP_LEN = 3;
+constexpr bool QS_FLOOR = false;  // on: no split at 638 and no sprint_escape() that leaves the queen under QS_KEEP_LEN
@@ 638 @@ act()
-            if (!exposed && ct.can_split(keep) && !(QS_KEEP_LEN > 0 && hit_escape(path, true, 0))) {
+            if (!exposed && ct.can_split(keep) && !(QS_KEEP_LEN > 0 && hit_escape(path, true, 0)) &&
+                !(QS_FLOOR && length - keep < QS_KEEP_LEN)) {
@@ 2864 @@ sprint_escape(), before the first check
+        if (QS_FLOOR && real_queen() && !qs_plain && sprint_free() < 2 && length - 1 < QS_KEEP_LEN) {
+            return false;
+        }
@@ 2873 @@ sprint_escape(), the three-step try
-            if (found || (steps == 3 && (!force || sprint_reach() < 3))) {
+            if (found || (steps == 3 && (!force || sprint_reach() < 3 || (QS_FLOOR && real_queen() && length - 2 < QS_KEEP_LEN)))) {
```
## 5. Against it
- "No card" rests on outcome counts on paper from 30 games of one label. Counted by her length at death instead, the floor touches 6 of 22 and would pass the bar; I count it as 2 because 3 of those 6 were not boxed with a clean tile in reach and one ran into a head with kelp on two sides.
- Not replayed: what she does instead of the 638 split or the sprint. The 4 sprints were not followed by a hit within 3 turns, so the count cannot show whether they prevented one; the baseline (0 of 31, 3 of 96) says it is rare.
- Step away from the nearest seen head (take the farthest clean tile when one is within 5 tiles): fires in the last 3 turns of 4 of the 13 hits (main 8 of 34), 112 fires elsewhere per 30 games; stepping nearer is followed by a hit within 3 turns in 13 of 295 turns against 20 of 868 (both arms). It is the QS_AHEAD family, which added nothing locally, so it is not proposed; it is the count QS_AHEAD should move if it is ever played online.
- The dead-end deaths (6 of 22, 13 of 49 on main) are the largest class no candidate touches. The board-size gap (12 in 30 games against 7 in 60) is confounded with layouts: one 512-cell layout gave 6 of the 12 in its 6 games. On small boards the last choice was a pearl inside a pocket over a free tile in 4 of main's 9 and in none of the new build's 3, so opening the dead-end rule to all boards is not carded on this data.
- Team-mate counts are observational: mates are near her on crowded boards, where she is hunted more. They show no protection, not harm.
- The rebuild is my re-implementation (view, ghost lengths, rings, pockets), not the bot's log; which sprint or split path ran is inferred from the code. The ring was drawn 3 long for two 2-long heads at 1422316 (ghost parts). Two opponents, 15 layouts, the qualifier layouts unseen.
- Reproduce (about 2 minutes a label, one process each): `python3 data/analysis/ladder/dossier/work/q2_scan.py agg8-q1` (also `agg7-m1`, `agg7-m2`; it writes `q2_scan-LABEL.jsonl` itself), then `q2_deaths.py new detail`, `q2_before.py new`, `q2_cards.py new` (and `main`).
