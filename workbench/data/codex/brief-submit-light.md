# Brief: make /submit light (team lead, 10-04)

Repo: unsw-swarm, tools/meowbot.py (the /submit command was just added; see data/codex/report-merge-submit-split.md).
- /submit needs only ONE member: the requester, plus the confirm step. No second OK. Keep the freeze, the pending-battle check, exact-commit upload and UPLOAD_ENABLED=True.
- Update the docstring/help/footer text and the offline tests (replace the 2-member tests with 1-member + confirm).
- Do not run, restart or kill the bot. Do not commit. Write a ≤4-line note to data/codex/report-submit-light.md.
- Narrow the stale-base guard: treat a candidate as stale only if main moved AND the commits it is behind on touch bot code (mybot2/). Use the GitHub compare API files list. Changes in docs/, work/ or tools only must not block the merge. Update the tests.
