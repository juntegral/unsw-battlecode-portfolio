# [Idea] Ram their queen whenever one of our dragons can reach her

DRAFT, not posted. Written from the top-team study of 5 Oct (`unsw-swarm/data/analysis/top1/REPORT.md`).

What we tried: Nothing built yet. In 1,754 ladder replays we counted every turn on which a dragon had a legal ram on the enemy queen, and whether it took it, for the top three teams and for us.
Did it work: Not tested. The count says Vibing++ and SSS take 98% of such chances with a 2–3-long dragon; we take 36%, and 2% with anything longer.
Who decides now: The team. One OK puts it in the queue. It overlaps #17 and #31, so 준싱 or Zhe should say whether it becomes a new card or a change to #31.

**Idea by:** AI, from the top-team study

**Area:** queen

## Claim

If one of our dragons, at the start of its own turn, has a free path to the enemy queen's head that is no longer than its one-turn reach, it rams her. This applies to every dragon except our queen and our longest dragon, as long as the sprint costs it no more than 2 segments. It holds on every map, in every round, whether or not our own queen is alive. As a second step, a 5–9-long dragon that knows where she is walks to within its reach and strikes from there. At round 500 a living queen beats a dead one every time, and today theirs outlives ours in 37% of our games.

Words:
- **ram**: move a head into another head; both dragons die, whatever their lengths.
- **reach**: how far a dragon can move in one turn: its free steps plus one step per segment it gives up ("paid steps"). Length 2 reaches 1 cell, 3 reaches 2, 4 reaches 3, 5 reaches 5, 6 reaches 6. A dragon sees 3 cells.
- **chance**: a dragon's own turn (so after both queens have moved that round) on which a path of free cells no longer than its reach leads from its head to the enemy queen's head.
- **approach**: one head comes within 6 steps of a living enemy queen (walls and portals respected); it ends when that dragon dies, moves more than 9 steps away, or she dies.
- **top three**: Vibing++, SSS, forgot to mention.

## Evidence

### Measured (ladder replays, opponents rated 2000+, Schooltime left out because both queens are sealed in there)

Chances taken:

| | Vibing++ | SSS | forgot | meow |
|---|---|---|---|---|
| Attacker 2–3 long | 137 of 140 = 98% | 112 of 114 = 98% | 130 of 195 = 67% | 65 of 183 = 36% |
| Attacker 4 or longer | 58 of 224 = 26% | 81 of 309 = 26% | 22 of 241 = 9% | 9 of 466 = 2% |
| At most 1 paid step, attacker not the team's longest | 141 of 150 = 94% | 120 of 125 = 96% | 133 of 215 = 62% | 63 of 187 = 34% |

- We get the chances: at least one in 132 of our 289 games; on maps over 1,200 cells 4.8 chance-turns a game, of which we take 14 of 378.
- What the top three will pay: free steps only 83% taken, 1 paid step 74%, 2 paid 54%, 3 paid 24%, 4 or more 4%.
- Per approach, by attacker length: top three 7.3% (2–3 long), 11.6% (4), 28.0% (5–9) end with her rammed; ours 2.5%, 0.9%, 2.8%. A 5–9-long killer started the fatal round 4 or more steps from her in 86% of its kills. On large maps 46% of top-three queen kills are by a dragon 5 or more long.
- Rams on their queen per game: us 0.32 / 0.24 / 0.18 on small / medium / large maps; top three 0.43–0.54 / 0.36–0.65 / 0.58–0.80.
- Their queen is alive at the end in 41% of our games; against the top three in 18–31%. Against test4, an opponent we share, 48% in our games and 29% in theirs.
- Round-500 games with the own queen dead: if their queen lived, 0 wins of 51 for us and 0 of 108 for the top three. If she was rammed, we won 12 of 30 and they won 156 of 242.
- Game 1029030 (Autarky, loss to WeHaveQuizzes on the queen rule; from round 250 their only dragon is a 2-long queen, we have up to 58 dragons and a 93-long). Seven chances in rounds 227–248, none taken. Round 234: she steps from (39,9) to (38,9), directly in front of our 3-long #267 at (38,10); it moves east. Rounds 236, 238, 240: our 3-long #259 two steps from her with a free path. Round 227: our 6-long #262, four steps.
- From the code: `QUEEN_HUNT` is off. `mark_trade_targets()` needs `round <= feed_round`, at least as many of our other heads in view as enemy heads, and a target at least as long as the attacker (at least `max(5, own length + 2)` parts on maps over 1,200 cells); `is_trader()` lets only dragons 4 or shorter trade. So a 3-long of ours does not ram a 2-long queen, our 5–9-long dragons never ram a short queen, nobody does after the feeding round, and none of these tests knows she is the queen. This matches the table: 60% taken at length 2, 27% at 3, 8% at 4, 1.4% at 5–9.

