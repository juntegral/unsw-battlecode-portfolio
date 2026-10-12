# Builder: seen (a long dragon sizes an attacker by what was seen of it, not by the parts in view now)

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules), `data/codex/astra/CARDS.md`, and the notes of the builder whose
machinery you touch: `data/codex/build/bigesc/done.txt` if it exists (otherwise find the BIG_ESCAPE switches in the source).
Write only under `data/codex/build/seen/`. `main.cpp` there is the team's working source (every switch OFF by default);
`main.base.cpp` is the same file untouched. The live bot is that source with the switch values in `one14.switches` (same folder).

Why (measured on two lost battles of the live code, `data/codex/astra/weak13-opus/rammed-battles.txt`): our dragons of 8 or
longer were rammed 33 times; the attacker was fully in view 3 times, partly 19, not at all 11. The escape rule for long dragons
(`long_escape`, switches BIG_ESCAPE_STEPS / BIG_ESCAPE_MIN_LENGTH) returns unless `threat_at(chosen)` is non-zero, and
`map_threats` sizes an enemy by the body parts visible this turn (`visible_parts`; the floor of 4 parts applies to their queen
only). An enemy of 6 with one part in view therefore gets the free-step reach of a 1-long dragon and our 50-long dragon reads
the cell next to it as safe. The source already keeps "an enemy's size as this dragon has seen it, kept all game" (card 54).

Task: add `constexpr bool THREAT_SEEN_SIZE = false;`. When on, wherever `map_threats` (and any helper it shares with
`long_escape`) turns an enemy head in view into a reach, size that enemy by the larger of its parts in view now and the size
this dragon remembers for that enemy id (the card 54 memory; if that memory is only filled under another switch, fill it under
this one too). Nothing else changes: same reach formula, same paid-step terms. It must apply to every dragon of ours that
uses `map_threats`, not only long ones.
Requirements: off = same program as `main.base.cpp` (guard every new line with the constant; no state updated when off; compile
both with `c++ -std=c++20 -O2` to the same output file name, compare sha1, report it); a copy with the constant true compiles.
CPU: no new search, one lookup per enemy head. No comments beyond one short line, no map names, no size tables.
Write `diff -u main.base.cpp main.cpp > seen.diff` and `done.txt`: lines changed, sha1 result, which reach computations now use
the remembered size, whether the ram at game 1513123 round 461 (our dragon 1234, attacker 1112, replay under
`data/online/live-one1/b1513119/`) would now be read as a threat, and what would show the switch is wrong (our pearls per game
falling because dragons shy away from enemies that have shrunk since they were last seen). You cannot play games; do not try.
