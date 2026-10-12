# Brief: update tools/smoke.py with the team's guardrails

Repo: unsw-swarm. tools/smoke.py was just written by another job; read it and data/codex/report-smoke.md first. Also tools/smoke_pick.py, if it exists.

The team agreed (Discord, 10-03 22:28) on these rules:
1. Use the DEV allowance. The team "dev_test_1" has its own 60 games/hour, so we don't burn the normal budget.
   Find out from tools/online.js / docs/online.md how dev games are requested and counted. If there is a dev-specific flag or team, use it; if not, document clearly what `plan` assumes.
2. About 60 games per candidate. Default the map list or repeat count so that one `start` requests about 60 games. Show the count in `plan`.
3. Record a v61-vs-dev_test_1 baseline once and reuse it: `smoke.py baseline --name v61 ... --confirm`.
   - It requests the same set with the current active (rollback target) bot and stores it as data/online/smoke/baseline-<label>.json.
   - `report` compares the candidate with the stored baseline.
   - If a baseline is missing, `plan` says so.
4. Judge by mechanism numbers, not by wins. `report` runs tools/smoke_pick.py, if present, on the downloaded dir and on the baseline dir.
   It shows the facts side by side and includes the top replay ids "for Zhe to eyeball". The win count is shown but labelled "noise at 60 games (±8)".
5. Keep vs roll back: the area owner decides, plus one OK from someone else. `report` ends with that line. Nothing is automatic.

Same constraints as before:
- no keys printed;
- nothing touches the server without --confirm;
- do NOT run anything with --confirm;
- stdlib only; py_compile must pass;
- leave the changes uncommitted.
Write data/codex/report-smoke-2.md, under 25 lines.
