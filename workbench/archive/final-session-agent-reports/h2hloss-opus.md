# Reports sent to the lead by h2hloss-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-08 21:47:59 — h2h loss analysis: three lines and suspect counts

h2hloss-opus result: no switch among (a)-(g) causes the losses; 15 of one11's 28 losses are "killed one8's queen first, then lost our own queen".
MECHANISM: 15 of one11's 28 losses (11 of one10's 24) = it killed one8's queen first, then lost its own (8 of the 15 at length 2; all 26 ram deaths of our queen are by one8 dragons of 2-4), and the game went to elimination or longest dragon. 5 of its 14 longest-dragon losses turned on a dragon of ours rammed after r400 that was at least as long as one8's final longest (one8 lost 0 of 7 that way). On 24x12 open, rotation and ring the same seat wins in all four pairings, whatever the version.
CONSTANTS: none removes most losses. Keep QUEEN_SURE_LEN:64,QUEEN_SURE_STEPS:5. Weakly supported only: QS_KEEP_MIN_UNITS:2,RALLY_END_FRESH:5. The fix is a rule, not a constant: once the enemy queen is dead, our queen stops splitting and paying below 4 and is fed from that round.
HOW SURE: sure of the counts; not sure one11 is worse than one8 at all. At 06:46 KST: one11 v one8 17-28-2 in 47 games (P 0.068 one-sided), one10 v one8 21-24-3 (P 0.383), one8 v one5 14-19, one11 v one5 17-17. No change was built or played.
Per suspect (one11 v one8; one10 v one8 in brackets), all measured:
(a) QUEEN_SURE 64/5: kills one8's queen 31 (32); 10 (8) needed a 4-5 step move; rammer of 5+ in 7 (10), longest 13 (11), total length 61 (70), all before r216 (r321). No long dragon thrown away. First queen kill in 27 of 47 games, but only 12 of those 27 won (one8 wins 8 of the 11 where it kills ours first).
(b) QS_KEEP_MIN_UNITS 6: queen at length 2 in 31% of alive rounds r0-100 v 13%; 4-long queen splits r<=100 83 v 12. Queen deaths per 100 rounds (poor maps out, both arms): 1.27 at 2, 0.61 at 3, 0.35 at 4; once one8's queen is dead 2.61 / 0.87 / 0.08. But of 14 traced deaths at 2, 5 were escape splits within 2 rounds of death, not this switch.
(c) REACH_EATS, CUT_BODY, QS_PAY_REACH: no pearl loss (dragons of 2-4: 29.0 v 30.2 pearls per 100 turns r1-50, 15.3 v 15.9 r51-100; queen 14.2 v 15.3, 7.1 v 6.8). Queen paid moves 50 v 23 (55 v 33). Costs games only on poor maps: 3 losses on queen length (2:3, 2:5, 2:3), two of the payments with the nearest one8 head 6-7 tiles away.
(d) QUEEN_BOOT_LEN 6: queen alive at r350 in 11 games: 5 with a queen of 13-37 (4 wins), 6 poor-map games with no pearls. Never the cause.
(e) QUEEN_EXIT_STRICT: mates self-killing within 2 of our queen r<=300: 28, length 69 (one10 without it: 22, length 72). About 1.4 length a game.
(f) SPLIT_PORTAL_OK: islands 4-2 (5-1). Not the cause.
(g) no RALLY_END_FRESH: longest ours v one8 r400 24.7 v 24.1, r475 43.9 v 49.3, end 47.8 v 55.2 (one10 with rally: 28.0 v 26.9, 48.9 v 50.8, 46.6 v 51.2); our top dragon rammed after r350 60 v 34 (38 v 30). But on the 31 map+side pairs both played: one11 12-17, one10 13-15.
By family, one11 then one10: rooms 1-5, 1-5; ring 2-4, 1-5; rich 0-5, 4-2; poor 1-3, 1-2; corridors 4-2, 4-2; islands 4-2, 5-1; open 3-3, 2-4; rotation 2-4, 3-3. I did not find why rooms and ring favour one8.
Measure next: share of "we killed their queen first" games won (now 12 of 27, 3 on queen length); our queen's deaths per 100 rounds after theirs is dead, by her length; our top dragon rammed after r350 per game (now 1.9, one8 1.1).
report.md was NOT written: the write of a report file is blocked for me, and I did not route around it. Full report text follows in my next message. Scripts and tables are in data/codex/astra/h2hloss-opus/ (out-losses.md = every loss; ledgers-losses.txt = 25-round ledgers; out-pairs.txt, out-suspects.txt, out-feed.txt, out-extra.txt, out-q2.txt).

