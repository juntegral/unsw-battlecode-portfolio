# On two-dragon starts our second dragon eats 1.1 pearls by round 40 and theirs 3.8. Find the code term

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
Read first: `diag-wipeout.md` (the finding this task starts from), `diag-opening.md`, `diag-hungry.md`.

## What we know (measured in `diag-wipeout.md`)
On layouts where each side starts with two dragons of total length 4 to 6, our non-queen starter eats 1.08 pearls
by round 40 against the opponent'"'"'s 3.84; with no pearl in view it steps toward the map centre on 75% of turns
(opponents 48%, rank-1 49%); they eat their second pearl at round 15 and we at round 30 and they hold twice our
dragon count for good from round 33. The analyst did not find the code term. The bot has a centre pull
(`CENTER_PULL`, `center_map`, `center_rounds`, `CENTER_MAX_LENGTH`, the stall release `TR_STALL_RELEASE`
and `stall_seek`), a queen split in round 1, and territory terms; read how they apply in the first 40 rounds.

## Your job
1. Rebuild the first 40 rounds of both starters (queen and second dragon) of both sides in every online game on
   such layouts (three arms apart) and in our ladder games and rank-1'"'"'s: per round the position, length, pearls
   in view, the step taken, distance to the nearest pearl and to the map centre, and whether the step went toward
   the nearest known pearl, toward the centre, toward unseen tiles, or elsewhere.
2. Classify our second starter'"'"'s turns with no pearl in view and with a pearl in view but not taken (who is
   nearer, is it the queen'"'"'s) and count what it does; the same for the opponents and for rank-1. Where do their
   starters go to find the first three pearls (toward their own side'"'"'s spawn tiles, along walls, outward)?
3. From the code, compute for those turns which score term is the largest for the step actually taken (rebuild
   the terms from the replay state as `diag-hungry.md` did): centre pull, territory, unseen, hot tiles, stall
   seek. Count how often the centre pull decides the step, and on which layout sizes `center_map` is true.
4. Decide the card: the smallest generic change that makes the second starter eat first (for example the centre
   pull only once the dragon count is above N, or only when no spawn tile is known nearer than the centre, or not
   for a side that holds fewer than N dragons), with the count of turns it changes in the data and what the centre
   pull was bought for (find the card or comment that introduced it, and what would be lost).

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
Report: `data/analysis/ladder/dossier/diag-opening2.md`; scratch prefix `o2_`.
