**What this is, in three lines**
- Tried: `main` follows the live bot again. Two commits: (1) the profile drops `TERRITORY_DECAY` (live bot one15, 11:44 KST); (2) one new switch in the code, `QUEEN_NO_BLIND_PORTAL` (4 added lines, off by default), turned on in the profile (live bot one16, submission 21651, 12:51 KST).
- Worked? With the new switch off the program is the same as before (same binary). `python3 work/server_bot.py OUT --no-compile` on this branch gives a source identical to the uploaded `one16-bot/main.cpp` (0 lines differ).
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

Local map files of seven ladder maps are rebuilt from replays, so their pearl supply is an estimate; comparisons between builds on the same file are what counts.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
