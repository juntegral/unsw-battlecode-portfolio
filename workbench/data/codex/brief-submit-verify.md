# Brief: `submit.js upload` reports "server zip DOES NOT match" for a bot folder outside this repo

Work in this repository (unsw-swarm). You may edit `tools/submit.js` and add or extend a test next to the existing JS or Python tests if there is a harness for it. No commits. No network: do NOT run `upload`, `activate`, `active` or `check` (they call the server). Never read or print `docs/api.txt` or `docs/discord.txt`.

## What happened (5 Oct)
- 18:36 `node tools/submit.js upload ~/meow-release/mybot2 --name card-25-ff0327008d --desc "…" --confirm` uploaded and activated the bot, then printed `active: 17594 card-25-ff0327008d; server zip DOES NOT match ../../../meow-release/mybot2` and exited 1.
- A minute later `node tools/submit.js check ~/meow-release/mybot2` printed `active: 17594 card-25-ff0327008d; identical to ~/meow-release/mybot2`.
- 20:27 the same thing through `tools/smoke.py pair` with that folder: upload, then `active: 17678 bl17594b-test; server zip DOES NOT match ../../../meow-release/mybot2`, exit 1 (log: `data/online/smoke/bl17594b-test.log`).
- About a dozen uploads the same day from folders inside this repo (`data/online/smoke/<name>-bot/`) all verified fine.
So the upload itself is right; the verification after `upload` gives a false mismatch for a folder outside the repo root, while `check` on the same folder is right.

## Wanted
1. Read `tools/submit.js` (the `upload` path, the zip it builds, the post-upload comparison around the "server zip … match" line, and the `check` path) and find why the two comparisons disagree for an outside folder: how entry names are built from the folder path, relative paths with `..`, symlinks or path normalisation under `~/01. Project/…` against `~/meow-release`, files skipped or added, or a race on which submission's zip is downloaded.
2. Fix it so the post-upload verification compares the same things `check` does and is right for any folder, inside or outside the repo. If the cause is in how the zip itself is built for an outside folder (for example entry names containing `../`), fix that too and say plainly whether the two zips uploaded today from that folder could contain anything different from a folder inside the repo with the same four files (the server compiled and ran them, and `check` says the hashes are identical).
3. Keep the exit code meaning: non-zero only when the server really holds something different, or the upload failed.

## Checks
`node --check tools/submit.js`. If you can exercise the comparison offline (for example by factoring the comparison into a function and calling it on a zip you build locally from a temporary folder inside and outside the repo), do so and show the output; otherwise say exactly what was not exercised. From inside `tools/`: `python3 -m unittest discover -p 'test_*.py'` still ends with `OK`.

## Output
Write `data/codex/report-submit-verify.md` last: the cause with the lines that show it, what you changed, what you exercised, and anything you could not confirm without the server.
