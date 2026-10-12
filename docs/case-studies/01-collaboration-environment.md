# Case study 1: a collaboration environment for three time zones

## Problem

The team formed seven days before the deadline: three people, up to nine hours apart, one shared bot. Two of us
could rarely be awake at the same time as the third. Ideas arrived in chat in three languages, test results lived
on one laptop, and "is that merged?" had no place to be answered.

## What I built

A bridge between the team's Discord channel and its GitHub repository, so that the channel became the place where
work was proposed, shown and approved, and GitHub the place where its state was kept.

**meowbot** ([`workbench/tools/meowbot.py`](../../workbench/tools/meowbot.py)) started on the first full day of the
team and grew through the week:

| Function | How it works |
|---|---|
| Pull request and idea feed | Polls repository events and posts each PR and each idea card as an embed with a three-line plain summary |
| `/hypo`, `/hypo-max` | A modal that turns a hypothesis written in Korean, Chinese or English into a structured GitHub issue (claim, evidence, expected change, what would show it is wrong). The original text is kept; `-max` adds a read-only analysis with code pointers and prior attempts |
| `/board`, `/loop`, `/status`, `/task` | Private one-screen views of the idea board, what every loop is doing, the ladder and open PRs, and what each person is waiting to decide |
| `/answer`, `/board-edit` | Answer a loop's question on a card, or edit a card, without leaving the channel |
| Candidate approval | A release candidate appears with approve and hold buttons that only the three members can press. Any vote has a force path that needs a second confirmation and a reason, and is announced publicly |
| `/submit` | Preview an exact release and confirm its upload as the requesting member |
| `/meow` | A threaded teammate: a read-only AI session with the team's context. Anything it wants to do becomes a plan the requester must confirm ([`meow_chat.py`](../../workbench/tools/meow_chat.py)) |

Around it, a set of scripts with no model in them:

- [`discord_sync.py`](../../workbench/tools/discord_sync.py) mirrors the channel to local files.
- [`team_watch.py`](../../workbench/tools/team_watch.py) shows new messages and new GitHub events; it was the first
  action of every working turn.
- [`mention_watch.py`](../../workbench/tools/mention_watch.py) and [`loop_watch.py`](../../workbench/tools/loop_watch.py)
  sleep until a mention or a card needs attention, then wake a session.
- [`decision_nudge.py`](../../workbench/tools/decision_nudge.py) and [`snooze.py`](../../workbench/tools/snooze.py)
  remind an author that a card is waiting, only inside their configured hours.

## Design decisions

- **Fail closed.** The chat session runs behind a tool policy
  ([`meow_guard.py`](../../workbench/tools/meow_guard.py)) that allows reads inside named folders and refuses
  everything else, including any path that looks like a key or credential.
- **Responsibility instead of gates.** A sleeping teammate must not block the other two, so every approval can be
  forced, but forcing is visible and carries a reason.
- **The bot speaks when spoken to.** It answers a mention or a command and otherwise stays out of the teammates'
  conversation.
- **Text files as the interface.** Notices are short text files that any script or person can write and one command
  posts. The same files are the audit trail.
- **Tested offline.** Fake Discord, GitHub and model clients; 38 test files and 431 test functions across the bot
  and the loop.

## What happened

- Ideas were built while their authors slept, and any teammate could answer the loop's questions on another's card
  so the queue kept moving.
- 69 promises made to teammates in the channel were logged in a ledger and closed as done or as a posted
  correction (write-up, chapter 01, "What we would do again").
- On the last day a separate low-cost "desk" session took over channel talk so that chatter stayed out of the lead
  session's context ([`DISCORD-DESK.md`](../../workbench/docs/DISCORD-DESK.md)).

## What I would change

The bot became the largest single tool in the project. Whether a team of three needed all of it, rather than the
mirror and the watchers alone, was never measured (write-up, chapter 04, section 7). Next time I would start from
the watchers and add interactive features only when a concrete delay shows they are needed.

Sources: [write-up 04, section 7](../../writeup/04-tools.md), [write-up 05, section 6](../../writeup/05-ai-workforce.md).
