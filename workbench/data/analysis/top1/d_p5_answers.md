## 5. Answers to the eight questions

Each count names its script and output file in brackets. All scripts are in this directory; outputs are in `d_out/`.

### a. Every death, classified

The tables are in section 2 [`d_md.py`, `md_class.md`; `d_haz.py`, `haz.txt`; `d_box.py`, `box.txt`]. In one paragraph:

- Of our 362 queen deaths, 251 are rams, 91 are boxed-in deaths, 19 are her own rams and 1 is a portal step onto a body. Of the rams, 104 happened on a turn on which a safe step existed and she ended in reach (66 stepped in, 38 stayed in), 114 when cornered, 2 on a cell the model called safe, and 31 by an enemy she could not see.
- By round band (0-49 / 50-99 / 100-299 / 300+): all deaths 80 / 100 / 156 / 26. The avoidable rams are spread over the first three bands (22 / 33 / 45 / 4); the boxed-in deaths by a team-mate are heaviest in the opening (23 / 13 / 18 / 4) because of two patterns (question d); terrain dead ends come later (2 / 11 / 16 / 1).
- Live bot against candidates: the shares are the same within noise (alive 10% and 10%; stepped or stayed in 25% and 29%; cornered 26% and 33%; boxed by a team-mate 16% and 12%). No candidate changed how the queen dies.
- Rules on against rules off (live bot, deaths per 1,000 queen-rounds): all 5.0 against 10.7; boxed by bodies 0.7 against 2.6; terrain 0.3 against 1.4; own rams 0.07 against 1.5; avoidable rams 1.5 against 2.4; cornered 1.7 against 2.4.
- Her length at death is 2 or 3 in 314 of the 362 (2 long: 188, 3 long: 126). The killer is 3 or shorter in 183 of the 251 rams and 4 long in 37; its ramming move had one step in 82, two in 76, three or more in 93.
- What the games became: section 2, last table. 102 of the 362 are round-500 losses with both queens dead.

### b. Avoidable or not

[`d_b.py`, `b.txt`; `d_expo.py`, `expo.txt`; `d_ramdet.py`, `ramdet.txt`]

**The last six turns before a ram** (251 of ours, 797 of the top three; first number ours, second the top three):

| Her own turn, counted back from the ram | last | 2nd last | 3rd last | 4th last | 5th last | 6th last |
|---|---|---|---|---|---|---|
| an enemy head in her view | 94% / 84% | 75% / 73% | 65% / 68% | 61% / 61% | 55% / 58% | 52% / 54% |
| the later killer in her view | 88% / 76% | 60% / 55% | 41% / 39% | 34% / 32% | 28% / 25% | 25% / 22% |
| free one-step moves (mean) | 2.1 / 1.9 | 2.3 / 2.1 | 2.3 / 2.2 | 2.4 / 2.3 | 2.4 / 2.2 | 2.4 / 2.3 |
| safe one-step moves (mean, turns with an enemy in view) | 0.8 / 0.4 | 1.8 / 1.5 | 2.0 / 1.7 | 2.1 / 1.9 | 2.1 / 1.8 | 2.2 / 1.9 |
| a safe step existed (of turns with an enemy in view) | 51% / 28% | 96% / 91% | 99% / 96% | 100% / 96% | 99% / 95% | 98% / 96% |
| she ended in reach (of those turns) | 93% / 89% | 6% / 9% | 1% / 5% | 1% / 4% | 1% / 4% | 2% / 3% |
| she ended in reach although a safe step existed (of those turns) | 44% / 17% | 2% / 2% | 0% / 1% | 1% / 1% | 0% / 1% | 1% / 1% |

Everything is decided on the last turn. On it our queen had a safe step in half of her rammed deaths and a top-three queen in a quarter of hers.

**Shares of the rammed deaths with a way out:**

