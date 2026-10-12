# Analyst: sweep 0410 win2 (won games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/0410/win2/`. Report `data/codex/astra/sweep/0410/win2/report.md`.

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
- game 1485178, `data/online/smoke/one8-k1-old/M1485178.replay`, map Trophy, we are side A, against kraken (team 989), test set one8-k1-old
- game 1485179, `data/online/smoke/one8-k1-old/M1485179.replay`, map Devil, we are side A, against kraken (team 989), test set one8-k1-old
- game 1485487, `data/online/live-one1/b1485486/M1485487.replay`, map Queen Of Spades, we are side B, against kraken (team 989), ranked
- game 1485488, `data/online/live-one1/b1485486/M1485488.replay`, map Autarky, we are side B, against kraken (team 989), ranked
- game 1485483, `data/online/live-one1/b1485483/M1485483.replay`, map Trophy, we are side B, against the uncancelables (team 899), test set ranked
- game 1485484, `data/online/live-one1/b1485483/M1485484.replay`, map Prisoners Dilemma, we are side B, against the uncancelables (team 899), test set ranked
- game 1485485, `data/online/live-one1/b1485483/M1485485.replay`, map Autarky, we are side B, against the uncancelables (team 899), test set ranked
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
