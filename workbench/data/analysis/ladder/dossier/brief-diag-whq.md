# One opponent beats us 6 times in 7. Read its play backwards, one behaviour at a time

You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
2026-10-09 15:00 KST; the qualifier maps are unseen, so no map names in any rule. The winner of a game is the side
with the longer queen (the dragon with starting id 0 or 1; a dead queen counts 0), then the longest dragon, then
total length; a side with no dragon left is eliminated.

## Data
- Today's online games against two opponents (Big Bobs Bots, WeHaveQuizzes), 15 maps each per label, replays in
  `data/online/smoke/<label>-new/` (`M*.replay`, `game-*.json`): arm MAIN = current team main (`agg7-m1`,
  `agg7-m2`, `agg7-m3`; 21 wins of 90), arm B7 = main + seven switches (`agg7-b1`, `agg7-b2`; 23 of 60),
  arm B7Q = B7 + queen keeps 3 (`agg8-q1`, later `agg8-q2`; 14 of 30; this is our live bot, source
  `data/online/smoke/agg8-bot/main.cpp`). Counts already made: `data/analysis/ladder/dossier/online/agg7.md`,
  `online/agg7-games.json`, tool `online/agg7_report.py` (shows how to read these replays).
- Our 500 older ladder games (`dossier/per-game.jsonl`, `data/online/ladder/`) and the rank-1 team's 597
  (`dossier/target/per-game-top1.jsonl`, `data/online/top1/`, team 306); reader `tools/ladder_replay.py`; scan
  scripts in `dossier/work/`.
- Earlier diagnoses: `dossier/diag-*.md` (read the ones named in your task before you start).
Read first: `fingerprint.md`, `target/scoreboard.md`, `diag-attack.md`, `diag-wipeout.md`.

## What we know
Against WeHaveQuizzes main won 5 of 45, B7 7 of 30, B7Q 6 of 15; against Big Bobs Bots 16 of 45, 16 of 30 and 8
of 15. In main'"'"'s games WeHaveQuizzes ends with 165 total length against our 65.

## Your job
1. A behaviour fingerprint of each opponent in these games, side by side with ours in the same games (three arms
   apart) and with rank-1'"'"'s ladder marks where they exist: pearls eaten per 1,000 dragon turns by length class,
   splits per 1,000 turns and the length they split at, dragons alive and longest dragon at rounds 50, 100, 200,
   300, 400, 500, deaths by cause, head-ons started and taken (by attacker length and target length), the steps
   and paid length of their rams, how they treat our queen and our longest dragon, where their dragons spend
   their turns (own half, middle, our half), their first 40 rounds, their queen (length, place, company).
2. For WeHaveQuizzes: the three behaviours that produce most of its margin over us (in the deciding quantity of
   the games it wins), each with the counts and the rounds it happens in; and for each, whether Big Bobs Bots
   does the same, and whether rank-1 does.
3. For each of the three: what our bot does in the same situation today and which main.cpp lines decide it
   (rebuild the decision from the replay state where you can). Is it something we can do too, or something we
   can deny them (for example by not standing where their rams reach)?
4. Decide the card(s): the largest one first, with the count of events in the data it would change.

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
Report: `data/analysis/ladder/dossier/diag-whq.md`; scratch prefix `wq_`.
