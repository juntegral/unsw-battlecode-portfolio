# Where does the queen loop? (card #38, QUEEN_LOOP)

Read-only count on replay files. Do not edit any existing file. Do not run games. Do not post anywhere.
Write only inside `data/local/hunter38/where/`.

## Why
A teammate watched one replay (weakhold) and said the queen "moves through the small maze and heads toward the
middle of the map, where there are a lot of enemy dragons, instead of staying safely at home". The build has no rule
that brings her home: she roams as the old bot does and starts a 2x2 loop wherever she is, except within 4 tiles of
her spawn tile. We want numbers for where the loops actually happen.

## Inputs
- Replays with the switch off and on, 16 games each side, against the normal bot:
  `~/meow-loop-out/card-38/attempt-1/replays/` (`base_*.replay`, `candidate_*.replay`)
- If present when you start, replays against a queen-hunting bot:
  `data/local/hunter38/replays/` (read `data/local/hunter38/README.md` for which files are switch off / on and which
  side is ours). If that run is not finished (no line `DONE` at the end of `data/local/hunter38/run.log`), skip this
  set and say so.
- The existing check script defines every term and already parses these replays:
  `data/local/hunter38/harness/work/card_38_check.py`. Reuse its parsing and its definitions by importing it or
  copying functions into your own script. Use the same meaning for: our queen, her spawn tile, a lap step, on the
  loop, view (7x7 box), round limit UNTIL, length 2-3.

## Count, per replay set, per map, and in total, for switch off and switch on
Only our queen, only decisions before round UNTIL.
1. Lap steps: how many, and the Manhattan distance from her spawn tile at each: median, 25th and 75th percentile,
   and the share at distance <= 4, 5-8, 9-12, 13+.
2. All her decisions at length 2-3: the same distance figures.
3. Map scale for each map: width, height, and the Manhattan distance from her spawn tile to the map centre and to
   the enemy queen's spawn tile, so the distances in 1 and 2 can be read as "near home / middle / their side".
   Report for lap steps the share that are closer to the enemy queen's spawn tile than to her own.
4. Enemy pressure where she loops: for lap steps, the share of decisions with at least one enemy head inside her
   7x7 view, and the mean number of enemy heads within Manhattan distance 6 of her head (true positions from the
   replay). The same two numbers for all her length 2-3 decisions with the switch off, as the comparison.
5. The single replay the teammate watched: `candidate_weakhold_13801_0.replay`. A short timeline: for every 20
   rounds up to her death or UNTIL, her distance from spawn, her length, whether she was lapping, and the number of
   enemy heads within distance 6. Also the same timeline for `base_weakhold_13801_0.replay` if it exists.

## Output
- `data/local/hunter38/where/count.py`: the script, runnable as `python3 data/local/hunter38/where/count.py` from the repo root.
- `data/local/hunter38/where/summary.md`: plain English, short. First 5 lines: the answer to "does she loop near
  home, in the middle, or on their side, and is it more crowded there than where she walks with the switch off".
  Then one small table per count above. State the number of games and decisions behind each number, and anything
  you could not measure. Say which numbers are from the replay's true positions (she cannot see all of that).
- `data/local/hunter38/where/rows.json`: the per-map numbers.

Check your numbers once against the existing `check.json` in `~/meow-loop-out/card-38/attempt-1/`:
your total of lap steps with the switch on should be explainable against its `on_the_loop_decisions` (1255); if it
differs, say why.
