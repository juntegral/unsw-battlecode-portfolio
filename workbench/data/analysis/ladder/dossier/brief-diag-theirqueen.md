# Their queens outlive ours. Read how the two opponents'"'"' queens live, and what of it we can copy

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
Read first: `diag-queenhit.md`, `diag-queenkill.md`, `queen-path.md`.

## What we know
In games decided on queen length we are 3 won and 9 lost even with the new build (0 and 24 for main). Our queen
is alive at the end in 18 to 27% of games. Their queens are alive far more often in the same games.

## Your job
1. For each opponent'"'"'s queen and for ours, in the same games (all three arms, reported apart): alive at rounds
   50, 100, 150, 300, end; her length over time; the share of her turns at each length; her splits (round, length
   before and after); distance from her start tile over time and the area she covers (distinct tiles per 50
   rounds); how many own heads are within 3 and 5 tiles; how many enemy heads come within 3 steps of her per 100
   turns and what she does on those turns (steps away, sprints, splits, stays); pearls she eats; whether she sits
   in a place with one entrance, behind kelp, behind her own dragons; whether she ever attacks.
2. Say in plain words what each opponent'"'"'s queen does that ours does not (they may differ from each other), with
   the counts, and how often our dragons get near her at all (the chance side of `diag-queenkill.md`).
3. Compare with rank-1'"'"'s queen on the ladder for the same measures where the earlier files have them.
4. Which of their habits can our bot take as ONE or TWO switches? Tie each to main.cpp lines: what our queen'"'"'s
   scoring does today in that situation and the smallest change. Count on our own games how many of her deaths
   the habit would have touched and what it costs (pearls she would not eat, turns it fires).

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
Report: `data/analysis/ladder/dossier/diag-theirqueen.md`; scratch prefix `tq_`.
