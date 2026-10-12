# Fact sheet: the numbers so far (lead session, refreshed 10:00 KST on 5 Oct, after sub-sessions A, A2, A3, A4)

This is the input sheet for the sub-sessions. Everything here is counted from ladder replays by the scripts in this directory;
raw outputs are in `out2/`. Snapshot: 2,343 games (1,637 top-team games, 706 of ours). Unless a line says otherwise: opponents
rated 2000+, and the map Schooltime left out of every queen number (both queens are sealed in a room there and always end 3 long).
These are measurements, not conclusions. Where a sentence interprets, it says "reading".

Teams: Vibing++ (id 306, elo 2309, rank 1 = the protagonist), "forgot to mention" (264, 2306), SSS (91, 2297), meow (1119, us, about 1850).
"Top three" = the first three. Sample against 2000+ teams: Vibing++ 537 games (341 wins), SSS 534 (348), forgot 670 (387),
meow 427 (118). Our 2000+ sample is narrow: 170 games vs WeHaveQuizzes, 165 vs test4, 30 vs dev test, 17 vs forgot, 5 vs Vibing++.

Words: **queen** = each team's lowest-id dragon (id 0 or 1; both queens move before all other dragons each round). **ram** = head into
head, both die. **reach** = most steps in one turn = ceil(L/4) free + (L-2) paid: 1, 2, 3, 5, 6 for lengths 2, 3, 4, 5, 6.
**view** = the 7x7 square around a head. **self-kill** = death with reason `noaction`.

**Which bot played our games (found by A3, recounted by the lead: `bybuild.py`, `recount3.py`).** Our 401 games against 2000+ teams
are eleven runs, and "meow" below pools them unless a line says otherwise: two ladder downloads (24 + 153 games, the live bot of
that hour) and smoke-test pairs in which the live bot ("-old") and a candidate ("-new") each play test4 and WeHaveQuizzes once per
map: stride-old/new, passage2-test-old/new, qh31-test-old/new (28 games each), tc30-test-new (28), tc30-dev1-old and tc30-dev1b-new
(14 each, against "dev test 1"). Two candidates are online trials of ideas in this study:
- **qh31 = queen-hunt build (card #31, hunters 4 or shorter).** Team record (`../../online/smoke/qh31-test-result.txt`,
  `qh31-analysis/summary.txt`): new 10 wins of 30, live 8 of 30 on the same pairs (live average 9.2 of 30); head-on kills of her queen
  10 -> 11; 338 hunters in 23 games, 8 rammed her queen, 36 died in head-ons with other enemies. My count on its 28 games: in-view
  chances taken by 2-3-longs 8 of 9 (live bot in the paired run 8 of 20), by 4+ longs 2 of 11 (0 of 9); only 1 game with a
  chance and no kill.
- **tc30 = trade-on-contact build** (on maps over 1,200 cells a small dragon may ram an enemy showing at least its own length; the
  live bot asks for max(5, length + 2) there). Team record: new 6 of 30, live 9.2 of 30. On large maps it rams in 28% of meetings
  (live 8%), has 52 units against 58 at round 150 (live 46 against 61), and won 0 of 12 large-map games (live 12 of 99).

In-view ram chances on her queen taken, by run: ladder 3 Oct 3 of 8; ladder 4 Oct 16 of 72 and 24 of 125 (smoke copy); stride-old 7
of 36, stride-new 9 of 37; passage2-old 8 of 27, -new 5 of 25; qh31-old 8 of 29, qh31-new 10 of 20; tc30-new 7 of 34; tc30-dev1-old
1 of 21, tc30-dev1b-new 1 of 12. The low take-up holds for every build.

## 1. What decides games

Round-500 games by queen state at the end, counted from each team's side (`out2/redteam3.txt`, `out2/endstate.txt`):

| Own queen / their queen at the end | Top three | meow |
|---|---|---|
| alive / dead | 177 of 177 won | 1 of 1 |
| alive / alive | 103 of 159 | 3 of 14 |
| dead / dead (longest dragon decides) | 266 of 447 = 60% | 41 of 143 = 29% |
| dead / alive | 0 of 132 | 0 of 73 |

Queen alive at the end, all endings: own / enemy = Vibing++ 27% / 23%, SSS 41% / 19%, forgot 36% / 31%, meow 10% / 40%.
Our large maps: own 0 of 111. How our games end (427 incl. Schooltime): wipe-out 67 W / 103 L; round 500: 51 W / 206 L.
Win rate by size: small 36%, medium 32%, large 13% (top three: 57–66%, 50–75%, 56–67%).

