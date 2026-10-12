# Reports sent to the lead by opp-cybers

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 05:39:58 — Cybers first report: 6/10, longest-dragon race decides

5) Another ranked battle vs Cybers: weak YES. Per-game win chance 0.60 [M: 6 of 10, all seat A, two battles both 3-2; one18 = 3 of 5]; if games were independent that is ~0.68 to take the battle [E]. Points seen on disk: +20 for our 3-2 here, -36 for a 2-3 vs a 2151 team as seat A, so expected gain is near zero: it is variance, not value.
Decides our games: whether their side collapses early. When it does we win by elimination (5 of 5: weakhold x2, Trophy, Queen Of Spades, Devil; they hold 0-3 dragons by r75). When they grow level, the queens end equal (both dead, or both sealed at 3) and the LONGEST dragon decides: we are 1 of 5 there.
Constant for the last upload: NONE. The gap is how fast their feeding runs after r400, not a round threshold we have.

Table [M] (same scripts both sides: l15.py, both.py, qside.py in data/codex/astra/opp-cybers/)
```
game    ver   map         res  how      endQ u/t  longest u/t  r100 pearls u/t  r100 dragons u/t
1512747 one13 Default     L    longest  0/0       14/45        20/51            9/18
1512748 one13 Trophy      W    elim r75 0/0        3/0         81/17 (r75)      33/0 (r75)
1512749 one13 Portals     L    longest  0/0       24/38        62/50            20/14
1512750 one13 weakhold    W    elim r111 4/0       4/0         57/6             20/1
1512751 one13 Islands     W    longest  0/0       55/24        168/164          54/40
1535558 one18 weakhold    W    elim r195 4/0       4/0         55/6             19/1
1535559 one18 Slithery    L    longest  0/0       26/40        271/258          57/62
1535560 one18 Schooltime  L    longest  3/3       43/44        103/130          34/33
1535561 one18 QueenSpades W    elim r246 7/0       7/0         36/23            11/8
1535562 one18 Devil       W    elim r122 3/0       5/0         112/12           38/1
```
All seat A. By map: weakhold 2/2; every other map 1 game.

Our losses (class):
- 1512747 Default: queen rammed in the open, r120 L4, by an L3 from gap 2 (1 free + 1 paid), two foe heads adjacent, no mate within 4. Their queen was already dead (r76): she only had to live. Also out-eaten from r50 (26/26 at r50, 21 vs 43 at r100).
- 1512749 Portals: queen self-trap (pocket), r228: portal (18,2)->(13,15) at r223, 0 free cells two turns later. Their queen dead since r185. one16's blind-portal rule covers this size [E].
- 1535559 Slithery (one18): queen boxed with a mate, r227: sides = mate, mate, own body; shed 4->2 at r226, L3 foe came 5->3->2 and rammed with the free step.
- 1535560 Schooltime: other. Both queens sealed in a 2x2 cage all game (free 1, 500 rounds); lost longest 43 vs 44.
Our wins: their queen rammed alone in a corner by our L2-L3 from gap 1, free step (weakhold r111 and r167, QoS r212); queen trade r23 then their side rammed out (Trophy); their queen hit her own body (Devil r122); L11 with 3 free steps from gap 3 (Islands r365).
More in the final message by 14:46: their feeding rate, long-dragon rams.

---

## 2026-10-09 05:39:58 — Cybers final: weak yes, longest-dragon race, no constant

FINAL opp-cybers. 5) Another ranked battle vs Cybers: weak YES, per-game 0.60 [M: 6 of 10 games, all seat A, two battles both 3-2, one18 3 of 5]; no new battle on disk at 14:38. It is map luck: 5 of 5 on maps where their side collapses, 1 of 5 where it grows.
Decides it: when they grow level the queens end equal (both dead in 4 games, both sealed at 3 in Schooltime) and the longest dragon decides; from r400 they turn the whole side into one dragon and we do not.
Constant for the last upload: NONE. The only constant pointing that way is RALLY_END_FRESH, already live in one6-one8 and removed after it lost locally (SESSION-STATE lines 547, 595). Nothing else is a value change.

