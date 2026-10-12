# Astra analyst: worstmaps

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `worstmaps`. Live bot: one7 (`data/online/smoke/one7-bot/main.cpp`).

Tonight's record by map over 256 games (each game id once; mostly against top-15 teams): Australia 1 of 18, Tower Defense 1 of 15,
Stripes 2 of 18, Around UNSW 2 of 15, Schooltime 2 of 14, Slithery Fight 3 of 18, Trauma 3 of 17, Maze 3 of 15; against Default 9 of
19 and Devil 10 of 19. The qualifier is on unseen maps, so the question is not how to fix these maps but which general weakness
each exposes: an unseen map with the same feature will beat us the same way.
1. For the five worst maps: the features of the map (size, open or corridors, portals, pearl density and timers, start layout
   and distance between the sides) and, over all one5/one6/one7 games on it, how we lose: the round the game turns, dragons and
   length both sides at r50/r100/r150/r300, our deaths by cause against theirs, where on the map our dragons are against theirs
   (own half, far half, share of bearing tiles nearest to us). Compare with Default and Devil where we hold.
2. Group the findings by FEATURE, not by map: for example "large open ground: we cover x% of bearing tiles at r100 against y%",
   "two-dragon start: first split at round a against b", "corridors of width 2: n pins". For each feature the mechanism in our
   code (lines in one7-bot/main.cpp) and a general rule that would change it.
3. Up to three cards, largest first, each with the count that shows it works and what it costs. Existing switches or constants
   that already do part of it go first (give the paste form `CONST:value`).