## 2. Gap table, large maps (means per game; W / L = Vibing++'s own wins / losses; `out2/gap2_large.txt`)

| | Vibing++ | (W / L) | SSS | forgot | meow | our opponents |
|---|---|---|---|---|---|---|
| Units r100 | 38 | 40 / 36 | 49 | 47 | 39 | 50 |
| Units r200 | 53 | 57 / 47 | 58 | 57 | 39 | 61 |
| Units r300 | 55 | 60 / 48 | 59 | 57 | 34 | 61 |
| Total length r100 | 105 | 109 / 99 | 130 | 117 | 98 | 138 |
| Total length r200 | 177 | 191 / 153 | 195 | 165 | 116 | 254 |
| Total length r300 | 208 | 230 / 169 | 220 | 183 | 113 | 326 |
| Natural pearls eaten r50–100 | 102 | 104 / 99 | 107 | 108 | 83 | 115 |
| Natural pearls eaten r150–200 | 124 | 128 / 117 | 112 | 107 | 52 | 129 |
| Natural pearls eaten r250–300 | 120 | 125 / 113 | 104 | 102 | 44 | 124 |
| Rams started r150–200 | 12.3 | 12.8 / 11.3 | 9.1 | 12.3 | 3.3 | 11.1 |
| Longest r300 | 16 | 18 / 14 | 21 | 17 | 15 | 24 |

Medium and small tables: `out2/gap2_medium.txt`, `out2/gap2_small.txt`. On medium maps our units keep rising until round 300
(27 at r200) and our "stop splitting" round there is 300; on large maps it is 150 and our units fall from round 150.
Our code: `LEADER_GROW_ROUND_BIG = 150` on maps over 1,200 cells, `LEADER_GROW_ROUND = 300` otherwise; after that round a dragon
longer than 4 no longer splits (`split_child_size()`). Card #14 tried a state-based version locally: units did not change because
our bot already reaches 60 units locally by round 200.

## 3. The enemy queen: do we take the ram?

**Turn-level chances** (`extract3.py`, `out2/an4.txt`). A chance = at the start of a non-queen dragon's own turn there is a path
of free cells from its head to the enemy queen's head no longer than its reach (dragons over 12 long skipped). In view = her head
inside the attacker's 7x7 square at that moment.

| Chances taken | Vibing++ | SSS | forgot | meow | other 2000+ teams |
|---|---|---|---|---|---|
| In view, attacker 2–3 long | 186 of 186 | 155 of 155 | 221 of 317 = 70% | 87 of 231 = 38% | 366 of 399 = 92% |
| In view, attacker 4 long | 25 of 25 | 26 of 26 | 12 of 53 = 23% | 5 of 39 = 13% | 88 of 108 = 81% |
| In view, attacker 5–9 long | 38 of 38 | 59 of 61 | 21 of 65 = 32% | 5 of 137 = 4% | 84 of 162 = 52% |
| In view, attacker 10–12 long | 17 of 18 | 10 of 12 | 0 of 22 | 2 of 39 = 5% | 17 of 68 = 25% |
| In view, all | 266 of 267 | 250 of 254 | 254 of 457 = 56% | 99 of 446 = 22% | |
| Not in view, all | 1 of 214 | 0 of 273 | 2 of 210 | 2 of 542 | 7 of 916 |

- Vibing++ and SSS pay any price when she is in view: 3 paid steps 15 of 15 and 20 of 22; 4 or more 8 of 9 and 12 of 14; even the
  team's longest dragon goes (30 of 30, 28 of 28). forgot takes 70% of free ones, 56% with 1 paid step, 25% with 2. We take 53% of
  free ones, 13% with 1 paid step, 11% with 2, 4% with 3.
- We had an in-view chance in 176 of our 401 games (44%); we rammed her in 102 games. In 76 games we had an in-view chance and
  never rammed her (Vibing++ 0 of 502 games, SSS 3 of 503). Those 76 became: 25 round-500 losses with her alive, 17 round-500
  losses with her dead later anyway, 20 wipe-out losses, 14 wins. If she had died and nothing else changed, 13 of the 25 flip
  (`out2/an4b.txt`; the 13 games are listed there). 13 of 401 games = 3 points. Only our longest dragon had the chance in 15 of the 76.
