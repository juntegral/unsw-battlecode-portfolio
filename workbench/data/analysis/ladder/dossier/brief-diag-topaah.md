# aAah (rank 1) and larp stock zi balls (rank 7): what do today's two most promising teams do that Cutlery did not

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

Read first: `fingerprint.md`, `target/scoreboard.md`, `diag-economy.md`.

## What we know
All our top-team marks come from Cutlery (team 306) up to 5 Oct. aAah (454) is now 110 points above it and larp
stock zi balls (157) is the team our lead thinks has the most promise. We have never measured either.

## Your job
1. A behaviour fingerprint of 454 and of 157 from the fresh folder (and the few older aAah games), with the same
   rates as `target/scoreboard.md` where the tools allow (reuse `dossier/work/tg_run.py` and the scan scripts),
   beside Cutlery's old marks, Cutlery's fresh games, chad gdp (70) and our live build. Say how many games each
   column rests on and mark the rates that rest on fewer than 20 games.
2. The five rates where 454 differs most from Cutlery, and the five where 157 does, each with what the replays
   show behind the number (open two or three games per team and describe the first 150 rounds in plain words:
   how they open, when they split, how the queen moves, when a long dragon appears, how they fight).
3. Anything structurally different from our bot: a fixed opening, a guard around the queen, a second long dragon,
   deliberate deaths to recycle length (illegal split deaths were 18 per 1,000 turns for Cutlery), portal use,
   camping on spawn tiles, blocking corridors with bodies.
4. Which two of these our bot could take with one switch each, the code lines of ours that decide the same
   moment, and the counts in our own games.

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
Report: `data/analysis/ladder/dossier/diag-topaah.md`; scratch prefix `ta_`.
