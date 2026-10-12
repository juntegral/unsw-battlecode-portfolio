# Reports sent to the lead by opp-ballers

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 05:47:33 — Ballers first report: no rematch

opp-ballers 1/2: NO rematch with Ballers. Live bot one18 just lost to them 1-4 (b1535553); I put about 35% per game on it (1 of 5 with one18, 5 of 10 over both battles, all seat A).
Decides the games: we only beat them by wiping them out on maps of 972 cells or less (4 of our 5 wins, r156-r240). On 1152+ they keep pace or out-eat us, hold their queen at home at L3-6, then feed her after r400 (Trauma 4>23 in r401-r416, Maze 2>31>75).
Constant for the last upload: none (checking FEED_CAP_ROUND and the queen split now, final by 14:46).

[M] all rows from data/codex/astra/opp-ballers/tab.py, same script both sides. Qend = queen length at the end, r100 = natural pearls / dragons.
game    ver   map(cells)        res  how      Qend u/t  pearls u/t  dragons u/t
1507596 one13 Autarky 972       W    elim r164   3/0     88/33      34/5
1507594 one13 Devil 512         W    elim r156   0/0    100/29      32/2
1507595 one13 Prisoners 512     W    elim r240   4/0      7/4        8/1
1507593 one13 Schooltime 2400   W    longest 24v23 3/3   26/22      16/13
1507592 one13 Trauma 1152       L    queen       0/34     6/26       6/10
1535556 one18 weakhold          W    elim r180   4/0     68/10      18/3
1535553 one18 Maze 1152         L    queen       0/75   100/97      37/34
1535555 one18 Stripes 288       L    elim r207   0/0     30/17       4/7
1535557 one18 Schooltime 2400   L    longest 14v22 3/3   18/21      11/14
1535554 one18 Around UNSW 4096  L    longest 62v78 0/0  131/236     49/62
Seat A 5/10, seat B none. Schooltime 1/2; every other map once.

Losses, one line each [M]:
- Maze: queen self-trap. r236-r250 she split six times (7>5>3, then 4>2 four times) in cells with 1 free neighbour, took a portal r245, free 0 at r250, died on her own tail r251 at L2. Totals were level (165 v 153 at r250).
- Stripes: queen rammed from a one-way place, THROWN (their queen dead since r75). r155 three heads 2 away, r156 she took a portal into a 1-free lane, rammed r159 by dragon 25 (L2, 1 free step, from 1 away), unseen by her.
- Around UNSW: out-eaten from r50 (74 v 111) + queen rammed in the open r121 (L4, free 3) by dragon 219 (L7, from 4 away).
- Schooltime: out-eaten from r175 (73 v 86); our total fell 83 > 37 r225-r400, theirs rose to 150. Queens 3/3.
- Trauma (one13): out-eaten from r50 (6 v 26 pearls by r100) + long queen lost (L16 split to 2 at r430, rammed r431): the split is what QS_SHED_MAX fixed in one17.
Wins: their queen rammed by our L2-L3 from 1-2 away (Devil r137, Prisoners r240, weakhold r180) or dead by their own mate through a portal (Autarky r24), then elimination.

---

## 2026-10-09 05:47:33 — Ballers final: no rematch, no constant

opp-ballers FINAL: NO rematch with Ballers. About 35% per game for one18 (1 of 5 in b1535553 today; 5 of 10 over both battles, all seat A, no seat B games).
Decides the games: map size. We wipe them out on 972 cells or less (4 of 5 wins, r156-r240; Stripes 288 was thrown). On 1152+ we are 1 of 5: they keep pace or out-eat us and their queen outlives ours.
Constant for the last upload: none. Nothing here is verified as a value change, and the one bot fault I can name needs code, not a constant.

Table and per-loss lines are in my first message (unchanged). One correction to the Maze line [M 1535553, one18]:
- Maze is "long queen lost" first, self-trap second. Queen was L15 at r232 standing at (17,22) and split off 2 a turn for six turns (15>13>11>9>7>5>3, r232-r237), nearest foe 4-6 away (L2-L6). Then 4>2 four times in 1-free cells (r239-r250), dead on her own tail r251. Their queen was L4-6 until r400, so L15 was ahead for 170 more rounds. This is the standing split battle-opus saw in 1532061 (main.cpp:1797 by its note); QS_SHED_MAX 9 does not stop it. Second sighting, now on one18.

