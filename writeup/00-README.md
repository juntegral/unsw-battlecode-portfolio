# Contest write-up: UNSW Battlecode-style contest 2026, team meow (1119)

> **Reading this in the public portfolio.** These chapters were written for the private project archive and are
> published with personal details and private chat removed. Paths are quoted as they were in the original
> repositories: `S/...` (or a bare `tools/...`, `docs/...`, `data/...`, `archive/...`) is [`workbench/`](../workbench)
> here, `R/...` is [`local-rig/`](../local-rig), and `B/...` is the team's private repository, of which my files are
> in [`card-loop/`](../card-loop) and the final bot in [`final-bot/`](../final-bot). This folder itself was
> `docs/retro/`. Some cited sources (the channel mirror, replays, bulk data, a few private notes) are not published.

Written 2026-10-10, the day the team's run ended. This folder is the part of the project meant to be read again: what
we learnt that would help in the next bot-programming contest, and a map of where everything else is kept.

## The contest in ten lines

- Two teams of snake-like units ("dragons") on a wrap-around grid. They eat pearls to grow and split to multiply.
  A head-on ram kills both dragons whatever their lengths. Each dragon sees only nearby cells. 500 rounds.
- From the rule change of 2026-10-01 the team with the longer **queen** (its lowest-numbered dragon) wins; a dead queen
  counts as zero. Then longest dragon, then total length.
- A public ladder with a rating led to a qualifier played as single-elimination series on maps nobody had seen.
  Submissions closed 2026-10-09 15:00 KST.
- jun worked first in another team (583) with his own bot, then from 10-02 in team meow with Zhe and QWQ, seven days
  before the deadline. jun ran the tools, the tests and the AI sessions; the base bot was QWQ's; Zhe supplied most of
  the strategic reads.
- The final bot is "one21" (submission 21857, uploaded 14:49 on the last day): one C++ file with 49 switch values.
  At the deadline it was rated 2092, rank 41; jun reported a final seed of 39.
- The team was knocked out on 2026-10-10. jun reports a quarterfinal exit; the bracket, the opponent and the scores
  are not in any file here (see "Gaps" below).

## Chapters

| File | What it answers | Start here if |
|---|---|---|
| [01-playbook.md](01-playbook.md) | How to decide what to build, test a change, ship, and prepare for unseen maps; what cost us most; a day-one checklist. | you are starting a new contest |
| [02-game-knowledge.md](02-game-knowledge.md) | The rules as we understood them, what decided matches, how queens died, what strong teams did, map families, opponent types, open problems. | you want the findings about this game |
| [03-bot-design.md](03-bot-design.md) | How the final bot decides a turn, every switch in the final profile with its evidence, dropped candidates, version history, known weak points with code locations. | you will read or continue the bot |
| [04-tools.md](04-tools.md) | The scripts worth keeping, grouped by job, with the command lines as used and the traps. | you need to rebuild the tooling |
| [05-ai-workforce.md](05-ai-workforce.md) | How the AI sessions, analysts and the build loop were directed; briefs that worked; confident reports that were wrong; incidents; a recommended setup. | you will run AI workers again |
| [06-timeline.md](06-timeline.md) | Day by day from 09-25, hour by hour for the last night, rating history, rule changes. | you need a date or a number |

Each chapter marks what was measured and what is the writer's reading, and ends with what it looked for and could not
establish. The chapters were written by separate AI writers from the project record and were checked by the lead
session for the points it could check; where two chapters disagree, the timeline's tables and the corrected entries in
`docs/SESSION-STATE.md` are the reference.

## If you read only this page

1. **Test on maps you have not seen from the first week.** The qualifier used unseen maps. Our first structured run
   on freshly generated maps came 13 hours before the deadline and showed the live version losing to our own old bot
   there while winning on the familiar maps (playbook, section 1 and section 5).
2. **Know the noise of each instrument before deciding with it.** The same bot against the same opponent scored 8 of
   15 and then 4 of 15 two hours apart. Eight switches turned on during the last night on such sets were turned off
   again (playbook T1 to T3 and its appendix).
3. **Read health numbers per map and per version, not only wins.** A table of pearls and dragons at round 50 and 100
   and the queen's death round found two harmful switches within an hour each, after hours of win counts had found
   nothing (playbook T5).
4. **Put every new behaviour behind a switch that is off by default, and prove identity by hash.** All switches off
   had to give the old program byte for byte, and the new source with the old values had to give the live binary.
   This is what made 21 versions in 16 hours possible without a broken upload (playbook B1, tools section 3).
5. **A finished diagnosis names a counted behaviour, the code line and a board that reproduces it.** Fixes built on a
   count alone mostly did not survive (playbook D2).
