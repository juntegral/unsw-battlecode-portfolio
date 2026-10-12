# When both queens are dead the longest dragon decides. Who wins that race against us, and how

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
Read first: `diag-feeding.md`, `leader-len.md`, `diag-islands.md`, `diag-bigmap.md` if it exists by then.

## What we know
In today'"'"'s games 30 to 45% are decided on the longest dragon. Our longest at round 300 is 5 (median) and 7 to 10
(mean); the leader rules start at round 151 above 1200 cells and 300 below; "leader rammed late" was the largest
loss class in the first loss anatomy; team card 54 protects only dragons of 31 or longer.

## Your job
1. Every online game decided on the longest dragon (three arms apart) and those decided by elimination after
   both queens died: the length of each side'"'"'s longest dragon at rounds 100, 150, 200, 250, 300, 350, 400, 450,
   500, the round the opponent'"'"'s passes ours for good, and what happened at that round (our longest rammed: by
   whom, from how far, was it in view; their longest fed; ours stopped growing: why).
2. How each side grows its longest: pearls it eats itself, pearls from team mates that die beside it (feeding),
   merges if the rules have them, and when that starts. Per 100 rounds: length gained by the longest and length
   the team spends on it. Compare our leader rules (`grow_round`, `is_leader`, `feeding_phase`,
   `FEED_CAP_UNITS`, `FEED_CAP_ROUND`, `LEADER_FULL_UNITS`, `ENDGAME_ROUND`, read them) with what the
   opponents and rank-1 visibly do.
3. Our longest dragon'"'"'s deaths: its length, the round, the cause, the rammer'"'"'s length and steps, own heads within
   5 tiles, and whether a rule like card 54'"'"'s (keep off tiles an enemy head can reach) at a lower length would
   have had a clean tile to offer on its last two turns (count for thresholds 8, 12, 16, 20, 31).
4. Decide the card(s): what would move the final longest-dragon comparison most (start the leader earlier or
   later, feed differently, protect it from a lower length, keep two long dragons), with the count of games in
   the data each would have turned on the final board, and the main.cpp lines.

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
Report: `data/analysis/ladder/dossier/diag-longest.md`; scratch prefix `lg_`.