What Ballers do [M unless marked]:
- Queen stays home. Maze and Trauma: no foe within 6 at any 50-round sample, 2-8 mates within 4 (Maze). Schooltime both games: she circles a 1-free nook at (2,2)/(3,1) at L3 for 500 rounds.
- Late feed after r400 when she is alive on a mid map: Trauma 4>23 in r401-r416 (34 at the end), Maze 2>31 in r404-r428 (75 at the end). Not on Schooltime (3 both times). So a queen of ours under about 30 loses a mid-map game that reaches r420 with their queen alive [E from 2 games].
- Rams on our queen, 4 of them: attacker L2-L7 from 1-4 away, 1-2 free steps plus 0-1 paid. Devil r42 (L4, 2 away), Trauma r431 (L4, 3 away), Stripes r159 (L2, 1 away, free), Around UNSW r121 (L7, 4 away). Our queen was L2-L4 each time; three of the four came the turn after she split or took a portal.
- Big maps: they out-split us early (Around UNSW dragons r50 47 v 30, pearls by r100 236 v 131).
What of ours beats them: small-map eating (pearls by r100 88 v 33, 100 v 29, 68 v 10) and our L2-L3 ramming their queen from 1-2 away with 0-1 paid (Devil r137, Prisoners r240, weakhold r180).

Not checked: rating points per result, why our Schooltime total fell 83 > 37 in r225-r400 (1535557), whether the standing split has a live switch that should have caught it. Files: data/codex/astra/opp-ballers/ (tab.py, qt2.py).

---

## 2026-10-09 05:47:33 — closing summary

Both reports went to the lead (first at 14:41, final at 14:42 KST). No code or git changes were made.

**Answer for the lead**
- **Rematch with Ballers: no.** The live bot one18 just lost to them 1-4 (battle b1535553). I put about 35% per game on it, resting on 5 games with one18 and 10 over both battles, all seat A.
- **What decides the games: map size.** We eliminate them on maps of 972 cells or fewer (four of our five wins, by r156-r240). On 1152 cells and up we are 1 of 5.
- **Constant for the last upload: none.** No value change is verified, and the one bot fault I can name needs code.

**Losses by class**

| Game | Map (cells) | Version | Class |
|---|---|---|---|
| 1535553 | Maze (1152) | one18 | long queen lost, then queen self-trap |
| 1535555 | Stripes (288) | one18 | queen rammed from a one-way place (thrown: their queen was dead since r75) |
| 1535554 | Around UNSW (4096) | one18 | out-eaten from r50, plus queen rammed in the open at r121 |
| 1535557 | Schooltime (2400) | one18 | out-eaten from r175 |
| 1507592 | Trauma (1152) | one13 | out-eaten from r50, plus long queen lost (the split one17 fixed) |

- **Maze fault:** our queen was L15 at r232 and split off 2 a turn for six turns down to L3, with the nearest enemy 4-6 away. She then split 4 to 2 four more times in one-exit cells and died on her own tail at r251. `QS_SHED_MAX` 9 did not stop this; it is the standing split battle-opus already flagged in game 1532061.

**What Ballers do**
- **Queen stays home:** in Maze and Trauma no enemy was within 6 of her at any 50-round sample; in Schooltime she circles a one-exit nook at L3 all game.
- **Late feed:** on mid maps with her alive, they feed her after r400 (Trauma 4 to 23 in r401-r416, Maze 2 to 31 in r404-r428, 75 at the end).
- **Rams on our queen:** four of them, by dragons of L2-L7 from 1-4 away, using 1-2 free steps plus 0-1 paid. Our queen was L2-L4 each time.

**Not checked:** rating points per result, why our Schooltime total fell from 83 to 37 in r225-r400, and whether a live switch should have caught the standing split.

Scripts are in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/opp-ballers/` (`tab.py` for the both-sides table, `qt2.py` for the queen trace, `poll.py`).
