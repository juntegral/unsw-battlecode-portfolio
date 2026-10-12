## 6. What I could not determine

1. **What any of the four rules does in a real game.** I ran none. Every size in this file is arithmetic on games
   that were played, or a comparison inside them that still leaves the winning side looking better.
2. **Whether a kill of her queen causes the win or comes with it.** The comparisons that hold the economy, the round,
   our own queen and the local head count fixed leave +2 to +9 points on the games concerned, with a range that
   includes zero. Only games with the switch on can narrow it, and it takes about 300 a side on the end state to see
   it.
3. **Why our own queen died earlier in all three hunt runs** (40 pairs earlier against 24 later). Two runs of the
   same bot differ as much, so I cannot call it an effect; I cannot rule it out either.
4. **How a veto built from the bot's existing pieces behaves.** I counted what those pieces would see on the turns
   of played games (`x_c2vis.py`); what the queen then does on the next turn, and the turn after, is not in a replay.
5. **Which part of the queen rules cost local wins on small maps.** The log gives the totals (16 to 13 and 11 to 7)
   and says it was not the trading. Candidate 2 switches on the threat map and the trade ban there and leaves the
   portal ban off; nobody has played that mix.
6. **Whether the leader built from round 150 wins our big-map games or only comes with them.** Among all teams the
   longest dragon at round 300 has no weight in who wins a both-queens-dead game once total length is counted; in our
   own 65 such games it has. With 12 wins I cannot tell which is the truth for us.
7. **How much length the round-150 switch costs.** In our big-map games with a full team at round 150 our total
   length still grows 13% to round 300 (the top three 25%, our opponents in those games 39%); in the others we
   collapse whatever the rule. B's +12 to +24% is possible for the first half and unknown for the second.
8. **Whether "feed the longest dragon earlier" would close the gap on the smaller maps.** The gap is measured (30%
   against 55% at level total length). The trials of the simple version were neutral, on an older bot and map pool.
9. **Anything against the three top teams.** We have 21 games against them. The opening exists (their queens offer
   in-view chances as often as test4's and WeHaveQuizzes's); what a kill is then worth to us, I cannot count.
10. **What the qualifier maps are like.** Candidate 3 and nine tenths of candidate 4 act only on maps over 1,200
    cells (5 of the 15 known maps); the shed-not-cut part of candidate 2 is worth most where a queen starts long and
    coiled (one known map). None of this can be said of maps nobody has seen.
11. **Which build played each ladder game.** As B: the two ladder downloads are "the live bot of that hour".
12. **Whether the opponents will change.** test4 and WeHaveQuizzes are the opponents in 313 of our 401 games; the
    numbers for candidates 1 and 2 are, to a large part, numbers about those two bots as they were this week.
