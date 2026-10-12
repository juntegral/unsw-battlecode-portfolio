# Analyst: sweep 0630 win1 (won games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/0630/win1/`. Report `data/codex/astra/sweep/0630/win1/report.md`.

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
- game 1496853, `data/online/smoke/one11-c1-old/M1496853.replay`, played by our bot 21269 (one11), map Queen Of Spades, we are side A, against Cache me outside (team 952), test set one11-c1-old
- game 1496854, `data/online/smoke/one11-c1-old/M1496854.replay`, played by our bot 21269 (one11), map Schooltime, we are side A, against Cache me outside (team 952), test set one11-c1-old
- game 1496855, `data/online/smoke/one11-c1-old/M1496855.replay`, played by our bot 21269 (one11), map Trophy, we are side A, against Cache me outside (team 952), test set one11-c1-old
- game 1496856, `data/online/smoke/one11-c1-old/M1496856.replay`, played by our bot 21269 (one11), map Devil, we are side A, against Cache me outside (team 952), test set one11-c1-old
- game 1497631, `data/online/live-one1/b1497630/M1497631.replay`, played by our bot 21269 (one11), map Default, we are side B, against ComTamSuonNuong (team 193), test set ranked
- game 1497632, `data/online/live-one1/b1497630/M1497632.replay`, played by our bot 21269 (one11), map Islands, we are side B, against ComTamSuonNuong (team 193), test set ranked
- game 1497634, `data/online/live-one1/b1497630/M1497634.replay`, played by our bot 21269 (one11), map Queen Of Spades, we are side B, against ComTamSuonNuong (team 193), test set ranked
- game 1497388, `data/online/live-one1/b1497386/M1497388.replay`, played by our bot 21269 (one11), map Stripes, we are side A, against Cutlery (team 306), ranked
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
