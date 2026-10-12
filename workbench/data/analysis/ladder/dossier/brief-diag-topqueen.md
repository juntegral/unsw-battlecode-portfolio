# How the top teams' queens live, and what of it our queen can copy

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

Read first: `diag-queenhit.md`, `diag-queenhit2.md`, `diag-theirqueen.md`, `queen-path.md`.

## What we know
With our queen dead and theirs alive we won 0 of 61. Our queen is alive at the end in 27% of games on the live
build. Two mid-table opponents keep their queens alive by being threatened less (one stays home, one roams inside
its own swarm and grows after round 100). An earlier note says Cutlery's queen is not a home queen: she roams and
survives by length and sprints.

## Your job
1. For each top team's queen (454, 157, 306, 70, and 91 and 264 from the older set), and ours beside them:
   alive at rounds 50, 100, 150, 300, end; her length over time and the share of her turns at each length; her
   splits (round, length before and after, how many children); distance from her start tile over time; own heads
   within 3 and 5 tiles; enemy heads within 3 steps per 100 of her turns and what she does then (step away,
   sprint with how much paid, split, attack); pearls she eats per 100 turns; how she dies when she dies; whether
   she kills (rams) and what.
2. Sort the top teams into the kinds of queen they run (home, escorted, long roamer, fighter, sacrificed early on
   purpose: check deaths by illegal split or by her own move in the first rounds, which may be deliberate) and say
   which kind wins most against which. Is there one thing all of them do that ours does not?
3. For that thing (or the two largest): the exact rule as far as replays show it (thresholds in length, distance,
   rounds), what our queen does instead and which code lines decide it (her split rule, QS_KEEP_LEN, the safety
   rings, queen_wait, QUEEN_NO_FEED, QUEEN_LEAD_BONUS, the dead-end terms, home terms), and the smallest change.
4. Count on our own online games how many of her deaths each change would have touched and what it costs.

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
Report: `data/analysis/ladder/dossier/diag-topqueen.md`; scratch prefix `tq2_`.
