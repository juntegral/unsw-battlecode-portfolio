# Astra analyst: sweep 1055 loss9 (lost games)

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md` (what is live, what is being built, what was dropped).
The bot that played each game is the id in its replay (teams.<side>.botId); the sources are `data/online/smoke/one<N>-bot/main.cpp`
(21126 = one8, 21165 = one9; a larger id is a later version: `docs/SESSION-STATE.md`, grep "라이브 = one").
Write only under `data/codex/astra/sweep/1055/loss9/`. Report `data/codex/astra/sweep/1055/loss9/report.md`.

The team analyses every game as it comes in. These are LOST games; each needs its cause, not a summary.
- game 1503514, `data/online/smoke/one12-p1-old/M1503514.replay`, played by our bot 21330 (one12), map Portals, we are side A, against Preyas (team 1101), test set one12-p1-old
- game 1503515, `data/online/smoke/one12-p1-old/M1503515.replay`, played by our bot 21330 (one12), map Slithery Fight, we are side A, against Preyas (team 1101), test set one12-p1-old
- game 1503326, `data/online/live-one1/b1503326/M1503326.replay`, played by our bot 21330 (one12), map Portals, we are side B, against Quantify (team 273), test set ranked
For each game: 1. how it was decided (queen / longest / total / wiped out), the final state of both sides, and the round it turned
for good; 2. the single event or habit of ours that lost it, with rounds and dragon ids (if our queen died: the round, the cause,
her last three own turns drawn as 7 by 7 boards, what the attacker did; if she lived and was shorter: why she did not grow; if
we were outgrown: from which round and what our dragons were doing instead of eating; if the longest decided: what happened to
our long ones); 3. which LIVE switch in the bot that played was meant to prevent it and the exact condition in the code that
failed, or "nothing covers this"; 4. after our queen died, did any dragon of ours get within 5 steps of their queen, and if not,
where was she.
Then: the causes ranked by how many of these games they explain, and for each a card: the rule, the lines, the existing switch
if one does it (paste form `CONST:value`), the count that would show it works. Mark every card as NEW, BEING BUILT or
LIVE-BUT-FAILED against CARDS.md. Under 600 words plus tables; first three lines = the top cause, its card, how sure.
