# Brief: approval = merge to main only; uploads move to /submit (team decision 10-04 11:10)

Repo: unsw-swarm, tools/meowbot.py. Read the candidate approval flow first (data/codex/report-approve-merge-submit.md, report-approver.md), plus battlecode docs/LOOP.md and work/loop/runner.py for card states.

## 1. Candidate OK → merge only
- When the OK rule is met (author + 1 other; AI-only: 1) and confirmed, merge the candidate PR into main and stop. No upload.
- After the merge, set the linked card(s) to status:kept with a short comment "merged to main as <sha>; ships with the next /submit".
- **Stale-base guard.** Before merging, check that the candidate PR is up to date with main, i.e. its base contains the current main HEAD (GitHub compare API: behind_by == 0).
  - If main moved, do not merge. Post: "main moved since this candidate was built; the loop is re-checking it on the new main", and add the label `needs:rebase` to the PR.
  - Keep the recorded OKs, but only for the same change: store the PR's patch-id (or the sorted diff hash of the card's own changes), and carry the OKs over only if the re-checked PR has the same patch-id. Otherwise OKs reset as now.
  - Document the runner side in the report (the runner must rebase card/N onto main, re-run identity for tasks or identity + a short A/B for ideas, and update the PR). Don't edit the runner; that is a separate job.

## 2. New /submit command (members only)
- `/submit` with an optional `ref` (default main).
- It shows ephemerally:
  - the commit;
  - the changes since the currently active submission: the list of merged candidates/cards since the last /submit, recorded in state;
  - the planned version name (next vNN after the highest existing, e.g. v62);
  - the freeze status (no new submissions after 2026-10-08 20:00 KST, only rollback).
- It posts a public card "Submit main@sha as vNN" with an OK button. It needs 2 different members, and the requester counts as one.
- When met: confirm → sync_release(that exact commit) → upload(c) through the existing UPLOAD_ENABLED gate → record the submission id + version in state → edit the card with the result.
- It refuses while our battles are pending; submit.js already checks this, so surface its message.
- `/rollback` (members only): re-activate the previous active submission (or a given id) via submit.js activate. One member is enough because it restores a known version. Confirm step, then post the result publicly. Allowed after the freeze.

## 3. Housekeeping
- Update the docstring, the footer texts and the /status view (active submission + "merged but not yet submitted: N cards").
- py_compile must pass. Add offline fake tests for:
  - the merge-only path;
  - the stale-base refusal + needs:rebase;
  - OKs carried on the same patch-id and reset on a different one;
  - /submit's 2-member rule, freeze refusal and the version name;
  - /rollback.
- Do not run, restart or kill the bot. No real gh writes or uploads. Do not commit.
Write a ≤12-line note to data/codex/report-merge-submit-split.md, including the exact runner changes needed.

## CHANGES from the team lead (override the above)
- /submit really uploads. Set UPLOAD_ENABLED = True. It only gates /submit now; candidate OKs never upload. Keep every other /submit guard: 2 different members, the freeze, pending battles, the exact commit.
- No /rollback command. Rollbacks are done by hand. Remove it from the plan, the tests and the docs.
