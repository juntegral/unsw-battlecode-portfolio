# Quiet mode for tools/loop_watch.py

Edit only `tools/loop_watch.py`. Do not run the watcher loop, do not post anywhere, do not touch other files
except the summary file named at the end.

## Why
The watcher wakes a costly session on every finished loop step. We want an optional mode that wakes only when
a person (or the session acting for a person) has something to do.

## Change
Accept an optional third command-line argument `quiet` (`python3 tools/loop_watch.py 3600 20 quiet`).
Without it, behaviour must stay exactly as it is now.

In quiet mode:
- Do NOT wake for the "step finished: ..." reason (events with `event == 'done'`).
- Do NOT wake when a card's state changes to `building` or `testing`.
- DO wake when a card's state changes to anything else (for example `needs-look`, `needs-info`, `tested`, `candidate`).
  A card that is new in the list and already in `needs-look` or `needs-info` should also wake.
- Keep every other wake reason unchanged: FAILED step events, "needs attention"/"failed" in the step text,
  a card gone from the list for 4 checks, a late step, stale status.json, runner or meowbot process gone,
  and the `humans()` check.
- When a state change is skipped in quiet mode, update the remembered state (`st0`) so a later change is
  compared with the latest state, not the old one.

Keep the file's style (compact, few comments). Update the module docstring with one line on the new argument.

## Check
- `python3 -m py_compile tools/loop_watch.py`
- Read the diff once and confirm the non-quiet path is unchanged.

## Report
Write 5 lines or fewer to `data/codex/quiet-watch.last.txt`: what changed, and the result of the check.
