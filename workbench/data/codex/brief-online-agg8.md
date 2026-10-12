# Add a third arm to the online report

`data/analysis/ladder/dossier/online/agg7_report.py` (yours, written this morning from
`data/codex/brief-online-agg7.md`) compares arm MAIN (labels `agg7-m1..m3`) with arm B7 (`agg7-b1..b3`).
The plan changed: there is no `agg7-b3`; instead a third arm B7Q = B7 plus one more switch (`QS_KEEP_LEN 3`: our
queen makes no routine split below length 5 and uses the paid escape before the split; bot
`data/online/smoke/agg8-bot/main.cpp`) plays as labels `agg8-q1` (same hours as `agg7-m2`... it runs right after
it) and `agg8-q2` (right after `agg7-m3`). Files are laid out like the other labels
(`data/online/smoke/<label>.json`, `<label>-new/`, `<label>-report.log`). Only some labels exist yet.

Change the tool so that `agg7.md` (130 lines or fewer) also has:
1. Arm B7Q in the results table and the size table; paired tables B7Q against MAIN (q1 with m2, q2 with m3) and,
   as a second table, B7Q against B7 on (opponent, map) pooled over all rounds (say that hours differ).
2. A queen block for the three arms: queen alive at rounds 100, 150, 300 and at the end; her length at those
   rounds (mean over games where she lives) and the share of her turns at length 2, 3, 4+ in rounds 0-300; her
   routine splits per game and the length she had after each; her deaths by cause and her length at death; games
   decided on queen length, won and lost; children she split off per game.
3. Behaviour table and switch table with a B7Q column. Loss anatomy for B7Q too.
4. Section 5: one more line for B7Q (counts only).
Keep everything else as it is, keep the checks (every game once, wins equal the report logs). Write only under
`data/analysis/ladder/dossier/online/`. No network, no posts, no games. `nice -n 10`, at most 3 processes.
Last step: rewrite `data/analysis/ladder/dossier/online/agg7-done.txt` with the labels found.
