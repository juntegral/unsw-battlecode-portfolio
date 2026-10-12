# label_report.py: two small extensions (mechanical)

Tool: `data/analysis/ladder/dossier/online/label_report.py` (you wrote it today; brief `data/codex/brief-label-report.md`).
1. Let the MAIN label carry a half too: `label_report.py one1-w1:old --ref agg8-q1 --ref nc62-whq1:old` must work (today it stops with
   "본 라벨은 new half만 집계"). Output name `label-<label>-old.md` for an `:old` main label.
2. A folder of downloaded battles as a column, main or reference: `--dir <name>=<folder>[,<folder>...]` defines a pseudo-label
   `<name>` from folders written by `node tools/online.js download` (each holds `index.json`, `game-<id>.json`, `M<id>.replay`;
   look at `data/online/live-one1/b1460075/`). Our side and the opponent come from the game json; a pseudo-label may hold several
   opponents. Usage: `label_report.py --dir ranked=data/online/live-one1/b1460075 ranked --ref one1-w1:old`. For a pseudo-label
   the "same opponent only" filter on reference columns is switched off, and the header line of each column lists its opponents
   with games and wins each. A glob is fine too: `--dir ranked=data/online/live-one1/b*`.
3. In section 2 (per game) add, for our queen's death, the length and side of the dragon that rammed her and its distance in
   steps from her head one turn earlier, when the cause is "rammed".
Keep every existing output unchanged for existing calls (rerun `label_report.py agg8-q1 --ref nc62-whq1:old --ref agg7-m2` and
diff against the current `label-agg8-q1.md`: only the new death detail of point 3 may differ). Test: (a) `one1-w1:old --ref agg8-q1
--ref nc62-whq1:old`; (b) `one1-d1:old`; (c) `--dir ranked=data/online/live-one1/b* ranked --ref one1-w1:old`. Append to
`label-report-done.txt`: the three commands, wins per column, anything not countable.
Write only under `data/analysis/ladder/dossier/online/`. No network, no posts, no games, no compiling.
