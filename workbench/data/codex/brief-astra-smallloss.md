# Astra analyst: smallloss

Read `data/codex/astra/ASTRA-COMMON.md` first, then `data/codex/astra/CARDS.md`; your name is `smallloss`.

The live bot keeps getting better online against team kraken (one8 9 of 15, one9 10, one10 12) and at the same time worse
locally on small maps against our own OLD main, a much weaker bot: on four small maps, both sides, eight games each, one5 wins 8,
one8 7, one9 6, one10 4, and one10 with QUEEN_WAR 8 on wins 3 of 7. All the losses are by elimination. A bot that a weaker
style can wipe out on small maps will lose games in the qualifier, so this needs its cause before the next version.
Local replays (same map, seed and side for every arm, so pairs are exact):
`~/meow-redteam/solo/runs/<arm>/<map>-seed1-side<K>/game.replay` with `result.txt`; the arm plays side K (side0 = player 0);
the opponent is `~/meow-redteam/solo/bots/m3base`. Arms: `mDl5_vb` = one5, `mDone8`, `mDone9`, `mDone10`, `mUw11_vb` = one10 +
QUEEN_WAR 8. Maps: `sqheld_open_small_90012` (one5 W W; one8 L W; one9 L L; one10 L L), `ladder_stripes_1` (one10 loses side1;
the war arm loses both), `sqheld_portals_small_90029` (one10 loses side1), `sqheld_blobs_small_90028` (all win).
Sources with the switch values of each version: `data/online/smoke/one<N>-bot/main.cpp`.
1. For every lost game: the round where it parts from the one5 game on the same map and side, and from there every 10 rounds
   dragons / total length / queen for both sides, our deaths by cause with the dragon's length and what it was doing (ramming
   their queen, evading, split child, wait-split, boxed), their deaths, pearls eaten. The moment our count falls behind for good.
2. Which switch that the losing version has and the last winning version has not is acting in those rounds? one9 added
   REACH_EATS, SPLIT_PORTAL_OK, QS_KEEP_MIN_UNITS 6 (was 2), SHORT_EVADE with one paid step; one10 added QUEEN_SURE_LEN 64 /
   QUEEN_SURE_STEPS 5 (any dragon rams their queen within 5 steps), CUT_BODY_LEN 4 / QS_PAY_REACH 4, QUEEN_PORTAL_ALL,
   QUEEN_BOOT_LEN 6; one8 added SMALL_SPRINT_THREAT, MATE_UNPIN, POCKET_KEEP_OUT, TARGET_REACHABLE, QUEEN_SURE_LEN 4. Use what the
   dragons do in the replay and the code; count the turns each suspect switch changes.
3. Is it one switch, or the sum of safety rules making short dragons too timid to eat on a small board (pearls per dragon turn
   in r0-100 per version)? Does old main do something our rules are blind to?
Verdict: the switch(es) to change and how, as a general rule (a condition on the situation, never on the map or its size), with
the count that decides it. Under 500 words plus tables; first three lines = why the newer versions get wiped out on small maps
by a weaker bot, the change, how sure.
