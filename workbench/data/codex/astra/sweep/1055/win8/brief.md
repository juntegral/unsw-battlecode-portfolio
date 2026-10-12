# Analyst: sweep 1055 win8 (won games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/1055/win8/`. Report `data/codex/astra/sweep/1055/win8/report.md`.

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
- game 1509103, `data/online/smoke/one13-k1-old/M1509103.replay`, played by our bot 21377 (one13), map Around UNSW, we are side A, against kraken (team 989), test set one13-k1-old
- game 1509104, `data/online/smoke/one13-k1-old/M1509104.replay`, played by our bot 21377 (one13), map Default, we are side A, against kraken (team 989), test set one13-k1-old
- game 1509105, `data/online/smoke/one13-k1-old/M1509105.replay`, played by our bot 21377 (one13), map Queen Of Spades, we are side A, against kraken (team 989), test set one13-k1-old
- game 1509106, `data/online/smoke/one13-k1-old/M1509106.replay`, played by our bot 21377 (one13), map Schooltime, we are side A, against kraken (team 989), test set one13-k1-old
- game 1509110, `data/online/smoke/one13-k1-old/M1509110.replay`, played by our bot 21377 (one13), map Portals, we are side A, against kraken (team 989), test set one13-k1-old
- game 1513833, `data/online/smoke/one13-k2-old/M1513833.replay`, played by our bot 21377 (one13), map weakhold, we are side A, against kraken (team 989), test set one13-k2-old
- game 1513835, `data/online/smoke/one13-k2-old/M1513835.replay`, played by our bot 21377 (one13), map Islands, we are side A, against kraken (team 989), test set one13-k2-old
- game 1513837, `data/online/smoke/one13-k2-old/M1513837.replay`, played by our bot 21377 (one13), map Stripes, we are side A, against kraken (team 989), test set one13-k2-old
- game 1513838, `data/online/smoke/one13-k2-old/M1513838.replay`, played by our bot 21377 (one13), map Tower Defense, we are side A, against kraken (team 989), test set one13-k2-old
- game 1513841, `data/online/smoke/one13-k2-old/M1513841.replay`, played by our bot 21377 (one13), map Queen Of Spades, we are side A, against kraken (team 989), test set one13-k2-old
- game 1513843, `data/online/smoke/one13-k2-old/M1513843.replay`, played by our bot 21377 (one13), map Trophy, we are side A, against kraken (team 989), test set one13-k2-old
- game 1508580, `data/online/live-one1/b1508580/M1508580.replay`, played by our bot 21377 (one13), map Around UNSW, we are side B, against ouroboros (team 1022), ranked
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
