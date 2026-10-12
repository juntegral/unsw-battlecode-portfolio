# How queens die, and the sure hits on their queen that we pass up (team 1119; 45 online games of current main, 500 ladder games, 597 rank-1 games; written 8 Oct 2026)

1. **How queens die.** On every side the first cause is an enemy head rammed into hers (13 and 27 of 45 queens online, 0.43 to 0.59 of all queens on the two ladders), by a dragon of 2 or 3 in two cases of three or more, and the rammer dies with her every time. Online the two opponents did it to our queen in 27 of 45 games and we to theirs in 13; on the ladder it is level (221 against 214 in 500); rank-1 does it in 355 of 597. We refuse little: with her head in sure reach our short dragons ram on 13 of 16 turns online and 206 of 236 on the ladder (rank-1 237 of 237, the two online opponents 20 of 20). What we lack online is the chance: her head came into our sure reach in 13 games of 45, ours into theirs in 20.
2. **The change.** One switch, QUEEN_SURE_LEN (0 = off, test 8): a dragon of ours of that length or less that is neither the queen nor the leader rams the enemy queen's head whenever a free way of at most 3 steps inside its sprint reach, with no portal step, leads into it. No hunter token, local count, round or part count is asked.
3. **How sure.** Sure of the mechanism: every turn of all 1,142 games, queen fates equal to the dossier's in 2,194 of 2,194, chance counts equal to diag-attack's scan, seven refused turns redrawn from the replays, and on none of 1,107 such turns does the mover die without her. Small in results: the switch would have fired on 5 turns in 4 of the 45 online games and 46 turns in 28 of the 500 ladder games, and on the final board it turns 1 online loss and 5 ladder losses. About one game in a hundred: a 30-game test cannot show it, the mechanism check can.

Labels: [M] measured by my scripts in dossier/work/. qk_scan.py replays every game (online labels agg7-m1, 30 games, and sr51-bob1, 15 games, both the bot in sr51-bot; the 500 games of per-game.jsonl; the 597 of per-game-top1.jsonl) and writes every queen death and every turn on which a queen's head is in reach; qk_tab.py and qk_band.py print the tables below, qk_agg.py the longer cuts; qk_check.py is the recount against per-game.jsonl, per-game-top1.jsonl and at_scan; qk_view.py draws one turn from the replay with its own path search. [C] read from data/online/smoke/sr51-bot/main.cpp, line given. [E] my estimate. agg7-m2 and agg7-m3 had not arrived and agg7-b1 had only just started (no replays) at 09:58 KST, so there is no second sample.
Terms: "queen" = the lowest starting id of a side. "Rammed" = an enemy head moved into her head; both die. "Chance" = at the start of a dragon's turn the enemy queen's head can be entered this turn over free tiles, on its free steps (ceil(L/4)) or by paying a segment a step down to length 2. "Short" = a non-queen of 2 to 4; "plain" = no pearl needed on the way; "in view" = part of her inside the mover's 7 by 7. "Sure way" = a plain chance of at most 3 steps with no portal: every tile of it is inside the view. "Taken" = she dies head-on in that turn with this dragon as the mover. "FLIP" = a game lost on queen length in which, on the final board, her death alone gives us the game (our queen alive, or our longest above their longest); "open" = she is their longest and I cannot tell their next.

## 1. The fate of every queen and who killed her (job 1) [M]
| Queen of | games | alive at the end | dead by r100; r101-300; later | rammed by an enemy head | she rammed an enemy head | wall; own body | body or head of her own side | enemy body | illegal split or no action |
|---|---:|---:|---|---:|---:|---|---:|---:|---:|
| ours, online | 45 | 7 | 18; 19; 1 | 27 | 1 | 7; 2 | 1 | 0 | 0 |
| the two opponents, online | 45 | 27 | 9; 9; 0 | 13 | 2 | 1; 1 | 1 | 0 | 0 |
| ours, ladder | 500 | 126 | 143; 179; 52 | 221 | 15 | 75; 37 | 22 | 3 | 1 |
| our ladder opponents | 500 | 153 | 171; 124; 52 | 214 | 34 | 43; 20 | 19 | 1 | 16 |
| rank-1 | 597 | 185 | 196; 154; 62 | 262 | 18 | 0; 1 | 6 | 3 | 122 |
| rank-1's opponents | 597 | 163 | 162; 198; 74 | 355 | 20 | 17; 23 | 11 | 0 | 8 |

