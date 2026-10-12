# Top-team study: what the best three teams do that we don't

5 Oct 2026, overnight. 1,754 ladder replays: 1,170 games of the top teams, 586 of ours.

## The 30-second version

**What we studied.** How the three best teams play against teams rated 2000 or more, where we differ from them, and which difference is worth acting on. The best-rated team in the collected games is now Vibing++ (2332); SSS (2300) and "forgot to mention" (2288) are the cross-check.

**The one thing to try.** Ram the enemy queen whenever one of our dragons has a legal ram on her at its turn (a free path to her head, no longer than it can move in one turn), on every map and in every round; then let our 5–9-long dragons walk to her and do it. Today the bot mostly lets the chance go.

**Why.**
- At round 500 a living queen beats a dead one every time: 0 wins in 108 top-team games for the side whose queen was dead while the other's lived, and 0 in 51 for us.
- Their queen survives against us more than against anyone: alive at the end in 41% of our games, 18–31% of the top three's.
- When one of their 2–3-long dragons has a legal ram on the enemy queen at its own turn, Vibing++ and SSS take it 98% of the time (249 of 254). We take it 36% of the time (65 of 183), and with dragons 4 or longer 2% (9 of 466).
- We get the chances: in 132 of our 289 games at least one of our dragons had a legal ram on her, on big maps almost 5 such turns a game.
- In one game (1029030) the opponent's only dragon for the last 250 rounds was a 2-long queen. We had up to 58 dragons. Just before that, in rounds 227–248, one of ours had a legal ram on her seven times (at round 234 she stepped right in front of our 3-long); nobody took it, and we lost on the queen rule.

**How sure.** That kills will go up: very. The gap is 98% against 36%, the two best teams behave the same way (forgot does it two times in three), and a few rules in our code explain it exactly. That wins will go up: yes, but not by much. My estimate is 5 to 8 more wins in 289 games against 2000+ teams (+2 to +3 points), on maps where she can be reached and we are not hopelessly behind. It will not fix Australia or Islands, where the economy is the problem.

**Three things this is not.** It is not a fix for our queen dying (see "Runners-up" and "The queen questions"). It is not something a local win count can confirm, because our local opponents lose their queen anyway. And it is not new as a direction: cards #17 and #31 hunt her too. What is new is the size of the gap, that the first fix is simply taking a legal ram at any length, that for walking to her a 5–9-long dragon is a better tool than a 2–4-long one, and that waiting until our own queen is dead is not needed.

---

## 1. What decides games

Games that reached round 500, counted from each team's side, Schooltime left out (script `endstate.py`, `redteam3.py`).

| At round 500 | Top three | Us |
|---|---|---|
| Own queen alive, theirs dead | 146 of 146 won | 1 of 1 |
| Both alive | 70 of 104 (queen length, or longest if equal) | 2 of 10 |
| Both dead (longest dragon decides) | 196 of 326 = 60% | 28 of 101 = 28% |
| Own dead, theirs alive | 0 of 108 | 0 of 51 |

Share of games in which a queen is alive at the end (all endings, `final_numbers.py`):

| | Own queen alive | Enemy queen alive |
|---|---|---|
| Vibing++ | 28% | 24% |
| SSS | 41% | 18% |
| forgot | 36% | 31% |
| meow | 10% | 41% |

We are worst on both sides of the same rule. On large open maps ours is alive at the end in 0 of 79 games.

One map is special. On **Schooltime** both queens are sealed in a tiny room and always end 3 long (71 of 71 top-team games, 18 of 18 of ours), so the longest dragon decides there. Every queen number in this report leaves Schooltime out.

## 2. Gap table

Means per game, opponents rated 2000+. W and L are Vibing++'s own wins and losses, used as a control: a number that does not separate its wins from its losses is a habit, not a winner. Source: `gap2_large.txt`, `gap2_medium.txt`, `gap2_small.txt` (from `timeline.csv`).

