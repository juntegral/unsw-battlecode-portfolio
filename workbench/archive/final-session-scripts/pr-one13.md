**What this is, in three lines**
- Tried: puts the code of the bot that is live for the deadline (one14, submission 21497) into `main`, with every new switch off by default, and updates the server profile to its 44 switch values.
- Worked? With all switches off the bot plays exactly like the current `main` (checked on 12 local games). With the profile on, the built source is identical to the live bot's source.
- Who decides: jun or Zhe merges. Nothing on the server changes when this is merged; the live bot is already one14.

**Files**
- `mybot2/main.cpp`: the working source of the night of 8-9 Oct. 2,523 lines added, 93 removed.
- `work/server_profile.txt`: 44 switch values (it had 16), header updated to one14.

**Checks**
| check | how | result |
|---|---|---|
| all switches off = current main | 6 maps, both sides, against old main: 12 games of this source and 12 of `main`'s, replays compared byte for byte | same size, 4 differing bytes in each (the two bot names) |
| profile on = live bot | `python3 work/server_bot.py OUT --no-compile` on this branch, then `diff OUT/main.cpp` against the uploaded `one14-bot/main.cpp` | 0 lines differ (checked again after the second commit) |
| live bot | `submit.js check` at 10:24 KST | active 21497, server copy identical to the folder |

**What the switches are** (all off in `main`; the profile turns these on)
A glossary, newest last. "Queen" = the dragon with the lowest starting id, the first tiebreak.
- From one5 and earlier: `EAT_FIRST` (a pearl one step away is eaten), `HEADING_TIE` (keep straight in the first 12 rounds), `FEED_CAP_ROUND 350`, `QUEEN_HERD`, `QUEEN_DEFEND_STEPS`, and the eight switches of v62.
- one6 to one8: `SMALL_SPRINT_THREAT` (short dragons price an enemy's sprint reach), `MATE_UNPIN` (no pinning a mate on a wall), `POCKET_KEEP_OUT`, `TARGET_REACHABLE`, `QUEEN_DEAD_ALL`, `QUEEN_EXIT_KEEP`, `QS_KEEP_MIN_UNITS 2` (a queen alone may split).
- one9 to one11: `REACH_EATS` (an enemy's reach counts pearls it eats on the way), `SPLIT_PORTAL_OK`, `QUEEN_SURE_LEN 64` / `QUEEN_SURE_STEPS 5` (any dragon rams their queen when it can reach her head), `CUT_BODY_LEN 4`, `QS_PAY_REACH 4`, `CUT_BODY_STRIDE`, `QUEEN_BOOT_LEN 6`, `QUEEN_PORTAL_LAST`, `QUEEN_EXIT_STRICT` (Zhe's rule: a mate of 2 or 3 never takes the queen's last free cell).
- one12: `BIG_ESCAPE_STEPS 6` / `BIG_ESCAPE_MIN_LENGTH 8`, `TERRITORY_DECAY 16`, `QUEEN_FAR_HEADS 2`, `QUEEN_CORRIDOR_GUARD 6`.
- In the code but off in the profile (built, tested, not kept): `SHORT_EVADE` and its two options, `RALLY_END_FRESH`, `QUEEN_PORTAL_ALL`, `QUEEN_WAR`, `WAR_FEED_FIRST`, `QUEEN_EDGE_REACH`, `PORTAL_SCOUT_MIN_LEN` (see the update below).

**Update 10:24 KST: one14 = one13 without `PORTAL_SCOUT_MIN_LEN`** (second commit)
The rule "a dragon under 4 does not step through a portal nobody has seen through when an ordinary way is open" kept the whole side out of portals: on open ground an ordinary way is always open, and since nobody crosses, the far side never becomes seen. Our pearls by round 100, per map, means of 3 to 4 online games a version:
| map | one11 | one12 | one13 |
|---|---|---|---|
| Portals | 238 | 76 | 71 |
| Trauma | 41 | 8 | 4 |
| Queen Of Spades | 59 | 11 | 30 |
| Australia | 92 | 49 | 36 |
| Default | 58 | 22 | 32 |
| Trophy | 112 | 70 | 66 |

Maps without long portals did not move. It was found from a 1-4 ranked loss to a team 90 points below us; the local head to head had not shown it (21-2-21 with and without the rule).

**Why one13 was chosen at 09:00** (numbers from the night; each online set is 15 games)
| | one11 | one12 | one13 |
|---|---|---|---|
| Cache me outside | 4 | 2 | 6 |
| Preyas | 3 | 4 | 4 |
| kraken | 10 | 8 | 8 |
| online total of 45 | 17 | 14 | 18 |
| local head to head against one5, 48 games (wins-draws-losses) | 21-2-24 | 25-1-22 | 25-2-21 |

One thing learned on the way: a 15-game online set cannot tell two versions apart (the same bot scored 8 and then 4 of 15 against the same unchanged opponent), so versions were compared by playing them against each other locally on maps none of them was tuned on.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
