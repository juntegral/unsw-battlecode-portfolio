## What I could not determine

1. **What any rule does in a real game.** Every "expected effect" here is arithmetic on games that were played. No
   game was run. The strict readings change one event and keep the rest of the board; the realistic ones borrow our
   own or the top three's rates for the new state. Neither is a measurement.
2. **What the enemy does once its queen is dead, in that same game.** Across games our opponents end with a longer
   longest dragon when their queen is dead than when she is alive (56 against 46), which is why I trust the low
   strict count of candidate 1 (6 or 7 games) more than the lenient one (13). What a given opponent would have built
   in a given game cannot be seen.
3. **What an earlier kill is worth.** In 80 games candidate 1 would kill her 70 rounds earlier on average without
   changing who is alive at the end. A queen that makes most of her team's new dragons dies with that; I counted
   nothing for it.
4. **How long a saved queen of ours lives.** Candidate 2's range (3.7 to 11.1 wins) is the distance between "at our
   own other death rates" and "like a top-three queen". The turns on which she already steps away (rammed within ten
   rounds in 19-24% of cases) suggest the middle; only games can tell.
5. **What a dragon of ours knows.** Candidate 3's mechanism (the leader is the longest own dragon a dragon has heard
   of; pearls within 9 cells of its last known head are left alone) is read from the source. The replay shows the
   fall at the switch round and a slope with the distance from longer dragons, not the leader each dragon had in
   mind. Why the rate is still 72% and not 83% far from every longer dragon, I can only guess (a position remembered
   for up to 25 rounds; self-styled leaders that no longer go into tight places for pearls).
6. **How much length the leader switch costs.** +12% to +24% at round 300 is inferred from growth on the other maps
   and from the pearls declined, not measured. The three local trials of the same change were neutral; local games
   are a poor witness, but they are the only trials.
7. **Whether the trade-on-contact build's 0 wins in 12 big-map games is bad luck.** Its economy moved as the swing
   count predicts (+34 segments a game from its own rams, +25 total length at round 300 measured). Our band win rates
   predicted 1.7 wins. Twelve games cannot separate "economy does not convert for us" from chance.
8. **Whether the top teams really count heads.** "Not outnumbered" in candidate 4 is my count of heads in the
   replay's 7x7 squares. It separates their behaviour very sharply (about 90% against 14-19% for same-length enemies
   on the next cell), but their code may test something else that goes with it.
9. **Whether rams on shorter enemies would pay for us.** They pay the top three +1.1 segments each because their
   team eats 84% of the pearls. In our 31 such rams on big maps our team ate 55% and the swing was -0.7. Whether that
   is a property of our bot or of 31 odd cases I cannot tell.
10. **Whether our own queen should ram hers** when both are alive and hers is the longer. Candidate 1 excludes the
    queen as attacker. It would turn a queen-length game we lose (11 of 14) into a longest-dragon game (29%), but I did
    not count how often she has the chance.
11. **Whether `hunt_path()` sees exactly the chances counted here.** It searches cells that are free at that moment,
    like the stricter of my two counts (435 chances, 99 taken). The qh31 build, which used the same function, took 8
    of 9 with 2-3-longs; the one it missed I did not trace.
12. **Which build played each ladder game.** The two ladder downloads are "the live bot of that hour". The live and
    candidate columns agree wherever both are shown, so I pooled where it did not matter.
13. **Whether opponents would adapt.** The top teams update their bots often. Candidates 1 and 4 feed on what the
    enemy does today (queens that walk into reach, small dragons that come to us); a changed opponent changes the
    numbers.
