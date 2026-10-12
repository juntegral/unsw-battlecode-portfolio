# Analyst: sweep 0436 win1 (won games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/0436/win1/`. Report `data/codex/astra/sweep/0436/win1/report.md`.

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
- game 1486055, `data/online/live-one1/b1486051/M1486055.replay`, played by our bot 21126 (one8), map Prisoners Dilemma, we are side A, against Codehammer 40K (team 34), ranked
- game 1487475, `data/online/smoke/one9-k1-old/M1487475.replay`, played by our bot 21165 (one9), map Islands, we are side A, against kraken (team 989), test set one9-k1-old
- game 1487476, `data/online/smoke/one9-k1-old/M1487476.replay`, played by our bot 21165 (one9), map Maze, we are side A, against kraken (team 989), test set one9-k1-old
- game 1487477, `data/online/smoke/one9-k1-old/M1487477.replay`, played by our bot 21165 (one9), map Stripes, we are side A, against kraken (team 989), test set one9-k1-old
- game 1487480, `data/online/smoke/one9-k1-old/M1487480.replay`, played by our bot 21165 (one9), map Default, we are side A, against kraken (team 989), test set one9-k1-old
- game 1487481, `data/online/smoke/one9-k1-old/M1487481.replay`, played by our bot 21165 (one9), map Queen Of Spades, we are side A, against kraken (team 989), test set one9-k1-old
- game 1487482, `data/online/smoke/one9-k1-old/M1487482.replay`, played by our bot 21165 (one9), map Schooltime, we are side A, against kraken (team 989), test set one9-k1-old
- game 1487483, `data/online/smoke/one9-k1-old/M1487483.replay`, played by our bot 21165 (one9), map Trophy, we are side A, against kraken (team 989), test set one9-k1-old
- game 1487484, `data/online/smoke/one9-k1-old/M1487484.replay`, played by our bot 21165 (one9), map Devil, we are side A, against kraken (team 989), test set one9-k1-old
- game 1487485, `data/online/smoke/one9-k1-old/M1487485.replay`, played by our bot 21165 (one9), map Trauma, we are side A, against kraken (team 989), test set one9-k1-old
- game 1487487, `data/online/smoke/one9-k1-old/M1487487.replay`, played by our bot 21165 (one9), map Slithery Fight, we are side A, against kraken (team 989), test set one9-k1-old
- game 1488287, `data/online/live-one1/b1488287/M1488287.replay`, played by our bot 21165 (one9), map Default, we are side A, against kraken (team 989), ranked
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
