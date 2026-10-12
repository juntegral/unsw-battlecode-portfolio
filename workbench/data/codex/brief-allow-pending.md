# Brief: uploading main must not wait for pending battles

Work in this repository (unsw-swarm). Edit `tools/submit.js`, `tools/meowbot.py` and tests under `tools/`. No commits. No network: do not run `upload`, `activate`, `active` or `check`. Never read `docs/api.txt` or `docs/discord.txt`. Do not start, stop or restart any process.

## Why
`submit.js upload` refuses with `refusing: N of our battles are live or pending (…); retry later or --force` (two places, around lines 102 and 134). On 5 Oct that made a release upload wait 20 minutes for an unrelated ranked battle. A match that is already running keeps the bot version it started with, so a release upload does not disturb it. The refusal is still needed for paired online tests (`tools/smoke.py pair` swaps the active bot and relies on it so test games and other games do not mix), and for `activate` used as a rollback inside those tests.

## Wanted
1. `submit.js upload` accepts `--allow-pending`: with it, live or pending battles produce one line `note: N of our battles are live or pending (ids); uploading anyway, running matches keep their version` and the upload continues. Without it, behaviour is exactly as today. `--force` keeps its meaning. `activate` is unchanged.
2. `tools/meowbot.py` `upload()` (the release upload behind `/submit` and candidate approvals) passes `--allow-pending` always. Nothing in `tools/smoke.py` changes: test uploads keep the refusal.
3. Update the usage text in `submit.js`.

## Checks
`node --check tools/submit.js`; from inside `tools/`: `python3 -m unittest discover -p 'test_*.py'` ends with `OK` (184 tests now), with a test that the bot's release upload command includes `--allow-pending` and that the smoke upload command does not. If the pending check in `submit.js` can be exercised offline by factoring it into a small function, add a test for both branches; otherwise say what was not exercised.

## Output
Write `data/codex/report-allow-pending.md` last: what changed, the last 4 lines of the test run, anything not exercised.
