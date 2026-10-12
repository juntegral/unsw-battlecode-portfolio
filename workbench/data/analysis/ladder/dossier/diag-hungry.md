# No one term holds the hungry dragon; it walks a noisy path to the nearest tile it has not seen itself. No card, and the traced build was not run (team 1119; 128 local m3b7 games, 500 ladder games of ours, 597 of rank-1's; written 8 Oct 2026)

1. **What holds a hungry dragon in place.** Nothing pins it. On 57% of its hungry turns no pearl is in view, and there 83% of its steps aim at the nearest tile that this one dragon has never had in view. That pull is 8 points a step within 6 steps and 2 beyond; beside team mates the territory share differs by 27 points between steps (median), and alone two or more steps tie within 1 point on 44% of turns, so the id-and-round noise picks. The path folds back: on the ladder its head stands on a tile of its last 12 turns on 29.6% of hungry turns against rank-1's 17.5% (rank-1 the higher on 0 of 19 layouts). Circling a refused pearl, the picture of 3b, is 1.7% of hungry turns.
2. **The change.** No card. Steps 2 and 4 of the brief were not done: this session's tool guard (tools/ladder_guard.py) refuses the compiler, play.sh, nice and every write outside data/analysis/ladder, so no tracing copy, no fix copy and no game exist. In their place: an offline rebuild of score_step on every hungry turn of the 128 replays. One candidate switch came out of it (HEADING_KEEP, diff in part 4, not built) and its own check speaks against calling it a card.
3. **How sure.** Sure of the counts (118,680 hungry turns, counted alike by two scripts). Fairly sure of the rebuild: it names the step the dragon took on 83.1% of 95,236 turns against 45.2% by chance, 93.8% when alone with nothing in view. Not sure of any gain: inside our own games a dragon that kept its heading for three steps eats within 20 turns as often as one that turned three times (24.4% against 26.1%).

Labels: [M] measured by my scripts in dossier/work/: hg_scan.py with hg_agg.py (spell account), hg_scan3.py with hg_agg3.py, hg_agg3b.py, hg_orbit.py and hg_find.py (the rebuild), hg_lad.py with hg_lagg.py (motion, ladder and local). [C] read from ~/meow-redteam/solo/bots/m3b7/main.cpp, line given. [E] my estimate.
Terms: hungry turn = a turn of one of our dragons of length 2 or 3, rounds 0-300, 26 rounds or more after its last meal or its birth (the rule of ec_idle.py); spell = such turns in a row. Ladder cells are ours / rank-1 over 19 layouts with equal weight, (k/n) = layouts where rank-1 is the higher. Steps are path steps over open edges and portals, bodies in view shut.

## 2. The spell account [M]
| Local m3b7 side, 128 games (32 maps, 2 seeds, 2 sides) | Value | Ladder, ours / rank-1 |
|---|---|---|
| Share of short-dragon turns that are hungry | 14.5% pooled (118,680 of 817,443); per map 0.0 to 44.5%; the 8 ladder layouts 35.8% (large, 20 games) and 23.5% (small, 12 games); generated maps 0.4 to 15.4% | 37.4% / 25.1% |
| By rounds 0-100, 101-200, 201-300 | 8.7%, 18.8%, 15.2% | |
| Spells | 5,426, 42.4 a game (median 36.5); length at the end median 37 rounds, 19.1% reach 60, 4.4% reach 100 | |
| How a spell ends | a meal 66.4%; still hungry at round 300 or the end 11.2%; death 22.3% (head-on 6.0, no action 5.6, other body 5.0, own body 2.9, wall 2.8) | |
| Hungry turns with no pearl in view | 56.8% | 57 to 59% / 48 to 50% |
| Team mates' heads in view: 0, 1, 2, 3 or more | 25.2%, 25.2%, 18.1%, 31.4% | 3 or more: 28.9% / 36.4% (13/19) |

| Where the 118,680 hungry turns go (first that holds) | Share | Note |
|---|---|---|
| Nothing in view, team mates in view | 37.8% | 22% of steps fold back; 4 tiles (median) from where it stood 10 turns ago |
| Nothing in view, no mate in view | 16.6% | 10% fold back; 6 tiles; same step as last turn 40% |
| Pearl in view, no target: behind kelp or bodies, or over 12 steps | 15.4% | no path of 12 steps with the bodies in view shut |
| Pearl in view, no target: a team mate is nearer | 6.8% | 8,111 turns; the mate is 1 step away on 3,468 |
| Pearl in view, no target: an enemy is nearer by 2 | 0.2% | |
| Pearl a target, 2-3 steps / 4-6 / 7-12 | 7.1% / 3.5% / 1.8% | |
| Pearl a target, beside the head | 4.3% | eaten that turn 66.2% |
| Boxed in (under 6 free tiles) | 6.3% | median 2 turns a dragon; 45 dragons boxed for 20 turns or more hold 3,190 turns (2.7%) |

