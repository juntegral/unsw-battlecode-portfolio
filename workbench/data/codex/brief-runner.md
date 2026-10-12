# Brief: the loop runner (work/loop/) for docs/LOOP.md

Repo: battlecode, branch juntegral. Read these first:
- docs/LOOP.md (the spec, authoritative);
- work/board.py (just updated: next/state/report/ask/heartbeat/migrate);
- work/ab2.py, work/ab3.py, work/ident.py, work/feedcheck.py;
- the old overnight runner, as a pattern only: ~/meow-loop/loop/runner.py, PROMPT.md, guard.py, settings.json.

Build work/loop/:
- runner.py, prompts/*.md, guard.py, settings.json;
- a README section in docs/LOOP.md ("Running the loop"), ≤25 lines.

## Runner (python3 stdlib, no AI tokens itself)
- Polls GitHub every 3 min (via board.py / gh) and acts per card state. All decisions come from labels and card comments, plus a local out dir `~/meow-loop-out/card-N/` (batch pids, results, replays, base commit).
- Safe to kill and restart at any point, and resumes correctly.
- Global lock: one game batch at a time on this Mac. AI steps for other cards may run while a batch runs, but at most one AI step at a time.
- AI step = headless Claude:
  `claude -p --model opus --effort high --permission-mode bypassPermissions --settings work/loop/settings.json --output-format stream-json --verbose`
  The prompt comes from prompts/<step>.md filled with the card number, title, body, comments, base commit and paths.
  The working dir is a per-card git worktree `~/meow-cards/card-N` on branch `card/N`, made from origin/main.
  Log to `~/meow-loop-out/card-N/<step>-<time>.jsonl`. Timeout 60 min.
- Light steps (classifying a human reply, formatting) use
  `claude -p --model claude-sonnet-5-5 --effort medium --tools "" --no-session-persistence`.

## States (see LOOP.md for the full table)
- ready
  - Zhe cards always, and others if unclear: AI step `clarify` writes edge-case questions, then `board.py ask`.
  - Otherwise: state building.
- needs-info: wait for a human comment after the questions comment. Once there is one, go to building. Answers may be in Korean, English or Chinese.
- building: AI step `build`.
  1. Implement a default-off toggle in mybot2/main.cpp.
  2. Build.
  3. Run `ident.py` against the base on the old 10 maps (IDENT_MAPS, IDENT_SEEDS=2).
  4. Write a mechanism check for the card's expected behaviour (reuse feedcheck/splitcheck style).
  5. Commit on card/N.
  The runner pushes `card/N` (the only push it does). On ident failure, go back to ready with a note.
  Then the runner launches the small mechanism run (KEEP=1, ~16–32 games on maps where the behaviour should show) and runs the check. The AI step `look` picks the 2–3 most telling replays, writes `~/meow-loop-out/card-N/look.json` ({"replays":[paths], "note": "..."}) and a short card comment, then the state becomes needs-look.
- needs-look
  - by:zhe: wait for Zhe's reply. A light step classifies it as ok / revise. Revise goes back to building with the reply as input.
  - Others: auto-pass to testing.
- testing: the runner launches the outcome A/B (one batch at a time).
  - Sets: work/heldset_sq.txt + work/freshset.txt (held), their _T versions (transposed), old 10 maps x8.
  - Command: ab3 with SEED0 fixed per card, KEEP off, WORKERS=8.
  - Base = origin/main bot built from the base commit; candidate = card/N with the toggle on.
  When it finishes, the AI step `verdict` writes the result comment:
  - the 3-line plain summary first (tried / worked? / who decides);
  - the "why" table: our longest vs their longest at the end (ab3 rows: us/them), total length if available, results by map family;
  - paired flips per set.
  Then `board.py report --state tested`. If the base changed during the run, mark it "old base".
- tested / candidate / smoke: people act. The runner only:
  - for a card the author moved to candidate: creates `candidates/<version>.json` (CANDIDATE_FIELDS from unsw-swarm/tools/meowbot.py) on a branch `candidate/<version>` that turns the toggle on;
  - opens the PR (`gh pr create`);
  - blocks this after the freeze, 2026-10-08 20:00 KST.
- Track 3, every 4 h: AI step `ladder`.
  1. Read our latest ladder games: read-only `node ~/01. Project/개인 프로젝트/unsw-swarm/tools/online.js battles --json` and `download`, which cost no tickets.
  2. Write at most 2 cards labelled by:ai, status:ready, using the Idea template fields.
  3. Skip the step if there are no new games.

## Guard (settings.json PreToolUse hook → guard.py) blocks the AI from:
- git push (the runner pushes, not the AI);
- gh pr merge, gh pr create, any gh write except `board.py` itself;
- submit.js, online.js request/activate, any `--confirm`;
- reading docs/api.txt or docs/discord.txt;
- editing work/loop/ itself.

## Also
- `runner.py --once` (single tick) and `--dry-run` (print planned actions, no gh writes, no AI calls).
- Status file `~/meow-loop-out/status.json` (Korean labels are fine there; it is local only). Heartbeat to the Loop status issue as loop name `card-loop`.
- Prompts: English, short, each says what to output and where. Every GitHub-facing text uses the plain summary first, casual teammate tone, no unexplained jargon.
- python3 -m py_compile on all files. Test with --dry-run against fake gh data (the sandbox has no network).
- Do not run real AI calls, games, pushes or GitHub writes. Do not commit.
- ≤20-line note to ~/01. Project/개인 프로젝트/unsw-swarm/data/codex/report-runner.md.
