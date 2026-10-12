# Card 47 third build in 15 online games: does it do its job, and what does it cost?

Three sets of 15 online games against the same opponent (Big Bobs Bots, team 946) on the same 15 maps, all 7 Oct:
- new = current main (v47 + card 48 first build) + card 47 third build, UPDATE_MAP on:
  `data/online/smoke/um47c-bob1-new/` (`M<id>.replay`, `game-<id>.json`; state `data/online/smoke/um47c-bob1.json`)
- main48 = current main without card 47 (v47 + card 48 first build): `data/online/smoke/qn48v1-bob1-new/`
- main47 = v47, the main before card 48: `data/online/smoke/qn48v1-bob1-old/`
We are team 1119; find our side per game yourself. Online games are not paired move for move: the opponent plays
differently every game, so differences between sets mix the build with luck. Say so where it matters.

What card 47 is meant to do (third build; issue text and the builder's notes are in
`~/meow-loop-out/card-47/attempt-3/` : `look.md`, `check.json`, `mechanism-summary.json`, and the
source diff `attempt3-main.diff` if present, else compare `~/meow-cards/card-47/mybot2/main.cpp`
with `~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp`):
(1) any dragon standing in a dead end pings that dead end in all four directions every turn; a teammate that
hears a new one passes it on once; (2) a dragon that knows a dead end holding fewer than 2 pearls pays a cost of
2 lengths to step in (a cost, not a wall); (3) refill tiles are sent only by a mother that splits while trapped in
a dead end, and a newborn told one heads for it when nothing else is in reach.
The loop's own checker is `~/meow-cards/card-47/work/card_47_check.py` (written for paired local
replays). Reuse its definitions and as much of its code as runs on online replays (same replay format; sonar rays
and which dragon a ray hits are in the replay). Where a definition needs the base game of a pair, compute it for
each set on its own and compare the sets instead.

## Count
A. The job, on the new set (and the same counts on main48 and main47 where they exist without the switch, as the
   "before" numbers): stays in a dead end and how many had an alert; alerts sent, true on the real map, heard by a
   teammate, passed on; dragons told a dead end for the first time; arrivals at a way in by told and by untold
   dragons and the share that walked in; told-and-charged arrivals that walked in, and how many had an enemy head
   within 3 tiles; wasted stays (fewer than 2 pearls eaten, then split or died inside) per 1,000 of our dragon
   turns; pearls eaten on stays and lengths lost inside; refill tiles told at a trapped mother's split, babies
   told, babies that stood on a told tile within 30 rounds, pearls eaten there.
B. Downsides, all three sets, per game means: result and how the game ended; pearls eaten by r100 and r300;
   dragons alive at r100, r200, r300; our deaths by cause (wall, own body, another body, head-on as mover, head-on
   hit, no action, timeout, unpaid sprint, illegal split) per game and per 1,000 dragon turns; turns that ran out
   of time or made no action when a move existed; sonar messages sent per game by kind (leader reports and the new
   kind), since the new pings share the same channel; our queen alive at the end; our longest at the end.
C. Per map, new against main48: result, pearls by r100, dead-end stays wasted, deaths in dead ends.

## Output: `data/local/card47/online-v3/table.md` (70 lines or fewer), English
Tables A, B, C, then "What the counts say" in at most six plain sentences: which parts of the job show in these
games and which do not, and which downside measures moved by more than the spread between main48 and main47
(that spread is the size of luck here). Counts only; no opinion on shipping. Also `rows.jsonl` (one row per game).
Last step: `data/local/card47/online-v3/done.txt` (one line).
Write only under `data/local/card47/online-v3/`. No network, no posts, no games.