- Pearl beside and not taken. A pearl on a step on offer: 5,870 turns, eaten 62.0%. Of the 2,229 refusals the pearl step is trapped (under L+2 tiles) on 1,225, tight on 161, has a mate's head beside it and nothing else on 107, and carries nothing I rebuilt on 706. This is part 3a of diag-economy; it is 1.9% of hungry turns.
- Small room, zone, feeding. Target pearl beside the head: room 3,970 turns, tight 194, trapped 942. Leader zone on with the longest own dragon within 12 tiles: 6.1% of hungry turns (3,929 with a pearl in view). After round 200 with 56 or more alive (feeding on): 33.3% of hungry turns, and the rebuild fits them nearly as well (80.1% against 84.7% in rounds 101-200), so the feeding rules are not what steers them; 301 hungry dragons end as a feeding death.
- 37.1% of hungry turns are by a dragon that has not eaten since it was born.
- The ladder picture holds locally. Hungry dragons on the 8 ladder layouts, local m3b7 beside the ladder build: tiles from where it stood 10 turns ago 6.4 (ladder 5.7), on a tile of its last 12 turns 32.3% (29.6%), same step as last turn 30.4% (33.2%), meals per 1,000 hungry turns 24.1 (19.5). The seven switches of m3b7 did not change how a hungry dragon moves.
- Ours against rank-1 on the ladder, hungry turns (hg_lad.py, all 1,097 games): tiles from where it stood 10 turns ago 5.7 / 6.9 (19/19); 4 or fewer 51.4% / 39.0% (0/19); head on a tile of its last 12 turns 29.6% / 17.5% (0/19); same step as last turn 33.2% / 44.1% (19/19), alone with nothing in view 41.4% / 55.9% (17/17); tiles seen for the first time per turn 2.4 / 3.0 (17/19); meals per 1,000 hungry turns 19.5 / 30.8 (18/19). The meal gap is two things: a pearl in view on 42.1% / 50.4% of hungry turns (16/19) and, with one in view, 54.7 / 71.3 meals per 1,000 (15/19); [E] by the layout means about two fifths of the gap is the view and three fifths the taking.
- The 4 by 3 patch of 3b is real and small: runs of 4 or more turns in a row with a target pearl within 3 steps and no meal are 393 runs, 2,069 turns, 1.7% of hungry turns (hg_orbit.py); all runs with a target pearl within 3 steps are 14,727 turns and 53.1% end in a meal.

## 3. The trace: an offline rebuild, terms and counts [M]
hg_scan3.py keeps for each of our dragons what the bot keeps (per tile: round seen, pearl, countdown, hot mark; blank at birth) and rebuilds for every step on offer the survey within 16 steps: room, territory, the distances to pearl, soon, hot and never-seen targets, tight / trapped / no tail, eat bonus, spawn clear, a mate's head beside the step, and a one-tile look-ahead. Left out: 15,816 turns with no step, one step on offer or boxed in, and 7,628 with an enemy head in view (threat terms not rebuilt).

| Hungry turns rebuilt | n | Rebuild names the step taken | By chance | 2+ steps within 1 point | Step lands on a tile of its last 12 turns |
|---|---|---|---|---|---|
| All | 95,236 | 83.1% | 45.2% | 17.2% | 22.1% |
| Nothing in view, no mate | 16,941 | 93.8% | 52.3% | 44.2% | 9.9% |
| Nothing in view, 1-2 mates | 25,998 | 71.9% | 40.6% | 8.4% | 21.1% |
| Nothing in view, 3+ mates | 13,774 | 90.9% | 45.1% | 13.3% | 22.9% |
| Pearl in view | 38,523 | 83.1% | 45.4% | 12.8% | 27.7% |

