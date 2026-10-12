# Close read of 15 top-team games

**Who did this.** The lead session, not a sub-session: the loop guard blocks the sub-session command (it refuses any shell
command that names the loop settings file), so I read the games myself. Tools: `digest.py` (one page per game from one
team's side), `story.py` (`view`, `events`, `track`, `queen`), both built on `lib.py`, whose move model reproduces
81,853 of 81,853 real steps in four test games. The per-game digests I worked from are in `dg/<game_id>.txt`.

**Protagonist.** Vibing++ (team 306), rank 1 by the newest elo in the collected games (2332; SSS 2300, "forgot to mention" 2288).
"Own" below means Vibing++. Distances are path steps (kelp and portals respected) unless I say otherwise.
A dragon of length L can move ceil(L/4) + (L-2) steps in one turn: L2 = 1, L3 = 2, L4 = 3, L5 = 5, L6 = 6. A dragon sees 3 cells around its head.

## Games read

| # | Game | Map (size) | Opponent | Result | Ended by |
|---|---|---|---|---|---|
| 1 | 1052802 | Around UNSW 64x64 (large) | SSS | loss | longest 75 vs 77 |
| 2 | 1058916 | Around UNSW (large) | SSS | win | longest 102 vs 91 |
| 3 | 1056036 | Australia 64x64 (large) | SSS | win | longest 81 vs 24 |
| 4 | 1059823 | Australia (large) | forgot | loss | longest 4 vs 100 |
| 5 | 1052703 | Islands 56x40 (large) | SSS | loss | longest 18 vs 44 |
| 6 | 1053751 | Slithery Fight 63x27 (large) | SSS | win | queen rule (53 vs dead) |
| 7 | 1056022 | Slithery Fight (large) | SSS | loss | queen rule (dead vs 5) |
| 8 | 1046968 | Australia (large) | forgot | loss | queen rule (dead vs 9) |
| 9 | 1056710 | Trauma 48x24 (medium) | SSS | win | queen rule (32 vs dead) |
| 10 | 1047092 | Maze 48x24 (medium) | horse | loss | queen rule (dead vs 60) |
| 11 | 1046961 | Queen Of Spades 25x35 (medium) | forgot | win | wipe-out, round 273 |
| 12 | 1046780 | Tower Defense 32x16 (small) | SSS | loss | wipe-out, round 168 |
| 13 | 1046964 | Trophy 25x25 (small) | forgot | loss | wipe-out, round 138 |
| 14 | 1046782 | Portals 32x16 (small) | SSS | win | queen rule (33+ vs dead) |
| 15 | 1050166 | Prisoners Dilemma 32x16 (small) | bread first search | loss | wipe-out, round 116 |

8 large, 3 medium, 4 small; 6 wins, 9 losses. Schooltime was left out on purpose: both queens are sealed in a tiny room there and always end at length 3.

## Per-game notes

### 1. 1052802 Around UNSW, loss to SSS (longest 75 vs 77)
- **Opening.** 10 dragons each. Splits from round 0 at length 4 (4 -> 2+2); the 10-long starter splits 8+2. First contact round 16, first ram round 25. Round 50: 22 units vs 29; round 100: 57 vs 51.
- **Mid-game.** Both hold about 60 units from round 150 to 350. Vibing++ rams 19 enemy heads per 100 rounds; the rammers are 3–4 long sprinting 2–3 steps (40 of 76 rams) or 2 long stepping onto an adjacent head (11). SSS does the same at a slightly lower rate (11–15 per 100).
- **Queen.** Kept 6–7 long. Rounds 75–225 she stays within 2–3 cells of her spawn at (20,42) and visits only 5–9 different cells per 25 rounds (a small loop at home). Allies near her: 0–1. Only 4 enemy heads came within 6 steps in 385 rounds; one stayed rounds 147–206 and was finally rammed by an own 3-long. She leaves home at round 250, sheds length at rounds 316–318 (8 -> 6 -> 4 -> 2) and is rammed at round 385 at (29,35) by SSS #533: it was 13 steps away at round 380 as a 2-long, ate up to length 5 on the way (13, 11, 9, 7, 5 steps) and sprinted 4 steps.
- **Enemy queen.** Killed at round 303 at (46,14) by own #681, 9 long, born at round 297: more than 14 steps away at round 300, then 11, 9, 5, and a 4-step sprint.
- **Late game.** Own longest: 21 at round 300, 37 at 400, 50 at 450, 69 at 475. SSS: 27, 33, 65. Own "reverse" splits (a long dragon keeps 2 segments and hands the rest to a child that faces the other way): 75 in the game.
- **Roles.** Round 300 own lengths: 24 of length 2, 16 of 3–4, 11 of 5–9, 7 of 10–19, 1 of 20+.
- **Sonar.** Vibing++ pings from round 0 (about 7,000 in the first 100 rounds, 15,000 per 100 later). SSS sends almost nothing in the first 100 rounds (119 pings) and then 19,000–24,000 per 100.
- Decisive moment: a slow one. Own 20-long was rammed at round 327 (31,34) by a 4-long sprinting 4 steps; SSS lost a 35-long to a body crash at round 388 but still had 65 at round 450. Final 75 vs 77.

### 2. 1058916 Around UNSW, win over SSS (longest 102 vs 91)
- **Opening.** Slower than SSS: round 50 25 units vs 40; round 100 42 vs 61 (total length 102 vs 210).
- **Queen.** 6 long, never split, roamed 9–13 cells from spawn. Rammed at round 82 at (29,39) by SSS #131: 12–13 steps away for rounds 74–78 as a 3-long, grew to 5 at rounds 78–79, then 9, 7, 4 steps and a 3-step sprint. Two other enemy heads that had come within 2 steps of her earlier (rounds 67–87) were rammed by own 2- and 3-long dragons.
- **Enemy queen.** SSS keeps hers 2–3 long (she splits every time she reaches 4: nine splits). Killed at round 226 at (51,7) by own #231: it sat 9 steps from her for rounds 218–223 while growing from 3 to 4 long, then closed to 7, 5, 4 steps at lengths 4, 5, 6 and sprinted 4 steps.
- **Mid-game.** Own rams 21–24 per 100 rounds; 36 of 85 by 3–4-long dragons sprinting 2 steps. They often hit something longer: 3–4 long into 5–9 long 18 times, into 10–19 long 6 times.
- **Late game.** SSS consolidated first (longest 52 at round 350, 68 at 400, 88 at 450). Vibing++ fed later and harder: 48 self-kills in rounds 350–400 and 60 in 400–450; its longest went 27 (r350), 54 (r400), 77 (r450), 103 (r475).
- Decisive moment: rounds 400–490, the late feeding surge; nobody rammed either leader.

### 3. 1056036 Australia, win over SSS (longest 81 vs 24)
- **Opening.** Slow: 11 units at round 50 vs 19. Catches up by round 250 (61 vs 59).
- **Queen.** 4 long, roamed 17–20 cells from spawn with no ally near. SSS #4 (3 long, a starting dragon) stayed exactly 5 steps from her for rounds 44–54, then closed to 3 and rammed her at round 55 at (29,36) with a 2-step sprint.
- **Enemy queen.** 2–3 long until round 400, then fed (7 at round 450, 9 at 472). Killed at round 472 at (40,15) by own #781, a 10-long born at round 464, which came from 12 steps away in 7 rounds and sprinted 4 steps.
- **Late game.** Own longest 20 (r350), 48 (r400), 58 (r450), 75 (r475).
- Decisive moment: rounds 472–479. After the queen kill, own #507 (14 long) split at round 478 into 2 + 12; the 12-long child #791 was born facing the SSS leader, sprinted 3 steps, and at round 479 sprinted 2 more and rammed the 57-long SSS leader #789 at (16,32). SSS finished with a longest of 24. Before round 472 SSS was winning on the queen rule.

### 4. 1059823 Australia, loss to forgot (longest 4 vs 100)
- **Opening.** First contact at round 4. Vibing++ never grows: 9 units at round 50, 7 at round 100, while forgot has 19 and 42.
- **Queen.** 7 long, roaming 10–13 cells from spawn, no allies. Rammed at round 149 at (22,12) by forgot #78 (5 long): more than 14 steps away until round 143, then 14, 12, 11, 10, 7, 4, and a 3-step sprint.
- **Enemy queen.** Fed from round 250 (11 long at round 350); killed at round 356 by an own 7-long split child that sprinted 6 steps in the round it was born.
- Decisive moment: rounds 0–100. The opening was lost and nothing after it mattered.

### 5. 1052703 Islands, loss to SSS (longest 18 vs 44)
- **Opening.** Queen splits twice (8 -> 6+2) and stays 6–11 long. Round 100: 43 units vs 54; round 150: 61 vs 56 with a bigger total (180 vs 129).
- **Mid-game.** Very high ram rate: 37–39 per 100 rounds (SSS 21–28). 42 of them are 2-long dragons stepping onto an adjacent head.
- **Enemy queen.** Killed at round 216 at (5,2) by own #484, born at round 209: 14 steps away as a 2-long, then 12, 10, 8, 6, 4 steps while growing 2 -> 3 -> 4 -> 5, and a 4-step sprint.
- **Queen.** 10–11 long, roaming 11–21 cells from spawn; only 3 enemy heads came near her. At round 262, 16 long and alive with the enemy queen already dead, she did a reverse split (16 -> 2 + 14) and at round 263 the 2-long queen asked for another split and died ("noaction") at (43,36). Vibing++ threw away a won game on the queen rule.
- **Late game.** Own leader 52 at round 400 and 68 at round 425.
- Decisive moment: round 426, the 69-long own leader #873 was rammed at (51,39) by a 4-long SSS dragon stepping onto it from the next cell. Own longest fell to 12; SSS won with 44 against a total length of 273.

### 6. 1053751 Slithery Fight, win over SSS (queen rule, 53 vs dead)
- **Opening.** Queens start 25 long. Vibing++ reverse-splits at round 0 (25 -> 3 + 22) and keeps a 6-long queen; SSS sheds 2 at a time for ten rounds down to 3.
- **Queen.** 6 long to round 150, 11 to round 325, then fed: 17 (r350), 30 (r400), 41 (r450), 53 at the end. She roams 5–22 cells from spawn in open water. **No enemy head came within 6 steps of her in the whole game.**
- **Enemy queen.** SSS fed hers too: 3 long until round 300, 16 at round 350, 49 at round 400, 76 at round 448.
- Decisive moment: round 448 at (7,16). Own #1542 (3 long, born round 396) came from 14 steps away in five rounds (14, 13, 10, 7, 6, 3) and rammed the 76-long SSS queen with a 3-step sprint. Ten rounds earlier (r438) an own 4-long had rammed a 46-long SSS dragon. Without the queen kill SSS wins 76+ vs 53.

### 7. 1056022 Slithery Fight, loss to SSS (queen rule, dead vs 5)
- **Queen.** 6–11 long. Enemy heads came near 11 times; 3 were rammed by own small dragons. At round 231 an own 6-long rammed SSS's 34-long leader at (56,9) next to her. SSS #771 then ate from 4 to 12 long in rounds 233–241 while approaching (14, 12, 9, 6 steps) and rammed her at round 241 at (62,6) with a 5-step sprint.
- **Enemy queen.** 3 long for the whole game, never fed. She drifts with the SSS swarm: 6–10 allied heads within 6 steps at every checkpoint up to round 350, in open water, 13–29 cells from her spawn. Only 3 enemy heads came within 6 steps of her in 500 rounds (1 rammed, 2 left).
- **Late game.** Own leader 56 long at round 400, rammed at round 423 at (20,8) by a 2-long from the next cell.
- Decisive moment: round 241, the own queen. SSS then won with a 3-long queen that nobody reached.

### 8. 1046968 Australia, loss to forgot (queen rule, dead vs 9)
- **Opening.** Lost: 11 units at round 100 vs 61.
- **Queen.** 4–6 long; 15 enemy heads came within 6 steps, 5 were rammed by own dragons. forgot #235 came from more than 14 steps away at round 297 as a 2-long, grew to 5, and at round 306 sprinted 5 steps (N, N, E, E, S) from (22,39) to ram her at (24,38).
- **Enemy queen.** 3 long, four splits by round 61, then 5–9 long from round 275. Never threatened.
- **Late game.** forgot's 5-long dragons also rammed own leaders at round 421 (21 long, 5 steps) and round 498 (18 long, 4 steps).
- Decisive moment: the opening; the queen kill at round 306 sealed it.

### 9. 1056710 Trauma, win over SSS (queen rule, 32 vs dead)
- **Opening.** 2 dragons each, first enemy ram only at round 139: the two homes are far apart.
- **Queen.** 2–3 long until round 250, grows slowly to 9 by round 400, then fed to 32. **No enemy head within 6 steps all game.**
- **Enemy queen.** Fed earlier: 21 at round 350, 30 at round 450.
- Decisive moment: round 469 at (40,15). Own #520 (10 long at round 458, 13 at the strike, born round 427) came from more than 14 steps away to 12, 11, 8 and rammed the 31-long SSS queen with a 6-step sprint.

### 10. 1047092 Maze, loss to horse (queen rule, dead vs 60)
- **Queen.** 2 long, wandering 21–30 cells from spawn in the maze with 0–2 allies. Rammed at round 183 at (21,4) by a 4-long horse dragon born two rounds earlier (6 steps away, then 4, then a 3-step sprint).
- **Enemy queen.** Fed from round 250: 9, 27 (r350), 39 (r400), 58 (r450). Vibing++ never got to her.
- **Late game.** Each side lost a leader to a 2-long from the next cell (own 37-long at round 383; horse 24-long at round 380).
- Decisive moment: round 183, then no answer to the fed enemy queen.

### 11. 1046961 Queen Of Spades, win over forgot (wipe-out, round 273)
- **Opening.** 2 dragons each; first contact round 39; even at round 50 (7 vs 6 units).
- **Queen.** 2 long; rammed at round 94 at (21,32) by a 2-long that closed from 10 steps in five rounds.
- **Enemy queen.** Own #93 (3 long) sat 3 steps from her for rounds 224–231 and rammed her at round 232 with a 2-step sprint.
- Decisive moment: rounds 200–250, 11 vs 9 units becomes 19 vs 3 through 1-for-1 trades that Vibing++ refilled faster.

### 12. 1046780 Tower Defense, loss to SSS (wipe-out, round 168)
- **Opening.** Both sides have 2 units until round 50. SSS then explodes to 15 units by round 100; Vibing++ has 3.
- **Queen.** 2–3 long; at round 100 four SSS 2-longs are within 7 steps; rammed at round 106 by a 2-long that had hovered 2–4 steps away for ten rounds.
- Decisive moment: rounds 50–100, the economy.

### 13. 1046964 Trophy, loss to forgot (wipe-out, round 138)
- **Opening.** forgot has 17 units at round 50 against 8. 25 enemy heads came within 6 steps of the own queen in 61 rounds; 6 were rammed.
- **Queen.** Rammed at round 61 by a 2-long from the next cell, with nine enemy heads within 6 cells.
- Decisive moment: rounds 0–50.

### 14. 1046782 Portals, win over SSS (queen rule)
- **Opening.** Sides are separated by portals; neither side rammed an enemy head in the whole game.
- **Queen.** 3 long until round 200, **no enemy head within 6 steps all game**, then fed: 17 at round 250, 21 at 300, 33 at 475. Self-kills cluster near her.
- **Enemy queen.** 2–3 long; she died at round 389 at (3,6), rammed by SSS's OWN #571 (7 long at round 378, 10 at the strike), which had come from 14 steps away over ten rounds with eight other SSS heads within 6 cells. Friendly fire, not a Vibing++ kill.
- Decisive moment: round 389 (SSS killed its own queen) plus the fed own queen.

### 15. 1050166 Prisoners Dilemma, loss to bread first search (wipe-out, round 116)
- **Opening.** Contact at round 0, first ram at round 3. Vibing++ is stuck at 5 units; the opponent rams 9 heads in the first 100 rounds with 3–4-long dragons sprinting 2 steps.
- **Queen.** Rammed at round 110 by a 4-long that had kept 6–8 steps away for ten rounds and then closed.
- Decisive moment: the opening trade war.

## Recurring patterns

**Things the protagonist DOES**

1. **It kills the enemy queen.** 8 of 15 games (1, 2, 3, 4, 5, 6, 9, 11); not in 7, 8, 10, 12, 13, 15, all of which it lost, and not in 14, where SSS rammed its own queen. The killer was 5 or more long in 6 of the 8 (lengths 9, 6, 10, 7, 5, 13; the other two were 3 long) and used 4–6 steps in those 6. Best examples: game 6 round 448, game 9 round 469.
2. **The killer travels to her.** In 5 of the 8 kills the killer was 11 or more steps away within the previous 5–10 rounds and closed at 2–3 cells per round (games 1, 3, 5, 6, 9). In 2 it sat 3–9 steps away for six or more rounds first (game 2 rounds 218–223, game 11 rounds 224–231). In 1 it was a split child born next to her (game 4). A replay cannot show how it knew where she was; she was far outside its sight in the fast cases.
3. **Hunters grow on the way in.** The killer gained length during the approach in 3 of the 8 own kills (game 2: 3 -> 6; game 5: 2 -> 5; game 9: 10 -> 13; game 1's was born 9 long), and in 4 of the 6 SSS/forgot kills of its queen on large maps (game 1: 2 -> 5; game 2: 3 -> 5; game 7: 4 -> 12; game 8: 2 -> 5). Longer means more reach: a 5-long strikes from 5 steps, beyond the 3 cells the victim can see.
4. **Its queen is fed only where nobody has come near her.** In the three games where no enemy head came within 6 steps of the queen all game (6, 9, 14) she was fed from round 200–400 and won the queen rule each time. In the other 12 she stayed short or mid-length and was not fed.
5. **Small dragons trade constantly.** 10–39 rams per 100 rounds on large maps; the typical rammer is 3–4 long with a 2–3-step sprint, or 2 long from the next cell. It rams longer dragons too (game 2: 24 rams by 3–4-long dragons into 5–19-long ones). All three top teams do this at similar rates.
6. **Trapped dragons kill themselves instead of crashing** (death reason "noaction"): 14–154 per 50 rounds, mostly 2–3 long. Only 4–40% die within 6 cells of the team's longest dragon before round 350, so most of this is recycling, not feeding; the share near the leader rises to 40–80% in the feeding phase (game 2 rounds 350–400: 42%; game 3: 79%).
7. **Reverse splits**: a long dragon keeps 2 segments and gives the rest to a child facing the other way (75, 54, 28, 26, 21, 18 times in games 1, 2, 5, 6, 7, 10). The leader's id therefore changes all the time. In game 3 the reverse split produced the dragon that killed the enemy leader one round later.
8. **Late consolidation**: longest 16–27 at round 300–350, then 37–54 at round 400 and 70–100 by round 475 (games 1, 2, 3).

**Things that HAPPEN to it**

9. **Its queen is rammed.** 11 of 15 games; she survived only in the three "nobody came near" games; in game 5 she killed herself. On the open large maps (games 1–5, 7, 8) the killer was 5 or more long in 5 of 6 rams and used 3–5 steps.
10. **Its leader is rammed late**: game 5 round 426 (69-long, by a 4-long from the next cell), game 7 round 423 (55-long, by a 2-long), game 10 round 383 (37-long, by a 2-long), game 1 round 327 (20-long).
11. **Stalking**: an enemy holds a fixed distance of 3–9 steps from the queen for many rounds before the strike (game 3 rounds 44–54 at exactly 5 steps; game 12 at 2–4 steps; game 15 at 6–8; game 2 own hunter at 9).

**Wins vs losses**

- Wins (6): the enemy queen was dead at the end in all 6 (5 own kills, 1 SSS friendly fire); decided by a queen or leader kill in 4 (games 3, 6, 9, 14), by late feeding in 1 (game 2), by trades in 1 (game 11).
- Losses (9): opening economy lost in 5 (games 4, 8, 12, 13, 15); own queen or leader assassinated with no reply in 3 (games 5, 7, 10); out-consolidated in 1 (game 1).

## What the protagonist's losses have in common
1. **Slow openings** (5 of 9 losses): it is behind on units by round 50–100 (9 vs 19, 11 vs 61, 3 vs 15, 8 vs 17) and never recovers. Its round-50 unit count on large maps is the lowest of the three top teams (22 vs 31 and 29).
2. **It does not protect its queen as a special dragon** (games 5, 7, 8, 10): she roams alone (0–2 allies within 6 steps), far from spawn, and in game 5 the bot split and killed its own living queen.
3. **Its leader dies to a small dragon from the next cell** (games 5, 7, 10): the giant dragon is not guarded.
4. **It fails to reach a fed or hidden enemy queen** (games 7, 8, 10): a 3-long queen inside the SSS swarm (game 7) and fed queens of forgot and horse (games 8, 10).

## What SSS and forgot do differently (seen in these games)
- SSS keeps its queen 2–3 long (it splits her every time she reaches 4) and she sits where the SSS swarm is thickest: in game 7, 6–10 allied heads within 6 steps for 350 rounds, against 0–3 for the Vibing++ queen. SSS's sonar is nearly silent for the first 100 rounds.
- forgot keeps a 3-long queen and feeds her from about round 250–275 if she is alive (games 4 and 8), and uses 5-long dragons with 4–5-step sprints against queens and leaders (game 8 rounds 306, 421, 498).

## Things I could not determine from replays
- How a hunter knows where the enemy queen is. Sonar values are packed 64-bit numbers; I could count pings but not read them.
- Whether "growing on the way in" is a rule (eat until you can reach) or just pearls lying on the route. Counted afterwards on all games (`an2_kills.txt`): on large maps only 8 of 57 Vibing++, 16 of 83 SSS and 8 of 57 forgot queen killers gained 2 or more segments in their last 8 rounds, so it is not a general rule; the games I read over-represent it.
- Whether the SSS queen deliberately moves towards allies, or allies happen to be where she is. (Measured separately on all games; see REPORT.md.)
- Whether Vibing++ decides not to protect the queen on small maps (she dies by "noaction" in 63 of 170 small-map games) or simply has no queen logic.
