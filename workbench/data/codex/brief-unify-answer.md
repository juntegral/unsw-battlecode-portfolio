# Brief: one human input, /answer (finish the meowbot side + guide)

Team decision (10-04 21:00): people act on cards through `/answer` only; `/meow` covers everything else.
Already done by the team lead:
- battlecode runner (main 's latest commit): a reply after the results is classified as candidate / rejected / inconclusive / revise (prompts/decide.md).
- unsw-swarm tools/meowbot.py (uncommitted): the extra post "#N: a member can take responsibility for the next state." after every card state ping was removed (one line in the poll loop).

Your job, in unsw-swarm (edit files only; never start/stop/kill the bot; do not commit):
1. `data/codex/check-meowbot-states.py` now fails because of that removal. Update it to the new behaviour: no force post after state pings.
   Then make sure EVERY offline check passes: tools/check-*.py, tools/test_*.py, data/codex/check-*.py.
2. Force must still be reachable: on candidate cards (button) and through `/meow` ("force #31 …"). Check that `chat.CardForceView` persistence code in setup_hook does not break for old messages (old buttons already posted in Discord should still answer, or fail gracefully). Fix it if needed; add a test.
3. Result pings (status tested): add one short hint line, "decide with /answer card:N text:ship it / drop it / revise: …". For needs-info and needs-look pings add "reply with /answer card:N text:…". Keep the messages short.
4. Docstring + data/meow/README.md: describe the unified flow.
5. data/guide/guide.html (EN + 中文, keep the design and contract): update the commands table, the "what comes next" chains and the Force section:
   - /answer is the single way to answer questions, confirm replays AND decide after results (examples);
   - /answer replies are visible to everyone;
   - no per-card force post any more; Force lives on candidate cards and in /meow.
   Do not publish.
Write a ≤8-line note to data/codex/report-unify-answer.md listing changed/new files.
