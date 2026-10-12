# Astra analyst: longest

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `longest`.

Question: games lost on the longest dragon. 16 of 71 losses in one1-one3 were lost on longest (both queens dead), the gap is 22 at
the median, our total length was the larger one in 5 (all against WHQ), and we end with 24 dragons unspent (median).
1. For every game of one1 to one5 decided on longest (won or lost): the longest dragon of each side every 25 rounds from r200, who it
   is (queen, fed leader, an ordinary long dragon), how it got its length (pearls it ate, feeders dying beside it, eating drops),
   and whether it died (round, cause). Our total against theirs at the end.
2. What do the opponents do in the last 150 rounds that turns total into longest: stops beside a longer mate (count, round), a queen
   fed from which round, dragons folding from N to M. Ours: feeding phase start (FEED_CAP_ROUND 350 since one3; feed_round otherwise),
   how many feeders reach the leader and how many die on the way, how far the unspent dragons are from the leader at r400.
3. An end rally exists and is off (RALLY_END_FRESH; `rally_ready()`): a local check of it on top of one4 is running, arms `mArl_vh`
   (rally) and `mAl4_vh` (one4) in `~/meow-redteam/solo/runs/`; include its table if the games are there: dragons alive at the end,
   our longest at r400 and at the end, whether the fed body is rammed.
4. Card: the one rule that converts unspent dragons into the longest body without feeding a body that is then rammed.
