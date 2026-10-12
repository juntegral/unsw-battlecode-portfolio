# Reports sent to the lead by late-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 05:00:59 — Interim headline numbers A and B

late-opus INTERIM (one11-15 only, 474 games, from shed-sonnet's per-round data; my full scan with head check, free cells and death causes is still running, final by 14:10).
WARNING for the wait-split builder [M]: the opening IS a wait split from 10+. In 33 of 474 games the queen starts at 25 and splits 25 -> 3 in 11 straight turns at rounds 0-10; 264 wait-split turns from 10+ happen in rounds 0-99 against 122 at round 300+ and 6 at 100-299. A switch "no wait split for queens of 10+" without a round or phase gate removes the opening. Gate it (e.g. round >= 100, or only when she is not the only dragon).
Count A, late only (run starts at r100+, queen 10+) [M]: 70 runs / 141 turns in 36 of 474 games (7.6%). Length lost 282 cells in total = 7.8 per affected game; 23 runs are 2+ turns long and take 188 of the 282 (longest 13 turns, 36 -> 10, game 1501020 r401). She led the queen race at the start of 56 of 70 runs; after the run she had lost that lead in only 1. Dead within 5 rounds of the run end: 4 of 70; within 20 rounds: 14 of 70 (13 of them from a lead). Those 36 games: 15 wins, queen alive at the end in 11.
Count B [M]: at round 350 our queen was alive and longer than theirs (or theirs dead) in 50 of 474 games. We won 25 and LOST 25; in 24 of the 25 losses our queen died after r350 (1 was overtaken alive). So the prize for late queen protection is about 25 games in 474 (5.3% of all games, half of all games where we lead at r350). 51 queen deaths at r350+ overall. Causes and the toward/away split follow.
Other [M]: our queen is alive at r300 in only 133 of 474 games (dead before r100 in 112, r100-299 in 175).

---

## 2026-10-09 05:01:58 — Final: wait-split and late queen death counts

late-opus FINAL (509 games, one11-16, 330 unranked + 179 ranked; no one17 game is on disk yet). Replaces my interim.
A. Late wait splits from 10+ (r100+) [M]: 72 runs / 166 turns in 38 of 509 games (7.5%), 332 cells lost (8.7 per affected game; 24 multi-turn runs take 236). She led at the start of 58 runs and still led after 57. Dead within 5 rounds 5/72, within 20 rounds 15/72. Lost cells alone flip exactly 1 game (1530577).
B. Prize [M]: queen alive and longer at r350 in 51 games; won 25, LOST 26 (5.1% of all games): 25 by her death after r350, 1 overtaken alive.
How sure: counts are exact for this population; whether the switch helps is not shown. Games with a late run do no worse than queens of 10+ without one (39% wins both).

WARNING for the builder [M]: the opening is the same pattern. 35 games open with an 11-turn run 25 -> 3 at round 0 (385 turns, 280 of them with 0 free cells). An ungated "no wait split at 10+" removes the opening. All 72 late runs start with 1+ free cell (23 with exactly 1, 49 with 2+). Forcing a move at 1 free cell sends her into her only exit, so gate on round >= 100 and 2+ free cells.

Count A tables (wait-split turns = head stays, length -2; all 2,126 queen splits leave her head in place, 2,080 are -2, 46 are sheds to 2)
  L       r0-99  100-299  300+   all  |  free 0   1    2+
  4-5      1081     403    17   1501  |     88   462  951
  6-9        80      22    44    146  |     37    72   37
  10-19     175       6    59    240  |    175    17   48
  20+       105       0    88    193  |    105    35   53
  all      1441     431   208   2080  |    405   586 1089
  In 473 of 509 games. Run lengths: 1 x1562, 2 x17, 3 x6, 4 x2, 8 x2, 10 x2, 11 x35 (openings), 13 x1, 24 x1.
  Late runs from 10+: nearest visible enemy head at the start was 7+ cells away in 43, 4-6 in 20, 3 or less in 7, none in 2. So mostly she is waiting, not hiding.
  The 38 games: 15 wins, queen alive at the end in 12.
  Comparison, queen 10+ at some round from 300 on:
    no late run   n 37  alive at end 15  wins 14  mean final length 18
    late run      n 36  alive at end 12  wins 14  mean final length 16
  Moments: 1530577 (one16, Slithery Fight v Preyas) r466-489, 24 splits 69 -> 21 with 1 free cell and enemy heads 1-5 cells away; their queen 19 -> 31, we lose 23 v 31. 1501020 r374-381 43 -> 27 and r401-413 36 -> 10, dead r422, lost. 1516556 r353-360 20 -> 4 and r427-436 29 -> 9, won 31 v 0.

Count B tables: 53 queen deaths at r350+ (41 lost, 12 won)
  cause                  all   longer than their queen at death
  rammed, seen            25    13
  rammed, unseen          10     8
  own move                17    11
  mate's turn              1     0
  total                   53    32 (21 lost, 11 won)
  Last 3 turns against the nearest visible enemy head: away 26, toward 14, level 11, none visible 2.
  Our dragons with head within 5 cells: none 24, one 13, two or more 16.
  The 26 losses from a lead at r350:
    died at 2-6 (13): 12 had shed from 10+ to 2-3 after r350; 11 rammed seen, 2 own move. This is the group one17's QS_SHED_MAX targets, unmeasured so far.
    died at 7+ (12): 6 rammed unseen, 5 rammed seen (attacker inside her own 7x7 in only 1), 1 own move; attacker took 3+ steps in all 11 (5 steps in 6) and was 6 or shorter in 7; no mate within 5 in 7; a wait split from 10+ in her last 20 rounds in 6.
    alive, overtaken (1): 1512570.
  By version, lead at r350 / won / lost by death: one11 5/3/2, one12 10/5/5, one13 19/9/9, one14 12/8/4, one15 4/0/4, one16 1/0/1.
  Moments: 1496859 r497 queen 85 rammed unseen by a 4 moving 5 steps; 1516206 r395 queen 46 by a 12; 1523634 r391 queen 44 by a 3 moving 4 steps.

Not checked: "rammed" means she died on an enemy's turn (death reason code not decoded); 7 own-move deaths have no identified target; toward/away uses torus distance ignoring walls and portals; "seen" = attacker head inside any of our 7x7 views at her last turn start.
Files: ~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/late-opus/ (scan.py, tab.py, extra.py, data.json, tables.txt with every run and death row, extra.txt).
