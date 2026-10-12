# Builder: three

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules), `data/codex/astra/CARDS.md`, the round synthesis
`data/codex/astra/sweep/0410/synth/report.md` (rows 1 and 2 and the "live fixes that failed" paragraph, with the loss reports it
points to) and the notes of the builders whose code you extend: `data/codex/build/qcut/done.txt`, `data/codex/build/war/done.txt`.
Write only under `data/codex/build/three/`. `main.cpp` is the team's working source (every switch OFF by default) and already
contains CUT_BODY_LEN, QUEEN_PORTAL_ALL, QUEEN_WAR and the rest; `main.base.cpp` is the same file untouched.

Three small switches, each off by default and each independent of the others:
A. `constexpr bool CUT_BODY_STRIDE = false;` When on (and `CUT_BODY_LEN` > 0), the real queen's multi-step move end-point check
   (`STRIDE_SAFE_END` and whatever else judges the last cell of a stride or sprint of hers) uses the SAME enemy length as the
   rings do under `CUT_BODY_LEN` (cut body = at least that long), and counts a cut enemy's reach without assuming it eats.
   The synthesis lists the turns it must mark dangerous: 1485490 r430 and the other four of its first row.
B. `constexpr bool QUEEN_PORTAL_LAST = false;` When on, the real queen's emergency entry into a portal whose far side the side has
   never seen (the branch near one8's lines 1487-1510 that fires when no ordinary exit is left) is refused as long as she has
   ANY other legal move, including a wait-split or a paid step, and when the portal is truly the only move she takes it as now.
   The synthesis' second row lists the four entries (1483997 r73, 1485181 r105, 1485489 r113, 1486054 r111).
C. `constexpr bool WAR_FEED_FIRST = false;` (a teammate's idea) When on and a dragon is in the armed QUEEN_WAR or QUEEN_AVENGE
   state: if on this turn it is in a position where the bot's existing leader-feeding action would trigger (it stands where the
   feed / stop-drop beside the leader is allowed by the existing feeding rules), it performs the feed, and only otherwise goes
   for their queen. Nothing else about either mechanism changes.
Requirements: with all three false the program is the same as `main.base.cpp` (guard every statement with its constant; no state
updated when off; compile both with `c++ -std=c++20 -O2` to the same output file name, compare sha1, report it). A copy
`main.on.cpp` with the three true, `CUT_BODY_LEN` 4, `QUEEN_WAR` 8 must compile. No comments beyond one short line each, no map
names, no size tables. Write `diff -u main.base.cpp main.cpp > three.diff` and `done.txt`: per switch the lines changed, what
exactly it checks, which of the listed turns it now covers (work it out from the replays under `data/online/`), and what would
show it is wrong. You cannot play games on this machine; do not try.
