# Brief: one number per idea — card number + short name everywhere

Problem: GitHub issues and PRs share one number line, so a card (#27) and its candidate PR (#32) have different numbers and teammates get confused.
Decision: people only ever see the CARD number plus a short name, e.g. `#27 passage`. PR numbers appear only inside links.
Short names live in a label `name:<slug>` on the card (already set by hand on all open cards: #27 name:passage, #29 name:safer-stride, #31 name:queen-hunt, #30 name:big-map-trades, …).

## Part A — unsw-swarm/tools/meowbot.py (+ meow_chat.py, meow_ui.py); edit files only, never start/stop the bot, do not commit
1. Helper `card_ref(issue_or_number)` → "#27 passage", from the name:* label. Fallback when there is no label: "#27" + the first 3–4 words of the title.
2. Use it in EVERY message that mentions a card:
   - state pings (needs-info, needs-look, tested, kept, rejected, inconclusive, candidate);
   - ETA posts ("⏱ #27 passage: local A/B started, about 42m …");
   - failure posts;
   - /board, /loop, /status;
   - /answer echo;
   - /meow brain;
   - new-card posts.
   Keep the full title only on the new-card post and inside embeds, as a second line.
3. New cards made through /hypo and /hypo-max get a `name:<slug>` label automatically: 1–2 lowercase words, hyphenated, ≤16 chars, unique among open cards. Derive it with the existing light Sonnet call used for translation, or a simple heuristic if that fails. The reply to the user shows the name. /board-edit can change it.
4. PRs:
   - candidate cards are titled "#27 passage" with the PR as a link ("PR" as link text, no bare PR number);
   - posts for normal PRs (opened/merged/closed) show the linked card refs when the PR title/body mentions "#N" of a known card, otherwise the PR title. Never lead with the PR number.
5. Offline tests for card_ref, slug generation/uniqueness and the message formats. ALL checks must pass: tools/check-*.py, tools/test_*.py, data/codex/check-*.py.

## Part B — battlecode loop; edit ONLY in the worktree ~/meow-dev (branch dev/names); never the live checkout; commit there, do not push
1. work/loop/runner.py + prompts:
   - cards the loop creates (ladder AI cards) get a `name:<slug>` label (same rules; the ladder prompt returns a slug per card, validated by the runner);
   - comments and status/events lines use "#27 passage";
   - candidate PRs are titled "Candidate #27 passage", and the PR body's first line links the card;
   - the events.jsonl `title` field carries the short ref too (add `name`).
2. work/board.py: `next`/`state`/`report` print the ref.
3. docs/LOOP.md + LOOP.zh.md: 4 lines on the naming rule (card number + short name; PR titles start with the card ref).
4. Tests; `python3 -m unittest discover -s work/loop/tests` must pass.

## Part C — unsw-swarm/data/guide/guide.html (EN/中文): one short paragraph on the naming rule near the top. Do not publish.

Write a ≤10-line note to data/codex/report-names.md listing every changed/new file in both repos.
