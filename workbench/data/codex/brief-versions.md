# Brief: name bots by their portal version in the online-test posts

Work in this repository (unsw-swarm). Edit `tools/smoke.py`, `tools/pair_report.py`, their tests under `tools/`, and `data/online/smoke/run-pair.sh` (git-ignored; first copy it to `data/online/smoke/run-pair.before-versions.sh`). Do not edit `tools/submit.js`. No commits. No network; never run a pair test, an upload, `submit.js`, `subs.js` or anything with `--confirm` (stub them in tests). Never read `docs/api.txt` or `docs/discord.txt`.

Start from the files as they are now (two other changes landed just before this one: plain-language descriptions with `--ref`/`--desc`, and the `--old-only` / `LIVE_ONLY=1` live-bot-only run; read `data/codex/report-live-only.md`).

## Why
The team reads the submissions page, where bots are v1, v2, … (the `version` field of `node tools/subs.js list --json`). Our Discord posts name bots only by card number (#31), which is confusing: a card has several builds and each online run is its own version. They want the version first, the card second.

## Wanted
1. After the upload in `smoke.py pair`, look up the version of the new submission and of the live submission (one `node tools/subs.js list --json --last 40` call; on failure keep going without versions) and store both in the state file (`halves.new.submission.version`, `halves.old.submission.version`, and the same for `rollback`).
2. Discord notices from `run-pair.sh`:
   - start: `🧪 testing online now: v<new> = v<live> main + <ref>, 15 maps vs each of <names>. the active bot swaps for ~20 min, please don't upload or swap until "done, swapped back"` (if the new version is not known yet when the notice is sent, send the notice right after the upload instead of before it, or say `new bot` and add the version in the "done" notice; choose the simpler one and say which).
   - done: `✅ done, swapped back: v<live> main is active again. v<new> (<ref>) finished, result coming`.
   - live-only mode: name the live bot as `v<live> main`.
3. `pair_report.py --post`: first line `📊 v<new> = v<live> main + <ref>, online result, same teams + maps`; column headers `wins v<new>` and `wins v<live>` instead of `wins new` / `wins live`; the last line says `v<live> baseline <g> games`. When the versions are not in the state (older runs), fall back to today's wording. The printed text and `<label>-result.txt` get one new first line `v<new> = v<live> main + <ref>` when versions are known and are otherwise unchanged.
4. Nothing else changes.

## Checks
`zsh -n data/online/smoke/run-pair.sh`; from inside `tools/`: `python3 -m unittest discover -p 'test_*.py'` ends with `OK`, with tests for: versions stored in the state, lookup failure, the three notice texts, the result message with and without versions.

## Output
Write `data/codex/report-versions.md` last: what changed, the sample notices and result message exactly as they would be sent, the last 4 lines of the test run, anything not exercised.
