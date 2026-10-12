# Brief: meowbot one-button "approve = merge to main + submit"

Repo: this directory (unsw-swarm). File: tools/meowbot.py. Read it fully first.

## Goal
Today a candidate manifest must already be on main (candidates/*.json) before meowbot posts an [Approve upload] button.
New flow, from the team's decision: one button does both steps.

1. Detection: meowbot watches OPEN PRs in forrest-gan2005/battlecode whose changed files include `candidates/*.json`.
   For each such PR, which it has not posted yet (keep state in data/meowbot/state.json):
   - read the manifest from the PR head;
   - post the candidate card (reuse the existing card code);
   - add a PR link and buttons [Approve: merge + submit] / [Hold].
   Keep the old on-main detection only if it is needed to avoid breaking the state file; otherwise replace it.
2. On [Approve: merge + submit], for MEMBERS only:
   a. Show an ephemeral confirm ("Merge PR #N into main and submit <version>?") with Confirm/Cancel.
   b. Take a lock so only one approval runs at a time, and ignore double clicks.
   c. Check that the PR is still open and mergeable and that its head SHA equals the SHA the card was posted for.
      If the head changed, refuse and repost the card.
   d. Merge with `gh pr merge N --repo forrest-gan2005/battlecode --merge`.
   e. Run the existing upload(c) after sync_release() (it already checks out origin/main into ~/meow-release).
      Keep the UPLOAD_ENABLED gate exactly as it is: when False, the merge happens for real but the submit stays mocked, and the message says so.
   f. Edit the card: who approved, the merge commit, and the upload result. Disable the buttons.
3. [Hold]: unchanged (mark held, who held).
4. Update the module docstring and the footer text to describe the new flow.

## Constraints
- Never print, log or echo the contents of docs/discord.txt, docs/api.txt or any token.
- Do not start, restart or kill the running meowbot process. Do not run the bot; it posts to a live Discord.
- Do not push, do not run submit.js, do not merge anything. Only the code changes.
- Use `--preview-candidate` / `--preview-pr` style offline checks only. Add a `--preview-candidate-pr N` that prints how the card for PR N would look (gh read-only calls are fine).
- Keep the style of the file: short comments, same helpers (gh(), embeds), English text.
- `python3 -m py_compile tools/meowbot.py` must pass.

## Output
- Leave the changes uncommitted in the working tree.
- Write a summary to data/codex/report-approve-merge-submit.md, under 40 lines, covering:
  - what changed, with function names;
  - how the state file changes;
  - what you tested offline;
  - any open risks.
