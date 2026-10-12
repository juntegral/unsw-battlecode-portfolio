# Builder: qsight

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules), `data/codex/astra/CARDS.md`, the round synthesis
`data/codex/astra/sweep/0436/synth/report.md` (first row and the loss reports it points to: games 1487478, 1487479, 1488290) and
`data/codex/astra/unseen/report.md` (the rows on sonar ranges and on the 12-bit sight packing) first.
Write only under `data/codex/build/qsight/`. `main.cpp` is the team's working source (every switch OFF by default; it already
holds REACH_EATS, CUT_BODY_LEN, QUEEN_WAR and the rest); `main.base.cpp` is the same file untouched.

Why: with the reach fixes live, what still kills our queen is an attacker she cannot see at all: it starts outside her 7 by 7,
eats the pearls on its way and hits her (three of one9's six losses to team kraken). Her rings are built only from enemy heads
in her own view.

Two switches, each off by default and independent:
A. `constexpr int QUEEN_FAR_HEADS = 0;` (0 = off; a positive value = how many rounds a shared sighting stays valid, test 2).
   When on, the real queen's danger computations (the same ones REACH_EATS and CUT_BODY_LEN feed) also use enemy heads that
   MATES have seen within that many rounds and told the side about. Find what the sonar already carries (leader ping, queen
   ping, mouth, ghosts, the `SHARE_SIGHT` path that is off) and use the cheapest existing channel; if none carries enemy head
   positions, add the smallest message: a mate that sees an enemy head within 8 cells of where it last knew our queen sends
   that head's cell and length once, with priority below the existing queen-death and queen-sighting messages. Respect the
   codec limits (coordinates, the 128-cell sonar gate) and do not reuse the 12-bit sight packing unless you also fix its
   sentinel problem on 4096-cell maps described in the unseen report. An enemy known this way is treated like a cut body
   (length at least `CUT_BODY_LEN` when that is on, else what was reported) standing on its reported cell.
B. `constexpr int QUEEN_EDGE_REACH = 0;` (0 = off; test 3). When on and no enemy head is known near her, a pearl chain that
   leads from the edge of what she sees to a cell beside her destination counts as a possible approach: a destination that an
   imagined enemy of length 3 entering at the view edge could reach within that many steps by eating visible pearls on the way
   is avoided WHEN another legal, not rejected move outside such reach exists; otherwise she moves as now. Bounded: only the
   pearls in view, at most that many steps.
Requirements: with both 0 the program is the same as `main.base.cpp` (guard every statement with its constant; no state updated
and no sonar sent when off; compile both with `c++ -std=c++20 -O2` to the same output file name, compare sha1, report it).
`main.on.cpp` with QUEEN_FAR_HEADS 2, QUEEN_EDGE_REACH 3, CUT_BODY_LEN 4, REACH_EATS true must compile. CPU: no new flood.
No comments beyond one short line each, no map names, no size tables.
Write `diff -u main.base.cpp main.cpp > qsight.diff` and `done.txt`: per switch the lines changed, the channel used and its
limits, which of the three cited hits each switch would have flagged on her last own turn (work it out from the replays in
`data/online/smoke/one9-k1-old/` and `data/online/live-one1/b1488287/`), and what would show it is wrong (her pearls per game
falling, sonar crowding out the leader ping). You cannot play games on this machine; do not try.
