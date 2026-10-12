# Analyst: sweep 1055 win2 (won games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/1055/win2/`. Report `data/codex/astra/sweep/1055/win2/report.md`.

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
- game 1504483, `data/online/smoke/one12-k1-old/M1504483.replay`, played by our bot 21330 (one12), map Stripes, we are side A, against kraken (team 989), test set one12-k1-old
- game 1504485, `data/online/smoke/one12-k1-old/M1504485.replay`, played by our bot 21330 (one12), map Around UNSW, we are side A, against kraken (team 989), test set one12-k1-old
- game 1504487, `data/online/smoke/one12-k1-old/M1504487.replay`, played by our bot 21330 (one12), map Queen Of Spades, we are side A, against kraken (team 989), test set one12-k1-old
- game 1504488, `data/online/smoke/one12-k1-old/M1504488.replay`, played by our bot 21330 (one12), map Schooltime, we are side A, against kraken (team 989), test set one12-k1-old
- game 1504490, `data/online/smoke/one12-k1-old/M1504490.replay`, played by our bot 21330 (one12), map Devil, we are side A, against kraken (team 989), test set one12-k1-old
- game 1504491, `data/online/smoke/one12-k1-old/M1504491.replay`, played by our bot 21330 (one12), map Trauma, we are side A, against kraken (team 989), test set one12-k1-old
- game 1504730, `data/online/live-one1/b1504730/M1504730.replay`, played by our bot 21330 (one12), map Queen Of Spades, we are side B, against kraken (team 989), ranked
- game 1504732, `data/online/live-one1/b1504730/M1504732.replay`, played by our bot 21330 (one12), map Stripes, we are side B, against kraken (team 989), ranked
- game 1504733, `data/online/live-one1/b1504730/M1504733.replay`, played by our bot 21330 (one12), map Devil, we are side B, against kraken (team 989), ranked
- game 1504734, `data/online/live-one1/b1504730/M1504734.replay`, played by our bot 21330 (one12), map Australia, we are side B, against kraken (team 989), ranked
- game 1501263, `data/online/live-one1/b1501263/M1501263.replay`, played by our bot 21330 (one12), map Portals, we are side A, against test4 (team 19), ranked
- game 1501264, `data/online/live-one1/b1501263/M1501264.replay`, played by our bot 21330 (one12), map weakhold, we are side A, against test4 (team 19), ranked
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
