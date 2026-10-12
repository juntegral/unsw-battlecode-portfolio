# We are wiped out in 11 of 30 online games. Anatomy of an elimination

You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
2026-10-09 15:00 KST; the qualifier maps are unseen, so no map names in any rule. The winner of a game is the side
with the longer queen (the dragon with starting id 0 or 1; a dead queen counts 0), then the longest dragon, then
total length; a side with no dragon left is eliminated.

## Data
- Fresh online games of the current team main: labels `agg7-m1` (30 games this morning, 7 wins), `sr51-bob1` (15,
  last night) and, as they arrive today, `agg7-m2`, `agg7-m3`: `data/online/smoke/<label>-new/M*.replay` with
  `game-*.json`. Labels `agg7-b*` are another build: use them only as a second sample, reported apart.
  Per-game counts already made: `data/analysis/ladder/dossier/online/agg7.md`, `online/agg7-games.json`, tool
  `online/agg7_report.py` (shows how to read these replays).
- Our 500 main ladder games (`data/analysis/ladder/dossier/per-game.jsonl`, replays `data/online/ladder/`; older
  builds of our bot) and the rank-1 team's 597 games (`dossier/target/per-game-top1.jsonl`, replays
  `data/online/top1/`, team id 306). Shared reader `tools/ladder_replay.py`; scan scripts in `dossier/work/`.
- The bot: `data/online/smoke/sr51-bot/main.cpp` (= team main a358ec8). Earlier diagnoses in `dossier/diag-*.md`
  (read `diag-attack.md`, `diag-feeding.md`, `diag-sacrifice.md` and `queen-path.md` before you start).

## What the online games show
Of this morning'"'"'s 30 games of current main, 11 ended with every dragon of ours dead (5 of 15 against one
opponent, 6 of 15 against the other). At round 300 we hold 26.9 dragons a game (rank-1 holds 35.0 on the ladder)
and our longest is 7.2 (9.7).

## Your job
1. Every game we lost by elimination (online first; then all ladder games of ours, and rank-1'"'"'s for the rate):
   the timeline of our dragon count, total length and the opponent'"'"'s, the round the count peaks, the round it
   falls below half of the peak, and the round of the last death. Is it a slow starve, one battle, or a steady
   bleed? What share happen on layouts of 700 cells or fewer, 701-1200, above 1200?
2. In the 60 rounds before the count halves: our deaths by cause (rammed by a head: the rammer'"'"'s length, steps,
   length paid; ran into a wall, own body, another body; no move), where they happen (near our start, mid map,
   near theirs), the length of the dragon that died, own heads within 5 tiles; and the same for the opponent'"'"'s
   deaths in those rounds. Who starts the head-ons, and who eats the pearls the dead leave (within 5 rounds)?
3. Compare with games on the same layouts that we did not lose by elimination, and with what rank-1 does when
   the same opponents (or any) press it: does it trade, run, split, gather?
4. Tie what our dragons do in those rounds to main.cpp lines (the trade and hunt rules, the head-penalty terms,
   the split rules, `aggressive`, the cramped terms). Decide: ONE default-off switch (generic, one build round)
   for the largest cause, with the mechanism check a replay can show and the share of the counted deaths it
   addresses; or "no card" with the three best leads and their sizes.

## Hard limits
Read-only on everything existing. No server calls, no posts, no games, no compiling. Write only the report named
below (110 lines or fewer) and scratch scripts under `data/analysis/ladder/dossier/work/` with your prefix. Label
every statement measured (script), read from code (file:line) or estimate. Heavy scans with `nice -n 10`, at
most 3 processes at a time.

## Output: `data/analysis/ladder/dossier/diag-wipeout.md` (scratch prefix `wo_`)
1. Three lines: how we get wiped out, the change in one sentence (or "no card"), how sure. 2. The timeline and
cause tables (online, ladder, rank-1). 3. "Why, in the code" with replay turns (game id, round, positions).
4. "The card" (`title:`, `slug:`, `### Claim`, `### Evidence`, `### Expected signal`,
`### What would show it'"'"'s wrong`) with the diff against sr51-bot/main.cpp. 5. "Against it".
