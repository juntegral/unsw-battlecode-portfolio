# Builder: evadepay

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules), `data/codex/astra/evade2/report.md` (all of it) and the first builder's
notes `data/codex/build/evade/done.txt` first. Write only under `data/codex/build/evadepay/`.

Why: `SHORT_EVADE` (in this file, off by default) changed about 0.10% of turns and did not lower the rate at which our short
dragons die to rams. Of the 329 avoidable rams in the first count, 139 came from outside the attacker's FREE reach (it paid a
segment to sprint) and 127 happened while we had more heads in view, where the rule does not apply; only 36 matched the rule.

Task: in `main.cpp` (working source, every switch OFF by default; `main.base.cpp` is the same file untouched) add two constants
beside `SHORT_EVADE`: `constexpr int SHORT_EVADE_PAID = 0;` = how many paid sprint steps to add to the reach of a visible enemy
head whose known length lets it pay them (it must stay at least the minimum length after paying), and
`constexpr bool SHORT_EVADE_ANY = false;` = when true the heads-in-view condition is dropped (the rule applies whatever the
local head count; the exception for a mate head nearer to the destination stays). Both only matter when `SHORT_EVADE` is true.
With `SHORT_EVADE` true and the two new constants at 0 / false the program must be the same as before; with everything false
it must be the same as `main.base.cpp`. Check both by compiling to the same output file name with `c++ -std=c++20 -O2` and
comparing sha1 (for the first check build a copy of `main.base.cpp` with `SHORT_EVADE` true as the reference). A copy
`main.on.cpp` with SHORT_EVADE true, PAID 1, ANY true must compile. No comments beyond one short line, code style as around it.
Write `diff -u main.base.cpp main.cpp > evadepay.diff` and `done.txt` (lines, both sha1 results, how the paid reach is computed,
CPU bound, what to count in a replay). You cannot play games on this machine; do not try.
