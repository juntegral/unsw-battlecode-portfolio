# Fix a crash in the online report

`nice -n 10 python3 -B data/analysis/ladder/dossier/online/agg7_report.py` now stops with
`KeyError: 'eaten'` at `count_job` (line 255: `assert extra['counts']['eaten'] == ours['game_counts']['pearls_eaten']`)
since label `agg7-m3` arrived (`data/online/smoke/agg7-m3.json`, `agg7-m3-new/`). Probably a game in which our side
ate no pearl (or ended in the first rounds). Find the game, fix the tool so that a missing counter is 0 and the
check still holds, rerun, and confirm `agg7.md` lists agg7-m3 (and agg8-q2 when it is there) with every game
counted once and wins equal to the `<label>-report.log` lines. Note: for labels started after 14:56 KST the live
bot is another build, so `<label>-report.log` prints "new bot 0 games" on its second line and the per-opponent
lines carry the wins; read the wins from those lines for such labels.
Write only under `data/analysis/ladder/dossier/online/`. No network, no posts, no games. Rewrite
`data/analysis/ladder/dossier/online/agg7-done.txt` as the last step.
