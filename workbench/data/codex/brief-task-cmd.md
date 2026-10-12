# Brief: `/task`, one screen that says what each person has to do next

Work in this repository (unsw-swarm). Edit `tools/meowbot.py`, add a small module `tools/tasks.py` for the logic, and add `tools/test_tasks.py`. You may read and import from `tools/decision_nudge.py`, `tools/snooze.py`, `tools/card_names.py`, `tools/fair_queue.py`. No commits. No network in tests (stub every `gh` call and file read). Do not start, stop or restart the bot or any other process; the bot will be restarted by hand after review. Never read `docs/api.txt` or `docs/discord.txt`.

## Why
Three people (준싱, Zhe, QWQ) work on idea cards that move through a loop (GitHub issue labels are the state). What each person has to do next is spread over card pings, the hourly "decision check" and PRs, and it is getting hard to keep in one's head. They want one slash command that lists it per person. It should be the last command the bot needs.

## Facts to build on (read the code before designing)
- `tools/meowbot.py`: slash commands are registered near the other `@self.tree.command(...)` definitions (`/board`, `/loop`, `/status` are good models: they answer only to the caller). `MEMBERS` maps Discord ids to names. `board_state()` lists the open idea cards with their status. Candidate PRs and their OKs are tracked in the bot's state (look for how the approve buttons record who has approved and who still has to; human ideas need the author's OK plus one non-author OK).
- `tools/decision_nudge.py`: `WAITS` and `waiting()` already compute which open cards wait on a person, since when, and who (labels `by:zhe`, `by:qwq`, `by:junsing`; `status:needs-look` waits on Zhe only for Zhe's cards, 준싱's and AI cards pass the look step by themselves). `tools/snooze.py` holds "I'm still deciding" snoozes per card.
- Card states that mean a person must act: `status:needs-info` (answer the loop's questions before the build), `status:needs-look` (check 2 to 3 replays), `status:tested` (decide: ship it, drop it or revise), `status:candidate` (a candidate PR is open and needs OKs).
- States that are information only: `status:in-progress` (the owner works on it by hand, outside the loop), `status:untested` on an open card that is not queued (parked), `status:ready` / `status:building` / `status:testing` (the loop is working, nobody has to do anything).
- The reply command for a card is `/answer card:<n> text:…`; approving a candidate is the OK button on the bot's candidate post; `/submit` uploads main.

## Wanted
1. `tools/tasks.py`: `collect(now)` returns a plain data structure per person (`준싱`, `Zhe`, `QWQ`) with
   - **to do**: every card or PR that waits on that person, oldest first: card ref (`#39 queen-safety`), what to do in plain words, how long it has waited, and the exact way to answer (`/answer card:39 text:…`, or "press OK on the candidate post", or a link for a PR). A snoozed card is listed with `(still deciding, quiet until ~HH:MM)` and does not count as waiting.
   - **yours, nothing to do now**: that person's cards the loop is working on (`building`, `testing`, queued) with the step and the expected finish time if `~/meow-loop-out/status.json` has one, and their `in-progress` cards.
   - **parked**: that person's open cards that are neither queued nor in progress (for example `status:untested`), with "queue it with status:ready or close it".
   and one shared block **anyone**: open candidate PRs that still miss a non-author OK (say whose OK is missing and who may give it), open non-candidate PRs older than a day, and whether `main` is ahead of the bot that is live on the server if the bot already knows this without a new network call (if it does not, leave that line out; do not add server calls).
   `render(data, who=None, now=...)` turns it into the message text.
2. Message format (Discord; keep it under 1,900 characters, cut the longest lists with "… and N more"):
   - first line `📋 tasks · HH:MM KST` (and the person's local time in brackets for Zhe (CEST) and QWQ (AEDT) next to their name)
   - one section per person, the caller's own section first: a bold name line with the count (`**Zhe** (15:27 there) · 3 waiting`), then the to-do rows in one fenced code block with aligned columns (card, what to do, waited), then one plain line each for "yours, nothing to do now" and "parked" if not empty. A person with nothing at all gets `nothing waiting`.
   - then `**anyone**` if not empty.
   - last line: `reply to a card with /answer card:N text:… · "/meow N still deciding" quiets the hourly check`
3. `/task` in `tools/meowbot.py`, team members only, answer visible only to the caller, no model call. Options: `who` (choice: me, 준싱, Zhe, QWQ, all; default all with the caller's section first) and `share` (boolean, default false; when true the answer is posted in the channel for everyone, with mentions disabled).
4. CLI for checking without Discord: `python3 tools/meowbot.py --preview-tasks [--who NAME]` prints the message text and exits (this may call `gh` like the other preview flags do).
5. Add `/task` to the module docstring's command list in one line.

## Checks
From inside `tools/`: `python3 -m unittest discover -p 'test_*.py'` ends with `OK` (123 tests now). New tests cover: each of the four waiting states mapped to the right person and wording; Zhe's look step against a card by 준싱 that passes by itself; a snoozed card; a candidate PR missing the non-author OK; in-progress and parked lists; `who` filtering and the caller-first order; the 1,900-character cap; a person with nothing. Then run `python3 tools/meowbot.py --preview-tasks` and `--preview-tasks --who Zhe` if `gh` works without the network sandbox; if it does not, say so and show the output of the same render on a fixture that matches today's board: Zhe has #39 queen-safety (needs-info), #31 queen-hunt and #36 queen-dead-end (needs-look), #16 safezone-v2 parked; QWQ has #38 queen-loop, #33 blind-circling, #22 late-feed in progress; 준싱 has nothing.

## Output
Write `data/codex/report-task-cmd.md` last: what changed and where, how candidate OKs are read, the rendered message for today's board (all, and `who=Zhe`), the last 4 lines of the test run, and anything you were unsure about or could not exercise.
