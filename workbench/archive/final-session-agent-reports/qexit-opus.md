# Reports sent to the lead by qexit-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 02:25:51 — qexit heads-up: one-way deaths, switch built

qexit-opus heads-up (11:27): of 286 deaths of our queen in 368 one11-one14 games (she is alive at the end in only 82), 205 are enemy rams and 131 come out of a one-way place (she had 0 or 1 free cell at her last turn start: 60 rammed after the forced step, 71 die on her own move); a mate taking her last cell is down to about 12, so mates are no longer the main class.
Built QUEEN_ONE_EXIT (int, 0 = off, all-off hash 92fb69564fbd OK) in ~/meow-redteam/solo/src/w-qexit/main.cpp: the real queen refuses a step whose landing cell has exactly one way on while a visible enemy head is within N of that way, if another open step exists that is not riskier; testing value 4 on/off against mNps now, NOT verified yet (the shared two game slots are slow), so treat as not ready until my report at 12:00.

---

## 2026-10-09 02:51:29 — qexit final: classes counted, QUEEN_ONE_EXIT not ready

qexit-opus FINAL (11:52): QUEEN_ONE_EXIT is built and fires as designed but is NOT ready to go live; no CONST change to offer.
Found [M]: 286 queen deaths in 368 one11-one14 games (225 unranked + 143 ranked; she is alive at the end in 82). 205 are enemy rams, 131 start from a one-way place (0 or 1 free cell at her last turn start). Mates closing her exit is now small (about 12-23 of 286, see below).
How sure: class counts high (full replay reconstruction, deduped); the switch's benefit unproven: 13 on/off pairs, targeted class 5 v 5.

HASH: all-off bots/qx_off = 92fb69564fbd OK. Test bot bots/qx_onew = one14 switches + QUEEN_ONE_EXIT:4 (582d50019d76). Source ~/meow-redteam/solo/src/w-qexit/main.cpp, diff ROOT/data/codex/astra/qexit-opus/qexit-opus.diff (79 lines, all inside keep_out_of_pocket, so it needs POCKET_KEEP_OUT on).
RULE [C]: the real queen refuses a step whose landing cell has exactly one way on while a visible enemy head is within N walkable cells of that way (bounded ring walk, N=4, at most 41 cells), if another open step exists that is neither a pocket, nor one-way-with-head, nor of higher reach risk; unknown portals are not taken as the alternative.

CLASSES [M] (free cells = unoccupied, unwalled neighbours of her head)
205 enemy head rams her: 152 with 2+ free cells after her last move, 41 with 1, 12 with 0. Attacker inside her 7x7 at her last turn start 158, only in a mate's view 19, unseen 28. Paid steps 140, free 65. Most common: 3 away, she steps to 2, L3 pays one step; and 2 away, she steps to 1.
   her last step (my ring: 2 = inside free steps, 1 = inside paid reach up to 4, torus distance):
   58 she had no other free cell | 53 every free cell was in reach | 12 a clean cell existed, not taken
   50 she stood outside the ring and was hit anyway (33 attacker unseen) | 18 she split that turn | 14 multi-step moves
69 boxed at her last turn start, dies on her own move (33 her own step left 0 free cells, 18 her split did, 16 she rams the head at the mouth). Walls of the box: own body + kelp only 30, enemy head 13, mate L2-3 16, mate L4+ 7, enemy body 3.
   a mate TOOK her last free cell between her last two turns: 2 (STRICT/KEEP hold); mate L4+ as part of the box: 7.
others: 6 she rams a head with a free cell left, 3 a mate's head rams her, 2 stop/timeout.
Length at death: L2 133, L3 89, L4 30, L5 9, L6+ 25. Rounds: under 100 87, 100-199 91, 200+ 108. After their queen was dead 94.
One-way 131: one turn earlier she had 1 free cell in 72, 2+ in 41, 0 in 18: mostly she is already deep in the lane.
WHY LIVE SWITCHES MISS [C, base main.cpp 8170-8196, 940-1046]: the reach rings (QS_PAY_REACH 4, REACH_EATS, FAR_HEADS) only penalise a step when a lower-risk OPEN step exists; in 111 of 172 single-step ram deaths none existed, the decisive turn is earlier. POCKET_KEEP_OUT rejects only 0 ways on; CORRIDOR_GUARD only a proven dead end with no unknown edge; neither looks at a head near the mouth.

OFFLINE [M], 225 unranked games, true boards, plain distance 4: the condition with another non-one-way step open happens 346 times = 1.54 per game = 0.70% of her turns; inside her last 4 turns before 28 of 81 one-way deaths and 14 of 100 other deaths. It overstates: it counts steps next to an enemy head as available, which the switch refuses.

