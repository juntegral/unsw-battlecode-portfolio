# Rank-1 eats 56% of the pearls dropped by dead dragons and we eat 41%. Find where ours go missing

You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
2026-10-09 15:00 KST; the qualifier maps are unseen, so no map names in any rule.

## The gap (measured, scoreboard.md, shared layouts, rounds 101-300)
- Share of pearls dropped by dead dragons that the side eats: rank-1 55.9%, ours 40.6% (15 of 19 layouts).
- A pearl on a neighbouring tile not taken: rank-1 19.3% of such turns, ours 26.9%.
- From diag-attack: in a head-on they start, their side eats 2.5 of the pearls dropped and ours 1.0; in ours we
  eat 2.2 and they 1.4. From diag-feeding: of 100 length our feeders give up, 20 reach our longest dragon.

## Your job
1. For every pearl dropped by a death in rounds 0-300, both teams' games: whose body it was (own side or the
   other), how it died (head-on, wall, own body, another body, no action), how many heads of each side were
   within 2 and within 5 steps at the death, who ate it and after how many rounds, or that nobody did. Give the
   side's share by class. Which classes carry the 15-point gap?
2. For the classes that carry it: what does the nearest dragon of ours do in the rounds after the drop while the
   pearl lies there (steps towards, steps past, turns away, is itself rammed), and what does rank-1's do?
   Use the "neighbouring pearl not taken" turns as a second view: what was beside the dragon each time.
3. Tie ours to the lines: the corpse rules (CORPSE_*), the leader pearl zone and its penalty, the pocket rule, the
   threat terms round a fresh fight, EAT_BONUS and what can outweigh it, feeders' drop cells, the stride and
   sprint code that may step past a pearl.
4. Decide ONE switch or none.

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
`data/analysis/ladder/dossier/diag-drops.md` (110 lines or fewer) and scratch scripts under
`data/analysis/ladder/dossier/work/` (prefix `dr_`). Label every statement measured (script), read from code
(file:line) or estimate. Run heavy scans with `nice -n 10`.

## Output: `diag-drops.md`
1. Three lines: what rank-1 does that we do not, the change in one sentence (or "no card"), how sure and why.
2. The tables. 3. "Why, in the code". 4. "The card": `title:`, `slug:`, `### Claim` (proposal and switch name,
   default off, fits a single build round), `### Evidence`, `### Expected signal` (a mechanism check a replay can
   show, rank-1's rate as the mark), `### What would show it's wrong`. Or "No card". 5. "Against it".
