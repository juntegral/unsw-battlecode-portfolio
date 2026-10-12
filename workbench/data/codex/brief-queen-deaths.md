# How our queen dies, and how long she is when the queen rule decides (card #38 follow-up)

Read-only count on replay files. Do not edit any existing file. Do not run games. Do not post anywhere.
Write only inside `data/local/hunter38/deaths/`.

## Why
Our queen (the dragon our team starts with; ids and the "real queen" rule are in the check script) is dead before
round 300 in about three of four games, with or without the new loop rule. A third of her deaths are recorded as
"wall" or "self" (own body), with no enemy needed. We need to know whether those are forced (she had no safe move)
or a bad step, and when and where they happen. Separately, in games decided by the queen rule (at round 500 the
longer queen wins, a dead queen counts as 0) the loop arm's queen ends shorter, and we do not know why.

## Inputs
- Hunter run, 68 games per arm: `data/local/hunter38/replays/` (read `data/local/hunter38/README.md` and
  `data/local/hunter38/result.md` for which files are switch off (base) / switch on (candidate) and which side is ours).
- Check run against the normal bot, 16 games per arm:
  `~/meow-loop-out/card-38/attempt-1/replays/` (`base_*.replay`, `candidate_*.replay`).
- The existing check script parses these replays and already classifies queen deaths:
  `data/local/hunter38/harness/work/card_38_check.py`. Reuse its parsing and definitions (our queen, death cause
  wall / self / body / headon / none, lap step, view, reach). Your death totals per arm must match
  `data/local/hunter38/check.json` (`queen_deaths_by_cause`: base wall 16, self 7, body 1, headon 33, none 2;
  candidate wall 12, self 9, body 2, headon 31, none 2). If they do not, stop and say why.

## Part A: every queen death, both replay sets, both arms
For each queen death record: replay, arm, map, round, cause, her length just before, Manhattan distance (board
wraps) from her spawn tile, and for the decision that killed her:
1. Safe moves she had: count the one-step moves from her head that were not a wall, not any dragon body in the
   replay's true state (her own included, allowing for her tail moving if the check script's rules do), and not a
   tile an enemy head could reach that turn by the check script's reach rule. Report three classes:
   `forced` (0 legal moves), `only risky` (legal moves existed but all were inside an enemy head's reach),
   `had a safe move` (at least one legal move outside every enemy head's reach).
2. Room: the number of tiles reachable from her head by walking (flood fill, true state, cap at 30) just before
   the death, and 5 and 10 rounds before it. A shrinking number means she walked into a pocket.
3. Enemy pressure: enemy heads within Manhattan 6 at the death and 5 rounds before.
4. For wall and self deaths only: was the fatal action a multi-step move (free or paid steps) or a single step,
   and was she on a lap step in the previous 4 rounds.
Tables: by cause x class (forced / only risky / had a safe move), per arm and per replay set; death round
distribution by cause (before r50, r50-99, r100-199, r200-299, r300+); by cause, the median room at -10, -5, 0.
List up to 5 example replays (file, round) for each of: wall death with a safe move available, self death with a
safe move available, forced wall death.

## Part B: queen length by round where the queen rule decided
Games that ended on the queen rule are marked `how == "queen"` in `data/local/hunter38/rows/*.rows.jsonl`
(fields tag, map, seed, side, win, us, them). For each such game, both arms, and also for every trauma game in the
hunter set whatever its ending: our queen's length and their queen's length at r100, r200, r250, r300, r350, r400,
r450, r500; pearls each queen ate in r0-299 and r300-500; the number of times each queen split (shed a child) in
r0-299 and r300-500; our queen's loop share (lap steps per decision) before r300 and from r300. State how many
games are behind each line. The question to answer in plain words: when does the switch-on queen fall behind the
switch-off queen in these games, before r300 or after, and is it from eating less, splitting more, or dying.

## Output
- `data/local/hunter38/deaths/count.py`, runnable from the repo root.
- `data/local/hunter38/deaths/summary.md`: plain English, short. First 6 lines: the answers (what share of wall
  and self deaths were forced, when they happen, and when the switch-on queen falls behind). Then the tables.
  Give the number of games and deaths behind every figure, say which figures use the replay's true state (she
  cannot see all of it), and list what you could not measure.
- `data/local/hunter38/deaths/rows.json`: one row per death, one row per game for part B.
