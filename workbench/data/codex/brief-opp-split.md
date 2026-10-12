# Brief: show the online test result per opponent as well

Work in this repository (unsw-swarm). Edit `tools/pair_report.py` and add tests in `tools/test_pair_report.py` (create it if missing). No commits. No network: do not let any test call `node`, `online.js` or meowbot (stub `load`, `baseline` and `subprocess.run`). Never read `docs/api.txt` or `docs/discord.txt`. Do not start or stop any running process; a detached script will call `python3 tools/pair_report.py bl17594b-test` (without `--post`) some time in the next half hour, so the file must stay importable and runnable at every moment: write your new version to a temporary file and move it into place in one step.

## Why
Today a card won 10 of 30 online against a live baseline of 4 of 30. Lumped together that looked like noise; split by opponent it was 8 of 15 against one team (live 0 of 15) and 2 of 15 against the other (live 4 of 15). The team wants the split in every result from now on.

## What to change
`pair_report.py` builds `lines` (the summary), a per-map `table`, writes `<label>-result.txt`, and with `--post` sends one Discord message built from `lines[0]` and `lines[1]`.
1. After the existing summary lines, add one line per opponent, in a stable order (the order of the run's opponents if the state has it, else by name):
   `vs <opponent>: wins new <w>/<n> vs live <x.x>/<n> | our avg score <a> -> <b> | their avg score <c> -> <d>`
   using the same pooled live baseline as the totals (only keys that have a baseline; opponents with no baseline keep the existing "no live baseline yet" line and get no split line).
2. The Discord message keeps its first sentence as it is and then adds the split in a compact form, for example:
   `by opponent: test4 8/15 (live 0.0), WeHaveQuizzes 2/15 (live 4.0).`
   before the closing "about ±4 wins in 30 games is luck". When the run has a single opponent, add nothing. Keep the whole message under 1,900 characters; if it would be longer, drop opponents from the end and append "…".
3. When the pooled baseline for an opponent holds fewer than 30 live games in total across the shared keys, append ` (thin baseline: <g> live games)` to that opponent's part in the Discord message, and add the same note to the totals sentence when the total pooled live games are fewer than 45. Plain words, no jargon.
4. Nothing else changes: file names, the per-map table, the "this run only" line, the exit behaviour.

## Checks
From inside `tools/`: `python3 -m unittest discover -p 'test_*.py'` must end with `OK` (it has 90 tests now). New tests cover: two opponents with baseline (text lines and message), one opponent (no split in the message), an opponent without baseline, the thin-baseline note, and the 1,900-character cap. Then run, read-only and without `--post`: `python3 tools/pair_report.py qh31d-test` and `python3 tools/pair_report.py qd36-test` (their game files are already downloaded; if a run tries to use the network, stop and say so) and paste the first 8 lines of each output.

## Output
Write `data/codex/report-opp-split.md` last: what changed, the two sample outputs, the Discord message each would have produced (build the string without sending), the last 4 lines of the test run, and anything you were unsure about.
