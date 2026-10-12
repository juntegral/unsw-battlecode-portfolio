# Brief: make the online pair test survive two start-up failures seen on 5 Oct

Work in this repository (unsw-swarm). Edit `data/online/smoke/run-pair.sh` (git-ignored; first copy it to `data/online/smoke/run-pair.before-retry2.sh`) and, only if needed, `tools/smoke.py` plus its tests under `tools/`. No commits. No network. Do NOT run a pair test, an upload, or anything with `--confirm`. Never read `docs/api.txt` or `docs/discord.txt`.

## What happened (logs are in `data/online/smoke/`)
1. `qw37-test.log` / `qw37-test.json`: `smoke.py pair` stopped with `STOPPED: submit.js upload failed (exit 1): fetch failed` (a network error on the upload request). Nothing had been swapped, the state says the live bot is active and verified, phase `failed`. `run-pair.sh` did not retry; it posted "online test stopped early" to Discord and the launcher went on.
2. `qh31c-dev1.log`: the run ended within 90 seconds with `Error: Our battles are live or pending; refusing to swap or start`, before a state file existed (the launcher logged phase `none`). `run-pair.sh` already retries on some messages (read it: "refusing to swap or start", "Insufficient", "live or pending"), but this case was not retried, and the "stopped early" notice went out with an empty phase.

## Wanted
- Case 1: when the pair run stops before any swap because the upload request failed on the network (`fetch failed`, `ECONNRESET`, `ETIMEDOUT`, `EAI_AGAIN`, `socket hang up`), and the state shows the live bot still active, wait 60 seconds and start the same run again, up to 5 times. It must be safe to start again under the same label: find out what `smoke.py pair` does when the label's state file already exists with phase `failed` and nothing played, and handle it (resume, or move the failed state aside as `<label>.failed-<n>.json`), without ever discarding a state that has played games or a pending rollback.
- Case 2: find why the "live or pending" refusal in `qh31c-dev1.log` was not retried, and make it retried: every 60 seconds for up to 30 minutes.
- Retries are quiet: no Discord post for a retry. The "stopped early" notice goes out only when the run finally gives up, and it then names the reason in plain words (for example "the server kept refusing the swap for 30 minutes because other battles of ours were running") instead of an empty phase.
- Everything else in the script stays as it is (the automatic rollback loop, the opponents argument, `BASELINE=1`).

## Checks
`zsh -n data/online/smoke/run-pair.sh`; from inside `tools/`: `python3 -m unittest discover -p 'test_*.py'` must end with `OK`. If you can exercise the new retry branches without the network (for example with a stub in place of `smoke.py` through an environment variable that already exists, or a dry-run path), do so and show the output; if not, say exactly which lines were not exercised.

## Output
Write `data/codex/report-runpair-retry.md` last: what changed and where (line numbers), how each of the two cases now behaves step by step, what was and was not exercised, and anything you were unsure about.
