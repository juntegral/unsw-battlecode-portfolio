# Online we win 1 of 20 on layouts above 1200 cells with main, 4 of 20 and 4 of 10 with the new builds. Why

You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
2026-10-09 15:00 KST; the qualifier maps are unseen, so no map names in any rule. The winner of a game is the side
with the longer queen (the dragon with starting id 0 or 1; a dead queen counts 0), then the longest dragon, then
total length; a side with no dragon left is eliminated.

## Data
- Today's online games against two opponents (Big Bobs Bots, WeHaveQuizzes), 15 maps each per label, replays in
  `data/online/smoke/<label>-new/` (`M*.replay`, `game-*.json`): arm MAIN = current team main (`agg7-m1`,
  `agg7-m2`, later `agg7-m3`; 14 wins of 60), arm B7 = main + seven switches (`agg7-b1`, `agg7-b2`; 23 of 60),
  arm B7Q = B7 + queen keeps 3 (`agg8-q1`, later `agg8-q2`; 14 of 30; this is now our live bot, source
  `data/online/smoke/agg8-bot/main.cpp`). Counts already made: `data/analysis/ladder/dossier/online/agg7.md`,
  `online/agg7-games.json`, tool `online/agg7_report.py` (shows how to read these replays).
- Our 500 older ladder games (`dossier/per-game.jsonl`, `data/online/ladder/`) and the rank-1 team's 597
  (`dossier/target/per-game-top1.jsonl`, `data/online/top1/`, team 306); reader `tools/ladder_replay.py`; scan
  scripts in `dossier/work/`.
- Earlier diagnoses: `dossier/diag-*.md` (read the ones named in your task before you start).
Read first: `diag-attack.md`, `diag-feeding.md`, `diag-wipeout.md`, `leader-len.md`, `diag-islands.md`.

## What we know
On layouts above 1200 cells main won 1 of 20, B7 4 of 20, B7Q 4 of 10. An earlier count says that on such
layouts we are rammed 96.8 times a game and ram 16.5 times. Our longest dragon at round 300 is 5 (median).

## Your job
1. For every online game above 1200 cells (three arms apart, the two opponents apart): the timeline of dragon
   count, total length, longest dragon and queen for both sides at rounds 50, 100, 150, 200, 300, 400, 500, and
   what decided the game. At which round does the opponent'"'"'s deciding quantity pass ours for good?
2. Split the length we lose and they lose by cause and by round band: rammed (by a dragon of what length, from how
   far, paying how much), wall, own body, other body, fed to the leader. Who starts the head-ons, who eats the
   drops. Where on the map (our half, middle, theirs)?
3. What the opponent does on these layouts that we do not: when it starts growing one long dragon, how long that
   dragon is at rounds 200/300/400 and how it is fed, how many dragons it keeps, whether its short dragons hunt in
   our half, how it treats our long dragon.
4. Find the one or two things that account for most of the gap in the deciding quantity, tie them to main.cpp
   lines (leader round and rules, feeding rules, `aggressive` false above 1200 cells, the threat terms for short
   dragons such as SMALL_UNIT_THREAT_REACH and SMALL_SPRINT_THREAT, trade and hunt rules), and decide the card(s).
   For each card count the events in the data it would have changed.

## Hard limits
Read-only on everything existing. No server calls, no posts, no games, no compiling. Write only the report named
below (110 lines or fewer) and scratch scripts under `data/analysis/ladder/dossier/work/` with your prefix. Label
every statement measured (script), read from code (file:line) or estimate. `nice` is refused by the guard: run
scans plainly, at most 2 processes at a time (other analysts share the machine).

## Output format
1. Three lines: the finding, the change in one sentence (or "no card"), how sure. 2. The tables. 3. "Why, in the
code" with replay turns (game id, round, positions). 4. "The card" (`title:`, `slug:`, `### Claim`,
`### Evidence`, `### Expected signal`, `### What would show it's wrong`) with the diff against
agg8-bot/main.cpp; at most two cards, each default-off, generic, one build round. 5. "Against it".
Report: `data/analysis/ladder/dossier/diag-bigmap.md`; scratch prefix `bm_`.
