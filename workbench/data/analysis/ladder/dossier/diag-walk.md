# With no pearl in view rank-1 walks on and we turn back: is that worth a switch now?

1. What the re-treading is and whether it costs: half of our re-tread steps go back onto the tile the head left three steps before (a 2 by 2 circle by a dragon of length 2 or 3), and 72% are taken with a new tile free beside the head. Ours is the higher rate in every kind of situation (least so in pockets, in cramped spots and for the queen, where rank-1 re-treads nearly as much), and it is behaviour, not dragon mix. It does not cost pearls that I can measure: inside our own games at most about 1 to 3 pearls a game of 399.
2. The change: no card. Neither a cost on the dragon's own recent tiles, nor a cost on turning, nor NO_REVERSE.
3. How sure: fairly sure. All 1,097 games were recounted step by step and agree with the dossier on every count; rank-1's walking on is real on 17 to 19 layouts, but in rank-1's own games the steps that keep direction are followed by fewer pearls than its turns. Every worth number is a correlation; nothing was built.

Scope: 500 main ladder games of ours and 597 of rank-1 (team 306), rounds 0-300, the followed side only, 19 shared layouts, each rate formed inside a layout and then averaged with equal weight (as scoreboard.md). Scripts in dossier/work/: wk_scan.py (the pass), wk_agg.py, wk_more.py (tables), wk_keep.py, wk_kept.py (kept against turned), wk_tie.py (tie-break check), wk_sim.py (toy walker), wk_index.py. Blind turn and re-tread as in the dossier. Check (measured): turns, blind turns, moved, re-tread, kept, eligible, pearls and splits match the dossier in both windows for 1,097 of 1,097 games, and the totals reproduce the scoreboard (17.8 and 10.4; 19.7 and 11.2; kept 40.4 and 48.9; blind 48.3 and 40.8). Pairs "a; b" are r0-100; r101-300. O = ours, R = rank-1.

