---
name: meowbot
description: meowbot (unsw-swarm/tools/meowbot.py) runs on the user's Mac since 10-03 11:57 — posts team-repo PRs, [Idea] issues and candidate approval buttons to #meow; real uploads off until the team agrees
metadata:
  type: project
---

Started 10-03 11:57 KST at the user's request ("이대로 키게 작업을 해줘") to connect GitHub with Discord.

- Process: detached `caffeinate -is python3 tools/meowbot.py` from unsw-swarm; log `data/meowbot/meowbot.log`, state `data/meowbot/state.json` (git-ignored). Restart = kill the python pid, relaunch the same way (start_new_session). Needs `SSL_CERT_FILE=/etc/ssl/cert.pem` fallback (python.org build), already in code.
- Posts (English embeds): PR opened/reopened/merged/closed (title, 3-line summary, author, branch, file counts, link); new issues titled `[Idea] …`; candidates = JSON manifests in `candidates/` on main (version, workflow 1/2/3, changes, results{held,main,mechanism,cpu}, bot_dir, issues, pr) → embed + [Approve upload]/[Hold] buttons, only the three member IDs (준싱 900000000000000005, Zhe 900000000000000002, QWQ 900000000000000003).
- `UPLOAD_ENABLED = False`: approve shows a mock message. Turn on only after QWQ agrees to the approve-button flow; real path fetches `~/meow-release` (worktree of origin/main, not created yet) and runs `tools/submit.js upload <bot_dir> --name <version> --confirm`.
- Slash commands (synced 10-03 12:09, members only): `/hypo <area>` modal → [Idea] issue (Korean/Chinese translated by Sonnet 5.5 medium, original kept in a <details> block); `/hypo-max <area>` → Opus high read-only analysis in ~/meow-release (main checkout) + ~/meow-loop ladder data, card with code pointers/prior attempts/ladder evidence/overlap/toggle/test plan; `/board` ephemeral list of open [Idea] issues with status untested/in-progress, indexed by issue number; `/board-edit <number>` prefilled modal → edits the four card sections + comment.
- 10-03 12:25 added `/loop` (all loops from pinned issue #12 "Loop status" + queue + latest [test]/[check] comments), `/status` (ladder active bot/rating via online.js, open PRs, merges in 24h, idea counts, loops), `/board` header (running loops, loop:ready queue, untested); push notices for verdict labels (status:tested/rejected/inconclusive on [Idea] issues). New ideas get `wf:1` if author is Zhe else `wf:2`.
- Board protocol (labels created 10-03): `loop:ready` queue, `loop:running` lock, `wf:1/2/3`, `status:inconclusive`; loops use `work/board.py` (juntegral branch, PR #8): next / claim / report (posts [test]/[check] with base commit, sets status) / heartbeat (edits the JSON block in #12) / ready.
- Restart: SIGTERM is ignored by discord.py here — use `kill -9` on the old python + caffeinate, or two bots will double-post.
- Buttons need the bot online (Discord 3-second rule); if the Mac is off, clicks fail until it is back.

Related: [[meow-team-repo]], [[upload-only-rule]], [[github-english]].

10-04: /meow being built: talk-to-meowbot teammate (threads, Sonnet/Opus routing, team-brain context, whitelisted action plans executed by meowbot after the requester confirms). Every vote gets a Force path for any member: double confirm + reason + public "⚠️ forced by X". Purpose: Zhe's time zone; responsibility instead of gates.

10-04 22:50: GitHub events feed: IssuesEvent payload.label is unreliable (named name:* instead of the status label that changed). meowbot now reads the status from payload.issue.labels. Symptom was: no state pings at all after name:* labels were added. Also big look replays (14 MB) are gzipped and sent one per message.
