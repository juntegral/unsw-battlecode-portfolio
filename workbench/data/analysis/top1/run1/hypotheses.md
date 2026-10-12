# Candidate hypotheses from the top-team study

Written by the lead session (the sub-session command is blocked by the loop guard; see REPORT.md, "Limits").
Inputs: the gap tables (`gap2_*.txt`, `qan_*.txt`), `deep-read.md`, the checks in `redteam_checks.txt`, `an2_kills.txt`,
and the scripts named under each item. All numbers are from ladder replays: 1,754 games (1,170 top-team games, 586 of ours),
opponents rated 2000 or more, and the map Schooltime left out of every queen number (both queens are sealed in there and always live).

Words used:
- **queen**: each team's lowest-id dragon. At round 500 the longer living queen wins; a dead queen counts as 0; if equal, the longest dragon wins.
- **ram**: moving a head into another head. Both dragons die, whatever their lengths.
- **reach**: how far a dragon can move in one turn, ceil(L/4) free steps plus one step per segment it gives up: length 2 = 1 step, 3 = 2, 4 = 3, 5 = 5, 6 = 6.
- **approach**: an enemy head comes within 6 steps (walls and portals respected) of a living queen. It ends when that dragon dies, moves more than 9 steps away, or the queen dies.
- **top three**: Vibing++ (306), SSS (91), "forgot to mention" (264).

The base fact all five rest on (script `endstate.py`): in top-team games that reach round 500, "own queen alive, theirs dead" won 146 of 146, and "own dead, theirs alive" won 0 of 108. Against teams rated 2000+, our queen is alive at the end in 10% of games and theirs in 41%; for the top three it is 28–41% and 18–31%.

---

## H1. Ram the enemy queen whenever one of our dragons can reach her, and let 5–9-long dragons do the hunting

**Claim (general rule).** If the enemy queen's head is within the one-turn reach of any of our dragons that is neither our queen nor our longest dragon, that dragon rams her, as long as the sprint costs it no more than about 2 segments. This holds on every map, in every round, at any attacker length. A dragon of length 5–9 that knows where she is moves to within its reach and strikes; it does not need to get next to her.

**Evidence.**
- Turn by turn (`extract3.py`, `an3.py`, added after the red team asked for a stricter count): a "chance" is a dragon's own turn on which a path of free cells no longer than its reach leads from its head to the enemy queen's head. With a 2–3-long attacker Vibing++ takes 137 of 140 chances and SSS 112 of 114 (98%), forgot 130 of 195 (67%), we 65 of 183 (36%). With an attacker 4 or longer: 26%, 26%, 9%, and 2% for us (9 of 466). For chances that cost at most one paid step and do not use the team's longest dragon: 94%, 96%, 62%, 34%. At least one such chance came up in 132 of our 289 games.
- Kills per game (rams on the enemy queen): top three 0.43–0.54 on small maps, 0.36–0.65 on medium, 0.58–0.80 on large; we get 0.32, 0.24, 0.18 (`misc.py` E).
- We get near her as often as they do. Our dragons make 9.7 approaches per game (6.9 small, 14.2 medium, 9.4 large). What differs is what happens next (`approach.py`, `approach3.py`):

| Attacker length at the start of the approach | Top three: approaches ending with the queen rammed | Us |
|---|---|---|
| 2–3 | 473 of 6,514 = 7.3% | 65 of 2,559 = 2.5% |
| 4 | 37 of 319 = 11.6% | 1 of 109 = 0.9% |
| 5–9 | 69 of 246 = 28.0% | 3 of 108 = 2.8% |
| 10+ | 32 of 137 = 23.4% | 2 of 41 = 4.9% |

- The length effect is in each top team separately (5–9-long: Vibing++ 27%, SSS 38%, forgot 17%; 2–3-long: 9%, 7%, 6%), in teams outside the top three (20–22% vs 5–10%), on every map with enough cases (Around UNSW 42% vs 8%, Australia 33% vs 6%, Islands 20% vs 4%, Slithery Fight 28% vs 10%, Maze 19% vs 9%), and when restricted to short queens before round 300 (42% vs 8%) (`approach2.py`).
- Why length matters: a 2–3-long killer started the fatal round 1–3 steps from her in 83% of its kills; a 5–9-long one started 4 or more steps away in 86% (`approach3.py`). She sees only 3 cells. On large maps 46% of top-three queen kills are by a dragon 5 or more long (small and medium maps: 4% and 9%).
- On large maps before round 150, with our own queen still alive, we had 180 approaches and 0 kills (`approach2.py` C5).
- Round by round: their queen is inside the reach of one of our heads for 10.2 rounds per game on maps over 1,200 cells (the top three have that for 5.8–7.7 rounds) and we ram her in 11 of 1,000 such rounds; they do in 34–90 (`redteam_checks.py` R4).
- In our 51 round-500 losses where their queen lived and ours did not, one of our heads could see her for a median of 80 rounds.
- Close read: Vibing++ killed the enemy queen in 8 of 15 games, 6 of them with a dragon 5–13 long sprinting 4–6 steps; in game 1053751 a 3-long killed a 76-long fed queen at round 448 and turned a queen-rule loss into a win; in 1056710 a 13-long did the same to a 31-long queen at round 469.

