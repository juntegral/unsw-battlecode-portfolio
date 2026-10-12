# Queen behaviour of aAah (team 454) against ours: statistics from replays (QWQ's request on card #38)

## Why
QWQ wrote on card #38 (7 Oct 12:02 KST): "I've just carefully reviewed nAah's (rank 1) replays and noticed that their
Queens don't play conservatively at all, there's no circling or similar behavior, yet their survival rate remains high.
In contrast, the 'Queen circling' tactic we currently use actually results in a loss of ground on the minimap. I believe
nAah's strategy boils down to a few key points: first, the Queen doesn't take the initiative, meaning she doesn't engage
the enemy first, and second, she spends most of her time positioned among or behind her teammates. Could you compile
some statistics from their replays?"

The closest team name on the leaderboard is "aAah", team id 454 (rank 5, rating 2406 on 7 Oct 12:04 KST). Use that team.
If the data shows a different team actually named nAah, say so at the top of the report and use that one instead.
We are team 1119 "meow". Rules reminder: at round 500 the longer queen wins and a dead queen counts as 0.

## Hard limits
- Server: read-only calls only (leaderboard, team, battles, game and replay downloads; these cost no tickets).
  Never request a battle, never upload or activate a submission.
- Never print, copy or move `docs/api.txt` or `docs/discord.txt`. Only our existing tools may read them.
- No Discord or GitHub posts. Do not edit existing files. Write only inside `data/local/queen454/`.
- The qualifier is played on unseen maps: no per-map conclusions. Splitting by map size class is fine.
- A replay shows positions, actions, deaths and pearls, not intent. Keep measured numbers apart from readings.

## Step 1: data
- Find how earlier work downloaded other teams' games: `data/online/dl-20261003/`, `data/online/dl-20261004/`,
  `data/online/REMOTE-LOG.md`, `data/analysis/top1/` (its scripts and `cache/`), and `tools/` (`online.js`, any
  story/digest/download tool). Reuse those tools.
- aAah: their recent games, both sides, aim for 60 to 120 games from the last 2 to 3 days, preferring opponents rated
  2000 or more. Note bot version changes if the data shows them.
- Ours: recent ladder games of our live code (versions 44 and 47 are the same code) from
  `data/analysis/ladder/rows.jsonl` and the replays under `data/online/` (60 games or more if available).
- If it is cheap: the replays of the #38 queen-loop builds under `~/meow-loop-out/card-38/` (read only) as a third column.

## Step 2: per-game numbers for a team's queen
The queen is the dragon a team starts with. For the id rule and for replay parsing see
`data/local/hunter38/deaths/count.py`, `data/codex/brief-queen-deaths.md` and `data/local/card47/ledger47.py`.
1. Survival: alive at the end, death round, cause of death (enemy head, wall, own body, dropped with no action, other).
2. Initiative: while an enemy head is inside her 7x7 view, how often her step shortens the distance to the nearest
   enemy head and how often it lengthens it; kills made by the queen; head-on hits she is part of; before each queen
   kill or queen death, who closed the distance over the previous 5 rounds.
3. Among or behind teammates (sample every 10 rounds): how many of her own dragons are nearer to the nearest enemy head
   than she is; share of samples with at least one teammate nearer; her distance to her team's centre, to the nearest
   teammate head, and to her start tile.
4. Circling against travelling: unique tiles per 50 rounds, net displacement per 50 rounds, bounding box, share of
   rounds spent in a loop of 2x2 or 3x3 tiles.
5. Ground: a team-level proxy for "ground on the minimap", for example the share of open tiles nearer to that team's
   heads than to the other team's, at rounds 100, 200, 300, 400; say which proxy you used.
6. Length: queen length at rounds 100, 200, 300, 400, 500; pearls eaten; splits after round 200.
7. Games decided by the queen rule: count, and her length against the other queen's.
Split by phase (rounds 1-100, 101-300, 301-500) and by map size class (600 tiles or fewer, larger).

## Step 3: output (all in `data/local/queen454/`)
- `summary.md`, 80 lines or fewer, plain English, no jargon without a gloss:
  - line 1 to 3: which team and how many games on each side of the comparison, and the dates.
  - one compact table: aAah, ours (and the #38 build if done) per number, with n.
  - "Measured": a verdict line for each of QWQ's claims, with the numbers: (a) their queen does not engage first,
    (b) she is mostly among or behind teammates, (c) she does not circle, (d) our circling queen holds less ground.
  - "Read, not tested": at most 5 lines.
  - "Limits": sample size, opponent mix, version changes, anything you could not measure.
- `rows.json` (one row per game) and the scripts you wrote.
- `last.txt`: 5 lines or fewer on what was done and anything that failed.

## Addendum for this run (7 Oct 12:2x KST)
An earlier run by another model was stopped. It left downloaded data in `data/local/queen454/`:
`M*.replay`, `game-*.json`, `battle-*.json`, `profile-*.json`, `team454.json`, `leaderboard*.json`, `manifest.json`,
`downloaded.json`, `fetch.js`. Reuse that downloaded data; download more only if a side of the comparison is missing.
Do NOT read or reuse its analysis: `analyze.py`, `report.py`, `validate.py`, `rows.json`, `summary.md`, `strata.json`,
`paired-ground.json`, `computed/`, `computed-v2/`. Write your own scripts and every output under
`data/local/queen454/sol/` (`summary.md`, `rows.json`, `last.txt`, scripts). Count from the replays yourself.
