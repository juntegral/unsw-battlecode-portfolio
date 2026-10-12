# Analyst: sweep 1055 win1 (won games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/1055/win1/`. Report `data/codex/astra/sweep/1055/win1/report.md`.

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
- game 1501017, `data/online/live-one1/b1501017/M1501017.replay`, played by our bot 21269 (one11), map Prisoners Dilemma, we are side B, against tozoman (team 357), ranked
- game 1501018, `data/online/live-one1/b1501017/M1501018.replay`, played by our bot 21269 (one11), map Schooltime, we are side B, against tozoman (team 357), ranked
- game 1501021, `data/online/live-one1/b1501017/M1501021.replay`, played by our bot 21269 (one11), map Default, we are side B, against tozoman (team 357), ranked
- game 1501671, `data/online/smoke/one12-c1-old/M1501671.replay`, played by our bot 21330 (one12), map Around UNSW, we are side A, against Cache me outside (team 952), test set one12-c1-old
- game 1501673, `data/online/smoke/one12-c1-old/M1501673.replay`, played by our bot 21330 (one12), map Queen Of Spades, we are side A, against Cache me outside (team 952), test set one12-c1-old
- game 1503501, `data/online/smoke/one12-p1-old/M1503501.replay`, played by our bot 21330 (one12), map weakhold, we are side A, against Preyas (team 1101), test set one12-p1-old
- game 1503505, `data/online/smoke/one12-p1-old/M1503505.replay`, played by our bot 21330 (one12), map Stripes, we are side A, against Preyas (team 1101), test set one12-p1-old
- game 1503507, `data/online/smoke/one12-p1-old/M1503507.replay`, played by our bot 21330 (one12), map Around UNSW, we are side A, against Preyas (team 1101), test set one12-p1-old
- game 1503511, `data/online/smoke/one12-p1-old/M1503511.replay`, played by our bot 21330 (one12), map Trophy, we are side A, against Preyas (team 1101), test set one12-p1-old
- game 1503361, `data/online/live-one1/b1503361/M1503361.replay`, played by our bot 21330 (one12), map Autarky, we are side B, against Quantify (team 273), test set ranked
- game 1504480, `data/online/smoke/one12-k1-old/M1504480.replay`, played by our bot 21330 (one12), map Australia, we are side A, against kraken (team 989), test set one12-k1-old
- game 1504481, `data/online/smoke/one12-k1-old/M1504481.replay`, played by our bot 21330 (one12), map Islands, we are side A, against kraken (team 989), test set one12-k1-old
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
