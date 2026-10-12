# Brief: smoke.py "pair" mode: v61 and the new bot vs the same top teams within one hour

Repo: unsw-swarm. Read tools/smoke.py, tools/test_smoke.py, tools/submit.js usage and tools/online.js help first.

The team agreed (Discord 10-04 00:57) on the following.

`python3 tools/smoke.py pair <botdir> --name <label> --opp <id,id,...|--top N> [--games 60] [--maps ...] --confirm`

1. Split the hour's unranked budget in half: about `--games/2` games for the current active bot (the rollback target, normally v61) and the same games for the new bot. Spread the games evenly over the chosen opponents; e.g. 2 teams x 15 maps each.
   - Both halves use exactly the same (team, map) list.
   - Opponents: explicit ids, or `--top N` = the N best eligible teams above us by elo (`online.js leaderboard --eligible --json`). The DEV team 545 is allowed too.
2. Order:
   a. Request the half for the current active bot. Wait until every game is finished (poll `online.js battle <id> --json`).
   b. Upload the new bot (submit.js upload --confirm). Verify it is active.
   c. Request the same (team, map) list with `--expect-active <new id>`. Wait until finished.
   d. Reactivate the rollback target (submit.js activate --confirm). Verify it.
   Never swap while any of our battles is pending.
3. Stop safely on any failure. If the new bot is active at that point, print the one-line rollback command loudly and record it in the state file. Never leave the state unknown.
4. `report <label>`: a side-by-side table per opponent, i.e. games and wins for the old vs the new bot, our longest vs their longest at the end, and how games ended.
   Run smoke_pick on both download dirs, so replay ids are there for Zhe.
   - Put a 3-line plain summary on top.
   - Label win counts as "small sample".
   - End with "keep vs roll back: author + one OK".
5. Respect the ticket estimate: refuse to start if the remaining normal allowance is below the planned total. Show the plan in `plan --pair`.
6. Block after the freeze, 2026-10-08 20:00 KST.

Constraints:
- No keys printed.
- Nothing touches the server without --confirm, and do NOT run anything with --confirm.
- Fake tests for: the order, the same list for both halves, a failure mid-way (rollback hint), the freeze, and budget refusal.
- py_compile must pass; stdlib only. Do not commit.
Write a ≤10-line note to data/codex/report-smoke-pair.md.
