# Analyst: sweep 0410 win1 (won games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/0410/win1/`. Report `data/codex/astra/sweep/0410/win1/report.md`.

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
- game 1484435, `data/online/smoke/one8-c1-old/M1484435.replay`, map Around UNSW, we are side A, against Cache me outside (team 952), test set one8-c1-old
- game 1486051, `data/online/live-one1/b1486051/M1486051.replay`, map Trauma, we are side A, against Codehammer 40K (team 34), ranked
- game 1483995, `data/online/live-one1/b1483995/M1483995.replay`, map Default, we are side A, against acegi (team 1090), ranked
- game 1483996, `data/online/live-one1/b1483995/M1483996.replay`, map Australia, we are side A, against acegi (team 1090), ranked
- game 1483999, `data/online/live-one1/b1483995/M1483999.replay`, map Around UNSW, we are side A, against acegi (team 1090), ranked
- game 1485168, `data/online/smoke/one8-k1-old/M1485168.replay`, map weakhold, we are side A, against kraken (team 989), test set one8-k1-old
- game 1485171, `data/online/smoke/one8-k1-old/M1485171.replay`, map Maze, we are side A, against kraken (team 989), test set one8-k1-old
- game 1485172, `data/online/smoke/one8-k1-old/M1485172.replay`, map Stripes, we are side A, against kraken (team 989), test set one8-k1-old
- game 1485173, `data/online/smoke/one8-k1-old/M1485173.replay`, map Tower Defense, we are side A, against kraken (team 989), test set one8-k1-old
- game 1485175, `data/online/smoke/one8-k1-old/M1485175.replay`, map Default, we are side A, against kraken (team 989), test set one8-k1-old
- game 1485176, `data/online/smoke/one8-k1-old/M1485176.replay`, map Queen Of Spades, we are side A, against kraken (team 989), test set one8-k1-old
- game 1485177, `data/online/smoke/one8-k1-old/M1485177.replay`, map Schooltime, we are side A, against kraken (team 989), test set one8-k1-old
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