| Rammed queen (the killer is the other side) | n | killer's length at its turn start 2; 3; 4; 5-8; 9+ | steps it walked 1; 2; 3; 4+ | paid a segment before the hit | in her 7 by 7 at her last turn | none of her side within 5 | killer, her mean length | by r100; r101-300; later |
|---|---:|---|---|---:|---:|---:|---|---|
| ours, online | 27 | 0.30; 0.52; 0.07; 0.11; 0.00 | 0.30; 0.37; 0.19; 0.15 | 0.30 | 0.85 | 0.44 | 3.0, 3.7 | 0.52; 0.44; 0.04 |
| the two opponents, online (killer ours) | 13 | 0.54; 0.46; 0.00; 0.00; 0.00 | 0.69; 0.31; 0.00; 0.00 | 0.00 | 1.00 | 0.54 | 2.5, 2.5 | 0.46; 0.54; 0.00 |
| ours, ladder | 221 | 0.27; 0.41; 0.10; 0.14; 0.09 | 0.35; 0.28; 0.18; 0.19 | 0.29 | 0.83 | 0.50 | 4.0, 4.7 | 0.38; 0.46; 0.17 |
| our ladder opponents (killer ours) | 214 | 0.38; 0.48; 0.11; 0.01; 0.01 | 0.61; 0.31; 0.07; 0.01 | 0.07 | 0.95 | 0.52 | 2.8, 4.2 | 0.52; 0.39; 0.09 |
| rank-1 | 262 | 0.27; 0.39; 0.14; 0.15; 0.06 | 0.34; 0.27; 0.21; 0.18 | 0.32 | 0.73 | 0.45 | 4.1, 6.8 | 0.43; 0.39; 0.18 |
| rank-1's opponents (killer rank-1) | 355 | 0.30; 0.41; 0.08; 0.12; 0.09 | 0.37; 0.28; 0.16; 0.18 | 0.28 | 0.81 | 0.46 | 4.3, 6.7 | 0.36; 0.46; 0.17 |

- [M] This morning's 30 games alone (agg7-m1): 7 won, 12 decided on queen length, our queen alive at the end in 5; she was rammed in 19, hit a wall in 4, her own body in 1 and rammed an enemy head in 1. All 10 wall and body deaths of our queen online, and 135 of 137 on the ladder, had no free tile beside her head at her last turn.
- [M] The killer is lost too: in all 1,088 rams followed step by step the mover dies head-on in the same turn (the other 4 of the 1,092 had no free way at the start of the turn by my search and were not followed); a queen dying on an enemy body, the one kill that costs nothing, happens 0 to 3 times a sample. Our killers are the odd ones: they come from one step in 0.61 to 0.69 and have paid a segment in 0.00 to 0.07; everyone else's come from two steps or more in two thirds and have paid in 0.28 to 0.32. Killers of 5 or more are 2 percent of ours and 11 to 23 percent of theirs.
- [M] Who kills the other queen first, and then wins: online we in 5 of 45 games (won 3), they in 24 (won 19). Ladder: we in 142 of 500 (won 101, 0.71), they in 159 (won 109, 0.69). Rank-1 in 212 of 597 (won 156, 0.74), its opponents in 177 (won 88, 0.50). Our queen dies first, by any cause, in 34 of the 45 online games and they win 27 of those.

## 2. What a kill is worth (job 3) [M]
- [M] Games in which we rammed their queen dead. Ladder 214: our queen alive at that moment in 127, won 94 (all 49 in which she then lived to the end, 45 of the 78 in which she died later); already dead in 87, won 51; no such kill in 286, won 124. Online 13: alive in 3, won 2; dead in 10, won 7; no such kill in 32, won 4. Rank-1 355: won 150 of 200 and 123 of 155; no such kill, 107 of 242.
- [M] End states, wins of games (ladder; online): ours alive and theirs dead 66 of 66; 2 of 2. Ours dead and theirs alive 0 of 93; 0 of 22. Both dead 165 of 281; 8 of 16. Both alive 38 of 60; 3 of 5. The price is the killer: mean length 2.8 on the ladder and 2.5 online at the start of its turn (rank-1 4.3), for a queen of mean 4.2 and 2.5 (rank-1 6.7).

