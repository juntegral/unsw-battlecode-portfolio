# Brief: who picks up the pearls dropped when a dragon dies (online replays)

Read-only counting. Work in this repository (unsw-swarm). Write only inside `data/online/smoke/drop-analysis/` (create it). No commits, no network, no game runs, never read `docs/api.txt` or `docs/discord.txt`. Leave every other file alone. Do not interpret; count.

Same 105 games as `data/codex/brief-fountain-count2.md` (our team 1119 against team 946, seven folders). Reuse `data/online/smoke/fountain-analysis-2/count.py`: file reading, sides, eats from `tileChange`, death causes (head-on, wall, enemy body, own body, other) and the fountain tile sets.

A teammate's claim to test: when our dragons die in a head-on, most of the pearls they drop are picked up by the opponent.

1. First establish from the rules (`rules/ALL.md`, the death and pearl sections) and from the replay events how a death turns into pearls on the map: which tiles, how many, in which event. Describe it in two lines and check it by hand on one death.
2. For every death, of our dragons and of theirs: cause, round, dragon length, number of pearls dropped. For each dropped pearl: who ate it (us, them, nobody before the game ended), and how many rounds it lay there.
3. Tables for our deaths and for their deaths, by cause, pooled and split into the five big maps (Australia, Around UNSW, Schooltime, Islands, Slithery Fight) and the other ten: deaths, pearls dropped, share eaten by us / by them / by nobody, median rounds until eaten, share eaten within 3 rounds and within 10 rounds. Add the same split by round window (r1-50, r51-100, r101-200, r201-end).
4. For head-on deaths, where both dragons die: pearls dropped by ours and by theirs in the same collision, and who ate each side's pearls. Net pearls per head-on for us and for them (pearls eaten from that collision by each side).
5. Per game on the big maps: the share of all pearls each side ate that were dropped pearls rather than spawned ones.
If a dropped pearl cannot be told from a spawned one on the same tile, say how you separate them and what share stays unknown.

Checks: print the raw events of three head-on collisions and follow every dropped pearl by hand.

Output (write `summary.md` last): `count.py` and `summary.md` in the folder above, pooled tables first, then big maps against the rest, then per map, then the hand-checks and what could not be measured.
