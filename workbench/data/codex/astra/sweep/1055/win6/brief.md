# Analyst: sweep 1055 win6 (won games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/1055/win6/`. Report `data/codex/astra/sweep/1055/win6/report.md`.

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
- game 1512560, `data/online/smoke/one13-p2-old/M1512560.replay`, played by our bot 21377 (one13), map Islands, we are side A, against Preyas (team 1101), test set one13-p2-old
- game 1512564, `data/online/smoke/one13-p2-old/M1512564.replay`, played by our bot 21377 (one13), map Around UNSW, we are side A, against Preyas (team 1101), test set one13-p2-old
- game 1512567, `data/online/smoke/one13-p2-old/M1512567.replay`, played by our bot 21377 (one13), map Schooltime, we are side A, against Preyas (team 1101), test set one13-p2-old
- game 1512571, `data/online/smoke/one13-p2-old/M1512571.replay`, played by our bot 21377 (one13), map Portals, we are side A, against Preyas (team 1101), test set one13-p2-old
- game 1512572, `data/online/smoke/one13-p2-old/M1512572.replay`, played by our bot 21377 (one13), map Slithery Fight, we are side A, against Preyas (team 1101), test set one13-p2-old
- game 1513122, `data/online/live-one1/b1513119/M1513122.replay`, played by our bot 21377 (one13), map Autarky, we are side B, against Quaker Qubits (team 501), ranked
- game 1515657, `data/online/smoke/one13-q1-old/M1515657.replay`, played by our bot 21377 (one13), map weakhold, we are side A, against Quaker Qubits (team 501), test set one13-q1-old
- game 1515659, `data/online/smoke/one13-q1-old/M1515659.replay`, played by our bot 21377 (one13), map Islands, we are side A, against Quaker Qubits (team 501), test set one13-q1-old
- game 1515663, `data/online/smoke/one13-q1-old/M1515663.replay`, played by our bot 21377 (one13), map Around UNSW, we are side A, against Quaker Qubits (team 501), test set one13-q1-old
- game 1515665, `data/online/smoke/one13-q1-old/M1515665.replay`, played by our bot 21377 (one13), map Queen Of Spades, we are side A, against Quaker Qubits (team 501), test set one13-q1-old
- game 1515666, `data/online/smoke/one13-q1-old/M1515666.replay`, played by our bot 21377 (one13), map Schooltime, we are side A, against Quaker Qubits (team 501), test set one13-q1-old
- game 1515668, `data/online/smoke/one13-q1-old/M1515668.replay`, played by our bot 21377 (one13), map Devil, we are side A, against Quaker Qubits (team 501), test set one13-q1-old
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
