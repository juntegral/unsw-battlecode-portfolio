# UNSW Battlecode 2026: Engineering Portfolio

한국어: [README.ko.md](README.ko.md)

This repository is my complete working record from UNSW Battlecode 2026, a two-week contest in which teams write
autonomous agents ("dragons", snake-like units on a wrap-around grid) that play each other on a public ladder and
then in a knockout bracket on maps nobody has seen.

My role was the engineering around the bot more than the bot itself: the test rigs, the online test harness, the
replay analysis, a Discord and GitHub collaboration environment for a team of three in three time zones, and the
loops that let AI coding agents build and test ideas while people slept. This repository collects all of it in one
place: source, design documents, the day-to-day operations record, and a seven-chapter write-up of what worked and
what did not.

It is an individual portfolio, not a mirror of the team's private repository. Where something was built with
teammates or by AI agents under my direction, it says so.

## At a glance

| | |
|---|---|
| Contest | UNSW Battlecode 2026, 2026-09-25 to 2026-10-10 |
| Teams | Solo as team 583 until 10-02, then team 1119 "meow" with Zhe and QWQ |
| My part | Infrastructure, tooling, test and analysis pipeline, AI session operations, and the switch project that produced most of the final bot's profile |
| Final bot | `one21`: one C++ file (8,657 lines) plus a profile of 49 switch values |
| Ladder | 1800 (rank 32) when the team formed, peak 2202 (rank 23), 2092 (rank 41) at the deadline, seeded 39th |
| Result | Qualified for the knockout bracket; eliminated there on 10-10 |
| Scale | 84 uploads, 21 live versions in the last 16 hours, about 9,000 local games, about 1,080 downloaded online games of the final line |

The numbers come from the timeline chapter of the write-up, which gives a source for each.

## What I built

### 1. A collaboration environment for a three-time-zone team

Three people, up to nine hours apart, sharing one bot. I connected the team's Discord channel and GitHub repository
so that work could move while its owner was offline.

- **meowbot** ([`workbench/tools/meowbot.py`](workbench/tools/meowbot.py), 2,082 lines, plus
  [`meow_chat.py`](workbench/tools/meow_chat.py), [`meow_ui.py`](workbench/tools/meow_ui.py),
  [`meow_guard.py`](workbench/tools/meow_guard.py)): a Discord bot that posts pull requests and idea cards to the
  channel, turns a slash command into a structured GitHub issue, shows the board and loop status, offers
  release candidates with approve and hold buttons restricted to team members, and answers questions in threads
  through a read-only AI session.
- **Watchers with no model in them** ([`team_watch.py`](workbench/tools/team_watch.py),
  [`discord_sync.py`](workbench/tools/discord_sync.py), [`mention_watch.py`](workbench/tools/mention_watch.py),
  [`loop_watch.py`](workbench/tools/loop_watch.py)): scripts that mirror the channel, poll GitHub, and wake a session
  only when something needs thought.
- **Offline tests** for all of it: 38 test files, 431 test functions, with fake Discord, GitHub and model calls.

Case study: [docs/case-studies/01-collaboration-environment.md](docs/case-studies/01-collaboration-environment.md)

### 2. The card loop: a GitHub-label state machine that builds and tests ideas

One GitHub issue per idea. One `status:*` label is the whole state. A runner polls the labels and calls an AI only
when a card's state needs work: clarify with the author, build behind a default-off switch, prove the build is
inert when off, let the author look at picked replays, run the outcome test, write a verdict, open a candidate
pull request. People approve; the loop never uploads.

- Specification: [`card-loop/docs/LOOP.md`](card-loop/docs/LOOP.md) (also in Chinese for a teammate),
  [`WORKFLOW.md`](card-loop/docs/WORKFLOW.md)
- Runner and job supervisor: [`card-loop/work/loop/runner.py`](card-loop/work/loop/runner.py) (1,051 lines),
  [`jobs.py`](card-loop/work/loop/jobs.py), [`guard.py`](card-loop/work/loop/guard.py),
  step prompts in [`prompts/`](card-loop/work/loop/prompts), 13 test files
- Fair queue across authors: [`card-loop/work/fair_queue.py`](card-loop/work/fair_queue.py)

Case study: [docs/case-studies/02-card-loop.md](docs/case-studies/02-card-loop.md)

