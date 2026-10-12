# Brief: update tools/check-meowbot-look.py to the new replay-attachment behaviour

Repo: unsw-swarm. tools/meowbot.py `send_state_message` was just changed (uncommitted): for needs-look pings it now
- sends the text message first, without files;
- then sends each replay (max 3) in its own message as `discord.File(io.BytesIO(raw), filename=name)`;
- gzips a replay larger than LOOK_INLINE_BYTES (8 MiB) and names it `<name>.gz`; skips it if still too large;
- adds the line "(.gz files: unzip first, then open the .replay)" to the text when any file was gzipped;
- logs and continues if one file fails to send.
Update tools/check-meowbot-look.py so its tests assert this behaviour (small file sent as is, big file gzipped, oversize skipped, one failing send does not stop the others, text sent first, missing look.json keeps the plain ping). Do not change tools/meowbot.py unless a test reveals a real bug (then say so). All checks must pass: tools/check-*.py, tools/test_*.py, data/codex/check-*.py. Do not run or restart the bot. Do not commit.
Write a 3-line note to data/codex/report-look-test.md.
