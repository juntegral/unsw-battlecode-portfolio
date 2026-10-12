# Case study 2: the card loop

## Problem

An earlier overnight arrangement kept AI sessions alive while they waited for CPU-bound game batches. It worked
unattended, and it burned most of a week's usage allowance on waiting. The team also needed one queue that three
people could feed and read, with a clear answer to "what happens to my idea next, and who has to act?".

## Design

**One issue per idea, one label per state.** A card is a GitHub issue made from a template: the claim, the
evidence, the expected change, and what would show it is wrong. Exactly one `status:*` label is the card's state.
The runner keeps no private queue and no remembered timer, so it can be killed and restarted at any point and
resume from the labels alone.

**A runner that waits without a model.** [`runner.py`](../../card-loop/work/loop/runner.py) polls GitHub every few
minutes and starts an AI session only when a card's state needs AI work. Games run as detached jobs with lease
files ([`jobs.py`](../../card-loop/work/loop/jobs.py)), one batch at a time, and outlive the runner.

**Steps with a person at the right points.**

| State | Who acts | Gate to leave it |
|---|---|---|
| `ready` | runner | picked by a fair rotation across authors |
| `needs-info` | AI asks, author answers | "what if" edge-case questions answered on the card or in chat; any teammate may answer for an absent author |
| `building` | AI | build passes, and with the new switch off the bot is replay-identical to the current release on the regression maps |
| `needs-look` | author | watches two or three picked replays and says "that is what I meant" |
| `testing` | runner | paired local A/B on held-out maps, transposed copies and the regression maps |
| `tested` | author | chooses candidate, rejected or inconclusive |
| `candidate` | people | approvals, merge, upload of that exact commit |

**Rules written into the specification** ([`LOOP.md`](../../card-loop/docs/LOOP.md)):

- New behaviour is a switch that starts off. A build that changes play with the switch off goes back.
- Every result opens with three plain lines: what we tried, did it work, who decides now.
- Every result carries a "why" table, not only wins: the behaviour counted on base and candidate.
- Task cards (refactors, tooling, CPU) must leave play identical; anything that changes play is an idea card.
- The loop never uploads and never requests ranked games.
- A session working on a card runs under a hook ([`guard.py`](../../card-loop/work/loop/guard.py)) that restricts
  what it may touch.

## What happened

- The loop ran from 10-04 and worked on 24 cards. In its phase (10-04 to 10-07) the live bot moved through six
  versions and the rating from 1800 to about 1950.
- Ideas were built while their authors were offline, and every card left a build that was provably inert when off.
- AI-written cards started to crowd the single game slot, so from 10-05 the queue carried only the teammates' ideas
  and AI cards were closed or advanced by fixed thresholds.

## What did not work

The result test was local win counts against our own bot, and it mostly returned "no difference": 199 against 194
over 400 pairs, with 391 of 400 pairs identical. For two days the loop also tested against stale default settings.
The single local game slot was the bottleneck.

## What I would keep and change

Keep the label state machine, the inert-build gate and the three-line result format. Replace the win-count test
with two cheaper questions, "how often did the switch change a decision?" and "did any map break?", and send the
survivors to a paired online run in bundles.

Sources: [write-up 01, P2](../../writeup/01-playbook.md), [write-up 05, section 1.3](../../writeup/05-ai-workforce.md),
[`LOOP.md`](../../card-loop/docs/LOOP.md).