| | meow, all (251 rams) | live bot (165) | our opponents (102) | forgot (327) | SSS (240) | Vibing++ (230) | top three (797) |
|---|---|---|---|---|---|---|---|
| last turn: killer in view and a safe step existed | 106 (42%) | 70 (42%) | 28 (27%) | 48 (15%) | 41 (17%) | 38 (17%) | 127 (16%) |
| ... she ended in reach although a roomy safe step that crossed no portal existed | 90 (36%) | 59 (36%) | - | - | - | - | 71 (9%) |
| last turn: killer in view, safe only by paying segments for a longer move | 35 (14%) | 21 (13%) | 16 (16%) | 60 (18%) | 34 (14%) | 13 (6%) | 107 (13%) |
| in one of her last three turns she ended in reach although a safe step existed | 107 (43%) | 71 (43%) | 32 (31%) | 46 (14%) | 41 (17%) | 37 (16%) | 124 (16%) |
| in one of her last three turns the killer was in view and a safe step existed | 185 (74%) | 122 (74%) | 85 (83%) | 213 (65%) | 133 (55%) | 132 (57%) | 478 (60%) |

**Every turn of every game with an enemy head in view** (not only the fatal ones), per 1,000 queen-rounds:

| | meow, all | live bot | meow against test4 / WHQ | our opponents | forgot | SSS | Vibing++ | top three | top three against test4 / WHQ |
|---|---|---|---|---|---|---|---|---|---|
| share of her rounds with an enemy head in view | 20.2% | 20.5% | 20.3% | 17.0% | 20.7% | 17.9% | 21.1% | 19.8% | 20.5% |
| A. outside reach, safe step exists: she ends in reach (share of such turns) | 0.76% | 0.68% | 0.77% | 0.42% | 0.18% | 0.15% | 0.23% | 0.19% | 0.06% |
| A. the same per 1,000 queen-rounds | 1.45 | 1.32 | 1.49 | 0.67 | 0.35 | 0.27 | 0.46 | 0.35 | 0.12 |
| B. in reach, safe step exists: she ends in reach again (share of such turns) | 19% | 17% | 21% | 13% | 10% | 8% | 10% | 9% | 11% |
| B. the same per 1,000 queen-rounds | 1.22 | 1.22 | 1.08 | 0.79 | 0.46 | 0.31 | 0.59 | 0.44 | 0.28 |
| C. no safe step (cornered), per 1,000 queen-rounds | 2.77 | 2.39 | 2.48 | 3.92 | 3.07 | 2.16 | 3.54 | 2.88 | 2.15 |
| all turns that end in reach, per 1,000 queen-rounds | 5.44 | 4.94 | 5.05 | 5.39 | 3.88 | 2.73 | 4.59 | 3.67 | 2.55 |
| ... of which by her own choice (A + B) | 2.66 | 2.54 | 2.57 | 1.46 | 0.81 | 0.57 | 1.05 | 0.79 | 0.40 |
| rammed on a turn that ended in reach | 71% | 72% | 77% | 16% | 44% | 47% | 32% | 40% | 67% |

Three things follow. Our queen sees an enemy head as often as anyone (one round in five). She is cornered as often as the top three. She ends in reach by choice 3.4 times as often as they do, and 6.4 times as often against the same two opponents. And a turn in reach costs her life 71% of the time (77% against test4 and WHQ), because those two take the ram; they take it 67% of the time against the top three as well. By map size the "by choice" rate is 3.3 (ours) against 0.6 (top three) on large maps, 1.3 against 0.5 on medium, 4.4 against 1.3 on small [`d_expo_size.py`, `expo_large.txt` and so on].

**Does she step nearer to a visible small enemy head?** Turns with an enemy head of 4 or shorter in view on which a nearer and a farther one-step move both existed; share on which she took the nearer one, by the path distance to that head:

| Distance to the small enemy head | meow live, rules on | meow live, rules off | our opponents | forgot | SSS | Vibing++ | top three against test4 / WHQ |
|---|---|---|---|---|---|---|---|
| 2 steps | 14 of 365 (4%) | 15 of 56 (27%) | 5% | 2% | 3% | 2% | 2% |
| 3 steps | 75 of 784 (10%) | 74 of 154 (48%) | 12% | 5% | 7% | 16% | 14% |
| 4 steps | 271 of 906 (30%) | 59 of 88 (67%) | 12% | 5% | 8% | 32% | 13% |
| 5 or more | 344 of 855 (40%) | 184 of 286 (64%) | 23% | 47% | 20% | 37% | 33% |
| all | 24% | 57% | 16% | 19% | 12% | 27% | 22% |

