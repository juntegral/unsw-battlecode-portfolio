# Builder: war

Read `data/codex/astra/ASTRA-COMMON.md` (Game, Bot, Rules) and the earlier builder's notes `data/codex/build/avenge/done.txt`
first. Write only under `data/codex/build/war/`.

Why: the first tiebreak is the queen. When our queen is dead and the enemy queen is alive we have lost unless she dies; total
length and the longest dragon are then worth nothing. `QUEEN_AVENGE` (in this file) arms a hunt for dragons of 4 or less within a
chase distance, and it did not win the games it was built for: against team kraken we ended Portals 1485181 with 11 dragons
against ONE enemy dragon, her queen 8 long, and lost; Australia 1485169 with 42 dragons / 481 length against 10 / 82 and lost
(replays in `data/online/smoke/one8-k1-old/`, bot `data/online/smoke/one8-bot/main.cpp`).

Task: in `main.cpp` (the team's working source = live one9's source with every switch OFF by default; `main.base.cpp` is the
same file untouched) add `constexpr int QUEEN_WAR = 0;` (0 = off; a positive value L = the longest dragon that joins, test 8).
First work out from the code and from the two replays why the current avenge would not have armed or not have killed there
(signal not shared, chase distance, length limit, nobody knowing where she is) and write that down. Then, when QUEEN_WAR > 0:
- arming: as `QUEEN_AVENGE` (our real queen believed dead, enemy queen not known dead), plus any cheaper sure signal you can find
  (for example the engine telling a dragon which ids of its side are alive, or the unit count dropping in a way that names her;
  check the helper API). Every dragon that learns it re-broadcasts it by the existing sonar fields so the whole side arms.
- every non-queen dragon of length L or less (the leader too if it is that short) stops harvesting and goes for her: to her
  last known cell (shared by sonar; keep the freshest sighting), no chase-distance limit; when no sighting is fresher than 30
  rounds it explores toward ground the side has not seen for longest. It eats only pearls that are on its way.
- it rams her head whenever it can reach it this turn, free steps first, paid steps if it has the length; a dragon that cannot
  reach her head moves to cut her free neighbours when another of ours is already in reach of her.
- dragons longer than L keep normal play (they are the longest-dragon tiebreak once she is dead). When she is known dead,
  everything disarms.
Requirements: `QUEEN_WAR = 0` = same program as `main.base.cpp` (guard with the constant; no state updated when off; compile both
with `c++ -std=c++20 -O2` to the same output file name, compare sha1, report it); `main.on.cpp` with `QUEEN_WAR = 8` compiles and
works with `QUEEN_HUNT` false and `QUEEN_AVENGE` either 0 or 8. CPU: reuse the existing `qh_*` floods and routes; nothing new
per turn while disarmed. No comments beyond one short line, no map names, no size tables.
Write `diff -u main.base.cpp main.cpp > war.diff` and `done.txt`: lines changed, sha1 result, why the old rule failed in the two
games, the arming signal and how fast it spreads, what to count in a replay (rounds from our queen's death to the first of ours
within 3 steps of her, her death round), what would show it is wrong. You cannot play games on this machine; do not try.
