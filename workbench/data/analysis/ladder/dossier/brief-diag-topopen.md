# The first 100 rounds of the top teams against ours: where the gap opens

You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
2026-10-09 15:00 KST; the qualifier maps are unseen, so no map names in any rule. The winner of a game is the side
with the longer queen (the dragon with starting id 0 or 1; a dead queen counts 0), then the longest dragon, then
total length; a side with no dragon left is eliminated. We are far below the top teams (we are about 1950; they
are 2440 to 2590) and want to learn what they do, one behaviour at a time, and copy what a code line of ours can do.

## Data
- Top teams, fresh (today's bots): `data/online/top3/<battle>/` (`M*.replay`, `game-*.json`), index
  `data/online/top3/index.jsonl` (team = the studied side: 454 aAah rank 1, 157 larp stock zi balls rank 7,
  306 Cutlery rank 4, 70 chad gdp rank 2). A collector adds battles every minute or two: list the folder again
  before your last pass and use everything that is there.
- Top teams, older (to 5 Oct): `data/online/top1/<battle>/`, index `data/top1/index.jsonl` (keys team, opp,
  wins, losses, at): 597 games of Cutlery (306), 611 of SSS (91), 761 of "forgot to mention" (264), 109 of horse
  (842), a few of aAah. The Cutlery games were already measured as "rank-1": `dossier/target/per-game-top1.jsonl`,
  `dossier/target/scoreboard.md`, `dossier/fingerprint.md`.
- Ours: today's online games of the live build B7Q (`data/online/smoke/agg8-q1-new/`, source
  `data/online/smoke/agg8-bot/main.cpp`) and of main (`agg7-m1-new/`, `agg7-m2-new/`, `agg7-m3-new/`), counted in
  `dossier/online/agg7.md` (tool `online/agg7_report.py`, which shows how to read online replays). When present,
  our live build against the top teams themselves: folders `data/online/smoke/top-l1-*` (vs 157 and 306) and
  `top-l2-*` (vs 454 and 87): the most direct evidence, use it if it has arrived.
- Reader `tools/ladder_replay.py`; scan scripts in `dossier/work/`; earlier diagnoses `dossier/diag-*.md`.

Read first: `diag-opening.md`, `diag-opening2.md`, `diag-economy.md`, `diag-spawn.md`, `target/scoreboard.md`.

## What we know
Our live build eats 45% of the natural pearls born and holds 35 dragons at round 300, about what Cutlery held on
the ladder a few days ago. We do not know the same numbers for today's aAah and larp stock zi balls, nor the curve
round by round.

## Your job
1. Growth curves, each top team apart and ours beside them (same layout sizes: 700 cells or fewer, 701-1200,
   above 1200; say how many games each cell rests on): dragons alive, total length, longest dragon, pearls eaten,
   splits, deaths (by cause) at rounds 10, 20, 30, 40, 60, 80, 100, 150, 200, 300. At which round does each top
   team first hold 1.5 times our count or length on the same size class?
2. The mechanics behind their curve in the first 60 rounds: the length they split at and what the child does, how
   soon a new dragon eats its first pearl, how far apart their dragons spread (mean distance to the nearest team
   mate), what share of the layout they have seen by round 30 and 60, whether they send dragons through portals
   early, how they use sprints in the opening (free only, or paying length to reach pearls), how many dragons they
   lose and to what.
3. The two largest differences from ours, with the counts, and for each what our bot does at that moment and the
   code lines (split_child_size and the split constants, sprint use for pearls, the spread and territory terms,
   pocket and portal rules, the centre pull).
4. Cards: the change, the count of turns in our games it would alter, the expected move in the curve.

## Hard limits
Read-only on everything existing. No server calls, no posts, no games, no compiling. Write only the report named
below (120 lines or fewer) and scratch scripts under `data/analysis/ladder/dossier/work/` with your prefix. Label
every statement measured (script), read from code (file:line) or estimate. `nice` is refused by the guard: run
scans plainly, at most 2 processes at a time (other analysts share the machine).

## Output format
1. Three lines: the finding, the change in one sentence (or "no card"), how sure. 2. The tables (each top team
apart, ours beside them). 3. "Why, in the code": what our bot does in the same situation and which
agg8-bot/main.cpp lines decide it, with replay turns (game id, round, positions). 4. "The card(s)" (`title:`,
`slug:`, `### Claim`, `### Evidence`, `### Expected signal`, `### What would show it's wrong`) with the diff
against agg8-bot/main.cpp; at most two, each default-off, generic, one build round, each with the count of
events in our own games it would change. 5. "Against it".
Report: `data/analysis/ladder/dossier/diag-topopen.md`; scratch prefix `to_`.
