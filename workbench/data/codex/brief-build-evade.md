# Builder: evade

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules) and `data/codex/astra/evade/report.md` (all of it, with its code notes)
first. Write only under `data/codex/build/evade/`.

Files: `main.cpp` is the team's working source, every switch OFF by default, already carrying an earlier builder's switch
`QUEEN_EXIT_KEEP` (off). `main.base.cpp` is the same file untouched; `main.orig.cpp` is the source before either change.

Task A, switch `SHORT_EVADE` (`constexpr bool SHORT_EVADE = false;`): the report found that of 559 rams on our non-queen dragons 329
had a free way out, because a short dragon prices only the one-step reach of enemies whose visible body is under 5 and nothing
else. Implement the rule broader than the report's strict card:
- who: a non-queen, non-leader dragon of length 4 or less, on its final choice of move (ordinary step, stride, portal step; not a
  ram or hunt it chose on purpose, not a trade target, not a queen-defence move).
- danger: a destination cell that a visible enemy head can enter on its next turn with its free steps, ceil(L/4) with L the
  enemy's known length (use the largest length the side has seen for that id, at least what is visible; any body size counts,
  including 5 and over), walking over cells that are free now. Do not count paid sprint steps.
- when: the heads the mover sees (itself included) are not more than the enemy heads it sees, and no mate head is nearer to that
  destination than the enemy head is.
- what: such a move is rejected if another legal, not rejected move exists whose destination is outside that reach and is not a
  dead end by the checks the bot already makes; among those keep the bot's own score order (so a safe pearl still wins).
  If there is none, move as before.
Task B, switch `PORTAL_ID_GUARD` (`constexpr bool PORTAL_ID_GUARD = false;`): in `remember_portal`, when on, ignore a portal id of
`2 * cells` or more before the edge table is resized (see `data/codex/astra/unseen/portal_guard.patch`).
Requirements for both:
- With both switches false the compiled program must be the same as `main.base.cpp`: guard every new statement with the constant,
  no new state updated when off. Check with `c++ -std=c++20 -O2` on both files and compare the binaries' sha1 (equal), and say so.
  Then `main.on.cpp` with both true must compile.
- Keep CPU small: reuse the bot's existing reach or flood helpers; at most one bounded search per visible enemy head per turn.
- No comments beyond one short line each, no map names, no size tables. Match the code style around it.
- Write `diff -u main.base.cpp main.cpp > evade.diff` and `done.txt`: lines changed, the sha1 result, the move paths covered and
  not covered, and what the lead should count in a replay to see it fire (and what would show it is wrong).
You cannot play games on this machine; do not try.