- Our code (`mybot2/main.cpp`): `QUEEN_HUNT = false`; `mark_trade_targets()` needs `round <= feed_round` (400, or 300 in queen-feeding
  mode), at least as many of our other heads in view as enemy heads (`TRADE_LOCAL_EDGE 1`), and a target with at least as many
  visible parts as the attacker's length (at least `max(5, length + 2)` on maps over 1,200 cells); `is_trader()` lets only dragons
  4 or shorter trade. Nothing in it knows the target is the queen. Our take-up by attacker length (60% at 2, 27% at 3, 8% at 4,
  1% at 5–9 in the first snapshot) follows these rules step by step.

**Per game and per approach** (`out2/misc.txt`, `out2/approach*.txt`). Rams on the enemy queen per game, small / medium / large:
Vibing++ 0.56 / 0.65 / 0.74, SSS 0.56 / 0.61 / 0.78, forgot 0.47 / 0.40 / 0.60, meow 0.31 / 0.23 / 0.19. An approach = an enemy head
comes within 6 path-steps of a living queen. We make 9.3 approaches a game. Share ending with her rammed, by attacker length
2 / 3 / 4 / 5–6 / 7–9 / 10+: top three 6% / 10% / 10% / 29% / 28% / 22%; meow 3% / 3% / 2% / 2% / 2% / 2%. On large maps 43% of
top-three queen kills are by a dragon 5 or longer (small 4%, medium 10%). A 5–9-long killer started the fatal round 4 or more steps
from her in 86% of its kills (first snapshot).

**Does the kill matter?** Round-500 games with the own queen dead: she lived = 0 of 132 (top three) and 0 of 73 (us); we rammed
her = 209 of 338 (62%) and 15 of 42 (36%); she died another way = 57 of 109 (52%) and 26 of 101 (26%). Against test4 (first
snapshot): top three kill her 0.48 times a game, we 0.21; her queen alive at the end 29% vs 48%.
Our round-500 losses with their queen alive: 84. 44 flip if she dies and nothing else changes; in 19 of those 44 we made at
least one approach. Trauma and Portals queens sit behind portals (we were almost never within 8 steps); Australia and Islands
losses mostly do not flip because we are too far behind on length.

## 4. Our own queen

How she ends (share of games, `out2/selfdeath.txt`, `out2/qmap.txt`; table corrected after A2):

| | alive | rammed by an enemy | boxed in or own crash (kelp / own body / another body / she rams / `noaction`) |
|---|---|---|---|
| Vibing++ | 27% | 46% | 27% (of which `noaction` 22%) |
| SSS | 41% | 48% | 11% |
| forgot | 36% | 52% | 12% (of which `noaction` 8%) |
| meow | 10% | 63% | 28% |

Correction (A2): the last column is ONE kind of event. A queen with no free cell next to her head dies whatever she does; Vibing++
and forgot send no action (`noaction`), SSS and we step into something. A2's comparable figure for "a 2-3-long queen boxed in":
Vibing++ 23%, forgot 11%, SSS 10%, ours 28% of games.

When she dies (`qearly.py`, `out2/qearly.txt`; share of games, in brackets how many of those deaths were enemy rams):

| Own queen dead before | meow | Vibing++ | SSS | forgot |
|---|---|---|---|---|
| round 50 | 20% (49 of 80) | 17% (47 of 87) | 9% (45 of 47) | 13% (68 of 80) |
| round 100 | 45% (118 of 180) | 34% (96 of 171) | 17% (82 of 88) | 30% (160 of 191) |
| round 300 | 84% (231 of 336) | 62% (187 of 312) | 43% (184 of 215) | 52% (273 of 330) |
| the end | 90% (251 of 362) | 73% (230 of 368) | 59% (240 of 296) | 64% (327 of 406) |
| before round 300, maps of 600 cells or fewer | 95% (69 of 138) | 74% | 42% | 51% |
| before round 300, maps of 601-1,500 cells | 63% (77 of 92) | 58% | 38% | 50% |
| before round 300, maps over 1,500 cells | 95% (85 of 106) | 50% | 49% | 57% |

