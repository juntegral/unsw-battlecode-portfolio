---
name: discord-first
description: user core rule 10-03 — sync and read #meow Discord at the start of every task; also in battlecode/CLAUDE.local.md
metadata:
  type: feedback
---

Before starting any task, run `python3 tools/discord_sync.py` in unsw-swarm and read the new #meow messages, then proceed.

**Why:** 10-03 the user made it a top principle ("대원칙") — we move as one team, so teammates' latest posts must shape every step.

**How to apply:** first tool call of each task = `python3 tools/team_watch.py` in unsw-swarm (Discord + GitHub team repo activity, added 10-03 when the user asked to track both). Do NOT wake on every Discord message (user 10-03: too many tokens) — read Discord only when the user speaks. Background: only `team_watch.py --prs --wait 86400` (PR changes, which touch the environment); report only when it catches a PR change, silently re-arm on timeout. Also report lightly/casually in Korean, not stiff report style (same day). Written into `battlecode/CLAUDE.local.md` (git-excluded). Related: [[check-in-first]], [[meow-team-repo]].
