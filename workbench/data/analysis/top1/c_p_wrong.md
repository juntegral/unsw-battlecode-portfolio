## Where `findings.md`, `deep-read.md` or `deep-read-2.md` look wrong or thin

1. **All of them, and the brief, treat our games as one bot.** The 401 games are eleven runs (`c_batches.py`), and 42 of them, 12
   on large maps, were played by a candidate that rams on contact. On the measures that matter here the two bots are not the
   same team: 10% and 31% of meetings end in a ram, 46 and 52 units at round 150, total length 121 and 143. Every pooled
   "meow" number for contact (for instance "rams started in rounds 150-200: 3.3" in `findings.md` section 2) is a mix of the
   two, and a reader who picks "our newest games" to read, as I did, reads the candidate. Nothing in `findings.md`, the two
   deep reads or `plan.md` mentions that test or its result.
2. **`findings.md`, section 2, the column "our opponents".** It reads as if test4 and WHQ had a stronger economy than the top three
   (total length 254 at round 200 against 165-195). They do not: it is the economy of a team that plays us. Against the top
   three test4 has 52 units at round 100 and eats 285 natural pearls in rounds 0-149 (forgot 322, SSS 315, Vibing++ 305), holds
   6-11 dragons of 5-9 from round 150 instead of 12-16, and gains nothing from rams (-3 segments a game; against us +68).
3. **"On large maps our units fall from round 150 because growth splits stop"** (`findings.md` section 2 and the brief). True and
   half the story. The same switch stops small dragons from eating pearls next to them (82% before, 60% after; 44% near the
   longest dragon), which no earlier note mentions and card #14 did not touch; and in the two games read with a won opening
   (both of the test build) the units fall because of rams (17 and 26 of our dragons rammed in rounds 150-199 against 4 and 5
   rams made), not because of missing splits alone.
4. **"Per dragon we eat about 10% less in rounds 20-60; the unit gap compounds from there"** (the brief's list of known facts). The 6-8% in
   rounds 0-49 is there (6.6 natural pearls per 100 dragon-turns against 7.0-7.2), but the gap that decides is made in rounds
   50-149 and close to half of it at the border and in the enemy's half. On Around UNSW and Slithery Fight there is no unit gap
   at all until round 300 (median unit ratio 0.94-0.97 at round 150 and 200) and we win 11 of 53: there the measure that shows the
   gap is total length (ratio 0.61 and 0.78 at round 150). In the live game read on Islands (1063012) we are ahead until round
   90.
5. **`deep-read-2.md`, answer 7 and table row 34: "the team that spreads wins the opening ... parent and child part faster
   (6.4-7.3 steps against 4.0-5.3)".** That was one game. Over all games the parent-child distance five rounds after a split is
   the same for everybody (meow 6.2, test4 6.1, WHQ 6.4, forgot 6.1, SSS 5.7, Vibing++ 5.9) and so is the share of the child's
   steps onto unvisited cells (18-21%). Spread differs at team level: cells visited, and above all how much of the team
   stands and eats in the other half.
6. **`deep-read-2.md`: "no top team avoids" the dead-end deaths.** True as far as cells go (40-80% of every team's boxed deaths are
   on a cell where a team-mate had died), but SSS has a third of the others' boxed deaths on Slithery Fight (88 against
   207-288 in rounds 0-150); in the game read it splits at 4 and 5 where we shed at 6-8, eats a quarter fewer pearls than we
   do and has more total length at round 150.
7. **The brief: "we ram much less (3 rams started against 9-12)".** The count is right; two things about it are not where one
   would look. First the cost: in dragons a ram is one for one whoever starts it, and in segments we even lose a little less
   than the enemy (296 against 332 per large-map game); the cost is the pearls (28% against 67%) and the ground. Second the
   kind: more than half of everybody else's rams are charges from two or three cells away (8.7-13.7 a game in rounds 0-149
   against our 1.0), so a rule that only answers at a meeting, like the test build's, closes about half of the gap in rams
   made (13.8 a game in rounds 0-149 against the live bot's 5.1 and the opponents' 22.9).
8. **The brief: Islands, "a 4-cell dead-end corridor where a split child walks in every 6 rounds".** It is there ((40,12): 14
   deaths in 150 rounds of 1068051). The larger countable loss on that map is another: 18.4 dragons a game in rounds 0-149
   step through a portal onto a body they cannot see, 43% of our non-ram deaths there.
9. **`findings.md` section 2 reads the large maps as one.** They are two pairs. Australia and Islands: units and length both
   collapse (1 win in 58). Around UNSW and Slithery Fight: units level, length 60-80% (11 wins in 53). A change that only
   raises the unit count will not show on the second pair; the test build shows it: against the live bot's game with the
   same opponent it has 36-79 segments more total length at round 150 in all four pairs on Australia and Islands, 6 and 49
   more on Around UNSW, and 21 and 33 fewer on Slithery Fight (`c_out/pairs_large.md`).
10. **"Win rate by size: large 13%" as the thing to explain** (`findings.md` section 1). Two different gaps are in that number, and
    the earlier notes study one each without saying how they add up. Counted (`c_endstate.py`): at round 300 we are behind in
    total length in 108 of our 109 large-map games that reach it; forgot in 82 of 158, SSS in 48 of 139, Vibing++ in 40 of
    127. Of the games in which they are behind, they still win 35%, 50% and 40%; we win 10%, and all 12 of our wins are
    longest-dragon wins, 11 of them from behind. So the economy is why we are always behind, and the end game (A, A2) is why
    a game in which we are behind is won three to five times less often than one of theirs. With their conversion and our
    economy we would win 35-50% of the large-map games; with our conversion and their economy I cannot say, because we have
    one game to judge it by.
11. **Thin everywhere, this file included: what a team does in rounds 300-500 with an economy that is level.** forgot was out-eaten
    by test4 on Australia (120 natural pearls against 287 in rounds 0-149) and on Trauma (9 units against 20 at round 100) in
    the games read and won both; the test build is ahead of WHQ at round 150 in 1068050 and 1068051 and loses both; on Portals,
    where the teams never touch, we end 21 losses with as much total length as the winner (50 against 52) and a longest dragon
    of 30 against 42.
