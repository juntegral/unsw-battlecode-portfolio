# Rank-1 splits a third more often than we do and turns its dragons over faster. Find the rule that holds ours back

You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
2026-10-09 15:00 KST; the qualifier maps are unseen, so no map names in any rule.

## The gap (measured, scoreboard.md, shared layouts)
- Splits per 1,000 dragon turns: rank-1 30.6, ours 22.7 (17 of 19 layouts); in rounds 101-300 28.9 against 21.1.
- All deaths per 1,000 dragon turns: rank-1 27.8, ours 20.1 (18 of 19). Splits per pearl eaten are about the same
  (0.36 against 0.38): rank-1 eats more and splits it all; ours keeps length.
- Related, from diag-sacrifice: on a full board rank-1-like teams keep dragons 2 to 4 long and go on splitting;
  ours stop at 60 dragons (SPLIT_SOFT_LIMIT) and grow where they are. From diag-islands: after round 150 or 300 a
  dragon of ours longer than 4 never splits again.

## Your job
1. For both teams, over all games: the length distribution of living dragons by round band (0-100, 101-200,
   201-300, 301-400), the share of dragon turns spent at length 2, 3, 4, 5-7, 8+; the length at which a dragon
   splits and the child size; how many rounds a dragon lives; dragons alive against the layout's limit by round.
2. The moments ours could split and does not while rank-1 in the same state does: by dragon length, round band,
   dragons alive, room behind the tail, enemy near. Rank the classes by how many splits a game they explain.
3. Tie the largest classes to the lines (split_child_size, SPLIT_MIN_LENGTH, SPLIT_SOFT_LIMIT, the round rule,
   child_has_exit, CHILD_MIN_ROOM, harvesting, the queen's split rules, the unit limit read from the game).
4. What does the extra splitting buy rank-1 in the terms the game is decided on (pearls eaten per dragon turn,
   board held, deaths), and what does keeping length buy us (the longest-dragon rule)? Decide ONE switch or none.

## Already counted (read first, do not recount what is there)
`dossier/target/scoreboard.md` and `scoreboard.json` (ours = 500 main ladder games, rank-1 = 597 of its own games,
19 shared layouts, each weighted equally), `target/per-game-top1.jsonl` (rank-1 rows; replays `data/online/top1/`,
team id 306), `dossier/per-game.jsonl` (ours; replays `data/online/ladder/`), `dossier/fingerprint.md`, and
tonight's diagnoses in `dossier/`: diag-islands (leader rules from round 151), diag-australia (even trades),
diag-stripes (pocket rule), diag-attack, diag-feeding, diag-sacrifice (boxed-in deaths are the same on both
sides), diag-spawn (we stand on tiles about to spawn), diag-walk, sweep. Shared replay reader:
`tools/ladder_replay.py`; earlier scan scripts in `dossier/work/` (sp_scan.py, at_scan.py, wk_scan.py) show how to
pass over all 1,097 games. Bot: `~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp` (current
main; it now has QUEEN_NO_FEED and TR_STALL_RELEASE on, which the ladder games did not).

## Hard limits
Read-only on everything existing. No server calls, no posts, no edits to bot or loop code. Write only
`data/analysis/ladder/dossier/diag-split.md` (110 lines or fewer) and scratch scripts under
`data/analysis/ladder/dossier/work/` (prefix `sl_`). Label every statement measured (script), read from code
(file:line) or estimate. Run heavy scans with `nice -n 10`.

## Output: `diag-split.md`
1. Three lines: what rank-1 does that we do not, the change in one sentence (or "no card"), how sure and why.
2. The tables. 3. "Why, in the code". 4. "The card": `title:`, `slug:`, `### Claim` (proposal and switch name,
   default off, fits a single build round), `### Evidence`, `### Expected signal` (a mechanism check a replay can
   show, rank-1's rate as the mark), `### What would show it's wrong`. Or "No card". 5. "Against it".
