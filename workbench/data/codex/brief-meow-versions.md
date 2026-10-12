# Brief: let the `/meow` teammate know which bot version is which

Work in this repository (unsw-swarm). Edit the code that builds the `/meow` context ("brain", see `tools/meow_chat.py`, `tools/meow_ui.py` and how `data/meow/brain.md` is refreshed on each call) and its tests under `tools/`. No commits. No network in tests (stub subprocess calls). Do not start, stop or restart the bot. Never read `docs/api.txt` or `docs/discord.txt`.

## Why
On 5 Oct a teammate asked the bot "what is the difference between v26 and the base version now? When can we decide to merge them?". The bot answered "I can't pin down which build v26 is from here: the upload list is blocked for me in this mode". Versions (v1, v2, …) are how the team sees bots on the submissions page, so the bot must know them.

## Wanted
Each time the brain is refreshed, add a short section "Bot versions on the server" built by the bot process itself (not by the model):
- from `node tools/subs.js list --json --last 15` (fields `version`, `id`, `name`, `status`, `description`, `uploadedAt`): one line per version, newest first, `v26 · 17648 · qh31d-test · idle · <description>`; mark the active one as `LIVE`.
- for versions whose `name` matches a pair-test label in `data/online/smoke/<label>.json` (the new half's submission id equals the version's id), append what was tested, from that state file: the card reference (`ref` if stored, else the label), the opponents, and the result line from `data/online/smoke/<label>-result.txt` if it exists (first line only).
- one line that says which version is the control: the active submission, and that card tests are `v<live> main + <card>`.
If `subs.js` fails (no network), keep the previous section and add `(could not refresh at HH:MM)`. Keep the section under 2,500 characters; cut the oldest versions first. The call must not slow a `/meow` answer by more than a few seconds: use a 10 second timeout.
Also add one sentence to the bot's instructions where the other standing facts are: when someone names a version, look it up in that section, and name bots by version first and card second.

## Checks
From inside `tools/`: `python3 -m unittest discover -p 'test_*.py'` ends with `OK` (151 tests now), with new tests for the section (matching a label, a version with no label, the LIVE mark, the failure fallback, the size cap).

## Output
Write `data/codex/report-meow-versions.md` last: what changed and where, a sample of the section built from fixtures that match these facts (v22 = 17594 card-25-ff0327008d, live; v26 = 17648 qh31d-test, ref "#31 queen-hunt (on new main)", vs test4 + WeHaveQuizzes), the last 4 lines of the test run.