- What the step taken aims at (all 95,236): the nearest never-seen tile within 6 steps 49.5%, the same over 6 steps away, where only far gain pays, 18.6%; a pearl in view 14.3%; a remembered spawning tile due within 6 rounds 6.5%; a remembered spawning tile with nothing due 3.7%; a remembered pearl that is gone 1.0%; nothing named 1.6%. With nothing in view the never-seen tile is 82.8% (63.0 + 19.8).
- Points between the best and the worst step, median / 75th / 90th percentile. Nothing in view, 1-2 mates: territory 27 / 61 / 108, target bonus 8 / 16 / 27, far gain 4 / 4 / 8. Nothing in view, no mate: territory 0 / 0 / 0, target bonus 8 / 16 / 20, far gain 2 / 4 / 6. A mate's head beside one of the steps (450) on at least 1 turn in 10 with 1-2 mates in view and 1 in 4 with 3 or more.
- The step changes when the term is removed (79,130 turns the rebuild explains): never-seen target 11.1%, territory 7.3%, mate's head beside 4.3%, soon 2.1%, pearl target 1.9%, far gain 1.3%, look-ahead 1.2%, hot 0.1%. Nothing in view with 1-2 mates: territory 18.6%, never-seen 13.1%. With 3+ mates: mate's head beside 9.1%, territory 7.2%, never-seen 7.1%. Alone: never-seen 22.9%, soon 3.5%, territory 0.
- Steps that fold back (21,015): aimed at a never-seen tile over 6 steps away 29.0%, within 6 steps 27.7%, a pearl in view 17.8%, a remembered spawning tile 15.5%. No single term marks them: removing territory changes 8.2% of them and 7.1% of the other steps.
- Does a straighter walk feed it? (hg_find.py, hungry turns with nothing in view, by how many of the last 3 steps repeated the step before: 0 / 1 / 2 / 3.) A pearl in view on the next turn 12.4 / 10.8 / 10.2 / 9.2%; a meal within 20 turns 26.1 / 25.6 / 25.8 / 24.4%. With no mate in view 18.1 / 19.8 / 21.6 / 23.0%; with mates in view 29.0 / 28.2 / 28.1 / 25.6%. Dragons among mates eat sooner than dragons alone.

### Why, in the code [C]
- The target bonus is the largest of pearl 2.0, soon 0.45, hot 1.2, never-seen 0.20 and portal 0.40 times (260 - 40 x steps) (5084-5096, 3313-3319, 357-360, 368, 389, 397): the never-seen tile pays 8 a step and nothing from 7 steps. Beyond that FAR_GAIN pays 2 a step toward the nearest of the four (5100-5110, 269-270).
- Never seen means seen_round below 0 in this dragon's own arrays (3002-3005, 453, 1452); each dragon is one process with one Bot (5758-5760), so a child starts blank among mates that have seen it all. [M] 93.8% agreement alone fits a blank start.
- Territory counts every reachable tile the dragon reaches before any enemy head in view and no later than any team mate's head in view (2956-2967, floods 2391-2433), with no decay by distance (349, 3221-3224), at 1.5 a tile times 1 for a pearl, 0.3 for a tile that never spawns, 80 / (80 + rounds to spawn) otherwise and 0.5 never seen (346-348, 3234-3247). One step beside a mate moves the whole border between them.
- A step a team mate's head could also take costs 450 (5142-5144, 391). The tie noise is 0.25 x ((id x 31 + round x 17 + k x 7) % 5) (5459). Nothing in pick_direction reads the heading: the dragon's own ct.get_dir() is read only at 1437, for the leader report.
- A remembered pearl stays a target out of view (1450, 2982-2985) and a countdown that ran out unseen counts as due for good (2989-2996): 4.7% of aims together.

