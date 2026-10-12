# Brief: PR notifications missed — stop relying on the repo events feed for PRs

Repo: unsw-swarm. Files: tools/meowbot.py (new_events, PR posts, candidate detection) and tools/team_watch.py (PR section, `--prs` mode).
Bug: PR #26 was opened on 2026-10-04 07:02Z in forrest-gan2005/battlecode and nobody was told. `gh api repos/<repo>/events` returned no PullRequestEvent at all for this private repo (not for #19, #20 or #26), only Issues/IssueComment/Push events. Both tools read PR activity from that feed.

Fix, in both tools:
- Get PR activity from the PR list itself: `gh pr list --repo <repo> --state all --limit 30 --json number,title,state,isDraft,author,headRefName,headRefOid,updatedAt,mergedAt,closedAt,url` (or the REST pulls endpoint).
  Keep a small per-PR snapshot in state (state, draft flag, head SHA) and emit:
  - opened: a number not seen before;
  - reopened;
  - merged;
  - closed;
  - ready-for-review;
  - new commits pushed (head SHA changed; only for team_watch, where meowbot keeps its existing candidate-reset behaviour).
- First run after this change: seed the snapshot silently. Do not replay history. EXCEPT post PR #26 once if it is still open and was never posted (state has no record of it); it is the one we missed.
- meowbot: keep the same embeds/cards as before for opened/merged/closed. Add a mention line when the PR body or a Discord message requests a specific member's review? No, keep it simple: the opened post just @mentions nobody. Do not double-post if the events feed later delivers the same PR event (dedupe by PR number + action).
- team_watch: the normal turn check and `--prs` both use the new source. The output format stays "- <time> <who>: PR #N opened/merged/… <title>".
- Offline fake tests for: the first-run seed, open/merge/close detection, the head change, dedupe, and the one-time #26 catch-up. py_compile must pass.
- Do not run, restart or kill the bot. Do not commit. No real posts.
Write a ≤6-line note to data/codex/report-pr-poll.md.
