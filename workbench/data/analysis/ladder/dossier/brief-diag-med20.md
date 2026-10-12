# On medium layouts the top teams have 1.7 to 2.2 times our pearls by round 20. Find where those pearls come from

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

Read first: `diag-topopen.md` (the finding this task starts from, and what it ruled out), `diag-opening.md`,
`diag-opening2.md`, `diag-spawn.md`.

## What we know (measured in `diag-topopen.md`)
On layouts of 701 to 1200 cells the top teams have eaten 1.7 to 2.2 times as many pearls as we have by round 20.
It is the largest early gap measured and has no card. Ruled out already: eating the pearl beside the head (level),
stepping through a portal once beside it (level), paying length for pearls (only two teams). Top teams split
their starters of 4 in round 0 (96 to 100%); ours never do at this size. Their short dragons stand beside a
portal mouth 3.0 to 3.9 turns a game in rounds 0-20 against our 0.2 to 0.4, and nobody found the line for it.

## Your job
1. Rounds 0 to 20 on these layouts, turn by turn, for each top team (fresh games) and for ours (live build and
   main): for every dragon the position, length, what it sees (pearls in view with distance, spawn tiles about to
   spawn, portal mouths, unseen tiles), the step it takes and what the step goes toward. Account for every pearl
   eaten by round 20: was it in view from the start tile, found by walking where (toward the centre, along a
   wall, through a portal, toward the enemy side), eaten by a starter or by a child, on the first or second step
   of a turn.
2. Decompose the gap of pearls by round 20 into: more dragons sooner (round-0 split), more tiles seen sooner
   (direction of the first steps, spreading apart, portals), shorter time from seeing a pearl to eating it, more
   pearls available where they walk (do they go to where pearls are born: the spawn tiles nearest their start),
   two-step turns. The parts must sum to the gap.
3. For the two largest parts: what our dragons do in the same turn and which code lines decide it (the scoring
   terms active in rounds 0-20: territory, unseen, hot tiles, centre pull, stall release, portal terms, the split
   rule), rebuilt from the replay state where you can, as `diag-hungry.md` and `diag-opening2.md` did.
4. Cards: generic changes only (no layout names, no fixed paths), each with the count of turns it changes.

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
Report: `data/analysis/ladder/dossier/diag-med20.md`; scratch prefix `m2_`.
