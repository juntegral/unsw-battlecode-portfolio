---
name: meow-team-repo
description: "New team 1119 \"meow\" works in github.com/forrest-gan2005/battlecode (C-- = QWQ), cloned to 개인 프로젝트/battlecode; gh + key wiring done 10-02; Discord sharing pending"
metadata:
  node_type: memory
  type: project
  originSessionId: 33c2c5f9-3e6b-4223-83b1-8f982a6609b6
  modified: 2026-10-02T14:56:40.235Z
---

On 2026-10-02 at about 23:00 KST the user said they moved to team **1119 "meow"** (3 members, including the user and QWQ).
- The new main repo is the private **https://github.com/forrest-gan2005/battlecode** (the user has WRITE). Its README title is "C-- Battlecode bot", so QWQ = C--. This repo is the "C-- core code" the user promised.
- It is cloned to `~/01. Project/개인 프로젝트/battlecode`. At clone time `main` and `qualifiers` pointed to the same commit (26d6d2e).
- Team conventions live in its README. In short: bot changes go behind `constexpr` toggles that are off by default, no comments in bot code, no per-map hardcoding, and every ladder submission is tagged.
- The team's scripts fetch replays from the public `api/matches/{id}/replay` endpoint without a key.

**What was wired up:**
- `gh` is logged in as juntegral (keyring). `gh auth setup-git` was run, and the repo's gh default is set to forrest-gan2005/battlecode.
- The team 1119 API key is kept in a git-excluded local file that the tools read.
- `unsw-swarm/tools/online.js` now has `OUR_TEAM=1119`. This change is not committed.

**User direction (10-02):**
- The new repo comes first.
- The old repos (unsw-arena, unsw-heuristic, unsw-swarm) may be tidied up.
- The user wants to keep sharing the 3-person Discord team chat with Claude. On 10-02 they made a new server channel for it.
  - The mirror is `unsw-swarm/tools/discord_sync.py`, pushed and tested offline.
  - The bot token goes in `unsw-swarm/docs/discord.txt` (git-excluded). The channel id is passed once with `--channel` and remembered in `data/discord/channel.txt`. The readable log is `data/discord/<channel>.md` (git-ignored).
  - **Connected 10-02 ~23:55 KST:** server "meow", channel #meow (id 900000000000000004), bot "meowbot".
    - Members seen: 준싱 (the user), QWQ (writes as the bot developer) and Zhe.
    - This Mac's python.org Python 3.13 has no CA bundle, so the script falls back to `/etc/ssl/cert.pem`.
    - Text attachments (Discord turns long posts into `message.txt`) are saved to `data/discord/files/` and inlined in the log.
  - **QWQ's 10-02 23:28 post lists the bot's 7 main problems:**
    1. the queen dies on big maps (all 15 Australia/Islands ladder games lost);
    2. terrain traps;
    3. weak late-game feeding;
    4. dragons stuck at home on corridor maps;
    5. early accidents on small maps;
    6. local tests that don't match the ladder;
    7. CPU headroom (55–66M of 100M).
    - It also says the engine is now 1.2.7 and the maps were updated on 10-02, while local runs still use 1.2.3.
    - Read it in the log before planning.
  - Whenever the user mentions Discord, run the sync first and then read the new messages.

**Branch workflow (10-03):** the user works on a personal branch `juntegral` (created locally from main 26d6d2e, not pushed yet) and sends improvements in their area to `main` as PRs. Roles are not pre-assigned; the user proposed direction-only (area ownership by code subsystem, PR flow, shared A/B protocol) on Discord.

**How to apply:** do new-team work in this repo and follow its README. The team already has a bot live on the ladder, so never upload without the team's agreement.

Related: [[team-change]], [[upload-only-rule]], [[qualifier-timeline]], [[claude-usage-budget]].
