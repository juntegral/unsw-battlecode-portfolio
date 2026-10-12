# Against the top teams we lose short dragons to rams three times as fast as they do in the first 100 rounds. Where, how, and what would stop it

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

Read first: `diag-topfight.md` (their ram rules and why it found no defence card), `diag-topaah.md` (table 2a, the
direct games), `diag-topqueen.md`, `diag-attack.md`.

## What we know
All 45 direct games of our live build against larp stock zi balls, Cutlery and aAah have arrived (folders
`data/online/smoke/top-l1-*` and `top-l2-*`; 7 won). To round 100 we eat about as many pearls per turn as they
do, but we are rammed 4.6 to 5.0 times per 1,000 dragon turns and they 1.5 to 1.6; at round 100 we hold 18 to 25
dragons and they 29 to 43. Their usual ram is a 3 that pays one segment to hit a head two tiles away. Our build
has two switches for our own rams, played online right now (not in these games): a lunge through a pearl and a
trade on a head one shorter. The bot also has an unused term, `SMALL_SPRINT_THREAT`, that makes a short dragon
treat the tiles a short enemy head reaches with one paid step as dangerous.

## Your job
1. Every ram on a dragon of ours of length 2 to 4 in rounds 0 to 150 of the 45 games, and every ram of ours on
   theirs: round, both lengths, the steps and paid length, where on the map (own half, middle, theirs), what our
   dragon was doing on its last turn (walking to a pearl, eating, nothing in view), whether the rammer was in its
   7 by 7 view, heads of each side within 5 tiles, and what each side lost and regained within 5 rounds.
2. The turn before: for each ram on ours, was a step open that ended outside the rammer's free reach plus one paid
   step? Outside free reach only? What did that step cost (a pearl not eaten, distance to a pearl)? Count the
   same question over all turns where an enemy head of 2 to 4 stood within 3 steps of a short dragon of ours and
   no ram followed (the cost side: how many turns a keep-away rule would touch for each ram it avoids).
3. Who rams first when a short dragon of each side come within 3 steps of each other: count the meetings, who
   moved first into reach, who rammed, and the length account. With our two new attack switches on paper (state
   the rule you apply), in how many of the meetings would ours have rammed first?
4. Decide between defence and first strike with counts: `SMALL_SPRINT_THREAT` on (read its code and say exactly
   which tiles it marks), the attack switches, both, or a different rule (for example: only keep away when
   outnumbered in view, only ram when not). One or two cards with the diff, each with the count of rams on ours it
   would have avoided or pre-empted in these 45 games and the turns it changes.

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
Report: `data/analysis/ladder/dossier/diag-toprams.md`; scratch prefix `tr_`.