Per map the file shows where it is worst: on Portals (the teams never touch there) our queen is dead before round 300 in 26 of 27
games, never by a ram (SSS 28%, forgot 10% of games); Maze 26 of 27 (14 rams); Tower Defense 22 of 24; weakhold 27 of 27;
Slithery Fight 24 of 29 (9 rams); Stripes 29 of 29; Australia 28 of 28 and Islands 30 of 30 (all but three by rams).
Our own queen alive at round 300, by how the economy stands then (own / enemy total length; `behind.py`, `out2/behind.txt`):
under 0.67: 26 of 168 (top three 58 of 171); 0.67-1: 8 of 61 (115 of 241); 1-1.5: 0 of 12 (194 of 312); over 1.5: 7 of 27
(218 of 332). So at the same economy our queen is alive half to a quarter as often.

- Our 111 self-inflicted deaths (first snapshot: 81): no free neighbour cell at the start of the fatal round in 75 of 81; a small
  enemy within 3 steps in only 13; she was 2–3 long in 74; 58 on a cell with one or two open sides; 49 on maps of 600 cells or
  fewer, where our queen rules are off (`QUEEN_MIN_CELLS 600`). Portals 27 of 27 games (top three: rammed 0%, alive 49%),
  Slithery Fight 16 of 29, weakhold 14 of 27, Maze 13 of 27, Tower Defense 10 of 24. 33 of the 111 were round-500 losses with
  both queens dead (each a queen-rule win had she lived). Cards #23 (`QUEEN_NO_TRAP`) and #25 (`QUEEN_WAIT`, never fired
  because she is 2–3 long when boxed in) work on this.
- Alive at the end by map, top three / meow: Trauma 93 / 56, Autarky 54 / 12, Tower Defense 51 / 0, Portals 49 / 0, Slithery Fight
  44 / 0, Maze 40 / 0, weakhold 35 / 0, Stripes 33 / 0, Prisoners Dilemma 31 / 38, Trophy 26 / 50, Australia 25 / 0, Default 20 / 15,
  Around UNSW 18 / 0, Devil 18 / 3, Queen Of Spades 11 / 4, Islands 9 / 0.
- Per small-enemy approach (attacker 4 or shorter, `out2/defend.txt`): queen rammed by it 5.2% / 6.3% / 7.0% (Vibing++ / SSS /
  forgot), ours 10.0%; intruder rammed by a defender 13% / 16% / 14%, ours 5%. With 3+ allied heads within 6 steps: their queen
  rammed 2–4%, defender rams the intruder 24–27%; ours 10% and 15%.
- Once a small enemy is 2 steps away, a top-three queen on a large map is rammed that round about as often as ours (76–101 per
  1,000 rounds vs 106, first snapshot); the difference is how often one gets that close (1.3–2.0% of her rounds vs 3.6%).
- Queens are not parked (40–63 different cells per 100 rounds on large maps; ours 55–60) and do not camp at portals. SSS on small
  maps is the exception (29% of 25-round windows on 10 cells or fewer). Queen length rounds 100–200 on large maps: Vibing++ 5–8,
  SSS 2–3, forgot 2–3 (fed from about round 200–250), meow 2–3.
- Relative to her own team (`out2/an2.txt`, crowd): SSS's queen has about half the enemy heads within 8 cells that the average SSS
  dragon has, and as many allies; Vibing++'s 0.6–0.8 and fewer allies (0.6–0.7); ours 0.6–0.75 and as many allies. In absolute
  terms our whole team has more enemies around it (1.7 within 8 cells vs 1.0–1.3 at rounds 100–200, large maps).

## 5. Leaders (longest dragon, 15 or longer)

In top-three round-500 games decided by the longest dragon, the side that alone rammed the other's 20+ leader after round 400 won
61 of 68; the side that alone lost its leader won 15 of 69; neither: 180 of 292 (`out2/cf.txt`). We already take such chances at
their rate: with the enemy leader inside the reach of one of our heads (large maps) we ram 20 times per 1,000 such rounds, the top
three 21–33; exposure 13.8 rounds a game vs 10.7–17.8. No gap there.

## 6. What sub-session A found in 15 Vibing++ games (`deep-read.md`; checked by the lead on the points marked)

- Vibing++ rams the enemy queen only when she is inside the attacker's own view, and then always (checked on all games: section 3).
- Its queen is never thrown away by choice: every non-routine queen split and every queen self-kill happened with no free
  neighbour cell (14 events). A boxed-in queen of 4+ splits just in front of the own segment touching her head, which usually
  leaves her 3 long (85 -> 3 in 1063789, checked). forgot instead sheds 2 from the tail per round (42 -> 10 over 16 rounds).
