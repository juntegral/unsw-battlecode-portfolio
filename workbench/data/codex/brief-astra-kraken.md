# Astra analyst: kraken

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `kraken`. Standing rule of the team: every game lost to a team rated
100 or more below us gets its cause found and fixed. Team kraken (id 989, rated about 1970, we were 2095) challenged us twice in
five minutes at about 03:20 KST and won both battles 3 to 2; the second cost us 53 points. The jun thinks they have found
something in our bot that they can farm.
Games (replays `M<id>.replay`): `data/online/live-one1/b1482056/` = weakhold L, Maze W, Islands L, Prisoners Dilemma L, Australia W;
`data/online/live-one1/b1483343/` = Maze W, Portals L, Devil L, Autarky W, Trauma L. The bot that played is the id in each replay
(21086 = one7 `data/online/smoke/one7-bot/main.cpp`, 21126 = one8 `one8-bot/`). A 15-game set of one8 against kraken, `one8-k1`
(`data/online/smoke/one8-k1-old/`), is queued and arrives within about 30 minutes: add it when it is there, do not wait for it.
1. What does kraken do? Its opening (splits, spread, first pearls), whether it hunts queens, how it fights (who starts the rams,
   lengths, sprint use), what it does late (fold, rally, stand still), anything unusual (blocking corridors or portals, sitting on
   pearl tiles, mirroring us). Counts against WeHaveQuizzes and Cache me outside from the one7/one8 sets on the same maps.
2. Each of the six losses in three lines: how decided, the round it turned for good, the single thing of ours that lost it
   (queen's death with her last three turns drawn, a wipe-out, the longest dragon), and the four wins the same way.
3. Is there one habit of ours that kraken's play punishes in three or more of the six? Name it with rounds and dragon ids, the
   lines in the bot that played, the switch that was meant to cover it and why it did not.
4. Cards, at most three, largest first, general rules only (paste form `CONST:value` where an existing switch does it).
Report under 600 words plus tables; first three lines = what kraken does to us, the card, how sure.
