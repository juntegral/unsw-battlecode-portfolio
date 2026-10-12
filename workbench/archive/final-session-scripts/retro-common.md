# Common brief for the wrap-up writers (2026-10-10)

## Situation

The UNSW Battlecode-style contest is over. Team "meow" (team 1119: jun, Zhe, QWQ) submitted its final bot "one21" at
the qualifier deadline on 2026-10-09 15:00 KST and, by jun's account, was knocked out in the quarterfinal on 2026-10-10.
jun has asked for the material that helped in this contest to be kept so that it is useful in the next bot-programming
contest. You are writing one chapter of that knowledge base.

The reader is jun some months from now, a new teammate, or a new AI session. Assume they are capable and have none of
this project's context: they do not know our version names, switch names, folder layout or the game's rules.

## Where things are (read-only for you)

- `S` = `~/01. Project/개인 프로젝트/unsw-swarm` (jun's private repo: tools, docs, analysis).
  - `S/docs/SESSION-STATE.md` is the chronological log of the last days (long, Korean; grep and read in pieces).
  - `S/docs/HANDOVER-*.md`, `S/docs/STATE.md`, `S/DECISIONS.md`, `S/docs/PROMISES.md`, `S/docs/DISCORD-DESK.md`.
  - `S/data/codex/astra/` holds the analysts' output, one folder per analyst, and `CARDS.md`, `CLAUDE-COMMON.md`,
    `UNSEEN-BRIEF.md`, `OPPONENT-BRIEF.md`. `S/data/codex/brief-*.md` are the briefs given to Codex workers.
  - `S/data/analysis/` holds ladder and top-team studies, `S/data/online/smoke/` the uploaded bot folders and
    `versions.tsv`, `S/data/guide/` the notices posted to the team channel, `S/data/discord/` the channel mirror.
  - `S/archive/final-session-scripts/` (scripts and switch lists of the last session), `S/archive/claude-memory/`
    (the standing rules jun gave over the contest, one per file), `S/archive/claude-rules/CLAUDE.local.md`.
- `B` = `~/01. Project/개인 프로젝트/battlecode/.claude/worktrees/one13-into-main` (team repo, branch
  with the final bot: `mybot2/main.cpp`, `work/server_profile.txt`, `work/loop/`, `work/server_bot.py`).
- `R` = `~/meow-redteam` (local game rig: `play.sh`, `engine/`, `maps/`, `solo/src/`, `solo/tools/`).

Never open `S/docs/api.txt` or `S/docs/discord.txt` (keys). Do not copy any key, token or webhook address into your file.

## Rules

- Write only your one output file (given in your task) and, if you need scratch files, a folder
  `S/data/retro-work/<your-name>/`. Change nothing else. No git commands that change anything, no games, no uploads,
  no messages to Discord or GitHub, no network.
- English. Call the user "jun". Plain words; explain a project term the first time it appears, or avoid it.
- Lead each section with the lesson or the answer, then give the evidence: what happened, the date, the number, and the
  file it comes from (path relative to `S`, `B` or `R`).
- Mark what was measured and what is your reading of it. Never invent a number, a date or a cause. If the record does
  not say, write "not recorded". The log contains corrections of earlier statements; use the corrected version.
- Include what failed, what cost us, and what was never proven. This is a working reference, not a celebration.
- Write for reuse: say what to do next time and why, and what the lesson depends on, so the reader can tell whether it
  transfers to a different game.
- Prefer a table when comparing several things on the same attributes; prose for reasoning. Aim for 250 to 500 lines.
- When you are done, reply with the path of your file, a five-line summary of what it contains, and a list of what you
  looked for and could not establish.
