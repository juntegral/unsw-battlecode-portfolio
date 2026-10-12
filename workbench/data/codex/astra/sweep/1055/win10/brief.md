# Analyst: sweep 1055 win10 (won games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/1055/win10/`. Report `data/codex/astra/sweep/1055/win10/report.md`.

The team analyses every game as it comes in. These are WON games: find what nearly lost them and what the new switches did.
- game 1516202, `data/online/live-one1/b1516202/M1516202.replay`, played by our bot 21497 (one14), map Autarky, we are side B, against Check Raise (team 152), ranked
- game 1516204, `data/online/live-one1/b1516202/M1516204.replay`, played by our bot 21497 (one14), map Portals, we are side B, against Check Raise (team 152), ranked
- game 1516205, `data/online/live-one1/b1516202/M1516205.replay`, played by our bot 21497 (one14), map Devil, we are side B, against Check Raise (team 152), ranked
- game 1516987, `data/online/live-one1/b1516986/M1516987.replay`, played by our bot 21497 (one14), map Islands, we are side B, against Sponge(Albert and Bob) (team 213), ranked
- game 1516989, `data/online/live-one1/b1516986/M1516989.replay`, played by our bot 21497 (one14), map Stripes, we are side B, against Sponge(Albert and Bob) (team 213), ranked
- game 1516555, `data/online/live-one1/b1516554/M1516555.replay`, played by our bot 21497 (one14), map Schooltime, we are side B, against kraken (team 989), ranked
- game 1516556, `data/online/live-one1/b1516554/M1516556.replay`, played by our bot 21497 (one14), map Default, we are side B, against kraken (team 989), ranked
- game 1516557, `data/online/live-one1/b1516554/M1516557.replay`, played by our bot 21497 (one14), map Trophy, we are side B, against kraken (team 989), ranked
One table, a row a game: how it was decided, final state of both sides, the round we went ahead for good, our queen (alive and
her length, or the round and cause of her death), the closest we came to losing (a round where their queen could have decided
it, our queen one step from a ram, our count halved). Then counts over all of them: which of the switches listed as live in
CARDS.md can be seen acting (give a replay moment each), and any sign that one of them costs us (pearls passed by, dragons
standing still, hunters dying for nothing). No card unless a won game shows a habit that would lose against a better team.
Under 400 words plus the table; first three lines = what won these games, the weakest point seen, how sure.