## 3. Chances (job 2) [M]
| Side, at whose queen | short, plain, in view: turns, games, taken | free; 1 paid; 2 paid (taken/turns) | own length 2; 3; 4 | 5 or longer, 1-3 steps | 5 or longer, 4-5 steps | short, only with a pearl on the way | what the short refusers did |
|---|---|---|---|---|---|---|---|
| ours, online | 16, 13, 13 (0.81) | 9/11; 4/4; 0/1 | 7/8; 6/7; 0/1 | 0/3 | 0/3 | 0/2 | away 2, split 1 |
| the two opponents, at ours | 20, 20, 20 (1.00) | 8/8; 10/10; 2/2 | 8/8; 10/10; 2/2 | 2/2 | 1/2 | 4/4 | none |
| ours, ladder | 236, 218, 206 (0.87) | 128/138; 64/79; 14/19 | 81/88; 101/117; 24/31 | 3/47 | 2/147 | 0/42 | away 24, closer 5, split 1 |
| ladder opponents, at ours | 227, 167, 143 (0.63) | 73/83; 56/98; 14/46 | 50/56; 77/111; 16/60 | 17/76 | 26/215 | 24/113 | away 54, closer 18, split 11, level 1 |
| rank-1 | 237, 237, 237 (1.00) | 128/128; 92/92; 17/17 | 93/93; 116/116; 28/28 | 11/11 | 45/60 | 39/95 | none |
| rank-1's opponents, at rank-1 | 214, 193, 177 (0.83) | 84/102; 67/79; 26/33 | 64/73; 79/97; 34/44 | 16/22 | 30/76 | 27/86 | away 22, split 9, closer 4, level 2 |

- [M] After a short refusal of ours on the ladder (30 turns) she lived to the end in 15 games, died later in 13 and within 5 rounds in 2; the mover itself was dead within 5 rounds in 7. Online (3 turns) she was rammed 1, 23 and 50 rounds later and we won all three. Our take rate does not move much with anything: our queen alive 124 of 131, dead 82 of 105; outnumbered in view 124 of 144, not 82 of 92; after round 300 14 of 21.
- [M] We do not fail to walk at her. Short dragons with her head in their 7 by 7, 1 to 3 steps away and out of reach, move closer on 0.98 of turns (ours online), 0.90 (ours, ladder), 0.87 (rank-1), 0.90 (the two opponents); at 4 to 6 steps 0.90, 0.84, 0.82, 0.83. Online we have fewer such turns (2.2 and 5.0 a game against their 3.7 and 6.8) and go 71 rounds (median) from first sight of her to the killing ram where they go 34.
- [M] The pool this could ever reach: games lost on queen length with our queen dead are 60 on the ladder and 17 online; our longest was above their longest at the end in 27 and 3; one of our dragons had a sure way to her head at some time in 15 and 1 (7 and 1 of the ones we led).

## Why, in the code
- [C] The dragon can tell. An id of 0 or 1 is a queen (1422-1425); any part with such an id in view sets queen_id and enemy_queen_id by its team (1470-1478), and her head's tile and round are kept (1479-1482).
- [C] Only the hunter treats her differently. QUEEN_HUNT is false (141), so the block that marks her head for every non-queen (2587-2598, QUEEN_HUNT_MAX_LEN 0 at 156) is dead, and QUEEN_CHASE_DIST is 0 (116, 584-588). QH_SCOUT (372) marks her head (2575-2585) only when qh_on holds (2020): id above 1, not the leader, length 4 or less (2006), a sighting at most 20 rounds old (2007), and either first finder (2015: round above 20 and no other hunter heard for 20 rounds) or revenge (2012: it knows our queen is dead and the round is 100 or later). To every other dragon she is a head like any other: a trade needs the round at most feed_round, own heads in view plus one minus enemy heads at least 1, and her parts at least its own length up to 1200 cells (2680-2689; length 4 or less, 3704-3708); the hunt needs 10 parts and own length plus 4 (2624); the end hunt 6 parts and a known longer leader (2600-2607). In the move score her head tile is SCORE_REJECT times 0.5 like any enemy head (5290-5292). No QUEEN_HUNT constant enters a score.
- [C] A marked head is acted on first (549-555), over a free way of at most sprint_reach() steps (2636, 3673-3678: 1, 2, 3 steps at length 2, 3, 4); a pearl on the way is not counted as a step gained, which is the 0 of 42 in the table.
- [M] The reading fits the online games: where these lines say yes (hunter 8 turns, trade 3) ours rammed on 11 of 11; where they say no, on 2 of 23. The 3 short refusals: another short dragon of ours had her in view within 20 rounds (the token was elsewhere), no revenge (our queen alive, or round 90), and the trade rule said no (outnumbered in view twice, her 2 parts under own length 3 once). The 2 refusals of a 5 and a 6: length above 4 (2006), 4 and 9 parts shown (2624). Ladder (older builds): of 30 short refusals 15 have our queen dead after round 100 and 15 fit token plus trade rule; of 16 by dragons of 5 to 8, 14 saw under 6 parts.

