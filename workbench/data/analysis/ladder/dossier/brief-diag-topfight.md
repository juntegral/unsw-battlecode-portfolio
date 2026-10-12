# How the top teams fight: who they ram, when, at what price, and how they avoid being rammed

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

Read first: `diag-attack.md`, `diag-queenkill.md`, `diag-bigmap.md`, `diag-feeding.md`, `leader-len.md`.

## What we know
Cutlery started 4.2 head-ons per 1,000 dragon turns on the ladder and we 2.0; it rams the opponent's queen in 355
of 597 games. Our live build is rammed 105 times a game on big layouts and rams 47. Even trades below the dragon
cap and small-on-big rams were added to our build (TRADE_EVEN, HUNT_SMALL_RATIO).

## Your job
1. For each top team and for ours: head-ons started per 1,000 turns by round band; for each ram the attacker's
   length, the target's length and kind (queen, longest dragon, short), steps walked, length paid, whether the
   attacker died too, the length each side lost, who ate the drops within 5 rounds, own and enemy heads within 5
   tiles. The exchange rate: length lost by them per length lost by the enemy, by attacker length and target kind.
2. Their rules as far as replays show them: when a dragon of length L rams a head of length M (a table of taken
   share by L and M, with chances counted as heads within its free reach and within paid reach), whether they pay
   length to ram and how much, whether they hunt in groups, whether they go for the queen from far away, whether
   they ram to feed their own leader.
3. Defence: how often their dragons end a turn inside an enemy head's free reach, and paid reach, compared with
   ours (by length class); what they do with a long dragon near short enemy heads; whether they keep short
   dragons between their long one or queen and the enemy.
4. The two largest differences from ours, our code lines for the same decision (ram_path, hunt and trade rules,
   the threat terms for short and long dragons, SMALL_SPRINT_THREAT, LEADER_GUARD_*), and the cards with counts.

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
Report: `data/analysis/ladder/dossier/diag-topfight.md`; scratch prefix `tf_`.
