# Reports sent to the lead by weak13-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 01:15:59 — Early heads-up: portal ban starves one12/one13

Early heads-up from weak13-opus (full report follows): PORTAL_SCOUT_MIN_LEN 4, live since one12, has in practice stopped our short dragons using portals at all, and that starved us in 2 of the 4 Quaker Qubits losses (Trauma 1513120, Queen Of Spades 1513119).
[M] Portal crossings in r0-99 by our non-queens shorter than 4, online 15-game sets, maps that have portals: one8-11 mean 32.5 per game, 0 of 120 games with zero; one12-13 mean 4.1 per game, 48 of 108 games with zero. Trauma: 6.4-11.7 per game before, 0.0 in all 11 games of one12+one13.
[M] Our pearls eaten r0-99, one11 -> one12 -> one13: Trauma 40.3 -> 7.7 -> 5.0; Portals 235 -> 74 -> 71; Queen Of Spades 59 -> 10.7 -> 22; Australia 90 -> 48 -> 33; Default 57.7 -> 22 -> 30. Maps without portals or with short-hop portals (Devil, weakhold, Tower Defense, Maze, Stripes, Slithery Fight) did not move.
[M] Game 1513120 Trauma: #3 (L2) circles (37,22)-(37,23)-(38,23)-(38,22) and #5 (L3) circles (37,3)-(37,4)-(38,4)-(38,3) from about r15 onward, each loop touching the tile with the portal edge and being turned away; we ate 1 pearl in r0-49 with 12-14 pearls lying nearer to us than to them. Boards: data/codex/astra/weak13-opus/look-1513120-d3.txt.
[C] one13-bot/main.cpp 727-770 guard_portal_scout: a non-queen under 4 whose chosen step crosses a portal with a never-seen far tile (seen_round[next] < 0, line 736) is redirected whenever any ordinary neighbour with one free onward tile exists (portal_scout_open, 695-716). On open ground that is always true, and since nobody crosses, the far side never becomes seen. The queen is barred too (QUEEN_NO_PORTAL), and non-queens split at 4, so the whole side stays in its portal-free home area.
Candidate constant: PORTAL_SCOUT_MIN_LEN:0 (back to one11 behaviour for this one switch; the other four one12 switches untouched). Not tested by me (no games allowed). Caveats: the "affected maps" win split (one8-11 33 of 66, one12-13 16 of 54) is chosen after the fact and opponents differ between the version groups; I have not measured what the guard saved in blind-portal deaths.
Tables: data/codex/astra/weak13-opus/early.txt, portal.txt, wins.txt. Continuing with the other four lost games.

---

## 2026-10-09 01:27:08 — Final report: one13 losses to weaker teams

weak13-opus report: PORTAL_SCOUT_MIN_LEN 4 (live since one12) keeps our whole side out of portals; it starved us in 2 of the 4 Quaker Qubits losses. The other 4 lost games are the known open weaknesses.
BUG: yes, one. The rule fires far wider than written. CONST candidate PORTAL_SCOUT_MIN_LEN:0 (compiles; not played by me).
How sure: mechanism high (code + boards + 228 games counted). That 0 wins more: untested.

All 10 games of both battles were played by bot 21377 (one13); the 4-1 battle b1483679 by 21126 (one8). Ledgers every 25 rounds: ledger.txt. Queen boards (last 3 turns, 7 by 7): queen-boards.txt. Folder: ~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/weak13-opus/

THE BUG
[C] one13-bot/main.cpp 727-770 guard_portal_scout: a non-queen under 4 whose step crosses a portal with a never-seen far tile (line 736) is turned to the best ordinary step whenever any neighbour with one free onward tile exists (portal_scout_open 695-716). On open ground that always holds, and as nobody crosses, the far tile is never seen. The queen is barred as before (QUEEN_NO_PORTAL) and non-queens split at 4.
[M] Portal crossings r0-99 by our non-queens under 4, 15-game sets, maps with portals: one8-11 32.5 per game, zero in 0 of 120 games; one12-13 4.1 per game, zero in 48 of 108. Trauma 6.4-11.7 before, 0 in 11 of 11 games since.
[M] Our pearls r0-99, one11 -> one12 -> one13: Trauma 40.3 -> 7.7 -> 5.0; Portals 235 -> 74 -> 71; Queen Of Spades 59 -> 10.7 -> 22; Australia 90 -> 48 -> 33; Default 57.7 -> 22 -> 30. No-portal and short-hop maps (Devil, weakhold, Tower Defense, Maze, Stripes) did not move.
[M] Trauma under one12/13: 2 wins of 12 (sets 1 of 9, ranked 1 of 2, new q1 set 0 of 1); one8-11: 5 of 11.
[M] New set one13-q1 (7 of 15): zero turn starts outside the home area in r0-199 on Trauma (lost), Australia (lost), Schooltime (won); Default zero in r0-99 (lost).
Not checked: how many blind-portal deaths the guard saved; a local head-to-head of one13 against the copy with 0; the portal share of the local maps behind one12's 40-3-29.

