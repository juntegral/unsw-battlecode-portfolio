# Brief: meowbot /answer, to copy a Discord answer onto a card

Repo: unsw-swarm, tools/meowbot.py. Members only.

Add the slash command `/answer card:<issue number> text:<answer>`. Any language is fine; do NOT translate (the loop reads KO/EN/ZH).
- It posts a GitHub comment on that [Idea]/[Task] issue in forrest-gan2005/battlecode: `Answer from <MemberName>: <text>`.
  The MemberName is Zhe / QWQ / 준싱 from MEMBERS. The runner (battlecode work/loop/runner.py human_replies) accepts the "Answer from Zhe:" prefix for Zhe's cards, so keep that exact prefix format.
- It replies ephemerally with the comment link. It refuses with a short message if the issue is not open, or is not an [Idea]/[Task] card.
- Keep the style; add it to the docstring.
- py_compile must pass; add an offline fake test.
- Do not run, restart or kill the bot. Do not commit.
Write a ≤5-line note to data/codex/report-answer.md.