With the rules on she behaves like the top three at 2 and 3 steps and like Vibing++ (whose queen is longer: 4.9 on average in rounds 100 to 149) at 4 steps; SSS and forgot keep away at 4 steps in 92 to 95% of such turns. With the rules off she walks toward a small enemy head half the time at any distance. Only 5% of her nearer steps ate a pearl.

### c. How she lives

[`d_life.py`; `d_c.py`, `c_all.txt`, `c_large.txt`, `c_medium.txt`, `c_small.txt`; `d_where.py`, `where_all.txt`; `d_where2.py`, `where_r50_150.txt`]

Per 50 rounds, all maps (the live bot's queen; "q / team" = the queen against the other heads of her team, or for pearls against the whole team per dragon-round):

| | rounds | meow live | our opponents | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|
| natural pearls per 100 rounds, q / team | 0-49 | 4.7 / 7.2 | 4.9 / 7.6 | 4.6 / 7.6 | 4.1 / 6.7 | 4.7 / 8.1 |
| | 50-99 | 3.3 / 4.9 | 3.6 / 5.7 | 3.2 / 5.8 | 2.4 / 5.3 | 4.2 / 6.2 |
| | 100-149 | 2.2 / 3.6 | 2.4 / 4.3 | 1.3 / 4.2 | 1.6 / 4.2 | 2.3 / 4.8 |
| | 150-199 | 1.4 / 2.9 | 2.0 / 3.8 | 1.1 / 3.8 | 1.6 / 3.7 | 1.7 / 4.5 |
| path distance from her start, q / team | 0-49 | 9.4 / 17.4 | 8.3 / 19.4 | 11.4 / 18.7 | 9.5 / 19.4 | 10.5 / 20.1 |
| | 50-99 | 14.7 / 19.8 | 12.7 / 22.6 | 15.0 / 21.4 | 12.3 / 23.1 | 16.9 / 23.2 |
| | 100-149 | 14.3 / 21.0 | 13.6 / 24.0 | 11.8 / 22.2 | 12.7 / 23.7 | 18.4 / 24.9 |
| | 150-199 | 14.1 / 22.2 | 14.4 / 25.2 | 9.7 / 23.2 | 13.0 / 24.0 | 19.2 / 26.1 |
| share of rounds on the enemy's side, q / team | 50-99 | 17% / 21% | 13% / 24% | 20% / 23% | 8% / 24% | 16% / 23% |
| | 100-149 | 15% / 21% | 11% / 26% | 13% / 21% | 7% / 22% | 14% / 23% |
| rounds with an enemy head in her view | 50-99 | 23% | 18% | 25% | 19% | 23% |
| | 100-149 | 26% | 21% | 23% | 21% | 26% |
| enemy heads within 4 cells, q / team | 100-149 | 0.29 / 0.34 | 0.22 / 0.28 | 0.28 / 0.31 | 0.25 / 0.29 | 0.30 / 0.28 |
| enemy heads within 8 cells, q / team | 50-99 | 1.10 / 1.32 | 1.00 / 1.16 | 1.26 / 1.24 | 1.02 / 1.20 | 1.21 / 1.20 |
| | 100-149 | 1.65 / 1.64 | 1.33 / 1.32 | 1.45 / 1.48 | 1.29 / 1.44 | 1.40 / 1.39 |
| own heads within 4 cells of her | 100-149 | 1.22 | 1.52 | 1.66 | 1.74 | 1.36 |
| | 150-199 | 1.33 | 1.80 | 1.87 | 2.18 | 1.54 |
| her splits per 100 rounds | 0-49 | 3.6 | 3.6 | 4.4 | 4.9 | 3.2 |
| | 100-149 | 1.6 | 1.2 | 1.0 | 1.0 | 1.1 |
| her mean length | 100-149 | 2.5 | 3.0 | 2.7 | 2.6 | 4.9 |
| different cells her head used per 25 rounds | 100-149 | 19.4 | 16.4 | 17.6 | 18.1 | 18.6 |

**Is our queen a forager like any other dragon of ours?** No, and neither is anyone's, but ours is more of one than SSS's or forgot's. She eats half to two thirds of what an average dragon of our team eats (SSS's queen 38 to 61% of her team's rate, forgot's 29 to 60%); in rounds 100 to 149 that is 2.2 natural pearls per 100 rounds against 1.6 and 1.3. She is nearer to her start than her team (14.7 against 19.8 cells in rounds 50-99), but less so than SSS's queen is (12.3 against 23.1). Averaged over all maps, the five queens are close in every row of the table. The larger differences are in three places:

- **Large maps.** In rounds 50 to 199 the live bot's queen has an enemy head in view in 22%, 26% and 22% of her rounds; SSS's 11%, 10%, 11%; our opponents' 10%, 12%, 11%; forgot's 17%, 12%, 11%. Enemy heads within 8 cells of her: 0.97, 1.29, 1.30 (ours) against 0.53, 0.51, 0.61 (SSS) and 0.61, 0.80, 0.77 (our opponents). Her distance from her start grows from 15 to 19 to 22 cells; SSS's from 13 to 15 to 16; forgot's falls from 18 to 15 to 12 [`c_large.txt`].
- **Company.** Our queen has 1.2 to 1.3 own heads within 4 cells in rounds 100 to 199; SSS's has 1.7 to 2.2. For every team the ram rate of a short queen falls steeply with company (rounds 50 to 149, rams per 1,000 queen-rounds with 0 / 1-2 / 3 or more own heads within 6 path steps): ours 9.7 / 4.4 / 2.2; forgot 5.3 / 3.0 / 1.4; SSS 3.1 / 2.1 / 1.0; Vibing++ 4.9 / 3.5 / 0.7; our opponents 2.4 / 0.6 / 0.1. She is alone in 28% of those rounds, SSS's queen in 21% [`where_r50_150.txt`].
- **Distance from home.** Rams per 1,000 queen-rounds of a queen 4 or shorter by distance from her start cell (0-5 / 6-10 / 11-15 / 16-25 / 26 or more cells; all rounds): ours 1.8 / 3.0 / 5.5 / 8.1 / 8.6; SSS 0.8 / 1.6 / 1.7 / 2.9 / 2.5; forgot 1.1 / 2.4 / 4.8 / 4.5 / 4.0; our opponents 0.6 / 0.6 / 1.4 / 1.6 / 1.4. She spends 44% of her rounds more than 10 cells out, SSS's queen 45%: the time is the same, the price is three times higher [`where_all.txt`]. The gradient holds inside each round band (rounds 50 to 149: 3.0 / 4.2 / 5.5 / 8.2 / 5.3).

Two more states make every short queen die faster, ours most [`where_all.txt`]: a cell with one or two open sides (ours 7.6 rams and 9.0 other deaths per 1,000 rounds, against 3.7 and 0.8 on a cell with four open sides; SSS 3.9 and 2.3 against 1.4 and 0.2), and an enemy head within 8 path steps five rounds earlier (ours 10.5 rams per 1,000 rounds with one such head, 18.8 with two or more, 1.3 with none; SSS 6.9, 12.2, 0.4).

**When does a top queen stop foraging forward, and is there a hand-over?** There is no switch at a round in any of the five teams. Every queen begins as the mother of her team: in rounds 0 to 49 she eats 4 to 5 natural pearls per 100 rounds and splits 3 to 5 times per 100 rounds. The taper follows the size of the team (natural pearls and mother splits per 100 rounds while the team has 1-3 / 4-7 / 8-15 / 16-31 dragons at the start of the 50-round block):