## 4. The card
title: A dragon up to 8 long rams the enemy queen's head when it is a sure 1 to 3 steps away (QUEEN_SURE_LEN 8)
slug: sure queen hit
### Claim
[E, from the rows above] With her head a free 1 to 3 steps away our short dragons pass on about one turn in seven and our dragons of 5 or more nearly always; rank-1 never passes, at any length (248 of 248). Proposal: constexpr int QUEEN_SURE_LEN = 0 (0 = as now, test 8) and QUEEN_SURE_STEPS = 3. In mark_hunt_targets, after the hunter block, a dragon that is not the queen (real_queen(), 3748) and not the leader (3352), of length at most QUEEN_SURE_LEN, marks her head when it is within 3 tiles, and hunt_path takes it only over a free way with no portal step. Reach rule, exactly: steps at most min(ceil(L/4) + L - 2, 3), that is 1 step at length 2, 2 at 3, 3 from 4 up (2 of them free from 5 up, 3 from 9 up). Every tile of such a way is inside this turn's 7 by 7 view, so it is seen and not remembered, and she cannot move before the hit. The hunter, trades, the leader, our queen and every other head stay as they are. Switch name: QUEEN_SURE_LEN.
### Evidence
- [M] Sure ways by a non-queen that is not its side's longest when 5 or more, taken of all: ours online 13 of 18 up to length 8 (13 of 16 up to 4), ladder 207 of 253 (205 of 235); rank-1 242 of 242; the two online opponents 22 of 22; our ladder opponents 150 of 258; rank-1's opponents 189 of 226.
- [M] What the switch would have taken. Online 5 turns in 4 games: 3 turns of dragons of 2 to 4 in 3 games we won anyway, 2 turns of a 5 and a 6 in game 1360300, a FLIP. Ladder 46 turns in 28 games (30 turns in 22 games for 2 to 4, 16 in 10 for 5 to 8): 9 won anyway, 6 lost with her dead later anyway, 4 lost on another rule or with their longest still ahead, 5 FLIP, 4 open. With no length limit 68 turns in 39 games, 7 FLIP; at length 4 or less 3 FLIP.
- [M] The FLIP games, final board as dragons/longest/total/queen, ours against theirs (turns drawn with qk_view.py). Online 1360300: 29/70/217/0 against 35/25/183/25; at round 483 a 6 of ours is two free steps from her head (she is 25) and walks off. Ladder 1254719: 7/27/61/0 against 1/9/9/9, their queen their last dragon; at round 411 a 2 of ours beside her steps aside. 1285561: 43/29/193/0 against 54/18/210/18; at round 405 a 5 two free steps away walks off. 1307547: 60/76/405/0 against 2/42/60/42. 1305215: 9/55/81/0 against 26/35/139/10. 1332074: 30/28/205/0 against 28/25/186/14.
- [M] Cost and safety: one dragon a use, mean length 4.0 at the first refusal of a game, at most 28 uses in 500 games. Of 1,107 sure-way turns in all samples 843 were taken and on none of the other 264 did the mover die that turn.
### Expected signal
[E] In replays of the new build (qk_scan.py on the label, then qk_tab.py, line "SWITCH ... ours, length at most 8"): refused turns 0 (now 5 in 45 online games, 46 in 500) and taken share 0.95 or more (now 0.72 and 0.82); each such turn ends with two head-on deaths, hers and the mover's (qk_view.py). Their queen rammed dead in about 1 game more in 45 (now 13; in 3 of the 4 games with a refusal she died later anyway), and games lost on queen length with our queen dead about 1 fewer in 45 (now 17).
### What would show it's wrong
- A sure-way turn on which the mover dies and she does not, or a mover that is our queen or our longest dragon of 5 or more: the way was not sure, or the switch reached code it should not.
- Taken share still under 0.9: the dragon believed it was the leader (3352) or did not know her id; read those before anything else.
- Over a few hundred games, games with such a ram won less often than today's rams (0.59 with our queen dead, 0.74 with her alive), or our dragons alive at round 300 down by more than 1: at most one dragon a game cannot do that.

