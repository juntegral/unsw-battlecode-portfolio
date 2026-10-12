# Builder: avenge

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules), `data/codex/astra/weak/report.md` (the table of losses to lower-rated
teams) and `data/codex/astra/queenhunt/report.md` first. Write only under `data/codex/build/avenge/`.

Why: all ten games lost tonight to lower-rated teams were lost the same way: our queen died (rammed in eight) between r10 and r400
and in six of them the enemy queen was still alive at r499, so we lost on the first tiebreak although our total length and longest
dragon were level or ahead. Once our queen is dead and theirs lives, the only way to win is to kill theirs, and nothing is left
to protect. The bot has a queen-hunt mode (`QUEEN_HUNT`, `QUEEN_CHASE_DIST`, the `qh_*` code, hunter tokens, sonar sighting of the
enemy queen) that was rejected as an always-on mode because it spent long dragons and exposed our own queen.

Task: in `main.cpp` (working source, all switches OFF by default; `main.base.cpp` is the same file untouched) add one switch
`constexpr int QUEEN_AVENGE = 0;` (0 = off; a positive value N = the chase distance to use, test value 8). When it is positive:
- the hunt machinery is armed only while this dragon believes our real queen is dead and the enemy queen is not known dead. Use
  whatever the bot already tracks and shares for this (find how `queen_game`, the queen sighting/death sonar fields and the real
  queen's id are maintained; a dragon that has never seen our queen is not enough: require the shared death signal or having
  seen her die, and say in `done.txt` exactly which signal you used and how reliable it is; if no dragon can know that our
  queen died, add the smallest sonar or state change that makes it known, guarded by the switch);
- while armed it behaves as `QUEEN_HUNT true` with `QUEEN_CHASE_DIST N` would for non-leader dragons of length 4 or less; the
  leader and long dragons keep their normal play (they are the longest-dragon tiebreak once her queen dies);
- once the enemy queen is known dead it disarms and play returns to normal.
Requirements:
- `QUEEN_AVENGE = 0` must compile to the same program as `main.base.cpp` (guard every new statement with the constant, no state
  updated when off). Check with `c++ -std=c++20 -O2`, same output name for both compiles, compare sha1, say the result.
  `main.on.cpp` with `QUEEN_AVENGE = 8` must compile. It must also be correct with `QUEEN_HUNT` false (the live setting).
- No comments beyond one short line each, no map names, no size tables, code style as around it.
- `diff -u main.base.cpp main.cpp > avenge.diff` and `done.txt`: lines changed, the sha1 result, the signal used, what the lead
  should count in a replay to see it fire (rounds from our queen's death to the first hunter within 5 cells of their queen, her
  death round) and what would show it is wrong.
You cannot play games on this machine; do not try.
