# Analyst: sweep 0705 win1 (won games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/0705/win1/`. Report `data/codex/astra/sweep/0705/win1/report.md`.

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
- game 1500220, `data/online/smoke/one11-k1-old/M1500220.replay`, played by our bot 21269 (one11), map weakhold, we are side A, against kraken (team 989), test set one11-k1-old
- game 1500222, `data/online/smoke/one11-k1-old/M1500222.replay`, played by our bot 21269 (one11), map Islands, we are side A, against kraken (team 989), test set one11-k1-old
- game 1500224, `data/online/smoke/one11-k1-old/M1500224.replay`, played by our bot 21269 (one11), map Stripes, we are side A, against kraken (team 989), test set one11-k1-old
- game 1500226, `data/online/smoke/one11-k1-old/M1500226.replay`, played by our bot 21269 (one11), map Around UNSW, we are side A, against kraken (team 989), test set one11-k1-old
- game 1500227, `data/online/smoke/one11-k1-old/M1500227.replay`, played by our bot 21269 (one11), map Default, we are side A, against kraken (team 989), test set one11-k1-old
- game 1500228, `data/online/smoke/one11-k1-old/M1500228.replay`, played by our bot 21269 (one11), map Queen Of Spades, we are side A, against kraken (team 989), test set one11-k1-old
- game 1500230, `data/online/smoke/one11-k1-old/M1500230.replay`, played by our bot 21269 (one11), map Trophy, we are side A, against kraken (team 989), test set one11-k1-old
- game 1500231, `data/online/smoke/one11-k1-old/M1500231.replay`, played by our bot 21269 (one11), map Devil, we are side A, against kraken (team 989), test set one11-k1-old
- game 1500232, `data/online/smoke/one11-k1-old/M1500232.replay`, played by our bot 21269 (one11), map Trauma, we are side A, against kraken (team 989), test set one11-k1-old
- game 1500234, `data/online/smoke/one11-k1-old/M1500234.replay`, played by our bot 21269 (one11), map Slithery Fight, we are side A, against kraken (team 989), test set one11-k1-old
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
