# Astra analyst: qwq3

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `qwq3`. The live bot is now one6 (submission 21033,
`data/online/smoke/one6-bot/main.cpp` = one5 + RALLY_END_FRESH 25 + QUEEN_DEAD_ALL). A teammate watching our ranked games reported
three things. Explain each from the replay and the code, say how often it happens in all one5 and one6 games
(`data/online/smoke/one5-*-old/`, `one6-*-old/`, `data/online/live-one1/b*/` from 00:49 KST on; the same game can sit in both a
smoke folder and a `b*` folder: count each game id once), and give a card where a general rule fixes it.
1. Game 1477042, map Stripes (`data/online/live-one1/b1477038/M1477042.replay`), our dragon id 6 "keeps circling around the portal".
   Which rounds, what does it see, which score terms hold it there (HARVEST_PORTAL, portal scouting `can_scout_portals`, SPAWN_CLEAR,
   POCKET_LOOP, a pearl timer behind the portal?), what did it give up (pearls it could have reached). Count: dragon-turns of ours
   spent within 2 cells of the same portal mouth for 10 or more rounds in a row without eating, per game, ours against theirs.
2. Game 1477048, map Trophy (`b1477038/M1477048.replay`), round 17: a dragon of ours saw the enemy queen and neither attacked
   nor ate the pearl, it moved away. Which dragon, the lengths, the distances, what each option scored as far as the code shows
   (queen safety rings, `threat_at`, `risk_at`, trade rules, QUEEN_SURE reach, EAT_FIRST conditions), and what the right move was.
   Count: turns on which a non-queen of ours has the enemy queen's head inside its free reach and does not ram it, and turns with
   a pearl one step away not taken while an enemy queen (a short dragon like any other) is within 3 cells.
3. Game 1476179, map Tower Defense (`b1476178/M1476179.replay`): already diagnosed. Our two starters (ids 1 and 3) walk east side
   by side from r13, id 3 along the north wall, id 1 beside it one step ahead and moving first; id 3 has one legal move each
   round and at r16 is in the corner (29,7) with the mate's body on its only exit, and dies on it. The same death, same cell,
   in game 1465497. The lead is having a rule built for this; from you only the count: pairs of our dragons that move in the same
   direction on adjacent parallel lines for 4 or more rounds in a row in r0-40, per game, ours against theirs, and how many end in
   a death of one of the two within 5 rounds.
Report as usual; one section per case, the counts in one table.