- 7 of 9 losses were behind 1.5 to 1 or worse in units by round 50–100, with half or less of the opponent's natural-pearl intake.
- Queen kills: 6 of 7 by a 5–11-long with a 4–6-step sprint; 3 of 7 by a fresh split child that never ate and went straight for
  her; hunters walked 14–29 steps to a queen nobody on the team had in view (she was within 8–15 cells of her own spawn).
- Queens that lived on open big maps: nothing of length 4–11 with a sprint ever had her in view; a 12–13-long queen has 3–4 free
  steps and walks away from 2–3-long followers.
- The queen always moves away from a close enemy (151 of 151 rounds) and pays segments to do it; no escort was seen (no own head
  within 6 steps in 128 of the 151 rounds).
- Leader kills use a "split first" trick in 4 of 10 cases (a split child born facing the target, or the 2-long front part rams).

## 6b. What sub-session A2 found in 15 SSS and forgot games (`deep-read-2.md`; the lead recounted the marked points, `check_a2.py`)

- The one hunting rule all three share: a 2-3-long with the enemy queen in view and in reach rams her (Vibing++ 186 of 186, SSS 155
  of 155, forgot 136 of 139 from round 100 on; before round 100 forgot rams only when not outnumbered locally, 47 of 51 against
  38 of 127; recounted). forgot's longer dragons mostly do not (4-long 12 of 53, 5-9 21 of 65, 10-12 0 of 22). Nobody rams a queen
  that is outside the attacker's own view.
- Queen survival is about where she lives, not about guards: SSS's queen eats 2.1 natural pearls per 100 rounds (an average SSS
  dragon 4.7) and stays 10.8 cells from her spawn (team 16.7). Nobody escorts (allies moved nearer to an intruder 40 times, away
  44). Dead before round 100 on large / medium maps: SSS 8% / 7%, forgot 30% / 20%, Vibing++ 10% / 24% (recounted).
- A boxed-in long queen: SSS and forgot shed 2 segments from the tail each round and never cut themselves short (0 cuts in 503
  and 632 games); Vibing++ cuts to 3. A boxed-in 2-3-long queen dies in all three teams.
- Feeding the queen: forgot feeds her from round 200-225 whatever the game looks like (8+ long by round 300 in 175 of 189 games)
  and wins 52 of 71 games in which both queens live; SSS keeps her 2-3 long and decides late (27 of 48); Vibing++ 24 of 40.
- The early "self-kills" of small dragons are not a choice: 97-99% happen with no free cell (one-cell dead ends holding a pearl).
- Followers (a 2-3-long keeping the enemy queen in view for 6+ rounds) exist in SSS and forgot; in 18 of 28 streaks she got away.

## 6c. Economy and contact: what sub-session A3 found (`deep-read-3.md`), with the lead's own recount (`recount3.py`, `out2/recount3.txt`)

A3's three findings were recounted by the lead with a separately written script; the recount agrees within 1-3 points.

| Large maps (over 1,500 cells) | meow live bot (99 games) | meow tc30 build (12) | opponents in our games | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|
| Meetings (enemy head on the next cell, both 4 or shorter) that end in this side's ram | 8% of 9,789 | 28% of 1,031 | 35% | 35% | 41% | 33% |
| The same when this side is shorter / same length / longer | 13 / 9 / 5% | 43 / 33 / 7% | 62 / 32 / 20% | 64 / 34 / 25% | 83 / 40 / 24% | 53 / 34 / 23% |
| Charges per game (rams with a 2+ step move from a non-adjacent cell), rounds 0-149 | 1.0 | 3.9 | 13.5 | 8.8 | 10.2 | 12.9 |
| Share of the game's rams started by this side | 22% | 37% | 76% | 48% | 48% | 57% |
| Pearls of ram corpses eaten by this side | 29% | 35% | 68% | 49% | 50% | 52% |
| ... of the rams this side started / of the rams the enemy started | 50% / 21% | 53% / 23% | 78% / 46% | 67% / 33% | 68% / 36% | 66% / 34% |
| Free pearl on the next cell is eaten (dragon 2-4, no enemy head in view, a way out): rounds 0-149 / 150-299 / 300+ | 80 / 56 / 54% | 81 / 59 / 58% | 80 / 83 / 77% | 87 / 88 / 88% | 75 / 80 / 77% | 84 / 87 / 75% |
| ... rounds 150-299: within 9 cells of the own longest dragon (5+) / farther / no own 5+ | 41 / 58 / 66% | 40 / 61 / 60% | 81 / 83 / 84% | 87 / 89 / 87% | 80 / 80 / 86% | 86 / 87 / 87% |
| Games in which own total length is below the enemy's at round 300 | 96 of 97 | 12 of 12 | 1 of 109 | 82 of 158 | 48 of 139 | 40 of 127 |

