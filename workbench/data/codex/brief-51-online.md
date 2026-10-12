# Card 51 online: the walled-start games, one line each

Four sets of 15 online games against Big Bobs Bots (team 946) on the same 15 maps, 7-8 Oct:
- sr51 = current main + card 51 second build (TR_STALL_RELEASE on): `data/online/smoke/sr51-bob1-new/`
- main48 = current main: `data/online/smoke/qn48v1-bob1-new/`
- main47 = main before card 48: `data/online/smoke/qn48v1-bob1-old/`
- um47 = current main + card 47 third build: `data/online/smoke/um47c-bob1-new/`
(`M<id>.replay` and `game-<id>.json` in each; we are team 1119, find our side per game.)
Card 51 is about a start area closed by kelp with one narrow way out ("walled start"); the loop's checker
`~/meow-cards/card-51/work/card_51_check.py` defines the home room, "a head outside", the stall
test, the pin zone and the gates for local replays. Reuse its definitions and code on these online replays
(same replay format).

## Count
1. For every game in the four sets whose layout has a walled start for us by the checker's own test (expected:
   the Tower Defense game of each set, maybe others; list which layouts qualify): result and how it ended; the
   first round one of our heads is outside the home room (or "never"); share of our turns in rounds 30-59 that
   start outside; pearls we ate by r50 and r100; our dragons at r100; distinct tiles our dragons visited by r100;
   our wall and own-body deaths in rounds 0-100; our queen: death round and cause, or alive. And the same first-out
   round and pearls by r100 for the opponent.
2. For all 15 games of each set, as one line per set: our wall and own-body deaths in rounds 0-100 per game, our
   pearls by r100, and (sr51 only) the share of centre-rule turns on which the stall test was true, if the
   checker can compute it without the paired base game.

## Output: `data/local/card51/online/table.md` (30 lines or fewer), English
Table 1 (one line per walled-start game, sets side by side), table 2 (one line per set), then two plain sentences
on what differs, counts only. Unpaired games: say so. `rows.jsonl` too. Last step:
`data/local/card51/online/done.txt` (one line). Write only under `data/local/card51/online/`. No network, no games.
