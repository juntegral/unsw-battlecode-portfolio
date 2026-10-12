# Builder: orbit (a dragon stops circling a pearl it is not allowed to take)

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules), `data/codex/astra/CARDS.md`, and the notes of the builder whose
rule is involved: `data/codex/build/pocket/done.txt` (POCKET_KEEP_OUT). Write only under `data/codex/build/orbit/`. `main.cpp`
there is the team's working source with every switch OFF by default (it already holds two new switches of this morning, off);
`main.base.cpp` is the same file untouched. The live bot is that source with the switch values in `one14.switches`.

Why (measured on the live code, `data/codex/astra/stuck-opus/` has the detector and tables): our short dragons (2 or 3 long)
circle a 2 by 2 block beside a pearl that sits in a dead-end cell (kelp on three sides) for 100 to 300 rounds. Examples, replays
under `data/online/smoke/one14-c1-old/`: M1517691 (Around UNSW) dragon 31 rounds 4-130, pearls at (33,21) and (33,22) born
rounds 1-2 and never eaten; M1517687 (Islands) dragons 230 and 484 rounds 235-471, pearl at (39,18); M1517694 (Schooltime)
dragon 91 rounds 188-499. Over 14 games of the live bot, loops of 30 or more rounds without eating are 9.8 percent of our
dragon-rounds against 5.6 percent of the opponents'. Cause as read from the code: the target search and EAT_FIRST still choose
that pearl (`target_reachable`, around line 4939 of the live source `data/online/smoke/one14-bot/main.cpp`, only knows closed
rooms, not a cul-de-sac), while `keep_out_of_pocket` (around lines 940-1045, switch POCKET_KEEP_OUT, live) replaces the
entering move by the next best one every turn. So the dragon wants the pearl forever and is refused forever. Turning
POCKET_KEEP_OUT off is not the remedy: it would walk in and die.

Task: add `constexpr int POCKET_PEARL_SKIP = 0;` (0 = off; a positive value = rounds, test 40). When on: whenever
`keep_out_of_pocket` (or any other final veto that replaces a move whose purpose was a pearl: check which vetoes can do this
and say which you covered) refuses the step that would take or approach a target pearl because the pearl's cell is a pocket
the dragon may not enter, that dragon remembers the pearl's cell as "not for me" for that many rounds, and for that time the
target search, EAT_FIRST, the lunge and any pearl score ignore that cell for this dragon (other dragons and other pearls are
unaffected; a longer or shorter teammate may still judge it differently). Also when on: if a dragon has not eaten and its head
has stayed within the same 6 cells for 12 rounds while a pearl target was set, it drops that target cell for the same number
of rounds (this is the safety net for refusals you did not find). Memory is per dragon, small and bounded (a short fixed list).
Requirements: value 0 = same program as `main.base.cpp` (guard every new line; no state updated when off; compile both with
`c++ -std=c++20 -O2` to the same output file name, compare sha1, report it); a copy with the value 40 on top of
`one14.switches` compiles. CPU: no new search. No comments beyond one short line, no map names, no size tables.
Write `diff -u main.base.cpp main.cpp > orbit.diff` and `done.txt`: lines changed, sha1 result, which vetoes and which target
choosers are covered, what dragon 31 of M1517691 does at rounds 4-20 with the switch on (reconstruct that turn's view from the
replay as the earlier builders did: `data/codex/build/hidden/replay_check.py`, `replay_probe.cpp`), and what would show the
switch is wrong (pearls in safe pockets left uneaten: our pearls per game falling on maps with many small rooms). You cannot
play games; do not try.