LOST GAMES
1513120 Trauma v QQ: wiped out r353 (0 v 51 dragons, total 151, their queen 13). Out-eaten from r25 (r100 total 11 v 18, r200 20 v 89). [M] 0 of 916 turn starts outside our 264-tile home in r0-199; 12 of 184 natural spawns fell there; we ate 12, they 166. #3 (L2) circles (37,22)-(37,23)-(38,23)-(38,22) and #5 (L3) (37,3)-(37,4)-(38,4)-(38,3), each loop touching the portal tile (look-1513120-d3.txt). Queen #1 was our last dragon at L17, rammed r353 by #209 L7 from (44,10), 5 steps (2 free, 2 paid), no pearls, outside her view at her turn start; their queen alive. Cause: the bug.
1513119 Queen Of Spades v QQ: wiped out r264 (0 v 23 dragons, their queen 7); behind for good r47. [M] r0-49 we ate 2, they 26; 0 of 348 turn starts outside home in r0-99, 1 portal crossing. Queen #0 L4 ate 1 pearl in 74 rounds, never split; r74 she stepped E to (20,29), two tiles from visible #28 L3 at (20,31), which hit with 1 free + 1 paid step; W was open (why she chose E: not determined). Cause: the bug. Same map under one8 (1483680, won, wiped them out r308): 177 of 551 turn starts outside home, 22 crossings, 49 pearls r0-99 against 18.
1513121 Stripes v QQ: wiped out r409, both queens dead. Theirs died r98 (own body). Ours L2, rammed r149 at (9,10) by #75 L4 from (12,10): 4 steps through a portal, 1 pearl eaten, 2 paid, outside her view. Then attrition: 39 splits of 5-6 into 2 + 3-4 and 39 short wall deaths in r150-409; behind for good r367. Not the bug (25 crossings). REACH_EATS and QUEEN_FAR_HEADS were meant to cover the ram; which condition missed: not determined. Known: queen at 2 after theirs is dead.
1513123 Slithery Fight v QQ: lost on total 143 v 174 (queens 0 v 0, longest 29 v 29). Theirs died r258; ours (3 long from r25, 5 pearls all game) L4 rammed r285 by #943 L8, 8-step sprint paying 5, outside her view. Decider r461: our #1234 L50 (their longest 26) rammed at (5,4) by #1112 L6 from (6,7), 2 free + 2 paid; behind for good from r461. [C] BIG_ESCAPE was meant to cover: long_escape (4662-4664) returns unless threat_at(chosen) is non-zero, and map_threats sizes an enemy by visible_parts (4311; the 4-part floor at 4312-4317 is queen-only). [M] 1 of 6 attacker parts was in the L50's view. [E] so its step to distance 4 read as safe.
1508962 Slithery Fight v JM: lost on longest 9 v 28 (queens 0 v 0). Our queen led 28 v 20 (fed from 8 at r300 while total fell 138 to 76). r370-373 enemy #1128 L2 walked beside her, head adjacent at each of her turn starts; she took 1 step S a turn with 7 free steps available. r374, two more L2 heads in view: she split keeping 2 (child L26, lines 1805-1808 as written), rammed that round by #1128; child rammed r377 by an adjacent L2. Behind for good r374. No mate within 5; nothing makes her break contact with a following head.
1508963 Islands v JM: lost on longest 14 v 19 (queens 0 v 0). Theirs died r95; ours stayed 3-5 for 240 rounds. r337 at L8 she split keeping 2 (#560 L3 at distance 3), r338 stepped W into a one-wide lane, r339 both moves were next to #560's head: rammed at (1,35). Longest then 22-29 v 4-9 until r425; we lost L16 (r426), L30 (r442, L6, 3 steps, 2 of 6 parts in view), L19 (r466, L6, 4 steps, 2 of 6): behind for good r466; alive 42 to 3 over r400-499.
[M] Both battles: 33 rams on our non-queens of 8 or longer; attacker fully in view 3, partly 19, not in view 11 (rammed-battles.txt).

ONE THING FOR THE 1-4? Half. Trauma and Queen Of Spades are the portal bug; Stripes and Slithery Fight are queen-dead-short then longest dragon. Shared maps with one8's 4-1: Queen Of Spades (above) and Autarky (won both times).

VERDICT
1. BUG: PORTAL_SCOUT_MIN_LEN. Every use is gated by "> 0" (lines 625, 659, 689, 696, 728, 8252), so PORTAL_SCOUT_MIN_LEN:0 restores one11 behaviour for this switch and leaves the other four one12 switches alone. Built copy: build-ps0/ (one-line diff, compiles clean). Support: 48 of 108 games with zero crossings against 0 of 120; Trauma 2 wins of 12 against 5 of 11. Suggest a local head-to-head on portal maps before it goes live.
2. Not bugs, known open: queen shed to 2 and rammed (3 games); long dragon rammed by a short enemy mostly out of view (2 games). No constant: raising reach for all dragons (THREAT_REACH_MIN, BIG_REACH_BONUS) is unmeasured and wide.
3. No standing still, timeouts or illegal actions found in the traces I read.

---

## 2026-10-09 01:27:08 — closing summary

weak13-opus report: `PORTAL_SCOUT_MIN_LEN 4` (live since one12) keeps our whole side out of portals; it starved us in 2 of the 4 Quaker Qubits losses. The other 4 lost games are the known open weaknesses.
BUG: yes, one. The rule fires far wider than written. CONST candidate `PORTAL_SCOUT_MIN_LEN:0` (compiles; not played by me).
How sure: mechanism high (code + boards + 228 games counted). That 0 wins more: untested.

All 10 games of both battles were played by bot 21377 (one13); the 4-1 battle b1483679 by 21126 (one8). The same report went to team-lead by SendMessage.
Folder: `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/weak13-opus/` (ledgers every 25 rounds in `ledger.txt`, queen boards in `queen-boards.txt`).

**The bug**
- [C] `one13-bot/main.cpp` 727-770 `guard_portal_scout`: a non-queen under 4 whose step crosses a portal with a never-seen far tile (line 736) is turned to the best ordinary step whenever any neighbour with one free onward tile exists (`portal_scout_open`, 695-716). On open ground that always holds, and as nobody crosses, the far tile is never seen. The queen is barred as before (`QUEEN_NO_PORTAL`) and non-queens split at 4.
- [M] Portal crossings r0-99 by our non-queens under 4, 15-game sets, maps with portals: one8-11 32.5 per game, zero in 0 of 120 games; one12-13 4.1 per game, zero in 48 of 108. Trauma 6.4-11.7 before, 0 in 11 of 11 games since.
- [M] Our pearls r0-99, one11 -> one12 -> one13: Trauma 40.3 -> 7.7 -> 5.0; Portals 235 -> 74 -> 71; Queen Of Spades 59 -> 10.7 -> 22; Australia 90 -> 48 -> 33; Default 57.7 -> 22 -> 30. No-portal and short-hop maps (Devil, weakhold, Tower Defense, Maze, Stripes) did not move.
- [M] Trauma under one12/13: 2 wins of 12 (sets 1 of 9, ranked 1 of 2, new q1 set 0 of 1); one8-11: 5 of 11.
- [M] New set one13-q1 (7 of 15): zero turn starts outside the home area in r0-199 on Trauma (lost), Australia (lost), Schooltime (won); Default zero in r0-99 (lost).
- Not checked: how many blind-portal deaths the guard saved; a local head-to-head of one13 against the copy with 0; the portal share of the local maps behind one12's 40-3-29.

**Lost games**
- **1513120 Trauma v QQ:** wiped out r353 (0 v 51 dragons, total 151, their queen 13). Out-eaten from r25 (r100 total 11 v 18, r200 20 v 89). [M] 0 of 916 turn starts outside our 264-tile home in r0-199; 12 of 184 natural spawns fell there; we ate 12, they 166. #3 (L2) circles (37,22)-(37,23)-(38,23)-(38,22) and #5 (L3) circles (37,3)-(37,4)-(38,4)-(38,3), each loop touching the portal tile (`look-1513120-d3.txt`). Queen #1 was our last dragon at L17, rammed r353 by #209 L7 from (44,10), 5 steps (2 free, 2 paid), no pearls, outside her view at her turn start; their queen alive. Cause: the bug.
- **1513119 Queen Of Spades v QQ:** wiped out r264 (0 v 23 dragons, their queen 7); behind for good r47. [M] r0-49 we ate 2, they 26; 0 of 348 turn starts outside home in r0-99, 1 portal crossing. Queen #0 L4 ate 1 pearl in 74 rounds and never split; r74 she stepped E to (20,29), two tiles from visible #28 L3 at (20,31), which hit with 1 free + 1 paid step. W was open; why she chose E is not determined. Cause: the bug. Same map under one8 (1483680, won, wiped them out r308): 177 of 551 turn starts outside home, 22 crossings, 49 pearls r0-99 against 18.
- **1513121 Stripes v QQ:** wiped out r409, both queens dead. Theirs died r98 (own body). Ours at L2 was rammed r149 at (9,10) by #75 L4 from (12,10): 4 steps through a portal, 1 pearl eaten, 2 paid, outside her view. Then attrition: 39 splits of 5-6 into 2 + 3-4 and 39 short wall deaths in r150-409; behind for good r367. Not the bug (25 crossings). `REACH_EATS` and `QUEEN_FAR_HEADS` were meant to cover the ram; which condition missed is not determined. Known: queen at 2 after theirs is dead.
- **1513123 Slithery Fight v QQ:** lost on total 143 v 174 (queens 0 v 0, longest 29 v 29). Theirs died r258; ours (3 long from r25, 5 pearls all game) at L4 was rammed r285 by #943 L
[result truncated — ask the agent for the rest via SendMessage]