---

## 2026-10-08 21:47:59 — full report text for report.md

Full text intended for data/codex/astra/h2hloss-opus/report.md (I could not save it; paste as is if you want it on disk).

**Mechanism.** No switch among (a)-(g) accounts for the losses. 15 of one11's 28 losses (11 of one10's 24) are games where it killed one8's queen first and then lost its own queen (8 of the 15 at length 2, every ram by a one8 dragon of 2-4), after which the game went to elimination or the longest dragon; 5 of its 14 longest-dragon losses turned on a dragon of ours rammed after r400. On 24x12 maps the seat decides, not the version.
**Constants.** None removes most of the losses; keep `QUEEN_SURE_LEN:64,QUEEN_SURE_STEPS:5` (it creates the lead). Weakly supported only: `QS_KEEP_MIN_UNITS:2,RALLY_END_FRESH:5`. The fix is a rule, not a constant: once the enemy queen is dead, our queen stops splitting and paying below 4 and is fed from that round.
**How sure.** Sure of the counts. Not sure one11 is worse than one8 at all: 17-28-2 in 47 games (P 0.068 one-sided), one10 21-24-3 (P 0.383), and one8 itself is 14-19 against one5.

Counts are from games finished by 06:46 KST; more were arriving. [M] measured, [C] code (one11-bot/main.cpp), [E] inferred.

## 1. Record [M]
| pairing | games | W-L-D | 24x12 | 64x16 | 24x64 | lost by elim / longest / queen / total |
|---|---|---|---|---|---|---|
| one11 v one8 | 47 | 17-28-2 | 4-10 | 7-9 | 6-9 | 10 / 14 / 3 / 1 |
| one10 v one8 | 48 | 21-24-3 | 7-7 | 6-9 | 8-8 | 8 / 14 / 2 / 0 |
| one8 v one5 | 33 | 14-19-0 | 7-5 | 5-6 | 2-8 | 5 / 14 / 0 / 0 |
| one11 v one5 | 34 | 17-17-0 | 7-5 | 7-5 | 3-7 | 6 / 10 / 0 / 1 |

By family, one11 then one10 against one8: open 3-3, 2-4; rooms 1-5, 1-5; corridors 4-2, 4-2; islands 4-2, 5-1; ring 2-4, 1-5; rotation 2-4, 3-3; poor 1-3, 1-2; rich 0-5, 4-2.
Seat [M]: on open, rotation and ring 24x12 the same seat wins in all four pairings (out-pairs.txt). A loss on those maps says nothing about the version.

## 2. Every loss
All 28 + 24 losses (how decided, final queen / longest / total, round behind for good, queen deaths, biggest own dragon rammed after r400): out-losses.md. Ledger every 25 rounds for each (dragons, total, longest, queen; pearls natural / own corpse / enemy corpse; deaths by cause with lengths): ledgers-losses.txt.

| one11 losses (28) | count |
|---|---|
| one8's queen died first, then ours (our queen at 2 / 3 / 4 / 5+ when she died) | 15 (8 / 4 / 1 / 2) |
| our queen died first | 8 |
| queens rammed each other | 2 |
| both queens alive, lost on queen length (poor maps) | 3 |
| of the 14 lost on longest: a dragon of ours rammed after r400 was at least as long as one8's final longest | 5 (one8 lost 0 of its 7 that way; one10: 3 lost, 6 won) |

