# Builder: pocket

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules) and `data/codex/astra/deathcell/report.md` (all of it, with its ten
cells and its reading of the dead-end terms) first. Write only under `data/codex/build/pocket/`.

Why: 64% of our non-combat deaths (22,045 of 34,201 over 191 games) are on cells where another dragon of ours died the same way in
the same game; the opponents' share is 43%. In ranked game 1471966 three of ours, the last one the queen, died on a wall in the
same cell behind a portal. The report's card: when another legal move exists, a queen, or a dragon that will be shorter than 4
after eating there, does not enter a cell from which every known exit only leads back onto its own neck.

Task: in `main.cpp` (working source, every switch OFF by default; `main.base.cpp` is the same file untouched) add
`constexpr bool POCKET_KEEP_OUT = false;` and implement the card as a final check on the chosen move (ordinary step, stride,
portal step; not an intended ram or hunt): simulate the dragon's own body after the move (growth if a pearl is eaten there, the
tail leaving otherwise) and the exits of the destination as known this turn (walls, portals with their known exits, bodies and
heads in view; an unknown edge or an unknown portal exit counts as an exit). If no exit remains other than cells of its own body,
reject the move when another legal, not rejected move exists, keeping the bot's own score order among the alternatives. Apply it
to the real queen at any length and to any dragon whose length after the move is under 4 (a longer dragon may be harvesting on
purpose; leave it). Reuse the body simulation of `keep_queen_exit` / the MATE_UNPIN code already in the file where it fits.
Requirements:
- switch false = same program as `main.base.cpp` (guard every statement with the constant; no state updated when off): compile
  both with `c++ -std=c++20 -O2` to the same output file name, compare sha1, report it. `main.on.cpp` with the switch true compiles.
- CPU: the four neighbours of one destination, no flood. No comments beyond one short line, no map names, no size tables.
- `diff -u main.base.cpp main.cpp > pocket.diff` and `done.txt`: lines changed, sha1 result, exactly what counts as an exit,
  which of the report's ten cells the rule would have refused (work it out from the replays), and what would show it is wrong.
You cannot play games on this machine; do not try.
