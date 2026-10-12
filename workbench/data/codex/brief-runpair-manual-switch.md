# Brief: online pair test must not undo a teammate's manual bot switch; start notice must not be skipped

Work in this repository (unsw-swarm). Mechanical change. Do NOT run any online command (no `submit.js`, `online.js`, `smoke.py start|pair|baseline|rollback`, `run-pair.sh`), no network, never read `docs/api.txt` or `docs/discord.txt`, no commits. Do not post to Discord (do not call `meowbot.py`).

## What happened (2026-10-06 05:38–05:44 KST)
`data/online/smoke/run-pair.sh qs39c-test …` had uploaded and activated a test bot (18016); the bot that was live before was 17997. A teammate then activated 17790 by hand. The tool noticed (`data/online/smoke/qs39c-test.log`: "STOPPED: Active submission identity not verified / Active state: {"id": 17790 …} (verified) / ROLLBACK REQUIRED … activate 17997") and then its rollback step activated 17997, undoing the teammate's choice. Also, because the upload had needed a retry, the "🧪 testing online now" start notice was never posted (see the condition around lines 109–114 of `run-pair.sh`: it requires `attempts = 1` and `network_retries = 0`).

## Change 1: do not roll back over a manual switch
In `data/online/smoke/run-pair.sh` (git-ignored; first copy it to `data/online/smoke/run-pair.before-manual-switch.sh`), and in `tools/smoke.py` only if really needed:
- Before the rollback step runs, read the active submission id (the script already has a way to do it; reuse it). Let TEST be the id of the test submission of this run (from the state file `data/online/smoke/$LABEL.json`, `halves.new.submission.id`) and BASE the id to restore.
- If the active id is neither TEST nor BASE, a person switched the bot: do NOT roll back, do not retry, and post exactly one notice through the existing `say` helper:
  `⚠️ $REF online test stopped: someone set the active bot to <id> <name> during the test. leaving it as it is, nothing was swapped back. the bot that was live before the test was $BASEID`
  Then mark the state so later runs do not try again (the state file has `rollback_required`; set it to false and add a `note` saying the active bot was changed by hand to <id> and the rollback was skipped). Exit non-zero so launchers see the run did not finish normally.
- If the active id is TEST or BASE, behave exactly as today.

## Change 2: the start notice is posted once even after retries
The start notice must be posted the first time the test bot is really about to be or has been activated, whatever the number of attempts or network retries, and still only once per run. Keep the LIVE_ONLY variant as it is.

## Checks
- `zsh -n data/online/smoke/run-pair.sh` passes.
- Add a small offline test (`tools/test_run_pair_manual_switch.py` or a shell test under `data/online/smoke/`) that exercises the new decision with stubbed commands (put fake `node`/`python3` wrappers first in PATH, or factor the decision into a small function/script that can be called with ids as arguments) for the three cases: active = TEST, active = BASE, active = other. It must not touch the network.
- `cd tools && python3 -m unittest discover -p 'test_*.py'` still passes; report the count.

## Output
Write `data/codex/last-runpair-manual-switch.txt`: what changed (file and line ranges), the test output, and anything you could not verify offline.
