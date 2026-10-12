# Builder: unpin

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules) first. Write only under `data/codex/build/unpin/`.

Case (replay `data/online/live-one1/b1476178/M1476179.replay`, Tower Defense, our dragons are ids 1 and 3, both length 2):
from r13 they walk east side by side, id 3 on row 7 along a kelp wall on its north side, id 1 on row 8 one column ahead. Id 1 moves
first each round, so when id 3 moves, the cell south of its head holds id 1's body: id 3 has exactly one legal move (east) every
round. At r16 id 3 is in the corner (29,7) (walls north and east, its own body west) and id 1 has just stepped south from (29,8),
leaving its tail there: id 3 has no move and dies on its mate's body. The same death on the same cell in game 1465497. With a
two-dragon start that is half the team at r16; both games were lost. The existing switch `QUEEN_EXIT_KEEP` (an earlier builder's
work, in this file; read `keep_queen_exit`) stops a mate from closing the QUEEN's last exit; this case is the mirror: the queen
(id 1) pins a mate, and it is decided two or three rounds before the death.

Task: in `main.cpp` (working source, every switch OFF by default; `main.base.cpp` is the same file untouched) add a switch
`constexpr bool MATE_UNPIN = false;`. When on, a dragon (the queen included) that sees a mate's head must not make a move after
which that mate is left with no legal move on its coming turn, and should avoid a move after which the mate has exactly one
legal move that leads into a cell with no way on (a dead end by walls and bodies as known this turn, looking at most 4 steps
ahead along the forced line), when the mover itself has another legal move that is not rejected by its own scoring. Reuse
`keep_queen_exit`'s machinery where it fits. The rule must be symmetric and general: no ids, no map names, no size tables.
Requirements:
- `MATE_UNPIN = false` must compile to the same program as `main.base.cpp` (guard every new statement with the constant; no state
  updated when off). Check with `c++ -std=c++20 -O2`, same output file name for both compiles, compare sha1, report it.
  `main.on.cpp` with the switch true must compile.
- CPU: only when a mate head is within 2 cells; a bounded walk, no flood.
- No comments beyond one short line, code style as around it.
- `diff -u main.base.cpp main.cpp > unpin.diff` and `done.txt`: lines changed, sha1 result, what exactly is checked, the rounds
  in game 1476179 where the rule would have changed id 1's move (work it out from the replay by hand or by script; you may read
  replays with `tools/ladder_replay.py` as `data/analysis/ladder/dossier/work/o1_look.py` does), and what would show it is wrong.
You cannot play games on this machine; do not try.