**Mechanism.** The queen rule is decided by one dragon per side, and a ram kills it at any length. Against us their queen survives 41% of games, so 59 of our 289 games were round-500 losses with their queen alive. Killing her moves the game to "both queens dead, longest decides" (we win 28% of those) or, if ours is alive, straight to a queen-rule win. In top-three games that were even at round 150 (total lengths within 20%) and in which they lost their own queen to a ram, they won 18% (7 of 38) when they did not ram hers and 65% (31 of 48) when they did; when behind at round 150 it was 7% (8 of 107) against 31% (31 of 100).

**Why we don't do it now (code).** `QUEEN_HUNT` is off, so `mark_hunt_targets()` never marks her. On maps over 1,200 cells `mark_trade_targets()` only allows a ram on a head with at least `max(5, own length + 2)` visible parts, and the ordinary hunt needs 10 parts; a 2–3-long queen never qualifies. On smaller maps a dragon may ram a head at least as long as itself, so a 3-long still does not ram a 2-long queen. Everywhere, only dragons 4 or shorter trade (`is_trader()`), and no ordinary trade is allowed after the feeding round. By the strict turn-level count we take 22% of our chances on maps up to 1,200 cells (top three 40–80%) and 4% on larger maps (top three 28–31%).

**Expected effect.** Kills per game from 0.26 to about 0.4 with the approaches we already make (large maps 0.18 to about 0.45, medium 0.24 to 0.41, small unchanged), more if 5–9-long dragons also walk to her. Wins: of our 59 round-500 losses with their queen alive, 30 would flip if she died and nothing else changed. By the strict turn-level count, 9 of the 59 had a legal ram costing at most 2 paid steps that we never took, and 6 of those 9 flip. By the looser approach count, 11 of the 30 flip-games had an approach, and top-three conversion on them gives about 8. So 5 to 8 extra wins in 289 games, +2 to +3 points against 2000+ teams. The gain sits on maps where she is reachable and our economy is in range (Slithery Fight, Prisoners Dilemma, Queen Of Spades, Maze, weakhold, Default, Autarky). It will not rescue Australia or Islands (0 of 12 flip: we are too far behind on length), nor Trauma and Portals (16 flips, but she sits behind portals and we were almost never within 8 steps of her).

**What changes in `mybot2/main.cpp`.**
- `QUEEN_HUNT = true`; in `mark_hunt_targets()` also skip `is_leader()`; `QUEEN_HUNT_MAX_LEN` about 9; `QUEEN_HUNT_STEPS` stays 12 (`hunt_path()` already searches up to `sprint_reach()`).
- In `mark_trade_targets()`: the enemy queen's head always counts as `worth`, with no unit-count or local-edge condition and no map-size condition.
- Second step: `QUEEN_CHASE_DIST` about 8 with a new minimum length of 5 for chasers, so only dragons that can strike from range walk to her (uses `enemy_queen_pos`, already shared by sonar).

**What would show it is wrong.**
- Kills of the enemy queen per game do not rise in replays (below 0.35 overall, or below 0.3 on maps over 1,200 cells).
- Kills rise but "their queen alive at round 500" does not fall below about 30%, or our win rate in round-500 games does not move.
- Our longest dragon at the end gets shorter by more than 2 on average (hunters wasted), or eliminations against us go up.

---

## H2. Dragons near our queen ram small enemies that come for her

**Claim.** When an enemy head of length 4 or less is within its reach of our queen (or will be next round), the nearest of our non-queen dragons that can reach that head rams it, at any map size.

**Evidence** (`defend.py`, `qan.py intr`).
- Per small-enemy approach to the queen, top-three defenders ram the intruder 13–17% of the time; ours 5%. With 3 or more allied heads within 6 steps of the queen it is 24–27% for them and 13% for us.
- With 3+ allies near, a top-three queen is rammed by that intruder in 2–4% of approaches (0 allies: 7–10%) and dies in any way during the approach in 7–9% (0 allies: 22–24%). For our queen allies make no difference: 10.4% with 3+ allies, 10.8% with none.
- Per approach our queen is rammed by the intruder 9.6% of the time; theirs 5.3–6.7%.
- Close read: in 1058916 two SSS 2-longs that came within 2 steps of the Vibing++ queen were rammed by own 2- and 3-long dragons.

**Mechanism.** One small dragon for one small dragon is an even trade on length, but the intruder threatens the one dragon that decides the queen rule.

**Expected effect.** If our queen died per approach as rarely as a top-three queen (23% → 13–19%, all causes), she would survive rams to the end in roughly 15 more games per 100; with 73 round-500 losses where both queens died, that is about 8–10 wins in 289 games (+3 points). Mostly on medium and large maps.

**Code.** `guards_big_ally()` with `QUEEN_DEFEND_RADIUS` (tested at 4), and the same `worth` test in `mark_trade_targets()`; `is_trader()` caps defenders at length 4.

