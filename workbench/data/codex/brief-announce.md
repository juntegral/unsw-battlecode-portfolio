# Brief: meowbot --announce

Repo: unsw-swarm, tools/meowbot.py. Add the CLI option `python3 tools/meowbot.py --announce-file FILE [--dry-run]`.
- It posts the file's text, at most 2000 chars, to the #meow channel (data/discord/channel.txt) as meowbot, through the Discord REST API: POST /channels/{id}/messages with the bot token read the same way run_bot() reads it.
- It must work while the bot process is running (separate process, REST only, no gateway). Then it exits.
- `--dry-run` prints the text and the channel id only.
- Never print or log the token. Use urllib (stdlib) and the same SSL_CERT_FILE fallback.
- Do not run it without --dry-run. Do not restart the bot. Do not commit.
- py_compile must pass. Add a fake test for the request shape.
Write a ≤5-line note to data/codex/report-announce.md.
