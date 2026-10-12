# Brief: tools/smoke.py — online smoke test of a candidate with one-command rollback

Repo: this directory (unsw-swarm). Read tools/submit.js and tools/online.js (and docs/online.md) first; reuse them, do not reimplement the API.

## Goal
Team meow wants to try a candidate bot online when local A/B is inside noise.
The flow is: upload it, spend some unranked scrims against a chosen opponent (e.g. the team "dev_test_1" / ":P"), look at the result, and roll back fast if it fails.

## Commands (python3 tools/smoke.py ...)
- `plan <botdir> --name <label> --opp <team name or id> [--maps all|a,b,c]`
  Print what would happen: current active submission (rollback target), the upload, the request, and the ticket estimate (`online.js tickets`). Changes nothing.
- `start <botdir> --name <label> --opp ... [--maps ...] --confirm`
  1. Record the current active submission id as the rollback target in data/online/smoke/<label>.json.
  2. `node tools/submit.js upload <botdir> --name <label> --desc "smoke test" --confirm`.
  3. Read the new active submission id.
  4. `node tools/online.js request <opp> --maps <maps> --purpose "smoke <label>" --confirm --expect-active <new id>`.
  5. Save the battle ids to the state file.
  Stop at the first failure and print the exact rollback command.
- `status <label>`: progress of the requested battles (`online.js battle <id> --json`).
- `report <label>`
  Once all battles are done:
  - download them (`online.js download ... --out smoke/<label>`);
  - print a per-map W/L table and totals, plus how each game ended where the data has it;
  - compare with the previous version's games against the same opponent, if any exist in data/online;
  - write data/online/smoke/<label>-report.md.
  Make no decision.
- `rollback <label> --confirm`
  `node tools/submit.js activate <rollback target id> --confirm`, then verify with `submit.js active` and print the result.
  It is one command and is never called automatically by any other command.

## Constraints
- Never print, log or echo keys or tokens (docs/api.txt, docs/discord.txt). submit.js/online.js already read them; let them.
- Without --confirm nothing touches the server (plan output only).
- Do NOT run start/rollback with --confirm, do not upload, do not request battles. Read-only online calls (active, submissions, tickets, leaderboard, battle) are fine for testing.
- Resolve --opp by name via `online.js leaderboard --json` when it is not a number; fail clearly if ambiguous.
- Short comments, English text, python3 stdlib only, `python3 -m py_compile` must pass.

## Output
- Leave the changes uncommitted.
- Write data/codex/report-smoke.md, under 30 lines, covering:
  - usage;
  - what you tested;
  - what `plan` printed for: `plan <any bot dir> --name smoketest --opp dev_test_1 --maps all`;
  - open risks.
