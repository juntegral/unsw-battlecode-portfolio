# Rank-1 meets the enemy 7 rounds earlier and eats pearls sooner in the first 100 rounds. Find what its opening does

You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
2026-10-09 15:00 KST; the qualifier maps are unseen, so no map names in any rule.

## The gap (measured, scoreboard.md, shared layouts)
- First contact with the enemy: round 12.5 for rank-1, 19.9 for us.
- Rounds 0-100: rank-1 eats 53.4% of the pearls born, we 46.8%; eaten in the birth round 10.8% against 6.0%; wait
  from birth to eating 19.3 rounds against 29.5; a head within 1 step at birth 10.2% against 6.3%.
- Head-on meetings started in rounds 0-100: 4.3 per 1,000 dragon turns against 2.2.
- In our lost games being behind at round 100 goes with 72% losses (losses/summary.md).

## Your job
1. Rounds 0-60, both teams, per starting configuration (dragons at start and their lengths): when the first split
   comes and at what length; how far from the start each dragon is by round 10, 20, 30 (path steps); how many
   steps a turn they make (free steps and paid ones); how the dragons spread (distance between a side's heads);
   the round of the first pearl eaten by each dragon; the tiles seen by round 20 and 40; dragons alive at 20,
   40, 60; and what the queen does (stays, follows, leads).
2. Which of these differ on most layouts, and which differences come first in time (cause before effect)?
3. Tie ours to the lines: the centre rule, the pearl pull that ends at 7 steps, FAR_GAIN, the unseen bonus, the
   split rules in the opening (SPLIT_MIN_LENGTH, child room), sprint use (when do we pay or use free steps with
   nothing in view), queen rules in the opening.
4. Decide ONE switch for the opening or none. It must not undo the stall-release rule that is now in main.

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
`data/analysis/ladder/dossier/diag-opening.md` (110 lines or fewer) and scratch scripts under
`data/analysis/ladder/dossier/work/` (prefix `op_`). Label every statement measured (script), read from code
(file:line) or estimate. Run heavy scans with `nice -n 10`.

## Output: `diag-opening.md`
1. Three lines: what rank-1 does that we do not, the change in one sentence (or "no card"), how sure and why.
2. The tables. 3. "Why, in the code". 4. "The card": `title:`, `slug:`, `### Claim` (proposal and switch name,
   default off, fits a single build round), `### Evidence`, `### Expected signal` (a mechanism check a replay can
   show, rank-1's rate as the mark), `### What would show it's wrong`. Or "No card". 5. "Against it".
