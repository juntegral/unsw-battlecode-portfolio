# Brief: "I'm still deciding" — pause the hourly decision check for one card via /meow

Work only in this repository (unsw-swarm). Edit `tools/meowbot.py`, `tools/decision_nudge.py`, and test files under `tools/` (add `tools/test_snooze.py`). No commits, no network, do not start the bot or the nudge script (dry-run and unit tests only). Never read `docs/api.txt` or `docs/discord.txt`. `docs/PROMISES.md` has unrelated uncommitted edits: leave it alone.

## Background
`tools/decision_nudge.py` posts a "decision check" to Discord every hour, listing open cards that have waited an hour or more for a person's decision and @mentioning that person. Sometimes the person is still working on the decision and does not want hourly pings for that card. They should be able to say so in Discord with the existing `/meow` command, for example:

`/meow 25 im taking some time on my decision. ill call you later`

## What to build
1. A small snooze store, `data/meowbot/snooze.json` (git-ignored directory, create the file on first write): per card number `{until, by, note, set}` with ISO times. Put the read/write helpers where both the bot and the nudge script can use them (a tiny module under `tools/` is fine) and make writes atomic.
2. `/meow` handling in `tools/meowbot.py`. Read how `/meow` works today first and fit into it rather than around it.
   - Fast path, no model call: when a team member's `/meow` text starts with a card number (`25 …` or `#25 …`) and the rest says they need more time (English, Korean or Chinese: taking time, still thinking, still deciding, need more time, not yet, later, snooze, 아직, 생각 중, 나중에, 좀 더, 还在, 稍后, 再想想 and close variants), record a snooze for that card and answer in the channel, visibly, in one line, for example: `⏸ #25 queen-unbox: QWQ is taking more time on the decision. decision checks stay quiet for this card until ~17:00 KST. "/meow 25 back" ends it early`.
   - Length: default 6 hours; honour an explicit length in the text (`for 3h`, `12 hours`, `until tomorrow` = 24 h, `3시간`, `내일`), capped at 24 hours.
   - `/meow 25 back`, `done`, `cancel`, `resume`, `끝`, `취소` clears the snooze with a one-line confirmation.
   - If the text starts with a card number but the intent is not clearly one of these, let it go through the existing `/meow` flow unchanged. If that flow has a list of allowed actions for the model, add `snooze` and `unsnooze` to it so the model can choose them too; they need no confirmation step.
   - Only cards that exist and are open; otherwise answer that the card was not found. Do not post anything to the GitHub card (a comment there could be read by the loop as a decision).
3. `tools/decision_nudge.py`: a card with a snooze that has not run out is not pinged. Show it instead on one compact line without a mention at the end of the message, e.g. `still deciding: #25 queen-unbox (QWQ, quiet until ~17:00 KST)`. If every waiting card is snoozed, post nothing that hour. A snooze whose card is no longer waiting, or whose time is over, is removed from the store.
4. Keep everything else as it is.

## Tests
Unit tests for: the intent and length parsing (the example above; `#25 need more time for 3h`; a Korean and a Chinese example; `25 back`; a non-matching text such as `25 what did the test show?` falls through), the store (set, expire, clear), and the nudge filter (snoozed card not pinged and listed on the "still deciding" line; all snoozed → no post). Run the whole suite from inside `tools/`: `python3 -m unittest discover -p 'test_*.py'` must end with `OK`. Also run `python3 tools/decision_nudge.py --once --dry-run` if it works without network; if it needs `gh` and the network is not available, say so.

## Output
Write `data/codex/report-snooze.md` last: what changed, how `/meow` now decides between the fast path and the old flow, the last 4 lines of the test run, three example bot replies verbatim, and anything you were unsure about.
