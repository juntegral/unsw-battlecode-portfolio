---
name: discord-desk
description: user idea 10-09 00:5x — a separate Sonnet session "meow-desk" handles #meow conversation and passes work to the main session through a file inbox; main no longer runs the mention watcher
metadata:
  type: project
---

User, 2026-10-09 ~00:52 KST: handling teammates' conversation in the big main session costs too many tokens; open a separate Sonnet Discord session that does the Discord talk and only monitors the main work.

Set up the same hour: background session `meow-desk` (first id 6e5fd399; `claude --bg --name meow-desk --model sonnet --permission-mode auto`, cwd battlecode), rules in `unsw-swarm/docs/DISCORD-DESK.md`. It runs `mention_watch.py` and `jun_dm.py --watch`, answers questions from the state files, and for any request that needs work appends one line to `unsw-swarm/data/guide/desk-inbox.txt`; the main session watches that file, does the work and posts results itself.

**Why:** main-session context was about 700k tokens, so every Discord wake-up re-read all of it; weekly limit was at 17% ([[claude-usage-budget]]).

**How to apply:** in a main-session handover say that the desk owns the mention and jun-DM watchers (do not start them in main), start an inbox watcher instead, and keep `docs/SESSION-STATE.md` current because the desk answers from it. If the desk is gone (`claude agents --json`), start it again with the same command. Related: [[handover-semi-auto]], [[bot-speaks-when-mentioned]].