End race [M] (late.py, far.py), the five long games, longest us/them:
```
game     map        r400    r450    end     their own-body deaths r>=400   our dragons left at end
1512747  Default    13/9    14/42   14/45   59                             1
1512749  Portals     8/5    20/34   24/38   34                             8
1512751  Islands    19/20   34/35   55/24 W 55                             52
1535559  Slithery    7/19   23/23   26/40   178                            49
1535560  Schooltime 22/37   37/89   43/44   60                             48
```
- Their feeders die on their own body wherever they are and the leader collects: dragon count 58->15 (Schooltime), 30->1 (Portals), 49->8 (Islands) between r400 and r450. Ours die by stop/wall next to the leader only: at r450 on the three big maps 13 of 39, 21 of 48, 16 of 58 of our others are within 15 of our longest; the rest stay alive and uneaten (Schooltime end: total 327 vs 151, longest 43 vs 44).
- The two closest were decided by one event: Islands won because our L9 rammed their L49 at r497; Schooltime lost by 1 although their L78 died on its own body at r485 and we rammed their L28 at r486.
- Long dragon rammed [M]: ours of 8+ lost to rams: Slithery 8 (r208-r416, by L3-L4 from gap 2), Schooltime 6 (r268-r358); theirs: Slithery 2, Schooltime 11. Our leader at r350 in Slithery (13) was gone by r400 (7).

Their habits [M] (qside.py): first split r0 on 6 of 10 maps, r4-r12 on the rest. Where they grow, the queen drops to L2-L3 at once (Default split r1; Slithery 23 -> 2 by r25) and lives in open cells (1 free cell or less on 0-2% of her turns), 17-23 from her start, 1-2 mates within 4. Where they collapse she stays L4 alone (0.0 mates within 4) and is cornered: our L2-L3, gap 1, free step (weakhold r111, r167; Queen Of Spades r212).
Their kills of our queen: 3 rams, each by an L3 from gap 1-2 with the free step (one paid step, Default r120); she had exactly 1 free cell each time, and in 2 of 3 our own mates filled her sides (Islands r189; Slithery r227 with one18: mate, mate, own body, after shedding 4->2 at r226). Fourth death: Portals r228 pocket after a portal.
Loss classes to add up: queen rammed in the open 1, queen self-trap 1, queen boxed with a mate 1 (one18), other 1 (sealed queens, longest 43/44). In Default and Portals their queen was already dead (r76, r185): our queen living would have won both.

Not checked: why their side collapses on the five small-start maps (deaths there: rammed 2-7, own body 3-8; I did not trace them); what the rating fields mean (+20 for this 3-2; a 2-3 vs a 2151 team showed -36, so expected gain is about zero [E]); no games played, nothing built.
Files: ~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/opp-cybers/ (both-all.txt, late.txt, far.txt, qside-b1.txt, qside-b2.txt, l15-b1.txt, l15-b2.txt).

---

## 2026-10-09 05:39:58 — closing summary

Both messages are with the lead (first at about 14:37, final at 14:39 KST). The final ran over the 25-line limit.

- **Another ranked battle vs Cybers:** weak yes. Per-game win chance is 0.60 from 10 games, all as seat A, across two battles that both ended 3-2; one18 won 3 of its 5. Expected rating gain is about zero, so it is variance rather than value.
- **What decides the games:** whether their side collapses early. Where it did, we won by elimination (5 of 5: weakhold twice, Trophy, Queen Of Spades, Devil). Where they grew level, the queens ended equal and the longest dragon decided; we won 1 of those 5.
- **Why we lose the longest-dragon race:** from r400 they turn nearly the whole side into one dragon (dragon count 58 to 15 on Schooltime, 30 to 1 on Portals between r400 and r450). Ours feed only near the leader, so at r450 on the big maps fewer than half our other dragons are within 15 of it and 48 to 52 are still alive at the end. Schooltime was lost 43 to 44 on longest with total length 327 to 151.
- **Constant for the last upload:** none. The only one pointing the right way is `RALLY_END_FRESH`, which was live in one6 to one8 and removed after it lost locally.
- **Loss classes:**
  - Default: queen rammed in the open.
  - Portals: queen self-trap.
  - Slithery Fight (one18): queen boxed with a mate.
  - Schooltime: other; both queens were sealed in a cage all game.
  
  In Default and Portals their queen was already dead, so ours surviving would have won both.

Not checked: why their side collapses on the five maps we won by elimination, and what the rating-change fields actually measure. No games were played and nothing was built.

Scripts and outputs are in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/opp-cybers/`; `both-all.txt` has the full per-game table.
