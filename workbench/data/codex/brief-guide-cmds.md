# Brief: add a "Discord commands and how they connect" section to the loop guide

File: unsw-swarm/data/guide/guide.html (already published; keep its design, language toggle EN/中文, and page contract).
Facts: read tools/meowbot.py fully (slash commands, buttons, pings, what each posts and where), battlecode work/loop/runner.py + docs/LOOP.md (which states wait on which human action).

Add a new section placed right after "How to take part", titled "Discord commands and how they connect". Contents:
1. **Where things live**, as 3 short lines:
   - this guide (link https://claude.ai/artifact/(removed));
   - the spec (docs/LOOP.md / LOOP.zh.md on main in github.com/forrest-gan2005/battlecode);
   - the board (GitHub issues; /board shows it in Discord).
2. **A command table.** One row per command: /hypo, /hypo-max, /board, /board-edit, /loop, /status, /answer, plus the buttons (OK / Hold on candidate cards) and the automatic pings (needs-info, needs-look with replays attached, tested, PR posts).
   Columns: what it does · who sees the reply (only you / everyone) · what it triggers next.
   Be exact about what /hypo-max does. Check the code: it is an AI analysis, read-only, so state what it produces and whether it creates a card or not.
3. **"What comes next" chains**, as small step diagrams or numbered chains:
   - Idea: /hypo → card appears (status:untested) → someone marks it ready → loop asks questions (ping) → **/answer card:N text:...** (or reply on GitHub) → loop builds → ping with 2–3 replays → reply "looks right" with /answer (or on GitHub) → tests → result ping → you decide on the card → candidate → OK buttons (author + 1) → merge + submit.
   - /hypo-max: what happens after it and what you must do to turn its output into a card, if anything.
   - Task card: GitHub [Task] template → ready → build + check → result → decide → OK.
   - Online comparison: who runs it, the "testing online now" / "done, swapped back" Discord rule (agreed on 10-04), and that only one person swaps bots at a time.
   Make it obvious where the loop WAITS for a human and which command un-blocks it. Mark those steps as "⏸ waits for you".
4. **/answer explained in 3 lines with an example:** `/answer card:10 text:if an enemy gets in, leave through the other portal`. Any language, not translated; the comment shows as "Answer from <name>"; for Zhe's cards only Zhe's answers count.
Both languages (EN + 中文). Keep the tone casual and short, no jargon. Phone width must work (the table may scroll in its own box).
Also fix any place in the page that says you can "reply in Discord and have it copied" so that it names /answer.

Do not publish or commit. Write a ≤6-line note to data/codex/report-guide-cmds.md.
