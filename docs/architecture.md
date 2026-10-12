# Architecture overview

Three systems carried the work. This page shows how each was put together and where its source is.

## 1. The collaboration environment

Three people shared one bot from three time zones, up to nine hours apart. The design goal was that nobody had to be
awake for someone else's work to move, and that every decision stayed with a person.

```mermaid
flowchart LR
  subgraph people [People]
    Z[Zhe]
    Q[QWQ]
    J[jun]
  end
  D[(Discord channel)]
  G[(GitHub team repo<br/>issues = cards, pull requests)]
  M[meowbot]
  W[Watchers<br/>no model]
  L[Card loop runner]
  A[AI sessions<br/>lead, desk, workers]
  S[(Contest server)]

  Z & Q & J <--> D
  D <-- slash commands, buttons, threads --> M
  M <-- issues, labels, PR events --> G
  L -- polls labels, posts results --> G
  L -- starts a session only when a card needs work --> A
  W -- mirror channel, poll PRs --> D & G
  W -- wake on mention or PR change --> A
  A -- briefs, verdicts, notices --> M
  A -- upload after human approval --> S
  S -- replays, rating --> W
```

| Piece | Source | Job |
|---|---|---|
| meowbot | [`workbench/tools/meowbot.py`](../workbench/tools/meowbot.py) | Posts PRs and idea cards, ten slash commands (`/hypo`, `/hypo-max`, `/board`, `/board-edit`, `/task`, `/loop`, `/status`, `/answer`, `/submit`, `/meow`), candidate approval buttons limited to members |
| Chat session | [`meow_chat.py`](../workbench/tools/meow_chat.py), [`meow_guard.py`](../workbench/tools/meow_guard.py) | A read-only AI session per thread behind a fail-closed tool policy; any action is a plan the requester must confirm |
| Channel mirror | [`discord_sync.py`](../workbench/tools/discord_sync.py) | Mirrors the channel to local files so sessions read text, not an API |
| Team watch | [`team_watch.py`](../workbench/tools/team_watch.py) | New messages plus new GitHub events; first action of every working turn |
| Wake-up watchers | [`mention_watch.py`](../workbench/tools/mention_watch.py), [`loop_watch.py`](../workbench/tools/loop_watch.py), [`jun_dm.py`](../workbench/tools/jun_dm.py) | Exit when something needs a model; cost nothing while waiting |
| Nudges | [`decision_nudge.py`](../workbench/tools/decision_nudge.py), [`snooze.py`](../workbench/tools/snooze.py), [`tasks.py`](../workbench/tools/tasks.py) | Remind a card's author within their configured hours; snooze; per-person task list |
| Desk session | [`workbench/docs/DISCORD-DESK.md`](../workbench/docs/DISCORD-DESK.md) | A cheap model session that owns channel talk and passes work to the lead through a file |

Design rules that held:

- **Scripts wait, models think.** Polling, queues and long waits never run inside a model session.
- **People approve, tools execute.** Uploads and merges need a member's click; every vote has a visible force path
  with a reason, so a sleeping teammate cannot block the others and responsibility stays explicit.
- **Everything spends through a plan.** A tool that uses a scarce resource (test tickets, uploads, the live bot)
  prints its plan and does nothing without `--confirm`, and refuses when the live bot is not the expected one.

## 2. The card loop

One GitHub issue per idea. Exactly one `status:*` label is the card's state, so the runner can resume from the label
alone after a restart.

```mermaid
stateDiagram-v2
  [*] --> untested
  untested --> ready: team agrees to run it
  ready --> needs_info: unclear, or author wants questions
  needs_info --> building: author or a teammate answers
  ready --> building
  building --> needs_look: build passes and is replay-identical with the switch off
  building --> ready: build or identity check fails
  needs_look --> building: "not what I meant"
  needs_look --> testing: author confirms the behaviour on picked replays
  testing --> tested: outcome A/B posted with a why-table
  tested --> candidate: author decides
  tested --> rejected
  tested --> inconclusive
  candidate --> smoke: approvals, merge, upload of that exact commit
  candidate --> kept
  smoke --> kept
  smoke --> rejected
  kept --> [*]
  rejected --> [*]
  inconclusive --> [*]
```

