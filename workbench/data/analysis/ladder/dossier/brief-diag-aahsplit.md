# aAah keeps dragons of 5 to 8 and walks two tiles a turn. Recover its split and growth rule exactly

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

Read first: `diag-topaah.md` (tables 2a and 2b: the finding this task starts from), `diag-split.md`, `diag-economy.md`.

## What we know (measured in `diag-topaah.md`)
aAah (rank 1) runs a flat swarm with no leader and no feeding: 203 total length and 10 dragons of 6 or more at
round 200 (ours 115 and 2.8), 167 turns of two or more steps per 1,000 turns (ours 32), only 37% of its splits
are by a parent of exactly 4 (ours 69%: our bot splits 2 off as soon as a dragon is 4, `SPLIT_MIN_LENGTH 4`).
A dragon of L has ceil(L/4) free steps, so a dragon of 5 to 8 moves two tiles a turn for nothing.

## Your job
1. aAah's split rule from the replays (fresh games first): for every split the round, the parent's length before,
   the child's length, which end leaves, the parent's length after; the distribution by round band (0-20, 21-60,
   61-150, 151-300, 301+) and by dragon count at that moment; what a dragon does between splits (how long it
   stays at 5, 6, 7, 8; does it split when it reaches a length, when it has eaten N pearls, when no pearl is
   near, when an enemy head is near, when the team is under some count). State the rule as a table a programmer
   can code, and how well it predicts the splits (share of turns where the rule says split and it does, and the
   reverse).
2. What the second free step is used for: share of two-step turns that end on a pearl, that eat two pearls, that
   escape an enemy head, that ram; pearls per turn for its dragons of 2-3, 4, 5-8, 9+ against ours of the same
   lengths; deaths per turn by length (is a dragon of 6 rammed more or less than a dragon of 2, and what is lost).
3. The cost side for us: our dragon count would grow more slowly. Compare aAah's dragon count and total length at
   rounds 20, 40, 60, 100, 150, 200 with larp's, Cutlery's and ours on the same layout sizes; does aAah fall
   behind in count early and catch up, and when?
4. Our code: `split_child_size()` and every constant it reads, the sprint use (when does a dragon of ours with two
   free steps take the second one: read `ram_path`, the stride code, `STRIDE_*` constants), and say what the
   smallest change is that reproduces aAah's rule (constants first, new lines only if needed). Give two variants if
   the rule depends on the round or the dragon count. For each, the count of our split turns it would change.

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
Report: `data/analysis/ladder/dossier/diag-aahsplit.md`; scratch prefix `as_`.