| | 1-3 dragons | 4-7 | 8-15 | 16-31 |
|---|---|---|---|---|
| meow live | 4.1 pearls, 2.7 splits | 4.5, 2.5 | 2.9, 1.8 | 2.7, 1.2 |
| SSS | 4.1, 2.7 | 2.6, 1.9 | 2.4, 1.4 | 2.3, 0.9 |
| forgot | 5.1, 3.2 | 3.6, 2.3 | 2.3, 1.2 | 2.1, 0.7 |
| Vibing++ | 5.1, 3.2 | 4.3, 1.1 | 3.3, 1.4 | 2.3, 0.5 |
| our opponents | 4.2, 2.5 | 4.0, 2.2 | 2.1, 1.3 | 2.4, 1.2 |

SSS's queen hands over first: with 4 to 7 dragons in the team she already eats 2.6, ours 4.5. After the first enemy head has come into her view every queen eats about half of what she ate before (ours 4.0 then 2.5; SSS 3.1 then 1.8; forgot 3.9 then 2.0). So ours has the same hand-over as the others in what she eats and how often she splits. What she does not have is the second half of it: staying where her team is. In the SSS and forgot games read, the queen keeps to one area for hundreds of rounds (T1: 1 to 17 path steps from her start, T4: 1 to 19, T5: 2 to 14, T14: 1 to 5; in T12 one spot 20 to 25 steps out) and from round 100 mostly has 1 to 5 own heads within 4 cells; in ours she is 20 to 36 steps out by round 75 to 100 with fewer than one (games 2, 4, 8, 15, 25).

### d. The opening deaths

[`d_open.py`, `open.txt`]

80 of our queens die before round 50 (20% of games; top three 13%; our opponents 5%). By kind: boxed in by her own team 23, cornered 22, stepped in 15, stayed in 7, unseen 5, own ram 5, terrain 2, enemy body 1. By map: Devil 23 of 30 games, Stripes 13 of 29, Portals 12 of 27, Slithery Fight 10 of 29, Trophy 9 of 28, Around UNSW 5, Queen Of Spades 4, Autarky 2, Islands 2; none on the other seven maps. 28 of the 80 are five repeating patterns:

| Pattern | games | rounds | what happens | the general state |
|---|---|---|---|---|
| Slithery Fight, cell (4,21) or its mirror | 10 (7 live) | 3 | She starts 25 long with no free cell, cuts to 2 + 23, steps east, north, and is closed in by the child's body and a new 2-long's head (section 4.5a) | a boxed-in queen of 4 or more gives her length away and stays in the box |
| Portals, cell (4,7) | 7 (5 live) | 9 | Portal step at round 4 into a 4-cell pearl room, split at round 5, three more pearls, 5 long in 4 cells; the exit behind the portal holds her child's tail (section 4.5b) | she grows longer than the room she is in, and its only exit is a cell she cannot see |
| Portals, cell (27,8) (the mirrored start) | 4 (2 live) | 9-10 | the same | the same |
| Devil, cell (15,4) | 4 (3 live) | 18 | She walks to the centre lane and steps onto the cell next to an enemy 2-long's head (game 3) | steps next to a visible enemy head with two safe steps free; rules off |
| Devil, cell (16,9) | 3 (1 live) | 23-27 | She eats pearls along the centre lane, splitting 4 into 2+2 once or twice on the way, and is cornered by a 3- or 4-long one or two steps away | forages and splits in the contested middle |

The other 52 are single cases: 16 on Devil, 13 on Stripes, 9 on Trophy, 5 on Around UNSW, 4 on Queen Of Spades, 2 each on Islands and Autarky, 1 on Portals. On Devil and Trophy the top three die as early as we do (dead before round 50 in 54% and 34% of their games; ours 77% and 32%). The excess over the top three is on Portals (12 of 27 against 3 of 106), Slithery Fight (10 of 29 against 0 of 104) and Stripes (13 of 29 against 25 of 98).

### e. Queen rules on and off

[`d_haz.py`, `haz.txt`; `d_e.py`, `e.txt`; `d_f.py`, `f.txt`; `d_misc.py`, `misc.txt`; `d_pairs.py`, `pairs.txt`]

**What a replay shows of the switch** (live bot):