| Piece | Source |
|---|---|
| Specification | [`card-loop/docs/LOOP.md`](../card-loop/docs/LOOP.md), [`WORKFLOW.md`](../card-loop/docs/WORKFLOW.md) |
| Runner | [`card-loop/work/loop/runner.py`](../card-loop/work/loop/runner.py) |
| Detached job supervisor with leases | [`card-loop/work/loop/jobs.py`](../card-loop/work/loop/jobs.py) |
| Hook that restricts what a card session may do | [`card-loop/work/loop/guard.py`](../card-loop/work/loop/guard.py) |
| Prompts per step | [`card-loop/work/loop/prompts/`](../card-loop/work/loop/prompts) |
| Board commands | [`card-loop/work/board.py`](../card-loop/work/board.py) |
| Fair rotation across authors | [`card-loop/work/fair_queue.py`](../card-loop/work/fair_queue.py) |
| Per-card completion checks | `card-loop/work/card_*_check.py` |

## 3. Build, test, ship

```mermaid
flowchart TD
  I[Idea or loss analysis] --> SW[New switch, off by default]
  SW --> ID{All-off binary hash<br/>equals the old program?}
  ID -- no --> SW
  ID -- yes --> MECH[Count the behaviour in local games]
  MECH --> H2H[Local head-to-head on known and generated maps]
  H2H --> PROF[Profile = list of switch values]
  PROF --> UP[Upload with plan, confirm, expected active id]
  UP --> VER[Verify server copy and active id]
  VER --> HEALTH[Per-map, per-version health table from online replays]
  HEALTH --> I
```

| Stage | Source |
|---|---|
| Variant builder | [`local-rig/solo/tools/mkbots.py`](../local-rig/solo/tools/mkbots.py) |
| Local launcher and slot limit | [`local-rig/play.sh`](../local-rig/play.sh), [`local-rig/engine/run_game.py`](../local-rig/engine/run_game.py) |
| Generated map families | [`workbench/tools/mapgen/`](../workbench/tools/mapgen), [`local-rig/maps/`](../local-rig/maps) |
| Upload and online tests | [`workbench/tools/submit.js`](../workbench/tools/submit.js), [`smoke.py`](../workbench/tools/smoke.py), [`pair_report.py`](../workbench/tools/pair_report.py) |
| Replay reader and ladder study | [`workbench/tools/ladder_replay.py`](../workbench/tools/ladder_replay.py), [`workbench/data/analysis/ladder/`](../workbench/data/analysis/ladder) |
| Rating ratchet and weak-loss alarm | [`park_watch.py`](../workbench/tools/park_watch.py), [`weak_watch.py`](../workbench/tools/weak_watch.py) |
| Last day's scripts and switch lists | [`workbench/archive/final-session-scripts/`](../workbench/archive/final-session-scripts) |

## 4. AI session operations

```mermaid
flowchart TD
  J[jun: direction, grants, final decisions]
  LEAD[Lead session<br/>decide, integrate, upload, verify]
  DESK[Desk session<br/>channel talk]
  TH[Thinking workers<br/>read code and replays, propose one change]
  GR[Grinding workers<br/>count, build from a spec, tables]
  SC[Scripts<br/>wait, poll, queue, alert]
  MEMO[(Session-state memo,<br/>handovers, promises ledger,<br/>standing rules)]

  J --> LEAD
  LEAD -- written brief, fixed report format --> TH & GR
  TH & GR -- report with a number the lead re-checks --> LEAD
  SC -- wake on event --> LEAD & DESK
  DESK -- inbox file --> LEAD
  LEAD <--> MEMO
  MEMO -- next session resumes from the document --> LEAD
```

The record of how this arrangement was reached, one revision at a time, is in
[write-up chapter 05](../writeup/05-ai-workforce.md).
