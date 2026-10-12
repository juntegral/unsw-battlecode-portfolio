# Our dragons of 30+ in two online sets: how many, and how they died (mechanical count)

Sets (our team is 1119; replays as read by `data/analysis/ladder/dossier/online/label_report.py`, reuse its reader):
- `data/online/smoke/c5455-w1-new/` = live bot + LONG_SAFETY (card 54: dragons of 30+ avoid tiles an enemy head can reach) + QUEEN_FALLBACK, 15 games against WeHaveQuizzes
- `data/online/smoke/one2-w1-old/` = the live bot alone, same opponent and maps, 15 games
- `data/online/smoke/one1-w1-old/` = the previous live bot, same, 15 games (third column)
For each set, over all games, for OUR dragons and separately for THEIR dragons:
1. dragons that reached length 30 or more at any time: how many (count a dragon once), in how many games, and the mean of their peak length;
2. how each of those ended: alive at the end; rammed by an enemy head while 30+ (head-on, the other moved); died on its own move while 30+ (into kelp / its own body / another body, or no valid action); died after it had dropped below 30; with the round and the game id for every death while 30+;
3. dragon-turns spent at 30+ and, per 1,000 of those turns, the number of rammed deaths;
4. turns on which a dragon of 30+ started with an enemy head of length 2 to 4 within 3 steps (open edges and portals, bodies ignored) and what it did: stepped away / stayed within 3 / sprinted (paid) / split.
One table, three columns, ours and theirs as separate rows. Under it the per-death list for ours. Numbers only from the replays.
Write `data/analysis/ladder/dossier/online/long30.md` (script `long30.py` beside it). No network, no posts, no games, no compiling.
