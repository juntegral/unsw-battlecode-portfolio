# Analyst: sweep 1055 win5 (won games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/1055/win5/`. Report `data/codex/astra/sweep/1055/win5/report.md`.

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
- game 1512750, `data/online/live-one1/b1512747/M1512750.replay`, played by our bot 21377 (one13), map weakhold, we are side A, against Cybers (team 1148), ranked
- game 1512751, `data/online/live-one1/b1512747/M1512751.replay`, played by our bot 21377 (one13), map Islands, we are side A, against Cybers (team 1148), ranked
- game 1507573, `data/online/live-one1/b1507572/M1507573.replay`, played by our bot 21377 (one13), map Queen Of Spades, we are side B, against Heartbreaker (team 62), ranked
- game 1507574, `data/online/live-one1/b1507572/M1507574.replay`, played by our bot 21377 (one13), map Tower Defense, we are side B, against Heartbreaker (team 62), ranked
- game 1507576, `data/online/live-one1/b1507572/M1507576.replay`, played by our bot 21377 (one13), map Australia, we are side B, against Heartbreaker (team 62), ranked
- game 1508960, `data/online/live-one1/b1508960/M1508960.replay`, played by our bot 21377 (one13), map Trauma, we are side B, against Jingling Munmin (team 133), ranked
- game 1508961, `data/online/live-one1/b1508960/M1508961.replay`, played by our bot 21377 (one13), map weakhold, we are side B, against Jingling Munmin (team 133), ranked
- game 1508964, `data/online/live-one1/b1508960/M1508964.replay`, played by our bot 21377 (one13), map Devil, we are side B, against Jingling Munmin (team 133), ranked
- game 1507914, `data/online/smoke/one13-p1-old/M1507914.replay`, played by our bot 21377 (one13), map Australia, we are side A, against Preyas (team 1101), test set one13-p1-old
- game 1507920, `data/online/smoke/one13-p1-old/M1507920.replay`, played by our bot 21377 (one13), map Default, we are side A, against Preyas (team 1101), test set one13-p1-old
- game 1507924, `data/online/smoke/one13-p1-old/M1507924.replay`, played by our bot 21377 (one13), map Devil, we are side A, against Preyas (team 1101), test set one13-p1-old
- game 1507927, `data/online/smoke/one13-p1-old/M1507927.replay`, played by our bot 21377 (one13), map Slithery Fight, we are side A, against Preyas (team 1101), test set one13-p1-old
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
