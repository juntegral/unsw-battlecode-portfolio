**What this is, in three lines**
- Tried: `main` follows the final live bot. one21 (submission 21857, live since 14:49 KST on 9 Oct, the last upload before the 15:00 deadline) = this branch's `mybot2/main.cpp` with the values in `work/server_profile.txt`. Five commits following the live versions of this afternoon (one15, one16, one17, one18+one19, one20+one21).
- Worked? Every new switch is off by default and with all of them off the program is the same binary as before. `python3 work/server_bot.py OUT --no-compile` on this branch gives a source identical to the uploaded `one21-bot/main.cpp` (0 lines differ).
- Who decides: jun or Zhe merges. Nothing on the server changes when this is merged.

**What changed since `main` (one14), newest last**
"Queen" = the dragon with the lowest starting id; the longer queen is the first tiebreak and a dead queen counts 0.

| version | change | why | check |
|---|---|---|---|
| one15 | `TERRITORY_DECAY` removed from the profile | starved us on Queen Of Spades (3 dragons at r100) | pearls by r100 there 8 / 3 with it, 44 / 40 without (local, both seats); online 17 to 57 |
| one16 | `QUEEN_NO_BLIND_PORTAL` (new) | on maps of 600 cells or fewer the queen scouted portals with an unseen far side into closed rooms; she died in 30 of 30 Portals games | local Portals: queen dead by r100 6 of 7 to 1 of 8, wins 2 of 7 to 5 of 8; online no queen portal step in r0-99 |
| one17 | `QS_SHED_MAX 9` (new) | a queen of 10 or longer split down to 2 when exposed: 21 times in 474 games, 18 lost, 15 while leading | one17 plays the same game as one16 in 8 local games; online the sheds are gone, long queens die about as often as they shed before (level so far) |
| one18 | `QUEEN_CORRIDOR_MATE` (new) | the queen's dead-end guard kept a fatal step when her other way ran past a mate's body; three Maze games thrown from a lead | fired in 2 of 17 local pairs, queen lived r155 to r192 and r258 to r331; the other 15 pairs identical |
| one19 | `QUEEN_DEAD_ALL` removed | on small maps the queen took every small room for a dead end; from a start box opening through a portal into a small room the side never left | 20 pairs against old main: pearls by r100 522 to 1036, wins 8 to 12, no pair worse |
| one19 | `CENTER_MAX_CELLS 100000` | on a 1012-cell map with a closed start room nobody left the room in 500 rounds (at 968 cells they did) | that map: out at r26, win; ladder maps level (square maps identical games) |
| one19 | `QUEEN_NO_RAM` (new) | a head into a head kills both dragons; a trapped queen took the plain dragon's hunt and ram paths (8 percent of her deaths) | 9 of 9 local pairs identical against old main; no path without an action (code audit) |
| one19 | `QUEEN_BLIND_STALL 20` (new) | the one16 rule starved a side whose only way out of its start box is an unseen portal; lifted after r20 while we have 2 dragons or fewer | Portals and Stripes identical with and without; the blind start box eats a little, still lost |
| one20 | two completions in the code, same profile | under `QUEEN_NO_RAM` the trapped queen also stops marking trade and hunt targets (she was still pulled toward a head by one step); `QUEEN_BLIND_STALL` acts only from its round to five times its round | 17 local games identical to one19 |
| one21 | `QS_LONG_WAIT` (new) | Zhe, match 1532574: a queen of 11 stepped into a tile a visible enemy could sprint to. An exposed queen longer than `QS_SHED_MAX` with no escape now stays and splits off 2 cells instead | 4 short local games identical to one20; the effect itself is NOT measured, there was no time |

In the code but off in the profile (built and tested today, not kept): `QUEEN_CORRIDOR_TREE`, `SPLIT_KNOWN_TAIL`.

**Known limits**
- One measured cost: in a head to head on Portals the arm without `QUEEN_DEAD_ALL` lost both seats (queen died late); on Stripes it won both.
- Not fixed: 7x7 maps (we lose to old main), start rooms where the queen stays behind, Tower Defense (dragons will not enter the small pearl rooms), and our queen still dies in most of our losses.
- Seven local ladder map files are rebuilt from replays, so their pearl supply is an estimate; comparisons between builds on the same file are what counts.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
