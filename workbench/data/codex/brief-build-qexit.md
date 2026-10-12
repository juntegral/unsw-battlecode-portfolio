# Builder: qexit

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules) first. Write only under `data/codex/build/qexit/`.

Task: implement card 2 of `data/codex/astra/queenbox/report.md` (read it and its `code.md`) in `data/codex/build/qexit/main.cpp`,
a copy of the team's working source in which every switch is OFF by default (`main.orig.cpp` is the untouched copy).
The rule: a non-queen dragon of ours that can see our real queen's head must not make a move (ordinary step, stride, ram, escape,
split child placement) after which the queen's head has no free neighbouring cell left, when it has another legal move that is
not rejected. If every alternative is rejected it moves as before. The queen's free neighbours are counted from what the mover
knows this turn (walls, portals, bodies, heads; the cell the mover leaves becomes free only if its tail leaves it).
Requirements:
- One new switch `constexpr bool QUEEN_EXIT_KEEP = false;` beside the other queen switches. With it false the compiled program
  must be the same as before: guard every new statement with the constant so the compiler folds it away, add no new state that
  is updated when off. Check: compile `main.orig.cpp` and `main.cpp` with `c++ -std=c++20 -O2` and compare the two binaries'
  sha1; they must be equal. Then set the switch true in a second copy `main.on.cpp` and check it compiles.
- No comments beyond one short line, no map names, no size tables. Match the code style around it.
- Write `diff -u main.orig.cpp main.cpp > qexit.diff` and `done.txt`: the lines changed, the sha1 check result, every move path
  you covered and any you did not, and what the lead should look for in a replay to see it fire.
You cannot play games on this machine; do not try.
