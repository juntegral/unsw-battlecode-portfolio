# Running notes (times are minutes from start, 14:52:55 KST)

## Rules learned by experiment (not in the docs)
- Moving your head into an enemy head kills BOTH dragons, whatever their lengths (replay `runs/self-open-small`, r35: L4 and L2 both die).
- A dragon of length L may take ceil(L/4) steps free and more by paying one segment per step (min length 2).
  The opponent uses paid steps to lunge: L3 reaches 2 cells, L4 reaches 3 (`runs/s0-open-small` r14, `runs/dbg7` r19).
- Dragons act in id order inside a round; a split child gets the newest id and acts last.
- A dead dragon leaves ceil(L/2) pearls on its cells.
- Stepping onto the cell your own tail is about to leave is "hit itself" (`runs/testloop5` r12). So a closed loop needs
  one free cell.
- A pearl does not spawn on an occupied tile. A tile's countdown is visible; countdown 1 with a pearl on it = spawns
  every round. Many tiles never spawn (type 0/0).
- Unit limit is 64 per team.

## Opponent behaviour (measured)
- Splits 2 off as soon as length 4. Walks onto tiles as pearls spawn. 4 -> 60 dragons by round 25 on open_medium.
- Any dragon incl. queen steps into any enemy head in reach. Queen is not protected.
- Self-play dev (seed 1): small maps end by elimination at r18-62; medium/large go to r500 with both queens dead and are
  decided by "longest dragon" (102-177 long). In the last ~80 rounds it lets its own small dragons die and one "banker"
  eats the pearls: unit count drops from ~57 to 2-4 by r500 (`runs/big-v9/open_medium_90017-s1-side0`, `runs/v12-om-0`).
- It also loses dragons without combat in crowds: in one 500-round game 350 "hit another dragon", 250 "hit itself",
  165 "no valid action", 55 "hit a wall" (`runs/big-v9/open_medium_90017-s1-side0/engine.log`).

## Versions and dev results (wins of games, my bot vs opponent)
| version | change | small maps (open/blobs/islands small, both sides) | larger maps |
| --- | --- | --- | --- |
| v1 | lone evasive queen, no swarm | 0/2 | - |
| v2-v4 | swarm, fearful units | 0/6 each | - |
| v5 | hunt at >=4 units, density targets | 1/6 | - |
| v6 | fountain detection | 1/6 | - |
| v7 | fearless units | 7/24 (seeds 2-5) ; nohunt 8/24 | - |
| v8 | local-superiority rule, queen fights on small maps | 7/24 (nohunt 5/24) incl. draws at r7 | - |
| v9 | never trade the last two dragons | 9/24 (open 5/8, blobs 0/8, islands 4/8) | 5/10 (seed 1) |
| v10 | material-aware trades | 7/24, non-combat deaths 33 vs 11 -> dropped | - |
| v12-v17 | ring queen (see report) | - | queen died r19-r33 before closing the ring |
| v18 | ring queen from round 0, conservative reach | - | 1/6 (seed 1) |
| v19 | queen ends within 1 cell when nothing in view; quiet blocks accepted | - | 2/4 (seed 1); first ring win |
| v20 | graded danger, exact safety check on the ring | - | 2/4 (seed 1), 1/10 (seed 2) |
| v21 | + hunt everything after r400, no split after r440 | 5/20 (run cut short) | - |
| v22 | ring entry steps only onto visible cells | - | 0/10 (seed 2) |
| v23 | ring off, queen seeds swarm (QSW 6), late changes on | - | 1/10 (seed 1), 4 elimination losses r481-493 |
| v24 | v23 without the late changes | - | 3/10 (seed 1) |
| final | v24 + queen grows for the ring only from round 100 | sanity 2/4 (seed 3) | sanity 0/2 (seed 3) |

Ring closed in dev: `runs/big-v19/portals_medium_90007-s1-side0` (r36), `runs/big-v20/portals_medium_90007-s1-side1` (r37).
Queen deaths before the ring (ring-first versions): r19-r117, mostly head-to-head from heads outside her 7x7 view
(`runs/dbg7` r19: L4 lunges 3 cells; `runs/big-v18/blobs_large_90009-s1-side0` r23) or boxed in by her own body.

## Final evaluation commands (started minute 57.5)
./batch.sh bot opponent/bot eval 1,2 runs/eval-final
./batch.sh opponent/bot opponent/bot eval 1,2 runs/eval-self
Summaries: python3 mytools/evalsum.py runs/eval-final/rows.jsonl ; python3 mytools/evalsum.py runs/eval-self/rows.jsonl self

## Final evaluation results (measured, minute 73-77)
My bot (bot/) vs opponent, eval maps, seeds 1,2, both sides: 17/64, no draws.
small 4/12 (side 0) 3/12 (side 1); medium 3/8, 4/8; large 2/12, 1/12.
Wins: 14 elimination (7 small-map r34-r258, 7 medium-map r400-r492), 2 longer queen (ring closed), 1 longest dragon.
Losses: 20 elimination (17 small, 3 medium; r31-r282), 27 longest dragon.
Per map: blobs_large_90030 2/4, blobs_medium_90034 0/4, blobs_small_90028 2/4, islands_medium_90000 3/4,
islands_medium_90038 0/4, open_large_90036 0/4, open_small_90012 0/4, open_small_90015 0/4, portalrooms_large_90003 0/4,
portalrooms_large_90006 1/4, portalrooms_small_90021 1/4, portalrooms_small_90022 1/4, portals_large_90010 0/4,
portals_medium_90020 4/4, portals_small_90029 3/4, rooms_large_90035 0/4.
Opponent self-play (same games): side 0 wins 28, side 1 wins 36 of 64 rows (32 distinct games, each played twice with
identical results). small 14-10, medium 6-10, large 8-16. 28 elimination, 36 round limit (all longest dragon, queens dead).
Supplementary (not the evaluated bot): variants/ringfirst on 4 single-dragon eval maps, seed 1, both sides: 2/8, ring
closed 0/8; in portals_large_90010 side 0 the opponent's queen was alive at r500 with length 254.
