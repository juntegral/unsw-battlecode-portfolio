# Analyst: sweep 0436 win2 (won games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/0436/win2/`. Report `data/codex/astra/sweep/0436/win2/report.md`.

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
- game 1488288, `data/online/live-one1/b1488287/M1488288.replay`, played by our bot 21165 (one9), map Devil, we are side A, against kraken (team 989), ranked
- game 1488289, `data/online/live-one1/b1488287/M1488289.replay`, played by our bot 21165 (one9), map Stripes, we are side A, against kraken (team 989), ranked
- game 1488291, `data/online/live-one1/b1488287/M1488291.replay`, played by our bot 21165 (one9), map Autarky, we are side A, against kraken (team 989), ranked
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
