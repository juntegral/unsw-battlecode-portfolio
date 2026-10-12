# Independent recount of the key numbers behind two diagnoses

Two analyst reports claim numbers that two bot cards will rest on. Your job is to recount them independently and say
match or mismatch. You are a checker: do not explain, do not propose, do not soften a mismatch.

Reports (read both fully first): `data/analysis/ladder/dossier/diag-islands.md`, `data/analysis/ladder/dossier/diag-australia.md`.
Data: `data/analysis/ladder/dossier/per-game.jsonl` (500 main ladder games; schema is whatever
`data/analysis/ladder/dossier/count_dossier.py` writes) and the replays it was built from under `data/online/`.
The analysts' scripts are in `data/analysis/ladder/dossier/work/` (isl_*.py, au_*.py).

## Rules
- Write your own counting code in `data/analysis/ladder/dossier/verify2/` (create it). Do not import or copy the
  analysts' scripts for parts A to C. You may read them to learn a definition, and you must say when a definition
  in the script differs from the words in the report.
- "Ours" is team 1119 in each game; check the side mapping yourself per game, do not assume side 0.
- Rounds are raw replay rounds (0-based). "r101-150" means rounds 101 to 150 inclusive.
- Read-only on everything outside `verify2/`. No network, no posts.

## A. Islands (the 24 games of layout "Islands #1")
Per game means, ours and theirs, for rounds 101-150 and 151-200:
1. splits (report: ours 42.3 then 16.3; theirs 59.1 then 54.7)
2. pearls eaten, all tiles (report: ours 58.5+55.0=113.5 then 23.4+32.1=55.5; theirs 191.2 then 199.5)
3. dragons alive, mean over the rounds (report: ours 40.5 then 35.6; theirs 51.7 then 55.3)
4. deaths of ours in r101-150 (report 41.2)

## B. All six layouts above 1200 cells (width x height > 1200)
For each game: our mean dragon count over rounds 101-150 ("full" = 56 or more). Report says: full 40 won of 77,
not full 21 won of 84. Give your two fractions, and the same per layout (report table: Islands 1 of 7 and 0 of 17,
Australia 3 of 4 and 6 of 31, Around UNSW 15 of 30 and 0 of 2, Slithery Fight 17 of 32 and 1 of 5,
Schooltime 2 4 of 4 and 6 of 9, Schooltime 1 none and 8 of 20). State how you treated games that ended before
round 150 and draws.

## C. Australia (the 35 games of layout "Australia #1"), rounds 101-300
1. Cross-team head-on meetings per game, split by which side was the mover (report: they start 44.5, we start 6.0).
2. Dragons alive at r100, r150, r200, r300, ours and theirs (report: 36.7, 46.4, 42.1, 35.1 against 35.7, 51.7, 57.7, 59.0).
3. Total length at r100 and r300 (report: 90.9, 119.1 against 90.2, 261.0).
4. Record by our dragon count at r150 over all six big layouts: 59 or more 45 of 85; 50 to 58 6 of 19; under 50 10 of 56.

## D. The take rate (rerun, then read)
Rerun `work/au_scan2.py` (and whatever it needs) as it is and confirm it prints the report's
"0.111 (75 of 673)" under 59 dragons and "0.805 (62 of 77)" at 59 or more for ours on Australia, and theirs
"0.696 (473 of 680)". Then read the script and list anything that could make ours and theirs not comparable
(side mapping, who counts as having "the edge", off-by-one in rounds or reach, the queen excluded on one side only,
the unit count taken from the wrong side).

## Output: `data/analysis/ladder/dossier/verify2/result.md` (60 lines or fewer)
One table: item, report value, your value, match / mismatch (match = within 3 percent or 1 game), note.
Then "Definition differences" and "Could not check". Write `verify2/done.txt` with one line as the very last step.
