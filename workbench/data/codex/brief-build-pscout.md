# Builder: pscout

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules), `data/codex/astra/CARDS.md` and `data/codex/astra/walls/report.md` (all of
it: the class table, card A with its line references for one11, and its three example turns) first.
Write only under `data/codex/build/pscout/`. `main.cpp` is the team's working source (live one11's source plus QUEEN_CORRIDOR_GUARD,
every switch OFF by default); `main.base.cpp` is the same file untouched.

Why: of our 21,265 deaths on a wall or on our own body, 2,005 are short dragons that step through a portal whose far side the
side has never seen and are boxed there, although an ordinary step with a visible way on was available. The portal scouting
bonus (`WEIGHT_PORTAL_SCOUT`) pulls them in; `QUEEN_PORTAL_LAST` protects only the queen.

Task: add `constexpr int PORTAL_SCOUT_MIN_LEN = 0;` (0 = off; test value 4). When positive: a non-queen dragon shorter than that
value does not take, as its final move, a step through a portal whose exit cell the side has not seen, when it has another legal,
not rejected move onto an ordinary cell from which at least one further free cell is visible; among those alternatives keep the
bot's own score order. A dragon of that length or more scouts as now (it can pay or split its way out), and a short dragon with
no such ordinary move also moves as now. Apply it to every path that can emit a portal step (ordinary step, stride, escape).
Requirements: value 0 = same program as `main.base.cpp` (guard with the constant; no state updated when off; compile both with
`c++ -std=c++20 -O2` to the same output file name, compare sha1, report it); `main.on.cpp` with the value 4 compiles. CPU: the
destination's neighbours only. No comments beyond one short line, no map names, no size tables.
Write `diff -u main.base.cpp main.cpp > pscout.diff` and `done.txt`: lines changed, sha1 result, whether the report's three
example turns (1483015 dragon 5 r15, 1489833 dragon 201 r160, 1496003 dragon 187 r278; replays under `data/online/`) are now
refused and what the dragon does instead, and what would show it is wrong (portal connections never learned, so regions behind
portals are not harvested: natural pearls per turn on portal maps falling). You cannot play games on this machine; do not try.