| | rules on (175 games, maps over 600 cells) | rules off (100 games) |
|---|---|---|
| queens that take a portal step, on maps that have portals | 7 of 175, none before round 20 | 27 of 44, 24 of them before round 20 |
| her own rams with a free safe cell | 0 | 8 (10 with the candidates) |
| she steps nearer to a small enemy head 2 / 3 steps away | 4% / 10% | 27% / 48% |
| she ends on the cell next to an enemy head from outside reach (share of such turns) | 1 of 5,506 | 10 of 2,116 |
| rounds on a 4-cell loop | 0.3% | 11.2% |
| small intruders within 4 steps that she rams herself | 2 of 712 | 14 of 141 |
| queens alive at round 200 that split after it | 6 of 52 (7 splits, all with no free cell; 5 of them cuts from 15 to 61 segments; `d_late.py`) | 3 of 6 |
| deaths per 1,000 queen-rounds | 5.0 | 10.7 |
| alive at the end | 25 of 175 (14%) | 2 of 100 |

So the rules that are on do what they say (no portals, no trades, no late growth splits) and halve her death rate. They do not touch the two largest kinds: with the rules on she still dies at 1.5 per 1,000 queen-rounds by stepping or staying in reach and at 1.7 cornered (top three: 0.3 and 1.3). And one thing gets worse with the rules on: all 11 "cut and stuck" deaths of the live bot are on rules-on maps, because the cut is an escape split that the queen rules do not block.

**passage2 (old against new, 28 pairs by opponent and map).** The new queen died earlier in 16 pairs and later in 11; median death round 136 (old) and 106 (new); dead before round 100: 9 and 13. Kinds old / new: stepped in 4 / 7, boxed by her own team 3 / 5, terrain 1 / 3, cornered 8 / 4, unseen 6 / 4. That points the way the team's note says, but 28 pairs cannot carry it: the qh31 pair shows the same shift (earlier in 16, later in 10; median 117 and 92) with a change that has nothing to do with passages, and stride shows none (13 and 13).

**qn23, the "queen no trap" candidate** (45 games in `../../online/smoke/qn23-test-new`, not in `games.csv`; walked with `d_extra.py`). Against the live bot's 215 games against the same three opponents: boxed-in deaths 15 of 45 (33%) against 52 of 215 (24%); per 1,000 queen-rounds 2.1 against 1.6. Terrain dead ends went up (8 of 45 against 15 of 215), boxed by her own team stayed (7 of 45; 16% and 17%), her own rams went to 0 (10 of 215 before). Two things in its replays: on Around UNSW the queen dies at round 5 in all three games, boxed in by her own split child in a nook right after a split; and on Slithery Fight she no longer dies at round 3 in its three games, but in two of them she is cut from 13 and from 66 segments to 2 late in the game and dies boxed in at rounds 371 and 410. The candidate did not reduce the deaths it was built for.

### f. Found and survived

[`d_f.py`, `f.txt`; `d_f2.py`, `f2.txt`; `d_t4.py`, `t4.txt`]

**Seen.** An episode is a run of rounds with an enemy head in her view. Every team's queen is seen in 88 to 98% of its games, 3.1 to 4.2 times per 100 queen-rounds (ours 3.7), for 5 to 7 rounds at a time. So ours is found as often as the others. What differs is the outcome:

| | meow, all | live, rules on | live, rules off | our opponents | forgot | SSS | Vibing++ | test4 against the top three |
|---|---|---|---|---|---|---|---|---|
| episodes per game | 5.1 | 6.3 | 3.7 | 9.5 | 7.4 | 8.7 | 7.7 | 6.5 |
| ended with her rammed | 11.5% | 10.0% | 12.6% | 2.6% | 6.3% | 4.7% | 5.4% | 7.1% |
| ended with her dead another way | 3.5% | 1.0% | 10.8% | 1.7% | 1.2% | 0.8% | 2.0% | 2.2% |
| episodes with an enemy within 3 steps, per 100 queen-rounds | 1.02 | 1.09 | 0.87 | 0.73 | 0.64 | 0.48 | 0.68 | 0.53 |
| ... of those ended with her rammed | 33% | 25% | 46% | 12% | 27% | 25% | 24% | 31% |