### 3. Shipping discipline: default-off switches, proven by hash

Every new behaviour went behind a compile-time constant that is off by default, and the all-off build had to be
byte-identical to the previous program. That is what made 21 live versions in 16 hours possible without a crash,
a timeout or any doubt about what was live.

- Variant builder: [`local-rig/solo/tools/mkbots.py`](local-rig/solo/tools/mkbots.py)
- Upload with plan, `--confirm` and `--expect-active`: [`workbench/tools/submit.js`](workbench/tools/submit.js),
  [`smoke.py`](workbench/tools/smoke.py)
- The final bot and its profile: [`final-bot/`](final-bot)

Case study: [docs/case-studies/03-switches-proven-by-hash.md](docs/case-studies/03-switches-proven-by-hash.md)

### 4. Measurement: local rig, online harness, replay analysis

- **Local rig** ([`local-rig/`](local-rig)): deterministic game launcher with a machine-wide slot limit,
  batch runner, generated map families for unseen-map testing.
- **Online harness** ([`workbench/tools/smoke.py`](workbench/tools/smoke.py),
  [`pair_report.py`](workbench/tools/pair_report.py), [`park_watch.py`](workbench/tools/park_watch.py),
  [`weak_watch.py`](workbench/tools/weak_watch.py), [`fair_queue.py`](workbench/tools/fair_queue.py)): paired online
  tests against named opponents, a rating ratchet between two copies of the live bot, and an alarm with an analyst
  attached for any loss to a much lower-rated team.
- **Ladder study** ([`workbench/tools/ladder_*.py`](workbench/tools),
  [`workbench/data/analysis/ladder/`](workbench/data/analysis/ladder)): an hourly collector, a replay reader that
  rebuilds the true game state, and a loss classifier over every game.
- **Map generator** ([`workbench/tools/mapgen/`](workbench/tools/mapgen)): map families for held-out testing.

Case study: [docs/case-studies/04-measurement-and-noise.md](docs/case-studies/04-measurement-and-noise.md)

### 5. Running AI sessions as a workforce

Most of the code and analysis here was written by AI coding agents (Claude Code sessions, Codex workers) that I
directed. Designing that operation was a large part of the work: who decides, who thinks, who counts, what a brief
must contain, how a report gets verified, and how a session hands over to the next one after its context grows too
large.

- Handovers between six successive lead sessions: [`workbench/docs/`](workbench/docs) (`HANDOVER-*.md`,
  `SESSION-STATE.md`, `PROMISES.md`; mostly Korean)
- Standing rules, one per file, each with the incident that caused it:
  [`workbench/archive/claude-memory/`](workbench/archive/claude-memory)
- Analyst briefs and reports: [`workbench/data/codex/astra/`](workbench/data/codex/astra),
  [`workbench/archive/final-session-agent-reports/`](workbench/archive/final-session-agent-reports)
- Twelve cases where a confident report was wrong, and the checks added after each:
  [write-up chapter 05](writeup/05-ai-workforce.md)

Case study: [docs/case-studies/05-ai-workforce.md](docs/case-studies/05-ai-workforce.md)

### 6. Bots

- **First bot** ([`first-bot/`](first-bot)): the heuristic C++ bot of the solo phase, with its research notes and the
  checkpoint that ended that line ([`CHECKPOINT-2026-10-01.md`](first-bot/research/CHECKPOINT-2026-10-01.md)).
- **Lineage loop** ([`lineage-loop/`](lineage-loop)): an earlier "improve forever" loop that ran one AI session per
  wave on separate bot lineages, with its runtime tests.
- **Swarm line** ([`workbench/versions/`](workbench/versions), v0 to v1.8): a system-level redesign with a per-version
  record of hypothesis, change, pre-registered criterion and verdict; design diagrams in
  [`workbench/docs/arch/`](workbench/docs/arch).
- **Final bot** ([`final-bot/`](final-bot)): the team's bot as shipped. The base bot is QWQ's; the switches and the
  profile that turned it into `one21` come mostly from my switch project.

## The write-up

[`writeup/`](writeup) holds seven chapters written on the day the run ended. They separate what was measured from
what is interpretation, and each ends with what could not be established.

