# Card 47 fourth build in 15 online games: does it cost anything, and does it stop the baby going back in?

Sets of 15 online games against Big Bobs Bots (team 946), the same 15 maps, 7-8 Oct (we are team 1119):
- new = current main (v47 + card 48 first build + card 51) + card 47 fourth build, UPDATE_MAP on:
  `data/online/smoke/um47d-bob1-new/`
- main51 = current main without card 47: `data/online/smoke/sr51-bob1-new/`
- main48 = main before card 51: `data/online/smoke/qn48v1-bob1-new/`
- main47 = main before cards 48 and 51: `data/online/smoke/qn48v1-bob1-old/`
(`M<id>.replay`, `game-<id>.json`.) Unpaired games: the spread between the three main sets is the size of luck.
You did the same job for the third build: `data/local/card47/online-v3/` (analyze.py, report.py, table.md);
reuse that code. The fourth build differs: a dragon standing in a dead end sends the dead-end message in ONE
direction only, into her own neck (it comes out at her tail, where a baby would be), on that turn and the 2 after
and again when she splits in there; nobody passes it on; the other three pings are main's. Builder's check and
definitions: `~/meow-cards/card-47/work/card_47_check.py`, and the look note and check.json in the
newest `~/meow-loop-out/card-47/attempt-*/`.

## Count
A. The one behaviour the card is now about, in every set (the three main sets give the rate without the card):
   dead-end splits (the mother splits while standing in a dead end); in the new set, how many of those children
   were hit by her message; children that walk back into that same dead end within 30 rounds, told against not
   told against the main sets; and of those, how many died or split again inside. Also wasted stays (fewer than 2
   pearls eaten, then split or died inside) per 1,000 dragon turns in each set.
B. Cost, per game means for each set: wins; our total length and longest at the end; pearls eaten by r100 and
   r300; dragons alive at r100, r200, r300; queen pings and leader reports sent per game and new-kind messages
   (the third build cut queen pings from about 1,700 to 270 a game; this build should not); deaths by cause per
   1,000 dragon turns; turns out of time.
C. One line per map: result in each set, pearls by r100 in new and main51.

## Output: `data/local/card47/online-v4/table.md` (55 lines or fewer), English
Tables A, B, C, then at most five plain sentences: does the baby case show (with the counts; say plainly if the
cases are too few to tell), and which cost measures of the new set fall outside the range of the three main sets.
Counts only. `rows.jsonl` too. Last step: `data/local/card47/online-v4/done.txt`.
Write only under `data/local/card47/online-v4/`. No network, no posts, no games.
