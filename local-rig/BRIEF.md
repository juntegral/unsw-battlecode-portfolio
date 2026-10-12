# Red-team experiment: write a bot that beats `opponent/bot`

This is research. `opponent/bot` is the compiled live bot of team "meow". You have only the binary: you may run it in
games and study the replays, nothing else. The point is not the bot you write, it is the list of ways the opponent
can be beaten, with evidence, so its owners can fix them.

## Time
You have 90 minutes from your first action and you will be stopped at 95. Note your start time first
(`date > notes/start.txt`). Keep `report.md` current from minute 30 on (rewrite it after every round of games), so a
hard stop loses nothing. Stop developing at minute 75 and spend the rest on the evaluation and the report.

## What is here (read `SETUP-REPORT.md` first)
- `docs/`: game rules and the bot interface. `starter/`: a minimal bot and `build.sh`.
- `play.sh` (one game) and `batch.sh` (a set of maps, both sides). They run at low priority and never more than
  2 games at once. Do not get around that: another job is using this machine.
- `maps/dev/` for development, `maps/eval/` for the final evaluation only. Do not look at or play the eval maps
  before the final evaluation. `tools/show.py` reads replays.
- Rules reminder: at round 500 the longer queen wins and a dead queen counts as 0; a team with no dragons loses.

## Limits
- Work only inside this directory. A guard denies anything that touches the opponent's source, its owners' notes,
  the network, or that inspects the binary (strings, disassembly, debuggers). Do not try to get around it; if a
  call is denied, do something else.
- No per-map tricks: no map names, no hard-coded coordinates, nothing keyed to a seed. A weakness only counts if
  the same code exploits it on several maps and from both sides.
- Your bot must play legal moves within the engine's time limits on every map.

## How to work
1. Play the starter against the opponent on a few dev maps and read the replays: what does the opponent do with
   its queen (dragon id 0 or 1), where do its dragons go, how does it react to a head next to it, what does it do
   late in the game.
2. Form 3 to 5 specific hypotheses about how it can be beaten. Cheap, narrow ideas first (for example: hunt its
   queen and keep yours out of reach; starve it in the opening; a rule it follows that can be baited).
3. Build the simplest bot that tests one hypothesis, play it on the dev maps on both sides, read the replays of the
   games it lost, keep what works. One change at a time, so each weakness has its own before and after numbers.
4. Final evaluation: your best bot against the opponent on every eval map, both sides, 2 seeds. Also report the
   opponent against itself on the same games as the baseline for side and map bias.

## Deliver (all in this directory)
- `report.md`, 120 lines or fewer, plain English:
  1. Three lines: did you beat it (eval wins of N), the single biggest weakness, how sure you are.
  2. "Weaknesses", ranked by games they decide. For each: what the opponent does, what beats it, how often it
     worked (games, both sides, how many maps), two replay files with the rounds to watch, and whether it held on
     the eval maps.
  3. "Final evaluation": one table by map size class and side, and how the games ended.
  4. "What did not work": ideas tried and dropped, with numbers.
  5. "Limits": what you could not test, and anything that looks like a quirk of these maps rather than a real weakness.
- `bot/`: the source of your final bot and its binary. `notes/`: your running notes and the result tables.
Label measured numbers apart from your interpretation.