What can score (first that holds; the replay does not carry the bot's sums or the countdowns, so this says which terms can be non-zero): an enemy head in view; a target near = a pearl is born inside the view within 8 rounds (the countdown was visible), or a pearl this dragon saw earlier lies within 7 tiles, or a tile with 2+ births so far is in view; cramped = fewer than 3L+8 free tiles reachable; centre rule on (L 4 or less, small layout, first 30 or 60 rounds); else nothing scores. Around: a team mate's head within 3 tiles, else a pocket (20 or fewer tiles within 4 path steps), else a portal within 3 steps, else walls near (21-32 tiles), else open.

## 1. Where the re-tread steps are (measured, wk_agg.py kinds, wk_more.py)
| Blind moved turns | Share O | Share R | Re-tread O | Re-tread R | R lower on (layouts) | Points of the gap |
|---|---|---|---|---|---|---|
| All | 100 | 100 | 17.8; 19.7 | 10.4; 11.2 | 17; 18 of 19 | +7.41; +8.49 |
| Enemy head in view | 22.3; 27.8 | 20.0; 24.8 | 18.3; 20.3 | 10.9; 12.7 | 16; 17 of 19 | +1.56; +2.38 |
| Target near | 35.8; 46.0 | 43.6; 57.5 | 21.1; 21.9 | 13.4; 13.0 | 18; 18 of 19 | +1.55; +3.01 |
| Centre rule on, nothing else | 7.9; none | 9.8; none | 21.8 | 2.1 | 7 of 8 | +1.71; 0 |
| Cramped | 1.3; 0.6 | 1.5; 0.4 | 14.7; 20.6 | 19.5; 13.0 | 3 of 7; 10 of 13 | +0.07; +0.19 |
| Nothing scores | 32.6; 25.6 | 25.1; 17.2 | 9.7; 13.0 | 3.4; 4.0 | 17; 17 of 17 | +2.52; +2.91 |
| - never-seen tile within 4 steps | 23.1; 14.6 | 19.2; 12.3 | 3.2; 3.8 | 1.4; 1.4 | 15; 16 of 17 | +0.51; +0.45 |
| - never-seen tile 5+ steps away | 9.5; 11.0 | 5.9; 4.9 | 23.4; 25.5 | 10.3; 10.0 | 17; 17 of 17 | +2.00; +2.47 |
| Length 2 | 67.4; 63.4 | 64.5; 62.0 | 14.3; 18.4 | 7.0; 9.1 | 19; 18 of 19 | +4.81; +5.92 |
| Length 3 | 31.8; 31.7 | 33.5; 30.7 | 24.3; 23.3 | 15.9; 15.0 | 13; 18 of 19 | +2.84; +2.91 |
| Born 0-5 rounds ago | 16.4; 6.6 | 19.0; 9.8 | 3.6; 4.9 | 2.2; 2.9 | | +0.12; +0.04 |
| Born 41+ rounds ago | 29.1; 57.5 | 21.1; 41.3 | 21.8; 23.1 | 16.3; 14.5 | 14 of 18; 19 of 19 | +3.18; +7.35 |
| Team mate's head within 3 | 38.4; 51.5 | 40.7; 58.2 | 19.7; 21.4 | 11.8; 12.6 | | +2.96; +3.64 |
| Pocket | 5.0; 3.8 | 6.8; 4.0 | 25.1; 25.4 | 23.3; 20.8 | 13 of 17; 13 of 16 | -0.21; +0.44 |
| Open ground | 26.1; 21.0 | 20.5; 16.5 | 11.9; 15.6 | 4.0; 5.3 | | +1.77; +1.96 |
| Blind for 5+ rounds already | 56.3; 58.3 | 47.3; 46.4 | 19.4; 20.0 | 9.1; 9.1 | 17; 19 of 19 | +7.37; +7.45 |
| The queen (the rest: 16.2; 19.1 against 8.1; 10.4) | 12.6; 3.9 | 12.3; 2.8 | 25.8; 28.8 | 21.3; 29.6 | | |

| What the re-tread step is (share of re-tread steps) | O | R |
|---|---|---|
| Onto the tile left 3 steps before; 5; 7; 9 or 11 | 50.1, 22.4, 14.0, 13.5; 53.1, 19.5, 12.1, 15.4 | 44.9, 19.0, 17.3, 18.8; 43.9, 21.5, 15.6, 19.0 |
| A new tile was free beside the head; only recent tiles free; one way out | 71.5, 16.3, 12.1; 72.0, 19.0, 9.0 | 56.8, 23.0, 20.2; 55.5, 24.2, 20.3 |
| So, of all blind moved turns: re-tread with a new tile free; without (product of the rows, approximate) | 12.7, 5.1; 14.2, 5.5 | 5.9, 4.5; 6.2, 5.0 |

Read with it (measured): our mix of kinds (length x age x what scores x around) with rank-1's rate inside each kind gives 10.6; 11.7, and rank-1 itself has 10.4; 11.2, so it is not the mix. The whole gap is steps back onto a recent tile when a new one was free, by dragons of length 2 and 3 that have been blind for 5+ rounds; it is spread over every kind, a mate near or not. Nothing-scores turns hold a third of it (2.5 and 2.9 of 7.4 and 8.5 points), the centre rule 1.7 points in r0-100 (Prisoners Dilemma 51% and 52%, Tower Defense 41%, Autarky 15% against 2% to 3% for rank-1). A split child's empty memory is not it: in its first 5 rounds a dragon re-treads 4% (it has no trail yet), and the gap sits in older dragons (born 6-15 rounds ago 16.8; 16.6 against 8.2; 9.1, born 16-40 rounds ago 21.4; 17.9 against 12.4; 10.9, and the 41+ row).

## 2. Is it worth pearls (measured, wk_agg.py worth part2 blind, wk_more.py, wk_kept.py)
| What follows a blind moved step that has a step before it, inside each bot | Step keeps direction | Turns onto a new tile | Onto own recent tile | Kept above turned on |
|---|---|---|---|---|
| O, all: pearl in view next turn %; pearls eaten in the next 10 rounds | 11.3, 0.270; 12.0, 0.211 | 15.6, 0.283; 15.8, 0.212 | 15.7, 0.279; 17.5, 0.217 | eaten: 7; 6 of 19 |
| R, all | 14.2, 0.346; 15.2, 0.300 | 21.2, 0.447; 22.4, 0.380 | 28.5, 0.561; 29.2, 0.474 | eaten: 2; 1 of 19 |
| O, nothing scores | 5.1, 0.174; 5.0, 0.120 | 4.9, 0.165; 4.8, 0.101 | 3.1, 0.160; 2.2, 0.097 | eaten: 9; 10 of 17 |
| R, nothing scores | 5.0, 0.181; 4.9, 0.143 | 6.5, 0.237; 6.0, 0.164 | 3.8, 0.281; 4.8, 0.201 | eaten: 0; 6 of 17 |
| O, nothing scores, open or walls near | 4.4, 0.153; 4.7, 0.133 | 4.2, 0.132; 4.8, 0.104 | 2.8, 0.133; 2.1, 0.096 | eaten: 11; 10 of 17 |
| R, nothing scores, open or walls near | 4.4, 0.167; 4.4, 0.141 | 4.9, 0.220; 5.1, 0.160 | 5.4, 0.258; 4.2, 0.182 | eaten: 5; 5 of 17 |

| Pearls a game inside our 500 games if (pooled; estimate, takes the correlation as cause; we eat 113.2 and 285.4 a game) | r0-100 | r101-300 |
|---|---|---|
| our re-tread steps above rank-1's rate were new-tile steps: all blind turns (47 and 186 steps a game) | -1.66 | -4.64 |
| same, nothing-scores turns only (18 and 65 steps); centre-rule turns only (5 steps) | +0.42; +0.86 | -0.08; none |
| our turns above rank-1's share kept direction: all blind turns (85 and 319 steps) | -1.57 | -4.19 |
| same, nothing-scores turns only (52 and 191 steps); open or walls near only (41 and 127) | +0.47; +0.94 | +1.85; +2.24 |

| Rank-1's games against ours, layout by layout | O | R | R higher on |
|---|---|---|---|
| Board seen by round 50; by round 100 | 0.632; 0.795 | 0.636; 0.822 | 10; 13 of 19 |
| First contact round, all 19; without Tower Defense, Trauma, Maze, Stripes (93% of the gap) | 19.9; 12.7 | 12.5; 12.0 | earlier on 11, later on 4, level on 4 |
| New-born dragon fed within 10; 20 rounds; same for one born with no pearl in view (31% and 28% of births) | 43.6, 53.7; 25.8, 40.1 | 51.3, 61.6; 33.9, 47.9 | 16, 16; 16, 17 of 19 |
| Turns blind for 5+ rounds as a share of all turns; pearl in view next turn; pearls eaten in the next 10 rounds | 30.4%; 11.1%; 0.187 | 21.3%; 15.9%; 0.318 | 1; 19; 19 of 19 |
| Blind 5+ rounds, nothing scores, open or walls near: pearl in view next turn; eaten in 10 | 4.0, 0.135; 4.4, 0.104 | 4.6, 0.169; 4.7, 0.139 | found 13; 9, eaten 13; 15 of 17 |
| Lone dragon, nothing scoring, never-seen tile within 6 steps (76 games each, wk_tie.py): kept; re-tread | 46.8%; 4.5% | 70.6%; 2.4% | |

| Where the extra blind turns come from (measured, wk_agg.py blind) | O | R |
|---|---|---|
| Blind share of turns | 49.9; 48.3 | 42.0; 40.8 |
| Blind spells started per 100 turns; mean length of a spell (R shorter on 19; 18 of 19) | 6.66, 7.30; 5.99, 7.86 | 7.45, 5.59; 7.25, 5.36 |
| Turns with a tile that has had 2+ births in view; blind when there is one; when there is none | 41.6, 29.9, 64.6; 68.3, 35.4, 74.7 | 54.8, 25.1, 62.6; 81.4, 32.9, 75.0 |
| Turns with no team mate in view; blind then. With 2+ in view; blind then | 36.1, 52.6, 35.5, 46.9; 23.3, 49.6, 52.4, 45.3 | 30.5, 50.1, 43.4, 35.6; 16.5, 49.6, 63.8, 37.0 |
| Blind share with rank-1's mix of places (board pearls x mates in view x repeat tile) and our blind rate inside each place | 45.3; 43.2 | |

Read with it (measured, the first sentence is my reading): walking on buys rank-1 nothing I can find. Its board seen is ours; in open ground with nothing scoring a dragon of either bot has a pearl in view next turn after 4 to 5% of steps whether it kept direction or turned; in rank-1's own games kept steps are followed by fewer pearls than turns in every row, and its re-tread steps by the most. The 7 to 8 points of extra blind turns are longer spells, not more of them, and 4.6 and 5.1 of the points go when our turns are put in rank-1's places: its dragons spend 55% and 81% of their turns in sight of a tile that has already spawned twice (ours 42% and 68%) and 43% and 64% with two or more team mates in view (ours 36% and 52%). Away from such tiles, or alone, the two bots are blind equally often. The rest (2 to 3 points) is inside the crowd, where rank-1 has a pearl in view more often; it eats 467 pearls a game in r101-300 to our 285.

## Why, in the code (main.cpp)
- Read from the code: nothing in the step score knows the last direction or the last 12 tiles; trail holds the body only (1395-1399). With no target within 7 steps the terms that differ by direction are the distance to the nearest tile this dragon has never seen (unseen bonus 0.2 x (260 - 40 x steps), 374, 5028; FAR_GAIN 2 a step, 261-262, 5037-5046) and the tie-break 0.25 x ((id x 31 + round x 17 + k x 7) % 5) (5361), which changes its favourite direction every round. The memory is per dragon (seen_round, 438).
- Measured (wk_tie.py, 76 games, 17,749 steps of a lone dragon with nothing scoring): the step is the one nearest a never-seen tile in 92.4%; where two or more tie (8,313) the formula at 5361 names the step in 94.4% (chance 48.5%; 29.6% with the round shifted by one; rank-1's steps 45.7% against chance 44.6%). The two together name 89.7% of our steps. So the low direction-keeping is the tie-break; a toy walker with these terms alone keeps direction 20% and never re-treads (wk_sim.py).
- Measured: the re-tread itself comes where the never-seen tile is far: 25.0% for a lone dragon (1,213 steps), and the same rule reproduces 22.8%. Estimate: the dragon turns back across its own track to mop up the nearest never-seen patch, then the next.
- Read from the code, estimate for the rest: with a team mate near, a tile the mate reaches first counts nothing toward territory, 1.5 a tile (335-336, 2928-2939, 4972-4976), and a tile its head can step to costs 450 (376, 5066-5068), so the best step moves when the mate moves. A remembered pearl pulls only if we reach it first or within 1 step of the enemy (316, 2949-2957). The centre rule takes 40 a tile (358, 5061-5064). None of these was reconstructed from replays.
- Read from the code and the notes: NO_REVERSE (240, 4957, 2994) only stops the room count going back through the head's tile; it lost 3 of 4 locally because it keeps dragons out of pockets (plan.md:49).

## The card (a record of a negative result; nothing to build)
title: Walking on with no pearl in view: counted against rank-1 on 1,097 games, no switch earns the build round
slug: walk check
### Claim
Measured: against rank-1 our dragons re-tread 7.4 and 8.5 points more and keep direction 8.5 and 10.5 points less, on 17 to 19 layouts, in every kind of situation; the gap is smallest in pockets, in cramped spots and for the queen. Measured: the cause of the turning is the round-rotating tie-break at main.cpp:5361 (94.4% of tied steps). Estimate: a cost on turning or on the dragon's own recent tiles, held to turns where nothing scores, would move 52 to 190 steps a game and is worth between 0 and 3 pearls a game of 399; outside those turns the sign is against it. The extra blind turns are where our dragons stand, not how they step.

### Evidence
- Measured: steps that keep direction are followed by fewer pearls in the next 10 rounds than turns onto a new tile in rank-1's own games (0.346 against 0.447; 0.300 against 0.380; kept higher on 2 and 1 of 19 layouts) and by no more in ours (0.270 against 0.283; 0.211 against 0.212).
- Measured: where nothing scores, ours 0.174 against 0.165 and 0.120 against 0.101 (9 and 10 of 17 layouts); pooled, +0.47 and +1.85 pearls a game at rank-1's share of kept steps; a re-tread step there +0.42 and -0.08.
- Measured: board seen by round 50 is 0.632 against 0.636; first contact is 12.7 against 12.0 once the four layouts that carry its gap are set aside.
- Measured: 4.6 and 5.1 of the 7.9 and 7.5 points of extra blind turns go with position (repeat-spawn tile in view, mates in view).

### Expected signal
Estimate, if this verdict is right: in the next 100 main games our kept steps with nothing scoring are again followed by no more than 0.03 pearls above our turns (now +0.009 and +0.019), on about half the layouts; and a build that only raises direction-keeping leaves pearls by round 100 inside the run-to-run spread.

### What would show it's wrong
- A local pair, same seeds: at main.cpp:5361, when the best target bonus of the four directions is zero, no enemy head is in view, the dragon is not the queen and the step is not into a pocket, give the direction of the neck-to-head step (trail[1] to trail[0]) a bonus in place of the rotating term (estimate: 1.5 makes the toy walker keep direction 99% on empty ground, so start lower and tune to the mark). Mechanism mark from rank-1: a lone dragon keeps direction in 70% of such steps (ours 47%) and re-treads 2.4% (ours 4.5%); over all blind turns kept about 48%, re-tread about 11%. If that build eats 3+ pearls a game more by round 300 on at least 12 of 19 layouts, the within-bot cuts were hiding a cost. It must leave alone: pockets and cramped spots (in pockets rank-1 re-treads 23% and 21%, we 25%), a dragon with an enemy head in view, and the queen (26% and 29% against rank-1's 21% and 30%).
- On new games, inside our own play, kept steps with nothing scoring are followed by 0.05+ more pearls than turns on 13+ of 17 layouts.
- Our share of turns in sight of a twice-spawned tile rises to rank-1's (55% and 81%) and the blind share does not fall: then position is not what holds the blind turns.

## Against it
- Measured: between the bots, rank-1's long-blind dragons do better on 19 of 19 layouts (pearl in view next turn 15.9% against 11.1%, eaten in 10 rounds 0.318 against 0.187) and its new-born dragons are fed sooner on 16. Even in open ground with nothing scoring it eats more after a step (0.169 against 0.135; 0.139 against 0.104; 13 and 15 of 17) while finding a pearl no more often. I put that down to more pearls lying about in its games and to what it does once a pearl is seen; that is inference, not a count.
- Every worth number is a correlation inside games. A dragon turns for a reason, so turns are followed by more pearls partly because of where they happen. If the nothing-scores numbers are all cause, the switch is worth 0.1% to 0.8% of our pearls; that is under what one build round of local games can show, which is the practical reason for the no.
- What can score is a reconstruction. The pearl-due class uses births the replay shows 8 rounds on; the remembered pearl uses straight distance; the repeat tile counts death drops too. The bot's hot marks, countdowns, look-ahead and territory weights are not in a replay, so some nothing-scores turns have a small term at work. With a team mate near (38% and 52% of our blind moved turns) the deciding term is an estimate.
- The tie-break check is lone dragons in 76 games a bot, rounds 0-200. It also shows the main.cpp on disk walks like the ladder build; the rest of the build was not checked.
- Rank-1's 597 games are mostly against teams that reached 2100+ (448 of them); ours are against the whole ladder. Layouts are held equal, opponents are not.
- The centre-rule kind is the one place a re-tread step is followed by clearly fewer pearls (0.069 against 0.231 after a new tile; +0.86 pearls a game). That is the stall release card (losses/early-growth.md); it now reads as Prisoners Dilemma and Autarky as well as Tower Defense, and those are layouts we win on with the rule.
- Housekeeping: the guard refuses plain writes because the project path is stored in decomposed Unicode; files went through the reviewed Python route as before. wk_keep-*.jsonl repeats wk_scan-*.jsonl with one more field.
