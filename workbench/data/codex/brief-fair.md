# Brief: fair turns between people in the loop queue (no one's ideas get starved)

Team rule change (team lead, 10-05): today the queue order is task cards > Zhe's cards > other people's cards > AI cards. If Zhe posts ideas faster than the loop finishes them, QWQ's and 준싱's cards never get a turn. Replace the fixed "Zhe first" with fair rotation between people.

## New order
1. Task cards (`type:task`) first, oldest first. Unchanged.
2. Human idea cards: **round-robin by author** (`by:zhe`, `by:qwq`, `by:junsing`). Pick the author who was served least recently (never served = first); within that author, the oldest ready card. "Served" = the loop started building one of that author's cards. Keep it in `~/meow-loop-out/fair.json` ({author label: ISO time of the last start}), written when a card moves ready → building (or ready → needs-info).
3. AI cards (`by:ai`) when no human idea card is ready, plus a guaranteed share: after every 3 human cards started, one AI card may go even if human cards are waiting (so the ladder ideas don't starve either). Keep the counter in the same file.
4. The same rotation applies wherever cards compete for a shared slot (the AI lock and the game-batch lock): when several cards wait for the same lock in one poll, the one whose author was served least recently goes first. Tasks still go first.
Zhe's extra steps stay exactly as they are (questions always, replay check required). This change is only about whose turn it is.

## Where
- Work ONLY in the worktree ~/meow-dev2 (branch dev/fair, from main); never the live checkout. Commit there if git allows it; do not push.
- work/loop/runner.py: the priority/ordering code (card selection and the order in which waiting cards are offered locks).
- work/board.py `next` (same rule; read fair.json if it exists, otherwise fall back to author rotation by oldest card).
- docs/LOOP.md and docs/LOOP.zh.md: update the queue-order paragraph/table (short).
- Tests: rotation across three authors, a never-served author goes first, the AI share (1 after 3 humans), tasks first, lock order. `python3 -m unittest discover -s work/loop/tests` must pass.

## Also (unsw-swarm, edit files only, never start/stop the bot, do not commit)
- tools/meowbot.py: /loop and /board show the queue in the new order with a short "next up: <author>" hint (read ~/meow-loop-out/fair.json; tolerate a missing file).
- data/guide/guide.html (EN + 中文): update the queue line ("Tasks → people take turns (Zhe, QWQ, 준싱) → AI ideas get every 4th slot"). Do not publish.
- ALL offline checks must pass: tools/check-*.py, tools/test_*.py, data/codex/check-*.py.

Write a ≤8-line note to data/codex/report-fair.md listing changed/new files in both places.
