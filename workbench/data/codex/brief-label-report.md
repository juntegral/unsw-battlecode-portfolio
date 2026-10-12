# A per-label online report: the new bot's own games, with references taken only from games already on disk

Context: from now on an online test plays the NEW bot only (no live-bot half). We judge a change from its own games: did each
mechanism fire, and did the bot grow. Existing tool for the earlier A/B labels: `data/analysis/ladder/dossier/online/agg7_report.py`
(read it first: its replay reader, `count_job`, `extra.counts`, the queen block and the switch-event rows are to be REUSED by import,
not copied). Queen measures: `data/analysis/ladder/dossier/work/tq2_scan.py`, `tq2_near.py`, `tq2_chase.py`, `tq2_def.py`, `tq2_depth.py`.

Write `data/analysis/ladder/dossier/online/label_report.py`:
`nice -n 10 python3 -B data/analysis/ladder/dossier/online/label_report.py <label> [--ref <label>[:old|:new] ...]`
-> `data/analysis/ladder/dossier/online/label-<label>.md` (+ `label-<label>.json` with the per-game rows).
Layout on disk: `data/online/smoke/<label>.json` (state, opponents, maps, schedule), replays of the new bot in `<label>-new/`,
of the live bot in `<label>-old/` when that half was played, wins in `<label>-report.log`. A label may be half-written: report what
is there and list what is missing. A reference `X:old` means the live-bot half of label X, `X:new` (default) its new-bot half.
Reference columns only use games against the same opponent, and say how many games and which hours they are from.

Sections of the report (plain tables, the label's column first, then one column per reference):
1. Three lines at the top: games, wins, and the two or three numbers that moved most against the references (no judgement words).
2. Per game: map, cells, result, what decided it (queen length / longest / total / elimination), our and their final total length,
   longest, queen length, the round and cause of our queen's death (rammed / boxed in / ran into a head / alive).
3. Growth: own and their dragons alive and total length at r50, r100, r150, r200, r300, r400 and the end; pearls eaten by r100 and
   r300; net length per 1,000 turns (the agg7 definition).
4. Queen: alive at r100 / r150 / r300 / end; death causes; share of her turns at length 2 / 3 / 4+; enemy head within 3 steps per
   100 of her turns by band (r0-50, r51-100, r101-300); close chases (count, turns each, share starting with no mate within 5 tiles,
   chases in which a mate rams a pursuer, chases ending in her rammed); own heads within 5 tiles of her by band; pearls she eats.
5. Mechanisms fired, one row each, counted for every column so the references give the base rate (reuse agg7's rows where they exist):
   ZONE_NEARER, TRADE_EVEN, HUNT_SMALL_RATIO, QS_KEEP_LEN, TRADE_SHORT_BY, LUNGE_PEARL, FEEDER_EAT (agg7 definitions), and new:
   - SPLIT_ROUND0: starters of length 4+ that split in round 0 / such starters.
   - QUEEN_DEFEND_STEPS: head-ons started by our non-queen dragon of length 4 or less on an enemy head (not their queen) that was
     within 3 steps of our queen's head at the start of that turn; next to it the same for rammers of 5+ and for targets 4-5 tiles off.
   - QUEEN_HERD: her turns (r51-300) with no own head within 5 tiles (%), and on turns with fewer than two own heads in her 7 by 7
     the share of her steps that end nearer to the nearest own head.
   - QUEEN_FALLBACK: her turns that start with more enemy than own heads in her 7 by 7 (her own head counts as ours), and what she
     did on them (away from the nearest enemy head / toward it / level; toward the nearest own head).
   One line under the table defines each row.
6. Checks: wins equal the per-opponent lines of `<label>-report.log`; every game counted once; anything not countable and why.

Test it on existing data, no network: `label_report.py agg8-q1 --ref nc62-whq1:old --ref agg7-m2` (agg8-q1 = v62 against Big Bobs
Bots and WeHaveQuizzes, 30 games; nc62-whq1:old = v62 against WeHaveQuizzes, 15 games; agg7-m2 = old main, 30 games). The wins in
its output must match `data/analysis/ladder/dossier/online/agg7.md` for agg8-q1 (14 of 30) and agg7-m2. Keep a cache so a rerun is
fast. Write only under `data/analysis/ladder/dossier/online/`. No network, no posts, no games, no compiling. Finish by writing
`data/analysis/ladder/dossier/online/label-report-done.txt` (usage line, the test command's result in 5 lines, known limits).