## 3. Suspects [M unless marked]; one10 v one8 in brackets
| suspect | count | verdict |
|---|---|---|
| (a) QUEEN_SURE 64/5 | kills one8's queen 31 times (32); 10 (8) needed a 4-5 step move; rammer of 5+ in 7 (10), lengths 7,9,5,8,10,13,9, sum 61 (70), all before r216 (r321); those games 3 W 4 L (7 W 3 L) | no long dragon thrown away; not the cause. First queen kill in 27 of 47 (20 of 48) |
| (b) QS_KEEP_MIN_UNITS 6 | queen at length 2 in 31% of alive rounds r0-100 v 13% (31% v 13%); 4-long queen splits r<=100 83 v 12 (76 v 11). Deaths per 100 queen rounds, poor maps out, both arms: 1.27 at 2, 0.61 at 3, 0.35 at 4; once one8's queen is dead 2.61 / 0.87 / 0.08 | real but small: of 14 traced deaths at 2, 9 followed a 4-into-2+2 split, 5 of them within 2 rounds (escape splits [C] 1529-1540, not this switch) |
| (c) REACH_EATS, CUT_BODY, QS_PAY_REACH | pearls per 100 turns ours v one8: dragons of 2-4 29.0 v 30.2 (r1-50), 15.3 v 15.9 (r51-100), 14.0 v 14.8 (r101-350); queen 14.2 v 15.3, 7.1 v 6.8. Queen paid moves 50 v 23 (55 v 33), segments 65 v 23 | no pearl loss. The queen pays twice as often; decides games only on poor maps (queen 2:3, 2:5, 2:3) |
| (d) QUEEN_BOOT_LEN 6 | queen alive at r350 in 11 games: 5 with a queen of 13-37 (4 wins), 6 poor-map games with a queen of 2-3 and no pearls | never the cause |
| (e) QUEEN_EXIT_STRICT | mates killing themselves within 2 of our queen, r<=300: 28, length 69, 0.37 per 100 queen rounds (one10 without it: 22, length 72, 0.31; one8 0.22) | about 1.4 length a game; not the cause |
| (f) SPLIT_PORTAL_OK | islands 4-2 (5-1) | not the cause |
| (g) no RALLY_END_FRESH | longest mean ours v one8: r400 24.7 v 24.1, r475 43.9 v 49.3, end 47.8 v 55.2 (one10: 28.0 v 26.9, 48.9 v 50.8, 46.6 v 51.2). Our top dragon rammed after r350 60 v 34 (38 v 30). Feeder pearls reaching the leader 24% v 25% | weak: on the 31 map+side pairs both played, one11 12-17, one10 13-15 |

[C] 4053-4058: with REACH_EATS every dragon of ours rings a visible enemy of under 5 parts at its exact sprint reach (parts - 1), where one8 gave dragons of 15+ a ring of parts + 2 (BIG_REACH_BONUS, 374). [M] dragons of 15+ rammed by a 2-4: 301 v 237 (353 v 299), but 55 v 44 in one8 v one5 where neither side has the switch: not attributable.

## 4. What one8 does to us
[M] All 26 ram deaths of our queen are by one8 dragons of 2-4 (its QUEEN_SURE_LEN 4), 16 from 1-2 steps. [M] When one8 kills our queen first it wins 8 of 11; when we kill its queen first we win 12 of 27. [E] one8 does not counter the new rules; one11 reaches the winning position more often and has no rule for holding it.

## 5. General or one8 only
General (any opponent that rams queens or leaders): losing the only queen at length 2-3; the late leader ram; the queen paying on poor maps. Not version related: the 24x12 seat. Against one5 (QUEEN_SURE_LEN 0) one11 is 17-17.

## 6. Replay moments (h2h_mDone11_v8)
- rooms_24x12 side0: r38 our 3 rams one8's queen and our queen pays 3 to 2; r44-46 she walks (1,1), (1,0), (2,0) with a one8 2-long behind, at r47 has no free cell and rams it; eliminated r90. Same opening in one10.
- corridors_24x12 side1: one8's queen dead r64; ours splits 4 into 2+2 and dies within a round (r95, own body).
- ring_64x16 side1: one8's queen dead r61; ours splits to 2 and is rammed by a 3 at r226.
- rich_24x64 side0: longest 195:117 at r475; our 216 rammed r489 by an 8; final 118:119.
- rooms_64x16 side0: 56:30 at r475; our 56 rammed r486 by a 4 in 3 steps; final 8:43.
- poor_64x16 side0 r302 and side1 r258: queen pays 3 to 2 with the nearest one8 head 7 and 6 tiles away; final queens 2:3 and 2:5.

## 7. Next head-to-head: measure
Games where we kill their queen first and win (now 12 of 27, 3 on queen length); our queen's deaths per 100 rounds after their queen is dead, by her length (now 2.61 at 2, 0.08 at 4); our top dragon rammed after r350 per game (now 1.9, one8 1.1).

