**What this is, in three lines**
- Tried: `main` follows the live bot again. Three commits: (1) the profile drops `TERRITORY_DECAY` (live bot one15, 11:44 KST); (2) one new switch in the code, `QUEEN_NO_BLIND_PORTAL` (4 added lines, off by default), on in the profile (one16, 12:51 KST); (3) one new constant, `QS_SHED_MAX` (2 lines, 0 = off), set to 9 in the profile (live bot one17, submission 21693, 13:31 KST).
- Worked? With the new switches off the program is the same as before (same binary). `python3 work/server_bot.py OUT --no-compile` on this branch gives a source identical to the uploaded `one17-bot/main.cpp` (0 lines differ).
- Who decides: jun or Zhe merges. Nothing on the server changes when this is merged.

**Commit 1: `TERRITORY_DECAY` off**
`TERRITORY_DECAY 16` (added in one12: territory far from a dragon counts less) starved us on Queen Of Spades. Each one12 switch was taken out of one14 in turn and played on that map locally, against old main, both seats:

| build | pearls by r100, seat A / B | dragons at r100, seat A / B |
|---|---|---|
| one14 | 8 / 3 | 3 / 2 |
| one14 without `TERRITORY_DECAY` | 44 / 40 | 17 / 11 |
| one11 | 44 / 55 | 17 / 16 |
| one14 without any of the other four one12 switches | same as one14 | same as one14 |

Online afterwards: our pearls by r100 on that map were 17 with one14 and 57 with one15. On all 16 local ladder maps (32 pairs against old main) one15 against one14: natural pearls by r100 3224 against 3050, wins 22 against 15.

**Commit 2: `QUEEN_NO_BLIND_PORTAL`**
The queen is the dragon with the lowest starting id; the longer queen is the first tiebreak and a dead queen counts 0. On maps of 600 cells or fewer the queen was allowed to scout portals whose far side nobody had seen (`can_scout_portals()` only excludes her above `QUEEN_MIN_CELLS`). On Portals the far side is a closed 2x2 pearl room or a one-cell pocket: she eats, splits, and the way back lands on her own body. Our queen died in 30 of 30 Portals games of one11 to one14, 28 of them with no free side, six at round 9 or 10. The switch stops the real queen from taking such a portal.

| Portals, local, 15 games | one15 | one16 |
|---|---|---|
| queen dead by r100 | 6 of 7 | 1 of 8 |
| queen alive at r500 | 0 of 7 | 2 of 8 |
| queen portal steps per game | 23 | 3 |
| wins | 2 of 7 | 5 of 8 |
| pearls by r100 | 204 | 173 |

On Stripes, a generated portal map and 8 maps without portals one16 plays the same game as one15 (13 of 13 compared event for event). Known cost: about 15 percent fewer early pearls on Portals; she still dies there later in most games by being boxed in.

Online afterwards (one16 against Cache me outside, Portals): no queen portal step in the first 100 rounds (one15 took them at r4 and r8), 22 dragons at r100 against 16, game won.

**Commit 3: `QS_SHED_MAX`**
The queen has an emergency rule: when she thinks an enemy can reach her own cell and finds no escape, she splits, keeps 2 cells and lets the rest leave as an ordinary dragon. For a long queen that gives up the first tiebreak. Counted over 474 games of one11 to one15:

| queen splits down to 2 from 10 or longer | |
|---|---|
| how often | 21 games, all after round 339 |
| she led the queen race before it | 15 of 21 |
| dead within 3 rounds / within 20 | 12 / 16 of 21 |
| games lost | 18 of 21 |
| comparison: long queen near an enemy head that did not split | 42 games, 21 won |

With `QS_SHED_MAX 9` a queen of 10 or longer skips that rule and makes her ordinary move; at 9 or shorter nothing changes. In 8 local games against old main one17 plays the same game as one16 (same result and final lengths), so it acts only in the rare spot it was made for; what it buys can only show online.

Local map files of seven ladder maps are rebuilt from replays, so their pearl supply is an estimate; comparisons between builds on the same file are what counts.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
