# Red-team report: beating `opponent/bot`

1. Not beaten: my final bot won 17 of 64 eval games (16 maps, both sides, 2 seeds), no draws.
2. Biggest weakness: late on it lets its swarm die to feed one long dragon and can then be eliminated (7 of my 17 wins).
3. Confidence: mechanism measured in replays on 2 eval maps from both sides; win rates are small samples; it is stronger.

Second finding, rarer but never failed once set up: it cannot kill a queen whose head rests inside her own body (W1).

## Weaknesses, ranked by eval games they decided

**W2. Late self-thinning (7 eval wins, 2 maps, both sides, 0 losses of this kind).**
- Measured: in games that run long, its dragon count drops while one dragon grows. `portals_medium_90020` seed 1,
  my side 0: opponent has 59 dragons at r320, 39 at r360, 26 at r440, 5 at r480, gone at r489. At the round limit it
  held 2, 4, 5 and 6 dragons in 4 of the 30 eval games that got there.
- What beats it: nothing special. My swarm keeps splitting to the end (57-60 dragons) and strikes any head in reach.
- How often: 7 elimination wins at r400-r492 (`portals_medium_90020` 4/4, `islands_medium_90000` 3/4), sides 0 and 1.
  Dev: 3 wins of the same kind on `portals_medium_90007` (r474, r481, r484).
- Watch: `runs/eval-final/sqheld_portals_medium_90020/seed-1-A-side-0/game.replay` r320-r489;
  `runs/eval-final/sqheld_islands_medium_90000/seed-2-A-side-1/game.replay` r320-r447 (opponent 50 dragons at r320, 12 at r400, 2 at r440).
- Interpretation: it stops replacing dragons late so that pearls from the dead feed one "banker" for the
  longest-dragon rule. When the banker lives this wins it the game (27 of my losses were "longest dragon", its
  longest was 13-200). It only fails when my swarm outlasts it, which happened on 2 of 10 medium/large maps.

**W1. No answer to a sealed queen (2 eval wins, 2 maps, side 0 only; never lost once closed).**
- Measured rule: a dragon dies only when a head enters its head cell (both die), or when it runs into something.
  The opponent's queen is not protected: it was dead at round 500 in all 30 eval games that reached the limit, and
  in all 36 of its own self-play games that did. A live queen of any length then wins on the queen rule.
- What beats it: a length-23 queen walks a fixed 24-cell cycle on a 6x4 block, 6 steps a turn (her free allowance).
  At each of her four stopping cells her head and the single free cell are surrounded by her own body, so no enemy
  head can become adjacent. Tiles under a body do not spawn pearls, so the length stays 23.
- How often: closed in 2 of 64 eval games, both won "longer queen, 23 to 0": `blobs_large_90030` seed 1 side 0
  (closed r186, held 314 rounds with 47-64 enemy dragons alive) and `portalrooms_large_90006` seed 1 side 0 (closed
  r56). Dev: 2 more, one per side, on `portals_medium_90007`; in one my queen was my only dragon left (23 vs 483).
- Watch: `runs/eval-final/sqheld_blobs_large_90030/seed-1-A-side-0/game.replay` from r186, stops (22,42) (21,43)
  (19,43) (20,42); `runs/eval-final/sqheld_portalrooms_large_90006/seed-1-A-side-0/game.replay` from r56.
- Limit: getting there is the hard part. The queen needs 20 pearls and 24 free quiet tiles with no enemy in view.
  A variant that goes for it from round 0 closed it in 2 of 34 dev games and 0 of 8 supplementary eval games
  (`runs/eval-ringfirst.log`; 2 of those 8 were won, both by late elimination as in W2).

**W3. It trades its queen (enabler for W1, decides no game alone).** Any of its dragons, queen included, steps
into any head in reach, paying segments to lunge 2-3 cells. `runs/s0-open-small/game.replay` r14: its queen dies
that way. `runs/self-open-small/game.replay` r10: both queens die in self-play.

**W4. Crowd losses (not exploited).** It loses dragons without combat in dense games: 350 "hit another dragon",
250 "hit itself", 165 "no valid action" in one 500-round game
(`runs/big-v9/open_medium_90017-s1-side0/engine.log`). I did not find a way to cause these.

