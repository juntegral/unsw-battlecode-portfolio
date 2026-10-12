# Builder: psplit

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules) and `data/codex/astra/worstmaps/report.md` (the rows on two-dragon starts
and on breeding beside portals, and its one test card with `evidence.md`) first. Write only under `data/codex/build/psplit/`.

Why: on maps where each side starts with two short dragons our first split comes at a median r65 (Tower Defense) against r41 for
the opponents, and at r100 we hold 2.9 dragons against 17.9. One measured cause: a non-queen of length 4 or more whose tail is
beside a portal is refused the split although an ordinary free edge is open (the report cites lines 1515-1519 of one7-bot's
main.cpp and games 1472756 r35-36 #6, 1480434 r26 #12, 1471465 r32-33 #11).

Task: in `main.cpp` (the team's working source, every switch OFF by default; `main.base.cpp` is the same file untouched) add
`constexpr bool SPLIT_PORTAL_OK = false;` implementing the report's card exactly: the portal-adjacent refusal no longer applies
when the child that would be born at the tail has at least one ordinary (non-portal) free neighbour cell that is not a dead end
by the checks the split code already makes. Change nothing else about splitting.
Requirements: switch false = same program as `main.base.cpp` (guard with the constant; compile both with `c++ -std=c++20 -O2` to
the same output file name, compare sha1, report it); `main.on.cpp` with the switch true compiles; no comments beyond one short
line, no map names, no size tables. Write `diff -u main.base.cpp main.cpp > psplit.diff` and `done.txt`: lines changed, sha1
result, whether the three cited turns would now split (work it out from the replays under `data/online/`), what would show it
is wrong (children dying within 3 rounds of a portal-side split). You cannot play games on this machine; do not try.
