# Online test of main against main + seven switches: one re-runnable report

Today we play two bots online in the same hours, each 15 maps against each of two opponents per run:
- arm MAIN (current team main): smoke labels `agg7-m1`, `agg7-m2`, `agg7-m3`, and last night's `sr51-bob1` (same code, other hours: report it apart, never pooled into the paired tables).
- arm B7 (main + seven default-off switches turned on): labels `agg7-b1`, `agg7-b2`, `agg7-b3`.
Only `agg7-m1` and `sr51-bob1` exist now; the others arrive over the next hours. The tool must run on whatever
labels exist and say which are missing.
Files per label: `data/online/smoke/<label>.json` (state: battle ids, opponents), `data/online/smoke/<label>-new/`
(`M<match>.replay`, `game-<id>.json`), `data/online/smoke/<label>-report.log`. We are team 1119. Replay readers:
`tools/ladder_replay.py` (ladder format), `data/analysis/ladder/dossier/local/replay_format.py` (local format).
The local scoreboard `data/analysis/ladder/dossier/local/scoreboard.py` with `count_local.py`, `spawn.py`,
`rams.py`, `leader.py` computes behaviour rates for local runs and prints them beside the rank-1 team's and our
ladder marks (`dossier/target/scoreboard.md`, built by `dossier/work/tg_run.py`); reuse their definitions.
The seven switches are the constants set in `data/online/smoke/agg7-bot/main.cpp` against
`data/online/smoke/sr51-bot/main.cpp` (diff them): SPAWN_CLEAR, ZONE_NEARER, POCKET_LOOP, HARVEST_PORTAL,
TRADE_EVEN, HUNT_SMALL_RATIO 2, LEADER_FULL_UNITS 56.

## Build `data/analysis/ladder/dossier/online/agg7_report.py` (run: `nice -n 10 python3 -B <it>`), writing
`data/analysis/ladder/dossier/online/agg7.md` (120 lines or fewer), with these parts
1. Results. Per arm and opponent: games, wins, mean our score and theirs (final lengths), how the game was
   decided (longer queen, longest dragon, total length, elimination), our queen alive at the end and her length.
   Paired table on (opponent, map): B7 result against MAIN result of the same round (m1 with b1 and so on), with
   counts of both win, both lose, only B7, only MAIN, and the sign test. By layout size (cells <= 700, 701-1200,
   above 1200).
2. Behaviour rates, MAIN against B7, beside the rank-1 and ladder marks, for the rates the switches aim at:
   pearls eaten per 1,000 dragon turns (all, and by dragons of 2-3), natural pearls eaten per pearl born, spawn
   tile stepped on at countdown 1 (%), pearl born when one of ours stood 2 away (%), birth-to-eaten wait, splits
   per 1,000 turns, dragons alive at rounds 100 and 300, longest dragon at 300 and at the end, deaths per 1,000
   turns by cause, head-ons started per 1,000 turns, net length per 1,000 turns (eaten minus length lost in
   deaths). Mark each rate where B7 moved toward the rank-1 mark and where away.
3. Did each switch fire online: per switch a count that only the switch can produce, MAIN against B7
   (SPAWN_CLEAR: part 2's two spawn rates; ZONE_NEARER: after the leader round, a pearl within 9 tiles of our
   longest dragon eaten by a shorter dragon of ours that was nearer to it; TRADE_EVEN: even-length head-ons we
   started while holding fewer dragons than the cap; HUNT_SMALL_RATIO: a dragon of 4 or less ramming a head at
   least twice its length; POCKET_LOOP and HARVEST_PORTAL: pearls eaten in rooms behind a portal by round 100;
   LEADER_FULL_UNITS: on layouts above 1200 cells, the first round our longest dragon passes 10 while we hold
   fewer than 56 dragons). Say plainly when a count is too small to read.
4. Loss anatomy of arm MAIN and of arm B7 apart: for each loss, what decided it, the round our queen died and the
   cause (head-on hit by whom: length and how many steps away at the start of its turn, wall, own body, other
   body), her length then, own heads within 5 tiles of her; the round the opponent's deciding quantity (queen
   length, else longest dragon) passed ours for good; whether our longest dragon was rammed after round 300 and
   its length then. Then a table of loss classes with counts (queen died before round 100 / 100-300 / later;
   leader rammed late; out-eaten with both queens dead; eliminated; other), per opponent.
5. Ten lines or fewer, plain: what the online games show about the bundle (counts only, no advice), and the three
   largest loss classes of current main.
Check the tool: every game of every present label is counted once, wins equal those in `<label>-report.log`.

## Limits
Read-only on everything existing. Write only under `data/analysis/ladder/dossier/online/`. No network, no posts,
no games. At most 4 processes. Last step: write `data/analysis/ladder/dossier/online/agg7-done.txt` with the run
command and the labels found.
