## Things I could not determine from replays

1. **Why a dragon declines a free pearl next to its head.** The count is solid (who, when, where); the reason is the bot's score for
   that step, which a replay does not hold. Before round 150 our rate is the same as our opponents' (80-82%); what the missing
   18-20% are I did not find. The one case I followed (1068051, `#3` at (1,37), round 20) had no enemy in view, an open cell,
   and a team-mate three cells away.
2. **Whether the leader zone is the whole reason for the drop at round 150.** The drop is deepest within 9 cells of our longest
   dragon (44%) but is also there with no own dragon of 5+ within 9 cells (67% against 82% before). A remembered leader
   position would explain it; the replay does not show what a dragon remembers. A run with the rule's log line switched on
   would settle it.
3. **Which build played each game, beyond the run name.** The smoke runs name their candidate, and three candidates have their
   source kept (`tc30-bot`, `qh31-bot`, `qn23-bot` under `data/online/smoke/`); the candidates "stride" and "passage2" do not, and
   the two ladder downloads (177 games) carry no mark at all. Whether the live bot itself changed between the four "-old" runs
   of 4 October I did not check; its moves of two or more steps in rounds 0-149 are 7, 13, 18 and 38 a game in those runs,
   which may be the build or the game. The pocket rule in particular: by my own reconstruction of kelp-closed regions our
   dragons still eat 68% of the adjacent pearls in pockets that the rule would forbid (small maps), so either it was not in
   those builds, or it rarely fires because a dragon has not seen every edge of the pocket.
4. **Why our queen waits at the portal door on Stripes.** She has the two pocket pearls in view at round 7, is on the door cell at
   round 18 and goes in or not; forgot's queen goes in at round 8 from the same start. The pocket has four cells, which our
   pocket rule would call too small for a dragon of 2, and in the game in which she stays out an enemy head is two cells from
   the pocket. Either may be the reason; the replay holds neither.
5. **Whether test4 and WeHaveQuizzes know the maps.** Their first dragons are on the fountains at rounds 11-12 on Stripes (through
   a portal) and at round 20 on Trauma, and inside our pocket on Australia at round 33. Knowledge, a strong pull towards
   portals, or symmetry reasoning: a replay cannot tell. They are not always fast: WHQ is stuck in its start room in the
   Tower Defense game read and does not find its fountain column on Trauma until round 130, and test4 is stuck on Tower
   Defense against forgot.
6. **How the opponents' dragons come to stand in our half**: by a rule that sends them there or simply by not turning back at an
   enemy head. The counts fit the second (they end the turn nearer to an enemy head in view in 18-21% of turns, we in 12-13%)
   but do not exclude the first. The same goes for our side: the test build shows that ramming at a meeting does not bring our
   dragons forward, and which of our rules holds them back (the penalty next to small enemy heads, the pearl-target rule, or
   something else) is in the scores, not in the replay.
7. **The true pearl supply.** The replay hides each tile's spawn gap; my "fountain" tiles are counted from appearances, and a
   tile that is eaten promptly appears more often, so the pooled rates are lower bounds and the supply is not strictly "the
   same for both sides" once one side leaves pearls lying.
8. **Whether SSS remembers the cells where its dragons died** on Slithery Fight, or only splits earlier.
9. **Why the same pearls cost us more dragons on Portals** (a dragon lost boxed for every 1.6 natural pearls; test4 1.9, forgot 2.1,
   WHQ 3.3). Our deaths repeat on fewer cells and come more often right after eating there, but we do not take pearls in
   dead-end cells more readily than our opponents. I did not follow single dragons on that map.
10. **Whether opponents call team-mates to a fight or a corpse by sonar.** I did not read the sonar values. That the enemy has
    more heads within 8 steps of a ram in 53% of the rams in our games (top three: 44%) may be numbers, position or a call.
11. **What our win rate would be with a level economy.** We are level or ahead in total length at round 300 in one large-map
    game of 109 (and won it). The top three win 68-75% of such games.
12. **What a ram is worth exactly at each length pair.** I counted who eats the pearls and what the two dragons eat in the next
    ten rounds; I did not follow the units that each side makes from those pearls.
13. **Whether the trade-on-contact test would have won more with more games.** 0 wins in 12 large-map games against a base rate
    of 12 in 99 is no evidence either way.
