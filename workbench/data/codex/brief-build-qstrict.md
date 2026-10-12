# Builder: qstrict

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules), the first builder's notes `data/codex/build/qexit/done.txt` and the round
synthesis `data/codex/astra/sweep/0436/synth/report.md` (the row on a mate closing the queen's last exit, game 1488288 r100-101).
Write only under `data/codex/build/qstrict/`. `main.cpp` is the team's working source (every switch OFF by default);
`main.base.cpp` is the same file untouched.

A teammate's rule, to be built exactly as stated: "ban any 2-or-3-segment dragon from taking a step that completely traps an
adjacent friendly queen with nowhere to move. if that exact spot is the only space the small dragon can go to, it should crash
straight into its own body and die."
Task: add `constexpr bool QUEEN_EXIT_STRICT = false;`. When on: a non-queen dragon of length 2 or 3 whose chosen final move
(any kind: step, stride, portal step, ram, escape) would leave our REAL queen, whose head is adjacent to the cell it enters or
in its view within 2 cells, with no free neighbouring cell (as `keep_queen_exit` counts them), must take another legal move;
if it has none that keeps her a free cell, it kills itself on its own body (or by whatever legal self-destruct the engine
gives a dragon of that length: check the rules and say which) instead of taking the cell. The existing `QUEEN_EXIT_KEEP`
behaviour stays for the cases this does not cover. Say in `done.txt` exactly how this differs from `QUEEN_EXIT_KEEP` in the code
as it is (the earlier builder said that rule already models a self-crash as a move: confirm or correct that from the source).
Requirements: switch false = same program as `main.base.cpp` (guard with the constant; compile both with `c++ -std=c++20 -O2`
to the same output file name, compare sha1, report it); `main.on.cpp` with the switch true compiles. No comments beyond one
short line, no map names, no size tables. Write `diff -u main.base.cpp main.cpp > qstrict.diff` and `done.txt`: lines changed,
sha1 result, whether game 1488288 r100-101 (replay in `data/online/live-one1/b1488287/`) is now covered, and what would show
it is wrong (mates dying beside a queen that then dies anyway). You cannot play games on this machine; do not try.
