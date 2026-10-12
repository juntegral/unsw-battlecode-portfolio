## 8. Where `findings.md`, `hypotheses.md`, `redteam.md` or the earlier deep reads look wrong or thin

1. **The footing of the race gap (`redteam.md` section 1; repeated in my brief).** "At equal economy the gap stays on
   small maps: with own / enemy total length at round 400 between 0.8 and 1.25 we win 9 of 30, the top three 22 of
   40." Total length at round 400 is not the economy once somebody has fed: a 2-long feeder leaves 1. In those 30
   games of ours the enemy had 90.5 against our 65.5 at round 300 (potential 54 against 39.5) and had caught down to
   us by converting; in 17 of the 30 the enemy had over 1.25 times our total at round 300. In the top three's 40
   games the top team was ahead at round 300 (101 against 94). On potential, which feeding does not change, we win
   11 of 23 level races at round 300 and 12 of 24 at round 350. The sentence "the largest countable gap that no
   candidate works on is the longest-dragon race" should read: the race is where the economy gap is paid; a gap of
   its own is small (our rate at level potential is about 50%, the top three's 58-59%; against test4 and WHQ only, 10
   of 21 against 11 of 13).
2. **"After round 400 both grow by about 20" (`hypotheses.md`, "Not proposed").** The others do (15.5-26 in the
   median race); our live bot's longest grows 10 on small maps and 14 on big ones, the test builds' 21 and 9.5. And
   "it has been tried directly" covers only the clock (rounds 330 and 300); what breaks after the clock starts was
   not tried. B's ceiling for the whole race gap (+6.9 wins of 268 games on the total-length bands) agrees with mine
   on potential (+4 to +9.5 of 401), so dropping it then was fair.
3. **"Our late feeding often feeds the opponent" (`findings.md` section 7, the team's note).** On the same count for
   every team the enemy eats 4.7% of the pearls of our deaths by choice on small maps and 10.5% on big ones (others
   0.6-2.4% and 1.8-6.0%). It is two to eight times the others' share and still one pearl in ten at most; seven times
   as many of our pearls go to another small dragon of ours. It happens when an enemy head is within 8 cells of the
   dying feeder (15% within 4 cells, 8% at 5-8), and our rule asks only for more than 4.
4. **"Top teams ... feed from about round 300" (`findings.md` section 7).** SSS and WHQ do, and forgot with a full
   team. Vibing++, rank 1, starts at round 360 with a full team and at 370-400 otherwise, and test4 waits for its
   queen to die. The start does not sort the teams by strength.
5. **"About 2.6 segments spent per segment it gains" (`deep-read-2.md`).** That is the gain of the dragon fed at the
   moment. Followed to the end of the game, the dragon that wins the race gains one segment per 3.4-4.3 spent on
   small maps (0.23-0.29 per feeder segment) and one per 5-11 on big maps (0.09-0.19): of the pearls dropped, the
   final longest's lineage eats 36-47% on small maps and 15-31% on big ones, for every team; the rest goes to
   dragons that do not end as the longest.
6. **"forgot starts at about round 200-225, SSS at about 200-300" (`deep-read-2.md`, as quoted in my brief).** For a
   leader that is not the queen: forgot at round 300 with 56 or more units and about 370 otherwise (median 359 over
   309 games), SSS at 301 (221-302 only with a full team, on big ground). The earlier rounds are queen feeding.
7. **Candidate 3's open risk (`hypotheses.md`): "all our wins on these maps are longest-dragon wins, so an earlier
   leader may be part of some of them."** It is not the zone that builds the big-map leader. After the switch the
   leader of the time eats 1.6-3.4 natural pearls per 50 rounds, fewer than before it (4.0); of the pearls our small
   dragons leave in the zone the leader gets 7-17%; our longest is 10 at round 200 and 14 at round 400. What builds
   it in the four wins read is feeding from round 201-204 with 56-60 units, and the leader's not splitting. So
   candidate 3 keeps those wins if the fed dragon still stops splitting once feeding starts (B's own caveat).
8. **The pearl rate after the switch, "56% instead of 80%" (`findings.md` 6c, `hypotheses.md` candidate 3).** It is
   a mixture. By the dragon's own belief (readable games) it takes a pearl inside its believed leader's zone in
   18-26% of turns and outside it in 75-87%. B's "slope with distance, not a step at 9 cells" is the remembered
   position: B inferred it, the pings show it.
9. **"None of the test builds changed the leader or feeding rules" (my brief).** True of the rules as far as the log
   says, but the test builds end small-map races at 0.71 of potential against the live bot's 0.65, grow 21 against
   10 after round 400, and do not show the cut contrast there (9.9 and 9.7; 42 and 13 windows). Either 25 races are
   too few, or a movement change (their leader takes 65-79 steps per 25 rounds against 53-59) matters to the race.
   Nobody has compared the builds' races; I only counted them.
10. **The list of 14 "losses with at least level total length at round 400" (`x_out/race.txt`).** A good reading
    list, a bad sample: by potential the enemy was clearly ahead at round 300 in four of them (1045202 43:58,
    1058858 31:53, 1063682 29:55, 1027971 29:42) and we were clearly ahead in three (the weakhold games, 39:22,
    54:24, 41:23). Seven of the 14 were lost after being level or ahead in the longest dragon after round 425; the
    other seven were not conversion losses in that sense.
11. **Cards #14 and #22.** `findings.md` lists them as known to the team; `work/plan.md` has no entry for either
    (it ends on 2 October with v61). Whatever "late feeding (card #22)" tested is not in anything I could read.
12. **Thin in every earlier file, including the brief:** a team's own second and third dragons. The team's log
    notes that the top teams "often keep a big 2nd dragon too"; nobody counted what happens to it. On small maps
    test4 and WHQ feed it to the leader late (1.3-1.5 dragons of 8+ a race in the last 50 rounds) and the top three
    mostly do not (0.2-0.6); on big maps everybody ends with several (second / longest 0.45-0.72).
