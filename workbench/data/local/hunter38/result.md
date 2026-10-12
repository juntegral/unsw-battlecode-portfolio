# Card #38 QUEEN_LOOP against a queen-hunting spar

Finished 2026-10-07 00:20 KST. 17 maps x 4 games per arm (seeds 3000-3001, both starting sides), 68 pairs. Both arms play the same opponent: main 0e03867 with QUEEN_HUNT=true and QUEEN_CHASE_DIST=8. Switch off = main 0e03867; switch on = main 0e03867 + card #38 (c1c2c29) with QUEEN_LOOP=true.

## Games

|  | switch off (base) | switch on (candidate) |
|---|---|---|
| wins | 35 of 68 | 31 of 68 |
| wins starting as side 0 | 20 of 34 | 17 of 34 |
| wins starting as side 1 | 15 of 34 | 14 of 34 |
| games we were wiped out | 7 | 7 |
| games the hunter was wiped out | 7 | 9 |
| mean rounds | 439.2 | 431.2 |
| ended by elim (wins of games) | 7 of 14 | 9 of 16 |
| ended by longest (wins of games) | 25 of 49 | 22 of 46 |
| ended by queen (wins of games) | 3 of 5 | 0 of 6 |

Paired flips (same map, seed and side): switch on won where switch off lost in 5 pairs, lost where switch off won in 9 pairs.
Won only with the switch on: around_unsw 3000/0, default 3001/1, devil_v0 3001/1, queen_of_spades 3001/0, stripes 3000/1.
Won only with the switch off: around_unsw 3001/1, australia 3001/0, devil_v0 3000/0, devil_v0 3001/0, islands 3000/1, maze 3001/1, queen_of_spades 3000/1, trauma 3000/0, trauma 3001/0.

## Our queen (work/card_38_check.py on the kept replays)

|  | switch off (base) | switch on (candidate) |
|---|---|---|
| queen alive at the end | 9 of 68 | 12 of 68 |
| queen deaths (before r300) | 59 (53) | 56 (48) |
| rammed by an enemy head | 28 | 24 |
| of those right after a lap step | 4 | 1 |
| deaths by cause | wall 16, self 7, body 1, headon 33, none 2 | wall 12, self 9, body 2, headon 31, none 2 |
| mean death round | 98.7 | 130.7 |
| loop share (lap steps per queen decision before r300) | 23.9% (1868 of 7801) | 59.1% (5605 of 9483) |
| loops, lap steps per loop | 331, 8.4 | 389, 16.7 |
| on the loop with a seen head inside reach + 1 of her square | 31 decisions | 84 decisions |
| of those, she took the next lap step anyway | 15 | 39 |
| same by the real enemy length (went on / decisions) | 9 / 21 | 21 / 52 |
| push-offs (followed by a lap step near the pusher) | 16 (6) | 45 (12) |
| alive at r100 / r200 / r300 | 29 / 14 / 14 | 37 / 22 / 16 |
| queen pearls eaten before r300 | 255 | 230 |

The check's own verdict: passed = True. Its pass rule was fixed for games against main (does she loop, does she step off); here it is shown for reference only, and the deaths and rams above are raw counts.

## Per map

| map | off wins | on wins | off queen alive | on queen alive | off rammed | on rammed | on loop share |
|---|---|---|---|---|---|---|---|
| default | 3/4 | 4/4 | 1 | 0 | 2 | 3 | 21.6% |
| trauma | 2/4 | 0/4 | 3 | 4 | 1 | 0 | 95.8% |
| queen_of_spades | 2/4 | 2/4 | 1 | 0 | 1 | 4 | 44.5% |
| schooltime | 1/4 | 1/4 | 4 | 4 | 0 | 0 | 97.3% |
| portals_v0 | 3/4 | 3/4 | 0 | 0 | 0 | 0 | 16.7% |
| slithery_fight_v0 | 2/4 | 2/4 | 0 | 0 | 0 | 0 | 0.0% |
| autarky_v0 | 2/4 | 2/4 | 0 | 0 | 0 | 0 | 0.0% |
| devil_v0 | 2/4 | 1/4 | 0 | 0 | 2 | 2 | 53.1% |
| prisoners_dilemma_v0 | 1/4 | 1/4 | 0 | 0 | 0 | 0 | 0.0% |
| trophy | 2/4 | 2/4 | 0 | 1 | 4 | 2 | 41.7% |
| around_unsw | 2/4 | 2/4 | 0 | 0 | 3 | 4 | 66.4% |
| australia | 2/4 | 1/4 | 0 | 0 | 4 | 3 | 75.1% |
| islands | 3/4 | 2/4 | 0 | 0 | 4 | 3 | 29.7% |
| maze | 2/4 | 1/4 | 0 | 0 | 0 | 2 | 49.7% |
| stripes | 2/4 | 3/4 | 0 | 3 | 3 | 0 | 40.8% |
| tower_defense | 2/4 | 2/4 | 0 | 0 | 1 | 1 | 28.2% |
| weakhold | 2/4 | 2/4 | 0 | 0 | 3 | 0 | 71.2% |

By map size (the check splits at 600 tiles):

| group | pairs | off wins | on wins | off queen alive | on queen alive | off rammed | on rammed |
|---|---|---|---|---|---|---|---|
| small | 24 | 12 | 12 | 0 | 3 | 9 | 3 |
| big | 44 | 23 | 19 | 9 | 9 | 19 | 21 |

## The check's note

QUEEN_LOOP shown on 68 paired games. Loop share (lap steps per queen decision before r300): switch off 23.9% (1868 of 7801) -> switch on 59.1% (5605 of 9483); with the three lead-in steps of each loop 34.9% -> 70.1%; loops 331 -> 389, lap steps per loop 8.4 -> 16.7. Quiet decisions (2-3 long, away from spawn, no enemy head seen, no pearl within 4 steps): 2666 -> 4336, of those lap steps 229 -> 3594. Share of her decisions before r300 at length 2-3: 95.4% -> 95.9%. Tiles her head stood on per 100 decisions: 49.6 -> 24.7. Stepping off: on the loop with a seen head inside reach + 1 of the square, switch off 31 decisions, went on in 15 -> switch on 84 decisions, went on in 39; by the enemy's real length 52 decisions, went on in 21 (she could not tell in 0). Why she left the loop, switch on: {'tight': 45, 'pearl': 70, 'blocked': 15, 'foe_seen': 15, 'other': 47}. Push-offs 16 -> 45, followed by a lap step near the pusher 6 -> 12. Square placement, lap steps in steady loops (8+ lap steps in a row) 2228 -> 5878: within 4 of spawn 2173 -> 2173, portal on or beside 8 -> 26, taken 4+ long 0 -> 0; all lap steps 2785 -> 6510: within 4 of spawn 2446 -> 2424, pearl on or beside 168 -> 242 (not gated). Not gated, 68 games each: queen deaths 59 -> 56, rammed by an enemy head 28 -> 24 (right after a lap step 4 -> 1), alive at the end 9 -> 12, mean death round 98.7 -> 130.7, queen pearls eaten before r300 255 -> 230, team pearls by r100 per game 179.0 -> 179.5, wins 35 -> 31, pairs where the queen did exactly the same with the switch on and off 26 of 68

## Next to QWQ's numbers

QWQ's QUEEN_MARGIN run used the same 17 maps, 4 games per map and SEED0=3000; there the base won 36 of 68 against the hunter. His base and hunter were built from main fa61861; here both are built from main 0e03867, so the switch-off arm is the like-for-like line, not an exact repeat.

Files: hunt.json (all game rows), rows/ (per map), replays/, check.json, check.log, run.log.
