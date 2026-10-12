# Frozen method — 2026-10-01

This file is written before replay deep reading. All permitted online sets are censuses,
not samples. Current waves and historical sets are separate outcome populations.
W0 has three actual runs; W6/W7 have the same stack6 bot. W12 is included if available
when the population manifest is frozen; its absence is explicit. Every opponent is
one of 306, 70, 20, 801, 264, 46, 545. No filtering on replay success or outcome.

1. Join every index/game JSON to mass-ledger and endgame-king caches. Independently
   reconstruct every permitted raw replay using official head/tail updates, without
   importing either extractor. Report both counts and every mismatch. Missing cached
   features use the independent reconstruction and are marked as such.
2. Count classes over the full population. Wins: opponent eliminated; otherwise late
   opponent king loss (a current longest dragon of length >=8 dies at r>=300);
   otherwise won the final length race. Near-miss losses have positive enemy final
   longest and own/enemy final longest >=0.8. Their exclusive mechanism is the largest
   positive term in the final-line identity difference from r300 (initial lineage,
   natural pearls, own sacrifice pearls, other own death pearls, enemy death pearls,
   sprint cost or split loss); ties use this listed order. If either lineage is absent,
   use "no r300 decomposition". Also classify losses after leading current longest at
   r300 or r400, prioritizing our subsequent king death, then opponent sacrifice growth,
   then other growth. Near-miss and lead-loss sets can overlap and are not added.
3. Select the two lowest numeric game IDs per win class, near-miss class and lead-loss
   class, across all permitted sets; deduplicate selected games. For each selected win,
   also read the lowest-ID loss on the same map and opponent, preferring the same bot
   era (waves/history). Do not change selection after reading. Produce raw event and
   dragon pointers, then write a step-by-step narrative for every selected replay.

All-game visible-failure flags are measurable observations, not claims about intent:
timeout, enemy head collision, or current-king self death with a legal free neighbour.
Intentional feeding is possible; call a self death a candidate mistake only when
recovery is poor, and explain that intent and the counterfactual are unobserved.

Natural intake ratio is own/enemy; a zero enemy denominator is missing, never silently
smoothed. Late pieces are new children born with length <=3 at r250..499 (not stubs).
Exposure is the fraction of final-king-line turns at r300..499, with length >=8, whose
nearest enemy head is within toroidal Manhattan distance 6; walls and portals ignored.
Checkpoint counts and current kings are conditional on the replay reaching that round;
absorbing terminal values are provided separately, with explicit denominators.

Wilson 95% intervals apply to binomial proportions (W/D/L, elimination and longest
dominance). Lengths and other continuous quantities use mean 95% t intervals and
median/IQR; Wilson intervals for a continuous length would be invalid. Intervals
describe repeat-seed uncertainty, not uncertainty about this enumerated census.

Models condition on map x opponent using informative-stratum fixed intercepts, with
wave-cluster robust intervals where feasible. Early models use only information
available by r100; landmark models use r300 survivors and by-r300 information.
Retrospective models use late features and are labeled association only. Final longest
and elimination are outcome-defining, so are tabulated but excluded from predictive
covariates. Static map layout main effects are not identifiable with map fixed effects;
report layout tables and an explicit layout-interaction sensitivity model instead.

Power: two-sided alpha .05, 80% and 90% power, independent equal-size old/new arms,
normal two-proportion approximation. Effects are +3/+5/+10 wins per 60. Estimate
repeat-wave dispersion from merge2 x3 and stack6 x2 (3 residual degrees of freedom),
show its wide interval, retain a binomial floor, and show an upper-dispersion sensitivity.

All outputs are exclusive-created new files in the authorized paths. No network,
uploads, commits, external sites or credentials. At most one analysis worker; resource
checks pause below 10% free memory or 20 GiB disk. The sandbox denied nice -n 15;
heavy execution requires the user's explicit acceptance of inherited niceness 10.