**Large maps (over 1,500 cells)**: Vibing++ 129 games, SSS 135, forgot 131, us 97.

| | Vibing++ | (W / L) | SSS | forgot | meow |
|---|---|---|---|---|---|
| Units at round 100 | 39 | 41 / 36 | 49 | 47 | 38 |
| Units at round 200 | 53 | 57 / 46 | 58 | 57 | 37 |
| Units at round 300 | 55 | 60 / 47 | 59 | 58 | 33 |
| Total length at round 200 | 175 | 190 / 147 | 194 | 168 | 112 |
| Total length at round 300 | 208 | 231 / 165 | 219 | 184 | 110 |
| Natural pearls eaten, rounds 150–200 | 125 | 131 / 114 | 113 | 108 | 50 |
| Rams started, rounds 150–200 | 12.2 | 12.8 / 10.9 | 9.1 | 12.4 | 3.0 |
| Longest at round 300 | 16 | 18 / 14 | 20 | 18 | 14 |
| Longest at round 400 | 35 | 36 / 33 | 42 | 43 | 17 |
| Longest at the end | 57 | 65 / 43 | 56 | 58 | 30 |
| Queen length, rounds 100–200 | 5–8 | | 2–3 | 2–3 | 2–3 |

**Medium maps (701–1,500 cells)**: 106, 108, 120, 85 games.

| | Vibing++ | SSS | forgot | meow |
|---|---|---|---|---|
| Units at round 200 | 37 | 41 | 30 | 27 |
| Total length at round 200 | 98 | 102 | 76 | 66 |
| Rams started, rounds 150–200 | 4.7 | 4.5 | 3.7 | 2.8 |
| Longest at round 400 | 16 | 30 | 29 | 15 |

**Small maps (700 cells or fewer)**: 171, 156, 175, 125 games.

| | Vibing++ | SSS | forgot | meow |
|---|---|---|---|---|
| Units at round 100 | 15 | 17 | 19 | 14 |
| Total length at round 100 | 38 | 42 | 45 | 34 |
| Rams started, rounds 50–100 | 2.5 | 2.2 | 2.1 | 1.5 |
| Games ended by wipe-out | 66% | 67% | 66% | 66% |

**The five largest, most consistent gaps, and whether each is a cause or a consequence**