**What would show it is wrong.** "Intruder rammed by a defender" does not rise above 10% of approaches; or it rises and the queen's death per approach does not fall; or her self-inflicted deaths go up because allies crowd her.

---

## H3. Our queen must never die by her own move

**Claim.** The queen never makes a move that kills her (into kelp, her own body, another body, or a head), on any map; she does not enter a cell she cannot leave, and she never takes part in pocket harvesting or equal trades.

**Evidence** (`selfdeath.py`, `qmap.py`).
- Our queen dies by her own move in 81 of 289 games (28%): kelp 35, another body 23, a head she rammed 12, her own body 11. Top three: Vibing++ 4.0%, SSS 11.6%, forgot 4.7% (Vibing++ and forgot also have 23% and 8.5% "no action" deaths, which include deliberate ones, so SSS is the fair comparison).
- In 75 of the 81 she had no free neighbour cell at the start of the fatal round; a small enemy was within 3 steps in only 13. She was 2–3 long in 74. 58 happened on a cell with one or two open sides.
- 49 of the 81 were on maps of 600 cells or fewer, where our queen rules are switched off (`QUEEN_MIN_CELLS`).
- Portals: 19 of 19 games, 9 of them at round 9–10. No queen of either the top three or us was rammed on Portals; top-three queens are alive at the end in 48% of games there, ours in 0%. Slithery Fight: 12 of 21, 7 of them at round 3. Maze 10 of 19, weakhold 8 of 19, Tower Defense 7 of 16.
- 22 of these games were round-500 losses with both queens dead: each would have been a queen-rule win had she lived.

**Mechanism.** Every such death hands over the queen rule for free.

**Expected effect.** About 9 wins in 289 games (+3 points) if she stopped crashing and then survived as often as a top-three queen on the same map; half of that is Portals.

**Code.** `is_queen()` and `QUEEN_MIN_CELLS`; `harvestable()`, `is_trader()`, `escape_child_size()`; cards #23 (`QUEEN_NO_TRAP`) and #25 (`QUEEN_WAIT`) already work here.

**What would show it is wrong.** Self-inflicted queen deaths stay above 15% of games; or they fall and rams on her rise by the same amount (she only dies later).

---

## H4. Keep the queen in the quiet rear of our own swarm

**Claim.** The queen prefers cells where the count of enemy heads seen recently is lowest and allied heads are many, i.e. she lives behind our own front.

**Evidence** (`an2.py crowd`, close read game 1056022).
- On large maps the SSS queen has about half as many enemy heads within 8 cells as the average SSS dragon (ratio 0.47–0.58) and as many allies as the average (ratio 1.0; 4.3 within 6 cells). SSS has the best queen survival of the three (alive at round 200: 76–79% at every map size; end: 41%).
- Vibing++ does not do this (enemy ratio 0.6–0.8, ally ratio 0.6–0.7). forgot's enemy ratio falls from 0.85 to 0.5 only after round 200, when its queen is being fed away from the swarm (ally ratio 0.4–0.6). Our own ratios are already 0.6–0.75 for enemies and about 1.0 for allies.
- In absolute terms our queen has 1.3 enemy heads within 8 cells at rounds 100–200 on large maps; SSS 0.6, forgot 0.7, Vibing++ 1.1. But our whole team has more enemies around it (1.7 against 1.0–1.3).

**Mechanism.** Fewer approaches means fewer chances to be rammed.

**Expected effect.** Unknown; at best SSS's survival, which is 13 points above Vibing++'s.

**Code.** `zone_queen()`, `QG_SAFEZONE`, `QG_CORNER` (card #16).

**What would show it is wrong.** Approaches per 100 queen-rounds do not fall, or self-inflicted deaths rise.

---

## H5. Send small dragons to ram the enemy's longest dragon late in the game

**Claim.** After round 400, dragons of length 3–9 ram the enemy's longest dragon when it is in reach.

**Evidence** (`cf.py`, `an2.py leader`).
- In top-three round-500 games decided by the longest dragon, the side that alone rammed the other's leader (20+ long) after round 400 won 51 of 55; the side that alone lost its leader won 9 of 53.
- 28 of our 73 "both queens dead" round-500 losses would flip if their longest had died at the end.
- But we already do this as well as they do: with their leader in reach of one of our heads we ram it 20 times per 1,000 such rounds, the top three 22–34; they get 12–17 such rounds per large-map game, we get 13. Our kills per large-map game are 0.35 against 0.54–0.63.

**Expected effect.** Small; there is no conversion gap to close.

**Code.** `HUNT_*`, `END_HUNT_*`, `mark_hunt_targets()`.

**What would show it is wrong.** Already shown: equal conversion.

---

## Not re-proposed

**The big-map economy.** It is the largest gap (large maps, round 200: 37 units and 112 total length for us; 53–58 units and 168–194 for the top three; our units fall after round 150, theirs hold near 60 until round 300). It is already known, tracked in card #7, and card #14 found that our bot reaches 60 units locally with or without the change, so a local test cannot see it. New detail from this study: on medium maps, where our split-stop round is 300 instead of 150, our units and income keep rising until round 300 and then fall the same way.