GAMES [M]: on (qx_onew) and off (qx_base) v mNps, same map, seed, side, 13 pairs. Games are deterministic: 6 pairs identical, 7 diverge, first different action is dragon 0 or 1 every time.
map (side)            pearls r100 off>on  dragons r100  queen dies off>on   result off>on
gx_islands 24x12 (0)      100>111           18>26        r282>r75            loss>win
gx_ring 24x12 (1)          64>93             3>15        r78>lives           loss>win
gx_rooms 24x12 (1)         64>60            10>9         r24>r53             loss>loss
gx_rotation 24x12 (1)      27>13             0>0         r41>r43             loss>loss
ladder_australia (1)       64>64            18>18        r361>r239           loss>win
ladder_islands (1)        203>203           37>37        r180>r184           loss>loss
ladder_queen_of_spades(0)  30>22             9>10        r219>r34 (one-way)  loss>win
identical: gx_corridors, gx_open, gx_poor, gx_rich, ladder_maze, ladder_portals (pearls 105, 128, 0, 1753, 76, 207)
Totals off>on: wins 4>8, queen alive at r100 6>5 games, at r200 4>3, at end 1>2, queen deaths 12>11, one-way deaths 5>5, pearls r100 2821>2835, dragons r100 211>231.
Against your bar: targeted class not lower (5 v 5), survival at r100/r200 one game lower, pearls down more than 10% on rotation and queen_of_spades (small counts). No head to head v mNps on 16 maps both sides: no time. 4 losses turned into wins and none the other way, but 7 diverging games prove nothing.
WRONG IF: more pairs keep one-way deaths level or her death round earlier (3 earlier, 2 later, 2 same here). In queen_of_spades ON she is still walked into the lane by an L3 head: at r31 and r33 both her steps were bad, so a one-step refusal cannot fix it; the real fix is distance from a visible head two or more turns earlier (not built).
LEFTOVERS: I could not delete (rm denied by the safety check) solo/runs/qx_base/ and solo/runs/qx_one4/ (3 folders each, only a play.log inside, no games); solo/runs/qx_one4_r holds one game of an earlier plain-distance build. Bots qx_one3, qx_one4 are earlier builds, ignore. Scripts and tables: ROOT/data/codex/astra/qexit-opus/ (qdeath.py, classify.py, opts.py, oneway.py, cond.py, cmp.py, cmp-onew.txt).

---

## 2026-10-09 03:00:38 — closing summary

`QUEEN_ONE_EXIT` is built and fires as designed, but it is **not ready to go live**, and I have no `CONST:value` to offer instead. The final report went to the lead at 11:52; all game processes of mine are stopped.

## What the deaths look like
I counted 286 deaths of our queen in 368 one11–one14 games (225 unranked, 143 ranked); she is alive at the end in only 82.

- **Enemy rams: 205.** The attacker was inside her 7x7 at her last turn start in 158 of them, and 140 used paid steps.
- **One-way places: 131.** She had 0 or 1 free cell at her last turn start. This is the largest class no live switch covers, and it overlaps the rams (60 rammed after the forced step, 71 died on her own move).
- **Boxed and died on her own move: 69.** The walls were her own body plus kelp in 30, an enemy head in 13, a mate of 2–3 in 16, a mate of 4+ in 7, an enemy body in 3.
- **Mates taking her last cell: 2.** So `QUEEN_EXIT_STRICT` and `QUEEN_EXIT_KEEP` hold; mates longer than 3 are not the main problem.

The reach rings only penalise a step when a lower-risk open step exists. In 111 of the 172 single-step ram deaths none existed, so the decisive turn is earlier than her last one.

## The switch
`QUEEN_ONE_EXIT` (int, 0 = off) makes the real queen refuse a step whose landing cell has exactly one way on while a visible enemy head is within N walkable cells of it. She only refuses if another open step exists that is not riskier. It lives inside `keep_out_of_pocket`, so it needs `POCKET_KEEP_OUT` on.

- **Hash:** all-off `bots/qx_off` = `92fb69564fbd`, equal to the base.
- **Test bot:** `bots/qx_onew` = one14 switches + `QUEEN_ONE_EXIT:4`.

## Test against mNps
I ran 13 on/off pairs, same map, seed and side. Games are deterministic: 6 pairs were identical and 7 diverged.

| Measure | Off | On |
|---|---|---|
| One-way deaths (the targeted class) | 5 | 5 |
| Queen alive at r100 (games) | 6 | 5 |
| Queen alive at r200 (games) | 4 | 3 |
| Queen alive at end (games) | 1 | 2 |
| Wins | 4 | 8 |
| Pearls by r100, total | 2821 | 2835 |
| Dragons at r100, total | 211 | 231 |

- **Pearls per map:** down more than 10% on two maps, gx_rotation (27 to 13) and queen_of_spades (30 to 22); both are small counts.
- **Not run:** the head to head on 16 maps both sides; the two shared game slots were too slow.
- **Wins:** four losses turned into wins and none the other way, but seven diverging games prove nothing.

In queen_of_spades with the switch on, an L3 head still walked her into the lane: both her steps were already bad two turns before she died. A one-step refusal cannot fix that; keeping distance from a visible head two or more turns earlier would, and that is not built.

## Leftovers
- **Not deleted:** the safety check denied the removal of `solo/runs/qx_base/` and `solo/runs/qx_one4/`. Each holds three folders with only a `play.log`, no games.
- **Ignore:** `solo/runs/qx_one4_r` (one game of an earlier build) and the bots `qx_one3` and `qx_one4`.
- **Moved aside:** the stale 01:53 copy in my source folder is now `main.cpp.stale0153`.

Files are in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/qexit-opus/`:
- qexit-opus.diff
- cmp-onew.txt
- qdeath.py
- classify.py

Source: `~/meow-redteam/solo/src/w-qexit/main.cpp`
