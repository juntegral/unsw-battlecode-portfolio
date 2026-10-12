# Our queen is rammed with the queen-safety rule on: why the rule did not save her
Sample: 45 games of one bot (`agg7-m1` 30, `sr51-bob1` 15; `agg7-m2`/`m3` had not arrived), 7,564 queen turns, 27 queen deaths by head-on hit (19 + 8); 11 more by her own move (7 kelp, 2 own body, 1 other body, 1 as the mover), 7 alive at the end. **M** = measured (`work/qh_*.py` on the replays), **C** = read from `sr51-bot/main.cpp` (line), **E** = estimate. Every count below is M unless marked.
## 1. Three lines
1. **Why.** The rule held as written in all 27: no bug, and no constant ever turned it off. In 19 she had no clean tile left on her last turn (11 stepped on the pay tile as line 640 tells her and the enemy paid; 8 had only hit tiles and the rule fell back to "plain dragon", line 652); in 4 the rammer was not a head she could see (3 one column outside her 7 by 7, 1 a child split off after her turn); in 4 the ring was too small (3 rammers ate pearls on the way, 1 had its length cut by the view edge). She was 2 long in 19 of the 27 and 3 long in 6.
2. **Change.** (1) The queen keeps 3 after a routine split, so the paid two-step escape the rule already has (line 628) is open to her: in 10 of the 19 boxed deaths a clean tile was two steps away and she was too short to pay for it. (2) Among the tiles the veto leaves unpenalised she takes the one from which she can keep walking four turns ahead of the heads she sees: it changes a move in the last three turns of 7 deaths, 6 counted as prevented. Together 12 of 27 on paper.
3. **How sure.** Classes: high (each death rebuilt from the replay; `qh_list.py` prints the list). Fixes: paper only, nothing compiled or played; card 1's 10 is an upper bound (E), card 2's 6 covers the first changed move only (E); two opponents, 15 layouts.
## 2. Classes (exclusive; her last own turn before the hit)
| class | all | r0-100 | r101-300 | r>300 | cells <=700 | 701-1200 | >1200 |
|---|---:|---:|---:|---:|---:|---:|---:|
| no clean tile: stepped on the pay tile (line 640) | 11 | 8 | 3 | 0 | 5 | 3 | 3 |
| no clean tile: only hit tiles, rule off for that turn (`qs_plain`, line 652; C) | 8 | 2 | 6 | 0 | 3 | 3 | 2 |
| rammer outside her 7 by 7 (4 columns off; length 4, 5, 6; 3, 3, 6 steps) | 3 | 1 | 2 | 0 | 1 | 0 | 2 |
| rammer a child split off after her turn (queen 40 long, r474) | 1 | 0 | 0 | 1 | 0 | 1 | 0 |
| ring too small: the rammer walked 1 to 3 steps more than its length pays for (pearls eaten on the way) | 3 | 2 | 1 | 0 | 1 | 0 | 2 |
| ring too small: head on the view edge, 1 of 4 parts seen (reach drawn 2, true 3) | 1 | 1 | 0 | 0 | 0 | 0 | 1 |
| total | 27 | 14 | 12 | 1 | 10 | 7 | 10 |
- Empty classes (0 each): a ringed tile taken with a clean one open (the bug case), rule off by a constant, a split or no-move turn, a rammer through a portal, the enemy queen as rammer. What closed the box in the 19: kelp on two or more of her four sides 9, two or more enemy heads 5, a teammate's body or head on a side 4, one head in the open 1. A clean single step existed in 0 of the 19 and in all 8 others (she took it). A clean tile two steps away, in view and free, existed in 10 of the 19, all with her 2 long (2 long cannot pay); in none of the 4 where she was 3 long.
- Denominator: 386 of her turns began with an enemy head within 3 steps of her head (she survived such a turn in 28 games): 367 survived, 19 were followed by the hit that round; 8 hits came with no head within 3 steps. Of 85 runs of such turns 19 ended in the hit, 9 of them within two turns. Standing on a tile with kelp on 2+ sides: 8 hits in 38 such turns; one side 6 in 124; none 5 in 224. The rammer was a head she saw on her last turn in 23; 2 long in 8 (one free step), 3 long in 14 (10 walked one free and one paid step), longer in 5. When the tile she ended on was ringed and truly in reach, the ram was taken 18 of 18 times (pay tiles 10 of 10); on a tile drawn clean but truly in reach, 5 of 12.
- Rule on? Yes on every turn (C): `QUEEN_SAFETY` true (127); `queen_wary()` = `real_queen() && !qs_plain` (3757); `real_queen()` is the id alone (3748). `QUEEN_MIN_CELLS` 600 (161) only enters `is_queen()` (3356), which neither `map_hits()` (called at 1547) nor the veto (5318) uses; `QUEEN_SAFE_ROUND` 300 and `QUEEN_SAFE_SPAN` 0 (150-151) only move the feed round (528-533). Never ring sources: the enemy queen (3778), heads seen on earlier turns (3777 loops this turn's heads only), tails that can split.
## 3. Why, in the code (both no-clean-tile classes, 19 of 27, share two causes)
- **The escape ladder is empty at length 2 (C).** With no clean tile, lines 615-650 try a free sprint (618), a split (624), a paid sprint (628), a split (635), then the pay tile (640), a sprint to a pay tile (645), then "plain dragon" (652). `hit_escape()` walks at most `sprint_free()` or `sprint_reach()` steps (3837) and accepts only tiles two or more steps away (3871); both are 1 at length 2 (3673-3682), and a split needs 4. So a 2-long queen goes straight to 640 or 652. She is 2 long because the routine split (`split_child_size()`, 1026-1077, taken at 754) cuts 2 off at length 4; the only queen guard (1030-1033) sits behind `is_queen()` with `QUEEN_KEEP` 0 (142). M: 88 of her 95 routine splits left her 2 (24 of them in round 1); she was 2 long on 2,898 of 6,395 turns in rounds 0-300. Boxed turns (no clean tile, a ring on a tile): at 2 long 15 of 20 ended in the hit, at 3+ long 4 of 13 (4 paid a segment).
- **The veto is one turn deep (C).** `map_hits()` stops at the head's reach (3804) and `pick_direction()` penalises only ringed tiles (5335-5340), so the tile one step outside a ring scores like any other and she walks to the ring's edge. M: 75 of her steps with a head in view ended where a seen head could stand on its next turn but one; 13 of those were among her last three turns (17%), against 14 of 192 one turn further out and 13 of 1,929 beyond.
- Pay tile, game 1360291 (32 by 16): r98 queen head (20,0), 2 long; head #24, 3 long, at (17,14), five steps off. N, E, W all clean; she steps W to (19,0). r99: #24 at (17,15); N (19,15) and W (18,0) are pay tiles, S (19,1) is clean but a closed pocket, E is her body. Line 640: N. #24 walks E, E (one paid) into her. Card 2 takes E at r98; 3 long she could have paid at r99. Only hit tiles, game 1397920 (24 by 12): r155 queen (5,5), 2 long; head #27, 2 long, at (3,3). N (5,4) and E (6,5) clean; she steps N. r156: #27 at (4,3); N (5,3) and W (4,4) are hit tiles, E (6,4) is a teammate's body. Line 652: W. #27 steps S into her. Herded, game 1398177 (64 by 64), r222-227: head #19, 3 long, holds three steps off for six rounds; each turn she has exactly one clean tile; at r226 it is (42,5) with kelp S and W; at r227 only the pay tile (42,4) is left; #19 walks W, W. Neither card changes a move here.
## 4. The cards
title: Queen keeps three: no routine split below five, paid escape before the split
slug: queen-keep-three
### Claim
A 2-long queen has no escape when every tile next to her is ringed; kept at 3 or more she can pay one segment for the clean tile two steps away, which `hit_escape(path, true, 0)` already looks for. Default off (`QS_KEEP_LEN = 0`; on: 3).
### Evidence
M: 10 of the 19 boxed deaths had a clean tile two steps away, seen and free, with her 2 long (1397917, 1397920, 1397921, 1397923, 1398183, 1398187, 1360287, 1360291, 1360294, 1360296). E (`qh_len.py`: same pearls and paid steps, routine split only from 5): she is 4 long on all ten turns, and 2 long on 136 instead of 2,898 turns of rounds 0-300. Cost on paper: 39 of 95 routine splits not made (0.9 fewer queen children a game, the round-1 split in 24 games); a boxed turn at 3+ costs a segment (13 such turns in the sample, 9 survived).
### Expected signal
In replays (`qh_scan.py`, `qh_len.py` with the new label added): routine splits leaving her 2: 88 to 0; her turns at length 2 in rounds 0-300: 45% to under 10%; boxed turns answered with a paid sprint. E: 3 to 10 fewer head-on-hit queen deaths per 45 games (27 now).
### What would show it's wrong
Boxed turns at 3+ long still end in the hit at the 2-long rate (15 of 20); own dragons alive at round 100 down by more than 1; queen deaths by her own move (11 in 45 games) up.

title: Queen looks four turns ahead of the heads she sees
slug: queen-look-ahead
### Claim
Among tiles the ring veto leaves unpenalised she prefers the one from which she can keep walking, one tile a turn, for four enemy turns before a seen head can stand there; ties go to the tile a seen head needs longer to reach. Default off (`QS_AHEAD = 0`; on: 4).
### Evidence
M (`qh_card.py`, the rule replayed on all 7,426 of her moves): it would move her on 48; 10 of those fall in the last eight turns of 8 deaths, in the last three turns of 7. Counted as prevented when the new tile is open, out of true reach that round and has a look-ahead longer than the turns she had left: 6 (1397916, 1397920, 1397930, 1398187, 1360287, 1360291). Cost: 38 changed moves on other turns (11 with a head within 3 steps), 2 of her 236 pearl steps given up.
### Expected signal
`qh_card.py` on new replays: steps onto a tile with a shorter look-ahead than another unpenalised tile: 48 per 45 games to 0; steps ending one enemy turn outside a ring (75) down; runs with a head within 3 steps that end in the hit below 19 of 85.
### What would show it's wrong
The count does not go to 0 (the term is outvoted); the share of runs ending in the hit is not down; her pearl steps per game (5.2) fall by more than 1; deaths by her own move rise.
### Diff for both cards against `data/online/smoke/sr51-bot/main.cpp` (not compiled; hunk numbers are that file's lines)
```diff
@@ 132 @@ after constexpr int QS_ESCAPE_EVALS = 6;
+constexpr int QS_KEEP_LEN = 0;  // card queen-keep-three: 3
+constexpr int QS_AHEAD = 0;     // card queen-look-ahead: 4
+constexpr double QS_AHEAD_PENALTY = 1e6;
@@ 624 @@ act(): with the card on, the paid escape comes before the split that would leave her 2
-            if (!exposed && ct.can_split(keep)) {
+            if (!exposed && ct.can_split(keep) && !(QS_KEEP_LEN > 0 && hit_escape(path, true, 0))) {
@@ 1042 @@ split_child_size(): after the (hit_head || pay_head) guard
+        if (QS_KEEP_LEN > 0 && real_queen() && length - unswbc::Constants::MIN_SIZE < QS_KEEP_LEN) {
+            return 0;
+        }
@@ 3770 @@ map_hits(): after pay_stamp.assign(cells, 0);
+            soon_stamp.assign(cells, 0);
+            soon_turn.assign(cells, 0);
@@ 3804-3820 @@ the walk goes on past the reach; turns = enemy turns until this head can stand on the tile
-                if (steps >= reach) {
+                if (steps >= reach + std::min(8, QS_AHEAD * free)) {
-                    if (next == index_of(head)) {
+                    if (next == index_of(head) && steps < reach) {
-                    pay_stamp[next] = hit_mark;
+                    if (steps < reach) {
+                        pay_stamp[next] = hit_mark;
+                    }
+                    int const turns = steps < reach ? 1 : 2 + (steps - reach) / free;
+                    soon_turn[next] = soon_stamp[next] == hit_mark ? std::min(soon_turn[next], turns) : turns;
+                    soon_stamp[next] = hit_mark;
@@ 3833 @@ after risk_at()
+    int soon_at(int index) const {
+        return !QUEEN_SAFETY || qs_plain || hit_round != round || soon_stamp[index] != hit_mark ? 99 : soon_turn[index];
+    }
+    // Turns she can keep walking from cell, one tile a turn, before a seen head can stand there first.
+    int qs_ahead(int cell, int from, int turn) const {
+        bool const safe = soon_at(cell) > turn;
+        int best = safe ? turn : turn - 1;
+        for (Direction const direction : Direction::get_direction_list()) {
+            std::uint8_t const edge = edge_at(position_of(cell), direction);
+            int const next = index_of(position_of(cell).add_dir(direction));
+            if (safe && turn < QS_AHEAD && edge != EDGE_KELP && edge != EDGE_PORTAL && next != from && enter_time[next] <= turn + 1) {
+                best = std::max(best, qs_ahead(next, cell, turn + 1));
+            }
+        }
+        return best;
+    }
@@ 5342 @@ pick_direction(): before hit_blocked = risky && !open[0];
+            int best_ahead = 0;  // second pass: each tile pays for what it lacks against the best one
+            for (std::size_t pass = 0; QS_AHEAD > 0 && pass < 2; pass++) {
+                for (std::size_t k = 0; k < directions.size(); k++) {
+                    if (scored[k] && dests[k] >= 0 && edge_at(head, directions[k]) != EDGE_PORTAL) {
+                        int const ahead = 3 * qs_ahead(dests[k], index_of(head), 1) + std::min(soon_at(dests[k]), 3);
+                        best_ahead = std::max(best_ahead, ahead);
+                        scores[k] -= pass == 1 ? QS_AHEAD_PENALTY * (best_ahead - ahead) : 0.0;
+                    }
+                }
+            }
@@ 5650 @@ after std::vector<int> pay_stamp;
+    std::vector<int> soon_stamp;
+    std::vector<int> soon_turn;
```
## 5. Against it
- 15 of the 27 are untouched by both cards: the herded ones (one clean tile a turn, as in 1398177), the 4 unseen rammers and the 3 pearl cases. Widening the ring (pearls cost no reach, a cut head counts as 4 long) was replayed too: it changes the last move in 1 death (1397930, which card 2 also catches) and takes the clean tile away on 16 survived turns, so it is not carded. Standing with kelp on 2+ sides while hunted is ten times as deadly (8 in 38 against 5 in 224), but preferring open tiles while a head is in view changes a move in the last three turns of only 3 deaths for 98 changed moves elsewhere; not carded either.
- Both counts are paper: a changed move or an open escape, not what follows. 5 of her 10 paid sprints in the sample were followed by the hit within ten turns, and these opponents took every ram she offered on a ringed tile (18 of 18), so line 640's premise fails against them and an escape buys turns, not safety.
- Card 1 trades children for length: 0.9 fewer queen splits a game and one dragon fewer from round 1 on 24 of 45 starts. It needs room two steps away, which 6 of the 9 kelp-pocket deaths did not have. Card 2 treats unknown edges as open, sees no head outside the 7 by 7 and no child off a tail, and may push her off pearls or into a teammate's way; its measured cost is 38 changed moves against two opponents.
- The rebuild is a re-implementation of her view, the ghost lengths and the rings, not the bot's own log; `qs_plain` and which split path ran are inferred from the code. 45 games, 15 layouts, two opponents; the qualifier layouts are unseen. Reproduce: `python3 data/analysis/ladder/dossier/work/qh_scan.py` (about 2 minutes, one process), then `qh_class.py runup`, `qh_list.py`, `qh_more.py`, `qh_rules.py`, `qh_card.py`, `qh_len.py`; one death on a map: `qh_view.py <game> [turns back] [radius]`.
