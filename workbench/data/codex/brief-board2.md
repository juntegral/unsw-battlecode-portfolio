# Brief: make work/board.py follow docs/LOOP.md

Repo: battlecode, branch juntegral. Read docs/LOOP.md fully (the spec), then work/board.py.
All state labels already exist on GitHub (status:ready, needs-info, building, needs-look, testing, tested, candidate, smoke, kept, rejected, inconclusive, untested; by:zhe/junsing/qwq/ai).

Change board.py so that:
- `next`: picks a status:ready card by priority (by:zhe, then other non-ai, then by:ai; oldest first within a group) and prints number, title, labels, body and all comments.
  `next --state S` lists the cards in state S.
- `state N S [--note FILE]`: replaces any status:* label with status:S, never stacks them, and removes legacy loop:ready / loop:running / status:in-progress. It optionally posts a note comment and updates the Loop status heartbeat.
- `report N --kind test|check --file F --state S`: posts the comment.
  The FILE must already start with the 3-line plain summary. The tag line ("[test] by … · base …") goes AFTER the summary, as a small footer line, not before it.
  The base is the current origin/main commit (git fetch first), not local HEAD.
- `ask N --file F`: posts edge-case questions as a comment that starts "Questions before we build" and sets status:needs-info (meowbot does the @mention).
- `ready N` sets status:ready (via state). `claim` becomes an alias of `state N building`.
- `heartbeat` and `remove` stay as they are.
- `migrate`: one-off. Map legacy labels on open [Idea] cards per the "Mapping the old labels" table in LOOP.md. Default is a dry run that prints the planned changes; it acts only with --apply.
Keep the file style (short comments, gh() helper). The docstring lists the commands.
Check: `python3 -m py_compile`. Test the parsing and priority logic with fake gh output (no network in the sandbox; don't call gh for real).
Do not commit or push. Write a ≤10-line note to ~/01. Project/개인 프로젝트/unsw-swarm/data/codex/report-board2.md.