- **On medium and small maps the live bot already rams at meetings like everyone else** (33-35% of meetings; opponents 30-31%).
  The 8% is a large-map behaviour, and the code says why: `AGGRESSIVE_MAX_CELLS = 1200` switches the trade rule
  (`worth = aggressive ? parts >= length : parts >= max(5, length + 2)`, minimum units 1 instead of 8). The tc30 build removed
  that size gate for contact and got 28%. Even so, on medium and small maps we start only 39-41% of the rams (charges 0.6-0.8 a
  game in rounds 0-149 against 2.1-2.5) and eat 41-44% of the ram pearls (opponents 51-56%).
- **The round clock.** The free-pearl row drops at exactly our `grow_round`: on large maps at round 150 (80% -> 56%), on medium and
  small maps at round 300 (85% in rounds 0-149, 82-84% in rounds 150-299, then 49-50%; near the own longest 30-45%). Every run
  and both builds show it. Code after `grow_round`: a pearl within 9 cells (Manhattan) of the known leader position costs
  `ZONE_PEARL_PENALTY 600` for everyone but the leader and loses `EAT_BONUS 300` (`score_step`, `in_leader_pearl_zone`), and dragons
  longer than 4 stop splitting (`split_child_size`). The drop is also there far from the own longest dragon (58%) and with no
  own dragon of 5+ at all (62-66%), so a remembered leader position or another rule is involved too (not visible in a replay).
- A3's reading: at contact our small dragons give way (finding 1), the enemy eats the ram pearls (2), and the round-150 clock
  turns eaters into prey (3); about 110 segments a game move to the enemy through rams on large maps.
- A3: large maps are two pairs. Australia and Islands: units and length both collapse (1 win in 58). Around UNSW and Slithery
  Fight: units level until round 300, total length 60-80% (11 wins in 53).
- A3: fewer of our dragons die in dead ends than our opponents' on 8 of 10 maps; the exceptions are Slithery Fight (sheds) and
  Portals; 6.4 of our dragons a game die by stepping through a portal onto a body they cannot see (18.4 on Islands).

## 6d. From behind, and the longest-dragon race (lead: `behind.py`, `leaderrace.py`; `out2/behind.txt`, `out2/leaderrace.txt`)

Games reaching round 300, all sizes, by own / enemy total length at round 300:

| Total-length ratio at round 300 | top three: games, won | meow: games, won | top three's wins by queen rule / longest | our wins by queen rule / longest |
|---|---|---|---|---|
| under 0.67 | 171, 15% | 168, 7% | 15 / 10 | 2 / 10 |
| 0.67-1 | 241, 48% | 61, 26% | 58 / 56 | 1 / 14 |
| 1-1.5 | 312, 61% | 12, 50% | 97 / 88 | 0 / 5 |
| over 1.5 | 332, 88% | 27, 63% | 110 / 111 (+70 wipe-outs) | 1 / 10 (+6) |

- We are far behind (under 0.67) in 63% of our games that reach round 300; the top three in 16% of theirs. A3's "they win 35-50%
  of the games in which they are behind, we 10%" is mostly this mix: inside the same band the gap is 15% against 7% and 48%
  against 26%.
- Two rough what-ifs with these four bands: our band win rates with the top three's mix of bands would give 42% (we have 19% of
  these games); the top three's band win rates with our mix would give 32%. Reading: economy is the larger lever, the conversion at
  equal economy the smaller one, and both are large. (Our two "ahead" bands hold only 39 games.)
- About half of every top team's wins in every band are queen-rule wins. Ours: 4 of 51.
- Longest dragon, medians in round-500 games (longest / total length): round 300 meow 5 / 72, Vibing++ 12 / 141, SSS 8 / 167,
  forgot 15 / 127; round 400 meow 12 / 74, Vibing++ 25 / 145, SSS 31 / 151, forgot 34 / 121; end 26 / 57, 45 / 131, 44 / 136, 50 / 106.
