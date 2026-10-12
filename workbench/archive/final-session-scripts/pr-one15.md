**What this is, in three lines**
- Tried: the server profile follows the live bot again. one15 (submission 21583, live since 11:44 KST) is one14 without `TERRITORY_DECAY`; this removes that one line from `work/server_profile.txt`. No code change.
- Worked? `python3 work/server_bot.py OUT --no-compile` on this branch gives a source identical to the uploaded `one15-bot/main.cpp` (0 lines differ).
- Who decides: jun or Zhe merges. Nothing on the server changes when this is merged.

**Why the switch went off**
`TERRITORY_DECAY 16` (added in one12: territory far from a dragon counts less) starved us on Queen Of Spades. Each one12 switch was taken out of one14 in turn and played on that map locally, against old main, both seats:

| build | pearls by r100, seat A / B | dragons at r100, seat A / B |
|---|---|---|
| one14 | 8 / 3 | 3 / 2 |
| one14 without `TERRITORY_DECAY` | 44 / 40 | 17 / 11 |
| one11 | 44 / 55 | 17 / 16 |
| one14 without any of the other four one12 switches | same as one14 | same as one14 |

Online the same map: our pearls by r100 were 59 with one11 and 17 with one14 (3 games each). The local map file is rebuilt from a replay, so its pearl supply is an estimate; the comparison between builds on the same file is what counts.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
