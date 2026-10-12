# Talk to meowbot

Use `/meow <message>` in Discord. Only team members can request actions.
It replies “👀 on it…” immediately and opens a conversation thread.
Continue in that thread; it resumes the same Claude session, including after bot restarts.
Short explanations use Sonnet medium. Analysis, judgment and actions use Opus high.

Each model call refreshes `data/meow/brain.md`: loop rules, promises, live status,
open cards/results, the last 40 Discord messages, analysis summaries and read-only memory.
The brain is capped at 15,000 UTF-8 bytes; sources remain readable on demand.
Claude can read team code/history, GitHub cards/PRs and reviewed online history tools.
Claude cannot execute changes itself. It proposes actions; meowbot validates and confirms them.

Examples:
- `/meow What is a toggle?`
- `/meow /hypo queen` — opens the usual hypothesis form; `hypo-max` adds deep analysis.
- `/meow /board-edit 42` — opens the edit form.
- `/answer card:42 text:Keep the queen near the fountain.`
- `/meow Set card 42 ready, then explain what happens next.`
- `/meow Use branch fix/feeding as the implementation for card 42.`
- `/meow Queue a mechanism check for card 42.`
- `/meow pause runner` / `/meow resume runner` — between jobs; running jobs finish.
- `/meow submit main` — previews an exact commit; merging never uploads by itself.

Card replies can be plain words (reply to meowbot's ping, or mention @meowbot) or
`/answer card:N text:…`: answer questions, confirm replays
(`text:looks right`) and decide after results (`text:ship it`, `text:drop it`,
`text:revise: …`, or explain why the evidence is inconclusive). Any member can answer for
another member's card. `/meow …` and `/answer …` also work when sent as an ordinary message
in #meow instead of through the slash menu. Replies keep your original
words and appear on GitHub and publicly in #meow. The runner interprets result replies
as candidate / rejected / inconclusive / revise; candidate approval still needs OKs.
Use `/meow` for everything else: create/edit cards, vote OK/Hold, request tests and escalate decisions.
Online pair requests preview a pinned implementation and active baseline: 30+30 unranked games,
one eligible stronger opponent, matching maps, then rollback. No ranked requests are allowed.
Unsettled requests appear in `/meow queue` and `/status`; human decisions can ping the team.
For a resolved judgment entry, its requester can say `queue done <id>` in the thread.

State pings no longer get a separate per-card Force post. Existing Force menus remain usable.
Any member can press Force on candidate/submit cards or ask `/meow force #31 …`.
`/meow force …` takes one Confirm and records your message as the reason (up to 300 characters).
The Force buttons ask for a one-line reason; sending it is the last step. A confirmation stays valid for 2 hours.
Force can override votes, stale-base/test/automatic-decision gates and freeze rules.
`tools/meow_offer.py` lets the session that answers @mentions hand one named member a ready-made plan:
meowbot posts it in #meow with a Confirm that only that member can press. Nothing is applied before the click,
the card is re-checked at the click, and the offer lapses after 12 hours (2 hours for a vote or a submit).
It always posts “⚠️ forced by <name>: <reason>” in #meow and on the GitHub card/PR.
Forced bot merges queue an old-10-map toggle-off identity check afterwards; failures warn, never undo/block.
Keys, ranked requests, branch/issue deletion and edits to team rules/memory cannot be forced.
Votes/answers always use the requester. Every action is audited “via /meow by <name>”.

Deployment needs Discord Message Content Intent and thread permissions, plus the updated loop runner.
Existing processes were not restarted by this change. The guard is a policy hook, not an OS sandbox.
