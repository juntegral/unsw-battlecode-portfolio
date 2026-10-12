# Builder: qcut

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules) and `data/codex/astra/weak-b1485486/report.md` (all of it: card 1, its
line references for one8, and the two hits it must cover) first. Write only under `data/codex/build/qcut/`.

Why: team kraken has beaten us 3 to 2 three times tonight by ramming our queen. In two of the last three lost games the rammer's
body was cut by the edge of our queen's 7 by 7 view, the bot took the visible part as its length (1 seen, 3 assumed, reach 2)
and the real reach was 3.

Task: in `main.cpp` (the team's working source = live one9's source with every switch OFF by default; `main.base.cpp` is the same
file untouched; line numbers differ from the report's one8 numbers, find the same code) add
`constexpr int CUT_BODY_LEN = 0;` (0 = off; test value 4). When positive, for the REAL QUEEN's safety computations only (the
single-move threat field and the sprint end-point / hit / pay rings): an enemy whose visible body reaches the edge of what the
queen can see this turn (its body may continue outside the view) is given a length of at least `CUT_BODY_LEN`, or the largest
length the side has recorded for that id if that is larger, and the SAME length is used in every one of those computations.
An enemy whose whole body is in view keeps its true length. `QS_PAY_REACH` and the other caps stay.
Requirements: `CUT_BODY_LEN = 0` = same program as `main.base.cpp` (guard with the constant; no state updated when off; compile
both with `c++ -std=c++20 -O2` to the same output file name, compare sha1, report it); `main.on.cpp` with the value 4 compiles;
it must also work with `REACH_EATS` true (that switch adds pearls eaten on the way to the same searches). No comments beyond one
short line, no map names, no size tables.
Write `diff -u main.base.cpp main.cpp > qcut.diff` and `done.txt`: lines changed, sha1 result, how "cut by the view" is decided,
whether the two hits of the report (Slithery Fight 1485486 and Trauma 1485490, replays in `data/online/live-one1/b1485486/`)
are now marked dangerous on the queen's last own turn, and what would show it is wrong (the queen's pearls per game falling
because every half-seen enemy freezes her). You cannot play games on this machine; do not try.
