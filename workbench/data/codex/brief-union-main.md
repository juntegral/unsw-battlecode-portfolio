# Team main + the solo switches in one source (mechanical merge; I verify by replays afterwards)

You are in a git worktree of the team repo (branch `jun/aggro-switches`, already merged with origin/main). Write only inside this
worktree. Do not commit, push, or touch any other branch. No network, no games.

## Job 1: `mybot2/main.cpp`
Target = team main's bot (`git show origin/main:mybot2/main.cpp`, 5,700 lines) plus EVERY switch that exists in the solo source
`~/meow-redteam/solo/src/solo/main.cpp` (6,228 lines, read-only) and not in main, EXCEPT the code of the two team cards that are not
merged in main yet:
- card 54: `LONG_SAFETY`, `LS_*` constants and everything only they use
- card 55: `QUEEN_FALLBACK`, `QF_*` constants, the `fb_*` state and everything only they use
The solo source = main (commit a358ec8, same mybot2 as origin/main) + solo switches + card 54 code + card 55 code, all default off.
Suggested method: copy the solo source, then take the card code out, using `git diff a358ec8 <card commit> -- mybot2/main.cpp` as the
guide (card 55: 48381e2; card 54: one of the commits on `origin/card/54`, pick the one whose diff reverse-applies with the fewest
rejects, `git log --oneline a358ec8..origin/card/54`). `patch -R` leaves 2 rejected hunks for each card: resolve those by reading both
sides. Where a solo switch and a card touched the same expression, keep the solo switch's part and drop only the card's part.
The solo switches to keep (all must stay default off, with the same default values as in the solo source):
CRAMPED_EAT, EAT_BEFORE_SPLIT, FEEDER_EAT, HARVEST_PORTAL, HEADING_TIE, HUNT_SMALL_RATIO, LEADER_FULL_KEEP, LEADER_FULL_UNITS,
LUNGE_PEARL, POCKET_LOOP, QS_KEEP_LEN, QUEEN_DEAD_ALL, QUEEN_HOME_LEASH, QUEEN_HOME_SLOPE, QUEEN_SURE_LEN, QUEEN_SURE_STEPS,
QW_END_ROOM, RALLY_END_FRESH, SPAWN_CLEAR, SPAWN_CLEAR_ALL, SPAWN_CLEAR_MAX, SPAWN_CLEAR_PENALTY, SPLIT_ROUND0, TRADE_SHORT_BY,
ZONE_NEARER, and any other constant the solo source has that main lacks and that is not card 54/55 (list what you find).
Rules of this repo: no comments added to the bot code, nothing map-specific.
Checks you must run and report:
1. `c++ -std=c++20 -O2 mybot2/main.cpp -o /tmp/union_check_bot` inside the worktree's own tmp folder (use `./.tmp-union/`, delete it after) compiles with no error.
2. `grep -c "LONG_SAFETY\|LS_MIN_LENGTH\|LS_ESCAPE\|LS_PAY\|QUEEN_FALLBACK\|QF_\|fb_on\|fb_" mybot2/main.cpp` is 0 (or explain every hit).
3. The list of `constexpr` names: (result) minus (origin/main) = exactly the solo switch list; (origin/main) minus (result) = empty.
4. Every line that differs from the solo source belongs to card 54 or card 55: show `diff <solo> <result> | grep -c '^[<>]'` and a
   10-line sample; and `git diff --stat origin/main -- mybot2/main.cpp`.

## Job 2: the server profile
The bot we upload to the server is the latest source with a fixed set of switches turned on (the "live profile"), so that a card
tested or shipped online always carries the switches that are live. Add two files:
- `work/server_profile.txt`: one `NAME value` per line, `#` for comments. Content = the live set:
  `ZONE_NEARER true`, `POCKET_LOOP true`, `HARVEST_PORTAL true`, `SPAWN_CLEAR true`, `TRADE_EVEN true`, `LEADER_FULL_UNITS 56`,
  `HUNT_SMALL_RATIO 2`, `QS_KEEP_LEN 3`. Header comment (3 lines): what the file is, that the live bot v62 (submission 20366) = main a358ec8 + this
  profile, and that a line is added or removed only after an online test.
- `work/server_bot.py`: `python3 work/server_bot.py <out dir> [--src <bot dir, default mybot2>] [--profile <file, default work/server_profile.txt>] [--on NAME:value ...] [--no-compile]`.
  It copies main.cpp, helper.hpp, sonar_codec.hpp and bot.toml from the source dir to the out dir, sets every profile constant and
  every `--on` constant in main.cpp with the pattern `(constexpr <type> NAME = )<anything up to ;>;` (each name must match exactly
  once: otherwise exit 1 and name the missing ones, which is how a branch without the switch code is caught), compiles the result
  once to check (`c++ -std=c++20 -O2`, binary not kept), and prints the final list of constants it set and the out dir.
  Plain standard-library Python, short docstring with usage, no other comments needed.
Test it: build an out dir under `./.tmp-union/` from `mybot2` with the profile; confirm each of the eight constants has the profile
value in the out dir's main.cpp; then delete `./.tmp-union/`.

## Hand back
Write `work/UNION-NOTES.md` (to be deleted before commit; plain notes): the card 54 commit you used, how each rejected hunk was
resolved (before/after lines), the outputs of checks 1 to 4, and the server_bot.py test output.
