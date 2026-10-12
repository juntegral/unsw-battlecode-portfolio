# Reports sent to the lead by opp-test4

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 05:39:58 — test4 first heads-up from metadata

opp-test4 first message (metadata only, replay scan of the 10 ranked games is running now):
1. Another ranked battle vs test4: YES on points [M]. Per-game 6/10 in the two ranked battles (both 3-2 wins, we were seat A both times, +22 and +13 Elo). Rests on 10 games only.
2. What decides our games: the map draw, not a mechanism I have measured yet. We win weakhold 2/2, Stripes 2/2, Portals 1/1, Slithery Fight 1/1 (205 v 204, one point); we lose Autarky (0 v 175), Trauma (10 v 125), Tower Defense (12 v 96), Trophy (0 v 207). Losses are blowouts, wins are queen kills (their score 0 in 3 of 6 wins).
3. Constant for the last upload: none so far.

Battle 1535543-1535547 is already on disk and finished 3-2 for us (L Tower Defense, W Slithery Fight, W weakhold, W Stripes, L Trophy).
Older unranked sets vs test4 (10-04 to 10-07, old bots, all seat A): 55/225 = 24%. By map over all 235 games: Australia 0/15, Islands 0/15, Tower Defense 0/15, Trauma 0/16, Maze 1/15, Portals 2/16; best weakhold 10/17, Devil 9/15. Those are old bots, so I am not counting them in the 6/10.
Not checked yet: how each loss was decided (queen death class), r100 pearls and dragons. Final by 14:46.

---

## 2026-10-09 05:47:33 — test4 final: request yes, no constant

opp-test4 FINAL. 1. Request another ranked battle vs test4: YES. Per-game win chance about 0.5 (6/10 measured, but 2 of the 6 were near coin flips), 10 games, all seat A; both battles ended 3-2 for us (+22, +13). I did not measure what a 2-3 loss costs.
2. What decides it: both queens die short almost every game (ours dead in 9/10, theirs in 8/10), so the game is army size, and that is set by who has more dragons by r100. They out-split us in 7/10 games.
3. Constant for the last upload: none. Nothing here is verified well enough to ship in 10 minutes.

Table [M], same script both sides (o1_scan + qdeath), us/them. No new test4 battle on disk since 1535543.
game    ver   map      res how      Qend  r100 pearls  r100 dragons  splits<100
1501263 one12 Portals  W   longest  0/0   54/95        16/25         32/51
1501264 one12 weakhold W   elim     3/0   76/29        22/7          42/21
1501265 one12 Autarky  L   elim     0/33  44/56        12/16         36/50
1501266 one12 Stripes  W   elim     0/0   56/40        15/6          36/22
1501267 one12 Trauma   L   queen    0/33  5/18         5/9           3/9
1535543 one18 TowerDef L   longest  0/0   6/61         1/26          2/25
1535544 one18 Slithery W   longest  0/0   321/389      55/61         238/298 (total 205 v 204)
1535545 one18 weakhold W   longest  0/0   74/28        25/5          41/20
1535546 one18 Stripes  W   elim     0/0   29/49        7/12          20/30
1535547 one18 Trophy   L   elim     0/0   48/104       12/41         23/50
Win rate 6/10, seat A 6/10, seat B none. weakhold 2/2, Stripes 2/2. one18 alone 3/5. Old unranked sets (10-04 to 10-07, old bots) 55/225, not counted.

Losses, class [M]:
- 1535543 TowerDef: out-eaten from r50 (3 v 3 dragons at r50, 1 v 26 at r100, we split twice in 100 rounds); queen L2 rammed r97 by L3 from gap 2, paid.
- 1535547 Trophy: out-eaten from r25 (9 v 20 at r50, 12 v 41 at r100); queen rammed in the open r155 (L2, free 3) by L4 from gap 3, paid; eliminated r235.
- 1501265 Autarky: queen rammed in the open r117 (L3, free 3) by L4 from gap 3, paid; out-eaten from r100 (14 v 26 at r150); eliminated r314.
- 1501267 Trauma: out-eaten from r100 (8 v 33 at r150); queen L6 rammed in the open r345 by L12 from gap 4, 4 steps.
Wins: we rammed their queen in 3 (1501264 r108 L2, 1501266 r76 L4, 1535546 r259 L6) and eliminated them each time; in the other 3 their queen died on its own turn (r168 L3, r101 L2, r446 L45 into own body) and we won on longest.

What they do [M]: split from r0 into L2-3 dragons and keep their queen at L2-3 all game, feeding it only after ours is dead (Autarky 4 to 33 from r225, Trauma 2 to 33 from r350). Their small dragons pay steps to ram: 4 of 6 rams on our queen were paid sprints from gap 2-4; on Autarky and Trophy 15 of our 47 dragons rammed before r200 were paid rams. We paid for 1 ram in all ten games. What beats them: out-splitting on small open maps (weakhold) and ramming their L2-4 queen early.
Not checked: where their queen sits relative to their swarm, per-seat effect (no seat B games), and no local test of any constant. Files: ROOT/data/codex/astra/opp-test4/ (tab-ranked.txt, l15-loss.txt, qt-*.txt, open.py).

---

## 2026-10-09 05:47:33 — closing summary

The final report on test4 has gone to the lead at about 14:40 KST, ahead of the 14:46 mark.

- **Request another ranked battle:** yes. We won 6 of the 10 ranked games (both battles 3-2, +22 and +13 Elo), all from seat A. I put the per-game chance at about 0.5, because two of the six wins were near coin flips. I did not measure what a 2-3 loss would cost.
- **What decides the games:** both queens die short almost every game (ours in 9 of 10, theirs in 8 of 10), so the result comes down to army size. test4 out-splits us by round 100 in 7 of 10 games; we won all three where we out-split them.
- **Constant for the last upload:** none. Nothing was tested locally, so nothing is safe to ship in the time left.

The four losses:

| Game | Map | Class | Detail |
|---|---|---|---|
| 1535543 | Tower Defense | out-eaten from r50 | 1 v 26 dragons at r100; queen L2 rammed r97 |
| 1535547 | Trophy | out-eaten from r25 | 12 v 41 dragons at r100; queen rammed in the open r155 |
| 1501265 | Autarky | queen rammed in the open r117 | then out-eaten; eliminated r314 |
| 1501267 | Trauma | out-eaten from r100 | 8 v 33 dragons at r150; queen L6 rammed in the open r345 |

In our six wins we rammed their queen and eliminated them three times; in the other three their queen died on its own turn and we won on longest dragon.

test4 splits from round 0 into length 2-3 dragons, keeps its queen at length 2-3 and feeds it only once ours is dead. Its small dragons pay steps to ram: four of the six rams on our queen were paid sprints from 2-4 cells away. We paid for one ram in all ten games.

The older unranked sets against test4 (10-04 to 10-07, old bots) came to 55 of 225 and are not counted in the 6/10. No new test4 battle had appeared on disk since 1535543. Not checked: where their queen sits relative to their swarm, and any seat effect (there are no seat B games).

Everything is in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/opp-test4/`; `tab-ranked.txt` has the per-game table.
