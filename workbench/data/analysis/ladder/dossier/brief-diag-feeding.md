# What does the feeding phase buy us and what does it cost? Decide, and design one switch or none

You are the analyst (team 1119 "meow"). Submissions close 2026-10-09 15:00 KST; the qualifier maps are unseen.
This is local, private work: write only the files named below.

## The question
From round 400 (or earlier once we hold 56 dragons after round 200) our bot feeds: short dragons die on purpose
beside the leader so that it eats what they drop, and FEEDER_KEEP_UNITS 3 is all that is kept. The game is decided
at round 500 by the longer queen (a dead queen counts 0), then the longest dragon, then total length; a side with
no dragon left has lost. Feeding turns a swarm into one long dragon. If that dragon dies, or was already long
enough, the swarm was spent for nothing, or for a loss.

Three observations that raise the question (none is a count over the ladder yet):
- A black-box opponent built against our bot won 7 of its 17 wins this way: "late on it lets its swarm die to feed
  one long dragon and can then be eliminated" (`~/meow-redteam/report.md`, weakness W2; our count
  went 59 at r320, 26 at r440, 5 at r480, gone at r489).
- A local game today on the ladder layout Islands: we held 52 dragons and a leader of 45 at r400 against an enemy
  whose longest dragon ended at 18; at r500 we had one dragon of length 2 and lost on longest dragon.
- An earlier ladder count (450 main games): 10 of 209 losses were wipe-outs after r400.

## Already counted (read first)
`data/analysis/ladder/dossier/summary.md` and `per-game.jsonl` (500 main ladder games, per-game rows; schema in
`count_dossier.py`), `data/analysis/ladder/findings.md` (search: feed, F32, leader, both dead, longest),
`data/analysis/ladder/losses/plan.md`, and today's `dossier/diag-islands.md` (the leader rules before feeding).
Replays under `data/online/`. Bot: `~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp`
(feeding_phase, is_feeder, FEED_CAP_UNITS, FEEDER_KEEP_UNITS, feed_round, ENDGAME_ROUND, the queen-game rounds).

## Your job
1. Over every main ladder game that reaches the start of our feeding (say how you detect it per game: the round,
   and whether it started by the round or by the 56-dragon rule): our dragons, longest and total length at that
   moment and at the end, theirs the same; how the game was decided; and the result.
2. What feeding buys: in how many games was the final decision "longest dragon" or "total length" in our favour
   AND would have gone the other way with our longest as it was when feeding began (compare with their longest at
   the end)? In how many was our leader already longer than their final longest when feeding began?
3. What feeding costs: games where the leader died after feeding began (round, cause, its length), games where
   we were wiped or ended with 3 dragons or fewer, games lost that we were winning on every rule when feeding
   began. Open 5 or 6 replays of the worst cases and say what kills the leader and what the feeders were doing.
4. How much of the fed length arrives: length our feeders give up against length the leader gains, per game.
5. Decide with confidence: ONE default-off switch that fits a single build round, or "no card". Candidates you
   may weigh, or better ones of your own: feed only while our leader is not yet longer than the longest enemy
   dragon known by a margin; keep a larger reserve than 3; stop feeding and split again when the leader dies.
   The rule must be something a dragon can measure in play. No map names.

## Hard limits
Read-only on everything existing. No server calls, no posts, no edits to bot or loop code. Write only
`data/analysis/ladder/dossier/diag-feeding.md` (110 lines or fewer) and scratch scripts under
`data/analysis/ladder/dossier/work/` (prefix `fd_`). Label every statement measured (script), read from code
(file:line) or estimate.

## Output: `diag-feeding.md`
1. Three lines: what feeding buys and costs in games, the change in one sentence (or "no card"), how sure and why.
2. The tables for jobs 1 to 4. 3. "Why, in the code". 4. "The card" with `title:`, `slug:`, `### Claim` (proposal
   and switch name), `### Evidence`, `### Expected signal` (a mechanism check a replay can show),
   `### What would show it's wrong`. Or "No card". 5. "Against it": the strongest counter-evidence, fairly.
