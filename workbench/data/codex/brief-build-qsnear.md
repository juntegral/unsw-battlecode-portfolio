# Builder: qsnear (the queen does not shed her length next to an enemy head)

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules), `data/codex/astra/CARDS.md`, and the two cases in
`data/codex/astra/weak13-opus/queen-boards.txt` (games 1508962 and 1508963; ledgers in `ledger.txt` beside it).
Write only under `data/codex/build/qsnear/`. `main.cpp` there is the team's working source (every switch OFF by default);
`main.base.cpp` is the same file untouched. The live bot is that source with the switch values in `one14.switches` (same folder).

Why: the first tiebreak of the game is the longer queen, and a dead queen counts 0. Twice in one battle our queen split while
an enemy head was beside her and died the same or the next round:
- 1508962 (Slithery Fight): she was 28 long and led 28 to 20. An enemy of 2 walked beside her for four rounds (its head adjacent
  at each of her turn starts; she took one step a turn with 7 free steps available). Round 374, two more heads of 2 in view:
  she split keeping 2 (the child got 26) and was rammed that round; the child was rammed three rounds later.
- 1508963 (Islands): at 8 long she split keeping 2 with an enemy of 3 at distance 3, stepped into a one-wide lane, and was rammed.
The split is the code around the queen's keep-length rule (QS_KEEP_LEN, QS_KEEP_MIN_UNITS, QS_PAY_REACH; search `real_queen()`
near `can_split`).

Task: add `constexpr int QS_HEAD_CLEAR = 0;` (0 = off; a positive value = a distance in steps, test 4). When on, the REAL queen
does not split on a turn when an enemy head in view could reach her head or the cell she would stand on after the split within
that many steps (count the enemy's free steps for its remembered or visible size; if you cannot size it, treat any head within
the distance as able). Feeding a mate, eating and moving are unchanged. Also when on: if such a head is adjacent to her head at
her turn start and she has free steps, she may not choose a move that leaves her head adjacent to that same enemy head when
another legal move exists (keep the bot's own score order among the rest). Nothing changes for other dragons.
Requirements: value 0 = same program as `main.base.cpp` (guard with the constant; no state updated when off; compile both with
`c++ -std=c++20 -O2` to the same output file name, compare sha1, report it); a copy with the value 4 compiles. CPU: one pass over
enemy heads in view. No comments beyond one short line, no map names, no size tables.
Write `diff -u main.base.cpp main.cpp > qsnear.diff` and `done.txt`: lines changed, sha1 result, which split sites are guarded,
what she does instead at 1508962 r370-374 and 1508963 r337 (work it out from the replays under `data/online/live-one1/b1508960/`),
and what would show the switch is wrong (her mates starving because she stops handing length over whenever enemies are around;
our dragon count at r200 falling). You cannot play games; do not try.
