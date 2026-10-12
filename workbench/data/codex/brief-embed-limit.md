# Brief: meowbot must never send an embed Discord rejects for length

Work only in this repository (unsw-swarm). Edit only `tools/meowbot.py` and the matching test file under `tools/` (add one if none fits). No commits, no network, do not run `tools/meowbot.py` except with options that only print (`--dry-run`, `--preview-*`). Never read `docs/api.txt` or `docs/discord.txt`.

## Problem
On 2026-10-05 from 06:15 to 07:25 KST the log `data/meowbot/meowbot.log` shows, once a minute:
`poll error: 400 Bad Request (error code: 50035): Invalid Form Body` / `In embeds.0.fields.3.value: Must be 1024 or fewer in length.`
The bot was trying to post the candidate message with OK buttons for PR #35 (candidate `card-29-82407e034c`). Its manifest has a very long `results.mechanism` text, which went into an embed field unshortened, so the approval buttons never appeared and the PR was merged by hand. The manifest is in the battlecode repo at `candidates/card-29-82407e034c.json` (a copy of the relevant part: `results` has keys held, main, mechanism, cpu; mechanism is about 1,500 characters).

## Change
Wherever the bot builds an embed (candidate posts, previews, board, anything else), clamp to Discord's limits before sending: field value 1024, field name 256, embed title 256, embed description 4096, at most 25 fields, and 6000 characters in total per embed. Shorten with a trailing "…" and, for a candidate field that was cut, end with a short pointer to the card or PR link if one is available in that embed. Do it in one shared helper so every embed goes through it. Do not change wording or layout otherwise.

## Tests
- A candidate whose mechanism text is 1,500 characters renders an embed whose every field value is at most 1024 characters and whose total is at most 6000.
- Short texts are unchanged.
Run the whole tools test suite from inside `tools/`: `python3 -m unittest discover -p 'test_*.py'` must end with `OK`. Also render the PR #35 candidate with the existing preview option (`--preview-candidate-pr 35` or the closest read-only preview the file offers) and confirm it no longer exceeds the limits; if that preview needs network access you do not have, say so and rely on the unit test.

## Output
Write `data/codex/report-embed-limit.md` last: what changed, the last 5 lines of the test output, and anything you were unsure about.
