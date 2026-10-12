# Builder: qboot

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules) and `data/codex/astra/avengewhy/report.md` (the table of games where
both queens were alive at the end, the paragraph under it, and card B) first. Write only under `data/codex/build/qboot/`.

Why: the first tiebreak is the longer queen. In Trauma 1485180 both queens lived to the end, ours 3 long, theirs 16, and we lost a
game we led. In the feeding phase (from r300) mates feed the queen only if their length times 2 is at most hers; a queen of 3
therefore gets nothing (the mates near her were 2 and 3 long) and she ate, split and paid nothing for 200 rounds. In Trauma
1483019 the same bot started the phase with a queen of 6, was fed 24 corpse pearls and ended 39 long.

Task: in `main.cpp` (the team's working source = live one9's source with every switch OFF by default; `main.base.cpp` is the same
file untouched; the report's line numbers are one8's, find the same code) add `constexpr int QUEEN_BOOT_LEN = 0;` (0 = off; test
value 6). When positive, in the feeding phase a mate of length 2 or 3 is exempt from the length-ratio condition when the target
it would feed is our REAL live queen and she is shorter than `QUEEN_BOOT_LEN`; every other existing condition (safety, distance,
enemies in view, who may feed) stays. Also make sure the queen, while shorter than `QUEEN_BOOT_LEN` in the feeding phase, does not
split away what she is fed (find the queen's split rule in that phase and say what it does; change it only under this switch).
Requirements: `QUEEN_BOOT_LEN = 0` = same program as `main.base.cpp` (guard with the constant; no state updated when off; compile
both with `c++ -std=c++20 -O2` to the same output file name, compare sha1, report it); `main.on.cpp` with the value 6 compiles.
No comments beyond one short line, no map names, no size tables.
Write `diff -u main.base.cpp main.cpp > qboot.diff` and `done.txt`: lines changed, sha1 result, whether dragons 134 and 173 of game
1485180 (replay in `data/online/smoke/one8-k1-old/`) would now qualify at r300, and what would show it is wrong (feeders dying
for nothing, the fed queen rammed). You cannot play games on this machine; do not try.
