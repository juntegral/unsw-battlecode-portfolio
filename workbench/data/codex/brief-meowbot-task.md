# Brief: meowbot state pings must cover [Task] cards (and candidates)

Repo: unsw-swarm, tools/meowbot.py. Today the automatic state pings (needs-info, needs-look, tested, rejected/inconclusive) only fire for issues whose title starts with "[Idea]". Task cards ("[Task] …") got no ping when card #15 reached tested.
- Treat "[Task]" titles exactly like "[Idea]" for state pings, /board, /loop and /answer.
- When a card gets status:candidate, post one short line: "#N is a candidate, PR + OK buttons coming".
- Wording: casual teammate tone, short.
- py_compile must pass; extend the existing offline checks.
- Do not run, restart or kill the bot. Do not commit.
Write a ≤5-line note to data/codex/report-meowbot-task.md.