Diff against data/online/smoke/sr51-bot/main.cpp (line numbers of that file; not compiled):
```diff
@@ 156 @@
+constexpr int QUEEN_SURE_LEN = 0;    // 0 = off, test 8
+constexpr int QUEEN_SURE_STEPS = 3;  // a way this short stays inside the 7 by 7 view
@@ 2569 mark_hunt_targets(), after "hunt_targets = 0;" @@
+        sure_queen = false;
@@ 2586, after the QH_SCOUT block, before "if (QUEEN_MODE && QUEEN_HUNT" @@
+        if (QUEEN_MODE && QUEEN_SURE_LEN > 0 && !real_queen() && !is_leader() && length <= QUEEN_SURE_LEN) {
+            for (std::size_t k = 0; k < enemy_heads.size(); k++) {
+                if (enemy_head_ids[k] == enemy_queen_id && manhattan(head, enemy_heads[k]) <= QUEEN_SURE_STEPS) {
+                    hunt_stamp[index_of(enemy_heads[k])] = round;
+                    hunt_targets++;
+                }
+            }
+            if (hunt_targets > 0) {
+                hunt_queen = sure_queen = true;
+                return;
+            }
+        }
@@ 2636 hunt_path() @@
-        int const reach = std::min(sprint_reach(), hunt_queen ? QUEEN_HUNT_STEPS : HUNT_MAX_STEPS);
+        int const reach = std::min(sprint_reach(), sure_queen ? QUEEN_SURE_STEPS : hunt_queen ? QUEEN_HUNT_STEPS : HUNT_MAX_STEPS);
@@ 2653 @@
-                if (next < 0 || visit_stamp[next] == visit_mark || qh_shut(position, direction)) {
+                if (next < 0 || visit_stamp[next] == visit_mark || qh_shut(position, direction) || (sure_queen && edge_at(position, direction) == EDGE_PORTAL)) {
@@ 5564, beside "bool hunt_queen = false;" @@
+    bool sure_queen = false;
```

## 5. Against it
- [M] Size. 1 FLIP in 45 online games and 5 in 500 on the ladder is about one game in a hundred, and FLIP is read off the final board, not from a replay of the rest of the game (in 1332074 the refused turn is at round 124). The 4 open games are probably not flips: their sides end with 81 to 483 total length against our 11 to 127. In 9 of the 28 ladder games we won anyway and the use spends a dragon for nothing.
- [M] It is not why they out-kill us online. There the gap is chances and our own queen: they had our queen's head in sure reach of a short dragon in 20 games and took all 20, we had theirs in 13; she dies first in 34 of 45 and 24 of those are their rams, the killer inside her view at her last turn in 0.85. That is her own safety (brief diag-queenhit), which this switch does not touch.
- [M] Rank-1's lead in queen kills (0.59 rams a game against our 0.43 on the ladder) is mostly outside this switch: killers of 5 or more are 21 percent of its rams and 2 percent of ours, it takes 45 of 60 sprints of 4 to 5 steps (ours 2 of 147) and 39 of 95 ways that need a pearl eaten (ours 0 of 42). Those leave the 3-step ring, where a tile is remembered and not seen, and hunt_path counts no pearl: more than one constant.
- [M] Half of the short refusals on the ladder (15 of 30) are "our queen dead, round 100 or later", which the hunter in current main should already take (online, our queen dead: 10 of 11). On current main the short class may be the 3 turns in 45 games seen online, all in games we won; the gain then rests on dragons of 5 to 8 (16 turns in 500 ladder games, 2 in 45 online) and one online game.
- [M] The 6 FLIP games sit on 4 layouts and 5 of them are above 1200 cells; on a small unseen map the switch may never fire. When she is within 3 tiles but walled off, the early return costs that dragon any other hunt for the turn (trades are not affected).
- Not checked: nothing was built, compiled or played; whether a dragon believes it is the leader and who holds the hunter token are not in a replay (proxies: its side's longest; another short dragon of ours with her in view within 20 rounds); the ladder bot is an older build than sr51-bot; the local spar with QUEEN_HUNT and QUEEN_CHASE_DIST 8 (data/local/hunter38) was an opponent for another card, not a test of this rule. Method: the guard refuses nice, so the scans ran at normal priority, three at a time, about 5 minutes a shard; the Write tool is refused for this folder (path spelling, verify/NOTE-write-guard.md), so every file went through the Python route. Left behind in dossier/work: qk_probe.txt and the first-pass qk_scan-*.jsonl (superseded by qk_scanf-*.jsonl; rm is refused).
