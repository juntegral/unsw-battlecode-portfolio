# Analyst: sweep 1055 win3 (won games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/1055/win3/`. Report `data/codex/astra/sweep/1055/win3/report.md`.

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
- game 1501266, `data/online/live-one1/b1501263/M1501266.replay`, played by our bot 21330 (one12), map Stripes, we are side A, against test4 (team 19), ranked
- game 1502774, `data/online/live-one1/b1502774/M1502774.replay`, played by our bot 21330 (one12), map weakhold, we are side B, against we love gru (team 998), ranked
- game 1502777, `data/online/live-one1/b1502774/M1502777.replay`, played by our bot 21330 (one12), map Trauma, we are side B, against we love gru (team 998), ranked
- game 1507593, `data/online/live-one1/b1507592/M1507593.replay`, played by our bot 21377 (one13), map Schooltime, we are side A, against Ballers (team 1149), ranked
- game 1507594, `data/online/live-one1/b1507592/M1507594.replay`, played by our bot 21377 (one13), map Devil, we are side A, against Ballers (team 1149), ranked
- game 1507595, `data/online/live-one1/b1507592/M1507595.replay`, played by our bot 21377 (one13), map Prisoners Dilemma, we are side A, against Ballers (team 1149), ranked
- game 1507596, `data/online/live-one1/b1507592/M1507596.replay`, played by our bot 21377 (one13), map Autarky, we are side A, against Ballers (team 1149), ranked
- game 1506213, `data/online/smoke/one13-c1-old/M1506213.replay`, played by our bot 21377 (one13), map weakhold, we are side A, against Cache me outside (team 952), test set one13-c1-old
- game 1506214, `data/online/smoke/one13-c1-old/M1506214.replay`, played by our bot 21377 (one13), map Australia, we are side A, against Cache me outside (team 952), test set one13-c1-old
- game 1506215, `data/online/smoke/one13-c1-old/M1506215.replay`, played by our bot 21377 (one13), map Islands, we are side A, against Cache me outside (team 952), test set one13-c1-old
- game 1506222, `data/online/smoke/one13-c1-old/M1506222.replay`, played by our bot 21377 (one13), map Schooltime, we are side A, against Cache me outside (team 952), test set one13-c1-old
- game 1506223, `data/online/smoke/one13-c1-old/M1506223.replay`, played by our bot 21377 (one13), map Trophy, we are side A, against Cache me outside (team 952), test set one13-c1-old
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
