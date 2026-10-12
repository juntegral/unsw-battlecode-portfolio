import os
D = "~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier"
HEAD = """You are the analyst (team 1119 "meow"). Private, local work: write only the files named below. Submissions close
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
- Reader `tools/ladder_replay.py`; scan scripts in `dossier/work/`; earlier diagnoses `dossier/diag-*.md`."""
TAIL = """## Hard limits
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
events in our own games it would change. 5. "Against it"."""
BRIEFS = {
"topqueen": ("tq2", "# How the top teams' queens live, and what of it our queen can copy", """Read first: `diag-queenhit.md`, `diag-queenhit2.md`, `diag-theirqueen.md`, `queen-path.md`.

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
4. Count on our own online games how many of her deaths each change would have touched and what it costs."""),
"topopen": ("to", "# The first 100 rounds of the top teams against ours: where the gap opens", """Read first: `diag-opening.md`, `diag-opening2.md`, `diag-economy.md`, `diag-spawn.md`, `target/scoreboard.md`.

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
4. Cards: the change, the count of turns in our games it would alter, the expected move in the curve."""),
"topfight": ("tf", "# How the top teams fight: who they ram, when, at what price, and how they avoid being rammed", """Read first: `diag-attack.md`, `diag-queenkill.md`, `diag-bigmap.md`, `diag-feeding.md`, `leader-len.md`.

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
   the threat terms for short and long dragons, SMALL_SPRINT_THREAT, LEADER_GUARD_*), and the cards with counts."""),
"topaah": ("ta", "# aAah (rank 1) and larp stock zi balls (rank 7): what do today's two most promising teams do that Cutlery did not", """Read first: `fingerprint.md`, `target/scoreboard.md`, `diag-economy.md`.

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
   moment, and the counts in our own games."""),
}
for name, (prefix, title, body) in BRIEFS.items():
    text = f"{title}\n\n{HEAD}\n\n{body}\n\n{TAIL}\nReport: `data/analysis/ladder/dossier/diag-{name}.md`; scratch prefix `{prefix}_`.\n"
    open(os.path.join(D, f"brief-diag-{name}.md"), "w", encoding="utf-8").write(text)
    print(name, len(text.splitlines()))
