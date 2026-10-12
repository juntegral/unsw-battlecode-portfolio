# Analyst: sweep 1055 win9 (won games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/1055/win9/`. Report `data/codex/astra/sweep/1055/win9/report.md`.

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
- game 1508581, `data/online/live-one1/b1508580/M1508581.replay`, played by our bot 21377 (one13), map Australia, we are side B, against ouroboros (team 1022), ranked
- game 1508582, `data/online/live-one1/b1508580/M1508582.replay`, played by our bot 21377 (one13), map Slithery Fight, we are side B, against ouroboros (team 1022), ranked
- game 1508583, `data/online/live-one1/b1508580/M1508583.replay`, played by our bot 21377 (one13), map weakhold, we are side B, against ouroboros (team 1022), ranked
- game 1508584, `data/online/live-one1/b1508580/M1508584.replay`, played by our bot 21377 (one13), map Schooltime, we are side B, against ouroboros (team 1022), ranked
- game 1512823, `data/online/live-one1/b1512823/M1512823.replay`, played by our bot 21377 (one13), map Islands, we are side B, against tozoman (team 357), test set ranked
- game 1517685, `data/online/smoke/one14-c1-old/M1517685.replay`, played by our bot 21497 (one14), map weakhold, we are side A, against Cache me outside (team 952), test set one14-c1-old
- game 1517688, `data/online/smoke/one14-c1-old/M1517688.replay`, played by our bot 21497 (one14), map Maze, we are side A, against Cache me outside (team 952), test set one14-c1-old
- game 1517691, `data/online/smoke/one14-c1-old/M1517691.replay`, played by our bot 21497 (one14), map Around UNSW, we are side A, against Cache me outside (team 952), test set one14-c1-old
- game 1517692, `data/online/smoke/one14-c1-old/M1517692.replay`, played by our bot 21497 (one14), map Default, we are side A, against Cache me outside (team 952), test set one14-c1-old
- game 1517695, `data/online/smoke/one14-c1-old/M1517695.replay`, played by our bot 21497 (one14), map Trophy, we are side A, against Cache me outside (team 952), test set one14-c1-old
- game 1517696, `data/online/smoke/one14-c1-old/M1517696.replay`, played by our bot 21497 (one14), map Devil, we are side A, against Cache me outside (team 952), test set one14-c1-old
- game 1517699, `data/online/smoke/one14-c1-old/M1517699.replay`, played by our bot 21497 (one14), map Slithery Fight, we are side A, against Cache me outside (team 952), test set one14-c1-old
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