## 4. No card
What the rebuild rules out as the thing that holds a hungry dragon:
- A refused pearl that keeps pulling: 1.7% of hungry turns; the refusals beside a pearl are 1.9% and belong to CRAMPED_EAT.
- Stale memory (pearl gone, spawning tile with nothing due): 4.7% of aims. Boxed in for 20 turns or more: 2.7%. The leader zone: 6.1% of turns at most. The feeding rules: the rebuild, which has none of them, fits those turns to 80%.
- Territory beside mates: it decides 18.6% of steps with 1-2 mates in view, but those dragons eat sooner than the ones alone (29.0% against 18.1% within 20 turns), so pushing them out of the crowd is not shown to feed them.
- The tie noise and the missing heading: real (44.2% ties alone; same step 33.2% against rank-1's 44.1%), but inside our own games heading kept is not followed by a meal sooner, except alone (18.1% to 23.0%).

Candidate, not built and not played, for a slot that would otherwise stay empty. Switch name HEADING_KEEP, against solo/bots/m3b7/main.cpp:
```diff
@@ -269,3 +269,6 @@
 constexpr double FAR_GAIN = 2;
 constexpr int FAR_RANGE = 80;
 constexpr int FAR_IDLE = 0;
+// With no team mate in view a short dragon keeps its heading unless another step scores HEADING_BONUS better.
+constexpr bool HEADING_KEEP = false;
+constexpr double HEADING_BONUS = 3.0;
@@ -5459,2 +5462,6 @@
             score += 0.25 * ((TIE_SEED * 101 + ct.get_id() * 31 + round * 17 + static_cast<int>(k) * 7) % 5);
+            if (HEADING_KEEP && length <= 3 && ally_heads.empty() && scored[k] && score > SCORE_REJECT * 0.5 &&
+                !is_queen() && !is_leader() && !is_feeder() && direction == ct.get_dir()) {
+                score += HEADING_BONUS;
+            }
 
```
- [M] First order, this turn only (hg_agg3b.py, turns the rebuild explains with the straight-on step on offer): alone with nothing in view the step is straight on 44.8% of turns now and 75.5% with 3 points (78.5% with 6); 30.6% of the steps that fold back there go straight with 6. Over all hungry turns 38.1% to 53.0%, were it not limited to dragons alone.
- [E] Worth: dragons alone are 25% of hungry turns (29.4% on the ladder); if their meal within 20 turns goes from 18.1% to 23.0%, the hungry share falls by under 1 point of 37. That is 0.1 to 0.3 of the 2.7 pearls per 1,000 turns, on an association, not a test.
- Mechanism check a replay can show (hg_lad.py L on the new run folder; it needs one line for the folder name): hungry, nothing in view, no mate: same step as last turn 37.7% to 60% or more, head on a tile of its last 12 turns 20.4% to 12% or less, tiles seen for the first time per turn 3.8 to 4.5 or more. Wrong if wall, own-body or other-body deaths of short dragons rise, or pearls by round 300 fall on the same seeds.
- Baseline to set a fix arm against (m3b7, 128 games, hg_agg.py): wins 105; spells per game 42.4; hungry share of short turns 14.5%; pearls eaten by round 300 per game 1,620; deaths by round 300 per game: head-on 120.4, other body 73.6, own body 55.9, wall 45.9, no action 34.2.
- To run steps 2 and 4 after all: work/hg_trace_patch.md says where a bot can write under play.sh (a file in its own folder; stdout is the protocol), what to log at which lines and how to check that play is unchanged. Neither was tried.

## 5. Against it
- [M] The trace the brief asked for does not exist. The rebuild is my reading of the code run on the true board; it misses 16.9% of steps (28.1% with 1-2 mates and nothing in view), leaves out every turn with an enemy head in view (7,628) and has no threat terms, no route targets, no harvest, no pockets, one tile of look-ahead for eight, and counts territory to 16 steps where the bot counts the whole board. A real log could show a term I did not rebuild deciding the missed steps.
- [M] The leader in the rebuild is the longest own dragon, not the one the dragon has heard of; the child's blank memory is inferred from the code and the fit, not seen in a log.
- [M] Local hunger is not ladder hunger: 14.5% of short turns against 37.4%, and on generated maps two thirds of hungry turns have 3 or more mates in view (ladder 28.9%). The local opponent is one bot. Only the 8 ladder layouts match the ladder picture.
- [M] Heading and meals are compared across turns the dragon chose, in places that differ; three steps is short; rank-1 is straighter on 19 of 19 layouts and better fed on 18, which my within-bot count neither explains nor contradicts.
- [M] "Unclaimed pearl" in hg_lad.py ignores walls (torus distance), so I did not use it. Who eats the pearl in the 47% of approaches that fail (a mate at equal distance, an enemy, nobody) is not counted.
- [E] The hungry share may not be a walking problem at all: as many pearls are born per turn of ours as of rank-1's (diag-economy part 1) and it eats more of them with a pearl already in view. The part of the gap this report can reach is the smaller one.
- Housekeeping: the guard has no nice, so scans ran plain, at most 4 at a time, a few minutes in all. The Write tool is refused for this folder (path spelling); files went through the Python route. In work/: 10 hg_ scripts, hg_trace_patch.md, hg_scan-m3b7-0..3.jsonl (32 MB), hg_scan3-m3b7-0..3.jsonl, hg_lad-*.jsonl and three test outputs. Nothing was written outside data/analysis/ladder; nothing under ~/meow-redteam was touched.
