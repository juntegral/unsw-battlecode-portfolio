# Counting job: regress (silent regressions between live versions)

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Data, Rules: mark [M] measured, never state a number you did not compute) and
`data/codex/astra/CARDS.md`. Write only under `data/codex/astra/regress/` (scripts, tables, `report.md`). Do not play games,
upload, or edit sources. Keep scripts light (`nice -n 10`, one process).

Why: one switch added in version one12 (PORTAL_SCOUT_MIN_LEN) kept our whole side out of portals and halved our pearls on six
maps; it stayed live for three hours because nobody put the versions side by side per map. It was removed in one14. This job is
that side-by-side table for everything else, so no second regression of that kind is still live.

Data: our unranked 15-game sets, one folder per set, `data/online/smoke/<label>-old/` (replays `M<id>.replay` and `game-<id>.json`),
labels `one5-*`, `one6-*`, `one7-*`, `one8-*`, `one9-*`, `one10-*`, `one11-*`, `one12-*`, `one13-*`, `one14-*` (one14 sets arrive
while you work: include what exists when you start the final table and say how many games). The version of a game is the bot id
in the replay (`data/online/smoke/versions.tsv` maps ids to names); trust that over the label. Readers: `tools/ladder_replay.py`,
`data/analysis/ladder/dossier/work/o1_scan.py`. We are team 1119.

Deliver `report.md`:
1. One table per metric, rows = map (15 ladder maps), columns = version (one5 ... one14), cell = mean over that version's games
   on that map with the game count in brackets. Metrics, all for OUR side: pearls eaten by r50 / r100 / r200; dragons alive at
   r100 and r200; total length at r100 and r200; queen length at r100 and r200; round our queen died (share of games she died,
   median round); portal crossings in r0-99; splits in r0-99; our deaths in r0-199 split by cause (wall, own body, mate, enemy
   body, rammed head-on); share of our turn starts in r0-199 that are farther than 12 steps from our start tile.
2. A list of every map and metric where two consecutive versions differ by more than 35 percent AND the later versions stay at
   the new level (so it is a step, not one noisy game). For each: the versions on both sides of the step and the switches that
   changed there (from CARDS.md and the upload notes `data/guide/px-live-one*.txt`).
3. The three steps you would look at first for the live bot (one14 keeps everything of one12 and one13 except the portal rule),
   and for each what a replay check should look for. If nothing besides the portal rule steps, say so plainly.
Your final message = the first 25 lines of the report.
