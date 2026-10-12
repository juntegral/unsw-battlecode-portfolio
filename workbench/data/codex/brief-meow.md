# Brief: /meow — a teammate you can talk to (meowbot), plus "force" on every vote

Repo: unsw-swarm, tools/meowbot.py (live bot on 준싱's Mac; edit files only, never start/stop/kill it). Read fully: tools/meowbot.py, battlecode docs/LOOP.md, battlecode work/loop/runner.py + guard.py + settings.json, tools/smoke.py, docs/PROMISES.md.
Why: team meow is spread over time zones (Zhe is 7h behind KST). Anyone should be able to move the loop forward at any hour by just talking to meowbot. "Give responsibility, then let people work freely."

## 1. /meow <message> (members only)
- It opens a Discord thread per conversation. Follow-ups in the thread continue the same session: headless `claude -p --resume <session>` per thread, session ids kept in state.
- It acks within 2 s ("👀 on it…"), then edits or replies with the answer.
- Model routing:
  - quick questions/explanations → `claude-sonnet-5-5`, effort medium;
  - anything needing actions, analysis or judgment → `opus`, effort high.
  The router is a tiny Sonnet call, or a heuristic.
- Context = the "team brain", NOT a giant transcript. Generate `data/meow/brain.md` on each call (≤ ~15k tokens) from:
  - battlecode docs/LOOP.md (short form);
  - docs/PROMISES.md;
  - ~/meow-loop-out/status.json;
  - open cards with their last result summaries;
  - the last 40 Discord messages (data/discord/*.md);
  - the latest analysis summaries (data/analysis/*.md, top sections only);
  - the memory index at ~/.claude/projects/-Users-jun-01--Project---------battlecode/memory/MEMORY.md + files, read-only.
  The session may read further files on demand.
- Read access, which Claude does directly:
  - team repo code/docs/history (battlecode checkout);
  - board/PRs (gh read);
  - loop outputs (~/meow-loop-out);
  - analyses;
  - Discord history;
  - read-only `node tools/online.js` (leaderboard, team, battles, battle, submissions, download).
  Never key/token files (docs/api.txt, docs/discord.txt, ~/Downloads/api.txt). Enforce this with a PreToolUse guard like the loop's guard.py, with its own settings file.
- Actions: Claude never executes side effects itself. It returns an ACTION PLAN, a JSON block of whitelisted actions, and meowbot executes them deterministically after the requester confirms.
  - Whitelist = everything the slash commands do: hypo, hypo-max, board-edit, answer, OK/Hold vote, submit. Plus:
    - set_state(card, state);
    - create_card(idea|task, fields);
    - comment(card, text);
    - queue_test(card, kind: mechanism|ab|pair-online);
    - use_branch_as_impl(card, branch_or_commit), which tells the runner to skip building and test that code;
    - pause_runner / resume_runner;
    - escalate(question), which posts a decision request to the team and @mentions the people needing to decide.
  - Votes and answers are always cast as the requester. Never on behalf of someone else.
- **Flexible handling:**
  - If the request maps directly to an existing command, do it right away with that command's normal confirm.
  - If it needs judgment the session can't settle, it QUEUES it: a `meow-queue` entry in state, shown in /meow queue and /status, plus an escalate post if a human must decide.
  - Don't over-plan. Let the model choose.
- Audit: every executed action leaves a line in the thread and on the GitHub card/PR: "via /meow by <name>".

## 2. Force ("강행") on top of every vote
Wherever a vote or a rule gates an action (candidate OK merge, the stale-base hold, waiting for the author's decision, skipping tests, overriding an auto-decision, pausing the runner), add a **Force** path available to ANY member:
1. Press Force (or ask /meow to force).
2. The requester confirms once, then types a one-line reason in a modal ("I take responsibility: …").
3. A final confirm.
4. meowbot executes, posts publicly "⚠️ forced by <name>: <reason>" in #meow, and comments the same on the card/PR.
- For a forced merge that touches mybot2/, queue an identity check (toggle-off vs the previous version on the old 10 maps) afterwards. It is a notification only, never a block. Post a warning if it fails.
- The existing vote logic stays for the normal path.
- Hard blocks no one can force: reading keys, ranked battle requests, deleting branches/issues, editing team rules/memory.

## 3. Housekeeping
- Two old offline checks now fail because behaviour changed: data/codex/check-approver.py and check-meowbot-states.py. Update or retire them.
- Add offline tests for:
  - the router;
  - brain.md size;
  - action-plan validation (whitelist, requester identity);
  - force flow (double confirm + reason + public notice);
  - the queue;
  - the guard blocking key files.
- Update the docstring. Write data/meow/README.md (≤40 lines) for teammates: what /meow can do, force rules, examples.
- py_compile must pass. No real Discord/GitHub/claude calls in tests. Do not commit.
Write a ≤15-line note to data/codex/report-meow.md.