| Chapter | Question |
|---|---|
| [00 Overview](writeup/00-README.md) | The contest in ten lines, nine lessons, gaps in the record |
| [01 Playbook](writeup/01-playbook.md) | How to decide what to build, test a change, ship, and prepare for unseen maps |
| [02 Game knowledge](writeup/02-game-knowledge.md) | What decided matches, how queens died, what strong teams did |
| [03 Bot design](writeup/03-bot-design.md) | How the final bot decides a turn, every switch with its evidence |
| [04 Tools](writeup/04-tools.md) | Every script worth keeping, with command lines and traps |
| [05 AI workforce](writeup/05-ai-workforce.md) | Directing AI sessions: what worked, what failed, what it cost |
| [06 Timeline](writeup/06-timeline.md) | Day by day, hour by hour for the last night, rating history |

## What went wrong

The write-up is deliberately not a success story. The short list, from the playbook:

1. Structured testing on unseen-style maps came 13 hours before the deadline. It showed the live version losing to
   our own old bot on new maps while winning on familiar ones.
2. For eight hours of the last night, versions were judged on 15-game online sets. The same bot against the same
   opponent scored 8 of 15 and then 4 of 15 two hours apart.
3. Two harmful switches were live for three to four and a half hours because versions were compared by wins, not
   map by map.
4. The largest class of losses, falling behind in unit count in the first 150 rounds, never got a fix.
5. Ranked games requested in the last hour to improve the seed cost rating instead.

Each of these has a section with numbers in [chapter 01](writeup/01-playbook.md).

## Repository map

| Folder | Origin | What it holds |
|---|---|---|
| [`docs/`](docs) | written for this portfolio | Architecture overview and five case studies |
| [`writeup/`](writeup) | `unsw-swarm/docs/retro` | The seven-chapter write-up |
| [`workbench/`](workbench) | private repo `unsw-swarm` (383 commits) | Main workbench: tools (meowbot, online harness, ladder study, map generator), the swarm bot line, experiments, analysts' work, the operations record |
| [`card-loop/`](card-loop) | my files in the team's private repo | Card loop runner, prompts, tests, loop specification, check scripts |
| [`local-rig/`](local-rig) | private repo `meow-redteam` | Local game rig, generated maps, variant builder |
| [`final-bot/`](final-bot) | team repo, final branch | `one21` source, profile and the script that produces the uploaded source |
| [`lineage-loop/`](lineage-loop) | private repo `unsw-battlecode-2026` | Earlier lineage loop and its bots |
| [`first-bot/`](first-bot) | private repo `unsw-heuristic` (133 commits) | First bot, research notes, experiment scripts |

Each folder keeps the layout of the repository it came from, so the paths quoted in the write-up still resolve:
`S/...` in the write-up is `workbench/...` here, `R/...` is `local-rig/...`, and `B/...` is the team repository
(my part of it is in `card-loop/`, the final bot in `final-bot/`).

## What is not here

- Keys and tokens. They were never in any repository; the tools read them from files outside version control.
- The team's private chat and anything personal about teammates. Passages that quoted them were removed or
  paraphrased; Discord IDs are replaced with placeholders.
- Teammates' code, other than the final bot (shared as a team artifact, with authorship noted in
  [`final-bot/README.md`](final-bot/README.md)).
- The organisers' engine, starter code, rule text and official maps.
- Replays, logs and bulk experiment output (tens of gigabytes). Scripts, reports and small tables are kept.
- Intermediate copies of the bot source inside experiment folders. The versioned lines are kept.

## Authorship

- The team was jun (me), Zhe ([zhex0121](https://github.com/zhex0121)) and QWQ
  ([forrest-gan2005](https://github.com/forrest-gan2005)). QWQ wrote the base bot and owned the team repository.
  Zhe supplied most of the strategic reads and idea cards; his own portfolio is at
  [zhex0121/unsw-battlecode-portfolio](https://github.com/zhex0121/unsw-battlecode-portfolio).
- Files under `card-loop/` are the ones in the team repository whose every commit is mine.
- Much of the code, analysis and prose in this repository was produced by AI agents working to my briefs and
  checked by me or by a second agent. I consider the system design, the direction, the verification and the
  decisions my work, and the mistakes recorded in the write-up mine as well.
- The history of this repository starts at the point of publication. The original repositories, with their full
  histories, remain private.
