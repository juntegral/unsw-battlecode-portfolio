# Analyst: sweep 1055 win7 (won games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/1055/win7/`. Report `data/codex/astra/sweep/1055/win7/report.md`.

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
- game 1515671, `data/online/smoke/one13-q1-old/M1515671.replay`, played by our bot 21377 (one13), map Slithery Fight, we are side A, against Quaker Qubits (team 501), test set one13-q1-old
- game 1506912, `data/online/live-one1/b1506911/M1506912.replay`, played by our bot 21377 (one13), map Stripes, we are side B, against Spearhead Capital (team 116), ranked
- game 1506913, `data/online/live-one1/b1506911/M1506913.replay`, played by our bot 21377 (one13), map Autarky, we are side B, against Spearhead Capital (team 116), ranked
- game 1506914, `data/online/live-one1/b1506911/M1506914.replay`, played by our bot 21377 (one13), map Islands, we are side B, against Spearhead Capital (team 116), ranked
- game 1506148, `data/online/live-one1/b1506148/M1506148.replay`, played by our bot 21377 (one13), map Around UNSW, we are side B, against Sponge(Albert and Bob) (team 213), ranked
- game 1511408, `data/online/live-one1/b1511406/M1511408.replay`, played by our bot 21377 (one13), map Stripes, we are side B, against Sponge(Albert and Bob) (team 213), ranked
- game 1514289, `data/online/live-one1/b1514288/M1514289.replay`, played by our bot 21377 (one13), map Devil, we are side B, against Team SKKU (team 249), ranked
- game 1515124, `data/online/live-one1/b1515123/M1515124.replay`, played by our bot 21377 (one13), map Slithery Fight, we are side B, against WeLikCoding (team 45), ranked
- game 1515127, `data/online/live-one1/b1515123/M1515127.replay`, played by our bot 21377 (one13), map Default, we are side B, against WeLikCoding (team 45), ranked
- game 1509098, `data/online/smoke/one13-k1-old/M1509098.replay`, played by our bot 21377 (one13), map Australia, we are side A, against kraken (team 989), test set one13-k1-old
- game 1509099, `data/online/smoke/one13-k1-old/M1509099.replay`, played by our bot 21377 (one13), map Islands, we are side A, against kraken (team 989), test set one13-k1-old
- game 1509101, `data/online/smoke/one13-k1-old/M1509101.replay`, played by our bot 21377 (one13), map Stripes, we are side A, against kraken (team 989), test set one13-k1-old
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
