# Builder: corridor

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules), `data/codex/astra/CARDS.md`, the round synthesis
`data/codex/astra/sweep/0544/synth/report.md` (the row "여왕의 보이는 막다른 외길 진입" and the loss reports it points to: games
1493880 r241/r244 and 1493891 r302-307) and the notes of the builders whose machinery you reuse: `data/codex/build/qstrict/done.txt`,
`data/codex/build/pocket/done.txt`. Write only under `data/codex/build/corridor/`. `main.cpp` is the team's working source = live
one11's source with every switch OFF by default; `main.base.cpp` is the same file untouched.

Why: our queen walks into a corridor she can see is a dead end (one way in, no way on once her body and the pearl she eats are
counted) and dies there or is hit at its mouth. The existing terms only penalise it (a score term), check a single exit cell,
or wait-split once she is already inside.

Task: add `constexpr int QUEEN_CORRIDOR_GUARD = 0;` (0 = off; a positive value = how many steps ahead the walk looks, test 6).
When on, as a final check on the REAL queen's chosen move (ordinary step, stride, portal step): simulate her body after the
move (growth if she eats, tail leaving otherwise) and walk forward from the destination through cells known this turn (walls,
known portals and their exits, bodies and heads in view; an unknown edge or portal counts as a way on). If within that many
steps every continuation ends in a cell with no way on other than back over her own body, the move is refused when another
legal, not rejected move exists that does not; among the alternatives keep the bot's own score order. If there is none she
moves as now. It must not refuse a corridor that has a second mouth, nor a room with at least `length + 2` free cells.
Requirements: value 0 = same program as `main.base.cpp` (guard with the constant; no state updated when off; compile both with
`c++ -std=c++20 -O2` to the same output file name, compare sha1, report it); `main.on.cpp` with the value 6 compiles. CPU: a
bounded walk from one destination, no flood. No comments beyond one short line, no map names, no size tables.
Write `diff -u main.base.cpp main.cpp > corridor.diff` and `done.txt`: lines changed, sha1 result, how a dead end is decided,
whether the entries at 1493891 r302 and 1493880 r241 / r244 are now refused and what she would do instead (work it out from the
replays under `data/online/`), and what would show it is wrong (her pearls per game falling: she refuses pockets that hold food
and are safe). You cannot play games on this machine; do not try.
