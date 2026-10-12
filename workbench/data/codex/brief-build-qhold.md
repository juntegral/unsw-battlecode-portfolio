# Builder: qhold

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules), `data/codex/astra/CARDS.md`, and the notes of the builders whose signals
and code you reuse: `data/codex/build/war/done.txt` (how "our queen is dead" / "their queen is dead" is known and shared),
`data/codex/build/qboot/done.txt` (late feeding of a short queen, and her splits while being fed).
Write only under `data/codex/build/qhold/`. `main.cpp` is the team's working source (every switch OFF by default);
`main.base.cpp` is the same file untouched.

Why (measured on 95 local games of our newer versions against an older one): the newer version kills the enemy queen first in 27
of 47 games and then wins only 12 of them, because it loses its own queen afterwards: 15 of its 28 losses are "their queen died
first, then ours", 8 of those with our queen 2 long. Once the enemy queen is dead our queen dies 2.61 times per 100 rounds at
length 2, 0.87 at length 3 and 0.08 at length 4 or more. She gets short by ordinary splits (a 4-long queen splits into 2+2
while the team is small), by escape splits, and by paying segments to sprint. With their queen dead and ours alive we win on
the first tiebreak if she simply survives, so from that moment nothing is worth making her shorter.

Task: add `constexpr int QUEEN_HOLD_LEN = 0;` (0 = off; test value 4). When positive, and this dragon is our REAL queen, and the
enemy queen is known dead (use the signal the hunt code already keeps and shares for "enemy queen dead"; say exactly which, and
how soon after her death our queen learns it: if she can only learn it by seeing it, add the smallest relay through the existing
queen-ping / leader-ping fields, guarded by the switch):
- she makes no ordinary split and no wait-split that would leave her shorter than `QUEEN_HOLD_LEN`, and no split at all while
  she is at or below it;
- she does not pay a segment for a sprint that would take her below `QUEEN_HOLD_LEN`, unless every unpaid move is rejected by
  her safety rings (then she moves as now);
- from that round on she counts as a feeding target for mates of 2 or 3 as under `QUEEN_BOOT_LEN` whatever the round (the
  feeding phase starts for her at once), until she is `2 * QUEEN_HOLD_LEN` long; every other feeding condition stays.
Nothing changes while the enemy queen is alive or not known dead.
Requirements: value 0 = same program as `main.base.cpp` (guard with the constant; no state updated and no sonar sent when off;
compile both with `c++ -std=c++20 -O2` to the same output file name, compare sha1, report it); `main.on.cpp` with the value 4
compiles, with `QUEEN_BOOT_LEN` 6 and `QUEEN_SURE_LEN` 64 as in the live bot. No comments beyond one short line each, no map
names, no size tables.
Write `diff -u main.base.cpp main.cpp > qhold.diff` and `done.txt`: lines changed, sha1 result, the signal and its delay, every
split and pay path of the queen you covered and any you could not, and what to count in a replay (games where we kill their
queen first and still have ours at the end; her deaths per 100 rounds after theirs is dead, by her length), and what would show
it is wrong. You cannot play games on this machine; do not try.