### Not measured

- Why our dragon did not ram on any particular turn. Ladder replays have no logs; the code reading above fits every number but is not proven turn by turn.
- The effect on wins. Estimate: 5 to 8 more wins in 289 games against 2000+ teams (+2 to +3 points). Strict version: in 37 games we had a chance costing at most 2 paid steps and never rammed her; 9 of those were round-500 losses with her alive; 6 of the 9 flip if she dies and nothing else changes. Looser version (top-three conversion on our approaches): about 8. Trauma and Portals queens sit behind portals and are out of reach; Australia and Islands losses do not flip because we are too far behind on length.
- Rams that only become possible by eating a pearl on the way. My strict test misses them; the top three made 110 queen kills it did not flag.
- What a missed strike costs (a 5-long that sprints 5 steps ends 2 long).
- How top-team hunters find her. Replays show them arriving from 10 or more steps away; they do not show what the sonar said.
- How this interacts with #31's scout-and-ping hunter.
- Local win counts will say little: our local opponents' queen is alive at the end in only 11–20% of games, so there is not much for a kill to change. The earlier local test (hunters of length 4 or less, 2 Oct) was neutral.

## Expected signal

- Share of chances taken (at most 2 paid steps, attacker not our longest) goes from about 30% to above 85%. This is the direct check and it can be counted in any set of replays, local or online.
- Rams on the enemy queen per game go from about 0.26 to 0.4 or more overall, and from 0.18 to 0.4 or more on maps over 1,200 cells.
- Dragons no longer tail her for tens of rounds without striking.
- Online: their queen alive at round 500 falls from about 41% of games to under 30%.
- Our own queen's fate does not change (this idea never moves her).

## What would show it's wrong

- Chances taken stay below 60%: the rule is not firing, and the build is not done.
- Chances are taken but rams on their queen stay below 0.35 a game: she is rammable less often than the ladder count says once opponents react.
- Kills rise but "their queen alive at round 500" does not fall, or round-500 results with our queen dead do not improve.
- Our longest dragon at the end is shorter by more than 2 on average, or we are wiped out more often: hunters are costing more than they bring.
- Our leader, our queen, or a dragon paying more than the cap is seen ramming her.

## Test plan

1. **Build**, default off. Step 1, "strike": the enemy queen's head is a ram target for any non-queen, non-leader dragon that has a free path to it within its reach at a cost of at most 2 paid steps (`QUEEN_HUNT` path in `mark_hunt_targets()` / `hunt_path()`, plus an exception in `mark_trade_targets()`; no map-size, round or head-count condition). Step 2, "walk in", separate toggle: a 5–9-long dragon with a sighting at most 8 rounds old and at most 8 steps away routes to her (`QUEEN_CHASE_DIST`, `QUEEN_CHASE_FRESH`, new minimum length). Toggle off must be replay-identical on the old 10 maps.
2. **Behaviour check with replays** (small local run, each step on its own). Count chances and chances taken with the counting class in `unsw-swarm/data/analysis/top1/extract3.py`; it needs only a replay path, so it works on local replays too. Keep three replays: a 3-long taking a one- or two-step ram, a 5-long or longer striking from 4–5 steps, and one chance that was not taken (to see why). If a dragon with a chance still moves away, the build is not done.
3. **Sparring pool, including the queen hunter.** Usual held-out, transposed and old-10 sets. Read it for harm, not for gain: wins not down by 9 or more on any set, our longest and total at the end unchanged, eliminations not up. If the pool has an opponent whose queen normally lives to the end, add it, so that a kill can change a result at all; against that opponent queen-rule losses should drop.
4. **Online 30:30 comparison** (`tools/smoke.py pair`, same teams and maps for base and candidate). Judge on the mechanism: chances taken, rams on their queen per game, their queen alive at round 500, and the round-500 table by queen state. Report wins too, but 30 games each cannot show a 2–3-point change (noise is about 12 points), so wins alone neither pass nor fail it.