## Final evaluation (measured)
My bot = `bot/` (first-named). Wins / games. Opponent self-play on the same games shows side bias.

| size class | my side 0 | my side 1 | self-play: side 0 wins - side 1 wins |
| --- | --- | --- | --- |
| small (6 maps) | 4/12 | 3/12 | 14 - 10 |
| medium (4 maps) | 3/8 | 4/8 | 6 - 10 |
| large (6 maps) | 2/12 | 1/12 | 8 - 16 |
| total | 9/32 | 8/32 | 28 - 36 (of 64) |

- My wins: 14 by elimination (7 on small maps at r34-r258; 7 on medium maps at r400-r492), 2 longer queen,
  1 longest dragon.
- My losses: 20 by elimination (17 small, 3 medium, rounds 31-282), 27 on longest dragon at round 500.
- Maps with at least one win: 8 of 16. 0/4 on `blobs_medium_90034`, `islands_medium_90038`, `open_large_90036`,
  `open_small_90012`, `open_small_90015`, `portalrooms_large_90003`, `portals_large_90010`, `rooms_large_90035`.
- Legality: 0 games with bot runtime errors, 0 "no valid action" deaths on my side in 64 games.
- Self-play: 28 by elimination, 36 at round 500, all 36 on longest dragon with both queens dead. The 64 rows
  are 32 distinct games played twice with identical results. Files: `runs/eval-final/summary.txt`, `runs/eval-self/summary.txt`.

## What did not work (dev maps, wins of games against the opponent)
- One long evasive queen and no swarm: 0/2, eliminated r32 and r63. It has 20-60 dragons by round 25.
- Swarm units that never end a move inside enemy reach: 0/6 three times. They were kept off the rich tiles.
- Trading only at even or better length: 7/24 against 9/24 without; my non-combat deaths rose from 10 to 33.
- Queen fighting as a normal unit on single-dragon maps: 6 of 24 games ended by r13; the two I opened were
  draws, both lone queens dead in one trade (`runs/m-v8/open_small_90018-s1-side0`, r7).
- Hunting every head after r400 and no splitting after r440: 1/10 against 3/10 without; 4 losses by elimination at
  r481-r493. My own swarm died out the way the opponent's does.
- Queen grows to 23 from round 0: 6/34. She died r19-r117 in 32 games, usually to a lunge from outside her 7x7
  view or boxed in by her own body, and the swarm starved without her early splits.
- Keeping out of fights where more enemy than friendly heads are in view: no gain on small maps (7/24 with,
  7/24 without, on different seeds). Kept, with no evidence either way on larger maps.
- Small-map swarm race in general: 7/24 on eval. On `blobs_small` dev (0/16) it ate 2-4 times as many pearls,
  mostly those dropped by dead dragons, because its dragons arrive in groups and mine one at a time.

## Limits
- Samples are small: 2 seeds, and the same seed with the same two binaries replays identically, so "2 seeds" is
  2 games per map and side. W1 rests on 4 closed formations in total, all won.
- W1 closed on eval only as side 0 and only on maps with one starting dragon per side. Not shown on small maps.
- The supplementary ring-first games were played on eval maps after the final bot was frozen; nothing was tuned on them.
- The judge's CPU-point budget is not metered in native games. My bot was not run in the sandbox.
- W1 assumes its queen is dead or short at round 500. That held in 30 of 30 eval games, but in one supplementary
  game its queen was the long dragon and won "longer queen, 254 to 0" (`runs/eval-ringfirst/portals_large_90010-side0`).
  A sealed queen of 23 would lose that game.
- I could not test whether the opponent can be made to attack the sealed queen's body on purpose, nor sonar.
- Possible map quirks: all W2 wins came from two medium maps; the ring needs a 6x4 block of tiles that never
  spawn pearls, which these generated maps have in large patches.
- Side bias (measured): in self-play side 1 won 26 of 40 medium and large games and 10 of 24 small ones. My results
  show no matching side effect (9 wins as side 0, 8 as side 1).
