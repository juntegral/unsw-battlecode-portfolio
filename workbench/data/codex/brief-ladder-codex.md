# Move the hourly ladder analysis from Claude to Codex, and run it every 3 hours

Edit only `tools/ladder_hourly.py` (and `tools/test_ladder.py` if a test needs to follow the change).
Do not start or stop the runner, do not call any model while testing, do not post anywhere.

## Why
The analyst and verifier steps of `tools/ladder_hourly.py` call `claude -p --model claude-opus-5-5` every hour.
That is the largest Claude cost of the day. jun decided (7 Oct 12:1x KST) to move both steps to Codex and to run
the analysis every 3 hours. Collecting and tallying stay as they are.

## Change
1. Analyst and verifier call Codex through our wrapper instead of `claude`:
   `tools/cx.sh <log file> -m gpt-6-astra -c model_reasoning_effort=high -s workspace-write -C <repo root> "<prompt>"`
   - Both roles use reasoning effort `high`. No `xhigh`, no `max`, also on the first run.
   - `tools/cx.sh` writes all Codex output to the log file and returns Codex's exit code. Stdin is closed.
   - Keep the prompts, the files each role is told to write, and the success checks as close to today's as you can.
     Where the code read Claude's stream-json output, read instead what the role wrote to disk, or the end of the
     cx log. Keep one log file per role and hour under `data/analysis/ladder/logs/`.
   - Remove the Claude-only arguments (`--settings`, `--permission-mode`, `--output-format`, and so on) from these calls.
2. The analysis (analyst, then verifier) runs only when the KST hour is a multiple of `ANALYSIS_EVERY_HOURS = 3`
   (00, 03, 06, ... 21). Polling, collecting and the tally steps keep their current schedule every hour.
   Log a short "analysis skipped this hour" line to `runner.log` on the other hours.
3. Keep the rule that this runner never posts to #meow.

Keep the file's style (compact, few comments).

## Check
- `python3 -m py_compile tools/ladder_hourly.py`
- `cd tools && python3 -m unittest test_ladder -q` must pass (adjust the test only where it asserted the old command).
- Read the final diff once.

## Report
Write 8 lines or fewer to `data/codex/ladder-codex.last.txt`: what changed, test result, and the exact command to
restart the runner without re-running the first analysis.
