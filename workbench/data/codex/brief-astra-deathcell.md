# Analyst: deathcell

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `deathcell`.

Question: in ranked game 1471966 (Stripes, `data/online/live-one1/b1471964/`) three dragons of ours died on a wall in the same
cell (6,2) at r136, r142 and r219, the last one our queen, who went through a portal to eat a pearl and had no way out. A bot that
walks into the same trap three times in one game will do it on every unseen map that has such a cell. How common is it, and why
does the dead-end check not stop it?
1. Over all one1 to one5 online games (`data/online/smoke/one*-old/`, `data/online/live-one1/b*/` from 22:29 KST on): every cell
   where two or more of our dragons died by wall, own body or mate body in one game without an enemy head within 3 steps. Per
   game the cells, the count, the rounds, whether the way in was a portal, a pearl-bearing tile inside, the length of the dragons,
   and whether the queen was one of them. Totals: games affected, deaths, length lost, share of all our non-combat deaths.
   The same count for the opponents as the baseline.
2. For the ten clearest cells: the geometry (draw the 7 by 7), what the dragon saw when it stepped in, and what the bot's dead-end
   terms said: read `DEAD_END`, `ROOM`, `portal_dead`, `last_dead_end`, `last_room`, `last_reaches_tail`, pocket and
   `HARVEST_PORTAL` in `data/online/smoke/one5-bot/main.cpp` and say which one should have fired and why it did not (portal exit
   not searched, pearl bonus larger than the penalty, room counted through the dragon's own tail, ...).
3. One card: a general rule that keeps a dragon out of a cell with no way back, or stops the second visit (the side shares what
   it sees: can a death cell be remembered?). Lines, the count that shows it works, what it costs (pearls in pockets not eaten).
   The rule must not name a map or a size.
