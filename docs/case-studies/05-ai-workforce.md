# Case study 5: running AI sessions as a workforce

## Problem

Most of the code and analysis in this project was produced by AI coding agents that I directed: a lead session, a
changing number of analyst and builder workers, and a build loop. Over two weeks the arrangement was revised more
than a dozen times, usually the day after it had run into a usage limit or shipped a wrong number. This case study
is about what the arrangement settled to and why.

## The division of labour

| Job | Who |
|---|---|
| Direction, grants of authority, final decisions | me |
| Decide, integrate, upload, verify | one lead session |
| Thinking: read code and replays, propose one change, judge replays | a strong model, as a worker with a written brief |
| Grinding: count with a defined metric, build from a ready specification, tables | a cheaper model |
| Waiting, polling, queues, alerts | scripts, no model |
| Talking in the team channel | a separate low-cost desk session |

The split by "does this need thinking?" survived every revision. The split by vendor flipped three times with
whichever account had quota left, so it is a capacity question and not a design one.

## Practices that earned their place

**Briefs and reports with a fixed shape.** A worker gets the goal, what is already ruled out, the files to read,
the metric's exact definition and the report format. The shared preambles are in
[`ASTRA-COMMON.md`](../../workbench/data/codex/astra/ASTRA-COMMON.md) and
[`CLAUDE-COMMON.md`](../../workbench/data/codex/astra/CLAUDE-COMMON.md); the builder brief is in
[`BUILDER-COMMON.md`](../../local-rig/solo/src/BUILDER-COMMON.md).

**A confident report is a lead until checked.** The write-up lists twelve cases where a report or a belief was
wrong, three of which reached the live bot. The checks added after each: re-count one key number independently,
attribute each game to the bot that played it from the replay, check that the game lasted as long as the metric
assumes, and treat a finished diagnosis as one that names a counted behaviour, the code line and a board that
reproduces it.

**Written state instead of a long context.** A long session's cost is calls times context size, and nearly all of
it is re-reading. By 10-05 the lead session was re-reading about 580k tokens per reply. What worked was a
session-state memo plus a planned replacement of the lead session about once a day, each started from a handover
document ([`workbench/docs/HANDOVER-*.md`](../../workbench/docs), [`SESSION-STATE.md`](../../workbench/docs/SESSION-STATE.md)).
Six successive lead sessions each resumed from a document. Every handover also lost something, and those losses are
tabulated in the write-up.

**Standing rules with their reason attached.** Each rule is one file with the incident that caused it and how to
apply it ([`workbench/archive/claude-memory/`](../../workbench/archive/claude-memory)). Examples: carry facts, not
verdicts, between rounds; stop a worker once its report is processed; name the model on every spawn; verify a fact
from its source before telling a teammate.

**Authority granted one step at a time.** Confirm every step, then routine infrastructure without asking, then
uploads, then a teammate's clear request carried out and reported after, then full autonomy on my own project. Two
limits never moved: a refusal by the permission system stops the action, and merging a teammate's card needs its
author.

**A promises ledger.** Every "I will" posted in the team channel was logged and closed as done or as a posted
correction ([`PROMISES.md`](../../workbench/docs/PROMISES.md)).

## What it cost

- Standing agents that mostly waited on CPU-bound game batches took a week's allowance to 95% in three days. The
  rule that followed: experiments run as loops, a script waits, one batch at a time.
- Two workers, one per teammate question, each reached about 200k tokens of context and 6M cache-read tokens in 11
  minutes. The rule that followed: say the size and the reason before spawning anything.
- A fan-out of analysts over every batch of new games was useful per round and ended in an incident on the last
  morning.

## What I would set up on day one next time

1. Three roles that do not blur, and scripts for all waiting.
2. Two state files: a short current-state page that is rewritten, and an append-only log.
3. A planned daily replacement of the lead session, with a handover template that copies its rule tables verbatim.
4. One independent re-count of a key number for every delegated analysis before acting on it.

Sources: [write-up 05](../../writeup/05-ai-workforce.md), [write-up 01, P3 to P6](../../writeup/01-playbook.md).
