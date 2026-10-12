# Brief: retry a swap when another team's battle is live (tools/smoke.py)

Work only in this repository (unsw-swarm). Edit only `tools/smoke.py`, `tools/test_smoke.py` and (for the last section) `tools/pair_report.py`. No commits, no network, never run smoke.py against the real server, never read `docs/api.txt` or `docs/discord.txt`. Other files here have unrelated uncommitted changes: leave them alone.

## Problem
In `pair_execute`, `run('submit.js', 'upload', ...)` and `run('submit.js', 'activate', ...)` can fail with a RuntimeError whose text contains `live or pending` (submit.js refuses while another team's battle against us is running). `wait_no_pending()` is called just before, but a new battle can arrive in between. Today this stopped two online tests: once at the swap back (the test bot stayed active) and once at the upload.

## Change
1. Add a helper, e.g. `swap(*args)`, that calls `run('submit.js', *args)` and, when the error text contains `live or pending`, sleeps 15 seconds and tries again, for at most 15 minutes in total (use `time.monotonic()` like `wait_no_pending`). Any other error is raised at once. After the deadline the last error is raised.
2. Use it for the upload and for the activate in `pair_execute`, and for the activate in `perform_rollback`. Before each retry of the upload keep the existing guards (`check_freeze()`, `pair_time_left(state)`).
3. Keep everything else as it is, including the state file fields and the messages printed on failure.

## Tests (tools/test_smoke.py, same style as the existing ones, `time.sleep` patched)
- upload refused twice with `live or pending`, then succeeds: the pair finishes `rolled-back`.
- activate at the swap back refused once, then succeeds: phase `rolled-back`, active bot is the old one.
- a refusal that never clears: the error is raised after the deadline (patch `time.monotonic`), state phase `failed`, rollback command printed.
- an error without `live or pending` is not retried.
Run `python3 -m unittest tools/test_smoke.py` from the repo root; it must end with `OK`.

## One more small fix (third file allowed: `tools/pair_report.py`)
The first line of the report lists every pooled live run, even runs that share no (opponent, map) key with the new games. Example seen: `live baseline pooled over 15 games: 10/30, 11/30, 8/30, 8/30, 2/15` where only the last run played that opponent. List only the runs that contributed at least one key that the new games also have, and show for each how many of its games were used (wins/games over the shared keys). Keep the rest of the output format unchanged. Check it by running `python3 tools/pair_report.py tc30-dev1b` and `python3 tools/pair_report.py tc30-test` (read-only: both already have their game files; do not pass `--post`).

## Output
Write `data/codex/report-smoke-retry.md`: what changed (short), the full test output's last 5 lines, and anything you were unsure about. Write that file last.