6. **In this game the queen's survival decided matches, and the economy of rounds 20 to 100 decided the queen's
   chances.** Our queen was dead in 243 of 266 losses; with our queen alive and theirs dead we won 65 of 65
   (game knowledge, section on what decides a match). We spent the last hours on queen rules and never fixed the
   early gap in dragon count, which was the larger class of losses (playbook, what cost us most, row 4).
7. **A worker's confident report is a lead until checked.** Twelve cases are listed where a report or belief was
   wrong, three of which reached the live bot (AI workforce, verification section).
8. **Scripts wait, models think.** Long waits, polling and queues belong in scripts; a model is called for a short
   step with a written brief and a fixed report format (AI workforce, division of labour).
9. **Write the state down as you go.** The session-state memo, the handovers and the promises ledger are why six
   successive sessions could each resume, and why this write-up could be made at all.

## Where everything is

| What | Where |
|---|---|
| The final bot as shipped | Team repo `forrest-gan2005/battlecode`, branch `one15-profile` (pull request 62): `mybot2/main.cpp` + `work/server_profile.txt`. `python3 work/server_bot.py OUT --no-compile` gives the uploaded source. |
| Every uploaded bot folder | This repo, `data/online/smoke/*-bot/` with `versions.tsv` (submission id to name) and `data/online/submissions.jsonl`. |
| The local game rig, maps, the bot's source stages, every test build's source | Private repo `juntegral/meow-redteam`, branch `archive`. Start at its `ARCHIVE.md`. |
| Tools | This repo, `tools/`; analysis scripts in `data/analysis/ladder/dossier/work/` and in each analyst's folder under `data/codex/astra/`. |
| Analysts' reports | `data/codex/astra/<analyst>/` (reports, scripts, tables) and `archive/final-session-agent-reports/` (reports that were sent only as messages during the last session, one file per analyst). |
| The running log, handovers, promises | `docs/SESSION-STATE.md`, `docs/HANDOVER-*.md`, `docs/PROMISES.md`, `DECISIONS.md`, `docs/STATE.md` (the earlier team phase). Mostly Korean. |
| Notices posted to the team channel | `data/guide/`. The channel mirror is not published. |
| The last session's scripts and switch lists | `archive/final-session-scripts/` (`one14.switches` to `one21.switches`, `up14.zsh` to `up21.zsh`, the check and battle scripts). |
| The standing rules given to the AI sessions | `archive/claude-memory/` (one rule per file, each with why and how to apply; a few private ones are not published). |
| Leftover local work in the team repo's worktrees | Team repo, branches `archive/local-1010/*` (snapshots, not for merge). |
| jun's earlier repos | `juntegral/unsw-battlecode-2026`, `juntegral/unsw-heuristic` (private). |

### Bulk data (not in git)

`data/` is ignored by this repo's `.gitignore`; the text part of it was added by hand in the wrap-up commit. Replays,
per-game json and derived tables are attached to the release **`data-2026-10-10`** of this repo as `tar.xz` archives
split into parts of at most 1.9 GB, with `SHA256SUMS.txt`.

| Archive | Restores to | Holds |
|---|---|---|
| `online-live-one1` | `data/online/live-one1/` | our online games from version one1 on (about 1,080 replays) |
| `online-smoke` | `data/online/smoke/` | online test sets of every earlier version, with per-game json |
| `online-ladder` | `data/online/ladder/` | ladder games collected for the ladder study |
| `online-top1`, `online-top3` | `data/online/top1/`, `top3/` | games of the top-ranked teams |
| `online-dl-20261003`, `online-dl-20261004` | `data/online/dl-*/` | early downloads |
| `local` | `data/local/` | replays and tables of three local studies |
| `analysis` | `data/analysis/` | derived tables of the ladder and top-team studies |
| `codex` | `data/codex/` | analysts' derived data and worker logs |

To restore one: download its parts, then run `cat online-top1.tar.xz.part-* | xz -d | tar -xf -` inside
`data/online/` (for the `online-*` archives) or inside `data/` (for `local`, `analysis`, `codex`).

### What was not kept

- Replays and engine logs of local games (`~/meow-redteam/solo/runs`, about 55 GB). Local games are deterministic:
  the same bots, map and seed give the same game. The result line of every local game is in
  `meow-redteam/solo/runs-results.tar.xz`.
- Compiled test bots and the engine install; both can be rebuilt.
- The server key and the channel token. They were never in any repo.

## Gaps in the record

- **The bracket.** Which round ended the run, the opponent, the maps and the scores are not in the files. The channel
  mirror has no message between the evening of 10-09 and the afternoon of 10-10. jun's statement (quarterfinal exit)
  is the only source.
- **The last three versions were never checked online.** No game of one19, one20 or one21 had been downloaded by the
  deadline; they were shipped on local checks ("plays the same games as the version before") and code review.
- **A scene flagged by jun and Zhe at the end** (game 1532570, round 469, our side) was not traced.
- **Who activated an older version on the server at 04:34 on 10-09** is not known; none of our tools did.
- Each chapter's last section lists more.
