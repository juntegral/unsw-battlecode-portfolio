# Builder: hidden (a long dragon assumes a size for an enemy whose body runs out of its view)

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules), `data/codex/astra/CARDS.md` and `data/codex/build/seen/done.txt`
(the builder before you: its switch THREAT_SEEN_SIZE does not cover the case it was built for, because the attacker was only
ever seen as a head, one part, so the remembered size is 1 as well). Write only under `data/codex/build/hidden/`. `main.cpp`
there = the `seen` builder's result (THREAT_SEEN_SIZE present, off); `main.base.cpp` = the team's working source untouched;
`one14.switches` = the live switch values.

Why (measured, `data/codex/astra/weak13-opus/rammed-battles.txt`): our dragons of 8 or longer were rammed 33 times in two
battles; the attacker was fully in view 3 times, partly 19, not at all 11. A head whose body leaves our 7 by 7 view has an
unknown length, and the bot sizes it by the parts it sees, so a 6-long enemy seen as a head gets the reach of a 1-long one.
Case to cover: game 1513123 (replay under `data/online/live-one1/b1513119/`), round 460 to 461: our dragon 1234 (50 long) at
(4,4) steps east to (5,4); enemy 1112 (6 long, head at (6,7), only its head in view) reaches (5,4) with 2 free and 2 paid steps.

Task: add `constexpr int THREAT_HIDDEN_PARTS = 0;` (0 = off; a positive value = the assumed number of parts, test 8). When on,
and only for OUR dragons of BIG_ESCAPE_MIN_LENGTH or longer (if that constant is 0 use 8), an enemy head in view whose body is
not completely in view (its visible parts do not end in a visible tail: decide this from what the view gives, and say how) is
sized as the larger of what the bot uses now and this value, in `map_threats` and in the reach map `long_escape` uses. Work out
from the code whether the reach the long dragon then assumes includes the enemy's PAID steps (in the case above the hit needed
2 free + 2 paid); if the long-dragon escape only counts free steps, add under the same switch the paid steps a dragon of the
assumed size can afford up to the same cap the queen's rule uses (QS_PAY_REACH), again only for our long dragons. Short dragons
and the queen's own rules are unchanged.
Requirements: value 0 = same program as `main.base.cpp` when THREAT_SEEN_SIZE is also off (compile both with
`c++ -std=c++20 -O2` to the same output file name, compare sha1, report it); a copy with the value 8 on top of `one14.switches`
compiles. CPU: no new search. No comments beyond one short line, no map names, no size tables.
Write `diff -u main.base.cpp main.cpp > hidden.diff` and `done.txt`: lines changed, sha1 result, how "body not completely in
view" is decided, whether the step at 1513123 r460 is now refused or escaped and what the dragon does instead (reconstruct from
the replay as the builder before you did, `data/codex/build/seen/replay_check.py`), and what would show the switch is wrong
(our long dragons fleeing from every lone head: their pearls per round and our longest dragon at r200 falling). You cannot play
games; do not try.
