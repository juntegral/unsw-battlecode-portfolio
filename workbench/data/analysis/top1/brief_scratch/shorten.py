from pathlib import Path
p=Path('data/analysis/top1/TEAM-BRIEF.md')
s=p.read_text()
def section(number,text):
 global s
 start=s.index(f'## {number}. ')
 end=s.index(f'## {number+1}. ',start)
 s=s[:start]+text.strip()+'\n\n'+s[end:]
section(1,'''## 1. Queen steps next to an enemy head

Card #39: Zhe raises the queen's threat multiplier from 1 to 4 and penalises stepping beside an enemy head (brief settings). The study measures full one-turn reach, including paid steps and pearls eaten en route.

### What the data says

- A safe alternative existed in **104/362 queen deaths**: 66 stepped into visible reach, 38 stayed there. In 90/104, the safe step had room behind it and crossed no portal. Top three: 59 stepped in, 53 stayed in. Samples: ours 401 games; top three 1,637. Source: `deep-read-4.md` §2.
- Against test4+WHQ, voluntary exposure was ours **2.6 versus top three 0.4 per 1,000 queen-rounds**; no-safe-step turns were 2.5 versus 2.2. Samples: 313 ours, 108 top-three games. Source: `deep-read-4.md` §§1–2.
- Across all opponents, voluntary exposure per 1,000 queen-rounds was ours 2.7, opponents 1.5, forgot 0.8, SSS 0.6, Vibing++ 1.1. Rams punished 71 / 16 / 44 / 47 / 32% of these turns. Samples: 401 / 401 / 632 / 503 / 502 games. Sources: `REPORT.md` §5; `deep-read-4.md` §2.
- Killers in the 66 stepped-in deaths were length 2 / 3 / 4 in 27 / 25 / 14 cases; none longer. Attacks used at least two steps in 48 cases. Our queen ate on the fatal step in only 1. Source: `deep-read-4.md` §§2, 4.1.
- In rounds 0–49 / 50–99 / 100–299 / 300+, stepped-in deaths were 15 / 22 / 26 / 3; stayed-in deaths 7 / 11 / 19 / 1, across 401 games. In the newer guard trial, enemy-initiated rams killed 16/30 live queens and 18/30 candidate queens; candidate killers were length 2 / 3 / 5 in 5 / 12 / 1 cases. Sources: `deep-read-4.md` §2; `kg34b-analysis/summary.md`, test4 + WeHaveQuizzes.
- For queens at most length 4, rams per 1,000 queen-rounds at 0–5 / 6–10 / 11–15 / 16–25 / 26+ path steps from spawn were ours 1.8 / 3.0 / 5.5 / 8.1 / 8.6; SSS 0.8 / 1.6 / 1.7 / 2.9 / 2.5; forgot 1.1 / 2.4 / 4.8 / 4.5 / 4.0; opponents 0.6 / 0.6 / 1.4 / 1.6 / 1.4. Ours spent 44% of rounds beyond 10 steps, SSS 45%. Same game groups above, filtered by length. Source: `deep-read-4.md` §5c.

### What the top teams actually do

In selected close turns, Vibing++ moved away from a nearby head in 151/151; SSS in 36/39, with the others forced or harmless. Forgot moved nearer in 11/88, sometimes by returning to a loop. They sometimes pay a segment to escape. Sources: `deep-read.md` §d; `deep-read-2.md` §8.

A penalty on adjacent cells does not cover every observed sprint. The study's strict preference for an unreachable cell is a proposed design, not recovered top-team code. Source: `deep-read-4.md` §7.1.

### Replays to open

Sources: `deep-read-4.md` §§3, 4.1, 4.4; `deep-read-2.md`, game 5.

| Link | Map | Who against whom | Rounds | What you will see |
|---|---|---|---|---|
| [1045200](https://game.battlecode.au/visualiser?match=1045200) | Devil | meow vs test4 | 18 | Steps beside a length-2 head despite two safe exits. |
| [980372](https://game.battlecode.au/visualiser?match=980372) | Around UNSW | meow vs 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿 | 92, 93, 94 | Two safe loop steps, then a return within sprint reach. |
| [1053773](https://game.battlecode.au/visualiser?match=1053773) | Australia | meow vs WHQ | 60–74 | Followed along a wall; the only roomy safe exit is a portal. |
| [1052766](https://game.battlecode.au/visualiser?match=1052766) | Trauma | meow vs test4 | 445 | A fed queen dies to a head outside her initial view. |
| [1060356](https://game.battlecode.au/visualiser?match=1060356) | Australia | SSS vs bread first search | 143 | Length-8 attacker pays for a six-step queen ram. |

### Not known

The later red team counts 106 avoidable rams versus 104, and 2.45 voluntary exposures per 1,000 queen-rounds versus 2.66. It uses the board after her move; the earlier read uses the board before it. Source: `redteam.md`, Candidate 2 A.

Safe-step queens survived to the end after only 9% of 288 turns starting in reach and 6% of 922 starting outside. The earlier core-rule estimate was +0.6 to +1.9 percentage points; the later report gives +0.3 to +1.5 for the broader “queen is never spent” candidate. Neither tests #39's exact multiplier. Sources: `deep-read-4.md` §7.4; `redteam.md`, Candidate 2 B/C; `REPORT.md` §4.''')
section(2,'''## 2. Queen walks into dead ends or gets boxed in

Brief settings: #36 uses a 6000 dead-end penalty, length + 8 room threshold and seen tiles only. PR #37, merged, makes a stuck queen shed 2 tail segments and wait. The study's room tests differ.

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
| [1053032](https://game.battlecode.au/visualiser?match=1053032) | Slithery Fight | meow vs WHQ | 0, 3 | Opening cut, then a queen trapped by allies. |
| [1125139](https://game.battlecode.au/visualiser?match=1125139) | Slithery Fight | meow wait vs WHQ | 0–9, 208 | Tail shedding avoids the opening death; later ram. |
| [1045387](https://game.battlecode.au/visualiser?match=1045387) | Portals | meow vs WHQ | 4, 5, 9 | Queen outgrows a room; child's tail blocks its exit. |
| [1063806](https://game.battlecode.au/visualiser?match=1063806) | Slithery Fight | SSS vs forgot | 489, 490–499 | Fed queen sheds while boxed by her own body. |
| [1067446](https://game.battlecode.au/visualiser?match=1067446) | Maze | forgot vs bread first search | 343 | Tail obstruction clears after one shed. |

### Not known

The study uses a terrain-and-portal dead-end graph and length + 2 for a “roomy” safe step, not #36's seen-only length + 8 test. An earlier no-trap candidate had 15/45 boxed deaths versus live 52/215 against the same opponents; it was not the current card. Source: `deep-read-4.md`, Words and §§2, 5e.

The wait count includes every observed two-segment split, not just the internal wait branch. Its direct collision labels do not reconstruct portal destinations and differ from the study's boxed-in diagnosis. Its live 1/30 own-body deaths and the study's 0/401 own-body-only boxes are different samples and definitions. Sources: `qw37-analysis/summary.md`, opening, test4 + WeHaveQuizzes, Measurement limits; `deep-read-4.md` §2.''')
section(3,'''## 3. Queen loop

Card #38: loop in a quiet open spot when nothing is worth chasing, then leave when a head approaches. The counter calls a round “on a loop” if the head used at most 4 cells in the preceding 12 rounds. Source: `deep-read-4.md` §5f.

### What the data says

- Test4 looped for **25.2%** of queen-rounds against us and **22.1%** against top three; loops lasting at least 20 rounds appeared in 84/154 and 44/78 games. Our live queen: 0.3% and 0/175 with rules on, 11.2% and 15/100 with rules off. Source: `deep-read-4.md` §5f.
- SSS looped for 5.2% overall, with long loops in 42/503 games; on weakhold, 46.2% and 21/28. Forgot and Vibing++ each looped for 2.4%, with long loops in 44/632 and 20/502 games. Source: `deep-read-4.md` §5f.
- Test4 had 184 loop rounds with our heads in view and no ram within 3 rounds of looping. Against top three: 86 and 1. Of its 38 ram deaths against them, 1 was within 3 rounds of a loop, 4 more within 20; 24 were cornered away from the loop. Source: `deep-read-4.md` §5f.
- Other loops were not uniformly safe. SSS / forgot / Vibing++ suffered 17 / 8 / 5 rams within 3 rounds of looping; loop rounds with a visible enemy numbered 1,216 / 534 / 1,577. Same samples above. Source: `deep-read-4.md` §5f.
- Different cells per 25 rounds in rounds 100–149: live meow 19.4, opponents 16.4, forgot 17.6, SSS 18.1, Vibing++ 18.6. Path distance from spawn in rounds 50–99: 14.7 / 12.7 / 15.0 / 12.3 / 16.9. Samples: 275 / 401 / 632 / 503 / 502 games, surviving queen-rounds. Source: `deep-read-4.md` §5c.

### What the top teams actually do

Test4 in 1045200 split at round 0, then looped north/east/south/west at spawn. SSS loops on weakhold and Portals; its Portals example T12 stayed 20–25 path steps from spawn. Sources: `deep-read-4.md` §§4.1, 5c, 5f.

The close-read departure: test4 in 1054795 looped on (4..5, 14..15) at rounds 120–146. A length-3 enemy appeared three steps east at 147. She went north, then west, safely. At 149 she returned south to the loop, two steps from the attacker, and was rammed; north and west remained safe. Source: `deep-read-4.md` §5f.

Rule-based inference: one length-2 attacker cannot catch a length-2 queen in open water if she keeps stepping away. Following a fixed loop exposes a predictable next cell; walls, bodies, another head or a longer attacker change the argument. Source: `deep-read-4.md` §5f.

### Replays to open

Sources: `deep-read-4.md` §§4.1, 5f; `deep-read-2.md`, games 4, 6.

| Link | Map | Who against whom | Rounds | What you will see |
|---|---|---|---|---|
| [1054795](https://game.battlecode.au/visualiser?match=1054795) | Default | test4 vs Vibing++ | 120–146, 147, 149 | Safe departure, fatal return. |
| [1045200](https://game.battlecode.au/visualiser?match=1045200) | Devil | meow vs test4 | 0, 18 | Spawn loop versus our queen entering the centre. |
| [1059840](https://game.battlecode.au/visualiser?match=1059840) | Australia | forgot vs SSS | 160, 208 | The next loop cell becomes attackable. |
| [1067641](https://game.battlecode.au/visualiser?match=1067641) | Islands | forgot vs SSS | 166 | Forgot loops onto a cell beside an attacker. |

### Not known

No controlled loop-versus-roam test or universal departure distance was counted. Leaving at two or three steps is the study's inference. SSS's location-selection rule is unknown. The second read could not explain why forgot kept dangerous loops in some games but moved away in all 18 close turns in 1067667. Sources: `deep-read-4.md` §5f; `deep-read-2.md`, Things I could not determine, item 9.''')
p.write_text(s)
print(len(s))
