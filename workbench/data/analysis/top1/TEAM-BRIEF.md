# Top-team study, 5 Oct: the data sorted by what we are building

What we tried: Read the ladder replays, compare our behaviour with the top teams, then independently recount and challenge the proposed explanations.
Did it work: It found repeatable behaviour differences, but no demonstrated large improvement. The study itself ran no games; its predicted gains remain estimates.
Who decides now: Nobody has to decide anything. This is reference material. Zhe and QWQ pick what is useful; questions about any number go to 준싱, who can have it recounted.

## How to read this

Written 5 October 2026: 2,343 replays, 1,637 top-team and 706 ours; main comparison 401 ours against 2000+ teams, excluding Schooltime. Downloads are labelled 3–4 October. Sources: `REPORT.md` §1; `findings.md`, opening.
Top three = Vibing++, SSS, forgot to mention (“forgot”); ours = meow. Our sample mixes 275 live and 126 candidate games; 313 face test4 or WeHaveQuizzes (“WHQ”). Source: `REPORT.md`, Words, §1.
Queen = lowest-id dragon; leader = longest; feeding = dying to leave corpse pearls; ram = head into head, both die; race = round-500 finish with both queens dead, decided by longest dragon. Source: `REPORT.md`, Words.
Small/big = ≤/>1,200 cells; queen-rule gate = 600; economy read's “large” = >1,500. Queen-round = one round alive; view = 7×7. Sources: `REPORT.md`, Words; `deep-read-3.md`, comparison table; `deep-read-4.md`, Words.
Numbers are replay counts/summaries unless marked inference, estimate, rule or brief setting. Numerical blocks name source files/sections; paths are listed at the end. Later online samples are separate.
The source files are in 준싱's analysis folder (`unsw-swarm`), not in this repo. Ask in Discord and any table, replay list or recount can be posted.

## Contents