1. **The big-map economy after round 150.** At round 200 we have 37 units and 112 length; they have 53–58 and 168–194. Our units fall from round 150; theirs stay near 60 until round 300. It separates their own wins from losses (57 against 46 units), so it is a real factor and also a snowball. Already known (card #7). Two things I can add: on medium maps, where our "stop splitting" round is 300 instead of 150, our units keep rising until round 300 and then fall the same way; and card #14 could not see the problem because our bot reaches 60 units locally either way.
2. **Rams started.** Four times fewer on large maps (3 against 9–12 per 50 rounds). It does not separate their wins from losses at all (12.8 against 10.9), so among them it is a shared habit. Already known.
3. **Our queen alive.** 10% at the end against 28–41%. Decisive by rule at round 500. Part cause, part consequence: see section 4.
4. **Their queen rammed.** 0.18 kills per large-map game against 0.58–0.80; of the legal rams a 2–3-long dragon gets, we take 36% and Vibing++ and SSS 98%. This is the chosen hypothesis.
5. **Our queen dying by her own move.** 28% of our games against 4–12% of theirs. See runner-up B.

Late consolidation (longest at round 400: 17 against 35–43) looks large but follows from gap 1: we have half the length to consolidate.

## 3. The chosen hypothesis

> **Ram the enemy queen whenever one of our dragons can reach her; let 5–9-long dragons do the hunting.**
> If, at the start of its own turn, one of our dragons that is not our queen and not our longest dragon has a free path to the enemy queen's head within its one-turn reach, and the sprint costs it no more than 2 segments, it rams her. No map-size condition, no round condition, no "only if our queen is dead". As a second step, a 5–9-long dragon that knows where she is walks to within its reach and strikes from there.

"Reach" is how far a dragon can move in one turn: its free steps plus one step per segment it gives up. Length 2 reaches 1 cell, 3 reaches 2, 4 reaches 3, 5 reaches 5, 6 reaches 6. A dragon sees 3 cells.

### 3.1 We get the chances and do not take them

**Turn by turn (the strictest count).** A **chance** = at the start of a dragon's own turn, so after both queens have already moved that round, there is a path of free cells from its head to the enemy queen's head that is no longer than its reach. It is **taken** if the dragon rams her that turn. Our queen and dragons longer than 12 are not counted. Scripts `extract3.py`, `an3.py`, `an3b.py`.

| Chances taken | Vibing++ | SSS | forgot | meow |
|---|---|---|---|---|
| Attacker 2 long | 57 of 57 | 53 of 55 | 62 of 88 = 70% | 29 of 48 = 60% |
| Attacker 3 long | 80 of 83 = 96% | 59 of 59 | 68 of 107 = 64% | 36 of 135 = 27% |
| Attacker 4 long | 18 of 20 = 90% | 21 of 23 = 91% | 8 of 30 = 27% | 3 of 37 = 8% |
| Attacker 5–9 long | 30 of 107 = 28% | 51 of 176 = 29% | 14 of 138 = 10% | 4 of 296 = 1.4% |
| Needs at most 1 paid step, attacker not the team's longest | 141 of 150 = 94% | 120 of 125 = 96% | 133 of 215 = 62% | 63 of 187 = 34% |

Vibing++ and SSS simply always do it when it is cheap. How much they will pay (top three pooled): free steps only 83% taken, 1 paid step 74%, 2 paid 54%, 3 paid 24%, 4 or more 4%. Ours: 54%, 13%, 8%, 2%, 0%.

We do not lack chances. Share of games with at least one chance: us 43% on maps up to 1,200 cells and 52% on larger ones; the top three 46–51% and 61–77%. Chances per game on the larger maps: us 4.8, them 1.7–2.2 (ours pile up because nobody takes them); we take 14 of 378, they take 28–31%.

**Per approach (a looser count, but it shows where longer dragons matter).** An **approach** = one of our heads comes within 6 steps of their living queen (walls and portals respected); it ends when that dragon dies, moves more than 9 steps away, or she dies. Scripts `approach.py`, `approach3.py`.

| Attacker length when the approach began | Top three: approaches that ended with her rammed | Us |
|---|---|---|
| 2–3 | 473 of 6,514 = 7.3% | 65 of 2,559 = 2.5% |
| 4 | 37 of 319 = 11.6% | 1 of 109 = 0.9% |
| 5–9 | 69 of 246 = 28.0% | 3 of 108 = 2.8% |
| 10+ | 32 of 137 = 23.4% | 2 of 41 = 4.9% |

Per game we make 9.7 approaches (large maps 9.4). Rams on their queen per game:

| | Small | Medium | Large |
|---|---|---|---|
| Vibing++ | 0.54 | 0.65 | 0.71 |
| SSS | 0.53 | 0.56 | 0.80 |
| forgot | 0.43 | 0.36 | 0.58 |
| meow | 0.32 | 0.24 | 0.18 |
| meow, if our approaches converted at top-three rates | 0.32 | 0.41 | 0.45 |

Against the same opponent (test4, 112 of our games and 73 of theirs): they kill her queen 0.48 times a game, we 0.21; she is alive at the end in 29% of their games and 48% of ours.

On maps over 1,200 cells, before round 150, with our own queen still alive: 180 approaches, 0 kills.

### 3.2 Why longer hunters work

| Killer length | Where it stood at the start of the fatal round (top-three queen kills) |
|---|---|
| 2–3 (477 kills) | 1–2 steps away 51%, 3 steps 32%, 4–6 steps 14% |
| 5–9 (96 kills) | 3 steps or closer 11%, 4–6 steps 68%, 7 or more 18% |

A short hunter has to get inside the 3 cells she can see, and she moves first every round (the queens have the lowest ids). A 5-long strikes from 5 steps. On large maps 46% of top-three queen kills are by a dragon 5 or more long; on small and medium maps 4% and 9%.

The step up from short to mid-length attackers is there for each top team (Vibing++ 9% to 27%, SSS 7% to 38%, forgot 6% to 17%), for the rest of the 2000+ field (5–10% to 20–22%), on every map with enough cases, and for short queens before round 300 (8% to 42%).

Card #31's first look shows the other side of this: a 2-long tailed her for 60 rounds, one sat next to her head for three rounds, one followed 3 cells behind for 90 rounds.

### 3.3 Why the bot does not do it (from the code, not from logs)

- `QUEEN_HUNT` is off (`mybot2/main.cpp` line 125), so `mark_hunt_targets()` never marks her.
- `mark_trade_targets()` allows a ram only if `round <= feed_round`, the unit count is high enough, the dragon sees at least as many of our other heads as enemy heads, and the target is "worth" it: at least as long as the attacker on maps up to 1,200 cells, and at least `max(5, own length + 2)` parts on larger maps. A 2–3-long queen does not pass the last test on a large map, and a 3-long of ours does not pass it against a 2-long queen on any map (the one exception is an enemy standing next to one of our 10+ long dragons). Nothing in these tests knows she is the queen.
- Only dragons 4 or shorter trade at all (`is_trader()`, `TRADE_MAX_LENGTH 4`), and after the feeding round (round 400, or 300 when our queen-feeding mode is on) the first test fails for everyone. So our 5–9-long dragons never ram a short queen, and in the last 100 rounds nobody does.
- The ordinary hunt (`HUNT_MIN_PARTS 10`) and the end-game hunt (6 parts) are for big dragons.

The numbers follow the code. Our take-up falls step by step with attacker length: 60% at length 2, 27% at 3, 8% at 4, 1.4% at 5–9. By map class: on maps up to 1,200 cells we take 22% of our chances (top three 40–80%), on larger maps 4% (top three 28–31%).

### 3.4 What it is worth

Round-500 games with the own queen dead at the end (`redteam3.py`):

| | She lived | We rammed her | She died another way |
|---|---|---|---|
| Top three | 0 of 108 | 156 of 242 = 64% | 40 of 84 = 48% |
| Top three, behind on length at round 150 | 0 of 40 | 33 of 65 = 51% | 15 of 35 = 43% |
| Us | 0 of 51 | 12 of 30 = 40% | 16 of 71 = 23% |
| Us, behind at round 150 | 0 of 34 | 4 of 18 = 22% | 9 of 54 = 17% |

The kill does not win the game. It turns a certain loss into a contest of longest dragons, which we win about one time in five when behind and more often when level.

A what-if on our own 289 games (`whatif.py`, `whatif2.py`, `final_numbers.py`), changing nothing but her death:

- 59 round-500 losses had their queen alive. 30 of them flip if she dies (22 because our longest beats their best other dragon, 8 because our own queen was alive).
- Strict count: in 37 games we had a legal ram costing at most 2 paid steps and never rammed her. 9 of those were round-500 losses with her alive, and **6 of the 9 flip** (Slithery Fight 2, Autarky, Prisoners Dilemma, Queen Of Spades, Trauma). With at most 1 paid step it is 5 of 7.
- Looser count: in 11 of the 30 we made at least one approach; giving those approaches the top-three conversion yields **about 8 wins**. The difference is what walking to her would add.
- The other 19 are almost all Trauma and Portals, where she sits behind portals and we were almost never near.
- None of the 12 Australia and Islands losses flips: we were too far behind on length for her death to matter.

So: **5 to 8 wins in 289 games, +2 to +3 points against 2000+ teams**, mostly from Slithery Fight, Prisoners Dilemma, Queen Of Spades, Maze, weakhold, Default and Autarky. It rests on a handful of games and could be 1 or 4.

### 3.5 Replays that show it

- **1029030, Autarky, loss to WeHaveQuizzes on the queen rule.** Our queen is rammed at round 131. From round 250 their only dragon is a 2-long queen. We have 46–58 dragons, total length up to 159, longest 93. Seven turns with a legal ram, none taken: round 227 (#262, 6 long, 4 steps), round 228 (the same dragon, 3 steps), round 234 (she steps from (39,9) to (38,9), directly in front of our 3-long #267 at (38,10), which moves east instead), rounds 236, 238 and 240 (#259, 3 long, 2 steps away), round 248 (#292, 3 long, 2 steps). Every one of these dragons was 3 or longer and she was 2 long, which the trade rule does not allow. One ram would have been a wipe-out win.
- **1053784, Trauma, loss to WeHaveQuizzes on the queen rule (our queen 31, theirs 39).** Rounds 449–463: our 8–9-long #361 has a legal ram on her on six turns (4–5 steps, 2 of them paid). Our own queen was alive, so one ram would have won the game outright.
- **1045197, Queen Of Spades, loss to test4.** 32 chance-turns. Rounds 328 and 329: our 2-long #152 is one step from her head at its own turn, twice. Her fed queen is 23 long; our longest is 9 against their best other dragon 4.
- **1029017, Slithery Fight, loss to test4.** Rounds 335, 401 and 402: our 6-long dragons 2–4 steps from her with a free path. Our longest 60 against their best other dragon 28.
- **990232, Prisoners Dilemma, loss to tungtung67.** Round 13 (our 4-long, 3 steps) and round 222 (our 3-long, 2 steps); she ends 9 long and they have no other dragon left.
- (`out/examples2.txt` lists every such game with rounds and dragon ids.)
- What a kill looks like when the top teams do it: **1053751** round 448 at (7,16), a Vibing++ 3-long comes from 14 steps away in five rounds and rams SSS's 76-long queen; **1056710** round 469, a 13-long sprints 6 steps into a 31-long queen; **1046968** round 306, a forgot 5-long sprints N, N, E, E, S from (22,39) into the Vibing++ queen at (24,38).

## 4. The queen questions from QWQ and Zhe

These are measured on the top-team games, as asked. Scripts: `qan.py`, `an2.py`, `misc.py`, `defend.py`, `qmap.py`.

**Enemy heads near her.** Enemy heads within 8 steps of the queen, large maps, rounds 100–200: Vibing++ 0.49, SSS 0.45, forgot 0.24, us 0.82. It separates their wins from losses too (rounds 50–200, all sizes: 0.3–0.4 in wins, 0.6–0.9 in losses). But relative to her own team our queen is not badly placed: she has 0.6–0.75 of the enemy density of our average dragon, like Vibing++'s (0.6–0.8). Our whole team simply has more enemies around it (1.7 within 8 cells against 1.0–1.3). Only SSS keeps its queen clearly in the quiet part: half the team average.

**How much she moves.** She is not parked. Different cells visited per 100 rounds on large maps: 40–63 for the three, 55–60 for us. Windows of 25 rounds in which she used 10 cells or fewer: 1–8% on medium and large maps for everyone. The exception is SSS on small maps (29% of windows, 22% with 6 cells or fewer). So "stay 2 long and circle on 4 tiles" is real, but it is an SSS small-map habit, not what keeps big-map queens alive.

**Where she sits.** 9–13 cells from her spawn (ours 12–13); in open water as often as ours; within 4 steps of a portal in 5–10% of rounds, same as ours. Nobody camps at a portal.

**How long she is.** SSS and forgot keep her 2–3 long and split her whenever she reaches 4; forgot feeds her from about round 200–250 if she is still alive (9 long by round 300, 19–25 later). Vibing++ keeps her 5–9 long on large maps. In the three games of the close read where no enemy ever came within 6 steps of the Vibing++ queen, she was fed and won the queen rule.

**What happens to small enemies that come near her.** Per approach by an enemy 4 or shorter:

| Victim queen | Intruder rammed by a defender | Queen rammed by it | Queen died another way meanwhile |
|---|---|---|---|
| Vibing++ | 13% | 5.3% | 14% |
| SSS | 17% | 6.3% | 7% |
| forgot | 14% | 6.7% | 11% |
| meow | 5% | 9.6% | 14% |

With three or more allied heads within 6 steps their defenders ram the intruder in 24–27% of approaches and she is rammed in 2–4%. For our queen, allies make no difference (10.4% with three or more, 10.8% with none).

**Found, and still alive?** Not better than ours once it is close. Large maps, chance of being rammed in a round that starts with a small enemy 2 steps away: 76–101 per 1,000 for them, 106 for us; at 3 steps 27–37 against 35. The difference is how often it gets that close: 1.3–2.0% of her rounds for them, 3.6% for us. This agrees with the author's reading that a better queen move only delays it.

**On open big maps nobody's queen lives.** Top-three queens alive at the end: Around UNSW 21%, Australia 27%, Islands 8%. They survive where the homes are separated or defensible (Trauma 93%, Autarky 51%, Tower Defense 49%, Portals 48%, Maze 41%, Slithery Fight 40%, weakhold 38%). Ours is alive in 0% on 10 of the 16 maps.

**How she dies.** Top-three queens are rammed in 45–51% of games. Ours is rammed in 62% and kills herself in another 28%.

## 5. Runners-up

**A. Dragons near our queen ram small enemies that come for her.** Their defenders ram 13–17% of intruders, ours 5%. But the matched check is weak (rammed within 5 rounds: 12.3% with an ally within 3 steps, 14.6% without), the escort toggle changed nothing locally, and pulling allies towards her risks boxing her in. It uses the same line of code as the chosen idea, so it is the natural second step.

**B. Our queen must never die by her own move.** 81 of 289 games (28%): kelp 35, another body 23, a head she rammed 12, her own body 11. Vibing++ 4%, SSS 12%, forgot 5%. In 75 of the 81 she had no free neighbour cell at the start of the round, and no small enemy was within 3 steps in 68. She was 2–3 long in 74, which is why card #25's "split and wait" never fired. 58 happened on a cell with one or two open sides. 49 were on maps of 600 cells or fewer, where our queen rules are off. Portals: 19 of 19 games (9 at round 9–10), on a map where no queen of ours or of the top three was rammed at all and theirs is alive at the end in 48%. Slithery Fight: 7 of 21 games at round 3. Worth about 9 wins in 289 games if she then lived as often as a top-three queen on the same map. Cards #23 and #25 already own this; the numbers are for them.

**C. Keep the queen in the quiet rear of the swarm.** Only SSS does it. Dropped as a recommendation.

**D. Ram their longest dragon late.** In top-team games the side that alone killed the other's leader after round 400 won 51 of 55. But we already take those chances at their rate (20 rams per 1,000 rounds in reach against 22–34). No gap.

## 6. The close read

`deep-read.md` has 15 Vibing++ games with rounds and coordinates. In short: it killed the enemy queen in 8 of 15 (6 of the 8 with a dragon 5–13 long sprinting 4–6 steps); its own queen was rammed in 11 and survived only in the 3 games where no enemy came within 6 steps of her; 7 games were decided by a queen or leader being rammed, 5 by the opening economy, 2 by late feeding, 1 by trades. Its weaknesses: slow openings (5 of 9 losses), a queen it does not treat as special (in 1052703 it split its own living 16-long queen and she died the next round, with the enemy queen already dead), and an unguarded leader (rammed by a 2–4-long dragon from the next cell in three games).

## 7. Limits

- **No sub-sessions.** The plan called for three separate max-effort sessions (close read, hypotheses, red team). The loop guard blocks any shell command that names the loop settings file, which the sub-session command has to do, and I did not route around a guard. I did all three steps myself, in order, at the effort level of this session. The red team is therefore not independent of the author. To offset that, every red-team item is a new measurement made after the hypotheses were written, and the raw outputs are kept.
- **The protagonist changed.** When the study was planned SSS was rank 1; after refreshing the metrics Vibing++ is (2332 against 2300). They are level head to head (41–38). I followed Vibing++ in the close read and report all three teams everywhere else.
- **Observation, not experiment.** Everything here is from ladder replays. The per-chance and per-approach numbers hold the situation equal, not the opponent's skill or our dragons' surroundings.
- **Three ways of counting a chance.** My first pass counted rounds that begin with her inside the reach of one of our heads. That ignores bodies and the fact that she moves first, so it overstates: 10.2 such rounds a game on big maps against 4.8 real chance-turns. The turn-by-turn count is the strict one and is what the estimate uses. It still misses rams made possible by eating a pearl on the way (the top three made 110 queen kills that my strict test did not flag; we made none), so their true take-up is, if anything, higher.
- **Our 2000+ sample is narrow.** 245 of our 307 games are against two teams (WeHaveQuizzes 125, test4 120). Only 5 are against Vibing++ and 17 against forgot.
- **The win estimate is thin.** 5 to 8 wins in 289 games comes from 6 to 11 games. A 30:30 online comparison cannot detect 2–3 points; it can confirm the mechanism.
- **What replays do not show.** Why a dragon moved, what it knew, what the sonar said. I cannot say how a hunter finds the queen, only that it arrives.
- **Self-kills.** Vibing++ and forgot kill trapped dragons with an order that cannot be carried out; the replay records "no action". Some are deliberate, some not, and I cannot tell which.
- **Coverage and checks.** 2 of 1,756 games are left out because of a bug in my own extraction (it trips when a queen dies of another cause in the same round in which a nearby enemy rams something): 1021191, one of ours against a team rated under 2000, and 1054802, one Vibing++ small-map game. Neither can move a number in this report by more than one count, so I documented the bug in `extract.py` instead of re-running everything. The base metrics were hand-checked on 4 replays: 1,064 values, 0 differences; my move model reproduces 81,853 of 81,853 steps. The headline count (approaches and how they end) was written a second time from scratch and run straight from the replays on 130 large-map games (`recount.py`): it matched the stored numbers exactly, 14 of 14 and 81 of 81 queen kills and every approach count.
- **Maps.** The numbers cover the 17 ladder maps. The qualifier uses new ones. The proposed rule has no map name and no size condition in it.

## 8. Files

| File | What |
|---|---|
| `card-draft.md` | The idea card, not posted |
| `SUMMARY-ko.md` | Korean summary |
| `deep-read.md` | 15 games read closely |
| `hypotheses.md`, `redteam.md` | Five candidates and the attempt to break each |
| `gap2_large.txt`, `gap2_medium.txt`, `gap2_small.txt` | Gap tables by phase |
| `qan_death.txt`, `qan_hazard.txt`, `qan_env.txt`, `an2_kills.txt`, `redteam_checks.txt`, `redteam2.txt`, `redteam3.txt`, `out/*.txt` | Raw outputs of every script quoted above |
| `subA.md` | The brief for the first sub-session, which could not be started |
| `lib.py`, `story.py`, `digest.py`, `extract.py`, `extract2.py`, `extract3.py` and the other `.py` files | Replay tools and analyses; `q/`, `q2/`, `q3/` hold per-game extracts (queen records, kill tracks, turn-level chances), `dg/` the digests |