## 8. Not checked
Which of CUT_BODY_LEN, QS_PAY_REACH, REACH_EATS triggers the poor-map payment (no games allowed). Why rooms and ring favour one8. Whether the 15+ ram excess is the hunter's or the victim's doing. One seed per map and side. No proposed change was built or played.

Scripts: scanall.py, turns.py, ledger.py, losses.py, pairs.py, suspects.py, feed.py, bigram.py, exposure.py, queens.py, small.py, q2.py, extra.py, trace.py; outputs out-*.txt.

---

## 2026-10-08 22:15:36 — closing summary

No switch among (a)–(g) causes the losses, and `report.md` was not written: the write of a report file is blocked for me, so I sent the full report text to you as a second message instead.

**Mechanism.** 15 of one11's 28 losses (11 of one10's 24) are games where it killed one8's queen first and then lost its own queen. In 8 of those 15 she died at length 2, and all 26 ram deaths of our queen are by one8 dragons of 2–4. 5 of one11's 14 longest-dragon losses turned on a dragon of ours rammed after r400 that was at least as long as one8's final longest (one8 lost 0 of 7 that way). On 24x12 open, rotation and ring the same seat wins in all four pairings, whatever the version.

**Constants.** None removes most of the losses. Keep `QUEEN_SURE_LEN:64,QUEEN_SURE_STEPS:5`. Only weakly supported: `QS_KEEP_MIN_UNITS:2,RALLY_END_FRESH:5`. The fix is a rule, not a constant: once the enemy queen is dead, our queen stops splitting and paying below 4 and is fed from that round.

**How sure.** Sure of the counts; not sure one11 is worse than one8 at all. At 06:46 KST one11 v one8 was 17-28-2 in 47 games (P 0.068 one-sided), one10 v one8 21-24-3 (P 0.383), one8 v one5 14-19, one11 v one5 17-17. No change was built or played.

Per suspect (one11 v one8; one10 v one8 in brackets), all measured:
- **(a) QUEEN_SURE 64/5:** kills one8's queen 31 times (32); a rammer of 5+ in 7 (10), longest 13 (11), total length 61 (70), all before r216 (r321). No long dragon is thrown away. It gets the first queen kill in 27 of 47 games but wins only 12 of those; one8 wins 8 of the 11 where it kills ours first.
- **(b) QS_KEEP_MIN_UNITS 6:** queen at length 2 in 31% of her alive rounds r0–100 against 13%; 4-long queen splits r≤100 83 v 12. Her deaths per 100 rounds are 1.27 at length 2, 0.61 at 3, 0.35 at 4 (2.61 / 0.87 / 0.08 once one8's queen is dead). Of 14 traced deaths at 2, 5 were escape splits within 2 rounds of death, not this switch.
- **(c) REACH_EATS, CUT_BODY, QS_PAY_REACH:** no pearl loss (dragons of 2–4: 29.0 v 30.2 pearls per 100 turns r1–50; queen 14.2 v 15.3). The queen pays twice as often (50 v 23 moves). That costs games only on poor maps: 3 losses on queen length (2:3, 2:5, 2:3).
- **(d) QUEEN_BOOT_LEN 6:** queen alive at r350 in 11 games: 5 with a queen of 13–37 (4 wins), 6 poor-map games with no pearls. Never the cause.
- **(e) QUEEN_EXIT_STRICT:** 28 mates self-killed within 2 of our queen by r300, length 69 (one10 without it: 22, length 72). About 1.4 length a game.
- **(f) SPLIT_PORTAL_OK:** islands 4-2 (5-1). Not the cause.
- **(g) no RALLY_END_FRESH:** longest ours v one8 is 24.7 v 24.1 at r400 and 47.8 v 55.2 at the end (one10 with rally: 28.0 v 26.9, 46.6 v 51.2). Our top dragon is rammed after r350 60 v 34 times (38 v 30). On the 31 map+side pairs both played, one11 is 12-17 and one10 13-15.

Rooms (1-5, 1-5) and ring (2-4, 1-5) favour one8 for both newer versions; I did not find why. I also did not determine which of the three queen-ring constants triggers the poor-map payment.

Everything is in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/h2hloss-opus/`: `out-losses.md` has the table of every loss and `ledgers-losses.txt` the 25-round ledgers.
