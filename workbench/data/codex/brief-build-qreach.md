# Builder: qreach

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules), `data/codex/astra/kraken/report.md` (all of it, with
`queen-boards.md`) and `data/codex/astra/weak-b1476178/report.md` first. Write only under `data/codex/build/qreach/`.

Why: every game we lost tonight to a lower-rated team had our queen dead, usually rammed. Team kraken beat us 3-2 twice; in its
games an enemy of length 3 ate two pearls on the way and hit our queen with its fourth step (weakhold 1482056 r37, dragon 3), and
a length-2 enemy ate one pearl and hit her with its second step (Trauma 1483347 r460, dragon 191). Our queen's danger rings and
the short dragons' threat field count an enemy's reach from its length NOW: free steps ceil(L/4), plus paid steps while it stays
at least the minimum length. A pearl eaten on the way adds a segment, so it pays for one more step, and can raise the free steps.

Task: in `main.cpp` (the team's working source, every switch OFF by default; `main.base.cpp` is the same file untouched) add
`constexpr bool REACH_EATS = false;`. When on, wherever the bot computes how far a visible enemy head can get next turn for
(a) the real queen's safety rings (`QS_*`, `ring_wary`, the hit / pay tiles, `QS_PAY_REACH`), (b) `SMALL_SPRINT_THREAT`, and
(c) `SHORT_EVADE` with `SHORT_EVADE_PAID`, the enemy's budget is computed along the path: each visible pearl on a cell of the
path adds one segment from that step on (so one more paid step is affordable, and the free-step count is re-derived from the
grown length if the engine does so; check the rules in `~/meow-redteam/docs/` and the engine for when growth takes effect and
whether a dragon may keep moving after eating in the same turn, and follow the engine exactly). Keep every existing cap
(search depth, `QS_PAY_REACH`) but let the caps count steps, not segments. No change to how OUR dragons plan their own moves.
Requirements: switch false = same program as `main.base.cpp` (guard with the constant; no state updated when off; compile both
with `c++ -std=c++20 -O2` to the same output file name, compare sha1, report it); `main.on.cpp` with the switch true compiles.
CPU: no new flood; extend the existing bounded searches. No comments beyond one short line, no map names, no size tables.
Write `diff -u main.base.cpp main.cpp > qreach.diff` and `done.txt`: lines changed, sha1 result, the engine rule you followed
(with file and line), whether the two cited hits would now be inside the ring on our queen's last own turn (work it out from the
replays in `data/online/live-one1/b1482056/` and `b1483343/`), and what would show it is wrong (queen frozen by rings that are
too wide: her pearls per game falling). You cannot play games on this machine; do not try.
