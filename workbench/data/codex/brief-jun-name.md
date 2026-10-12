# Brief: show the third team member as "jun" everywhere teammates read

Work in this repository (unsw-swarm). Edit the files under `tools/` that print or post names, and their tests. No commits. No network in tests. Do not start, stop or restart any process. Never read `docs/api.txt` or `docs/discord.txt`. Start from the files as they are now (another change to the `/meow` brain just landed; read `data/codex/report-meow-versions.md`).

## Why
The team is three people. Two of them (Zhe, QWQ) know the third as **jun**; that is the name they see in Discord. Our tools show him as `준싱`, which they cannot map to a person. Everything a teammate reads must say `jun`.

## Wanted
- Display name `jun` instead of `준싱` in everything the tools post or print for teammates: `tools/meowbot.py` (`MEMBERS`, the label-to-name maps, the `/task` choices and `--who`, queue and board texts), `tools/tasks.py`, `tools/decision_nudge.py`, `tools/check-meow.py`, the `/meow` prompt and brain builders if they name members, and any other file under `tools/` that prints the name (grep for `준싱`).
- The GitHub label stays `by:junsing` and every lookup keyed on it keeps working. Where a name is parsed from text a person typed (for example an `Idea by:` line, the `idea_by` option, `/task who:`), accept `jun`, `Jun`, `junsing`, `juntegral` and `준싱` and map them all to the same member, so nothing a teammate or he himself types stops working.
- State already on disk keeps working: `data/meowbot/state.json`, `data/meowbot/snooze.json` and the pair-test state files may hold `준싱` (for example a snooze's `by`); read both spellings, write `jun`.
- Do not rename anything in file names, memory files, docs or commit history; this is about what gets shown and posted from now on. Korean-language notes for the user himself (files under `docs/` or `data/guide/` written in Korean) stay as they are.

## Checks
From inside `tools/`: `python3 -m unittest discover -p 'test_*.py'` ends with `OK`; update the tests that expect `준싱` in output and add tests that the old spellings are still accepted as input and that `by:junsing` still maps to the member. Then `grep -rn "준싱" tools/*.py` and list every remaining hit with one line on why it stays (input alias, comment, test of the alias).

## Output
Write `data/codex/report-jun-name.md` last: what changed, the remaining hits and why, a sample `/task` render and a sample decision-check text built from fixtures, the last 4 lines of the test run.