| Section | Current work |
|---|---|
| [Queen steps next to an enemy head](#1-queen-steps-next-to-an-enemy-head) | Zhe, #39 queen-safety |
| [Queen walks into dead ends or gets boxed in](#2-queen-walks-into-dead-ends-or-gets-boxed-in) | Zhe, #36 queen-dead-end; QWQ, PR #37 queen-wait, merged |
| [Queen loop](#3-queen-loop) | QWQ, #38 queen-loop |
| [Queen and portals](#4-queen-and-portals) | Zhe and QWQ, portal discussion |
| [Hunting the enemy queen](#5-hunting-the-enemy-queen) | Zhe, #31 queen-hunt |
| [Guards and intruders near our queen](#6-guards-and-intruders-near-our-queen) | 준싱, #34 keep-guards, archived |
| [Small dragons circling instead of finding pearls](#7-small-dragons-circling-instead-of-finding-pearls) | QWQ, #33 blind-circling |
| [Late game: feeding and the race to the longest dragon](#8-late-game-feeding-and-the-race-to-the-longest-dragon) | QWQ, #22 late-feed |
| [Anything else in the study that fits none of the above](#9-anything-else-in-the-study-that-fits-none-of-the-above) | Shared context; no new card |

## 1. Queen steps next to an enemy head

#39 settings: threat multiplier 1→4; penalty beside an enemy head. Study reach includes paid and pearl-funded steps.

### What the data says

- A safe alternative existed in **104/362 queen deaths**: 66 stepped into visible reach, 38 stayed there. In 90/104, the safe step had room behind it and crossed no portal. Top three: 59 stepped in, 53 stayed in. Samples: ours 401 games; top three 1,637. Source: `deep-read-4.md` §2.
- Against test4+WHQ, voluntary exposure was ours **2.6 versus top three 0.4 per 1,000 queen-rounds**; no-safe-step turns were 2.5 versus 2.2. Samples: 313 ours, 108 top-three games. Source: `deep-read-4.md` §§1–2.
- Across all opponents, voluntary exposure per 1,000 queen-rounds was ours 2.7, opponents 1.5, forgot 0.8, SSS 0.6, Vibing++ 1.1. Rams punished 71 / 16 / 44 / 47 / 32% of these turns. Samples: 401 / 401 / 632 / 503 / 502 games. Sources: `REPORT.md` §5; `deep-read-4.md` §2.
- Killers in the 66 stepped-in deaths were length 2 / 3 / 4 in 27 / 25 / 14 cases; none longer. Attacks used at least two steps in 48 cases. Our queen ate on the fatal step in only 1. Source: `deep-read-4.md` §§2, 4.1.
- In rounds 0–49 / 50–99 / 100–299 / 300+, stepped-in deaths were 15 / 22 / 26 / 3; stayed-in deaths 7 / 11 / 19 / 1, across 401 games. In the newer guard trial, enemy-initiated rams killed 16/30 live queens and 18/30 candidate queens; candidate killers were length 2 / 3 / 5 in 5 / 12 / 1 cases. Sources: `deep-read-4.md` §2; `kg34b-analysis/summary.md`, test4 + WeHaveQuizzes.
- For queens at most length 4, rams per 1,000 queen-rounds at 0–5 / 6–10 / 11–15 / 16–25 / 26+ path steps from spawn were ours 1.8 / 3.0 / 5.5 / 8.1 / 8.6; SSS 0.8 / 1.6 / 1.7 / 2.9 / 2.5; forgot 1.1 / 2.4 / 4.8 / 4.5 / 4.0; opponents 0.6 / 0.6 / 1.4 / 1.6 / 1.4. Ours spent 44% of rounds beyond 10 steps, SSS 45%. Same game groups above, filtered by length. Source: `deep-read-4.md` §5c.

### What the top teams actually do

In selected close turns, Vibing++ moved away from a nearby head in 151/151; SSS in 36/39, with the others forced or harmless. Forgot moved nearer in 11/88, sometimes by returning to a loop. They sometimes pay a segment to escape. Sources: `deep-read.md` §d; `deep-read-2.md` §8.

Adjacency penalties do not cover every sprint. Strict safe-cell preference is a study proposal, not recovered code. Source: `deep-read-4.md` §7.1.

### Replays to open

Sources: `deep-read-4.md` §§3, 4.1, 4.4; `deep-read-2.md`, game 5.

| Link | Map | Who against whom | Rounds | What you will see |
|---|---|---|---|---|
| [1045200](https://game.battlecode.au/visualiser?match=1045200) | Devil | meow vs test4 | 18 | Steps beside a length-2 head despite two safe exits. |
| [980372](https://game.battlecode.au/visualiser?match=980372) | Around UNSW | meow vs 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿 | 92, 93, 94 | Two safe loop steps, then a return within sprint reach. |
| [1053773](https://game.battlecode.au/visualiser?match=1053773) | Australia | meow vs WHQ | 60–74 | Followed along a wall; the only roomy safe exit is a portal. |

### Not known

The later red team counts 106 avoidable rams versus 104, and 2.45 voluntary exposures per 1,000 queen-rounds versus 2.66. It uses the board after her move; the earlier read uses the board before it. Source: `redteam.md`, Candidate 2 A.

Safe-step queens survived to the end after only 9% of 288 turns starting in reach and 6% of 922 starting outside. The earlier core-rule estimate was +0.6 to +1.9 percentage points; the later report gives +0.3 to +1.5 for the broader “queen is never spent” candidate. Neither tests #39's exact multiplier. Sources: `deep-read-4.md` §7.4; `redteam.md`, Candidate 2 B/C; `REPORT.md` §4.

## 2. Queen walks into dead ends or gets boxed in

Brief settings: #36 uses penalty 6000, room length + 8, seen tiles only. Merged PR #37 sheds 2 tail segments to wait. Boxed = no free adjacent cell; cut = keep 2–3 and give the rest to a child.

### What the data says

- Our **91/401 boxed deaths** split into: cut then stuck 14; recent split child on exit 11; another allied head 20; another allied body 14; enemy body 2; own body alone outside a terrain dead end 0; terrain dead end 30. Cut-first takes precedence over body owner. Source: `deep-read-4.md` §2, boxed-in table.
- Boxed deaths were ours 91, opponents 110, forgot 52, SSS 39, Vibing++ 115; terrain subsets 30 / 37 / 29 / 15 / 21. Samples: 401 / 401 / 632 / 503 / 502 games. Source: `deep-read-4.md` §2.
- Of our 30 terrain deaths, she ate inside in 26 and split inside in 18. A roomier side existed in 21 when room fell below 12 cells. In 12/20 nose-to-nose deaths, an ally took the previously open exit after her move. Source: `deep-read-4.md` §2.
- We made 40 queen cuts from length at least 6 in 37 games, giving away 907 segments. SSS and forgot made no such cuts in 503 and 632 games. Forgot's long queens survived 184/207 shedding episodes. Source: `deep-read-4.md` §§1, 7.3.
- With queen rules off on maps at most 600 cells, live-bot deaths were 10.7 per 1,000 queen-rounds and final survivors 2/100; with rules on, 5.0 and 25/175. Across all builds, rules-off maps contained 21/30 terrain deaths and 17/19 queen-initiated rams. Ten own rams had a safe alternative. Source: `deep-read-4.md` §§2, 5e.
- In the later Slithery Fight wait test, all three live queens cut 25→2+23 at round 0 and died at 3. All three candidates shed 2 repeatedly; later deaths were at 269 against test4, 208 against WHQ, 78 against dev test 1 :P. Source: `qw37-analysis/summary.md` §§5–6, three pairs within 90 games.
- Whole-sample queen deaths were live 26/30 versus wait 27/30 against test4+WHQ; 14/15 versus 13/15 against dev test 1. Candidate sequences of 11 consecutive sheds occurred twice and once, respectively; live groups had only isolated events. Source: `qw37-analysis/summary.md`, both opponent sections.

### What the top teams actually do

SSS and forgot keep the head still by shedding a short tail child each turn. This can clear the tail, wait for an ally or preserve length until the finish. Forgot shed 77→75 when its tail blocked it in 1067446; in 1063806 its fourth segment blocked it, and shedding 82→62 through rounds 490–499 did not clear the box. Source: `deep-read-2.md` §3.

Vibing++ cuts before the segment touching its head. At the Slithery Fight start it cut 25→3+22; the child died and the queen ate 7/11 dropped pearls. A queen too short to split can still die under either behaviour. Source: `deep-read.md` §e.

### Replays to open

Sources: `deep-read-4.md` §§3, 4.5; `deep-read-2.md`, games 2, 11; `qw37-analysis/summary.md` §§5–6.

| Link | Map | Who against whom | Rounds | What you will see |
|---|---|---|---|---|
| [1125139](https://game.battlecode.au/visualiser?match=1125139) | Slithery Fight | meow wait vs WHQ | 0–9, 208 | Tail shedding avoids the opening death; later ram. |
| [1045387](https://game.battlecode.au/visualiser?match=1045387) | Portals | meow vs WHQ | 4, 5, 9 | Room outgrown; child blocks exit. |
| [1063806](https://game.battlecode.au/visualiser?match=1063806) | Slithery Fight | SSS vs forgot | 489, 490–499 | Fed queen sheds while boxed by her own body. |
| [1067446](https://game.battlecode.au/visualiser?match=1067446) | Maze | forgot vs bread first search | 343 | Tail obstruction clears after one shed. |

### Not known

The study uses a terrain-and-portal dead-end graph and length + 2 for a “roomy” safe step, not #36's seen-only length + 8 test. An earlier no-trap candidate had 15/45 boxed deaths versus live 52/215 against the same opponents; it was not the current card. Source: `deep-read-4.md`, Words and §§2, 5e.

The wait count includes ordinary two-segment splits. Collision labels omit portal reconstruction and differ from boxed-in diagnoses. Its live 1/30 own-body deaths and the study's 0/401 own-body-only boxes are different samples and definitions. Sources: `qw37-analysis/summary.md`, opening, test4 + WeHaveQuizzes, Measurement limits; `deep-read-4.md` §2.

## 3. Queen loop

#38 loops in quiet open space and leaves for approaching heads. Counter: at most 4 cells used in the preceding 12 rounds. Source: `deep-read-4.md` §5f.

### What the data says

- Test4 looped for **25.2%** of queen-rounds against us and **22.1%** against top three; loops lasting at least 20 rounds appeared in 84/154 and 44/78 games. Our live queen: 0.3% and 0/175 with rules on, 11.2% and 15/100 with rules off. Source: `deep-read-4.md` §5f.
- SSS looped for 5.2% overall, with long loops in 42/503 games; on weakhold, 46.2% and 21/28. Forgot and Vibing++ each looped for 2.4%, with long loops in 44/632 and 20/502 games. Source: `deep-read-4.md` §5f.
- Test4 had 184 loop rounds with our heads in view and no ram within 3 rounds of looping. Against top three: 86 and 1. Of its 38 ram deaths against them, 1 was within 3 rounds of a loop, 4 more within 20; 24 were cornered away from the loop. Source: `deep-read-4.md` §5f.
- Other loops were not uniformly safe. SSS / forgot / Vibing++ suffered 17 / 8 / 5 rams within 3 rounds of looping; loop rounds with a visible enemy numbered 1,216 / 534 / 1,577. Same samples above. Source: `deep-read-4.md` §5f.
- Different cells per 25 rounds in rounds 100–149: live meow 19.4, opponents 16.4, forgot 17.6, SSS 18.1, Vibing++ 18.6. Path distance from spawn in rounds 50–99: 14.7 / 12.7 / 15.0 / 12.3 / 16.9. Samples: 275 / 401 / 632 / 503 / 502 games, surviving queen-rounds. Source: `deep-read-4.md` §5c.

### What the top teams actually do

Test4 in 1045200 split at round 0, then looped north/east/south/west at spawn. SSS loops on weakhold and Portals; its Portals example T12 stayed 20–25 path steps from spawn. Sources: `deep-read-4.md` §§4.1, 5c, 5f.

The close-read departure: test4 in 1054795 looped on (4..5, 14..15) at rounds 120–146. A length-3 enemy appeared three steps east at 147. She went north, then west, safely. At 149 she returned south to the loop, two steps from the attacker, and was rammed; north and west remained safe. Source: `deep-read-4.md` §5f.

Rule inference: a length-2 queen can escape one length-2 attacker in open water. A fixed loop, obstacles or more reach change that. Source: `deep-read-4.md` §5f.

### Replays to open

Sources: `deep-read-4.md` §§4.1, 5f; `deep-read-2.md`, games 4, 6.

| Link | Map | Who against whom | Rounds | What you will see |
|---|---|---|---|---|
| [1054795](https://game.battlecode.au/visualiser?match=1054795) | Default | test4 vs Vibing++ | 120–146, 147, 149 | Safe departure, fatal return. |
| [1059840](https://game.battlecode.au/visualiser?match=1059840) | Australia | forgot vs SSS | 160, 208 | The next loop cell becomes attackable. |

### Not known

No controlled loop comparison or universal departure distance. Leaving at two or three steps is inference; SSS's location rule is unknown. The second read could not explain why forgot kept dangerous loops in some games but moved away in all 18 close turns in 1067667. Sources: `deep-read-4.md` §5f; `deep-read-2.md`, Things I could not determine, item 9.

## 4. Queen and portals

### What the data says

- Portal sample: **2,388 unique inputs; 1,947 portal-map games, 3,894 queen-games**, including Schooltime, both sides and 45 added live games. Source: `queen-portals/summary.md`, opening.
- Jumping queens on Portals: ours 45/45, top three 44/108, other 55/141; Prisoners Dilemma 19/19, 34/106, 15/109. On Stripes ours jumped less: 36/49 versus 88/99 and 119/144. Source: `queen-portals/games.json`, map/tag recount below.
- Ours never jumped on Default (0/44), Queen Of Spades (0/40) or Trophy (0/50); top three did in 34/103, 15/89 and 11/104. Maze: 10/42 versus 34/98. Source: `queen-portals/games.json`, recount below.
- Elimination, all tags and unique games: Portals 1/147; Prisoners Dilemma 106/117; Stripes 144/146; Around UNSW 0/143; Slithery Fight 0/144. This means either side wiped out. Source: `queen-portals/games.json`, per-map recount.
- On maps at most 600 cells, death within 10 rounds of any jump affected ours 63/100 jumping queens, top three 53/166, other 86/189. Per individual jump: 70/267, 68/764, 97/703. Repeated jumps can precede the same death. Source: `queen-portals/summary.md` §§3–4, Fate.
- Final survivors among those jumping queens: 9/100, 51/166, 36/189; among non-jumpers: 0/13, 69/147, 75/205. These groups are unmatched. Source: `queen-portals/summary.md` §§3–4.

Recount source: `data/analysis/queen-portals/games.json`, fields `map`, `end`, queen `tag`, `jumps`, `win`. Q = queens; G = distinct games within a tag. Wins use queen-games; elimination uses unique games, even when both queens have the same tag. Tags overlap. “Other” means all remaining teams. A dash means no sample. Wins are shown as counts; jump and elimination columns include shares.

| Map | Tag | Queens Q; games G | Any jump | Wins, jump | Wins, no jump | Elimination, unique games |
|---|---|---|---|---|---|---|
| Around UNSW | ours | 49; 49 | 0/49 (0.0%) | — | 14/49 | 0/49 (0.0%) |
| Around UNSW | top three | 104; 89 | 2/104 (1.9%) | 2/2 | 57/102 | 0/89 (0.0%) |
| Around UNSW | other | 133; 127 | 3/133 (2.3%) | 2/3 | 68/130 | 0/127 (0.0%) |
| Australia | ours | 43; 43 | 0/43 (0.0%) | — | 2/43 | 2/43 (4.7%) |
| Australia | top three | 113; 97 | 0/113 (0.0%) | — | 71/113 | 1/97 (1.0%) |
| Australia | other | 134; 127 | 11/134 (8.2%) | 7/11 | 65/123 | 3/127 (2.4%) |
| Autarky | ours | 26; 26 | 0/26 (0.0%) | — | 18/26 | 15/26 (57.7%) |
| Autarky | top three | 102; 87 | 0/102 (0.0%) | — | 70/102 | 72/87 (82.8%) |
| Autarky | other | 112; 104 | 15/112 (13.4%) | 3/15 | 29/97 | 78/104 (75.0%) |
| Default | ours | 44; 44 | 0/44 (0.0%) | — | 29/44 | 30/44 (68.2%) |
| Default | top three | 103; 90 | 34/103 (33.0%) | 22/34 | 40/69 | 50/90 (55.6%) |
| Default | other | 141; 129 | 13/141 (9.2%) | 9/13 | 44/128 | 78/129 (60.5%) |
| Islands | ours | 55; 55 | 1/55 (1.8%) | 0/1 | 2/54 | 20/55 (36.4%) |
| Islands | top three | 113; 95 | 4/113 (3.5%) | 3/4 | 66/109 | 9/95 (9.5%) |
| Islands | other | 146; 137 | 9/146 (6.2%) | 5/9 | 81/137 | 27/137 (19.7%) |
| Maze | ours | 42; 42 | 10/42 (23.8%) | 4/10 | 12/32 | 0/42 (0.0%) |
| Maze | top three | 98; 85 | 34/98 (34.7%) | 20/34 | 35/64 | 2/85 (2.4%) |
| Maze | other | 124; 118 | 29/124 (23.4%) | 12/29 | 49/95 | 2/118 (1.7%) |
| Portals | ours | 45; 45 | 45/45 (100.0%) | 13/45 | — | 0/45 (0.0%) |
| Portals | top three | 108; 92 | 44/108 (40.7%) | 24/44 | 37/64 | 1/92 (1.1%) |
| Portals | other | 141; 130 | 55/141 (39.0%) | 25/55 | 48/86 | 1/130 (0.8%) |
| Prisoners Dilemma | ours | 19; 19 | 19/19 (100.0%) | 13/19 | — | 15/19 (78.9%) |
| Prisoners Dilemma | top three | 106; 91 | 34/106 (32.1%) | 19/34 | 43/72 | 85/91 (93.4%) |
| Prisoners Dilemma | other | 109; 101 | 15/109 (13.8%) | 7/15 | 35/94 | 90/101 (89.1%) |
| Queen Of Spades | ours | 40; 40 | 0/40 (0.0%) | — | 11/40 | 32/40 (80.0%) |
| Queen Of Spades | top three | 89; 75 | 15/89 (16.9%) | 13/15 | 33/74 | 61/75 (81.3%) |
| Queen Of Spades | other | 107; 103 | 17/107 (15.9%) | 10/17 | 51/90 | 82/103 (79.6%) |
| Schooltime | ours | 47; 47 | 0/47 (0.0%) | — | 15/47 | 0/47 (0.0%) |
| Schooltime | top three | 107; 91 | 0/107 (0.0%) | — | 77/107 | 0/91 (0.0%) |
| Schooltime | other | 134; 127 | 0/134 (0.0%) | — | 52/134 | 0/127 (0.0%) |
| Slithery Fight | ours | 50; 50 | 0/50 (0.0%) | — | 14/50 | 0/50 (0.0%) |
| Slithery Fight | top three | 106; 88 | 5/106 (4.7%) | 4/5 | 59/101 | 0/88 (0.0%) |
| Slithery Fight | other | 132; 125 | 5/132 (3.8%) | 1/5 | 66/127 | 0/125 (0.0%) |
| Stripes | ours | 49; 49 | 36/49 (73.5%) | 16/36 | 0/13 | 49/49 (100.0%) |
| Stripes | top three | 99; 85 | 88/99 (88.9%) | 67/88 | 5/11 | 84/85 (98.8%) |
| Stripes | other | 144; 131 | 119/144 (82.6%) | 53/119 | 5/25 | 130/131 (99.2%) |
| Trauma | ours | 52; 52 | 0/52 (0.0%) | — | 19/52 | 3/52 (5.8%) |
| Trauma | top three | 103; 89 | 0/103 (0.0%) | — | 70/103 | 1/89 (1.1%) |
| Trauma | other | 145; 135 | 7/145 (4.8%) | 2/7 | 59/138 | 4/135 (3.0%) |
| Trophy | ours | 50; 50 | 0/50 (0.0%) | — | 37/50 | 49/50 (98.0%) |
| Trophy | top three | 104; 86 | 11/104 (10.6%) | 8/11 | 51/93 | 85/86 (98.8%) |
| Trophy | other | 126; 120 | 4/126 (3.2%) | 2/4 | 42/122 | 118/120 (98.3%) |

### What the top teams actually do

On Stripes, forgot crossed into a fountain pocket at round 8 and ate at 10–11. Ours stood beside the door at 7, crossed at 18 in one read game and never in the other. The initial explanation blamed a queen ban; the read corrected this because that ban was off. Source: `deep-read-3.md`, question b, point 5.

Portals has disconnected homes; survival there does not require reaching the opponent. Conversely, in Australia game 1053773 a portal was the only roomy safe escape from a ram. Source: `deep-read-4.md` §§4.1, 5e.

### Replays to open

Sources: `queen-portals/summary.md`, Raw event hand-checks, and `queen-portals/games.json` for opponents; `deep-read-4.md` §§3–4.1, 4.5.

| Link | Map | Who against whom | Rounds | What you will see |
|---|---|---|---|---|
| [1045387](https://game.battlecode.au/visualiser?match=1045387) | Portals | meow vs WHQ | 4, 5, 9 | Entry into the pearl room, a split, then a blocked portal exit. |
| [1053773](https://game.battlecode.au/visualiser?match=1053773) | Australia | meow vs WHQ | 74 | A portal was the only roomy safe alternative to a ram. |
| [980157](https://game.battlecode.au/visualiser?match=980157) | Stripes | meow vs life is NP hard | 18, 33 | Our queen jumps, then dies to an enemy ram fifteen rounds later. |
| [1006642](https://game.battlecode.au/visualiser?match=1006642) | Default | meow vs Vibing++ | 19, 162 | Vibing++ jumps; its later boxed death is outside the short death windows. |

### Not known

Frequent jumpers have more opportunities for a jump near death; one death can appear after several jumps. No matching by map, opponent, build or lifespan was done. The round-100 subset uses eventual jumping, even after that round. These are not causal estimates. Source: `queen-portals/summary.md`, Input checks and limits.

The detector misses ordinary-distance-one crossings and fatal entries without a landing update. Necessity, actual visibility and usefulness were not measured; distances ignore walls and portal shortcuts. The data settle neither a universal ban nor a need for every small-map queen to cross. Source: `queen-portals/summary.md`, Input checks and limits.

## 5. Hunting the enemy queen

Card #31 chases and pings. The study's runner-up takes an immediate visible ram at any attacker length, without adding a chase.

### What the data says

- Visible chances taken, later recount: **ours 99/435, opponents 197/228, Vibing++ 265/266, SSS 250/252, forgot 253/451**. Earlier: 99/446, 197/230, 266/267, 250/254, 254/457. Samples: 401 ours and 502 / 503 / 632 top-team games. The later path test keeps the attacker's body blocked. Sources: `REPORT.md` §4; `hypotheses.md`, Candidate 1 §2; `redteam.md`, Candidate 1 A.
- Ours by attacker length: 2–3 took 87/231, length 4 took 5/39, longer took 7/165. Forgot's short dragons took 136/139 after round 100. Source: `REPORT.md` §4.
- Six of seven Vibing++ close-read kills used length 5–11 and 4–6-step sprints. Three killers were fresh split children that ate nothing on approach. Source: `deep-read.md` §a.
- First scout trial, qh31: wins 10/30 versus live 8/30; queen rams 11 versus 10. Of 338 hunters, 8 rammed her and 36 died in head-ons with other enemies. Source: `hypotheses.md`, Candidate 1 §2, Trials.
- Portal-fix qh31b against test4+WHQ: short-dragon kills 8/30→13/30, wins 8/30→8/30; new killers length 2 / 3 / 4 numbered 5 / 6 / 2. Against dev test 1: kills 1/15→4/15, wins 3/15→1/15. Source: `qh31b-analysis/summary.md`, both opponent sections.
- Pooled test4+WHQ trials, excluding Schooltime: short-dragon chances 15/49→19/20; enemy queens alive 19→16; only-their-queen-alive losses 16→15; wins 16→17, in 56 games per side. Source: `redteam.md`, Candidate 1 F.

### What the top teams actually do

Vibing++ and SSS take visible queen rams with longer dragons too. Forgot differs: before round 100 its short dragons took 47/51 non-outnumbered chances versus 38/127 outnumbered ones. Source: `deep-read-2.md` §1.

Dispatched hunters are inferred from approaching split children; the shared observation is the final visible attack. Source: `deep-read.md` §§a–b.

The report's runner-up estimate was +0.5 to +2 percentage points, most likely +1. Of 75 games with an unused chance, 25 ended in a round-limit loss with their queen alive; the read estimated about 6 flips, 3 needing length-6 or length-8 attackers. This is arithmetic, not a tested gain or a recommendation here. Source: `REPORT.md` §4.

### Replays to open

Sources: `hypotheses.md`, Candidate 1 §2; `deep-read.md` §a; `qh31b-analysis/summary.md`, length ≤4 queen-kill list.

| Link | Map | Who against whom | Rounds | What you will see |
|---|---|---|---|---|
| [1029030](https://game.battlecode.au/visualiser?match=1029030) | Autarky | meow vs WHQ | 234 | A short dragon passes up the adjacent queen; our final longest cannot beat her survival. |
| [1053784](https://game.battlecode.au/visualiser?match=1053784) | Trauma | meow vs WHQ | 448–463 | A longer dragon circles within possible ram range of a fed queen. |
| [1097924](https://game.battlecode.au/visualiser?match=1097924) | Queen Of Spades | meow portal-fix hunt vs WHQ | 90 | A length-3 attacker kills the queen after recent pings. |

### Not known

The study sources cover two builds (qh31, and qh31b with the portal fix). The third build (qh31c: several hunters at once, a shut-in hunter leaves through a portal) ran online on 5 Oct after the study: wins 9/30 against test4+WHQ (live 8/30) and 2/15 against dev test 1 (live 3/15); short-dragon kills of their queen 11/30 and 4/15; 4 or more dragons pinging in 548/2,120 ping rounds (second build 60/1,549); 48 portal jumps by pinging dragons in 30 games, 28 of them on Portals (second build 11 and 1). Source: `qh31c-analysis/summary.md`, also on card #31. The newer summaries include Schooltime; the pooled study excludes it. Sources: `redteam.md`, Candidate 1 F; `qh31b-analysis/summary.md`, opening.

The red team found 99 additional pearl-funded opportunities, none taken by us; opponents took 52/65. The reviewed hunt path omitted this extra reach. We also won 0/49 races with their queen dead before 300 but our length below two thirds of theirs. Longer unrestricted immediate attackers were not tested online. Sources: `redteam.md`, Candidate 1 A; `REPORT.md` §4.

## 6. Guards and intruders near our queen

### What the data says

- Intruders at most length 4 entering within four path steps were rammed by our team **3.7%**, opponents 13.6%, forgot 13.5%, SSS 16.6%, Vibing++ 12.1%. Samples: 401 / 401 / 632 / 503 / 502 games; intruders/game 3.0 / 4.7 / 3.5 / 2.8 / 3.4. Source: `deep-read-4.md` §5f.
- With at least three allies within six steps, the same rates were 9.4 / 26.9 / 26.0 / 30.4 / 23.5%. Yet in 39 close SSS turns, allies moved nearer the intruder 40 times and away 44 times. Sources: `deep-read-4.md` §5f; `deep-read-2.md`, Corrections, item 8.
- Guard-build mean allies in view after 200 rose 0.473→1.141; empty-view rounds fell 830/1,274→647/1,331. Queen deaths stayed 26/30 per build against test4+WHQ. Source: `kg34b-analysis/summary.md`, test4 + WeHaveQuizzes.
- Guard rams: live 1 versus new 0 in 30 games each against test4+WHQ; 2 versus 0 in 15 each against dev test 1. Wins: 8/30→5/30 and 3/15→2/15. Source: `kg34b-analysis/summary.md`, both opponent sections and §6.
- Deaths before 100 / at 100–200 / after 200 were live 13 / 8 / 5 and guard build 16 / 8 / 2, each in 30 test4+WHQ games. Median death rounds: 87 versus 73. Source: `kg34b-analysis/summary.md`, test4 + WeHaveQuizzes.

### What the top teams actually do

No escort was observed. Ordinary nearby dragons ram reachable intruders. In 1067641 an SSS dragon killed a follower at 158, but a longer attacker killed the queen at 166. Source: `deep-read-2.md`, game 6 and §4.

### Replays to open

Sources: `deep-read-2.md`, game 6; `kg34b-analysis/summary.md` §§2, 6 and Raw event hand-checks.

| Link | Map | Who against whom | Rounds | What you will see |
|---|---|---|---|---|
| [1067641](https://game.battlecode.au/visualiser?match=1067641) | Islands | SSS vs forgot | 158, 166 | One follower is removed; another attacker later reaches the queen. |
| [1096729](https://game.battlecode.au/visualiser?match=1096729) | Trauma | meow live vs WHQ | 276, 410 | A counted defensive ram, then the queen's much later death. |
| [1102221](https://game.battlecode.au/visualiser?match=1102221) | Maze | meow guard build vs WHQ | 331 | Two allied heads are nearby at round start; a length-3 enemy still kills her. |

### Not known

“Guard” is a geometric action count, not a named role; nearby suicides do not prove the queen received their pearls. Source: `kg34b-analysis/summary.md`, Measurement limits.

Conditioned on an enemy within three steps, our short queen's same-round ram rate was 10 / 12 / 13 / 19% with 0 / 1 / 2 / 3+ allies within six steps. The later red team therefore rejected the broad company-survival correlation as proof that escorts protect her. Source: `redteam.md`, Candidate 2 B/C.

## 7. Small dragons circling instead of finding pearls

Free pearl = beside a length-2–4 non-queen, no enemy head in view, with an exit behind it (`REPORT.md`, Words).

### What the data says

- No-food-for-20-rounds dragons at round 90 / 140: ours 19/41 and 25/46; test4 20/52 and 31/62; WHQ 20/50 and 25/59. These are mean counts, not a no-pearl-visible loop rate. Large-map samples: ours 111, test4 42 and WHQ 44 against us. Source: `deep-read-3.md`, question b, point 7.
- Undisturbed pearls within six steps were eaten after 2.6 rounds by us in rounds 50–99; test4 3.0, WHQ 3.1, forgot 2.6, SSS 2.6, Vibing++ 2.0. Source: `deep-read-3.md`, question b, large-map sample.
- Parent-child distance five rounds after splitting: ours 6.2, test4 6.1, WHQ 6.4, forgot 6.1, SSS 5.7, Vibing++ 5.9. Children's steps onto unvisited cells: 21 / 21 / 20 / 20 / 18 / 18%. Large maps, rounds 0–149. Source: `deep-read-3.md`, question c.
- Own-half fountains eaten from by 150: ours 62%, opponents 80%, each top team 69%. Enemy-half fountain pearls/game in rounds 50–149: ours 34, test4/WHQ 76 each, forgot 58, SSS/Vibing++ 65 each. Source: `deep-read-3.md`, comparison table, rows 3, 5.
- Live free-pearl take rates on big maps at rounds 140–149 / 150–159 / 200–299: **84 / 64 / 58%**, opponents 86 / 85 / 85%. Small maps at 290–299 / 300–309 / 310–319: 83 / 64 / 51%, opponents 81 / 82 / 80%. All eleven runs in the 401-game sample show the switch. Source: `REPORT.md` §3.2(a).
- In 82 readable earlier-bot games, post-switch small-map take rates at distance 0–3 / 4–6 / 7–9 / 10–12 from the believed leader were 35 / 16 / 19 / 81%. Under 40% named the true longest. Source: `REPORT.md` §3.2(b–c).
- Natural pearls per 50 rounds before→after switching: small-map live cohort 39.5→31.0 (99 games), big-map 81.1→54.0 (75); opponents 51.4→48.7 and 130.6→130.8. Leaders' intake stayed 3.2→3.2 and 4.1→3.8. Source: `REPORT.md` §3.2(d–e).

Large-map means, sources by row: later `deep-read-3.md`, comparison table rows 1–2; earlier `findings.md` §2. Ours has 111 games; the later read's top-team round-300 survivors are forgot 158, SSS 139, Vibing++ 127, but its intake sample is not restricted to survivors. The earlier fact sheet gives round-100 units ours 39, Vibing++ 38, SSS 49, forgot 47; the later read gives 43 / 42 / 54 / 52. Both are retained as different counters, not silently combined.

| Measure | Ours | Opponents | Forgot | SSS | Vibing++ |
|---|---|---|---|---|---|
| Units 100 / 150, later | 43 / 47 | test4 56/62; WHQ 53/59 | 52 / 58 | 54 / 58 | 42 / 50 |
| Natural pearls 0–49 / 50–99 / 100–149, later | 72 / 91 / 79 | test4 76/125/129; WHQ 81/122/133 | 84 / 121 / 117 | 75 / 118 / 122 | 71 / 113 / 121 |
| Units 200 / 300, earlier | 39 / 34 | all 61 / 61 | 57 / 57 | 58 / 59 | 53 / 55 |
| Total length 100 / 200 / 300, earlier | 98 / 116 / 113 | all 138 / 254 / 326 | 117 / 165 / 183 | 130 / 195 / 220 | 105 / 177 / 208 |

### What the top teams actually do

On large maps, live meow rammed in 8% of 9,789 adjacent small-head meetings; opponents 35%, forgot 35%, SSS 41%, Vibing++ 33%. Our share of ram-corpse pearls was 29%, versus top three 49–52%. Source: `findings.md` §6c. The economy read infers that giving way restricts access to food; it is not a direct test of blind search.

They continue eating near the leader. Small-map free pearls within nine cells of a length-10+ leader, rounds 300–399: live meow took 29%, opponents 87%, forgot 96%, SSS 80%, Vibing++ 88%, in the main study sample. Source: `REPORT.md` §3.2(f).

The study's own pick was to remove the pearl zone before feeding, then reserve a smaller area around a visible leader. Its estimate was +0.3 to +2 percentage points, most likely +1; the amended design was never tested. This reports the study's conclusion, not a ranking of cards. Source: `REPORT.md` §§3.1, 3.4, 3.7.

### Replays to open

Sources: `deep-read-3.md`, Islands and Stripes notes; `deep-read-5.md` §3 and games 11–12; `REPORT.md` §3.2(h).

| Link | Map | Who against whom | Rounds | What you will see |
|---|---|---|---|---|
| [1068051](https://game.battlecode.au/visualiser?match=1068051) | Islands | meow trade-on-contact build vs WHQ | 14–26, 20, 140–220 | A camper circles beside an uneaten pearl; later growth stalls after the switch. |
| [1062235](https://game.battlecode.au/visualiser?match=1062235) | Islands | forgot vs WHQ | 100–350 | Forgot replaces losses and keeps eating from its occupied food areas. |
| [1045374](https://game.battlecode.au/visualiser?match=1045374) | weakhold | meow live vs WHQ | 300, 400 | Length lead erodes after the switch, before the final race. |

### Not known

No exact “nothing visible, choose a two-by-two loop” rate or step scores were measured. The Islands camper circles six cells. Early dispersal and undisturbed eating do not establish a general search failure. Source: `deep-read-3.md`, questions b–c and Islands notes.

The later red team rejected “the zone gives the leader nothing”: per small-map race, the final lineage ate 2.4 natural and 3.4 corpse pearls declined in it; 7/41 wins had smaller margins. Removing all reservation risks those pearls. More length also did not establish more wins: the trade build gained 21% big-map length at 300 but won 0/12. Sources: `redteam-2.md` §5; `REPORT.md` §3.7. Neither tests #33 alone.

## 8. Late game: feeding and the race to the longest dragon

Card #22 has feeders die in place and the leader sprint to their corpses. The sources do not test that exact behaviour.

### What the data says

- Races: ours **41/143 wins**, top three 266/447. At round 300, 106/143 of ours had under 0.8 of enemy potential; we won 20, top three 23/94 in that state. Potential = longest plus pearls all other dragons would drop. Source: `deep-read-5.md` opening, §1.
- Under two thirds of enemy total length at 300: ours 168/268 games reaching it, top three 171/1,056; wins within the band 7% versus 15%. At ratio 0.67–1: 26% of 61 versus 48% of 241. Denominators sum the source rows. Source: `REPORT.md` §2.
- Median feeding starts: live meow 401 (105/186 games with starts), forgot 359 (309/400), SSS 301 (291/334), Vibing++ 363 (236/322). Small-map medians: 403 / 372 / 307 / 401. Start = first of three feeder deaths within 15 rounds by a non-queen leader. Source: `deep-read-5.md` §2e.
- Apparent recipients ate 54% of live-meow feeder pearls; other allies 36%, enemy 3.4%, nobody 7%. Recipient shares: forgot 78%, SSS 77%, Vibing++ 77%, opponents 71%. Small-map races from 250; samples 53 / 65 / 42 / 67 / 78. Source: `deep-read-5.md` §2, Tables A1, B2.
- Following the final leader's ancestry instead: it ate 39% of our pearls from deaths by choice after 300 on small maps, opponents 39%, top three 45%; big maps 26 / 16 / 29%. The later report gives 25%. Different definition from apparent recipient above. Sources: `deep-read-5.md` §1; `REPORT.md` §3.6.
- Final longest / final potential, small-map medians: live meow 65%, candidates 71%, forgot 69%, SSS 79%, Vibing++ 59%, opponents 77%. Samples: 53 / 25 / 65 / 42 / 67 / 78 races. Source: `deep-read-5.md` §2, Table A1.
- At level potential before feeding, ours won 11/23 races, top three 99/169. The later red team attributed about 45% of the earlier gap to comparing total length after feeding. Its remaining estimate was about 8 wins across our 143 races at top-three conversion rates, range 0–16. Sources: `deep-read-5.md` §1; `redteam-2.md` §§1, 5.

### What the top teams actually do

Feeders die one to three steps from a larger head. In small-map races, one-step deaths were SSS 65%, forgot 14%, Vibing++ 12%, live meow 5%. The recipient and nearby allies eat the corpse. No remote summons was established. Source: `deep-read-5.md` §2, Table B2.

There was no pre-feeding gathering: heads within 15 cells of the longest at 50 / 25 / 0 rounds before start were forgot 15 / 14 / 13, SSS 18 / 19 / 18, Vibing++ 17 / 15.5 / 15. A clock tied to units or map size is inference; replays cannot distinguish them. Source: `deep-read-5.md` §2e.

Queen feeding differs. Forgot feeds from about 200–225 and reached length 8+ by 300 in 175/189 relevant games. SSS keeps her short and decides later. Vibing++ has both early and late queen-feeding examples; voluntary disposal of a fed queen was not observed. Sources: `findings.md` §6b; `deep-read.md` §f.

### Replays to open

Sources: `deep-read-5.md` §3 and game narratives 1, 8, 15, 22, 24.

| Link | Map | Who against whom | Rounds | What you will see |
|---|---|---|---|---|
| [1023828](https://game.battlecode.au/visualiser?match=1023828) | Maze | meow vs forgot | 325–475, 400 | A stable leader, known by much of the team, receives feeders and wins the race. |
| [1058858](https://game.battlecode.au/visualiser?match=1058858) | Portals | meow passage build vs test4 | 478 | Repeated cuts consume length during a close race. |
| [1063675](https://game.battlecode.au/visualiser?match=1063675) | Around UNSW | meow hunt build vs test4 | 400 | Test4 has much more total length, but meow has the longer leader. |
| [1054770](https://game.battlecode.au/visualiser?match=1054770) | Maze | SSS vs test4 | 300, 400 | SSS builds its leader while total length is comparable. |

### Not known

Earlier leader-cut delay: median 27 rounds, 388 cuts in 78 readable games. Later recount: median 28 among 370 resolved cases, 458 cuts in 82 games—but an older bot. Current live feeding recovered after about 15 rounds, candidates after 10. Growth after cuts was 11.4 versus 11.1 without; the deficit was in windows containing cuts. Source: `redteam-2.md` §5, correcting `deep-read-5.md` §§1, 7.

The race summary says test4 never feeds a leader while its queen lives; its §2e instead records living-queen starts in 38% of 61 starts against us and 12% of 26 against top three. This supports a tendency, not “never.” Earlier feeding, remote collection and faster leader identification were not causally settled. Source: `deep-read-5.md` §§1, 2e.

## 9. Anything else in the study that fits none of the above

### What the data says

- Board walker checked against 81,853 engine steps. Source: `REPORT.md` §1.
- Wins: ours 112/401, top three 1,001/1,637, in different opponent populations. Source: `REPORT.md` §2.
- Only 21/401 of our games faced the top three. Source: `REPORT.md` §6.
- Reachable enemy-leader rams on large maps: ours 20 per 1,000 exposed rounds, top three 21–33. No measured gap. Source: `findings.md` §5.

### What the top teams actually do

Vibing++ split before 4/10 late leader kills in the close reads; the cheap front or new tail-head rammed. Source: `deep-read.md` §g.

### Replays to open

Source: `deep-read.md`, game 3, §g.

| Link | Map | Who against whom | Rounds | What you will see |
|---|---|---|---|---|
| [1067620](https://game.battlecode.au/visualiser?match=1067620) | Australia | Vibing++ vs forgot | 391–392 | Split, then ram with the short front. |

### Not known

Unseen qualifier maps remain unmeasured. These estimates are not trials, and the newer smoke summaries share a live baseline. Sources: `REPORT.md` §6; online summaries, input descriptions.

## Where the full material is

- `data/analysis/top1/REPORT.md` — synthesis and estimates.
- `data/analysis/top1/findings.md` — counts and build inventory.
- `data/analysis/top1/hypotheses.md` — original candidates and examples.
- `data/analysis/top1/redteam.md` — first independent challenge, including queen safety and hunt trials.
- `data/analysis/top1/redteam-2.md` — pearl-zone and race corrections.
- `data/analysis/top1/deep-read.md` — Vibing++ close reads and attack sequences.
- `data/analysis/top1/deep-read-2.md` — SSS and forgot, queen loops, shedding and feeding.
- `data/analysis/top1/deep-read-3.md` — economy and food access.
- `data/analysis/top1/deep-read-4.md` — queen deaths; rule estimates in §7.
- `data/analysis/top1/deep-read-5.md` — feeder pearls, leader ancestry and longest-dragon races; read with the second red team.
- `data/online/smoke/kg34b-analysis/summary.md` — guard test and queen deaths.
- `data/online/smoke/qw37-analysis/summary.md` — wait test, shedding sequences and Slithery Fight starts.
- `data/online/smoke/qh31b-analysis/summary.md` — portal-fix hunt test, pings and queen kills.
- `data/online/smoke/qh31c-analysis/summary.md` — third hunt build: several hunters at once, portal exits.
- `data/analysis/queen-portals/summary.md` — portal definitions, death windows and measurement limits.
- `data/analysis/queen-portals/games.json` — per-game portal recount input.