- Round-500 games in which both queens are dead, own / enemy total length at round 400 between 0.8 and 1.25: we win 13 of 36
  (own longest 13 at round 400 -> 32 at the end; the enemy's 21 -> 39); Vibing++ 28 of 44 (32 -> 56), SSS 37 of 61 (37 -> 54),
  forgot 30 of 51 (40 -> 61). Our code starts feeding the leader at `ENDGAME_ROUND 400` (300 in queen-feeding mode, or round 200
  with 56 units).

## 6e. Our own queen's deaths: what sub-session A4 found (`deep-read-4.md`), with the lead's cross-check (`check_a4.py`)

Words: **in reach** = on a cell that an enemy head in her view can move into this round; **safe step** = a one-step move that
ends outside the reach of every enemy head in her view; **queen-round** = one round in which a queen is alive; **boxed in** = no
free cell next to her head; **cut** = a split that keeps 2-3 segments for her; **shed** = a split that gives away 2 from the tail.

| Queen deaths per 1,000 queen-rounds | all | rammed after she stepped or stayed in reach with a safe step on the board | rammed, cornered | rammed by an unseen enemy | boxed in by bodies | boxed in a terrain dead end | she rams |
|---|---|---|---|---|---|---|---|
| meow, all 401 games | 6.5 | 1.86 (104 deaths) | 2.07 | 0.55 | 1.09 | 0.54 | 0.34 |
| meow live bot, queen rules on (maps over 600 cells, 175 games) | 5.0 | 1.53 | 1.73 | 0.66 | 0.73 | 0.27 | 0.07 |
| meow live bot, queen rules off (600 cells or fewer, 100 games) | 10.7 | 2.40 | 2.40 | 0.33 | 2.62 | 1.42 | 1.53 |
| our opponents in our games | 2.2 | 0.24 | 0.61 | 0.06 | 0.66 | 0.33 | 0.16 |
| top three together | 2.7 | 0.29 | 1.25 | 0.49 | 0.36 | 0.17 | 0.12 |
| top three against test4 and WHQ only (108 games) | 3.0 | 0.28 | 1.46 | 0.61 | 0.28 | 0.28 | 0.00 |

- **She ends turns in reach by choice.** Against test4 and WHQ: turns with no safe step 2.5 per 1,000 queen-rounds (top three 2.2);
  turns that ended in reach although a safe step existed 2.6 (top three 0.4). 104 of our 362 queen deaths; in 90 a safe step with
  room behind it and no portal was on the board. When she did take the safe step in the same situation she was rammed within 10
  rounds in 19-24% of cases (65-87% when she did not). Code: for the queen the danger of a cell is one term of a sum
  (`PENALTY_HEAD_RACE 450 x max(0.5, length / 4) x ...`, smallest for a 2-long) that a pearl (`EAT_BONUS 300` plus target bonus) can
  outweigh; dragons of 8 or more have a strict "least exposed cell first" order (`LONG_SAFE_MIN_LENGTH` block in
  `pick_direction()`), the 2-3-long queen never enters it.
- **The mirror.** Their queens end a turn in the reach of one of our heads as often as ours does in theirs (5.4 per 1,000
  queen-rounds, both); they ram on 71% of those turns, we on 16%. The lead's own attacker-side data agree (`check_a4.py`): in-view
  ram chances on OUR queen taken by our opponents 197 of 230 = 86% (4.1 rounds with a chance per 1,000 queen-rounds); on THEIR
  queen taken by us 99 of 446 = 22% (3.9 per 1,000). Live bot alone: 88% against 21%.
- **Boxed-in deaths are five things** (91 of 401 games): cut and stuck 14 (a boxed-in queen of 4+ keeps 2 and gives the rest to
  a child: 40 cuts of a queen of 6+ in 37 games, 10 of them at round 3 on one map, also fed queens of 57, 32 and 15; SSS and
  forgot shed 2 and wait: 0 cuts in 1,135 games, and forgot's boxed-in queens of 6+ are alive after 184 of 207 such episodes); her
  own split child on her exit 11; a team-mate's head on her exit 20; a team-mate's body 14; terrain dead end 30 (she ate inside
  in 26). Card #25 (wait) could not fire because the cut had already made her 2 long.
- **Queen rules off** (`is_queen()` false on maps of 600 cells or fewer): she dies at twice the rate; takes a portal step in 27
  of 44 small-map games with portals (7 of 175 with rules on); rams an enemy head herself with a free safe cell in 10 games; 21 of
  the 30 terrain dead-end deaths are there. On Portals the two homes are not connected at all, so all 27 of our queen deaths
  there are self-made.
- **Where she lives matters less than A2 suggested, for us**: her average distance from her start, her eating and how often she is
  seen are like SSS's and forgot's; but a short queen of ours is rammed 1.8 times per 1,000 rounds within 5 cells of her start
  and 5.5-8 beyond 10, and with no own head within 6 steps 9.7 against 2.2 with three or more. A small intruder within 4 steps of
  her is rammed by one of her team in 3.7% of cases (top three 12-17%, our opponents 13.6%). test4's queen walks a 4-cell loop in
  a quarter of her rounds and is almost never rammed on it.
- **What it is worth (A4's arithmetic on played games, three readings: strict / she then survives like a top-three queen / every
  other kind of death stays at our rate):** the "never end in reach" rule alone 26 / 7.4 / 2.4 games of 401 (plus 0.6 to 1.9
  points of win rate); all four families she controls herself (that rule, shed-not-cut, the bans on every map, team-mates off her
  exit) 59 / 18.3 / 8.7 games (plus 2 to 5 points); all 362 deaths 102 / 30.4 / 8.2.
- qn23 ("no trap" candidate, 45 games outside `games.csv`): boxed-in deaths 15 of 45 against 52 of 215 for the live bot (no gain).
  passage2 pairs: the new queen died earlier in 16 pairs, later in 11; the qh31 pairs show the same shift (16 and 10), so the
  "passage change got the queen killed" note is not carried by these data.

## 6f. After the hypotheses, the race read and the two red-team rounds (added at the end of the study)

- `hypotheses.md` (B) proposed four candidates; `redteam.md` (C) recounted them: take the queen +0.5 to +2 points (most likely +1),
  our queen is never spent +0.3 to +1.5, leader rules at round 300 everywhere −1.2 to +1.3, do not give way at contact −0.5 to
  +1.5. A second queen-hunt trial (qh31b) and a guards trial (kg34b, 5 of 30 against 8) finished online during the study.
- `deep-read-5.md` (A5): the longest-dragon race gap at "level total length at round 400" is partly an artefact (a team that has
  fed has spent length); on potential (longest plus the pearls the rest would drop) we win 11 of 23 level races at round 300.
  `redteam-2.md` (C2): about 45% of that gap is the footing; about 8 wins in our 143 races remain against the top three's
  conversion (range 0 to 16). Candidate "one leader, known to all": −0.3 to +0.8.
- **The pearl zone** (the pick, `REPORT.md` section 3): free pearl turns taken go 84% -> 64% -> 58% at round 150 on big maps and
  83% -> 64% -> 51% at round 300 on small maps, in each of eleven runs and in no other team; by the dragon's own believed leader
  (82 readable games) 16-35% within 9 cells and 70-96% beyond; natural intake −22% (small maps) and −33% (big maps) with the
  other side flat; the leader's natural intake does not rise; two thirds of the pearls left are eaten by another small dragon of
  ours about 10 rounds later; but late in the game the zone hands the final longest 3.4 corpse and 2.4 natural pearls per
  small-map race, and 7 of our 41 race wins were closer than that. Sized at +0.3 to +2 points, most likely about +1.

## 7. Known already by the team (do not rediscover)

Weak maps: Australia, Tower Defense, Islands, Around UNSW, Stripes. On Tower Defense we leave the start room at round ~180
(opponents ~19). On big maps we ram in 8% of adjacent turns, opponents in 38%. Top teams have about 60 units by round 200 and feed
from about round 300. Our late feeding often feeds the opponent. A change that let short dragons through narrow passages got our
queen killed online. "Stride" (free sprint steps) raised our economy 14% without more wins. Queen toggles tried locally with no
gain in survival: never step into reach, escorts, give-way, longer queen, no early splits, never split, known cells, safe zone,
portal bans, wait. Local queen-alive rate 11–20% against our own bots. Cards on the board: #7 big-map economy, #14 split stop
(no gain locally), #17 revenge hunt, #31 scout hunter of length 4 or less, #23 no-trap, #25 queen wait, #18 queen should end
longer than 3, #22 late feeding, #21 strides, #16 safe zone.
