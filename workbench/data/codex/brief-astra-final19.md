# Last audit before the final upload (deadline 15:00 KST; report by 14:36 KST, short)

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules: [M]/[C]/[E]). Write only under `data/codex/astra/audit-final19/`.
No games, no uploads, no edits of sources.

Files: the live source is `~/meow-redteam/solo/src/solo/main.cpp` (= one18); the candidate source for the last bot is
`~/meow-redteam/solo/src/w-one19/main.cpp`. Run `diff` between them: it should show only two new constants
(`QUEEN_NO_RAM`, `SPLIT_KNOWN_TAIL`), two changed conditions in the queen's "Trapped" branch, and three added lines in
`split_child_size`. The last bot's switch values are in `~/.claude/jobs/e2109d93/tmp/one19B.switches`
(compare with `one18.switches` beside it: QUEEN_DEAD_ALL is REMOVED, i.e. back to its default false; CENTER_MAX_CELLS becomes
100000; QUEEN_NO_RAM and SPLIT_KNOWN_TAIL become true).

Answer in `report.md`, first line "SAFE" or "UNSAFE: <what>", then at most 30 lines:
1. `QUEEN_NO_RAM` true: in the Trapped branch the real queen now skips `hunt_path` and `ram_path`. Follow the control flow after
   the skip to the end of `act()`: is a legal action (a move or a split) always produced on that turn, or is there a path that
   returns without one (a dragon with no action dies)? Which statement produces it?
2. `SPLIT_KNOWN_TAIL` true: `split_child_size` returns 0 for a dragon that does not know its tail after round 0. List every
   caller of `split_child_size` and say what each does with 0 (no split and the turn continues to a move? or an early return
   without an action?). Can a dragon that never learns its tail be left unable to split for the whole game, and does anything
   depend on such a split to escape a pocket (so that it now dies there)?
3. `QUEEN_DEAD_ALL` false: list every place `dead_queen()` is used and what changes for the REAL queen on a map of 600 cells
   or fewer when it returns false there (which penalties, vetoes and scans switch off). Is any of them the only thing that
   stops her from an immediately fatal step (a one-cell pocket, a cell with no exit), or do `QUEEN_CORRIDOR_GUARD 6`,
   `POCKET_KEEP_OUT` and `QUEEN_EXIT_KEEP` (all still on) cover those?
4. `CENTER_MAX_CELLS` 100000: every use of `center_map` and of the stall release; anything that indexes an array or divides by
   a quantity that assumes at most 1000 cells; any loop whose cost now grows with a 65,536-cell map.
