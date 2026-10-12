# Brief: add /meow, Force and /submit to the loop guide

File: unsw-swarm/data/guide/guide.html (published guide; keep the design, the EN/中文 toggle, the page contract and phone width).
Facts: data/meow/README.md, tools/meowbot.py (docstring, /meow, Force flow, /submit), tools/meow_chat.py (whitelisted actions), battlecode docs/LOOP.md ("AI cards decide themselves", task cards).

Changes:
1. In the "Discord commands and how they connect" section, add rows for `/meow` and `/submit` to the command table, and a "Force" row under buttons.
2. New short section right after it: "Just talk to it: /meow". Contents:
   - **What it is:** a teammate you can ask or tell things in plain words, any language. It opens a thread, and replies in the thread continue the chat.
   - **What it can do:**
     - everything the slash commands do;
     - move a card (ready / decide);
     - queue a local test or an online 30:30 comparison;
     - use a branch you coded yourself as a card's implementation, e.g. "use my branch zhe/safezone2 for #16";
     - explain results;
     - draft a card from a chat.
   - **How actions run:** it shows what it will do, you press confirm, meowbot does it. Votes and answers are always yours, never someone else's.
   - **Not sure → queue:** if it needs a judgment call it can't make, it queues it and asks the team.
   - **3–4 example prompts**, including one in Chinese.
3. New short section "Force (when you can't wait)". Contents:
   - Any member can skip a vote or a gate: press Force → confirm → type a one-line reason ("I take responsibility: …") → confirm again.
   - It is posted publicly as "⚠️ forced by <name>: <reason>" and written on the card.
   - A forced merge of bot code gets an automatic "still plays the same when off" check afterwards (a warning only).
   - Nobody can force: reading keys, ranked requests, deleting things, changing team rules.
   - Purpose, in one line: time zones. Responsibility instead of waiting.
4. Update anything now out of date:
   - OK buttons merge to main only;
   - `/submit` uploads main to the server (one member + confirm; blocked after the freeze on Oct 8 20:00 KST);
   - rollbacks are done by hand;
   - AI cards decide themselves (revise once if the change barely fired; clear loss → closed; clear win → candidate; coin flip → people).
   Fix the journey diagram labels only if they contradict this.
Both languages. Casual, short, no jargon. Do not publish or commit. Write a ≤5-line note to data/codex/report-guide-meow.md.