An enemy comes within 3 steps of our queen 1.5 to 2 times as often per round as of a top-three queen, and such an episode ends with a ram 1.3 times as often.

**Small intruders** (an enemy of 4 or shorter that comes within 4 path steps of the living queen; from the lead's `q/*.json` episodes):

| | meow, all | live, rules on | our opponents | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|
| intruders per game | 3.0 | 4.1 | 4.7 | 3.5 | 2.8 | 3.4 |
| it rammed the queen | 17.0% | 12.1% | 4.9% | 11.5% | 11.6% | 9.4% |
| one of her team rammed it | 3.7% | 3.7% | 13.6% | 13.5% | 16.6% | 12.1% |
| ... when 3 or more own heads were within 6 steps | 9.4% | 8.3% | 26.9% | 26.0% | 30.4% | 23.5% |
| it rammed another of her dragons | 5.2% | 5.6% | 3.3% | 7.0% | 6.2% | 5.2% |
| it left | 56% | 65% | 62% | 49% | 53% | 48% |

An intruder near a top-three queen is rammed by one of her team three to four times as often as one near ours. No team escorts its queen (A2 found that); this is ordinary contact trading that happens to take place near her, and ours does little of it (`deep-read-3.md`).

**Circling.** A queen is "on a loop" in a round if her head used 4 or fewer cells in the 12 rounds ending there.

| | rounds on a loop | queens with a loop of 20 or more rounds | loop rounds with an enemy head in view | rammed within 3 rounds of being on a loop |
|---|---|---|---|---|
| test4 against meow | 25.2% | 84 of 154 | 184 | 0 |
| test4 against the top three | 22.1% | 44 of 78 | 86 | 1 |
| SSS on weakhold | 46.2% | 21 of 28 | 338 | 2 |
| SSS, all maps | 5.2% | 42 of 503 | 1,216 | 17 |
| forgot | 2.4% | 44 of 632 | 534 | 8 |
| Vibing++ | 2.4% | 20 of 502 | 1,577 | 5 |
| meow live, rules on | 0.3% | 0 of 175 | 21 | 2 |
| meow live, rules off | 11.2% | 15 of 100 | 258 | 2 |

So the teammate's idea is what test4 does in every game: split once at round 0 or 1, then walk N, E, S, W on four cells at length 2 (game 3). SSS does it on weakhold and Portals. Against the top three, who ram a queen in view every time, test4's queen is alive at the end in 21 of 78 games and dies 3.1 times per 1,000 queen-rounds (rams 2.1): half our rate, and at the level of the top three's own queens. Only 1 of her 38 rammed deaths against them came within three rounds of the loop, 4 more within 20 rounds; 24 of the 38 are cornered deaths away from the loop.

**Can a 2-long queen on a loop be caught? From the rules:**

- She moves before every enemy. An enemy with a reach of r rams her only if its head is within r free steps of hers after her move.
- One 2-long (reach 1). At the start of her turn its head can be on the cell next to hers. One of her four sides is her own tail, one is that head, and the two others are two steps from that head, never next to it. If one of those two is free she steps there and is out of reach. One 2-long alone can never catch a 2-long queen in open water. It needs kelp, a body or a second dragon to take those two cells (game 14: a wall took them).
- One 3-long (one free step, one paid). If she steps straight away each round the distance after her move never shrinks: it closes one step free, she opens one. It catches her only if she steps toward it or sideways, or has no step away.
- Two 2-longs catch her in the open when they stand on the two cells diagonally ahead of her head: each covers the cell in front and one flank. One on a forward diagonal with kelp or a body on the other flank does the same (game 17).
- On a strict 4-cell loop her next cell is known. Any dragon that stands next to that cell after she has stepped onto it rams her, so one 2-long is enough if she keeps looping. If she leaves the loop when a head comes within two or three steps, the rules above apply and one small dragon is not enough.
- A dragon of 5 or more reaches 5 cells and can ram from outside her view; no loop helps against it.

**Checked against cases.** One more game was read for this, 1054795 (Default, test4 against Vibing++): test4's queen walks W, N, E, S on (4..5, 14..15) from round 120 to 146. At round 147 a Vibing++ 3-long comes into view 3 steps east. She breaks the loop: north, then west, both safe. At round 149 she steps south, back onto her loop cell (4,14), two steps from the 3-long, and is rammed with `WW`; north and west were safe. So the loop itself did not kill her; coming back to it did. In our games no hunter of ours ever tested a test4 loop: 184 loop rounds with one of our heads in view, no ram.

### g. What it is worth

[`d_worth.py`, `worth.txt`]

Only one kind of game can flip without changing anything else on the board: a round-500 loss in which both queens are dead. Had ours been alive, the queen rule gives us the game. There are 102 such losses (69 for the live bot). Three readings:

1. **Strict.** She does not die that way and then lives to the end: the game flips.
2. **Top-three survival.** She does not die that way, and from that round on she lives as often as a top-three queen that is alive at that round, on that map-size class and in that economy band (own / enemy total length at that round: under 0.67, 0.67 to 1, 1 to 1.5, over 1.5). For example a top-three queen alive at round 100 lives to the end in 19% of games when her team is under 0.67, 38% at 0.67 to 1, 47% at 1 to 1.5 and 60% above; on large maps 29% over all bands.
3. **Our own other deaths.** She does not die that way but stays exposed to every other kind of death at our own rates for that map-size class and round band.

| Family of death | deaths | reading 1: flips | reading 2: expected flips | reading 3: expected flips | points of win rate (1 / 2 / 3) |
|---|---|---|---|---|---|
| rammed: stepped or stayed in | 104 | 26 | 7.4 | 2.4 | +6.5 / +1.9 / +0.6 |
| rammed: cornered | 116 | 29 | 8.4 | 4.1 | +7.2 / +2.1 / +1.0 |
| rammed: unseen | 31 | 14 | 3.7 | 0.9 | +3.5 / +0.9 / +0.2 |
| boxed in by bodies | 61 | 17 | 5.1 | 0.4 | +4.2 / +1.3 / +0.1 |
| boxed in: terrain | 30 | 8 | 3.3 | 0.4 | +2.0 / +0.8 / +0.1 |
| own ram | 19 | 8 | 2.4 | 0.0 | +2.0 / +0.6 / +0.0 |
| all | 362 | 102 | 30.4 | 8.2 | +25.4 / +7.6 / +2.0 |
| the four she controls herself (first, fourth, fifth, sixth row) together, with only cornered and unseen rams left in reading 3 | 214 | 59 | 18.3 | 8.7 | +14.7 / +4.6 / +2.2 |

The live bot alone (275 games, 77 won): stepped or stayed in 14 / 4.0 / 1.3 games; cornered 21 / 6.3 / 3.1; unseen 11 / 2.6 / 0.7; boxed by bodies 11 / 3.4 / 0.4; terrain 6 / 2.6 / 0.2; own ram 6 / 1.8 / 0.0; all 69 / 20.8 / 5.6 (+25.1 / +7.6 / +2.0 points); the four she controls together 37 / 11.9 / 5.5 (+13.5 / +4.3 / +2.0).

Reading 1 is an upper bound nobody will reach. Reading 3 is so low because a queen saved at round 85 on Around UNSW has a 1% chance to see round 500 at our present death rates. The honest range for all four of her own families together is plus 2 to plus 5 points of win rate on 28%.

Not in these counts: three round-500 losses with her queen alive in which our queen, when she died, was already longer than her queen at the end: game 29 (990346: ours 57 at round 385, hers 3), 990234 (Trauma: ours 28 at round 460, hers 5) and 1053389 (Trauma: ours 27 at round 424, hers 19). The first is a cut; the second is a fed queen cornered by a 5-long right after her own five-step move; the third is a fed queen rammed by a 4-long she could not see. Each is a win thrown away within the last 120 rounds.

### h. The rule

See section 7.
