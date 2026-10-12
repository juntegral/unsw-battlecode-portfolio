# Analyst: sweep 1055 win4 (won games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/1055/win4/`. Report `data/codex/astra/sweep/1055/win4/report.md`.

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
- game 1506224, `data/online/smoke/one13-c1-old/M1506224.replay`, played by our bot 21377 (one13), map Devil, we are side A, against Cache me outside (team 952), test set one13-c1-old
- game 1510783, `data/online/smoke/one13-c2-old/M1510783.replay`, played by our bot 21377 (one13), map weakhold, we are side A, against Cache me outside (team 952), test set one13-c2-old
- game 1510792, `data/online/smoke/one13-c2-old/M1510792.replay`, played by our bot 21377 (one13), map Schooltime, we are side A, against Cache me outside (team 952), test set one13-c2-old
- game 1510797, `data/online/smoke/one13-c2-old/M1510797.replay`, played by our bot 21377 (one13), map Slithery Fight, we are side A, against Cache me outside (team 952), test set one13-c2-old
- game 1508917, `data/online/live-one1/b1508916/M1508917.replay`, played by our bot 21377 (one13), map Maze, we are side B, against ChotteLoccoπ (team 510), test set ranked
- game 1508918, `data/online/live-one1/b1508916/M1508918.replay`, played by our bot 21377 (one13), map Trauma, we are side B, against ChotteLoccoπ (team 510), test set ranked
- game 1508919, `data/online/live-one1/b1508916/M1508919.replay`, played by our bot 21377 (one13), map Portals, we are side B, against ChotteLoccoπ (team 510), test set ranked
- game 1508920, `data/online/live-one1/b1508916/M1508920.replay`, played by our bot 21377 (one13), map Stripes, we are side B, against ChotteLoccoπ (team 510), test set ranked
- game 1508921, `data/online/live-one1/b1508916/M1508921.replay`, played by our bot 21377 (one13), map Trophy, we are side B, against ChotteLoccoπ (team 510), test set ranked
- game 1510461, `data/online/live-one1/b1510461/M1510461.replay`, played by our bot 21377 (one13), map Schooltime, we are side B, against ChotteLoccoπ (team 510), test set ranked
- game 1510462, `data/online/live-one1/b1510461/M1510462.replay`, played by our bot 21377 (one13), map Autarky, we are side B, against ChotteLoccoπ (team 510), test set ranked
- game 1512748, `data/online/live-one1/b1512747/M1512748.replay`, played by our bot 21377 (one13), map Trophy, we are side A, against Cybers (team 1148), ranked
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
