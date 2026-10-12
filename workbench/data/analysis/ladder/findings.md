# Ladder findings ledger (team 1119)

Rewritten 7 Oct 2026 18:20 KST (run 20261007-1800, the thirteenth run; it started 18:01 KST; the runner skipped the analyst at 16:00 and 17:00). Data: 940 games in 188 ranked battles,
5 Oct 15:14 UTC to 7 Oct 08:16 UTC. By our code: main 485 games (97 battles), v31 410, test builds 45 (never used below).
main results: 259 wins / 485. By opponent rating: under 1700 13/15, 1700-1899 119/190, 1900-2099 110/210, 2100+ 17/70. Battles on main: 3 of 3, 28 of 38, 24 of 42, 2 of 14.
New since the last run: 50 main games (10 battles, all bot id 18570, the main source): 27 won; 7 battles won, 3 lost, all three against 2100+ (2175, 2180, 2408: 4 games won of 15).
The 23 losses: 13 on longest dragon with both queens dead, 8 eliminations (4 by round 125, all four on Stripes), 2 on the queen rule with only their queen alive.
By layout in the new games: Stripes 0 of 5 (all by elimination, rounds 58 to 166), Islands 0 of 2, Around UNSW 0 of 2, Tower Defense 0 of 2, Portals 3 of 7; weakhold 4 of 4.

## Summary (10 lines)
1. F31 (confirmed). On layouts above about 1200 cells our dragons eat a quarter less from round 151 on: pearls in r151-200 are 0.73 of r101-150, the opponents' 1.12 (137 main games, ours lower in 124). New games in line (0.72 against 1.04 on 9).
   These are LEADER_GROW_ROUND_BIG 150 and LEADER_GROW_ROUND 300. main wins 58 of 154 on big layouts, 201 of 331 elsewhere; Islands 0 of 23. Test: one constant, locally (change 1 of the team's plan).
2. F42 (confirmed; new sight counts this hour). 26 of our 58 queen-rule losses with only their queen alive had our longest dragon the longer one: 12 percent of all main losses. By the bot's own rule (her head in view) we hold a sighting 20 rounds old or less in half of her turns,
   and in four fifths of those no dragon of ours is within 6 steps of her (the same for their dragons and our lone queen: two thirds). Big layouts: we lose sight of her. Small layouts: we see her and do not get there. Portals: she cannot be reached at all. A longer QH_FRESH alone reaches a quarter of her turns more, from far away.
3. F44 (confirmed, narrowed by the verifier; opening counts to-verify). Wiped out by round 125 in 18 of 94 main games on five small layouts with the queens 10 tiles apart or less (7 of 17 against 2100+); never on Default, Portals, Tower Defense or weakhold. In those games their 2- or 3-long dragons are the rammer in three opening meetings of four; elsewhere on the same layouts in two of five.
   Question 2: in rounds 0-60 on small layouts the 2100+ teams are the rammer in 0.65 of meetings (v31 0.60); teams below 2100 in 0.43 to 0.51.
4. F45 (new, to-verify). The 52 main losses by elimination after round 125 are mostly the opening too: in 41 our length was under 0.8 of theirs at round 100 (v31 49 of 58). The ladder shows no separate fault in the fighting after round 100.
5. F7 (confirmed on main by the verifier). Tower Defense and Stripes: 6 or fewer dragons at r100 in 53 of 55 main games; 12 won of 55. New games 0 of 7 above 6. On Stripes our pearls by r50 were never above 8 in 24 games.
6. F37, F13, F24 (confirmed; the queen). F13 bar met and passed (18 of 24). F37 bar not fired, but no gap in this block (5 of 21 against 4 of 19). F24: rammed in 10 of 24 against 1900+ (line 0.40; 30 needed), and we rammed theirs in 13.
7. F11, F25, F10 (confirmed): in line, short of their counts (0.29 of pearls on 8 large-layout games; a level position grew in 0 of 6; 0.22 of pearls by r50 on 7 scarce-layout games).
8. F4 (candidate; 2100+): behind at r100 in 6 of the first 10 new games (line 5), 53 of 70 in all. Against 2100+ we are wiped out in 0.30 of main games, against 1700-1899 in 0.10.
9. F46 (new, candidate, adds little): with both queens dead at round 500 we win 8 of 22 against 2100+ on main; that is above our overall 17 of 70 against them. Still weakened: F35, F38 (not re-counted).
10. Not done: F38_long_new and F39 on new games (pass work/h25 not rerun), question 3 (versions). Tests in order of size: F31 constant; F42 hunt switch in two arms (memory for big layouts, hunter speed for small); F44: one count first (do our dragons stand in reach when outnumbered); Tower Defense and Stripes start (team card).

Slices used: band b = main games vs opponents rated 1700-1899 (190 games); band c = 1900-2099 (210 games); band d = 2100+ (70 games, fourteen battles; used only together with v31 band d, 50 games);
half 1 / half 2 = main games before / from 2026-10-06 14:48:15 UTC (97 and 388); v31 = the old bot, 410 games (bands b 210, c 135, d 50), used as a second code slice.
"Free layouts" = layouts where the queen can leave spawn (Schooltime 1 and 2 and Slithery Fight left out). "Large" = 2000 or more open tiles. "Big" = width times height above 1200, the line in the bot source: the five large layouts and Slithery Fight.
"Full game" = a game that reached round 500 (no side wiped out). "Lone queen" = a queen whose opposite number died in an earlier round. "Level game" = total length at r100 within 20 percent of each other.
"Narrow tile" = a tile with two or fewer sides without kelp (portal sides count as open). "Short" dragon = length 4 or less. "Stay" = a run of consecutive queen turn starts on narrow tiles; "long stay" = 3 or more.
"Queen rule" = at round 500 the longer queen wins and a dead queen counts as 0. "Path steps" = steps along open tile sides and through portals, dragons ignored. "2-dragon-start layouts" = Maze, Queen Of Spades, Stripes, Tower Defense, Trauma, Trophy, weakhold.
"The five layouts" (F44) = Stripes, Trophy, Devil, Prisoners Dilemma 1 and 2. "Early wipe-out" = none of ours left by raw round 125. "Mover" or "rammer" = in a head-on meeting, the dragon whose turn it was; both dragons die. "f42_set" = full games lost on the queen rule with only their queen alive, free layouts.
All figures are from rows.jsonl unless marked "own count" (scripts in work/, named in each block). "r100" is raw round 100 (state after 101 rounds).
The 15 games against teams rated under 1700 are in the totals and in no band.
The bars counted this hour on new games, and F44_rate, F44_who and F42_sight, were saved in state.json by run 1500 before any of the 50 new games existed. Three bars are of this hour (E2_r100 for F45, L1_band for F46, F42_sight_head): each was saved before its count, and what I had seen is listed in state.json under bars_run_20261007_1800.
The verifier results of 15:26 KST on F44, on the F42 hunt count and on F7 (all three: holds in part) are folded into their blocks.
Blocks keep the order of earlier hours (F45 and F46 follow F44; refuted findings are at the end). Older run-by-run lines are kept inside each block as they were counted.

### F31 On layouts with more than 1200 cells our dragons eat and split much less from round 151 on while the opponents do not; on smaller layouts the same step comes at round 301. Those are the bot's own switch rounds
status: confirmed (verifier 07:54: holds in part; the step itself holds in every check, three points of wording do not, see below); cost in games still not shown      first seen: 7 Oct 07:06 KST run 20261007-0700   last tested: 7 Oct 18:20 KST (rows.jsonl, new games)
measured: Big = width times height above 1200. In this data: Around UNSW, Australia, Schooltime 1 and 2, Islands, Slithery Fight. main wins 35 of 88 games there and 122 of 192 elsewhere (v31 48 of 119 and 155 of 291).
  Pearls (rows.jsonl curves; every game that reached r200 with 20 or more of our dragons alive at r150): pearls eaten in r151-200 divided by pearls eaten in r101-150.
  Big layouts: main ours 0.768 (11,403 then 8,761; 81 games), theirs 1.134 (14,496 then 16,442). v31 ours 0.734 (16,851 then 12,374; 111 games), theirs 1.098.
  Our ratio is the lower one in 73 of 81 main games and 91 of 111 v31 games, and against 29 of 29 opponents on main (36 of 41 on v31). The step before it (r51-100 to r101-150) is 1.05 and 1.08 for us, 1.16 and 1.22 for them.
  By layout, ours / theirs, main then v31: Islands 0.51 / 1.15 and 0.59 / 1.18; Slithery Fight 0.69 / 1.04 and 0.63 / 1.01; Australia 0.88 / 1.32 and 0.77 / 1.24; Around UNSW 0.83 / 1.12 and 0.85 / 1.06;
  Schooltime 2 0.97 / 1.08 and 0.91 / 1.12; Schooltime 1 1.27 / 2.04 and 1.28 / 1.62. Ours is below theirs on all six in both codes.
  Slices on main: opponents 1700-1899 0.77 / 1.14 (34 games), 1900-2099 0.76 / 1.12 (40), 2100+ 0.79 / 1.20 (7); earlier half 0.83 / 1.10 (28), later half 0.74 / 1.15 (53); the 7 games of this hour 0.71 / 1.37.
  With 55 or more of our dragons alive at r150: 0.77 / 1.12 (57 games); with fewer: 0.77 / 1.19 (24 games). With 20 to 44 alive (bar F31_cap, main and v31 together, 46 games): 0.76 / 1.15.
  So it is not the limit of 60 dragons (SPLIT_SOFT_LIMIT).
  Layouts of 1200 cells or fewer, same measure: ours 1.250, theirs 1.236 (main, 68 games); 1.186 and 1.203 (v31, 97 games). Ours lower in 27 of 67 and 42 of 97 games. No such layout has ours more than 0.15 under theirs.
  On those layouts the step comes 150 rounds later: pearls in r301-400 divided by pearls in r201-300 (games reaching r400 with 10 or more of ours alive at r300): ours 0.811 (main, 85 games) and 0.790 (v31, 106), theirs 1.045 and 0.934.
  On big layouts nothing happens at round 300: 1.02 against 1.02 in both codes.
  Dragons alive on big layouts, ours / theirs: main r100 45 / 45, r150 52 / 53, r200 48 / 57; v31 47 / 46, 53 / 55, 49 / 59.
  Splits (own count, work/h14_pass.py and h14m_pass.py: split events per 25 rounds; games that reached r175 with 20 or more of our dragons alive at the start of r150; all 690 main and v31 games covered): splits in r150-174 divided by splits in r125-149.
  Big layouts: main ours 0.684 (1,853 then 1,267; 80 games), theirs 0.982. v31 ours 0.666 (2,849 then 1,897; 111 games), theirs 0.920. Ours lower in 62 of 80 and 90 of 111 games.
  Per game on big layouts, r125-149 then r150-174: main our splits 23.2 then 15.8 (theirs 28.9, 28.3), our pearls 70.1 then 54.3 (theirs 91.0, 99.0), our deaths 20.9 then 18.3. v31 splits 25.7 then 17.1 (31.6, 29.1), pearls 76.2 then 56.5 (101.8, 104.3).
  Smaller layouts at round 150: 1.077 against 1.064 (main, 73 games), 1.083 against 1.082 (v31, 105). At round 300 (r300-324 over r275-299): ours 0.623 (main, 48 games) and 0.580 (v31, 74), theirs 0.947 and 0.921.
  Big layouts at round 300: 0.95 against 0.94 and 1.00 against 1.03.
  Adjacent pearls (own count, work/h13_pass.py and h13m_pass.py; main big layouts complete, 88 games; v31 392 of 410 games): share of non-queen dragon turns that start with a free pearl one step away, with no enemy head within 2 tiles of it, and end without eating.
  Big layouts by round, r101-125 / r126-150 / r151-175 / r176-199: main ours 0.225, 0.239, 0.401, 0.405 (about 6,000 turns each); theirs 0.236, 0.245, 0.245, 0.236. v31 ours 0.227, 0.233, 0.413, 0.413; theirs 0.220, 0.219, 0.224, 0.213.
  It stays at 0.40 to 0.44 to the end of the game. Smaller layouts (v31, 277 games): ours 0.16 to 0.21 in every bin up to r300, then 0.446 in r301-350 and 0.487 after; theirs 0.20 to 0.27 throughout.
  (main, only 16 smaller-layout games covered: 0.22 to 0.26 up to r300, 0.50 in r301-350.)
  Where, big layouts, r151-199. Pearl within 9 tiles of the head of our longest other dragon: ours leave 0.498 (main, 1,701 turns) and 0.528 (v31, 2,618). Farther: 0.386 (9,788) and 0.390 (13,243); 19 tiles or more away still 0.380 and 0.390.
  Before round 151 the same cells give 0.180 and 0.195 inside, 0.253 and 0.245 outside. Their dragons in r151-199: 0.254 and 0.218 inside 9 tiles of their longest, 0.237 and 0.219 outside.
  When the acting dragon is itself our longest: 0.240 before and 0.292 after (main), 0.259 and 0.314 (v31). When it is not: 0.231 and 0.412; 0.225 and 0.420.
  Which pearls (own count, work/h15_pass.py, bar F31_neighbour saved 07:22 before the pass was written; all 88 main and all 119 v31 big-layout games): the same turns split by whether an own dragon
  strictly longer than the acting one has its head within 9 tiles of every adjacent free pearl. main: with one within 9 tiles ours leave 0.225 before round 151 (7,315 turns) and 0.451 after (6,852); without, 0.241 (5,612) and 0.331 (4,637).
  v31: 0.221 (11,022) and 0.451 (10,344) with one near; 0.240 (7,938) and 0.338 (6,056) without. Their dragons after round 151: 0.241 and 0.240 (main), 0.215 and 0.225 (v31).
  So about four fifths of our extra leaving after round 151 is at pearls near a longer dragon of our own, and one fifth is not, in both codes.
  By length of the acting dragon, after round 151, near / not near, main then v31: length 2 0.47 / 0.29 and 0.46 / 0.28; length 3 0.49 / 0.38 and 0.51 / 0.36; length 4 0.37 / 0.33 and 0.43 / 0.39;
  length 5 or more 0.34 / 0.31 and 0.33 / 0.32 (before round 151: 0.11 / 0.19 and 0.08 / 0.19).
  What the phase buys (rows.jsonl, bar F31_leader_length saved 07:26 before the count; big layouts, games reaching r300): our longest dragon is the longer one at r300 in 47 games against 36 (main) and 60 against 54 (v31);
  medians 19 against 16 and 18 against 17. At r200 it is 42 against 43 and 62 against 51. At the end of full games 34 against 50 (main) and 53 against 58 (v31), medians 34 against 39 and 42 against 37.
  Dragons alive at r300 (medians): 52 against 62 and 50 against 62. So 150 rounds of leader phase give us a longest dragon about as long as theirs, with ten fewer dragons.
  What failed, both on bars written first:
  - Cost. Inside a layout the games with the deeper drop are not lost more often: split at the layout median of our ratio, the lower halves win 37 of 84 and the upper halves 35 of 88 (both codes). Pooled split: main 14 of 40 against 20 of 41, v31 22 of 55 against 26 of 56.
  - Place. The leaving is not confined to 9 tiles around our longest dragon: inside it rises by 32 points, outside by 13 to 15, and five turns in six are outside, so 9 tenths of the gap to their rate is outside the zone as I measured it.
  Verifier, 07:54 KST: every headline number recounts exactly from its own rebuild of 730 replays. The step is ours only, between raw rounds 150 and 151 on the big layouts and between 300 and 301 on the others, in a single round
  (our rate of leaving an adjacent pearl by raw round, big layouts: main r149 0.281, r150 0.278, r151 0.427, r152 0.427; v31 0.244, 0.233, 0.401, 0.381; other layouts main r300 0.250, r301 0.495), in both codes, both rating bands, both halves,
  against 27 of 29 and 39 of 39 opponents, and in games that never came near the dragon limit (never above 54 of ours: pearls 0.765 against 1.178 on main). Chance: 73 of 81 games is p 3e-14.
  What the dragon does instead: on big layouts it ate in 0.761 of such turns before and 0.599 after, and moved elsewhere in 0.209 before and 0.373 after (main); it does not split or die more.
  Not as I worded it, all accepted: (1) Schooltime 1 does not show the step in the adjacent-pearl rate (0.33 then 0.37) and our pearls rise there; only its splits fall. So five of the six big layouts.
  (2) The data put the line between 1152 and 1701 cells, not at 1200; Devil and Stripes have no games long enough to show round 301, Trophy and Prisoners Dilemma rest on under 50 turns.
  (3) My split figures at round 300 were on another game set than I wrote: by the written definition they are ours 0.641 against theirs 0.971 (main, 91 games) and 0.609 against 0.903 (v31, 115 games); the direction is the same.
  (4) The splits by nearness to a longer own dragon and by the 9-tile zone are partly a length effect and are not the trigger: far and outside turns rose too.
  Cost, verifier: nothing in wins on big layouts (lower halves 44 of 95, upper 38 of 95). Our share of all length on big layouts is 0.479 after round 150 and 0.385 after round 300 (main); 0.475 and 0.367 (v31).
  There is no build without the step, so the ladder has no control group. That needs local games.
  New games this hour (rows.jsonl; bar F31_new_games of 07:24): 4 main games on big layouts: our pearl ratio 0.671 (735 then 493), theirs 1.338 (668 then 894); ours the lower one in 4 of 4. The bar needs 10 games; in line so far.
  All four were lost, and in all four we were ahead in total length at r100 (Australia 92 against 78 and 98 against 77, Around UNSW 187 against 94 with 61 dragons against 34, Slithery Fight 152 against 118).
  Smaller layouts (bar F31_small_new_games): 4 new games, ours 0.725 (637 then 462), theirs 1.311 (103 then 135); all four won. Needs 15.
  Totals now: big layouts, main 85 games, ours 0.762 (12,138 then 9,254), theirs 1.143; ours lower in 77 of 85. Smaller layouts at round 301, main 89 games: 0.808 against 1.046. main wins on big layouts 35 of 92, elsewhere 131 of 203.
  What the leader is worth on big layouts (bar F32 of this hour, which FAILED and so speaks for the leader phase; see F32): in games that end with both queens dead at round 500, the side with the longer longest dragon at r300 wins
  29 of 34 non-tied games on main and 37 of 44 on v31. When we had the longer leader and less total length at r300 we won 15 of 20 (13 of them Around UNSW). At r150 the longer leader predicts nothing yet (main: ahead 6 won 8 lost, behind 7 won 13 lost).
  We are behind in leader length at r300 in 19 of these 36 main games and lose 18 of them. So a test of the constant must watch the leader at r300, not total length.
  Pass mark, tightened this hour: besides the four lines below, our longest dragon at r300 must not get shorter (now a median of 19 on main) and the share of big-layout games in which it is the longer one at r300 must not fall (now 47 of 83).
  New games, run 0900 (rows.jsonl; bar F31_new_games, after battle 1281566; 10 needed): 8 main games on big layouts now. Our pearl ratio 0.685 (1,300 then 891), theirs 1.304 (1,497 then 1,952); ours the lower one in 8 of 8.
  The four of this hour (Australia vs 1794, Islands and Around UNSW vs 2067, Slithery Fight vs 2105) were all lost. Our bot ids 18504 and 18570, both the main source. Smaller layouts (bar F31_small_new_games; 15 needed): 12 games, ours 0.793 (2,333 then 1,851), theirs 0.945.
  Totals now: big layouts, main 89 games, ours 0.760 (12,703 then 9,652), theirs 1.150; ours lower in 81 of 89. Smaller layouts at round 301, main 97 games: 0.809 against 1.036. main wins on big layouts 35 of 97, elsewhere 139 of 218.
  The longer leader at r300 (bar F32_new, 10 needed): 3 new both-queens-dead games on big layouts; it won 2 (Australia 9 against 22 and Islands 6 against 15, both lost by us; Around UNSW ours 26 against 18 and still lost, 26 against 29 at the end).
  New games, run 1000 (rows.jsonl; bar F31_new_games, after battle 1281566; 10 needed, now met): 15 main games on big layouts that reached r200 with 20 or more of ours alive at r150. Our pearl ratio 0.689 (2,431 then 1,675), theirs 1.172 (3,045 then 3,569); ours the lower one in 15 of 15.
  The lines were 0.95 for ours and a gap of 0.15: holds. The 7 games of this hour: 0.693 against 1.045. Our bot id is 18570 in all 20 games of this hour, the main source.
  Smaller layouts (bar F31_small_new_games; 15 needed, now met): 16 games, ours 0.770 (2,956 then 2,276), theirs 0.947 (2,482 then 2,351); ours lower in 13 of 16. The lines were ours under 0.90 and theirs at least 0.10 above: holds.
  Totals now: big layouts, main 96 games, ours 0.754 (13,834 then 10,436), theirs 1.141; ours lower in 88 of 96. Smaller layouts at round 301, main 101 games: 0.805 against 1.031. main wins on big layouts 40 of 105, elsewhere 148 of 230.
  This hour we won 5 of 8 on big layouts: Slithery Fight twice and Around UNSW on longest dragon with both queens dead (82 against 43, 51 against 6, 73 against 37) and Schooltime 2 twice; lost Islands twice (wiped out at r176 and r359) and Australia (30 against 52).
  The longer leader at r300 (bar F32_new, 10 needed): 7 both-queens-dead games on big layouts now; it won 5.
  A cost bar of this hour failed (F40, refuted, below). I claimed the phase costs games when it starts before our board is full (under 55 dragons at r150). Our count falls by a median of 6 from r150 to r300 with a full board too (main 69 games, v31 72) while theirs rises by 1 or 2,
  and games under 55 at r150 are nearly all games already far behind. So the fall after round 150 is general, and there is still no cost figure from the ladder.
  New games, run 1100 (rows.jsonl; bar F31_new_games_2, after battle 1293952; 10 needed): 5 main games on big layouts that reached r200 with 20 or more of ours alive at r150 (Australia three times, Slithery Fight twice).
  Our pearl ratio 0.699 (707 then 494), theirs 1.077 (1,187 then 1,278); ours the lower one in 5 of 5. Bot id 18570 in all 20 games of this hour. In line; 5 short of the count.
  Totals now: big layouts, main 101 games, ours 0.752 (14,541 then 10,930), theirs 1.137; ours lower in 93 of 101. Smaller layouts at round 301, main 106 games: 0.803 against 1.020.
  main wins on big layouts 42 of 110, elsewhere 156 of 245. By layout: Islands 0 of 15, Australia 4 of 24, Around UNSW 13 of 23, Slithery Fight 13 of 23, Schooltime 1 and 2 12 of 25.
  The longer leader at r300 (bar F32_new, 10 needed, now met): 11 both-queens-dead non-tied games on big layouts since battle 1285561; the longer leader at r300 won 9. The line was 6 or fewer: holds. All main games: 47 of 55.
  Australia is four of the 11: our longest dragon at r300 was 9, 7, 9 and 10 against 22, 19, 25 and 34, all lost (this hour 9 against 25 and 10 against 34; dragons alive at r150 52 against 59 and 41 against 60).
  Slithery Fight is four more: 23, 21, 24 and 37 against 28, 14, 15 and 18, all won. So the same leader phase gives the longer leader on one big layout and a far shorter one on another; the ladder cannot say why.
  New games, run 1200 (rows.jsonl; bar F31_new_games_2, after battle 1293952; 10 needed, now met): 11 main games on big layouts that reached r200 with 20 or more of ours alive at r150. Our pearl ratio 0.615 (1,861 then 1,144), theirs 1.075 (2,939 then 3,158); ours the lower one in 11 of 11.
  The lines were 0.95 for ours and a gap of 0.15: holds. The 6 games of this hour: 0.563 against 1.073. Bot id 18570 in all 20 games of this hour.
  Totals now: big layouts, main 107 games, ours 0.738 (15,695 then 11,580), theirs 1.131; ours lower in 99 of 107. Smaller layouts at round 301, main 109 games: 0.799 against 1.022. main wins on big layouts 46 of 118, elsewhere 160 of 257. Islands 0 of 16, Australia 4 of 24.
  For the leader phase, this hour: the first battle won against a 2100+ team (3-2 against 2195) holds two wins on longest dragon with far less total length: Slithery Fight 75 against 29 (total 165 against 319) and Schooltime 1 27 against 23 (44 against 295).
  Against it, this hour: three games lost on the queen rule with our longest dragon the longer one (Slithery Fight 86 against 28, Around UNSW 77 against 64, Maze 71 against 57). The leader was there; their queen was alive. See F42.
  The longer leader at r300 (bar F32_new_2, 10 needed): 2 both-queens-dead non-tied games on big layouts since battle 1298211; it won 2. All main games: 49 of 57.
  New games, run 1500 (rows.jsonl; bar F31_new_games_3, after battle 1302921; 10 needed, now met): 21 main games on big layouts that reached r200 with 20 or more of ours alive at r150. Our pearl ratio 0.719 (3,238 then 2,328), theirs 1.127 (4,409 then 4,967); ours the lower one in 17 of 21. The lines were 0.95 for ours and a gap of 0.15: holds. Bot id 18570 in all 60 new main games.
  Totals now: big layouts, main 128 games, ours 0.735 (18,933 then 13,908), theirs 1.130; ours lower in 116 of 128. Smaller layouts at round 301, main 125 games: 0.802 against 1.017. main wins on big layouts 55 of 143, elsewhere 177 of 292. Islands 0 of 21, Australia 6 of 30, Around UNSW 15 of 28, Slithery Fight 17 of 33.
  The longer leader at r300 (bar F32_new_2, 10 needed, now met): 14 both-queens-dead non-tied games on big layouts since battle 1298211; it won 12. All main games: 59 of 69.
  New games, run 1800 (bar F31_new_games_4, after battle 1316833; 10 needed): 9 main games on big layouts that reached r200 with 20 or more of ours alive at r150. Our pearl ratio 0.715 (1,481 then 1,059), theirs 1.036 (2,099 then 2,174); ours the lower one in 8 of 9. One short of the count; in line.
  All main: 137 games, 0.733 against 1.123, ours lower in 124. main wins 58 of 154 on big layouts, 201 of 331 elsewhere; Islands 0 of 23, Australia 7 of 33.
would be wrong if: (F31_pearls, 07:12, before the count) on main or v31 our ratio on big layouts is 0.95 or more, or theirs is less than 0.15 above ours; or on the other layouts ours is more than 0.15 below theirs too. Passed: 0.77 and 0.73 against 1.13 and 1.10; other layouts equal.
  (F31_splits, 07:09, before any split count) our split ratio (r150-174 over r125-149) on big layouts 0.85 or more on main or v31, or theirs less than 0.1 above ours. Passed: 0.68 and 0.67 for us against 0.98 and 0.92 for them (bins are r125-149 and r150-174, one round off the wording).
  (F31 a, 07:06) our rate of leaving an adjacent free pearl in r151-199 less than 4 points above r101-150 on big layouts. (F31 b) inside 9 tiles of our longest dragon less than 10 points above outside. (F31 c) with the in-zone chances left out, more than 75 percent of the gap remains.
  Results: (a) passed, +17 points on main and +18 on v31, theirs 0. (b) between the lines: 11 and 14 points (wrong under 10, claimed 20). (c) FAILED: 92 and 88 percent of the gap remains without the zone.
  (F31_neighbour, 07:22) the rate of leaving with no longer own dragon within 9 tiles is 0.35 or more in r151-199 (claimed under 0.30), or the rate with one near is less than 10 points above it. Between the lines on both codes, not wrong: main 0.331 and 12 points, v31 0.338 and 11 points.
  (F31_cap, 07:24) with fewer than 45 of our dragons alive at r150 our pearl ratio on big layouts is 0.90 or more. Passed: 0.76 on 46 games.
  (F31_leader_length, 07:26) our longest dragon is the longer one at r300 in 60 percent or more of non-tied big-layout games (claimed under half). Between the lines: 0.57 on main, 0.53 on v31.
  (F31_cost, 07:13) the lower half wins less than 15 points below the upper half (pooled), or less than 10 points within layouts. FAILED: 14 points on main, 6 on v31, none within layouts.
inferred: In main.cpp a layout with more than AGGRESSIVE_MAX_CELLS 1200 cells gets grow_round = LEADER_GROW_ROUND_BIG 150; smaller ones get LEADER_GROW_ROUND 300. After grow_round three rules switch on:
  a dragon longer than SPLIT_MIN_LENGTH 4 never splits again; the dragon that holds itself for the leader never splits; and refresh_leader_zone() sets a zone of LEADER_PEARL_RADIUS 9 tiles around the known leader's head
  in which every other dragon gets no EAT_BONUS and a ZONE_PEARL_PENALTY of 600 for stepping on a pearl. The measured step sits on that round in both classes of layout, in both codes, against every opponent and rating band,
  and their side shows nothing at those rounds. So I read it as this switch, not as something opponents do. v31's source is not on disk; its games behave the same.
  It gives a date and a place in the code to F11, F25 and F26 (we lose the middle game on large layouts; a level position at r100 never grows there; we leave pearls next to the head).
  Why the leaving is everywhere and not only near the true longest dragon: my guess is that many dragons hold a neighbour for the leader (a report older than SONAR_STALE 25 rounds is dropped, and hear_sighting() then takes any ally in view),
  so pearls within 9 tiles of that neighbour are off limits. The h15 count fits this for most of it (the rise is 23 points near a longer own dragon and 9 to 10 points elsewhere, main and v31), but it is still a reading of the code; it needs the bot.
  The rest (dragons of length 5 or more leave three times as often as before wherever they are) may be the split stop: a dragon that can no longer split has less use for a pearl. Also a guess.
  Whether it loses games is not shown. The leader phase is deliberate (a long dragon for the longest-dragon ending), and the depth of the drop does not go with the result inside a layout.
  But the phase does not show a return either: at r300 our longest dragon is the longer one in little more than half of the games, and at the end of full games on main in 34 of 84.
  What it costs in pearls is large: from round 151 on big layouts the opponent eats nearly twice what we eat (per game and 25 rounds: 99 against 54 on main, 104 against 57 on v31), and by r200 they have 57 to 59 dragons to our 48 to 49.
not checked: which of the three rules makes a dragon leave an adjacent pearl; results with the switch off (needs local games); the leader's final length with the switch off (F29: the longest-dragon endings on Australia and Islands are already lost 12 to 52).
  All six big layouts have 1699 or more open tiles and the largest small layout has 1152, so the data cannot place the line anywhere but where the code puts it.
  Added 08:12: read with F32, the leader phase is not a mistake in kind. Where it gives us the longer leader by r300 we win the both-queens-dead ending. The open question is only whether starting it at 150 rather than later gives a longer leader at r300 or a shorter one
  (fewer dragons to feed it: 52 against 62 alive at r300). The ladder cannot answer that; one local run of the constant can.
look at: data/online/ladder/1280133/M1280136.replay r125-200 (Islands vs 1978: 56 dragons against 49 at r150; our splits per 25 rounds 35, 29, then 8, 7, 5; our pearls 82, 76, then 31, 30, 12; 24 against 62 at r200; eliminated at r387);
  data/online/ladder/1279530/M1279533.replay r150-300 (Australia vs 1870: 59 against 46 at r150, 44 against 62 at r200, lost on longest dragon 13 against 39);
  data/online/ladder/1280772/M1280776.replay r150-300 (Islands vs 1873: 61 against 19 at r150, 42 against 62 at r300, lost on longest dragon 25 against 46).
smallest test: one constant. Arm A: LEADER_GROW_ROUND_BIG 150 to 300, so that big layouts get the timing of small ones. Arm B, to tell the zone from the split stop: keep 150 and set LEADER_PEARL_RADIUS to 0 (no zone).
  Local games on Islands, Australia, Slithery Fight and Around UNSW (or any layout above 1200 cells).
  One thing to check in the code before arm A: feeding can start at round 201 once we have 56 dragons (FEED_CAP_ROUND 200, FEED_CAP_UNITS 56), and is_leader() is false until grow_round,
  so with 300 the dragon being fed could still split between rounds 201 and 300. A value of 200 for LEADER_GROW_ROUND_BIG avoids that overlap and is a third arm worth having.
  Pass mark to write first: pearls eaten in r151-200 at least equal to r101-150 (now 0.77 times), dragons alive at r200 not below r150 (now 52 then 48), wins on those layouts do not fall,
  and in games that end with both queens dead our longest dragon is not shorter than now.

### F35 In level games a lone queen of ours dies about three times as fast as a lone queen of theirs; over all games the two sides lose a lone queen equally often
status: weakened (new-games bar fired: in 59 new lone queens ours survives 0.79 times as often as theirs, line 0.7; before that confirmed in the verifier wording of 08:40)      first seen: 7 Oct 08:08 KST run 20261007-0800   last tested: 7 Oct 18:20 KST (rows.jsonl, new games)
measured: Restated after the recount of 08:40 KST. All my numbers reproduce from the raw replays; what they mean changes. Level game = total length at r100 within 20 percent of each other; free layouts; every ending counted. Lone queen = a queen whose opposite number died in an earlier round.
  Verifier, level games: per 1,000 turns as the only queen ours dies 9.41 times (19 deaths in 2,020 turns) and theirs 3.05 (19 in 6,237) on main; v31 8.53 (30 in 3,517) against 3.25 (29 in 8,930).
  Alive at the end: 2 of 21 against 11 of 30 (main), 2 of 32 against 15 of 44 (v31); both codes 4 of 53 against 26 of 74. Two code slices, the same size of gap. Full level games only: 3 of 41 against 23 of 64 (p 0.001).
  My count on rows.jsonl with the games of this hour (765 games): main 3 of 22 against 11 of 32; v31 unchanged.
  What does NOT hold (verifier): with every game counted, lone queens survive equally often (main 38 of 102 against 45 of 130; v31 47 of 159 against 61 of 182). We end games by elimination about twice as often as they do (76 against 36 on main) and 30 of our 38 surviving lone queens are in those wins.
  Per lone turn over all free games main is 5.32 against 4.33 per 1,000 (1.23 times, interval 0.89 to 1.70: not shown; 0.96 against 1700-1899; all of it after r300). v31 1.92 (1.48 to 2.48: holds in every slice).
  Grouped by who leads at r100, main: we ahead by more than 20 percent 3.43 against 8.53; level 9.41 against 3.05; they ahead 6.49 against 2.43. So on main the lone queen of the leading side is the safer one in both directions, and the level games are where ours is worse.
  Within full games the gap is beyond chance (main 8 of 43 against 32 of 80, p 0.017; v31 8 of 67 against 36 of 107, p 0.0012) and no opponent, layout or evening carries it (any one opponent out: ratio 0.32 to 0.51; any one layout out 0.38 to 0.58). But full games are a chosen set.
  Totals now, main, full games on free layouts (155): both queens dead 89, only theirs 35, only ours 11, both alive 20. Lone queens alive at the end 11 of 48 against 35 of 87. New games since the bar F35_new_games (after battle 1285561): ours 3 of 5, theirs 3 of 7 (15 a side needed).
  Size: of all 141 main losses, 56 end with only their queen alive (42 on the queen rule, 14 eliminations), 42 with both queens dead on longest dragon, 24 by elimination with both dead.
  Why: F39 (new this hour). Over lone-queen turns a short enemy head is within 6 path steps of our queen 2.5 to 4 times as often as one of ours is of theirs, and she has fewer of her own within 5 tiles.
  First wording and its numbers, kept as counted in run 0800: rows.jsonl, free layouts (queen can leave spawn), games that reached round 500 (last_round 499): main 143 games (71 won), v31 191 (82 won). Lone queen = the queen whose opposite number died in an earlier round.
  How these full games end. main: both queens dead 83 (49 won), only theirs alive 32 (0 won), only ours 8 (8 won), both alive 20 (14 won). v31: both dead 132 (63 won), only theirs 36, only ours 8, both alive 15 (11 won).
  So we win the both-queens-dead ending of a full game more often than not on main (49 of 83) and lose the one-queen ending 8 to 32. The 38 only-ours endings of the earlier ledger were 30 eliminations, where their queen is dead by definition.
  Lone queens alive at the end, ours against theirs: main 8 of 43 (0.19) against 32 of 80 (0.40). v31 8 of 67 (0.12) against 36 of 107 (0.34).
  Two things are in that: we hold the lone queen less often (43 against 80; 67 against 107), and she then survives half as often.
  Slices. main 1700-1899: 4 of 18 against 10 of 31 (0.22 against 0.32). main 1900-2099: 4 of 23 against 15 of 41 (0.17 against 0.37). main 2100+: 0 of 2 against 7 of 8. v31 by band: 7 of 32 against 16 of 47; 1 of 19 against 14 of 43; 0 of 9 against 6 of 16.
  main earlier half 4 of 15 against 13 of 25; later half 4 of 28 against 19 of 55. Big layouts (above 1200 cells), both codes: 5 of 44 against 24 of 69. Other layouts: 11 of 66 against 44 of 118.
  By layout on main, ours then theirs: Around UNSW 3 of 9 and 6 of 12; Australia 0 of 3 and 3 of 15; Islands 0 of 4 and 1 of 6; Maze 0 of 9 and 5 of 13; weakhold 0 of 4 and 3 of 10; Tower Defense 1 of 4 and 5 of 8; Portals 0 of 2 and 4 of 8;
  Default 2 of 4 and 0 of 1; Trauma 2 of 2 and 3 of 3. Their surviving lone queens on main come from 19 of the 28 opponents that had one.
  Over time: alive 100 rounds after becoming the only queen (games with 100 rounds left): ours 22 of 40, theirs 59 of 79 (main); 39 of 65 and 74 of 106 (v31). 200 rounds after: 11 of 38 against 41 of 75; 17 of 63 against 54 of 102.
  How the lone queens die in these games: ours 35 deaths on main, 20 rammed, 12 wall or own body; theirs 48 deaths, 26 rammed, 11 wall or own body. v31: ours 59 deaths, 46 rammed; theirs 71 deaths, 21 rammed, 23 wall or own body, 13 another body.
  Check against game length (own count, work/h10-shard files, 665 games up to battle 1276407, ALL free games, eliminations included; deaths per 1,000 turns spent as the only queen):
  main ours 5.51 (54 deaths in 9,809 turns), theirs 4.13 (73 in 17,680): 1.33 times. v31 ours 7.87 (112 in 14,233), theirs 4.11 (121 in 29,474): 1.92 times.
  Full games only: 5.88 against 2.68 (main), 6.43 against 2.97 (v31). Big layouts: 5.38 against 3.03 and 8.00 against 2.60. Other layouts: 5.55 against 4.68 and 7.82 against 4.75.
  So with game length taken out the gap is still there in both codes, smaller on main (1.33) than the full-game figure suggests, and largest on big layouts. A lone queen of theirs lasts 156 turns on average, ours 121 (main).
  When the gap opens (rows.jsonl, full free games): our queen is dead by r100 in 33 of 143 main games and theirs in 28; by r200 ours in 79 and theirs in 49. v31: 66 against 46 by r100, 121 against 85 by r200.
  Where their short dragons are (same h10 files, share of queen turns that start with an enemy head of length 4 or less within its full reach; before the bar F35_hunt, so a lead only):
  after round 200 ours 0.034 and theirs 0.0065 on main big layouts, 0.0079 against 0.0013 on other layouts; v31 0.028 against 0.0065 and 0.0059 against 0.0041. Before round 200 it is level on big layouts (0.015 against 0.016) and ours is the lower one elsewhere.
  What kills ours first (bar F35_first_death, saved 08:16, FAILED): in r101-200 of these full games our queen dies 46 times and theirs 21 on main. Rams account for 26 against 17; wall or own body for 17 against 1. v31: 55 against 39; rams 27 against 22; wall or own body 23 against 9.
  So the reason our queen is the first to go in full games is mostly that she runs into a wall or herself between rounds 101 and 200 (F37), not that she is rammed more.
  What it is not (bar F36 of this hour, FAILED): a grown queen. Their queens alive at r200 with length 5 or more are alive at the end in 12 of 25 (main) and 18 of 36 (v31); with length 3 or less in 32 of 58 and 29 of 65.
  New games, run 1000 (bar F35_new_games, after battle 1285561; 15 a side needed): lone queens in full main games on free layouts: ours alive at the end 4 of 7, theirs 4 of 10. Level games: 2 of 3 against 1 of 5. Too few; so far the new games do not show the gap.
  Totals main: full games 12 of 50 against 36 of 90; level games (all endings) 4 of 24 against 12 of 35.
  Size now: of 147 main losses, 59 end with only their queen alive (43 on the queen rule, 16 eliminations), 43 with both queens dead on longest dragon, 26 by elimination with both dead.
  New games, run 1100 (bar F35_new_games, after battle 1285561; 15 a side needed): lone queens in full main games on free layouts: ours alive at the end 5 of 10, theirs 6 of 16. Level games (all endings): 2 of 3 against 2 of 9.
  Ours is still short of 15. So far the new full games show no gap; the level games are too few to read. Totals main: full games 13 of 53 against 38 of 96; level games 4 of 24 against 13 of 39.
  Size now: of 157 main losses, 64 end with only their queen alive (45 on the queen rule, 19 eliminations), 46 with both queens dead on longest dragon, 28 by elimination with both dead.
  New games, run 1200 (bar F35_new_games, after battle 1285561; 15 a side needed): lone queens in full main games on free layouts: ours alive at the end 5 of 10, theirs 9 of 22. Level games (all endings): 2 of 3 against 4 of 12. Ours still short of 15; no gap in the new full games.
  Totals main: full games 13 of 53 against 41 of 102; level games 4 of 24 against 15 of 42.
  Size now: of 169 main losses, 72 end with only their queen alive (49 on the queen rule, 23 eliminations), 47 with both queens dead on longest dragon, 31 by elimination with both dead. In 20 of the 49 our longest dragon was the longer one (F42, new).
  New games, run 1500 (bar F35_new_games, after battle 1285561; 15 a side needed, now met): lone queens in full main games on free layouts: ours alive at the end 7 of 22 (0.32), theirs 15 of 37 (0.41). Ours is 0.79 of theirs; the line was 0.7. The bar FIRED: weakened.
  Level games (all endings) since that battle: 3 of 7 against 7 of 20, no gap either. Totals main: full games 15 of 65 against 47 of 117 (0.23 against 0.40); level games 5 of 28 against 18 of 50.
  So the survival gap of a lone queen was in the games up to battle 1285561 and is not in the 59 lone queens since. The per-turn death rates of the verifier wording were not recounted on the new games. What stays is the count of endings: we are the side without a queen far more often (F42: 47 full-game losses with only theirs alive against 15 wins with only ours).
  Size now: of 203 main losses, 56 on the queen rule with only their queen alive, 60 on longest dragon with both queens dead, 66 eliminations (18 by round 125), 21 with both queens alive.
  New games, run 1800 (bar F35_restore, after battle 1316833; 15 lone queens a side needed): full main games on free layouts: ours alive at the end 1 of 14, theirs 1 of 11. Not at the count; no gap either way. Stays weakened.
would be wrong if: (08:08, before the count; seen before it: the one-queen ending counts of full games with the sealed-queen layouts included, 10 against 38 and 13 against 46) our lone-queen survival rate is 0.7 or more of theirs on main or on v31;
  or in main band 1700-1899 or 1900-2099 (15 or more lone queens a side); or, both codes pooled, on big layouts or on the other layouts. Passed everywhere: 0.47 and 0.35; bands 0.69 (on the line) and 0.48; layout classes 0.33 and 0.45.
inferred: F13 said a lone queen dies two times in three whichever side she is on. That was per game. Many of our lone queens "survive" because we wipe the opponent out by round 150 and the game stops; in games that last, ours is the one that goes.
  The qualifier maps are unseen; on any layout where nobody is wiped out (every big layout here: 0 of 92 main games on big layouts ended by our elimination of them) this is the ending we get.
  How many games (main, 143 full games on free layouts), in three parts. (1) Our queen dies first in 80 games and theirs in 43. (2) Of those 80, their lone queen lives in 32, all lost; where we do kill her (48 games) the longest dragon decides and we win 24.
  If our hunters killed their lone queen as often as theirs kill ours (0.81 instead of 0.60) about 17 more games would go to the longest-dragon rule, worth about 8 wins at that rate. (3) Of our 43 lone queens 35 die, but we still win 25 of those 35 games on longest dragon,
  so keeping her alive as often as they do (0.40 instead of 0.19) is worth about 3 wins. The larger levers are therefore (1) and (2), not (3). 32 losses is a quarter of all 129 main losses and the upper limit of (1) and (2) together.
  Why: not shown. Two readings, both guesses. (a) After their queen is dead our dragons have no reason to stay near ours (QUEEN_DEFEND_RADIUS 0, QUEEN_GUARD_CELLS 0, and from round 201 or 301 the small ones go to feed the leader), while their short dragons keep coming for her:
  after round 200 a short enemy head is within reach of our queen about five times as often as one of ours is within reach of theirs (main). (b) When the roles are swapped our revenge hunt (qh_, dragons of length QH_MAX_LEN 4 or less, from round QH_REVENGE_ROUND 100) reaches their queen less often than their hunters reach ours.
not checked: which of the two; how many friendly heads stand near each lone queen over time (run 0400 measured it only at the moment of a ram: both sides alone); whether their lone queen hides (distance from the nearest of our heads); opponents differ and 19 of 28 is not all of them.
  Full games are a chosen set (our 76 elimination wins and their 36 are out); the per-turn check over all games is the fair figure and it is smaller on main (1.33). Main is one day of games.
look at: data/online/ladder/1255595/M1255597.replay r79-294 (Around UNSW vs 2020: their queen died r79, our lone queen, length 2, rammed at r294, lost on longest dragon 23 against 61);
  data/online/ladder/1278844/M1278847.replay r56-185 (Default vs 1814: their queen died r56, ours rammed at r185 at length 2, lost on longest dragon 17 against 21);
  data/online/ladder/1276407/M1276407.replay r155-499 (Around UNSW vs 2111, the mirror: our queen rammed at r155, theirs lives 345 more rounds with 43 of our dragons on the board and ends 18 long).
smallest test: one constant that is already in main.cpp and switched off: QUEEN_GUARD_CELLS (0 now). Set to 1200 it turns the queen-guard mode on for layouts above 1200 cells: queen_guard() then gives QG_GUARD_RADIUS 5, QG_THREAT_MULT 6.0 (now 4.0)
  and QG_SPLIT_CLEAR 6 (she stops splitting with an enemy within 6). I have read where these are used, not what the guard radius makes other dragons do; check that first.
  Second arm, as in F13: the same mode only once qh_foe_dead() is true (we hold the only queen). Local games on layouts where nobody gets wiped out (Around UNSW, Australia, Maze, weakhold).
  Before either arm, count first (next hour, bar F35_hunt in state.json): what stands near each lone queen over time. By the arithmetic above the bigger lever is their lone queen outliving our revenge hunt (32 of 80);
  if our hunters simply do not reach her, the test is in the qh_ constants (QH_MAX_LEN 4, QH_REVENGE_ROUND 100, QH_FRESH 20), not in the guard.
  Pass mark to write first: of games that reach round 500 with their queen dead first, ours is alive at the end in at least 0.35 (now 0.19), our queen is dead by r200 in under 45 percent of full games (now 55), and wins in both-queens-dead endings do not fall.
  Updated 09:12: both arms now have a count behind them (F39): the hunt (our short dragons are not near their lone queen) and the guard (ours has fewer friends near). Read the queen-guard code before using it as the guard arm: guard_radius moves the QUEEN away from enemy heads; it does not bring other dragons to her.
  A fair test set is level games (within 20 percent at r100), not full games.

### F39 With one queen left we have as many short dragons as they do, but theirs are near our queen two to three times as often as ours are near theirs; they keep her in sight a little more and answer a sighting with twice as many
status: confirmed in the narrower wording of the verifier (09:45 and 10:40). The swarm part of run 1100 is weakened (verifier 11:39: holds in part; the opponent kinds follow the layouts, 1.2 to 1.4 with the layout held)      first seen: 7 Oct 09:06 KST run 20261007-0900   last tested: 7 Oct 18:20 KST (not re-counted; a caution added)
measured: own count, work/h18_pass.py (all 725 main and v31 games, 0 errors). At the start of every turn of a queen whose opposite number is dead: is an enemy head of length 4 or less within 6 path steps of her head (kelp and portals respected, dragons ignored);
  how many heads of her own team (not hers) are within 5 tiles (wrapped Manhattan).
  Full games on free layouts. Short enemy head near: 0.256 of our lone queen turns (7,549) against 0.102 of theirs (18,226) on main, 2.5 times. v31: 0.241 (9,172) against 0.055 (23,941), 4.4 times.
  Own heads within 5 tiles, mean: main 1.72 against 2.27 (0.76 of theirs); v31 1.49 against 2.56 (0.58). Turns with none of her own within 5: 0.31 against 0.24; 0.32 against 0.21.
  All endings: main 0.260 (13,644 turns) against 0.140 (21,033), 1.85 times, own heads 1.71 against 2.14. v31 0.278 against 0.080, 3.5 times, own heads 1.56 against 2.50.
  Level games (bar F35_level; within 20 percent at r100, all endings): both codes 0.268 of 5,810 against 0.090 of 15,780, 3.0 times. main 0.318 against 0.117; v31 0.235 against 0.070. Own heads 1.69 against 2.70.
  Slices, full games, short-head share ours against theirs: main opponents 1700-1899 0.186 against 0.135 (1.4 times), 1900-2099 0.294 against 0.082 (3.6), 2100+ 0.255 against 0.100 (326 turns of ours only). v31 7.2, 4.1 and 1.6 times.
  Big layouts (above 1200 cells) 0.38 against 0.19 (main) and 0.40 against 0.10 (v31); other layouts 0.18 against 0.05 and 0.15 against 0.03.
  By 50-round bins since the other queen died (full games): main 1.9, 2.9, 2.4, 2.8, 2.2, 2.6 times; v31 2.7, 3.3, 3.2, 9.0, 8.7, 10.1. The gap is there in the first 50 rounds; on v31 it grows.
  Base rate with both queens alive (all free games), short enemy head within 6 steps of our queen against theirs: main r0-100 0.159 against 0.130, r101-200 0.118 against 0.082, r201-300 0.060 against 0.017, r301+ 0.113 against 0.023. v31 0.137 against 0.136, 0.222 against 0.166, 0.155 against 0.125, 0.084 against 0.062.
  Set side by side: when THEIR queen is the last one, a short head of ours is near her in 0.10 (main) and 0.055 (v31) of her turns, no more than with both queens alive in r101-200 (0.082 and 0.166). When OURS is the last one, a short head of theirs is near her in 0.26 and 0.24, twice the both-alive level on main (0.118) and the same on v31 (0.222).
  Verifier, 09:45 KST: holds in part. The counts are right to the last turn. The gap is not a matter of how many short dragons are alive (27.1 against 27.9 on main, 27.4 against 26.4 on v31, full games).
  The direction holds on both codes in full and level games, against every larger opponent and on each evening. The size does not: Portals #1 holds 22 percent of their full-game lone turns and the flag cannot fire there.
  Without Portals: full games 2.1 times on main and 3.3 on v31; all endings 1.6 and 2.7; per game 1.35 and 2.4. On the small boards there is no gap. main against 1700-1899 is not beyond chance, and main games that ended early go the other way.
  On main the same gap is there with both queens alive from r201 (3.6 and 5.0 times), so on main it is a late-game gap, not only a lone-queen gap; on v31 it is a lone-queen gap (1.0 to 1.4 with both alive).
  Fewer own heads within 5 holds on v31 and is thin on main (the median game is the same). All accepted; the heading is reworded.
  Supply and distance (own count, work/h20_pass.py and h20_count.py, 745 games, 0 errors; bar F39_supply saved 09:15). At every lone-queen turn: the other side's dragons of length 4 or less alive, and how many of them are within 12 path steps of her head (kelp and portals respected). Free layouts, all endings.
  Alive: at the turns of THEIR lone queen we have 25.9 short dragons (main, 21,707 turns); at the turns of OUR lone queen they have 20.6 (14,371 turns). v31: 23.3 against 22.2. Ours over theirs 1.26 and 1.05; full games 1.04 and 0.96; from grow_round 1.01 and 0.79.
  Within 12 path steps of the lone queen: 0.029 of ours against 0.082 of theirs (main), 0.022 against 0.079 (v31). Ours is 0.36 and 0.28 of theirs. In dragons a turn: 0.75 against 1.68; 0.51 against 1.75. At least one within 12: 0.30 against 0.50 of turns; 0.23 against 0.53.
  Slices, share within 12, ours over theirs, main then v31: without Portals 0.39 and 0.33; full games 0.30 and 0.27; before grow_round 0.43 and 0.29; from grow_round 0.30 and 0.27; big layouts 0.37 and 0.37; small layouts without Portals 0.43 and 0.29.
  Sightings (own count, work/h21_pass.py and h21_count.py, 745 games, 0 errors; bar F39_sight saved 10:11 before the pass existed). Seen = at the start of her turn a head of the other side is within 3 columns and 3 rows of any tile of her body (the 7 by 7 view).
  Fresh = seen at one of her turn starts in the last 20 rounds (the bot's QH_FRESH). Lone-queen turns from raw round 100, free layouts without Portals.
  Their lone queen is fresh to us in 0.60 of her turns (main, 16,432 turns in 108 games) and 0.49 (v31, 20,697 in 122). Ours is fresh to them in 0.70 (11,660 in 95) and 0.65 (10,480 in 115). Never seen since she became the only queen: theirs 0.24 and 0.25 of turns; ours 0.11 and 0.16.
  What a sighting brings. Short dragons within 12 path steps at fresh turns: ours 1.15 a turn near their queen, theirs 2.30 near ours (main); 0.90 against 2.38 (v31). At stale turns: 0.18 against 0.29; 0.21 against 0.53. At least one within 12 at fresh turns: 0.45 against 0.61; 0.40 against 0.66.
  So our hunt does answer a sighting (six times the stale level on main), with half as many dragons as theirs. With their share of fresh turns and our answer, we would have 0.86 short dragons a turn near her instead of 0.76; they have 1.71 near ours. About a tenth of the gap is sight, the rest is the answer (main).
  Big layouts differ: their lone queen is fresh in 0.50 (main, 6,676 turns) and 0.33 (v31, 8,155) of her turns and never seen in 0.35 and 0.26; ours is fresh to them in 0.78 and 0.72. Small layouts: 0.66 against 0.68 (main) and 0.59 against 0.62 (v31), no gap in sight;
  short dragons within 12 at fresh turns there 0.80 against 1.71 and 0.67 against 1.76. So on small layouts it is all the answer; on big layouts sight is part of it.
  Slices of the fresh share on main: opponents 1700-1899 0.59 against 0.67; 1900-2099 0.63 against 0.74; 2100+ 0.46 against 0.64 (10 and 5 games); earlier half 0.57 against 0.70; later half 0.61 against 0.71.
  Seen after the count, not under a bar (a lead for question 2): short dragons within 12 at fresh turns by opponent band, ours against theirs: 1700-1899 1.36 against 1.44; 1900-2099 0.97 against 2.89; 2100+ 1.45 against 1.61 (5 games of ours). Halves: 1.42 against 3.25; 1.05 against 1.83.
  Bar F39_band (saved 10:18, then counted on v31, which I had not seen by band): FAILED. v31: opponents rated 1900 or more bring 2.20 short dragons within 12 at the fresh turns of our lone queen (1,923 fresh turns); opponents rated 1700-1899 bring 2.32 (4,282). The line was 1.2 times; it is 0.95. So it is not rating.
  By opponent (150 fresh turns or more) there are two kinds. Bring 3.6 to 5.5: three teams on main (rated 1934 to 2140) and four on v31 (rated 1686 to 1973). Bring under 1.5: eleven of 16 on main and five of 13 on v31, among them teams rated 2021, 2167 and 2382.
  One team brings 4.7 on v31 and 0.95 on main, so even the kind is not fixed. The 1900-2099 figure on main is an opponent mix (two teams hold 1,692 of its 4,869 fresh turns at 4.4 and 5.5), not a finding about rating.
  Verifier, 10:40 KST (on the supply, distance and sighting counts of run 1000): holds in part. All counts recount exactly on 785 games and an exact sighting test gives the same fresh shares. The direction holds on both codes by game (label shuffle 0 of 5,000).
  What does not hold is the size as a general statement. With the layout mix held equal our short dragons within 12 steps a turn are 0.57 to 0.87 of theirs on main and 0.47 to 0.66 on v31, not a third:
  their lone-queen turns sit on Around UNSW, Maze, Tower Defense and weakhold, ours on the small boards. On main the gap is absent in games that end by elimination (1.03) and, at fresh turns, against 1700-1899 opponents (0.95; against 1900 and above 0.37,
  because the number of THEIR short dragons near our queen rises); three games carry a quarter of it (0.64 without them). On main the lone queens die equally fast on both sides (4.7 against 5.0 per 1,000 lone turns, no Portals),
  so time near her is not hunting success; on v31 ours died twice as fast (7.9 against 4.3). With a short head of ours within 12 steps at the turn start their lone queen dies 11.7 times per 1,000 turns; ours with one of theirs near 7.8.
  Fresh in about 6 turns in 10 holds for main (0.51 to 0.68) and is 0.50 on big layouts. All accepted.
  Do the hunters kill (bar F39_swarm, saved 10:21 before the count; own count, work/h22_pass.py, all 765 main and v31 games, 0 errors; its sight numbers equal work/h21 on the 745 older games).
  Opponent-and-code pairs with 150 or more fresh turns of our lone queen; free layouts without Portals; her lone turns from raw round 100. Pairs that bring 3.0 or more short dragons within 12 steps at her fresh turns
  (8 pairs: 4 on main rated 1665 to 2072, 4 on v31 rated 1753 to 1962): she dies 30 times in 4,843 lone turns, 6.19 per 1,000. Pairs that bring under 1.5 (17 pairs): 23 deaths in 7,033 turns, 3.27 per 1,000. That is 1.89 times.
  The 6 pairs in between: 4.76. By code: main 4.51 against 2.77 (13 and 15 deaths), v31 8.66 against 4.93 (17 and 8). The largest single opponent holds 6 of the 30 deaths; without it 5.87. Chance: 30 of 53 deaths on 41 percent of the turns, about 1 in 50.
  Beside it, not a bar: we win 67 of 110 games against the pairs that bring 3.0 or more, 70 of 115 against the middle and 54 of 115 against those that bring under 1.5 (among them teams rated 2021, 2167 and 2382).
  So a swarm does kill a lone queen faster, and the teams that swarm do not beat us more.
  New games (bar F39_new_games, after battle 1289717; 20 main games on free layouts and 1,000 lone-queen turns a side needed, now met; own count, work/h22_pass.py with the 6-step flag of work/h18):
  34 games; a short enemy head within 6 path steps in 0.270 of our lone-queen turns (531 of 1,965) and 0.126 of theirs (253 of 2,012): 2.1 times. The line was 1.3: holds. Full games only: 0.243 against 0.068.
  Verifier, 11:39 KST (on the swarm count of run 1100): holds in part. The counts recount exactly (two small readings: I count turn starts in the round their queen died; 2 of the 34 new games are on Portals, without them 0.270 against 0.169).
  The 1.9 times is right as a description of the 25 pairs and beyond chance pooled (199 of 10,000 shuffles), on neither code alone. It is NOT shown to be about the opponent: the kind of a pair follows the layouts its few lone spells fell on
  (rank correlation 0.82 with what the layouts alone give; B pairs have a median of 2 lone games); with the layout held the ratio is 1.40, with layout and code 1.19; with the kind taken from other games of the same pair 1.17 (0.73 to 1.75).
  In the 39 games with 3.0 or more brought she dies in 39 of 39, so the rate is partly there by construction. What stands: the extra deaths are at the hands of the other side (4.96 against 2.13 per 1,000) and not only in the last 20 rounds before her death.
  Accepted. "Teams that swarm" is dropped as a kind of opponent; what is left is a game-level link (many short heads near her, she dies), which is close to saying the same thing twice.
  New games, run 1200: not re-counted (15 new games on free layouts, 20 needed for bar F39_new_games_2).
  New games, run 1500 (bar F39_new_games_2, after battle 1298211; 20 main games on free layouts and 1,000 lone-queen turns a side needed, now met; own count, work/h25_pass.py, 199 games, 0 errors; it gives 123 of 275 against 147 of 1,927 on the 15 games up to battle 1302921):
  64 games; a short enemy head within 6 path steps in 0.207 of our lone-queen turns (586 of 2,834) and 0.138 of theirs (846 of 6,149): 1.5 times. The line was 1.3: holds, and smaller than before (2.1 and 2.5 times).
  The other direction counted in the games that matter (F42, this hour): where their queen is the only one alive at round 500, a head of ours of ANY length is within 6 path steps of her in 0.08 of her turns (main, 47 games) and 0.04 (v31, 36 games); where ours is the survivor theirs are near her in 0.20 and 0.21.
  Run 1800: not re-counted on new games (needs a rerun of work/h25_pass.py; bar F39_new_games_3 carried). A caution on the sight shares above: they count her as seen when a head is within 3 columns and rows of ANY tile of her body.
  The bot records a sighting only when her HEAD is in view (main.cpp lines 1477 to 1486). By that rule the shares are lower and the mirror gap is the same way: see F42, run 1800 (her head in view in 0.13 of her lone turns for us, 0.24 for them).
would be wrong if: (F35_hunt, saved 08:16, before the pass existed; seen before it: the exposure shares after round 200 from work/h10 and that rammed lone queens of both sides have fewer than 2 friends within 5 tiles)
  (a) our short-head share under 1.2 times theirs on main or v31 (claimed 1.5). Passed: 2.5 and 4.4. (b) our mean own heads 0.9 or more of theirs on main or v31 (claimed under 0.8). Passed: 0.76 and 0.58.
  (F35_level, saved 09:05 before the count) the level-game ratio under 1.2 with both codes pooled. Passed: 3.0. The slice nearest the line: main against 1700-1899, 1.4 times.
  (F39_supply, saved 09:15) first number: our short dragons alive at their lone-queen turns are 0.9 or more of theirs at ours (I had claimed under 0.7). FAILED, as the verifier's recount had shown before my own count: 1.26 and 1.05. We have the hunters.
  Second number, counted blind: the share of them within 12 path steps, ours 0.9 or more of theirs (claimed under 0.7). Passed: 0.36 on main, 0.28 on v31, and in every slice listed.
  (F39_sight, saved 10:11) their lone queen is fresh to us in under 30 percent of her turns on main or v31 (claimed at least 50). Not wrong: 0.60 on main (claim met), 0.49 on v31 (between the lines).
  (F39_swarm, saved 10:21) her death rate against the 3.0-plus pairs under 1.2 times that against the under-1.5 pairs, or one opponent with more than half of the deaths and under 1.2 without it. Passed: 1.89; 6 of 30; 1.80 without it.
  (F39_new_games) the 6-step share near our lone queen under 1.3 times the share near theirs on 20 new main games. Passed: 2.1 times on 34 games.
inferred: Both readings of F35 hold at once. Their short dragons close on our last queen. Ours do not close on theirs: her surroundings look as they did before our queen died, or emptier. And our last queen has fewer of her own within 5 tiles.
  In main.cpp a revenge hunter must be 4 long or less (QH_MAX_LEN), not a leader, hold a sighting no older than QH_FRESH 20 rounds, and pass qh_reach(). From grow_round (150 on big layouts, 300 elsewhere), and from FEED_CAP_ROUND 200 with 56 dragons, the short dragons are the ones sent to feed the leader.
  On main with both queens alive the gap opens after round 200 (0.060 against 0.017, then 0.113 against 0.023). My guess: feeding takes the short dragons away from both jobs, hunting their queen and standing between ours and their hunters. A guess; nothing here separates the hunt rule from the feeding.
  Updated 10:20: the guess about feeding is wrong. After grow_round we still have 27 short dragons alive at their lone-queen turns (main). They are far from her: one in 35 is within 12 steps; of theirs, one in 12 is within 12 steps of ours.
  Updated 11:12: the swarm bar says hunters near a lone queen go with her dying faster, on both codes, so the hunt is a real lever on HER death. Two limits from this hour: with the layouts held equal we are at 0.6 to 0.9 of theirs, not a third (verifier),
  and the teams that swarm do not beat us more. Their lone queen already dies faster with one of ours near (11.7 per 1,000) than ours with one of theirs near (7.8). So the test is still one constant and cheap, but it is no longer the second-largest item.
not checked: whether the short heads near her are hunters or just many (after the leader phase starts we have fewer dragons: F31); dragons standing in the way are ignored; near is 6 steps while a rammer usually starts from 3 (F24); not split by opponent; main against 1700-1899 is weak.
  It is a mechanism for F35, not a count of games: the all-games version of F35 is level.
look at: data/online/ladder/1289717/M1289720.replay r60-499 (Portals vs 2105: their queen alone for 440 rounds; no head of ours within 6 path steps of her at any of her turns; 4 to 6 of her own within 5 tiles);
  data/online/ladder/1276407/M1276407.replay r155-499 (Around UNSW vs 2111: our queen rammed at r155; theirs lives 345 more rounds with 43 of our dragons on the board);
  data/online/ladder/1255595/M1255597.replay r79-294 (Around UNSW vs 2020: their queen died r79; our lone queen, length 2, rammed at r294).
smallest test: no change yet, count first (one more pass): at each turn of their lone queen, how many of OUR dragons of length 4 or less are alive and how many are within 12 path steps of her, before and after grow_round.
  If we have short dragons and they are far, the hunt rule is the place: QH_FRESH 20 to 60 is one constant (a sighting stays usable longer).
  If we have few short dragons after grow_round, the feeding is the place: a default-off switch (say QH_HOLD_FEED) that keeps feeding_phase() off while qh_queen_dead() is true and their queen is not known dead, because in that position only the queen rule can still be lost.
  Test set: level games (within 20 percent at r100). Pass mark as in F35.
  Updated 10:20: counted. It points at the hunt rule, not at the feeding and only in part at sightings. One of ours has seen their lone queen within 20 rounds in six of her turns in ten, and then 1.1 short dragons of ours are within 12 steps (theirs 2.3; teams rated 1900-2099 2.9).
  In main.cpp (qh_watch) a dragon hunts when it is 4 long or less (QH_MAX_LEN), not the leader, holds a report no older than QH_FRESH 20 rounds that is newer than its last miss (qh_miss_round), and qh_reach() finds a walk; qh_reach() has no distance limit.
  A short dragon makes one free step a turn, so one that hears the report from more than 20 steps away drops the hunt before it arrives unless a newer report reaches it. That is a reading of the code, not a count.
  Smallest test, two arms, one constant each: QH_FRESH 20 to 60 (the report outlives the walk); QH_MAX_LEN 4 to 6 (more dragons qualify). Not a feeding switch: the feeding does not take the short dragons away.
  Check in the bot before running either: how far a report travels between our dragons. If most short dragons never hear it, neither constant helps and the relay is the place.
  Test set: level games on layouts where nobody is wiped out. Pass mark to write first: short dragons within 12 steps of their lone queen at fresh turns at least 2 a turn (now 1.15), their lone queen alive at the end in under 0.30 of full games (now 36 of 90 on main),
  our pearls after round 300 do not fall by more than a tenth.

### F42 Two in five of our queen-rule losses are games we had won on the next rule: our longest dragon is the longer one and only their queen being alive decides it
status: confirmed (verifier 12:24: holds). Hunt count: verifier 15:26 holds in part (without Portals no head of ours is within 6 steps in 85 of her turns in 100; flagged games no different from the rest). Sight counts of run 1800: bar F42_sight FAILED by its letter but measured her body, not her head; bar F42_sight_head is between its lines on main and passed on v31; the split by layout size is to-verify      first seen: 7 Oct 12:12 KST run 20261007-1200   last tested: 7 Oct 18:20 KST (own counts work/h26_pass.py and work/h27_pass.py; rows.jsonl new games)
measured: rows.jsonl. Games that reached round 500, lost on the queen rule with only their queen alive, on layouts where the queen can leave spawn. Flag = our longest dragon at the end strictly longer than their longest.
  With their queen dead these games go to the longest-dragon rule and are wins by definition.
  main: 15 of 41 (0.37). v31: 13 of 36 (0.36). main earlier half 6 of 13, later half 9 of 28; against 1700-1899 6 of 12, 1900-2099 7 of 21, 2100+ 2 of 8.
  Layouts of the 15: Portals 4, Maze 3, Tower Defense 2, Around UNSW 2, Trauma, Prisoners Dilemma 2, weakhold, Australia 1 each (v31: Around UNSW 4, Portals 4, Maze 2, three others). 12 opponents.
  Slithery Fight apart (the queen starts coiled there; kept out of queen statistics by the schema): 8 more such losses on main, 5 with our longer longest dragon; v31 10 and 5.
  So on main 20 of all 49 queen-rule losses with only their queen alive, 12 percent of all 169 main losses. In 8 of the 15 we also had more total length.
  The size of the lead in the 15 (ours against theirs): 83-28, 77-64, 71-57, 66-13, 48-43, 43-13, 36-34, 33-14, 32-9, 29-18, 28-25, 27-9, 21-18, 19-11, 16-15.
  Our queen in the 15 died at rounds 10, 44, 60, 78, 82, 90, 97, 137, 172, 187, 210, 222, 257, 381, 469: on a wall 5, rammed 5, on another dragon's body 3, on her own body 2; she was 2 or 3 long in 14.
  So in most of them their queen was the only queen for 300 rounds or more, with our dragons the longer ones.
  Second line, FAILED: I claimed their surviving queen is short (4 or less) in 60 percent of the flagged games. She is in 2 of 15 (main) and 3 of 13 (v31). Her lengths on main: 3, 4, 7, 9, 9, 11, 11, 14, 15, 18, 25, 32, 43, 57, 64.
  Seen after the count, not under a bar: in 9 of the 15 their queen IS their longest dragon. In the 26 unflagged losses she is 2 to 94 long (median about 21). Our queen at her death is 2 or 3 long in nearly every game.
  The mirror: we won 13 full games on the queen rule with only our queen alive (main, free layouts), 4 of them with the shorter longest dragon; v31 8 and 4. With both queens alive on the queen rule: main 15 won of 20, none lost with our longer longest dragon.
  This hour: 3 such losses in 20 games (Maze 71 against 57 and Around UNSW 77 against 64 vs 1995; Slithery Fight 86 against 28 vs 1881), which is what led to the count.
  Verifier, 12:24 KST: holds. All counts recount exactly from the raw replays (825 games). 15 of 41 on main (interval 0.24 to 0.52) and 13 of 36 on v31, the same in both halves; no opponent (26 of them), layout or evening carries it; with three flagged games out 12 of 38. The flag is not near-ties: the margin is 5 or more in 11 of 15.
  Three readings the verifier does not support, all accepted: (1) not that we were ahead: our total length is the larger in 8 of 15, in 6 we end with three or fewer dragons, in 4 their total is over twice ours; (2) not particular to our losses: the mirror share is the same (8 of 21 on both codes). What is lopsided is how often we are the side without a queen: 41 against 13 on main, 36 against 8 on v31;
  (3) their queen is as long in the losses that are not flagged (median 23 and 22). The share leans down with rating (2 of 14 against 2100+ on both codes; not established). Extra: in the flagged games our queen mostly died with no dragon of theirs involved (wall, own body, body of one of ours): 18 of 28 against 15 of 49 in the rest.
  New games, run 1500 (bar F42_new, after battle 1302921; 10 needed): 6 such losses in 60 main games, our longest dragon the longer one in 3 (Around UNSW 76 against 42 vs 2127 with total length 405 against 60; Maze 83 against 44 vs 1928; Portals 42 against 29 vs 2425). The line is 1 or none of 10: in line. In 5 of the 6 their surviving queen is their longest dragon (8, 42, 44, 29, 30, 75 long).
  Totals now, main: 18 of 47 on free layouts (v31 13 of 36); with Slithery Fight 24 of 56, which is 12 percent of all 203 main losses. Mirror: 15 wins with only our queen alive, 4 of them with the shorter longest dragon.
  Where our dragons are (bar F42_hunt, saved 12:42 before the pass existed; own count, work/h25_pass.py, 199 games, 0 errors). At every turn start of their queen after ours died, in the full games that end with only their queen alive on free layouts:
  A = a head of ours of length 4 or less within 6 path steps of her head (kelp and portals respected, dragons ignored); B = a head of ours of any length within 6 path steps.
  Flagged games (our longest dragon the longer one): main 18 games, 6,033 of her turns: A 0.079, B 0.094. v31 13 games, 4,905 turns: A 0.019, B 0.023. Not flagged: main 29 games, 8,956 turns: A 0.065, B 0.074; v31 23 games: 0.038 and 0.043.
  So in nine tenths of her turns (main) no dragon of ours of any length is within 6 steps of her. In 9 of the 18 flagged main games and 8 of the 13 on v31 none ever was (main: Portals 5, and one each of Maze, Around UNSW, Tower Defense, Trauma; v31: Portals 4, Around UNSW 3, Maze 1). Per game on main A is 0.00 in 10, 0.03 to 0.06 in 3, and 0.13 to 0.42 in 5.
  Without Portals (where their queen sits behind a portal and our queen died at rounds 10 to 187 in these five games, F23): main 13 games, 3,880 of her turns, B 0.146 (567 turns); B is zero in 4 of the 13.
  A head of ours within 2 path steps of her head (one move for most dragons): 0.004 of her turns (about 26 turns in 18 games), all lengths.
  The mirror, for scale: in the games where OUR queen is the survivor a short head of theirs is within 6 steps of her in 0.177 of her turns (main, 15 games, 4,372 turns) and 0.177 (v31, 8 games); within 2 steps in 0.020 and 0.021. So their dragons are near a queen that survives them twice as often as ours are near a queen we fail to kill, and five times as often at ram distance.
  By size of layout, flagged against mirror: big 0.116 against 0.31 (4 and 3 games), 1200 cells or fewer 0.069 against 0.151 (14 and 12 games) on main; v31 0.031 against 0.49 and 0.014 against 0.10.
  Her mean length over those turns: 10.6 (main flagged), 11.8 (not flagged), 8.6 and 14.1 on v31.
  Verifier, 15:26 KST (hunt count of run 1500): holds in part. All counts recount exactly. Stands: no head of ours within 6 steps in nine of her turns in ten on main; longer heads add 0.015; the mirror is higher on both codes (factor between two and nine; holds on the same layouts and with fewer heads).
  Accepted corrections: (1) Portals is two sealed halves: in the 13 such losses there (both codes) no head of ours is in her connected area in any of 5,534 turns; the usable figure is the one without Portals, 0.146. (2) Flagged games are no different from unflagged (0.094 against 0.074, inside chance).
  (3) Three games hold 421 of the 567 near turns; without them 0.029. (4) Long heads are near in proportion to their number. (5) The measure cannot tell our not approaching from her keeping away.
  Also from the verifier: on Portals our queen is dead at the end in 48 of 48 games (all codes), never by theirs, by r10 in 19 (16 on a body of ours).
  New games, run 1800 (bar F42_new, after battle 1302921; 10 needed): 7 such losses so far, our longest dragon the longer one in 4 (new: Portals 17 against 13 vs 1767, our queen on her own body at r191). Totals main: 19 of 48 on free layouts; with Slithery Fight 26 of 58, 12 percent of all 226 main losses.
  Sight, first count (bar F42_sight, saved by run 1500; own count, work/h26_pass.py, 654 games, 0 errors). Seen = a head of ours within 3 columns and rows of ANY tile of her body at one of her turn starts; fresh = seen in the last 20 rounds. Her lone turns from round 100 in the f42_set:
  main 48 games, 14,762 turns: fresh 0.693 (flagged 0.81); without Portals 0.621 (40 games). v31 36 games: 0.517; without Portals 0.41. Of the fresh turns a head of ours within 6 path steps: main 0.115 (0.159 without Portals), v31 0.067 (0.104).
  Mirror (their sight of our lone queen): fresh 0.82 and 0.69, near in 0.283 and 0.292 of the fresh turns.
  By the letter that bar FAILED on main (0.55 line) and its second line FAILED on both codes (0.15 line). But the definition is not the bot's: main.cpp lines 1477 to 1486 record a sighting only when the part in view is her HEAD. A queen 12 long seen at her tail is not a target. So a second bar was written (18:10, before the pass) on the bot's rule.
  Sight by the bot's rule (bar F42_sight_head; own count, work/h27_pass.py, 108 full games, 0 errors). Seen = a head of ours within 3 columns and rows of her HEAD. Age of the last sighting at her lone turn starts from round 100, f42_set without Portals:
  main (40 games, 11,874 turns; her mean length 12.5): 20 rounds or less 0.505; 21 to 50 0.156; 51 to 100 0.111; over 100 0.090; never seen 0.137. v31 (30 games, 10,321 turns; 10.1): 0.341, 0.139, 0.096, 0.169, 0.255.
  Nearest head of ours by path steps to her head (6 or less / 7 to 12 / further or no path), main: sighting 20 or less 0.190 / 0.228 / 0.583; 21 to 50 0.019 / 0.151 / 0.830; 51 to 100 0.008 / 0.121 / 0.872. v31: 0.120 / 0.311 / 0.569; 0.012 / 0.307 / 0.681; 0.015 / 0.248 / 0.736.
  Her head in view at that very turn: main 0.130 of turns, v31 0.095; the seeing head is 4 long or less in 0.89 and 0.93 of them.
  The mirror (their heads, our lone queen; main 16 games 4,523 turns, v31 8 games 2,346): sighting 20 or less 0.663 and 0.566; never 0.018 and 0.110; a head within 6 in 0.343 and 0.349 of the fresh turns; her head in view 0.243 and 0.205.
  Slices on main without Portals: halves 0.413 and 0.537 fresh (10 and 30 games), near when fresh 0.272 and 0.168; against 1700-1899 0.533 and 0.245 (11 games), against 1900+ 0.494 and 0.166 (29). Per game the fresh share is under 0.2 in 10 games and 0.8 or more in 5.
  By layout size (seen after the count, not predicted; the same on both codes): layouts above 1200 cells (13 and 14 games): fresh 0.411 (main) and 0.226 (v31), never seen 0.216 and 0.290; when fresh a head of ours is within 6 steps in 0.380 and 0.268, about as often as theirs in the mirror.
  Layouts of 1200 cells or fewer without Portals (27 and 16 games): fresh 0.563 and 0.460; when fresh a head of ours within 6 steps in 0.105 and 0.046, within 12 in 0.265 and 0.281.
  Portals (8 and 6 games): fresh 0.97 and 0.96, her head in view in half her turns, and no head of ours within 12 path steps in any turn: seen across kelp, never reachable.
would be wrong if: (F42, saved 12:11 before the count; seen before it: the three games of this hour and the older total of queen-rule losses) the flag holds in under 20 percent of such losses on main or on v31, or in either half of main, or one layout holds more than half of the flagged games on main.
  Passed: 0.37 and 0.36; halves 0.46 and 0.32; the largest layout holds 4 of 15.
  Second line: their queen 4 long or less in under 40 percent of the flagged games. FAILED: 2 of 15 and 3 of 13.
inferred: This is the countable core of F35 and F13. The leader phase (F31) does its job in these games: we hold the longest dragon. The queen rule comes first, so it is worth nothing while their queen lives.
  The queen to kill is not a 2-long hider. She is usually one of their longest dragons, often their leader. A long queen is easy to see and hard to box in; a ram into her head kills her whatever her length (head-on deaths are paired).
  In main.cpp the revenge hunt needs a hunter of 4 or less (QH_MAX_LEN) holding a sighting no older than QH_FRESH 20 rounds; F39 measured that our short dragons are seldom near their lone queen.
  A reading, not a count: many opponents let the queen grow while ours stays 2 or 3 long and keeps splitting. If both queens live theirs is then the longer one; whether length also keeps her alive is not shown (F36 found a queen of 5 or more at r200 no safer). Bar F43 for next hour.
not checked: whether our hunters ever reached her in these 15 games (needs a replay pass: short heads of ours within 6 steps of her head, and ram attempts); whether her length makes her harder to ram (more free steps: a 57-long queen moves 15 tiles a turn);
  whether the opponents fed her on purpose; main is 15 games and v31 13, each carried by no one layout or opponent but small. Not yet recounted by the verifier.
look at: data/online/ladder/1301812/M1301815.replay r44-499 (Around UNSW vs 1995: our queen rammed at r44; we end 353 long against 160 with the longest dragon 77 against 64, and lose; their queen is the 64);
  data/online/ladder/1301812/M1301813.replay r137-499 (Maze vs 1995: our queen dies on a wall at r137, length 3; 143 against 103 and 71 against 57 at the end; their queen is the 57);
  data/online/ladder/1251723/M1251727.replay r82-499 (Around UNSW vs 1883: our queen rammed at r82; longest 83 against 28; their queen ends 11 long).
  Hunt count, run 1500: in M1251727 no head of ours is within 6 path steps of her in any of her 417 lone turns; the same in data/online/ladder/1301812/M1301813.replay (Maze, 362 turns, their queen 57 long);
  the other kind: data/online/ladder/1240735/M1240738.replay r90-499 (Prisoners Dilemma 2 vs 1936: a short head of ours within 6 steps in 171 of her 410 turns, within 2 steps in 2, and she lives).
would be wrong if (F42_hunt, saved 12:42 before the pass was written; seen before it: the F42 block and the F39 shares of 0.10 and 0.055): in the flagged games A is 0.20 or more (then we are near and do not ram: the ram decision is the place), or B is under 1.5 times A (then longer dragons are not near her either and raising QH_MAX_LEN cannot help), on main or on v31.
  First line passed: A 0.079 and 0.019. Second line FAILED on both codes: B is 1.19 and 1.23 times A. So the constant I named last hour (QH_MAX_LEN 4 to 8) is the wrong place on its own: no dragon of ours is near her, long or short.
inferred (run 1500): it is not the ram decision (we are within one move of her head in 4 turns in 1,000) and not the length limit of the hunters. It is that nothing brings our dragons to her. In main.cpp update of the hunt (lines 1992 to 2011): a dragon hunts only while it is 4 long or less, not the leader, and holds a sighting of her no older than QH_FRESH 20 rounds;
  when it reaches her last known tile and she is not in view it stops and waits for a newer sighting (qh_miss_round). There is no search. F39 measured that their lone queen was never seen at all in a quarter of her turns and not seen in the last 20 rounds in 4 turns in 10. After grow_round the short dragons are also the ones sent to feed the leader.
  A reading of the code, not a count: once the sighting is 20 rounds old every hunter drops the hunt, and with 40 to 60 dragons on the board nobody is asked to look for her.
smallest test: one default-off switch, in the hunt terms the code already has: when our queen is dead and theirs is not known dead (the revenge case, qh_queen_dead() and round at least QH_REVENGE_ROUND), let a sighting stay good for 100 rounds instead of QH_FRESH 20,
  and do not close the target when the hunter reaches her last tile without seeing her (the qh_miss_round line): let it stay within view range of that tile. Second arm, alone: QH_MAX_LEN 4 to 8 in the revenge case only. The count says the second arm alone should do little; it is the control.
  Test set: local games that reach round 500 with our queen dead and theirs alive, on layouts with and without portals. Pass mark to write first: a head of ours within 6 path steps of their lone queen in at least 0.20 of her turns (now 0.09 on main, theirs 0.20 near ours),
  their lone queen alive at the end in under half of such games, and wins on longest dragon with both queens dead do not fall.
  Before building: count how old our last sighting of her is in these 47 games (bar F42_sight in state.json). If she is fresh to us in most turns and still nobody is near, the place is qh_reach() or the feeding, not QH_FRESH.
would be wrong if (F42_sight, saved by run 1500 before the 50 new games existed): fresh in 0.55 or more of her turns on main. FIRED by the letter (0.693; 0.621 without Portals). Second line (near in under 0.15 of fresh turns) FIRED (0.115 and 0.067). The definition counted her body; see the measured lines.
would be wrong if (F42_sight_head, saved 18:10 before work/h27_pass.py existed; seen before it: the first count and the code lines): claimed under 0.40 fresh on both codes without Portals; wrong at 0.55 or more on main. main 0.505: between the lines. v31 0.341: claim met.
  Second line (a sighting aged 21 to 100 in at least 0.25 of her turns; wrong under 0.10): main 0.267 passed, v31 0.234 not wrong. Third line (a head within 6 in 0.30 of fresh turns; wrong under 0.15 on main): main 0.190 between the lines; v31 0.120.
inferred (run 1800): both gaps are real and neither is the whole. Half her turns on main already have a sighting that QH_FRESH accepts, and in four fifths of those no head of ours is within 6 steps. A quarter more have a sighting 21 to 100 rounds old: that is what QH_FRESH 100 (change 2 of the team's losses/plan.md) would add, and in those turns our nearest head is further than 12 steps in 83 to 87 percent.
  The size split says which gap is where. Above 1200 cells we lose sight of her (fresh 0.41 and 0.23) and are near when we have it: a longer memory or a search fits there. On small layouts with corridors we have the sighting (0.56 and 0.46) and are not near (0.10 and 0.05): there the walk is the gap, not the memory.
  A reading, not a count: she is 10 to 13 long on average, so she has 3 or 4 free steps a turn; a hunter of 4 or less (QH_MAX_LEN) has one. A hunter that cannot pay cannot close on a queen that walks. Whether she does walk away from our hunters is not measured (the verifier's point 5 stands).
  Portals is outside any hunt: 14 of the 84 losses of this kind over both codes, 6 of the 19 flagged on main. There the only lever is our own queen (F23).
smallest test (run 1800; replaces the order given in run 1500): the same default-off revenge switch, judged by layout size. Arm A (memory): a sighting stays good for 100 rounds and the hunter does not stop at her last tile. Expect a gain above 1200 cells only. Arm B (speed, revenge case only): allow hunters up to her last seen length, not the leader, so that a hunter has her free steps. Expect a gain on small layouts if the reading is right.
  Pass mark, written before any run: a head of ours within 6 path steps of their lone queen in 0.30 of her turns that have a sighting 20 rounds old or less (now 0.19 on main; theirs 0.34), their lone queen alive at the end in under half of such games, wins on longest dragon not down. Leave Portals out of the test set.
  If there is no build slot, count first: after each turn with her head in view, how far the nearest head of ours is 5 and 10 rounds later and how many tiles she moved (bar F42_follow in state.json).
### F44 On five small layouts where the queens start 10 tiles apart or less we are wiped out by round 125 in one game in six, and in two of five against 2100+ teams. In those games their short dragons ram ours in the opening and we have eaten half as much by round 50
status: confirmed in the narrower wording of the verifier (15:26: holds in part: rare below 1900, common in the top band; two opponents carry most of the top band; the description fits early wipe-outs in both directions). The layout property (bar F44_rate passed on both codes) and the opening-ram counts (bar F44_who between its lines on both codes) are of this hour and to-verify      first seen: 7 Oct 12:40 KST run 20261007-1200 (as a lead)   last tested: 7 Oct 18:20 KST (rows.jsonl; own count work/h26_pass.py)
measured: rows.jsonl. Early wipe-out = the game ends by elimination with none of our dragons left at raw round 125 or earlier. main 18 of 435 games, v31 16 of 410. All 34 are on layouts of 1200 cells or fewer.
  By opponent rating on those layouts, main: 1700-1899 4 of 110, 1900-2099 7 of 142, 2100+ 7 of 32. v31: 1 of 156, 10 of 92, 4 of 32. Both codes: 5 of 266, 17 of 234, 11 of 64.
  The other way round (we wipe them out by round 125), same cells: main 10, 11 and 2; v31 18, 11 and 2. So against 1700-1899 we do it to them six times as often as they to us (28 against 5); against 2100+ they do it to us (11 against 4).
  Layouts, main: Trophy 5, Stripes 3, Queen Of Spades 3, Prisoners Dilemma 1 and 2 4, Devil 2, Autarky 1. v31: Stripes 7, Prisoners Dilemma 4, Queen Of Spades 2, Trophy 2, Devil 1. 13 opponents on main (none more than 3 games), 11 on v31.
  14 of the 18 (main) and 14 of the 16 (v31) are on layouts where the queens start 10 tiles apart or less (wrapped distance, walls ignored); the rest are Queen Of Spades (23) and Autarky (18). Rates per layout property not yet counted.
  Bar line 1: our pearls eaten by r50 are under half of theirs in 13 of 18 (main) and 13 of 16 (v31). Total length at r50, ours against theirs, main: 2 to 16 against 8 to 54 (median 6 against 25).
  Bar line 2: on 2-dragon-start layouts 11 of 18 and 11 of 16.
  Beside the bar. Our queen: dead in all 34, rammed (head-on, their dragon the mover) in 17 of 18 on main at rounds 24 to 116 (median 80) and in 14 of 16 on v31 (rounds 22 to 125; the other two: her own body, and a head-on in which she was the mover).
  Our deaths in r0-100 per game: 11.2 in the wipe-outs, 8.7 of them head-on (0.78); in the other main games on the same layouts 20.5, 8.2 of them head-on (0.40). v31: 8.1 with 6.4 head-on; 17.9 with 8.5. So in these games nearly every dragon we lose is lost in a head-on meeting, and we have few to lose.
  Halves of main: 3 in the earlier 97 games, 15 in the later 338.
  Verifier, 15:26 KST: holds in part. All counts recount exactly (890 replays). Stands: main 7 of 32 against 2100+ and 4 of 110 against 1700-1899 on small layouts (Fisher 0.003; 105 of 20,000 whole-battle shuffles as large); not the layout mix (2.9 expected at pooled layout rates, 7 seen); the description (pearls under half; queen rammed, by a dragon 2 or 3 long in 30 of 31).
  Weaker, all accepted: (1) the codes differ: main jumps at 2100, v31 at 1900; common to both is that it is rare under 1900 (5 of 266). (2) Two opponents (chad gdp, dev test 1) give 8 of the 11 wipe-outs in the top band over both codes; without them 3 of 37. (3) Pearls under half and a rammed queen describe early wipe-outs in both directions (when we do it to them: 19 of 24 and 19 of 24 on main).
  (4) 33 of 34 are on Trophy, Prisoners Dilemma, Devil, Stripes and Queen Of Spades, where one side is gone by r125 in 89 of 239 games and which side follows the rating (ours / theirs / games: 5 / 28 / 102, 16 / 21 / 98, 11 / 4 / 28).
  New games, run 1800: 4 more early wipe-outs in 50 main games, all on Stripes (rounds 58, 61, 77, 97), against teams rated 2180, 1889, 1795 and 1913. Bar F44_new (15 main games against 2100+ on small layouts needed; weakened if none): 11 so far, 1 wiped out; it can no longer fire. Now 22 on main, 16 on v31.
  By band on main small layouts now: 1700-1899 6 of 125, 1900-2099 8 of 151, 2100+ 8 of 43. Two of the four new ones are against teams under 1900, both on Stripes.
  Layout property (bar F44_rate, saved by run 1500; rows.jsonl, small layouts against 1900+): queens 10 tiles apart or less at spawn: main 13 of 89, v31 12 of 65; further apart: 3 of 105 and 2 of 59. That is 5.1 and 5.4 times; the largest single layout holds 4 of 13 and 5 of 12 (Stripes). Passed.
  Seen after the count: the near group is not all alike. 32 of all 38 early wipe-outs are on Stripes, Trophy, Devil and the two Prisoners Dilemma layouts (288 to 625 cells, queens 7 to 10 apart, the two sides connected). None in 45 games on Default (queens 2 apart, 1024 cells, 4 starting dragons), none in 50 on Portals (sealed halves),
  none in 109 on Tower Defense and weakhold (512 and 600 cells, queens 18 and 12 apart). The other 6 are Queen Of Spades 5 and Autarky 1. On the five layouts, all bands: main 18 of 94 (5 of 29, 6 of 42, 7 of 17 by band), v31 14 of 103 (1 of 54, 9 of 34, 3 of 10). We do it to them there in 25 and 32 games.
  Who rams in the opening (bar F44_who, saved by run 1500; own count, work/h26_pass.py, 654 games, 0 errors; head-on meetings between the teams in raw rounds 0-60; mover = the dragon whose turn it is when the other dies): in the 34 early wipe-outs of the bar their dragon is the mover in 83 of 115 meetings on main (0.72) and 50 of 64 on v31 (0.78).
  In the other games on the same layouts: 242 of 576 (0.42) and 233 of 526 (0.44). Their movers are 2 or 3 long in 77 of 83 and 50 of 50; our victims 2 or 3 long in 72 of 83. Our queen is the victim in 8 and 7 of these opening rams. The 4 new wipe-outs: 4 meetings, theirs the mover in 3; two of the four games had no meeting by r60.
  By rating, every small-layout game, r0-60 (seen after the count): their share of the movers is 0.44, 0.46 and 0.65 against 1700-1899, 1900-2099 and 2100+ on main (125, 151 and 43 games; 242, 393 and 114 meetings); v31 0.43, 0.51 and 0.60 (156, 92 and 32 games). On the five layouts alone: 0.44, 0.47, 0.66 and 0.43, 0.54, 0.58.
  Their share is above ours for 8 of the 10 top-band opponents on main and 7 of 8 on v31. Below 2100 we are the side that rams in the opening (0.54 to 0.57 of meetings on main).
would be wrong if: (F44, saved 12:42 before the count; seen before it: the wipe-out counts by band and three games against 2474) under 50 percent of the early wipe-outs have our pearls by r50 under half of theirs, on main or on v31 (claimed 70). Passed: 0.72 and 0.81.
  Second line: under 40 percent on 2-dragon-start layouts (claimed 60). Passed: 0.61 and 0.69. Games that ended before r50: none.
inferred: two things are true at once and the rows cannot order them. We are far behind in pearls by round 50, and four fifths of the dragons we lose are rammed. "Never grew" passed by the letter, but a team that rams our first children costs us the pearls those children would have eaten, so I do not read the bar as "not a fight".
  What separates the 2100+ teams here is measured: they finish small-layout games early against us, the lower band does not. It fits F24 (they pay length to sprint into our queen) and F4 (ahead by r100 in four games of five).
  For unseen maps the property is a small board with the two queens close at spawn; a 2-dragon start makes it worse but is not needed (Prisoners Dilemma and Devil start with 3 to 5).
not checked: who is the mover in the head-on meetings of rounds 0 to 60 in these games, and how long the rammers are (needs a replay pass; bar F44_who in state.json); whether our queen had a safe step when rammed; the rate per layout property (bar F44_rate);
  whether the same opponents wipe out other teams as early. 34 games on two codes; the rating gradient rests on 11 games against 2100+. Not yet recounted by the verifier.
look at: data/online/ladder/1312501/M1312503.replay r0-99 (Trophy vs 2309: our queen rammed at r33, 16 pearls against 47 at r50, wiped out at r99);
  data/online/ladder/1300343/M1300344.replay r0-99 (Trophy vs 2474: 21 pearls against 73 at r50, queen rammed in the last round) and M1300346.replay r0-93 (Devil: queen rammed at r30);
  data/online/ladder/1249035/M1249036.replay r0-104 (Queen Of Spades vs 2382: no pearl eaten by r50 against 20).
smallest test: no change yet, count first (bar F44_who): in rounds 0 to 60 of these 34 games, which side is the mover in head-on meetings and at what lengths, and how far our first children are from their heads when they die. If theirs is the mover in three meetings of four, the test is an early-rounds form of the threat rule on small boards (the bot already has AGGRESSIVE_MAX_CELLS 1200 as the size line); if ours is, it is our own rams in the opening.
would be wrong if (F44_rate, saved by run 1500): the early wipe-out rate with queens 10 or less apart is under 1.3 times the rate further apart on either code, or one layout holds more than half of the near wipe-outs on both codes. Passed: 5.1 and 5.4 times; Stripes 4 of 13 and 5 of 12.
would be wrong if (F44_who, saved by run 1500; seen before it: head-on is 0.78 of our early deaths in these games, the queen rammed in 31 of 34, F8): their dragon is the mover in under 0.65 of the opening meetings on main or on v31; claimed 0.80. Between the lines: 0.72 and 0.78.
inferred (run 1800): a head-on meeting kills both dragons, so a ram is a one-for-one trade. A side with 9 dragons that trades with a side of 3 wins the board. In the wipe-outs they are both the side that ate (line 1 of the first bar) and the side that takes the trade, three meetings in four; in ordinary games on the same layouts we take it more often than they do.
  The 2100+ teams take the trade in the opening against us; the bands below do not. It is the first measured thing they do in the opening that the lower bands do not (question 2). It may be a rule of theirs (ram when ahead in dragons) or a result of being ahead; the count cannot tell.
  For unseen maps the property is a board of about 600 cells or fewer with the queens within 10 tiles and no wall between the sides. AGGRESSIVE_MAX_CELLS 1200 treats Default, Maze and Trauma like these five; the wipe-outs are not there.
not checked (run 1800): whether our dragons could have stayed out of reach (bar F44_dodge); whether the opponents ram more when they have more dragons in view; the Stripes games of this hour end early without many meetings by r60 (4 meetings in 4 games), so on Stripes the trade is not the whole story (F7: we do not eat there).
look at (run 1800): data/online/ladder/1322012/M1322016.replay r0-58 (Stripes vs 2180: 7 pearls against 40 by r50, wiped out at r58); data/online/ladder/1321453/M1321456.replay r0-61 (Stripes vs 1889: 0 pearls against 32 by r50).
smallest test (run 1800): no change yet; one more count decides the switch (bar F44_dodge in state.json): in rounds 0-60 on the five layouts, how often a dragon of ours ends its turn inside the free reach of a short enemy head when it had a step that stays outside, split by whether we have fewer dragons than they do.
  If we stand in reach as often when outnumbered as when not, the test is a default-off switch that refuses the one-for-one trade while we have fewer dragons in view than they do, on boards of 625 cells or fewer, rounds 0 to 100.
  Pass mark: early wipe-outs on these five layouts against 1900+ from one game in five to one in ten, with our own early wipe-outs of them (25 of 94 on main) down by no more than a quarter.
### F45 Four in five of the games in which we are wiped out after round 125 were lost by round 100: our total length was already under 0.8 of theirs
status: to-verify (the bar passed on main and on v31 and in both halves of main; it is just as true of the opponents when we wipe them out)      first seen: 7 Oct 18:09 KST run 20261007-1800   last tested: 7 Oct 18:09 KST (rows.jsonl)
measured: rows.jsonl. Late wipe-out = ended by elimination with none of ours left, last_round 126 or more. Behind = our total length at r100 under 0.8 of theirs.
  main: 41 of 52 (0.79). v31: 49 of 58 (0.84). main halves 8 of 11 and 33 of 41; layouts of 1200 cells or fewer 32 of 40, larger 9 of 12; against 1700-1899 9 of 13, 1900-2099 18 of 25, 2100+ 13 of 13.
  In the same 52: behind by the same margin already at r50 in 30; pearls by r50 under half of theirs in 24; 6 or fewer of ours alive at r100 in 31; on 2-dragon-start layouts 31. v31, of 58: 41, 36, 36, 34.
  Layouts, main: Stripes 12, Tower Defense 9, Islands 8, Default 5, Queen Of Spades 4, Trophy 4, Australia 3, five others 7.
  The 11 that were not behind at r100 (Stripes 4, Default 2, Islands 2, three others): our total is under 0.8 of theirs at r200 in 10 of the 10 that got there (362 against 1,013 in sum); the first queen to die was ours in 5, theirs in 6.
  The mirror: when we wipe them out after round 125 they were behind at r100 in 78 of 85 (main) and 56 of 64 (v31). So this is how the game goes for either side, not a fault of ours alone.
  For scale, every main game that reached r100 (454): we are behind by this margin in 159 and win 44 (0.28); they are behind in 168 and win 33 (0.20). On layouts of 1200 cells or fewer: we win 31 of 105 from behind, they 11 of 128. Above 1200 cells: we 13 of 54, they 22 of 40: on big layouts a side of theirs that is behind at r100 wins more than half (F25, F31).
would be wrong if: (saved 18:07 before the count; seen before it: the bucket table of the team's losses/plan.md with 43 late wipe-outs, and one Stripes game of this hour) under 50 percent on main or on v31; claimed 70. Passed: 0.79 and 0.84.
inferred: the wiped-out-later bucket (52 of 226 main losses, the second largest) is not a fighting fault of the middle game. It is the opening seen later. With the 22 early wipe-outs (F44), 74 main losses are eliminations and about 60 of them were decided by round 100.
  The levers are the ones already named: the 2-dragon start (F7, F10: Stripes and Tower Defense hold 21 of the 52) and the opening trade (F44). From level or ahead at r100 we are wiped out late in 11 main games of 295.
not checked: why the 11 level games turned (they fall behind between r100 and r200); the margin 0.8 is my choice, not tried at 0.7 or 0.9; no replay count; not yet recounted by the verifier.
look at: data/online/ladder/1317597/M1317597.replay r0-166 (Stripes vs 1910: 1 pearl against 17 by r50, 2 dragons against 11 at r100, wiped out at r166); data/online/ladder/1321453/M1321457.replay r0-181 (Devil vs 1889, wiped out at r181).
smallest test: none of its own. It says where not to look: the ladder supports no switch for the fighting after round 100.
### F46 In full games that end with both queens dead we win 57 percent against teams under 2100 and a third against 2100+ teams
status: candidate (my bar is between its lines on main and passed on v31; it adds nothing to the overall gap by rating)      first seen: 7 Oct 18:09 KST run 20261007-1800   last tested: 7 Oct 18:09 KST (rows.jsonl)
measured: rows.jsonl; last_round 499 and both queens dead at the end (decided on longest dragon or total length), every layout. main 165 games, 92 won; v31 145, 73 won.
  By opponent band, main: 1700-1899 41 of 69, 1900-2099 39 of 69, 2100+ 8 of 22 (13 battles, 9 opponents). v31: 34 of 63, 27 of 52, 4 of 20 (9 battles, 7 opponents).
  Against 2100+ by size: layouts of 1200 cells or fewer 6 of 13 (main) and 4 of 14 (v31); larger 2 of 9 and 0 of 6.
  Second line: in the games of this kind lost to 2100+ our longest dragon at r300 was already the shorter one in 10 of 14 (main) and 8 of 16 (v31; equal in 4 more). The same share in the lower bands on main: 16 of 28 and 23 of 30. Nothing here is special to the top band.
  Margins at the end in the 14 main losses to 2100+ (our longest against theirs): 3-87, 5-31, 10-25, 10-106, 13-28, 15-44, 15-80, 19-22, 20-38, 30-38, 35-56, 37-77, 45-48, 65-71.
would be wrong if: (saved 18:07 before the count; seen before it: 8 of this hour's 11 losses to 2100+ are of this kind) the 2100+ share is 0.40 or more on main or on v31 (claimed under 0.30), or the 1700-1899 share is under 0.45. main 0.36: between the lines. v31 0.20: passed. Lower band 0.59 and 0.54: passed.
  Second line: our longest the shorter one at r300 in under 50 percent of those losses. main 0.71 passed; v31 0.50, on the line.
inferred: this ending is our best one against the top band, not our worst: 8 of 22 against 17 of 70 over all main games against them. What the 2100+ teams do more often is end the game before round 500 (the table by band in F4: wiped out in 0.30 of games against 0.10) and keep their queen (0.20 against 0.09).
not checked: nothing further; not queued for the verifier.
look at: data/online/ladder/1322206/M1322208.replay (Portals vs 2408, 35 against 56), M1322210.replay (Slithery Fight, 3 against 87) and M1322206.replay (Australia, 10 against 106).
smallest test: none.
### F37 Between rounds 101 and 200 our queen dies boxed in, on a wall or her own body, two to four times as often as their queens (20 times by the engine reasons alone); Maze, Portals and weakhold are two thirds of it
status: confirmed in the narrower wording of the verifier (08:40: holds in part; the core holds firmly); my bar on what is special about it (our own dragons beside her) FAILED this hour; F38 says where it happens      first seen: 7 Oct 08:17 KST run 20261007-0800   last tested: 7 Oct 18:20 KST (rows.jsonl, new games)
measured: rows.jsonl, free layouts, games that reached r200, queens alive at r100. Rate = queens that die by wall or own body in raw rounds 101-200 / queens alive at r100.
  main: ours 21 of 145 (13 wall, 8 own body), theirs 1 of 142. v31: ours 30 of 175 (22 wall, 8 own body), theirs 11 of 191.
  Her length at death is 2 or 3 in all 51. Their queen was already dead in 7 of the 21 (main) and 9 of the 30 (v31). We won 10 of the 21 games and 18 of the 30.
  By layout, ours then theirs, main: Maze 8 of 20 and 0 of 21; Portals 3 of 4 and 0 of 8; weakhold 2 of 9 and 1 of 10; Islands 2 of 7 and 0 of 4; Around UNSW 2 of 18 and 0 of 15; Tower Defense 1 of 21 and 0 of 19;
  Devil, Stripes, Prisoners Dilemma 2 one each; Trauma 0 of 25, Australia 0 of 11, Default 0 of 10, Queen Of Spades 0 of 10, Autarky 0 of 6.
  v31: Maze 11 of 22 and 2 of 20; Portals 6 of 6 and 4 of 23; weakhold 5 of 16 and 1 of 19; Islands 2 of 11 and 1 of 10; Around UNSW 2 of 17 and 1 of 20; Default 2 of 8 and 0 of 5; Tower Defense 1 of 21 and 2 of 19; Trauma 0 of 17, Australia 0 of 21, Autarky 0 of 16, Queen Of Spades 0 of 16.
  Corridor share (maps.json) does not order the layouts: Maze 0.40 has it, Tower Defense 0.35 and Trauma 0.30 do not, weakhold 0.29 does. Corridor-heavy layouts without Maze and without Portals, both codes: 15 of 129; the other layouts 8 of 139. That is 2.0 times, on the line of the bar and inside chance.
  The window. Queen deaths by wall or own body in full games on free layouts, ours against theirs: main r0-100 12 against 8, r101-200 17 against 1, r201-300 9 against 5, r301-499 4 against 9. v31: 14 against 10, 23 against 9, 9 against 8, 1 against 10.
  In the same full games the rams (queen as standing victim) in r101-200 are 26 against 17 (main) and 27 against 22 (v31). So of the surplus of our queen deaths in r101-200 (46 against 21; 55 against 39) two thirds or more is wall and own body, not rams.
  Maze, whole game: our queen dies by wall or own body in 14 of 23 main games and 16 of 24 v31 games (theirs 7 and 7). No Maze game in either code ended with only our queen alive; 5 and 6 ended with only theirs. We still win Maze 17 of 23 on main (9 of 14 when she dies that way, 8 of 9 otherwise).
  What boxes her in (own count, work/h17_pass.py, bar F37_board saved 08:19 before the pass was written; the board at the start of her fatal turn, all 60 of our such deaths in r101-200 on free layouts, games that ended before r200 included):
  she has no free tile next to her head in 60 of 60 (their queens: 16 of 16). Without Portals (51 deaths, 20 main and 31 v31): kelp on at least two of the four sides in 49.
  The tile that closes the way: another dragon of OURS in 31 of 51 (13 of 20 main, 18 of 31 v31; a dragon born from her own split in only 4 of those), an enemy dragon in 2, and in the other 18 nothing but kelp: she stands on a dead-end tile with her own body behind her.
  Maze: 19 deaths, a dragon of ours in front in 13, a dead-end tile in 6, an enemy in 0. weakhold: 8 deaths, a dragon of ours in 6. Portals (9 deaths): kelp on three sides in 7, a dragon of ours in 2; that is the small room of F23.
  She had split in the 10 rounds before in 25 of the 51 (9 of 20 and 16 of 31). Their queens (16 deaths, both codes): a dragon of their own in 5, an enemy in 3, a dead-end tile in 8.
  Verifier, 08:40 KST: every number recounts exactly. Beyond chance on both codes, on most layouts (ours higher on 9 of 14 main layouts, lower on none), no opponent or evening carries it, and still there with Maze removed (main 13 of 125 against 1 of 121; v31 19 of 153 against 9 of 171).
  Three corrections, all accepted. (1) "Many times" is too strong: their boxed-in queens often end the turn by ramming one of our heads, which engine reasons 0 and 1 miss. Every boxed-in death in r101-200: main ours 24 of 145 against 6 of 142 (3.9 times), v31 38 of 175 against 19 of 191 (2.2 times).
  With no enemy beside her: 24 against 2 and 34 against 14. (2) Maze is 19 of 51 (37 percent), not nearly half; Maze, Portals and weakhold are 35 of 51. Outside those three it holds on main (8 of 112 against 0 of 103) and not on v31 (8 of 131 against 4 of 129).
  (3) The other windows are level only within chance (r201-300 on main: 9 of 64 against 5 of 94). The board, on the 51 deaths of the claim itself: no legal step in 51; a dragon of her own team on a neighbour tile in 29 (her own child in 3); a dead-end tile in 22; an enemy in none; a split in the 10 rounds before in 23.
  Cost: not shown. We won 10 of the 21 main games and 18 of the 30 v31 games (other games that reached r200: 99 of 178 and 101 of 240).
  New this hour, bar F37_base_rate (saved 08:22) FAILED. Own count, work/h18_pass.py, every queen turn. On Maze and weakhold in r101-200 our queen starts 0.074 of her turns (4,313) with another dragon of ours next to her head; their queens 0.133 (6,047). I claimed 1.5 times theirs; it is 0.56 times.
  In r201-300 ours is 0.126, so the window is not special either (0.59; I claimed 1.3). By code: main 0.061 against 0.130, v31 0.089 against 0.136. All free layouts, r101-200: main 0.043 against 0.069, v31 0.047 against 0.081.
  So their queens have their own dragons beside them more often than ours does, and live. What differs is the tile she stands on: see F38 (on narrow tiles it is the other way round, 0.020 against 0.006).
  New games (bar F37_new_games, after battle 1285561; 20 needed): 11 of our queens alive at r100 in games reaching r200, 1 died this way (weakhold vs 2105, wall at r117); theirs 0 of 9. Totals, main: 22 of 156 against 1 of 151.
  New games, run 1000 (bar F37_new_games; 20 needed): 19 of our queens alive at r100 in games reaching r200, 2 died this way; theirs 0 of 16. One short of the count; in line. Totals, main: 23 of 164 against 1 of 158.
  New games, run 1100 (bar F37_new_games, after battle 1285561; 20 needed, now met): 31 of our queens alive at r100 in games reaching r200; 3 died by wall or own body in r101-200 (weakhold wall r117, Stripes wall r166, Maze own body r136; all three games lost); theirs 0 of 26.
  The line was 1 or none with theirs as many: holds. Totals, main: 24 of 176 against 1 of 168. The Maze death of this hour ends a walk of 13 turns down a passage (F38, new part).
  New games, run 1200 (bar F37_new_games_2, after battle 1298211; 20 of our queens alive at r100 in games reaching r200 needed): 7 so far; ours died on a wall or her own body in r101-200 in 1 (Maze vs 1995, r137, length 3; that game was then lost on the queen rule with our longest dragon 71 against 57), theirs in 0 of 8.
  New games, run 1500 (bar F37_new_games_2, after battle 1298211; 20 of our queens alive at r100 in games reaching r200 needed, now met): 34 queens a side; ours died on a wall or her own body in r101-200 in 6, theirs in 1. The line was 1 or none for ours: holds. All main: 30 of 210 against 2 of 202.
  New games, run 1800 (bar F37_new_games_3, after battle 1316833; 20 of our queens alive at r100 in games reaching r200 needed, now met): 21 of ours, 19 of theirs; ours died on a wall or her own body in r101-200 in 5 (weakhold three times, Portals twice), theirs in 4 (Portals twice, Islands, Tower Defense).
  The bar (weakened if ours in 1 or none) did not fire, but this block shows no gap: 5 of 21 against 4 of 19. All main: 35 of 231 against 6 of 221. The next bar compares the two sides (state.json, F37_new_games_4).
would be wrong if: (08:17, before the count; seen before it: the full-game counts by window and that Maze carried about half) (a) pooled over free layouts our rate is under 2 times theirs on main or v31. Passed: 0.145 against 0.007; 0.171 against 0.058.
  (b) on corridor-heavy layouts without Maze our rate is under 2 times our rate on the other layouts, both codes pooled. Not crossed, by a hair: 2.0 times (15 of 129 against 8 of 139), which chance alone gives easily. (c) on Maze our rate under 2 times theirs in either code. Passed: 8 of 20 against 0 of 21; 11 of 22 against 2 of 20.
  (F37_board, 08:19, before the pass was written) wrong if a body of her own team is on at least two of the four tiles in under 0.35 of the deaths; the split reading wrong if she split in the 10 rounds before in under 0.15. Not wrong: 31 of 51 (0.61) and 25 of 51 (0.49).
  Read with care: her own neck is always one of the four tiles, so the first figure means "another dragon of ours is next to her head", and the split figure has no base rate beside it; her own child is the blocker in only 4.
  (bar F35_first_death, 08:16, FAILED, which is how this was found) I had claimed the surplus of our queen deaths in r101-200 of full games is rams; rams are 36 and 31 percent of it.
inferred: F3 (our queen ends on a wall or her own body about twice as often as theirs) is not spread over the game. It sits between rounds 101 and 200, where it is 21 against 1 on main. Outside that window the two sides are level.
  The verifier showed for F3 that these are queens with no safe step left. The board count of this hour says what closes the last step: in six cases of ten one of our own dragons, met in a corridor with kelp on both sides; in three or four of ten a dead-end tile;
  an enemy almost never (2 of 51). So opponents do not trap her. Our own dragons do, or she walks to the end of a blind corridor.
  In main.cpp nothing keeps our other dragons away from her head: QUEEN_GIVE_WAY is 0 (the rule is written: a non-queen dragon loses QUEEN_GIVE_WAY_PENALTY 3000 for a destination within that many tiles of the queen it sees) and QUEEN_ALLY_BLOCK is false.
  QUEEN_DEAD_END is true (penalty 6000, QUEEN_ROOM 8), yet 18 deaths are on dead-end tiles; my guess is that once she is inside a corridor every step is forced, so the choice was made at its mouth some turns before.
  Her own splits are not it: the child is next to her in 4 of 51. Why the window is r101-200: our dragon count roughly doubles between r50 and r150, and from round 201 or 301 the small dragons go to feed the leader and die; that would thin the corridors again. A guess.
  As a map property the safest wording is "narrow ways and small rooms" (Maze, weakhold, Portals), not corridor share: Tower Defense and Trauma have as many corridor tiles and show nothing.
not checked: what stands on the four tiles around her head at her last turn (kelp, her own body, a dragon of ours, an enemy); whether she or a neighbour of ours split in the 10 rounds before; all main games are one day. Games at stake are few: 11 of the 21 main games were lost, and Maze is won 17 of 23 anyway.
look at: data/online/ladder/1281566/M1281569.replay r100-118 (Maze vs 2014: our queen, length 2, dies on her own body at r118; their queen lives and ends 94 long; lost);
  data/online/ladder/1259377/M1259381.replay r90-103 (Maze vs 2011: wall at r103, length 3, only their queen alive at the end, lost);
  data/online/ladder/1274524/M1274526.replay r130-143 (weakhold vs 1799: own body at r143, length 3, lost with only their queen alive).
smallest test: one constant that exists and is off: QUEEN_GIVE_WAY 2 (0 now), so that our other dragons do not step within 2 tiles of the queen they see. It addresses the 31 of 51; the 18 dead-end deaths need her own look-ahead (QUEEN_ROOM, QUEEN_KNOWN_STEP) and are a second step.
  Local games on Maze and weakhold, or any layout with narrow ways. Pass mark to write first: her wall-or-own-body deaths in r101-200 fall from 4 in 10 Maze games to under 2 in 10, her death rate by r200 falls, our pearls by r200 do not fall by more than a tenth
  (dragons that give way eat less), and wins there do not fall (Maze 17 of 23 now). The verifier has been asked to recount the board independently.
  Updated 09:12: see F38. Two existing switches fit, one for each side of the meeting: QUEEN_GIVE_WAY 2 (other dragons keep off her) and QUEEN_ALLY_BLOCK true (her room count closes the tiles next to friendly heads; mark_ally_block()). The dead-end half needs a new rule (F38, third switch).

### F38 Our queen dies on a wall or her own body only on narrow tiles (two or fewer open sides); once on one she walks on down the passage where their queens step back out, and a turn inside a long passage is six times as deadly as an average turn for either queen
status: weakened (new-games bar fired: on 64 new games her share of turns on narrow tiles is 0.93 of theirs, line 1.15; before that confirmed and narrowed to Maze, weakhold and Tower Defense)      first seen: 7 Oct 09:10 KST run 20261007-0900   last tested: 7 Oct 15:42 KST (own count work/h25_pass.py, new games)
measured: own count, work/h19_pass.py (all 725 main and v31 games, 0 errors; bar F38 saved 09:08 before the pass was written). Narrow tile = her head tile has two or fewer sides without kelp (a portal side is open; dragons ignored). Dead-end tile = one open side. Counted at the start of every queen turn.
  (c) Where she dies. Queen deaths by wall or own body in r101-200 on free layouts: ours 61 (24 main, 37 v31), 58 of them from a turn that started on a narrow tile (25 on a dead-end tile). Theirs 16, 13 from a narrow tile. All rounds, main: ours 60 of 65, theirs 30 of 32.
  Per 1,000 queen turns that start on a narrow tile in r101-200: main ours 21.5 (23 deaths in 1,068 turns), theirs 3.3 (2 in 615). v31 ours 36.2 (35 in 966), theirs 15.5 (11 in 712). Both codes 28.5 against 9.8: 2.9 times.
  On tiles with three or four open sides: 0.12 against 0.10 per 1,000 (3 deaths each, in 24,696 and 28,746 turns). Halves of main: 20.4 against 8.0 (6 deaths and 1) and 22.0 against 2.0 (17 and 1). Without Portals, both codes: 25.1 against 8.0.
  How often she is there. Share of queen turns on a narrow tile, free layouts, both codes: r0-100 0.082 against 0.059; r101-200 0.076 against 0.044; r201-300 0.056 against 0.049; r301 on 0.041 against 0.046. r0-200 by code: main 0.076 against 0.053 (1.4 times), v31 0.083 against 0.055 (1.5 times).
  (a) Maze and weakhold, r0-200: main Maze 0.138 against 0.032 (4.3 times); main weakhold 0.337 against 0.138 (2.4); v31 Maze 0.187 against 0.088 (2.1); v31 weakhold 0.294 against 0.080 (3.7).
  (b) FAILED. Tower Defense, Trauma and Devil pooled (the other layouts with corridor share 0.27 or more): 0.045 against 0.061, that is 0.73 times. By layout, both codes, ours / theirs. Ours higher: Maze 0.161 / 0.059; weakhold 0.312 / 0.102; Portals 0.122 / 0.026;
  Prisoners Dilemma 1 0.180 / 0.025; Prisoners Dilemma 2 0.205 / 0.005; Devil 0.161 / 0.113; Islands 0.090 / 0.075; Australia 0.030 / 0.025. Theirs higher: Tower Defense 0.046 / 0.081; Trauma 0.014 / 0.016; Stripes 0.122 / 0.136; Queen Of Spades 0.014 / 0.047;
  Around UNSW 0.039 / 0.061; Trophy 0.040 / 0.054; Autarky 0.009 / 0.017; Default 0.009 / 0.020. corridor_share in maps.json does not order these.
  What is with her on the narrow tile (seen after the count, not under a bar). Turns in r101-200 that start on a narrow tile with another dragon of her own team next to her head: ours 41 (17 main, 24 v31) of 2,034; theirs 8 (1 and 7) of 1,327. That is 0.020 against 0.006.
  Deaths from that position: ours 31 (14 and 17), theirs 2. On open tiles it is the other way round: an own dragon beside her in 0.048 of our queen turns and 0.079 of theirs. Deaths on a dead-end tile: ours 25 (8 and 17), theirs 9 (1 and 8). So 56 of our 58 narrow-tile deaths are one of the two.
  Queen length on narrow tiles: 2.6 against 3.7 (mean). Games: main 23 games with such a death, 12 won; v31 35 games, 20 won. No cost in wins shown.
  Opponents by band, share of our queen turns on narrow tiles in r0-200 against theirs: main 0.079 against 0.039 (1700-1899), 0.074 against 0.066 (1900-2099), 0.069 against 0.037 (2100+); v31 0.083 against 0.049, 0.085 against 0.049, 0.073 against 0.078.
  Verifier, 09:45 KST: holds. All numbers recount exactly from 765 rebuilt replays. The per-narrow-turn gap in r101-200 is beyond chance on both codes (side-swap test: main 30 of 20,000, v31 58 of 20,000), survives leaving out Portals (3.15 times),
  any one layout (2.68 to 3.26) and any one opponent (2.65 to 3.32). Three limits, all accepted. (1) About three times is r101-200 and the two engine reasons. All rounds together it is 1.6 times on each code
  (main 16.1 against 10.0 per 1,000 narrow turns, v31 18.3 against 11.4) and from r301 it reverses. Counting every death as the mover from a narrow tile it is 1.7 times (65 in 2,034 against 25 in 1,327): a boxed-in queen of theirs often rams one of our heads (10 of their 25).
  (2) The gap is the two positions: a team mate on her only way out (31 against 2) and dead-end tiles (25 against 9). (3) Five layouts have a far higher narrow share for our queen (Maze, weakhold, Portals, both Prisoners Dilemma: 0.205 against 0.056 together);
  on the other eleven ours is the lower one (0.040 against 0.053).
  How she gets there (own count, work/h20_pass.py and h20_count.py, all 745 main and v31 games, 0 errors; bars F38_entry saved 09:15 and F38_pearl saved 10:03, both before the pass was run).
  Chance = a queen turn that starts on a tile with three or more open sides and has a narrow tile next to it. Entered = she ends that turn on a narrow tile. Free layouts, r0-200.
  Entry per chance: main ours 0.307 (1,498 of 4,885), theirs 0.255 (1,249 of 4,908): 1.21 times. v31 0.315 (1,991 of 6,318) against 0.235 (1,328 of 5,649): 1.34 times.
  main slices: earlier half 1.29, later half 1.18; opponents 1700-1899 1.33, 1900-2099 1.13; r0-100 1.29, r101-200 1.07 (v31 1.35 and 1.30). Without Portals 1.22 and 1.35.
  So with a narrow tile next to her she steps in a fifth to a third more often than their queens. In r101-200 on main, the window of the deaths, entering is level (0.306 against 0.287).
  What differs there is the stay. Queen turns per stay on narrow tiles, stays begun in r101-200: main 2.05 against 1.29 (526 and 489 stays), v31 1.75 against 1.51. Stays that end in her death (any cause): main 47 of 526 against 23 of 489; v31 52 of 539 against 40 of 472.
  And where she lives, on the layouts of limit (3). Number of chances, ours against theirs, both codes, r0-200: Maze 1,047 against 497; Prisoners Dilemma 1 639 against 93; Prisoners Dilemma 2 414 against 34; weakhold 1,262 against 1,107 (entry rate 0.52 against 0.32).
  She spends her turns next to the passages there; their queens are somewhere else. On the Prisoners Dilemma layouts a stay lasts one turn (652 entries, 1.05 turns a stay, 12 deaths): she steps in and out of the same narrow tile.
  On Portals a stay lasts 4.2 turns against 1.5 and 37 of 79 stays end in her death (theirs 10 of 121): the small room of F23.
  Pearls (bar F38_pearl, FAILED on both parts). (a) Entries that land on a tile that held a pearl at the turn start: main 173 of 1,498 (0.12), v31 214 of 1,991 (0.11); their queens 0.09 and 0.13. I had claimed half.
  (b) With a pearl on a free narrow neighbour she enters in 0.342 of chances against their 0.324 (main, 1.06 times) and in 0.318 against 0.371 (v31, 0.86 times).
  So pearls do not draw her into passages: nine entries in ten are onto an empty narrow tile, and she takes a passage pearl no more often than their queens do.
  Seen after the count, not under a bar: in r101-200 alone she does take the passage pearl more often (main 77 of 194 against 50 of 197, v31 91 of 216 against 53 of 205); those are 13 percent of her entries in that window.
  Per chance she enters about as often as a step picked blindly would (0.31, with three or four ways to go). Their queens are a little below that (0.24 to 0.25).
  Verifier, 10:40 KST (on the entry, pearl and stay counts of run 1000): holds in part. All counts recount exactly. Stays: longer for main in every slice (side swap by game 0 of 10,000; without Maze and weakhold 1.75 against 1.22 turns);
  on v31 within chance by game and gone without Maze and weakhold. One turn long: 0.59 of our stays against 0.87 of theirs on main. Entries: 1.21 and 1.34 are right but are a layout mix. Our queen has twice the chances of theirs on Maze, weakhold
  and the two Prisoners Dilemma layouts; on the other twelve she enters less often than theirs on main (0.87) and as often on v31 (0.99); with the mix held equal 1.04 and 1.10. Where a wider tile was free too, main enters as often as theirs (1.04; 0.83 in r101-200).
  A gap inside one layout exists on weakhold (1.5 to 1.7), Trauma and Tower Defense. Pearls: one entry in nine is right, but "no more often than theirs" holds only for r0-200 pooled; in r101-200 a pearl on a free narrow neighbour
  pulls our queen in 1.6 times as often as theirs (both codes 168 of 410 against 103 of 402; 141 of 10,000 by game), on one entry in eight. All accepted: my line "she does not go in for pearls" is right for most entries and wrong as a flat statement for r101-200.
  Why her stays are longer (bar F38_stay, saved 10:21 before the count; own count, work/h22_pass.py, 765 games, 0 errors; its stay numbers equal work/h20 on the 745 older games). FAILED.
  Stays begun in r101-200 that last 3 or more turn starts, free layouts without Portals, both codes: ours 192, theirs 55. A body of another dragon of her team on a tile next to her head (through an open side) at some turn start of the stay:
  ours 20 of 192 (0.10), theirs 1 of 55. I had claimed at least half; the line was 0.35. So our own dragons are not what keeps her in passages. They are what kills her there when they are present: 19 of those 20 stays end in her death (F37).
  An enemy head within 3 columns and rows at some turn of the stay: 77 of 192 and 18 of 55 (died 22 and 8). A dead-end tile: 13 and 4 (all died). None of the three: 98 and 36.
  What the count showed instead, then put under a bar (F38_long, saved 11:08 after seeing the pooled, per-code and Maze-and-weakhold figures, before any half or band). Share of stays begun in r101-200 that last 3 or more turn starts, ours against theirs:
  main 0.217 (117 of 538) against 0.037 (18 of 485), 5.9 times. Earlier half 16 of 174 against 1 of 101 (9.3 times); later half 101 of 364 against 17 of 384 (6.3); opponents 1700-1899 64 of 231 against 6 of 169 (7.8); 1900-2099 53 of 295 against 12 of 289 (4.3).
  v31 75 of 533 against 37 of 432 (1.64). The line was 1.5 in each: passed, v31 narrowly. One opponent left out (main): 4.4 to 7.5. One layout left out (main): 5.1 to 8.1.
  Maze, weakhold and Tower Defense hold 165 of our 192 long stays. Inside them, both codes: Maze 87 of 328 against 17 of 104; weakhold 39 of 122 against 14 of 162; Tower Defense 39 of 86 against 16 of 91.
  Without the three: main 9 of 236 against 4 of 317 (3.0 times, few) and v31 18 of 299 against 4 of 243. Games with at least one long stay begun in r101-200: ours 33 of 195 queens alive at r100, theirs 11 of 176 (main); 40 of 206 against 16 of 192 (v31).
  Second line of the bar: a long stay ends in her death in 38 of 192 (ours, 0.20) and 8 of 55 (theirs, 0.15), 1.36 times, under the 1.5 I set. So the passage is not shown to be more deadly for her than for their queens; she is in it more often.
  All rounds, main: long stays 372 against 154; her death ends 45 of ours (19 wall, 11 own body, 12 rammed, 3 another body) and 24 of theirs. Per 1,000 queen turns inside long stays: 23.7 (45 in 1,898 turns) against 24.1 (24 in 996).
  Over all her turns it is 3.9 (223 deaths in 57,905). So a turn inside a long passage is about six times as dangerous as an average turn for either queen, and ours spends twice the share of her turns there (0.033 against 0.016).
  Of our 223 queen deaths on main (free layouts without Portals) 45 end such a walk, theirs 24 of 221; we lost 16 of those 45 games. Cost in games: not shown.
  v31, all rounds: 318 long stays against 248, 45 deaths against 38, 28.0 against 24.6 per 1,000 turns inside. Outside r101-200 v31 goes the other way (r201-300: 21 of 173 against 42 of 236), so this is a finding about main.
  main by window, ours against theirs: r0-100 157 of 1,055 against 82 of 804 (1.5 times); r101-200 as above (5.9); r201-300 54 of 257 against 17 of 340 (4.2); r301 on 44 of 225 against 37 of 345 (1.8).
  New games (bar F38_new_games, after battle 1289717; 30 main games on free layouts needed, now met; own count, work/h22_pass.py): 34 games. Our queen is on a narrow tile in 0.064 of her turns in r0-200 (283 of 4,442), theirs in 0.044 (185 of 4,187):
  1.44 times; the line was 1.15. Wall or own-body deaths from a turn that started on a narrow tile: ours 4 (of 5), theirs 2 (of 2). Holds; the deaths are too few to say more. As the verifier found, five layouts carry the share:
  without Maze, weakhold, Portals and the two Prisoners Dilemma layouts the 27 new games give 0.026 against 0.042. Totals main (307 free games): 0.075 against 0.052 in r0-200; wall or own-body queen deaths 70 against 34, from a narrow tile 64 and 32.
  Verifier, 11:39 KST (on the long-passage count of run 1100): holds in part. Every count recounts exactly. The main ratio (5.9 times) holds in both halves and bands, by game (0 of 10,000 side swaps), with the layout mix held (5.1) and is not sprinting.
  Limits: 108 of the 117 long stays are on Maze, weakhold and Tower Defense, in 33 of 293 games; three games hold 42; Tower Defense on main is two games against one opponent (30 of 37) and v31 runs the other way there;
  on Maze the jump from v31 to main is THEIR queens (16 of 63 long, then 1 of 41), not ours (41 of 152, 46 of 176). Equal death per turn inside long stays holds on main with a wide interval (0.60 to 1.61).
  Own dragons: beside her in only 20 of 192 long stays, but those are 19 of her 38 deaths in long stays: one of our dragons (her child in 5) is on her last free tile at the turn start she dies in.
  Over all rounds and stay lengths that is 80 of our queen deaths (of 496, both codes) against 28 of theirs (of 486): wall 53, own body 20, other dragon body 7. All accepted.
  The mouth (bar F38_mouth, saved 11:16 before the pass existed; own count, work/h24_pass.py, all 785 main and v31 games, 0 errors). Mouth turn = her last turn start on a wider tile before a stay. Another way = a neighbour through an open side that is not narrow and holds no dragon body (her own tail counts as blocked).
  FAILED. main, free layouts without Portals, her 122 long stays begun in r101-200: she had another way at 45 mouth turns (0.37; the line was 0.50, I had claimed 0.70). v31: 33 of 75 (0.44). Halves 7 of 16 and 38 of 106; bands 24 of 64 and 21 of 56; Maze 15 of 50, weakhold 6 of 25, Tower Defense 15 of 37.
  Their queens at the mouth of their long stays: 10 of 28 (main), 10 of 37 (v31): the same. At the mouth of short stays (1 or 2 turns): ours 286 of 440 (0.65), theirs 387 of 508 (0.76); v31 0.64 and 0.75.
  At 77 of the 122 mouths no wider neighbour was free; the commonest mouth is a tile with three open sides whose three neighbours are all narrow (34 of 122): a junction inside passages, not the edge of open water. Long stays that end in her death, all rounds: another way at the mouth in 19 of 48 (main) and 24 of 45 (v31).
  Second line, not wrong: an enemy head within 3 columns and rows at the mouth turn in 32 of 122 (0.26; the line was 0.60). She is not fleeing into passages.
  So in two long walks of three she was already inside passage country and had no wider tile to step to. A cost on stepping into a passage at the mouth can reach at most the 45 (main) where she had a choice.
  New games (same pass): stays begun in r101-200 on the 20 games of this hour: ours 5 long of 24, theirs 10 long of 51 (0.21 against 0.20): no gap this hour. Bar F38_long_new needs 150 stays; 24 so far. Totals main: 122 of 562 against 28 of 536 (5.9 times before this hour, 4.2 now).
  New games, run 1500 (bar F38_new_games_2, after battle 1298211; 30 main games on free layouts needed, now met; own count, work/h25_pass.py, field qt, same rule as work/h22): 64 games. Her share of turn starts on narrow tiles in r0-200: ours 0.0795 (640 of 8,053), theirs 0.0852 (733 of 8,606): 0.93 times. The line was 1.15. The bar FIRED: weakened.
  Long stays in r101-200 (bar F38_long_new, 150 stays of ours needed, 115 so far): ours 20 of 115 (0.17), theirs 31 of 259 (0.12): 1.45 times; the line is 2 times, so at present this would weaken it too.
  Her deaths on a wall or her own body in r101-200 go on (F37: 6 of 34 against 1 of 34), so the deaths hold and the "she spends more time in passages" part does not hold on new games. The verifier count of own dragons on her last free tile (80 of 496 against 28 of 486) was not recounted.
  Verifier, 12:24 KST (on the mouth count of run 1200): holds in part. Counts exact. A free wider neighbour at 45 of 122 mouths of long stays on main (0.29 to 0.47); v31 33 of 75, not shown to be under half. Most of these mouths are junctions inside the corridors, not entrances (68 of 122 long stays begin one turn start after her previous stay);
  where she comes in after four or more turn starts on wider tiles she had a free wider neighbour in 19 of 27 (main) and 22 of 28 (v31), so the count does not show that she is forced in. Their queens show the same shares. Given both a free wider and a free narrow neighbour the two queens take the narrow tile equally often (0.24 against 0.27). Accepted.
would be wrong if: (saved 09:08, before the pass was written; seen before it: the one-free-tile shares on Maze and weakhold from the F37 base-rate count, 0.26 against 0.11, and the corridor shares in maps.json)
  (a) the narrow-tile ratio under 1.25 in any of main Maze, main weakhold, v31 Maze, v31 weakhold (claimed 1.5). Passed: 4.3, 2.4, 2.1, 3.7.
  (b) the pooled ratio on Tower Defense, Trauma and Devil under 1.1 (claimed 1.25). FAILED: 0.73. So it says nothing, by corridor share, about a map nobody has seen.
  (c) under 50 percent of our wall or own-body deaths in r101-200 start on a narrow tile (claimed 70), or the per-turn rate there under 1.5 times theirs with both codes pooled (claimed 2). Passed: 95 percent; 2.9 times (main 6.6, v31 2.3).
  (F38_entry, saved 09:15 before the pass) per chance ours ends the turn on a narrow tile under 1.1 times as often as theirs on main or v31 (claimed 1.3). Not wrong: 1.21 on main (between the lines), 1.34 on v31.
  (F38_pearl, saved 10:03 before the pass was run) (a) under 35 percent of her entries land on a pearl tile on either code (claimed half). FAILED: 12 and 11 percent.
  (b) with a pearl on a free narrow neighbour she enters under 1.1 times as often as theirs on either code. FAILED: 1.06 and 0.86.
  (F38_new_games) not counted: 17 new main games on free layouts since the bar, 30 needed.
  (F38_stay, saved 10:21) of our stays of 3 or more turns begun in r101-200 under 0.35 have a body of another dragon of ours beside her head at some turn, or the two sides are within 10 points. FAILED: 0.10 against 0.02.
  (F38_long, saved 11:08) the share of stays that last 3 or more turns, ours over theirs, under 1.5 in main half 1, half 2, 1700-1899, 1900-2099 or on v31. Passed: 9.3, 6.3, 7.8, 4.3 and 1.64. Second line: her death rate per long stay above 1.5 times theirs. Not met: 1.36.
  (F38_new_games) her share of turns on narrow tiles in r0-200 under 1.15 times theirs on 30 new main games, or her wall and own-body deaths from narrow tiles not above theirs. Passed: 1.44; 4 against 2.
inferred: Two rare positions make up nearly all of these deaths. One: the queen on a dead-end tile; her own neck fills the only open side, so she is dead whatever she plays. Two: the queen in a passage one tile wide with one of our own dragons in front of her; neither can pass, and a dragon cannot turn round in such a passage.
  Their queens die of the same two positions; ours gets into them far more often (56 deaths against about 11). This fits the failed F37 base-rate bar: our own dragons are not beside our queen more often in general; they are beside her more often in the one place where it kills.
  Why she is in narrow ways more on some layouts and less on others is not a map property I can name: corridor share fails. Prisoners Dilemma (0.18 and 0.20 against 0.02 and 0.005) looks like a passage next to her spawn, which an unseen map may or may not have.
  In main.cpp the queen look-ahead in score_step() asks for room: last_dead_end, avail under length + QUEEN_ROOM 8, known_room() under length + 2. A blind passage five tiles long passes all three and is still fatal, because she can never come back out of it. For a passage the right question is whether it has a second exit, not how big it is.
  And with QUEEN_ALLY_BLOCK false her room count does not treat a friendly head in the passage as a wall. Both are readings of the code, not tested.
  Updated 11:12. A dragon cannot turn round inside a passage one tile wide, so a long stay is decided at its mouth: she steps in and has to walk to the other end. Their queens are out again on the next turn in nine stays of ten (main opponents); ours goes on in four of ten.
  So the place for a rule is the step INTO a passage, and what it should look at is how far the passage runs before the next tile with three or more open sides. Room is the wrong measure (QUEEN_ROOM counts tiles she can reach, and a long passage has plenty).
  Why main does this far more than v31 from round 101 on is not known. I looked for a queen rule that starts at round 100 and found QUEEN_QUIET_ROUND 100 (it sets queen_game when she has met no enemy by then, which moves feed_round and the leader priority);
  I did not trace whether queen_game changes her steps. A guess only; v31 source is not on disk.
not checked: how she comes to be on the narrow tile (how many turns earlier she entered the passage and what she could see then); whether their queens avoid passages or are simply longer by then; whether the dragon in front was a feeder, a hunter or a new child (her child in 3 of 29 by the verifier);
  the Portals rooms are in the count (F23); cost in games is not shown (won 12 of 23 on main); the ally-beside and dead-end split was seen after the count.
look at: data/online/ladder/1281566/M1281569.replay r100-118 (Maze vs 2014: narrow tile, an own dragon beside her, she dies on her own body at r118; lost with only their queen alive);
  data/online/ladder/1274524/M1274526.replay r130-143 (weakhold vs 1799: dead-end tile, own body at r143; lost with only their queen alive);
  data/online/ladder/1289717/M1289719.replay r100-117 (weakhold vs 2105: wall at r117, length 3; lost on longest dragon 19 against 22).
  data/online/ladder/1297395/M1297397.replay r124-136 (Maze vs 1918, this hour: 13 turns down a passage from r124, ends on a dead-end tile, own body at r136; lost on longest dragon 25 against 55);
  data/online/ladder/1263705/M1263705.replay r117-124 (Tower Defense vs 2022: 8 turns in a passage with an enemy head near, rammed at r124; lost with only their queen alive).
smallest test: three switches, each default off, in the bot own terms. (1) QUEEN_ALLY_BLOCK true: it exists; her room count then closes the tiles next to friendly heads. (2) QUEEN_GIVE_WAY 2: it exists; other dragons pay QUEEN_GIVE_WAY_PENALTY for a destination within 2 tiles of the queen they see.
  These two address the 31 deaths with an own dragon in front. (3) New, for the 25 dead-end deaths (call it QUEEN_NO_BLIND): in score_step() for the queen, when the destination has two or fewer open edges, follow the passage along known edges;
  if it ends in a dead end, or runs out of what she has seen before reaching a tile with three or more open edges, subtract QUEEN_DEAD_PENALTY.
  Local games on Maze, weakhold, Prisoners Dilemma and Portals. Pass mark to write first: queen deaths by wall or own body fall by half (main now 65 in 273 games on free layouts, 0.24 a game), her pearls by r200 do not fall by more than a tenth, wins do not fall.
  Updated 10:14: the entry count changes switch (3). Entering is not for pearls (one entry in nine lands on a pearl) and her scoring looks neutral to how narrow the destination is, so the simplest form is a plain cost:
  for the queen, subtract a penalty (call it QUEEN_NARROW_PENALTY, default 0) from a step whose destination has two or fewer open edges, when another step is not a dead end. No passage needs to be followed for that.
  It costs her at most one pearl in nine entries. Extra line for the pass mark: her share of turns on narrow tiles in r0-200 falls below theirs (now 0.076 against 0.053 on main), and stays begun in r101-200 last under 1.5 turns (now 2.05).
  Updated 11:12: switch (3) restated with the long-stay count. QUEEN_PASSAGE_MAX (new, default 0 = off): in score_step() for the queen, when she stands on a tile with three or more open edges and the destination has two or fewer,
  follow the passage along known edges; if it runs for more than QUEEN_PASSAGE_MAX narrow tiles (try 2) before a tile with three or more open edges, or ends, or leaves what she has seen, subtract QUEEN_DEAD_PENALTY unless every other step is fatal.
  QUEEN_GIVE_WAY 2 and QUEEN_ALLY_BLOCK stay as the answer to the stays with an own dragon in the way (20 stays, 19 deaths); they do not shorten the other 172.
  Local games on Maze, weakhold and Tower Defense (165 of the 192 long stays). Pass mark to write first: stays of 3 or more turns begun in r101-200 fall from 0.22 of her stays to under 0.08; her deaths that end a long stay fall from 45 in 307 games to under 25;
  her pearls by r200 do not fall by more than a tenth (in r101-200 one entry in eight is for a pearl); wins on those layouts do not fall (Maze 18 of 25, weakhold 12 of 21, Tower Defense 7 of 24).
  Updated 12:36: the passage-entry switch (QUEEN_PASSAGE_MAX) is withdrawn as the first test: at the mouth she had a wider way in only 0.37 of long walks. Two things are left, in this order.
  (1) The own-dragon cases, now counted by the verifier: 80 of our 496 queen deaths (both codes) have one of our dragons on her last free tile, against 28 of theirs. QUEEN_GIVE_WAY (0 in main.cpp, penalty QUEEN_GIVE_WAY_PENALTY 3000 for a non-queen stepping within that many tiles of her) set to 1 or 2 is the existing switch for it. Local games on passage-heavy layouts (corridor_share high: Maze, weakhold, Tower Defense or any like them).
  Pass mark to write first: queen deaths by wall, own body or own-team body per game do not rise and fall by a third; pearls by r100 do not fall by more than 5 percent.
  (2) No change yet, count first (bar F38_region in state.json): how much of her time in r101-200 she spends at junctions whose neighbours are all narrow, against theirs on the same layouts. If she lives in passage country and they do not, the place is the queen step score after QUEEN_QUIET_ROUND 100, not a mouth rule.

### F34 On big layouts where the queen can leave spawn, a game that ends with one queen alive ends with theirs alive
status: candidate (bar passed on main and v31 but on 13 and 16 endings; F35 shows it is mostly the full-game effect, which every big-layout game is)      first seen: 7 Oct 08:06 KST run 20261007-0800   last tested: 7 Oct 09:12 KST (totals only)
measured: rows.jsonl, free big layouts (Around UNSW, Australia, Islands). One-queen endings, theirs against ours: main 10 against 3, v31 14 against 2. Other free layouts: 35 against 35 and 47 against 45 (most of ours there are eliminations, see F35).
  By layout, main then v31: Around UNSW 6-3 and 7-0; Australia 3-0 and 4-2; Islands 1-0 and 3-0. main bands: 1700-1899 4-1; 1900-2099 2-2; 2100+ 4-0.
  Our queen rammed (standing victim) in 38 of 52 main games and 58 of 71 v31 games there; on other free layouts 79 of 203 and 113 of 291. Their queen: 30 of 52 and 32 of 71; 96 of 203 and 132 of 291.
  Rams on the queen per 1,000 queen turns in r0-200 (work/h10-shard files, 43 main and 71 v31 games on these layouts): ours 4.33 (25 rams) against theirs 2.24 (15) on main; 3.81 (38) against 2.24 (23) on v31. Other free layouts: 2.28 against 2.86; 2.72 against 3.24.
  Follow-up bar F34b (exposure) passed by the letter and explains little: our queen starts 0.036 of her turns in r0-200 inside the full reach of an enemy head, theirs 0.023 (main; v31 0.029 against 0.023), but Australia is the other way round in both codes
  and exposure to heads of length 4 or less, the ones that ram, is level (0.015 against 0.016 in both codes).
  New, run 0900: 3 more main games on free big layouts (Australia, Islands, Around UNSW), all ended with both queens dead and all lost. Totals main: only theirs 10, only ours 3, both dead 42 in 55 games (16 won). No new one-queen ending, so the bar is not re-tested.
would be wrong if: (08:06, before the count; the table with the sealed-queen layouts in it had been seen) their share of one-queen endings on free big layouts under 0.60 on main or v31; other free layouts within 10 points; a layout with ours ahead in both codes;
  or holding in only one main band (5 endings needed). Passed: 0.77 and 0.88 against 0.50 and 0.51. The band clause is undecided (1900-2099 has 4 endings).
  (F34b, 08:07) our exposed share under 1.15 times theirs on main or v31. Not wrong: 1.54 and 1.26 (claimed 1.3).
inferred: Size is not the cause by itself. Big layouts are where no side is wiped out, so every game there is a full game, and in full games the lone-queen race goes against us on every layout (F35).
  What is special about big layouts is the ram rate on our queen before round 200: nearly twice theirs per queen turn in both codes, while elsewhere theirs is rammed a little more than ours.
not checked: 25 against 15 rams on main is inside chance by itself (v31 38 against 23; both together about 1 in 250). Three layouts cannot show a property.
look at: data/online/ladder/1285561/M1285561.replay r200-222 (Australia vs 1791, new: ahead 98 to 77 at r100, queen rammed at r222 at length 2, their queen ends 18 long, lost on the queen rule with the longer longest dragon, 29 against 18);
  data/online/ladder/1271164/M1271166.replay r165-172 (Australia vs 1785).
smallest test: none of its own; the F35 test (QUEEN_GUARD_CELLS 1200) is aimed at exactly these layouts.

### F13 In a quarter of our games we hold the only living queen and then lose her, alone; on main her own last step could not have saved her
status: confirmed (verifier 03:43, 04:43 and 05:47); its sentence that both sides lose a lone queen equally often stands over all games (verifier 08:40 on F35), while in level games ours dies about three times as fast (F35)      first seen: 7 Oct 03:13 KST   last tested: 7 Oct 18:20 KST (rows.jsonl, new games)
measured: Free layouts (queen can leave spawn), games where their queen dies in an earlier round than ours.
  main: 72 games (71 last hour plus 1 new, which we won with her alive). Our queen dies later in 47: we win 26 of those. She survives in 25: we win 25. v31: 159 games, 112 die later (45 won), 47 survive (47 won).
  The verifier recounted every figure and narrowed the claim, and I accept all three points: winning when she survives is the queen rule itself (mirror: 0 of 31); their lone queen dies just as often
  (60 of 91 main, 121 of 182 v31), so two in three is how often any lone queen dies; "about half lost" is a 1900-2099 figure (17 of 33 won; 9 of 12 against 1700-1899).
  What stands: in 47 of 193 main games on free layouts (180 when the verifier counted) we had the queen lead and lost her; 21 of those games were lost; 30 of the 47 by an enemy dragon moving into her head.
  A queen's death rate per round roughly doubles once the other queen is dead, on both sides (verifier).
  Last hour (04:08 KST), own count (work/h4_pass.py; bars from 03:24 KST), the rams on our lone queen:
  - She is alone. Fewer than 2 of our other heads within 5 tiles of her at the ram: main 27 of 30 (none at all in 18), v31 57 of 75 (none in 35). Bands: main b 7 of 8, c 18 of 20; v31 b 27 of 40, c 23 of 25.
    We had a median of 14 other dragons alive at those moments (10 or more in 17 of the 30 rams, fewer than 5 in 8). Their lone queen when we ram her is just as alone (35 of 42, 46 of 58).
  - A step beyond the rammer's free steps existed, which is not a way out (see the verifier below). At her last turn before the ram a legal single step ending beyond the rammer's free steps existed in 17 of 27 main rams (3 of the 30 had a rammer born after her last turn) and 59 of 75 on v31.
    On the stricter reading (a step ending farther away than the ram actually travelled) it is 11 of 27 and 43 of 75: 13 of 27 and 38 of 75 rams were paid sprints (the rammer spent length for extra steps).
  - The rammer was in view. It was inside the 7 by 7 square around her head at her last turn in 23 of 27 (main) and 66 of 75 (v31). She always moves before it in the round (the ram is in the same round as her last turn in 252 of 253 rams on our queen).
  - What she did, all rams on our queen, lone or not: her last step took her from outside the rammer's full reach (free steps plus length it can pay, the bot's own enemy_reach) to inside it in 41 of 83 main rams and 113 of 170 on v31;
    in 36 and 50 she was already inside it and did not get out. Their queens do the same (61 of 90 and 116 of 162 stepped in).
  - Lengths at the ram (our lone queen, main): queen 2 (21 times), 3 (6); rammer 3 (18 times), 2 (5).
  Verifier, 04:43 KST: every count of last hour reproduced. The "alone" half stands (27 of 30 main, 57 of 75 v31, against 0.58 of all her turns in that state). The "way out" half is not a missed way out:
  in 15 of the 17 main rams (43 of 59 on v31) she did end beyond the free steps and was rammed anyway, because the rammer paid length for extra steps (it dies in the ram either way).
  New this hour, own count (work/h9_pass.py; bar from 04:21 KST, details fixed 05:04 before counting): a legal step ending beyond the full reach (free steps plus all the length it can pay, ceil(L/4) + L - 2)
  of every enemy head within 6 tiles of her existed in 5 of 28 rams on our lone queen on main (18 percent) and 33 of 75 on v31 (44 percent). Beyond the free reach of every such head: 15 of 28 and 57 of 75.
  Their lone queen when we ram her: 7 of 42 and 11 of 57. Not lone (the other queen alive): ours 12 of 58 main, 43 of 95 v31.
  Totals now (201 main games on free layouts): their queen died first in 73; ours died later in 48 (26 won, 22 lost; 31 of the 48 as the standing victim of a ram); she survived in 25 (25 won).
  New games since the bar: 2 (one survived and won; one, weakhold vs 2140, rammed at r166 with 2 friends within 5 tiles and one legal step, lost).
  Verifier, 05:47 KST: the safe-step count reproduces (5 of 28). On main she had one legal step or none in 14 of the 28 rams and no step beyond the rammer's own full reach in 19. Its limits, accepted: the measure is the strict one
  (against what the rammer really did 11 of 28 had a farther step); it is a main result (v31 0.44) and their lone queen on main is the same (7 of 42); the base rate on turns without a ram is not measured.
  Re-count this hour with the 20 new games (work/h9_pass.py): rams on our lone queen on main 34 (31 with a board): a step safe from every full reach in 5, fewer than 2 friends within 5 tiles in 27, one legal step or none in 16.
  Totals now (217 main games on free layouts): their queen died first in 81; ours died later in 54 (31 won, 23 lost; 34 as the standing victim of a ram); she survived in 27 (27 won). All 40 main games that ended with only their queen alive were lost.
  New games since the bar: 10 in which their queen died first; ours died later in 7 (5 of those won). The bar needs 15.
  New this hour (work/h4-shard files, games up to battle 1270027; the pooled figure was seen in run 0400 as 'toward the rammer'): in rams on our queen, lone or not, her last step shortened the path to the rammer
  in 65 of 83 (main) and 152 of 170 (v31). What the rammer then does is in F24: half or more of the rams are paid sprints.
  Re-test this hour (rows.jsonl): 23 new main games since the bar in which their queen died first (15 needed); ours died later in 13 (57 percent; 8 of those won). The bar (under 40 percent) is not reached: holds.
  Totals now (241 main games on free layouts): their queen died first in 94; ours died later in 60 (34 won, 26 lost; 37 as the standing victim of a ram); she survived in 34 (34 won). All 42 main games that ended with only their queen alive were lost.
  The lone-queen ram counts (alone, safe step) were not re-counted this hour: the h9 pass was not rerun.
  Re-count this hour (rows.jsonl): 255 main games on free layouts. Their queen died first in 102; ours died later in 64 (38 won, 26 lost; 37 as the standing victim of a ram); she survived in 38 (38 won). All 45 main games that ended with only their queen alive were lost.
  New games since the bar F13_new_games_2 (after battle 1281566): 8 in which their queen died first; ours died later in 4 (all 4 won, three by elimination). The bar needs 15.
  Correction this hour (F35): the line above that their lone queen dies just as often (two in three for any lone queen) is true per game and misleading. 30 of our 38 surviving lone queens are in games we ended early by elimination, where the game stopped before she was tested.
  Per turn spent as the only queen (all games, work/h10-shard files) ours dies 1.33 times as fast as theirs on main and 1.92 times on v31; in games that reach round 500 she is alive at the end in 8 of 43 against their 32 of 80.
  New games, run 0900 (bar F13_new_games_2, after battle 1281566; 15 needed): 18 main games in which their queen died first; ours died later in 10 (56 percent). The line was 40 percent: holds. All endings, main free layouts now: we held the only queen in 112 of 273 games and lost her in 70.
  New games, run 1000 (bar F13_new_games_3, after battle 1289717; 15 needed): 7 main games on free layouts in which their queen died first; ours died later in 3; 4 won. Too few. Totals main: 119 such games, ours died later in 73, 87 won.
  New games, run 1100 (bar F13_new_games_3, after battle 1289717; 15 needed, now met): 15 main games on free layouts in which their queen died first; ours died later in 8 (0.53); 10 won. The line was under 40 percent: holds. Totals main: 127 such games, ours died later in 78, 93 won.
  New games, run 1200 (bar F13_new_games_4, after battle 1298211; 15 needed): 3 main games on free layouts in which their queen died first; ours died later in 1.
  New games, run 1500 (bar F13_new_games_4, after battle 1298211; 15 needed, now met): 24 main games on free layouts in which their queen died first; ours died later in 17 (0.71). The line was 40 percent: holds. All main: 95 of 151.
  New games, run 1800 (bar F13_new_games_5, after battle 1316833; 15 needed, now met): 24 main games on free layouts in which their queen died first; ours died later in 18 (0.75); 15 won. The line was 40 percent: holds. All main: 113 of 175.
would be wrong if: (03:13) our queen dies later in under 40 percent of these games on main or v31, or we win 75 percent or more of the games in which she dies later. Passed, recounted.
  (03:24, counted 04:08) F13_ram: under 60 percent of the rams have fewer than 2 friends within 5 tiles. Passed, recounted: 90 and 76 percent.
  F13_escape: an escaping step (beyond free steps) existed in under half. Passed as written, but the verifier showed it does not mean what I read into it (she had taken that step and was rammed by a paid sprint).
  (04:21, counted 05:09) F13_safe_step: wrong if a step beyond the full reach of every enemy head within 6 existed in under 40 percent on main or v31. FAILED on main (18 percent); v31 44 percent.
  (new games) weakened if, once 15 new theirs-first games exist, ours dies later in under 40 percent. 2 so far, 1 died later.
inferred: One opening is left, not two. Nobody guards her: QUEEN_DEFEND_RADIUS is 0 and QUEEN_GUARD_CELLS is 0, so with a median of 14 other dragons alive none stays within 5 tiles.
  Last hour's second opening ("she walks into reach and could have stepped away") does not hold on main: in 4 rams of 5 no single step was safe from a rammer willing to pay its whole length.
  On v31 it held in 44 percent; my reading is that QUEEN_SAFETY on main already takes the safe step when there is one, so what is left on main are the positions with none.
  The fix is earlier than her last step: bodies between her and enemy heads, or her distance from enemy dragons several turns before. Opponents' queens die the same way (F9), but see F24: the stronger the opponent, the more often it is ours.
not checked: how far ahead a safe position existed (two or three turns before the ram); whether she knew their queen was dead (qh_foe_dead()). 22 losses is an upper limit on what could be gained.
look at: data/online/ladder/1250697/M1250697.replay r270-282 (Default vs 1952: their queen died r79; our lone queen, length 2, no friend within 5, three legal steps all out of free reach, she steps to distance 2 of a length-3 rammer);
  data/online/ladder/1256138/M1256140.replay r26-69 (Default vs 2021: their queen dies r26, ours rammed r69 at length 2, then eliminated);
  data/online/ladder/1255595/M1255595.replay r87-141 (Islands vs 2020: rammed with 5 friends near, one legal step, no way out: the other kind).
smallest test: a default-off switch, say LONE_QUEEN_GUARD, active once qh_foe_dead() is true and our queen is alive: QUEEN_DEFEND_RADIUS 5 so that a few small dragons stay by her (F24 argues for trying it from round 0 as a second arm).
  The "refuse a tile inside enemy_reach()" half proposed last hour is dropped: on main a tile outside it existed in 5 of 28 rams.
  Pass mark to write before any local test: of games where their queen dies first, ours alive at r500 rises from about 1 in 3 to 1 in 2, and wins in those games do not fall.

### F24 Against 2100+ teams our queen is rammed in seven games of ten and almost never alive at the end; they do not stand nearer to her, they pay length to sprint into her
status: confirmed for the top band in both codes (rammed share, alive at the end); the paid-sprint part holds on v31 only (verifier 06:53: holds in part); the rise with rating is main only (candidate)      first seen: 7 Oct 05:11 KST run 20261007-0500   last tested: 7 Oct 18:20 KST (rows.jsonl, new games)
measured: rows.jsonl, free layouts. Share of games in which our queen dies as the standing victim of an enemy ram (head-on, their dragon moved), by opponent rating 1700-1899 / 1900-2099 / 2100+:
  main 25 of 69 (0.36), 58 of 119 (0.49), 9 of 13 (0.69). v31 73 of 186 (0.39), 65 of 120 (0.54), 26 of 43 (0.60). (v31 against teams under 1700: 8 of 13.)
  Their queen rammed by us, same bands: main 32, 60, 2 (0.46, 0.50, 0.15); v31 96, 50, 17 (0.52, 0.42, 0.40). So against 1700-1899 we ram their queen more than they ram ours; against 2100+ it is 9 against 2 and 26 against 17.
  Our queen alive at the end: main 20 of 69, 25 of 119, 0 of 13; v31 44 of 186, 15 of 120, 2 of 43. Their queen alive at the end: main 0.26, 0.26, 0.62 (8 of 13); v31 0.18, 0.25, 0.28.
  Which queen dies first (bar F21 b, written before the count, passed): ours first in 0.49 of first-death games against 1700-1899 on v31 and 0.675 against 2100+ (27 against 13); main 2100+ 10 against 3.
  Chance: v31 0.39 against 0.60 is about 2.5 standard errors; main 0.36 against 0.69 about 2.2 with 13 games. main 2100+ is two opponents (8 and 5 games); v31 2100+ is eight opponents.
  When she is rammed (own count, work/h9_pass.py, bar saved 05:17 KST and counted 05:19): she has fewer than 2 friends within 5 tiles at her last turn in 0.80, 0.78, 6 of 7 of the rams on main by band and 0.65, 0.83, 0.77 on v31.
  Enemy heads within 6 tiles of her: median 2, 2, 3 on main and 2, 2, 3 on v31, but the means are level (v31 2.75, 2.45, 2.73). The rammer is 3 long (median) in every band.
  So against the top band she is no more crowded and no more alone than against the others; it just happens more often.
  Verifier, 05:47 KST: all counts equal. Holds: on main the rammed share rises step by step with rating (battle shuffles reach it in 6 of 4,000), and against 2100+ she is alive at the end in 0 of 13 and 2 of 43.
  Does not hold as worded: on v31 there is no rise, only one low cell (under 1800 0.53, 1800-1899 0.32, 1900 and over 0.56). main 2100+ was two opponents in three battles and cannot be told from 1900-2099 (p 0.24). I accept both.
  Totals now, main, free layouts, by band: our queen rammed 28 of 77 (0.36), 61 of 123 (0.50), 12 of 17 (0.71); alive at the end 21, 25, 1. Their queen rammed 35, 61, 4; alive at the end 19, 32, 9. main 2100+ is now three opponents in four battles.
  New games since the bar (after battle 1271874, opponents 1900+, free layouts): 8 games, our queen rammed in 6. The bar needs 30.
  New this hour, bar F24_reach FAILED (own count, work/h10_pass.py, 665 games; exposed turn = her turn starts with an enemy head within its full reach of her, min(12, ceil(L/4) + L - 2) path steps):
  share of our queen's turns in r0-200 that are exposed, by band: v31 0.0162 (390 of 24,107 turns), 0.0204, 0.0102 (45 of 4,415); main 0.0118, 0.0174, 0.0141 (31 of 2,194). Against 2100+ it is 0.63 times the 1700-1899 share on v31; the bar asked 1.3.
  Rams on her by r200 per game still rise: v31 0.27, 0.43, 0.53; main 0.32, 0.36, 0.53. Their queen starts a turn inside the full reach of one of our heads in 0.015, 0.016, 0.028 of her turns (v31) and 0.017, 0.017, 0.019 (main).
  New this hour, bar F24_sprint PASSED on v31 (work/h4-shard files, games up to battle 1270027; paid = the ram covered more path steps than the rammer's free steps, so it gave up length to reach her):
  paid share of the rams on our queen, by band: v31 31 of 72 (0.43), 33 of 64 (0.52), 20 of 26 (0.77); main 11 of 23, 30 of 54, 3 of 6 (too few against 2100+). Our rams on their queen: v31 0.40, 0.57, 0.41; main 0.37, 0.28.
  Against 2100+ on v31 the mean path distance from the rammer to her is 3.2 at her last turn and 2.2 after her step; she stepped closer in 26 of 26. Chance: 0.77 against 0.43 is about 3 standard errors; the 26 rams are from 8 opponents.
  New this hour, bar F27 FAILED: a ram that is one step away is taken by both sides about nine times in ten. We do not hold back; see F27.
  Verifier, 06:53 KST: all counts reproduce. On v31 both halves hold: her turns inside enemy reach are not more frequent against 2100+ (difference -0.015 to +0.004) and the paid share is higher (20 of 26 against 31 of 72), over all 8 opponents,
  and not because the rammers are longer (inside length 3-4 it is 16 of 16 against 53 of 70). On main it does not show: with every game up to battle 1276407 the paid share is 14 of 28, 32 of 57, 4 of 10 by band (three opponents in the top cell).
  Two cautions it adds, both accepted: reach is counted at her turn start and the rammer was inside it then in only 4 of 26 rams at 2100+ (she steps into it; rams per exposed turn 0.13, 0.19, 0.51);
  her last step shortening the path is the usual shape of a ram on either side (their queens: 155 of 162 before our rams).
  My bar F24_sprint_main (paid share on main against 1900+ at least 0.50 on 60 or more rams; wrong under 0.45) is met by the verifier's count, 36 of 67 (0.54), which I saw before counting myself; the 2100+ half (4 of 10) is below the 0.50 line and needs 15 rams.
  Totals now, main, free layouts, by band: our queen rammed 35 of 91 (0.38), 65 of 133 (0.49), 12 of 17 (0.71); alive at the end 25, 28, 1. Their queen rammed 46, 67, 4; alive at the end 19, 34, 9. No new game against 2100+ this hour.
  New games since the bar (after battle 1271874, opponents 1900+, free layouts): 18 games, our queen rammed in 10 (0.56). The bar needs 30.
  Re-counted at 07:35 after a second rerun of work/h4_pass.py with a longer limit (all 690 games). Paid share of the rams on our queen, main, by band: 21 of 35 (0.60), 35 of 61 (0.57), 4 of 10. Against 1900+ together 39 of 71 (0.55):
  the bar F24_sprint_main (at least 0.50; wrong under 0.45) is passed on my own count. The 25 new games: 7 of 7 against 1700-1899 and 3 of 4 against 1900-2099.
  So on main the paid sprint is not a mark of the top band: teams rated 1700-1899 now pay as often as any (0.60). The rise with rating (0.43, 0.52, 0.77) is a v31 fact only. Our own rams on their queen on main: 20 of 45, 19 of 65, 2 of 3.
  Totals now, main, free layouts, by band: our queen rammed 38 of 100 (0.38), 67 of 138 (0.49), 12 of 17 (0.71); alive at the end 27, 30, 1. Their queen rammed 52, 70, 4; alive at the end 21, 35, 9. No game against 2100+ this hour.
  New games since the bar F24_new (after battle 1271874, opponents 1900+, free layouts): 23 games, our queen rammed in 12 (0.52). The bar needs 30.
  Seen this hour beside the F34 count, not under a bar: the layout matters as much as the rating. On free big layouts (Around UNSW, Australia, Islands) our queen dies as the standing victim of a ram in 38 of 52 main games (0.73) and 58 of 71 v31 games (0.82);
  on the other free layouts in 79 of 203 and 113 of 291 (0.39 and 0.39). Their queen: 30 of 52 and 32 of 71 on big, 96 of 203 and 132 of 291 elsewhere. See F34 and F35.
  The paid-sprint and distance counts (work/h4 and h12 passes) were not rerun this hour: 15 new games, none against 2100+, cannot move those bars.
  Totals now (run 0900), main, free layouts, by band: our queen rammed 41 of 105 (0.39), 72 of 148 (0.49), 13 of 20 (0.65); alive at the end 28, 33, 1. Their queen rammed 57, 72, 6; alive at the end 21, 38, 10. main 2100+ is now four opponents in five battles (4 games won of 25).
  Bar F24_new (after battle 1271874, opponents 1900+, free layouts; 30 needed): 36 games, our queen rammed in 18 (0.50). The line was 40 percent: holds. The paid-sprint counts were not rerun (the 2100+ half still has 10 rams on file; this hour added 4 free-layout games against 2105).
  New games, run 1000 (bar F24_new_2, after battle 1289717; 30 needed): 8 main games against 1900+ on free layouts; our queen rammed in 6, theirs in 4. Too few. Totals main against 1900+: ours rammed in 91 of 176 games, theirs in 82.
  No game against 2100+ this hour (still rammed in 13 of 20, alive at the end in 1).
  New games, run 1100 (bar F24_new_2, after battle 1289717; 30 needed): 13 main games against 1900+ on free layouts; our queen rammed in 10, theirs in 7. Too few. Totals main against 1900+: ours rammed in 95 of 181 games, theirs in 85. No game against 2100+ this hour (still rammed in 13 of 20, alive at the end in 1).
  New games, run 1200 (bar F24_new_2, after battle 1289717; 30 needed): 25 main games against 1900+ on free layouts; our queen rammed in 17 (0.68), alive at the end in 3. The line is 40 percent; in line.
  Against 2100+ on free layouts, all main games now: rammed in 18 of 27, alive at the end in 1. The 7 of this hour (against 2474 and 2195): rammed in 5, alive at the end in 0. Sprint counts not rerun.
  New games, run 1500 (bar F24_new_2, after battle 1289717; 30 needed, now met): 53 main games against 1900+ on free layouts; our queen rammed in 35 (0.66), alive at the end in 5. The line was 40 percent: holds.
  All main on free layouts, rammed and alive at the end: 1700-1899 61 of 142 and 36 alive; 1900-2099 92 of 178 and 38 alive; 2100+ 28 of 43 and 1 alive. In the 18 main games in which we were wiped out by round 125 she was rammed in 17, between rounds 24 and 116 (F44).
  New games, run 1800 (bar F24_new_3, after battle 1316833; 30 needed): 24 main games against 1900+ on free layouts; our queen rammed in 10 (0.42), alive at the end in 4; their queen rammed by ours in 13. Not at the count; close to the 40 percent line.
  Totals main against 1900+: ours rammed in 130 of 245 games, theirs in 111. Against 2100+ on free layouts: rammed in 34 of 57, alive at the end in 2.
would be wrong if: no bar was written before these numbers were seen, except F21 b (v31 ours-first share against 2100+ at least 10 points above 1700-1899: passed, 18 points).
  A bar on the survival of THEIR queen, written 05:11 before its count, FAILED: on v31 their queen is alive at the end in 0.28 of games against 2100+ and 0.18 against 1700-1899, 10 points, the bar asked 15.
  So the measured difference is on our queen, not on theirs. Bars for new games are in state.json (F24_new, F24_alone).
inferred: This is the clearest thing so far that separates the top band by measured behaviour: they kill our queen with a ram, 6 to 7 games in 10. Rams as such do not cost us (F8), a ram on the queen does:
  once she is dead only the longest-dragon rule is left, and against 2100+ we have fewer and shorter dragons (F4). F13 says she is alone when it happens and, on main, has no safe step left at that point.
  Added 06:15: the top band does not crowd her; it is readier to pay. The typical ram of theirs: a dragon of length 3 stands 3 path steps from her, outside everything it can reach; she steps to 2; it gives up one segment and makes 2 steps.
  Teams rated 1700-1899 make that move in under half of their rams. So the distance she has to keep from a short enemy head is its full reach plus her own next step, not its free steps. This is measured on v31; main has 6 such rams against 2100+.
not checked: why it happens more often against the top band when the moment itself looks the same: how far their rammers come (paid sprints), and how many of her turns she spends with an enemy head within reach, by band.
  (05:17 bar F24_alone: median enemy heads against 2100+ at least 1 above 1700-1899 on v31: 3 against 2, passed by the median only; alone in at least 60 percent in every band with 15 rams: passed.)
look at: data/online/ladder/1271874/M1271877.replay r160-169 (Around UNSW vs 2140: our queen, length 2, rammed by a dragon of length 10, lost on the queen rule);
  data/online/ladder/1271874/M1271878.replay r160-166 (weakhold vs 2140: rammed with two friends within 5 tiles and one legal step);
  data/online/ladder/1271164/M1271166.replay r165-172 (Australia vs 1785: we led 100 to 71 at r100 and ate more in every window; queen rammed at r172, lost on the queen rule).
smallest test: the same switch as F13 without the lone-queen condition: QUEEN_DEFEND_RADIUS 5 (it is 0) from round 0, default off, so that two or three small dragons stay between her and enemy heads.
  Pass mark to write first, local games against the strongest local opponent: our queen rammed in under 35 percent of games (on the ladder 92 of 201 main games, 46 percent) and wins do not fall.
  Added 06:23 after reading main.cpp: a keep-away rule is already there. With QUEEN_SAFETY the queen marks every cell within ceil(parts/4) + parts - 1 steps of a seen enemy head (full reach plus 1, at most QUEEN_REACH_MAX 8)
  and a step into such a cell costs PENALTY_HEAD_RACE 450 x 0.5 x QS_THREAT_MULT 4.0 = 900 or more for a queen of length 2, more than a pearl is worth (EAT_BONUS 300, TARGET_REWARD 260). So I do not propose a wider margin.
  Two things in that rule could be tested instead, both small: (a) parts is the number of body parts she can see (VISION_RADIUS 3), so a rammer half out of view is rated shorter than it is; count it as at least 3;
  (b) the cost is a score term, so when every step is marked she takes the least marked one; the guard above is the only fix for that case, which is 4 rams in 5 on main (F13).

### F28 From 4 path steps away from a short enemy head our queen steps to 3 more often than their queens do: about a third more often per approach, twice as often per turn; at 3 the main queen is the more careful one
status: confirmed in the narrower wording of the verifier (06:53: holds in part); the distance split was seen after the count, not predicted; not re-counted this hour      first seen: 7 Oct 06:19 KST run 20261007-0600   last tested: 7 Oct 07:31 KST
measured (own count, work/h12_pass.py, 665 games; case = a queen turn start in raw rounds 0-200 on free layouts at which the nearest enemy head of length 6 or less is exactly 3 or 4 path steps from her head,
  kelp and portals respected, dragons ignored; closer = after her turn the path from that enemy head's position to her head is shorter):
  Pooled, distance 3 and 4. main: ours closer in 400 of 2,173 cases (0.184), theirs 279 of 1,847 (0.151): 1.22 times. v31: ours 860 of 3,505 (0.245), theirs 448 of 2,926 (0.153): 1.60 times.
  From distance 4: main ours 316 of 1,025 (0.308), theirs 163 of 970 (0.168). v31 ours 590 of 1,895 (0.311), theirs 220 of 1,358 (0.162).
  From distance 3: main ours 84 of 1,148 (0.073), theirs 116 of 877 (0.132). v31 ours 270 of 1,610 (0.168), theirs 228 of 1,568 (0.145).
  A legal step that does not come closer existed in 94 percent of cases on both sides; with one, main ours closer 0.141, theirs 0.103; v31 0.199 and 0.092. Without one the queen comes closer in 0.85 to 0.94 on either side (132 and 119 cases on main).
  By band, pooled, ours / theirs: main 0.176 / 0.118, 0.189 / 0.172, 0.179 / 0.137; v31 0.227 / 0.151, 0.276 / 0.149, 0.252 / 0.159. Their queens are at 0.15 against every band and both of our codes.
  By game (8 or more cases a side): ours higher in 23 games, lower in 18 (main); 50 against 16 (v31). By layout on main it runs from Autarky 0.12 against 0.16 to weakhold 0.39 against 0.22.
  Verifier, 06:53 KST: all counts reproduce (my denominators include the 1 to 6 turns in which the queen died). The direction at distance 4 holds under every check: resampled by game, battle, opponent or layout the gap stays between +0.09 and +0.20;
  ours is higher on 10 of 11 layouts on main and 13 of 13 on v31, in every band, with only real choices counted. The reversal at distance 3 on main holds too (gap -0.10 to -0.02).
  What does not hold is 'twice as often': counting each run of consecutive turns at 4 steps once (its first turn), ours steps closer in 0.40 against 0.30 on main (p 0.008) and 0.39 against 0.28 on v31. Their queens stay at 4 steps longer (3.1 turns a run against 2.5),
  which doubles the per-turn ratio. Over any turn of a run the main gap is not clear (230 of 418 against 150 of 310, p 0.085). All main cases are from one evening. Accepted.
  New games (counted 07:31 after a second rerun of work/h12_pass.py with a longer limit; all 690 games): 24 main games on free layouts after battle 1276407. From 4 steps ours steps closer in 37 of 119 cases (0.311), theirs in 17 of 127 (0.134).
  In line with the bar (ours at least 0.25, theirs under 0.20); it needs 300 cases a side before it can count against the claim. From 3 steps: ours 19 of 138 (0.138), theirs 20 of 163 (0.123): the main queen was not the more careful one in these games.
  Totals now, from 4 steps: main ours 353 of 1,144 (0.309), theirs 180 of 1,097 (0.164). From 3 steps: main 103 of 1,286 (0.080) against 136 of 1,040 (0.131).
would be wrong if: (06:19, saved under bars_for_next_run before the pass was written) our closer rate is under 1.15 times theirs on main or v31; passes at 1.3 on both. Passed on v31 (1.60); main is between the lines (1.22): undecided.
  The split by distance was listed to be reported, not predicted.
inferred: main.cpp marks cells within full reach plus 1 of a seen head (3 steps for a head of length 3), and the main queen respects that line better than their queens do (from 3 she goes to 2 in 7 percent of turns, they in 13).
  But she walks up to the line twice as often as they do (from 4 to 3 in 31 percent of turns against 17), on main as on v31. At 3 she is one forced step from a paid sprint: in rams on main her last step shortened the path to the rammer
  in 65 of 83 and a fully safe step existed in about 1 in 5 (F13, F24). So the handle that main has not moved since v31 is the approach from 4 to 3, not the step from 3 to 2.
not checked: what she was walking to at distance 4 (a pearl, the loop); whether the enemy head then came for her; cases repeat within a game (a queen can stand 4 away for many turns), so the game count (23 against 18 on main) is the cautious figure.
  The enemy position is frozen at her turn start. The team's QUEEN_MARGIN test (named in data/local/hunter38/result.md) may be this very switch; I have not seen its result.
look at: data/online/ladder/1276407/M1276407.replay r124-155 (Around UNSW vs 2111: from r124 a short enemy head is 4 steps away on most of her turns; rammed at r155 with one legal step);
  data/online/ladder/1275534/M1275537.replay r100-114 (Australia vs 1954: rammed at r114 by a dragon of length 2, one legal step, no friend within 5).
smallest test: a default-off switch that widens the queen's marked zone by one step for short heads (queen_reach plus 1, so a head of length 3 marks 4 steps), with the cost unchanged. Pass mark to write first, local games against a hunting opponent:
  from 4 steps she comes closer in under 20 percent of turns (now 31), rams on our queen per game fall, and her pearls by r100 do not fall by more than a tenth.

### F11 On large layouts we eat a third of the pearls, because their heads are nearer to the pearls and they also take more of the ones they are nearer to
status: confirmed (verifier 03:43 and 04:43: holds, both halves)      first seen: 7 Oct 03:11 KST   last tested: 7 Oct 18:20 KST (rows.jsonl, new games)
measured: Large = 2000 or more open tiles: Around UNSW, Australia, Islands, Schooltime 1 and 2. Share = pearls we ate / pearls both sides ate.
  r101-300: main large 0.340 (55 games; 0.334 on the 51 the verifier recounted), v31 large 0.341 (95 games). Other layouts 0.471 and 0.473. All five large layouts under 0.45 in both codes; every rating band.
  Wins on large layouts: main 22 of 55, v31 37 of 95; elsewhere 104 of 170 and 166 of 315.
  Verifier: every number reproduced; 46 of 51 main large games under one half; survives leaving out any opponent, either evening, the three worst games and both Schooltime layouts; and it is not a head-count effect
  (we hold 0.48 of the living dragons after r100 on large layouts and still eat a third). Its limits: the window is not special (0.43 in r0-100, 0.33 after r300); "other layouts" averages 0.09 to 0.78,
  and Tower Defense and Stripes are worse than any large layout; counted by layout, 5 of 19 at random do this badly in about 5 percent of draws.
  New this hour: 4 large-layout games, share 0.412 (1,703 against 2,431): Schooltime 1 0.24 (won), Around UNSW 0.44 (won) and 0.35 (lost), Australia 0.53 (lost). Too few for the bar (10).
  New this hour, own count (work/h4_pass.py), natural pearls born within 6 tiles of a head of both sides:
  - Who is nearer. Our head is the nearer one in 0.412 of non-tied births on main large layouts (8,887 against 12,667) and 0.401 on v31 (14,912 against 22,284). Other layouts 0.469 and 0.456.
    Per large layout 0.36 to 0.43 (main) and 0.34 to 0.44 (v31); main band b 0.435, band c 0.405.
  - Who converts. On large layouts we eat 0.774 (main) and 0.764 (v31) of the pearls we are nearer to; they eat 0.882 and 0.906 of the pearls they are nearer to.
    On other layouts the two are equal (0.774 and 0.774; 0.724 and 0.735). Equal distance on large layouts goes to us in 0.42 and 0.40 (0.54 and 0.53 elsewhere).
  - Length of the nearest dragon matters less than distance: when ours is nearer we eat 0.81 if ours is longer and 0.74 if theirs is longer (main, large).
  Verifier, 04:43 KST: the contested-pearl counts reproduce in every cell; both halves hold on each large layout and in both bands; share under one half in 47 of 55 main large games; 0 of 1000 label shuffles.
  With head counts within 10 percent the share is still 0.42 and 0.41 and they still convert better (0.79 against 0.88); matched on distance and lead, we eat 0.78 of ours and they eat 0.88 to 0.90 of theirs.
  Its limits: the conversion gap is small against 1700-1899 on main (0.05) and not clear of zero on Schooltime 2; early on, with level head counts, positions are even (0.49 in r0-100) and the deficit opens after r100;
  Stripes and Prisoners Dilemma 2 show the same pattern, so it is not only a large-layout fact.
  Totals now: main large 59 games, r101-300 share 0.338 (20,706 against 40,464), wins 22 of 59; other layouts 0.477, wins 107 of 176.
  New games since the bar: 8 on large layouts, share 0.368 (2,977 against 5,115), 2 won. Two Australia games at 0.53 and 0.51 were both lost (one on the queen rule after our queen was rammed at r172).
  Re-test, new games since the bar (after battle 1265766): 14 on large layouts (10 needed), r101-300 share 0.356 (5,114 against 9,253), 4 won. The bar (0.45 or more) is not reached: holds.
  Totals now: main large 65 games, share 0.339 (22,843 against 44,602), wins 24 of 65; other layouts 0.481, wins 116 of 190.
  New this hour, bar F11_convert passed by the letter and explains nothing (own count, work/h10_pass.py): when we are nearer and they eat the pearl, our nearest dragon was farther from it after its next turn in 0.639 of 2,254 cases (main)
  and 0.631 of 3,464 (v31). The mirror is the same (they nearer, we eat: 0.661 and 0.647) and so are the other layouts (0.61 to 0.65 for both sides). A lost pearl was walked away from six times in ten by either side on any layout.
  Paid sprints for a pearl are under 1 percent on both sides, so they do not out-run us. What does separate the sides on large layouts is in F26; what it costs from a level position is in F25.
  Totals now: main large 71 games, r101-300 share 0.347 (25,404 against 47,727), wins 26 of 71; other layouts 0.488, wins 131 of 209.
  New games since the second bar (after battle 1276407): 6 on large layouts, share 0.450 (2,561 against 3,125): Australia 0.49 (won), 0.42, 0.46 (lost), 0.56 (won); Islands 0.26 and 0.52 (both lost). The bar needs 10. Four of the six were lost with about half the pearls.
  New this hour: F31 dates the loss. On these layouts our eating falls by a quarter at round 151 while theirs rises, and round 150 is where the bot's leader phase starts on layouts above 1200 cells.
  Totals now: main large 74 games, r101-300 share 0.348 (26,670 against 49,880), wins 26 of 74; other layouts 0.491, wins 140 of 221.
  New games since the second bar (after battle 1276407): 9 on large layouts, share 0.420 (3,827 against 5,278), 2 won. This hour: Australia 0.43 and 0.43, Around UNSW 0.27, all three lost from ahead at r100. The bar needs 10; at 0.42 it is not far from the 0.45 line.
  New games, run 0900 (bar F11_new_games_2, after battle 1276407; 10 needed): 13 main games on large layouts, our share of pearls in r101-300 0.374 (4,924 against 8,259). The line was 0.45: holds. Totals: 0.344 on 78 main games (27,767 against 52,861), 26 won.
  New games, run 1000 (bar F11_new_games_3, after battle 1289717; 10 needed): 6 main games on large layouts, our share of pearls in r101-300 0.333 (2,185 against 4,369). In line; 4 short. Totals main: 0.344 on 84 games (other layouts 0.487 on 251); wins on large layouts 29 of 84.
  New games, run 1100 (bar F11_new_games_3, after battle 1289717; 10 needed): 9 main games on large layouts, our share of pearls in r101-300 0.314 (3,031 against 6,620). One short; in line. Totals main: 0.341 on 87 games (other layouts 0.483 on 268); wins on large layouts 29 of 87.
  New games, run 1200 (bar F11_new_games_3, after battle 1289717; 10 needed, now met): 14 main games on large layouts; our share of pearls in r101-300 is 0.298 (4,346 against 10,255). The line was 0.45: holds. All main games on large layouts: 0.337 on 92 games.
  New games, run 1500 (bar F11_new_games_4, after battle 1302921; 10 needed, now met): 18 main games on large layouts; our share of pearls in r101-300 is 0.282 (5,272 against 13,436). The line was 0.45: holds. All main games on large layouts: 0.328 on 110 games.
  New games, run 1800 (bar F11_new_games_5, after battle 1316833; 10 needed): 8 main games on large layouts; our share of pearls in r101-300 is 0.293 (2,625 against 6,330); 2 won. In line. All main games on large layouts: 0.326 on 118 games, 40 won.
would be wrong if: (03:11, passed, recounted) pooled r101-300 share on large layouts 0.45 or more on main or v31; fewer than 3 of 5 layouts under 0.45 in both codes; share elsewhere under 0.47.
  (04:02, counted 04:10, recounted) our-nearer share 0.48 or more on main or v31 large layouts. Passed: 0.41 and 0.40. Our conversion not at least 5 points below theirs. Passed: 11 and 14 points.
  (new games) weakened if, once 10 new main games on large layouts exist, our r101-300 share there is 0.45 or more. 8 so far: 0.37.
inferred: Both halves of the loss are real on large layouts: where our dragons stand (41 percent nearer) and what happens after (77 against 88 to 91 percent). The second half exists only on large layouts.
  See F16 and F20 for where their dragons stand: together at the tiles that keep giving pearls.
  Added 07:20: the timing is now known (F31): the gap opens at round 151, the bot's own LEADER_GROW_ROUND_BIG.
not checked: why they convert better there (a second head arriving, or our dragon turning away: SMALL_THREAT_MULT and the threat fields). Distance is straight-line with wrap, not path.
  Schooltime is also a sealed-queen layout; it is here for size only.
look at: data/online/ladder/1255622/M1255622.replay r100-300 (Islands vs 1934: pearls 144 against 895 in r101-300);
  data/online/ladder/1270027/M1270028.replay r100-300 (Around UNSW vs 1851, new: 60 dragons each at r100, pearls 495 against 905);
  data/online/ladder/1248527/M1248527.replay r100-300 (Australia vs 1946: 155 against 957).
smallest test: no change yet; F20 names where their dragons stand, and the test belongs there.

### F25 On large layouts a level or leading position at round 100 does not grow: our share of total length falls by round 300 in two games of three and rises in almost none
status: confirmed for the large-layout half (verifier 06:53: holds in part; main and v31, and not feeding); the contrast with other layouts is weaker than I wrote      first seen: 7 Oct 06:03 KST run 20261007-0600   last tested: 7 Oct 18:20 KST (rows.jsonl, new games)
measured: rows.jsonl curves. Games in which our total length at r100 is at least 0.95 of theirs. Share = ours / (ours + theirs). Large = 2000 or more open tiles.
  r100 to r300 (games that reached r300), share lower by 10 points or more: large layouts main 17 of 27 (0.63), v31 35 of 45 (0.78); other layouts 12 of 55 (0.22) and 28 of 95 (0.29).
  r100 to r200 (before any feeder death; games that reached r200): lower by 10 points in 8 of 27 and 20 of 45 on large layouts, 8 of 73 and 19 of 121 elsewhere. Higher by 10 points: large 2 of 27 and 0 of 45; elsewhere 30 of 73 and 39 of 121.
  By layout (fall by r300, main then v31): Australia 5 of 5 and 14 of 17; Islands 2 of 3 and 11 of 11; Around UNSW 5 of 10 and 5 of 9; Schooltime 1 3 of 6 and 1 of 2; Schooltime 2 2 of 3 and 4 of 6.
  Not large, for contrast: Slithery Fight 2 of 12 and 3 of 16, Maze 0 of 6 and 0 of 12, weakhold 0 of 10 and 3 of 20; but Portals 3 of 6 and 5 of 9, Trauma 4 of 8 and 4 of 9.
  Wins from that position: large layouts 13 of 27 (main) and 25 of 45 (v31); other layouts 56 of 73 and 77 of 121 (games reaching r200). Of the 17 main games that fell, 8 were won; 11 ended with both queens dead.
  Verifier, 06:53 KST: all counts reproduce. The large-layout half holds: not chance (fall by r300 p 0.0005 main, 8e-8 v31), not the r100 condition (38 of 65 and 58 of 94 without it), not one layout, opponent or three games, not small totals,
  and not feeding (no no-action death of ours before raw round 201; adding that length back moves at most 4 of 17 main and 8 of 35 v31 falls; in the fallen games they eat 299 against our 226 over r101-200 and 366 against 187 over r201-300 on main).
  What does not hold as worded, accepted: 'on other layouts this is rare'. It is one game in four there; Portals, Trauma and Tower Defense fall as often (21 of 37) as Around UNSW and Schooltime (20 of 36); Slithery Fight is at 5 of 28.
  The strong part is Australia and Islands (32 of 36), so the line is not at 2000 open tiles. Total length is not the result rule: on Around UNSW we win 15 of 19 of these games, on Islands 1 of 14. Main is one evening and its fall by r200 is thin (p 0.30 without three games).
  New games since the bar (after battle 1276407): 6 large-layout games level or ahead at r100. Share of total length rose by 10 points by r200 in 1 (Islands vs 1873: 0.65, 0.76, then 0.43 at r300, lost), fell by 10 in 2, fell by r300 in 5; 2 won. The bar needs 10.
  Totals now: main 33 such games: rose by r200 in 3, fell in 10, fell by r300 in 22; won 15. v31 unchanged (45: 0, 20, 35).
  New games since the bar (after battle 1276407): 9 large-layout games level or ahead at r100. Share of total length rose by 10 points by r200 in 1, fell by 10 in 3, fell by r300 in 8; 2 won. The bar needs 10.
  This hour: 3 large-layout games and one Slithery Fight game, all four ahead at r100 (by 18 to 99 percent), none won. Around UNSW vs 1990: 187 against 94 at r100 with 61 dragons against 34; 200 against 165 at r150; 190 against 279 at r200; lost on longest dragon 32 against 52.
  Totals now: main 36 such games: rose by r200 in 3, fell in 11, fell by r300 in 25; won 15.
  New games, run 0900 (bar F25_new_games; 10 needed): 10 main games on large layouts level or ahead at r100 and reaching r200; our share of total length rose by 10 points by r200 in 1. The line was 3 or more: holds.
  New games, run 1000 (bar F25_new_games_2; 10 needed): 3 such games; our share rose by 10 points in none and fell in 3. Totals main: 40 games, rose in 3, fell in 31.
  New games, run 1100 (bar F25_new_games_2; 10 needed): 4 such games; our share rose by 10 points in none and fell in 4. Totals main: 41 games, rose in 3, fell in 32.
  New games, run 1200 (bar F25_new_games_2; 10 needed): by the rule as I coded it this hour (ahead, or within 20 percent, at r100; reaching r200) 9 games since battle 1289717: our share rose by 10 points by r200 in none and fell in 5.
  The earlier hours counted 4 where this rule gives 6 on the same games, so the two counts differ a little; neither has a rise. The 3 games of this hour (Around UNSW twice, Schooltime 1) rose by 0 to 8 points and none fell. Totals main by this hour's rule: 55 games, rose in 4, fell in 39.
  New games, run 1500 (bar F25_new_games_2, the coded rule of run 1200; 10 needed, now met): 16 games since battle 1289717 on large layouts in which we were ahead or within 20 percent at r100 and that reached r200: our share of total length rose by 10 points by r200 in none and fell in 9. The line was 3 or more: holds. We won 9 of the 16.
  New games, run 1800 (bar F25_new_games_3; 10 needed): 6 such games since battle 1316833; our share of total length rose by 10 points by r200 in none and fell in 4; 1 won. In line.
would be wrong if: (06:03, before the count) the 10-point fall by r300 happens in under 40 percent of such large-layout games on main or on v31, or the rate on the other layouts is within 15 points of it. Passed: 63 and 78 percent against 22 and 29.
inferred: This is F11 seen in total length, with one thing added: being level or ahead at round 100 does not protect us there. On other layouts such a position grows by 10 points by r200 in four games of ten; on large layouts it did in 2 of 72.
  The fall by r300 is partly our own feeding (from round 201 we give up length on purpose), which is why the fallen games are still won half the time. The r100 to r200 figures are free of that.
not checked: games that end before r300 drop out (mostly our wins by elimination on small layouts); the r200 figures do not have that problem. Total length is not what decides a game. The two games that prompted the bar
  (Islands and Australia vs 1954) are inside the main count. Portals and Trauma fall as often as the large layouts, so size is not the only way to get this.
look at: data/online/ladder/1275534/M1275535.replay r100-300 (Islands vs 1954: 45 dragons against 25 at r100, pearl share 0.61, then 0.29, then 0.04; lost on longest dragon);
  data/online/ladder/1275534/M1275537.replay r100-300 (Australia vs 1954: level at r100, queen rammed r114, pearl share 0.55, 0.32, 0.18; lost).
smallest test: no change yet; this is the size of the F11 and F26 problem, not a mechanism. Use it as the pass mark for any large-layout switch: from a level position at r100 our share of total length at r200 should stop falling
  (now it falls by 10 points in a third of games and rises in almost none).

### F26 On large layouts they finish nine in ten of the pearls born nearer to them and we finish under eight in ten of ours; our rate is the same on every layout, theirs is better there
status: confirmed (verifier 06:53: holds; the walk-away margin on main sits at the bar, the finished gap is solid)      first seen: 7 Oct 06:08 KST run 20261007-0600   last tested: 7 Oct 07:04 KST (follow-up bars F30 and F31)
measured (own count, work/h10b_pass.py, 665 games): natural pearl births with a head of both sides within 6 tiles, one side strictly nearer, pearls that were eaten by someone.
  "In view" = the pearl is inside the 7 by 7 square of the nearer dragon's head (what a dragon sees); that is 96 to 97 percent of these births. All figures below are in view, main then v31.
  Finished (eaten by the nearer side). Large layouts: ours 0.787 (9,717 births) and 0.775 (14,085); theirs 0.889 (14,203) and 0.911 (21,359). Other layouts: ours 0.776 and 0.726; theirs 0.765 and 0.737.
  Walked away (the nearer dragon is farther from the pearl after its next completed turn, pearl still there). Large: ours 0.378 and 0.386; theirs 0.335 and 0.303. Other layouts: ours 0.410 and 0.422; theirs 0.424 and 0.425.
  Left lying (nearer to one side, eaten by the other 3 or more rounds after the birth). Large: ours 0.168 and 0.174; theirs 0.085 and 0.066. Other layouts: ours 0.181 and 0.215; theirs 0.170 and 0.188.
  By distance of the nearer head at the birth, large layouts, finished: 0 or 1 tile: ours 0.876 / 0.885, theirs 0.949 / 0.961; 2 or 3 tiles: 0.757 / 0.740 against 0.871 / 0.892; 4 to 6 tiles: 0.617 / 0.568 against 0.764 / 0.780.
  A pearl born 0 or 1 tile from the head: we are farther from it after the next turn in 0.344 / 0.350, they in 0.244 / 0.226 (other layouts 0.40 against 0.43).
  By game on large layouts our walk-away share is the higher one in 42 games against 16 (main) and 72 against 16 (v31). By layout, ours minus theirs in points: main Australia 8.8, Schooltime 1 5.8, Islands 4.4, Around UNSW 2.7,
  Schooltime 2 2.0; v31 4.7 to 12 on all five. By band: main 3.2, 5.7, -0.2 (2100+, 818 births); v31 8.9, 7.2, 8.9.
  By round of the birth (large, finished, ours / theirs): main r0-100 0.848 / 0.906, r101-300 0.786 / 0.896, r301+ 0.766 / 0.874; v31 0.839 / 0.916, 0.785 / 0.917, 0.741 / 0.901.
  Verifier, 06:53 KST: all counts reproduce. The finished gap is on all five large layouts in both codes and survives resampling and leaving out any layout or opponent (+0.10 main, +0.14 v31); a third of it is where the pearls fall,
  6.7 and 9.8 points remain inside the same cells of distance and head count. The walk-away gap on main is clear of zero (2.4 to 6.0 points) but sits at the 4-point bar. It is not eating another pearl (that is 0.155 of our walk-aways, 0.17 of theirs) and not head count.
  It is made at pearls born next to the head: a free pearl one open step away is left behind by ours in 0.28 and by theirs in 0.16 on main (767 of 2,774 against 674 of 4,133), 0.29 against 0.17 on v31; no pearl is ever born under a body, so it is a choice.
  At distance 2 or more the main gap is not clear of zero. 'Both about three quarters on other layouts' is true of the pool only. (This answers my planned F26_detail bar; the number was the verifier's, seen before I counted, so it is not a test of mine.)
  New this hour: F30 (failed bar) shows the left pearls are not about an enemy head being near; F31 shows the leaving starts at round 151 on layouts above 1200 cells and at round 301 on smaller ones, the rounds at which the bot's leader phase starts.
would be wrong if: (06:08) (our walk-away share minus theirs) among in-view births on large layouts is under 4 points on main or on v31. Passed: 4.3 (main) and 8.3 (v31).
  Seen before the bar: the v31 totals without the view split (0.40 against 0.31), found while reading the failed explanation of F11_convert. Not predicted.
inferred: The pearl gap of F11 is not about pearls our dragons cannot see; nearly all of these pearls are in view. Our dragons behave the same on every layout: they finish about 78 percent of the pearls they are nearer to and leave about
  17 percent lying for three rounds or more until the other side takes them. The opponents are the ones who change: on large layouts they leave half as much lying (7 to 8 percent against 17 to 19 elsewhere).
  So large layouts do not show a fault of ours that is absent elsewhere. They are where a pearl we leave is taken and a pearl they leave hardly exists. This fits F20 (their heads stay by the tiles that give pearls).
  A walk-away is not always a mistake (the dragon may be eating another pearl); the count cannot tell.
not checked: what our dragon was doing when it left a pearl 0 or 1 tile away (eating another pearl, going to feed, avoiding a head: SMALL_THREAT_MULT and the threat fields); whether an enemy head was closer by path.
  The main margin is thin (4.3 against a bar of 4), small on Around UNSW and Schooltime 2 and absent against 2100+ on main. The finishing gap (0.79 against 0.89) is the solid part; it was in F11 already (0.77 against 0.88).
look at: data/online/ladder/1275534/M1275537.replay r100-200 (Australia vs 1954); data/online/ladder/1276407/M1276407.replay r100-300 (Around UNSW vs 2111: 60 dragons each at r100, level in length, pearl share 0.33 after it);
  data/online/ladder/1255622/M1255622.replay r100-300 (Islands vs 1934).
smallest test: no change yet, count first: one local game on Around UNSW or Australia with a debug line for every dragon turn that starts with a pearl 0 or 1 tile from the head and ends without eating it
  (print is_feeder(), the route target, and whether a threat field ruled the step out). The switch follows from what that prints.
  Replaced 07:20 by the test in F31 (one constant: LEADER_GROW_ROUND_BIG). The debug line is still useful to tell which of the leader-phase rules makes a dragon leave a pearl.
  Pass mark for any switch: on large layouts we finish at least 0.85 of the pearls born nearer to us (now 0.78), and the F25 figure stops falling.

### F20 With the same number of dragons, a third of their heads stand at the tiles that keep giving pearls and a fifth of ours do; every rating band does it, from round 50 on
status: confirmed as a difference in where heads stand (verifier 04:43 and 05:47: holds in part: not the same size in every band; the link to pearls comes from their heads, not ours; no link to wins)      first seen: 7 Oct 04:14 KST   last tested: 7 Oct 06:06 KST
measured (own count, work/h8_fountain.py): layouts with 1500 or more open tiles (the five large ones and Slithery Fight). Busy tile = a tile with 8 or more natural pearl births in that game
  (10 to about 120 tiles a game; they give 80 to 93 percent of all births on Around UNSW, Islands and Slithery Fight, about half on Australia and Schooltime 2, a quarter on Schooltime 1).
  Snapshots at the start of rounds 100, 125, ..., 300 in which the two sides are within 10 percent in dragons alive. Share of heads within 2 tiles of a busy tile:
  main: ours 0.212, theirs 0.318 (11,350 and 11,698 heads, 197 snapshots). v31: ours 0.203, theirs 0.317 (17,554 and 18,041 heads, 301 snapshots).
  Standing on a busy tile: 0.054 against 0.080 (main), 0.052 against 0.080 (v31). With a looser cut (5 births): 0.28 against 0.37 and 0.26 against 0.37.
  By layout, ours / theirs, main then v31: Around UNSW 0.16 / 0.27 and 0.16 / 0.31; Slithery Fight 0.27 / 0.37 and 0.26 / 0.37; Schooltime 2 0.29 / 0.43 and 0.36 / 0.41;
  Islands 0.18 / 0.23 and 0.18 / 0.24 (6 and 11 snapshots); Australia 0.17 / 0.18 (4 snapshots) and 0.12 / 0.12 (30 snapshots): nothing there.
  Two other counts of this hour point the same way. F19a (bar failed, reversed): at the same snapshots their heads are closer to each other than ours in 66 of 78 non-tied snapshots on main
  and 104 of 122 on v31 (median distance to the nearest friend). F19b (bar failed): they do not push into our half more than we push into theirs (0.29 against 0.29; 0.30 against 0.30).
  Verifier, 04:43 KST: every number reproduced. The gap holds for main and v31, on Around UNSW and on Slithery Fight separately (game-resampled intervals clear of zero), by game (38 against 6 on main),
  for radius 1 to 4 and busy cuts 5 to 20, without any opponent, evening or three games. Its limits, which I accept:
  - the definition is partly circular (they eat 62 percent of the pearls on busy tiles and each side sits by the tiles it eats from); with busy tiles taken from the other games on the layout the gap is 0.19 against 0.27,
    about 70 percent of it; for the real fast tiles of Around UNSW it is 0.063 against 0.109;
  - our share of the eating on real fast tiles is no lower than on other tiles (Around UNSW 0.42 against 0.40), so where heads stand does not by itself explain the pearl deficit of F11;
  - the gap is the same in games we won (0.22 against 0.31) and lost (0.20 against 0.33).
  New this hour, own count (work/h9_pass.py; bars from 04:21 KST):
  - By opponent rating, balanced snapshots r100-300, gap in points: main 1700-1899 16.4 (64 snapshots), 1900-2099 7.4 (121), 2100+ 13.8 (20). v31 under 1700 10.2, 1700-1899 11.6 (142), 1900-2099 11.2 (101), 2100+ 11.7 (39).
    The same size against every band. It is not something the top teams do more.
  - Early: at rounds 50 and 75 the gap is already 8.3 points on main (0.319 against 0.402, 36 balanced snapshots) and 9.9 on v31 (0.338 against 0.437, 57). Same two layouts: Around UNSW 0.32 against 0.47 and 0.27 against 0.47;
    Slithery Fight 0.35 against 0.47 and 0.39 against 0.49. Nothing on Australia, Islands, Schooltime 2 (2 to 9 snapshots each).
  - Cost (bar saved 05:17 KST for the next run, counted 05:19 because the data were on disk): per game, gap against our share of pearls in r101-300, games with 3 or more balanced snapshots.
    Rank correlation: Around UNSW -0.68 (40 games; main alone -0.42, v31 -0.82), Slithery Fight -0.62 (32 games; -0.50 and -0.58). Our share is 0.31 in the bigger-gap half of Around UNSW games and 0.38 in the other half;
    Slithery Fight 0.35 and 0.43. Wins: bigger gap 18 of 36, smaller gap 20 of 36: no visible difference.
  Totals now: main 0.211 against 0.318 (205 snapshots), v31 unchanged.
  Verifier, 05:47 KST: all numbers equal. Holds: the gap in every band, at rounds 50 and 75, and the pearl-share correlation (also with busy tiles taken from other games: -0.67 and -0.65).
  Does not hold: 'the same size against every band'. On main it is 0.164 against 1700-1899 and 0.074 against 1900-2099, beyond chance (3 of 4,000 shuffles) and in the same order inside three layouts; the v31 bands agree with each other.
  Limits on the cost, accepted: the correlation with our pearl share comes from their heads (-0.68 and -0.56), not from ours (+0.21 and +0.27, within chance); main alone is within chance; no relation to wins; both measures cover the same rounds.
  Re-count this hour with the 20 new games: main ours 0.210, theirs 0.320 (229 snapshots); by band 0.211 / 0.362, 0.212 / 0.291, 0.196 / 0.351; the new games alone 0.205 / 0.344 (24 snapshots).
  Not re-counted this hour (the h9 pass was not rerun). F31 may be part of why our heads are not at the busy tiles after round 150, but the gap is already there at rounds 50 and 75, so F31 cannot be all of it.
would be wrong if: (04:14, passed, recounted) (their share minus ours) under 8 points on main or v31, or positive on fewer than 4 of the 6 layouts in either code.
  (04:21, counted 05:09) F20_bands: wrong if under 5 points in either main band, or if v31 2100+ is not above v31 1700-1899. Not crossed, and not supported either: main 1900-2099 is 7.4 (the claim asked for 8),
  and v31 2100+ is 0.1 point above 1700-1899, which is no difference. I read it as: no rating effect.
  F20_early: wrong if under 4 points at r50-75 pooled on main or v31. Passed: 8.3 and 9.9.
  (05:17, counted 05:19) F20_cost: wrong if the rank correlation between the gap and our r101-300 pearl share is above -0.15 on Around UNSW or Slithery Fight. Passed: -0.68 and -0.62.
inferred: Opponents of every rating keep more heads parked where pearls reappear, from the first 50 rounds, on the layouts where a few tiles give most of the pearls (Around UNSW, Slithery Fight, less clearly Schooltime 2).
  main.cpp has no memory of where pearls reappear. But this is a difference in behaviour, not yet a cause of losing: the gap is the same in won and lost games and against 1750 and 2150 teams alike,
  and on the real fast tiles of Around UNSW we eat our usual share. It does go with the pearl deficit of F11: on both layouts the games with the bigger gap are the games in which we eat less in r101-300.
  Which causes which is open, and wins do not differ visibly between the two halves, so a switch built on it is a fair test but not a sure gain.
not checked: which way the link runs (a side that eats more makes more tiles busy and then sits by them); 167 of 205 balanced snapshots on main are Around UNSW and Slithery Fight; Australia shows nothing.
look at: data/online/ladder/1270027/M1270028.replay r100-300 (Around UNSW vs 1851, new: 60 dragons each at r100, pearls 495 against 905 in r101-300, lost);
  data/online/ladder/1249035/M1249035.replay r100-300 (Around UNSW vs 2382); data/online/ladder/1266953/M1266954.replay r100-300 (Slithery Fight vs 1810, new, lost on longest dragon).
smallest test: a default-off switch (nothing like it exists in main.cpp), say RESPAWN_MEMORY: each dragon remembers tiles where it saw a pearl appear twice within 12 rounds,
  and a small dragon with no pearl in sight is pulled to stay within 2 tiles of the nearest remembered tile that has no friend on it. Pass mark to write first, local games on Around UNSW and Slithery Fight:
  our share of heads within 2 tiles of a busy tile at r150 rises from 0.2 to 0.3 and our pearl share in r101-300 rises above 0.40.

### F7 On Tower Defense and Stripes we have 6 or fewer dragons at round 100 in 53 of 55 main games and the opponents in 21; on the other 2-dragon-start layouts the opponents are there at least as often as we are
status: confirmed on main in the narrower wording (verifier 15:26: holds in part; every sentence stands on main, on both days and with any one opponent left out). On v31 the two layouts are Tower Defense and Queen Of Spades rather than Stripes      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 18:20 KST (rows.jsonl, new games)
measured: Stall = at r100 we have at most 6 dragons alive and they have at least 15. Layouts where each team starts with 2 dragons, games that reached r100.
  main: 18 stalls in 96 games, 3 won (Tower Defense 10 of 15, Queen Of Spades 3, Trophy 3, Trauma 2; Maze, weakhold, Stripes 0). v31: 23 stalls in 156 games, 1 won.
  The verifier recounted the first 84 games exactly (15 stalls: band b 3 of 24, band c 8 of 56, 2100+ 4 of 4).
  New this hour: 6 games on 2-start layouts reached r100 (Trauma 3, weakhold 2, Maze 1), 0 stalls. Since the bar was set: 12 games, 3 stalls, 1 won. No Tower Defense game this hour.
  Tower Defense, every game on disk: our pearls eaten in r0-100 are between 1 and 7 in 15 of 15 main games and 22 of 22 v31 games. Wins there: 5 of 15 and 2 of 22.
  Own count this hour (work/h5_decline.py): on Tower Defense in r0-100 one of our dragons starts a turn next to a pearl only 62 times in 15 main games (opponents 1,008 times) and 105 times in 22 v31 games (964).
  When a pearl is next to us there we eat it (97 percent). So the dragons do not get near the pearls; they do not refuse them.
  Verifier's limits, which I accept: this is a Tower Defense fact plus 8 of 81 elsewhere; 4 of the first 15 stalls (Trophy, Trauma) ate 17 to 41 pearls and are dragon losses, not unreached food.
  Totals now: 19 stalls in 100 main games on 2-start layouts, 3 won (Tower Defense 10 of 15, Queen Of Spades 3, Trophy 3, Trauma 2, Stripes 1). Since the bar: 16 games, 4 stalls, 1 won.
  The new stall is Stripes vs 2140 (1 dragon against 15 at r100, 1 pearl against 66, eliminated at r136). No Tower Defense game this hour.
  New this hour, own count (work/h9_pass.py; bar kept since the first hour): on Tower Defense a pearl lies inside the 7 by 7 square (what a dragon sees) of one of our heads in 0.35 of rounds 1-50, on main and on v31.
  The opponents see one just as rarely (0.37 and 0.31) and still get next to pearls 1,008 times against our 62. So what differs is what a dragon does when it sees nothing.
  For comparison, in sight ours / theirs: Queen Of Spades 0.63 / 0.71 (v31 0.57 / 0.76), Trauma 0.65 / 0.71, Trophy 0.87 / 0.87, Maze 0.91 / 0.93, weakhold 0.96 / 0.93, Stripes 1.00 / 1.00.
  Re-test, new games since the bar (after battle 1262592): 25 on 2-start layouts that reached r100 (20 needed): 5 stalls (20 percent), 1 won. The bar (under 8 percent, or 30 percent won) is not met: holds.
  The new stall of this hour is Trophy vs 1885 (3 dragons against 37 at r100; their queen died at r32, ours was rammed at r104 with one friend near, eliminated r113). Tower Defense vs 1954 misses the rule (3 against 8 at r100) but is the same game:
  pearls 3 against 17 by r100, lost. Totals now: 20 stalls in 109 main games on 2-start layouts, 3 won (Tower Defense 10 of 16, Trophy 4 of 8, Queen Of Spades 3 of 18, Trauma 2 of 23, Stripes 1 of 8, Maze 0 of 21, weakhold 0 of 15).
  Tower Defense: 5 won of 16; our pearls in r0-100 are 1 to 7 in 16 of 16 main games.
  New this hour: 10 games on 2-start layouts reached r100 (second bar, after battle 1276407; 20 needed): 0 stalls. Totals now: 20 stalls in 119 main games on 2-start layouts, 3 won.
  Tower Defense, three new games: our pearls in r0-100 were 7, 6 and 7 against 11, 8 and 19; dragons at r100 3 against 6, 3 against 4, 4 against 6. None is a stall by the rule because these opponents (1814, 1978, 1873) were small too; 1 won.
  Tower Defense on main: 6 won of 19; our pearls in r0-100 are between 2 and 7 in 19 of 19 games.
  New this hour: 7 games on 2-start layouts reached r100. One stall: Tower Defense vs 1791 (2 dragons against 21 at r100, 1 pearl against 72, eliminated at r229). Second bar (after battle 1276407; 20 needed): 17 games, 1 stall, 0 won.
  Totals now: 21 stalls in 126 main games on 2-start layouts, 3 won (Tower Defense 11 of 21, Trophy 4 of 9, Queen Of Spades 3 of 21, Trauma 2 of 25, Stripes 1 of 10, Maze 0 of 23, weakhold 0 of 17).
  Tower Defense on main: 7 won of 21; our pearls in r0-100 are between 1 and 7 in 21 of 21 games (this hour 2 and 1).
  New games, run 0900 (bar F7_2, after battle 1276407; 20 needed): 26 games on 2-start layouts reached r100: 3 stalls (12 percent), none won. The lines were under 8 percent or 30 percent won: holds. All three are Tower Defense (vs 1791, 2067 and 1915: 2, 4 and 4 dragons against 21, 19 and 27 at r100).
  Totals now: 23 stalls in 135 main games on 2-start layouts, 3 won. Tower Defense: 13 stalls in 23 games, 7 games won; our pearls in r0-100 were 5 and 6 in the two games of this hour (theirs 49 and 91).
  Both of this hour ran to round 500 and were lost on the queen rule: our queen lived to r446 and r469 (rammed; own body) while theirs, 3 or 4 long until r400, was fed to 20 and 15 in the last 100 rounds.
  New games, run 1000 (bar F7_3, after battle 1289717; 20 needed): 5 games on 2-start layouts reached r100 (Stripes, Queen Of Spades, Trophy, Trauma twice): 0 stalls. No Tower Defense game. Totals now: 23 stalls in 140 main games on 2-start layouts, 3 won.
  New games, run 1100 (bar F7_3, after battle 1289717; 20 needed): 14 games on 2-start layouts reached r100: 2 stalls (Trophy vs 1665, 5 dragons against 41, lost; Trauma vs 1790, 4 against 17, won). Totals now: 25 stalls in 149 main games on 2-start layouts, 4 won.
  Tower Defense vs 1790 misses the rule again (2 dragons against 5 at r100) and is the same game: 2 pearls against 12 by r100, 8 against 165 by r200, 49 against 731 at the end; lost on the queen rule. Tower Defense on main: 7 won of 24.
  Three more losses of this hour are games in which we never grew, off Tower Defense: Queen Of Spades vs 1790 (0 pearls against 30 by r50, wiped out at r54), Stripes vs 1790 (17 pearls against 82 by r200, never more than 5 dragons), Trophy vs 1665 (11 against 49 by r50).
  A bar on what they have in common failed this hour (F41): we are not much later to the first meal, and our dragons do not walk straighter than theirs when they see nothing. On Tower Defense our first meal is not late at all (median 17 rounds against 20.5); we stop after it.
  New games, run 1200 (bar F7_3, after battle 1289717; 20 needed, now met): 20 games on 2-start layouts reached r100: 2 stalls (10 percent), 1 of them won. The lines were under 8 percent, or 30 percent or more of the stalls won: the second line is crossed, on two stalls. By the letter the bar fired.
  What the rule misses, this hour again: Stripes vs 1995 (2 pearls each by r50, 4 dragons against 5 at r100, 19 pearls in the game against 144, lost), Stripes vs 2195 (4 against 11 at r100, 42 pearls against 260, wiped out at r213), Trophy vs 2474 (wiped out at r99, before the rule can look).
  Totals: 25 stalls in 155 main games on 2-start layouts, 4 won. The stall rule needs their side to have 15 dragons at r100; against opponents who are also small the game is not counted, though we never grew. A rule on our side alone is the bar for next hour (F7b).
  F7_sweep (what their dragons do when nothing is in view) was not counted this hour; carried.
  Restated and counted, run 1500 (bar F7b, saved 12:42; rows.jsonl). Never grew = 6 or fewer of our dragons alive at r100, or wiped out before r100. Layouts where each team starts with 2 dragons.
  main: 71 of 185 games (0.38), 19 of them won (0.27). v31: 60 of 168 (0.36), 7 won (0.12). Halves of main: 18 of 45 with 6 won, 53 of 140 with 13 won. Games in which we did grow: 80 won of 114 (main), 73 of 108 (v31). 52 of the 203 main losses are never-grew games.
  The lines were under 10 percent of games, or 40 percent or more won (also in either half): not wrong. The claimed win share (under 25 percent) is missed by 2 points on main.
  The mirror, counted after the bar and it changes the reading: the OPPONENT is at 6 or fewer dragons at r100 in 56 of the 185 main games and 50 of the 168 on v31. By layout, ours against theirs, main: Tower Defense 29 of 29 against 11; Stripes 17 of 19 against 9;
  Queen Of Spades 11 of 30 against 15; Trauma 7 of 31 against 8; Trophy 7 of 21 against 9; weakhold 0 of 23 against 4; Maze 0 of 32 against 0. v31: Tower Defense 22 of 22 against 13; Stripes 18 of 26 against 12; Queen Of Spades 12 against 3; Trophy 6 against 12; Trauma 2 against 1; weakhold 0 against 9.
  So it is a weak point of ours on Tower Defense and Stripes only (46 of 48 main games against 20 of 48); on the other five layouts the two sides stall equally often. When we never grew and they did we won 9 of 50 (main) and 4 of 43 (v31); when both never grew 10 of 21 and 3 of 17.
  Pearls by r100 in our never-grew games: a median of 6 against 48 (main), 5.5 against 56 (v31).
  By opponent rating (main; question 2): we never grew in 29 of 72 games against 1700-1899 (12 won), 31 of 92 against 1900-2099 (6 won), 10 of 19 against 2100+ (1 won). THEY never grew in 35 of 72, 19 of 92 and 2 of 19. v31: ours 30 of 93, 19 of 52, 7 of 15; theirs 33 of 93, 14 of 52, 2 of 15.
  So our rate does not depend on the opponent and theirs falls with rating, on both codes: half of the 1700-1899 teams stall on these layouts as we do, the 2100+ teams almost never.
  The team has since counted Tower Defense and Stripes in detail (losses/early-growth.md, 14:28 KST, not my count): on Tower Defense our two dragons stay inside the 49-tile start room for the first 60 rounds in 27 of 27 games (CENTER_PULL holds them at the wall nearest the centre; the exit is at the far corner), on Stripes 90 percent of the pearls are born in rooms behind portals and we step in 2.3 times a game against 6.5.
  Its notes also say EXPLORE_GAIN 5 to 40 did not get the dragons out locally, which answers my bar F7_sweep before I ran it: dropped. Property for unseen maps: a walled start whose way out leads away from the board centre, and pearls behind portals in rooms of 1 to 4 tiles.
  New games: 8 of 21 main games on 2-start layouts since battle 1302921 never grew (Tower Defense 4 of 4, Queen Of Spades 2, Stripes 1, Trophy 1), 1 won.
  Verifier, 15:26 KST: holds in part. All counts recount exactly. On main every sentence stands: ours 71 of 185, theirs 56; far above theirs only on Tower Defense (only ours 18, only theirs 0) and Stripes (10 against 2); their rate falls with rating (35 of 72, 19 of 92, 2 of 19; 97 and 4 of 20,000 battle shuffles), ours does not. Stable over limits of 3 to 10 dragons, rounds 80 to 150, one opponent left out, both days.
  It does not hold on v31 as worded: there Queen Of Spades is 12 against 3 of 26 and Stripes 18 against 12 (inside chance). And a correction of the reading: 'they stall as often' compares unlike games. Ours are mostly a side that did not eat (median 6 pearls in r0-100), theirs half a side that ate and was killed (median 12 on main, 19 on v31).
  Without Tower Defense and Stripes they are under the rule more often than we are (36 against 25 of 137 on main).
  New games, run 1800 (bar F7_td_stripes_new, after battle 1316833; 10 needed, weakened at 4 or more): 7 games on Tower Defense and Stripes; we have more than 6 dragons at r100 in none (2, 2 and 3 alive; four Stripes games ended before r100 with none of ours left). It can no longer fire.
  Totals main: 6 or fewer at r100 (or gone before it) on Tower Defense 31 of 31 (theirs 12), on Stripes 22 of 24 (theirs 9); wins 8 of 31 and 4 of 24.
  Stripes, all 24 main games (288 cells, 8 portals, 2 dragons each): 23 end by elimination, 19 lost by it. Our pearls by r50 are 0 to 8 in every game; theirs 10 or more in 16 games, of which we lost 15. In the 8 games where neither side ate we won 3.
would be wrong if: (first hour) stalls under 8 percent of main games on 2-start layouts, none below 2100, 30 percent or more won, or v31 under 8 percent. All passed and were recounted.
  (new games) weakened if, once 20 new games exist, stalls are under 8 percent or 30 percent or more are won. 16 so far: 4 stalls, 1 won.
  (F7_sight, first hour, counted 05:09) claim: nothing in sight in at least 70 percent of rounds on Tower Defense; wrong if a pearl is in sight in more than half. Between the lines: 65 percent. Not passed, not failed.
inferred: On Tower Defense the first pearls are 20 to 36 path steps from spawn and nothing in main.cpp pulls a dragon that far: the pearl pull (TARGET_REWARD 260 minus TARGET_DECAY 40 a step) is zero
  from 7 steps, PEARL_FAR_DECAY and EXPLORE_GAIN are 0, and a dragon sees only 3 tiles (VISION_RADIUS 3). The map property is "2 starting dragons and the first pearls far by path".
not checked: what our dragons had seen or been told at those rounds. All main games are from 6 Oct and the first hours of 7 Oct KST.
look at: data/online/ladder/1263705/M1263705.replay r0-100 (Tower Defense vs 2022: 3 dragons against 23 at r100, 2 pearls against 70);
  data/online/ladder/1255360/M1255361.replay r0-100 (Tower Defense vs 1873: nearest pearl 37 path steps away for 50 rounds).
smallest test: EXPLORE_GAIN above 0 (it is 0.0 in main.cpp; EXPLORE_RANGE 60, EXPLORE_ROUNDS 200 already exist), only while we have 3 or fewer dragons and no pearl in sight; local games on Tower Defense.
  This hour's count points at exploring rather than at PEARL_FAR_DECAY: for two rounds in three there is no pearl in sight to be pulled to, for either side.
  Pass mark to write first: our pearls by r100 on Tower Defense rise from 4 to at least 20, with no drop in wins on the other layouts.

### F23 On Portals our queen walks through a portal into a pearl room of 4 tiles at round 4 in every game and dies in such a room; their queen stays outside and often lives
status: confirmed as a one-layout fact (main and v31; verifier 05:47: holds)      first seen: 7 Oct 05:06 KST run 20261007-0500   last tested: 7 Oct 09:12 KST (work/h9_portalq.py rerun)
measured (own count, work/h9_portalq.py; room = tiles joined by open edges, kelp and portal edges closed): Portals is 32 by 16, 20 portal pairs, 3 starting dragons of length 3 a side, both queens start in the big
  208-tile area; three quarters of its pearls are born in rooms of 4 tiles or fewer behind portals.
  Our queen: dead before the end in 9 of 9 main games and 27 of 27 v31 games. Her head was in a room of 6 tiles or fewer when she died in 9 of 9 (1-tile room 5 times, 4-tile room 4 times) and 26 of 27.
  She had taken a portal step in 36 of 36 games, and her first turn inside a small room is round 5 in all 36. Causes: wall 14, own body 7, the body of one of our own dragons 15; an enemy never kills her there.
  Death round: main 10, 10, 38, 52, 68, 78, 182, 187, 231; v31 round 9 or 10 in 12 of 27 games (each time the body of one of our own dragons in the 4-tile room).
  Their queen: a portal step in 2 of 9 and 12 of 27 games; 8 of 3,226 queen turns in small rooms on main (ours 104 of 865); she died in a small room in 1 of 5 and 10 of 21 deaths; alive at the end in 4 of 9 and 6 of 27.
  Results on Portals: main 4 won of 9, all 4 games with their queen alive at the end lost; v31 13 of 27, the 6 such games lost. In the newest one (vs 2140) we ate 0.83, 0.73 and 0.70 of the pearls in the three windows,
  had 40 length against 23 at r100, and lost on the queen rule: our queen died on a wall in a 1-tile room at r187.
  One opening read round by round (1250318/M1250322 and 1271874/M1271875, same moves): she walks 30,10 to 29,10 to 28,10 to 28,9, a tile whose only way on is a portal, steps through it to 4,6 at round 4,
  eats the room's pearls, splits (the child comes out on the far side), and at round 10 runs into her own body in the 2 by 2 room.
  Second layout with pearl rooms behind portals, looked at after: on Stripes our queen died in a small room in 4 of 9 deaths (main) and 5 of 23 (v31), theirs 2 of 7 and 7 of 22. No such pattern there.
  Other layouts with portals (bar saved 05:17 KST, counted 05:19, field portal of work/h9_pass.py, queen turns in r0-100): on 12 of 16 portal layouts our queen takes no portal step at all
  (main 0 steps in about 15,400 queen turns, v31 1 in about 23,200; their queens 9 and 34). She goes through on four: Portals (28 steps in 565 turns main, 63 in 1,363 v31; theirs 3 in 819 and 17 in 2,530),
  Stripes (19 in 768 and 59 in 1,897; theirs 16 and 68), Prisoners Dilemma 1 (7 in 297 and 48 in 1,539; theirs 0 and 6) and Prisoners Dilemma 2 (13 in 455 and 16 in 620; theirs 0 and 0).
  Pooled without Portals and Stripes: 2.15 times their rate on main, 1.53 on v31 (the bar asked 2 and was wrong under 1.5: passed on main, undecided on v31). On the two Prisoners Dilemma layouts it does not cost her life
  (ours dies first in 4 games, theirs in 5, main).
  Verifier, 05:47 KST: all numbers equal; the first portal step is in raw round 4 and she is in a 4-tile room at round 5 in 36 of 36 games against 29 opponents. Two things it adds: she dies on that first visit in only 2 of 9 (main) and 12 of 27 (v31);
  otherwise she leaves and dies on a later visit, mostly in a 1-tile room. A 1-tile room kills every queen that starts a turn in one (ours 16 of 16, theirs 9 of 9); the sides differ in going in (36 of 36 against 14 of 36) and in the 4-tile rooms
  (ours die in 19 of 57 visits, theirs in 2 of 27). Whenever their queen survives we lose (0 of 10).
  New game this hour (1275421, vs 1885, won): the same opening (in a 4-tile room at round 5), 3 portal steps, dead at r111 on her own body in a 4-tile room; their queen died on a wall in a 1-tile room at r13.
  Totals: main 10 of 10 dead in a room of 6 tiles or fewer (1 tile 5 times, 4 tiles 5 times); main Portals 5 won of 10. Bar F23_new: 1 of 3 games arrived, in line.
  No Portals game this hour. Bar F23_new: 1 of 3 games arrived.
  New games, run 0900 (bar F23_new: 3 main Portals games after battle 1271874; work/h9_portalq.py rerun): our queen in a room of 6 tiles or fewer by round 5 in 3 of 3; alive at r200 in 0 of 3 (died r111, r10, r60). Holds. main now: 12 games, queen dead in 12, 11 of them in a small room; their queen died in 7 of 12, 3 in a small room.
would be wrong if: (05:06, before any count of where she dies) under 60 percent of our queen deaths on Portals are in a room of 6 tiles or fewer, on main or on v31. Passed: 100 and 96 percent.
  Seen before the bar: that she dies in 36 of 36 games, early, never by a ram, and that she made 2 portal steps in one new game.
inferred: QUEEN_NO_PORTAL is true and does not stop this. In score_portal_step() the ban returns SCORE_PORTAL (-1e9), a last resort and not a rejection (SCORE_REJECT is -1e15); she first walks to a dead-end tile whose
  only exit is the portal, so the last resort is all she has. My guess is that her pearl target is found by a path that runs through the portal; that needs the bot, not replays.
  The map property would be "fast pearls in rooms of 1 to 4 tiles behind portals, a queen that starts within a few steps of one". One layout cannot show a property, and Stripes does not repeat it.
  What it costs is bounded: 4 of 9 main Portals games and 6 of 27 v31 games were lost with only their queen alive.
not checked: which line of main.cpp sends her to 28,9 (survey_no_portal is set from queen_portal_ban(), so the survey is meant to leave portals out); whether main changed anything on purpose
  (on main she outlives round 10 in 7 of 9 games, on v31 in 15 of 27, and still dies in a room).
look at: data/online/ladder/1250318/M1250322.replay r0-10 (Portals vs 1971: through the portal at r4, dead on her own body at r10);
  data/online/ladder/1271874/M1271875.replay r0-8 and r180-187 (Portals vs 2140: same opening, 0.83 of the pearls by r100, dies on a wall in a 1-tile room, lost on the queen rule);
  data/online/ladder/1167648/M1167651.replay r0-9 (v31: dead on her own child at r9).
smallest test: one local game on Portals with a debug line for the queen in rounds 0-4 (which target she walks to and what score_portal_step() returns at 28,9). Then a default-off switch, say QUEEN_ROOM_MIN:
  the queen never takes a step, portal or not, into a tile from which the only way on is a portal, nor into a room smaller than 8 tiles, while any other legal step exists.
  Pass mark to write first: on Portals our queen is alive at r100 in at least 8 games of 10 (now 3 of 9 on main, 6 of 27 on v31) and wins there do not fall.

### F10 On four 2-dragon-start layouts we get about a third of the pearls by round 50
status: confirmed in the verifier narrower wording (holds in part)      first seen: 7 Oct 03:10 KST   last tested: 7 Oct 18:20 KST (rows.jsonl, new games)
measured: Tower Defense, Stripes, Trauma, Queen Of Spades together, share of pearls eaten by r50: main 0.339 (63 games, 327 against 637), v31 0.296 (91 games). All other layouts 0.510 and 0.507.
  Verifier: every count reproduced; 0 of 2000 shuffles; share under one half in 37 of 59 main games. Per layout main / v31: Tower Defense 0.37 / 0.38, Stripes 0.28 / 0.27, Trauma 0.20 / 0.33, Queen Of Spades 0.44 / 0.28.
  What the verifier took away, and I accept: scarcity as such is not the cause (Schooltime and Default are scarce and near half); "absent against 1700-1899 teams" is fragile (0.49 pooled, 0.33 without our three
  best games); late splitting explains at most Stripes and Queen Of Spades (on Trauma both sides split at r0 and r1 and we are still lowest).
  New this hour: 4 games (Stripes 8 against 10, Trauma 1 against 1, 7 against 0, 2 against 1). Against 1900+ only 1 new game; the bar needs 10.
  New this hour: Stripes is now explained separately (F18): the pearls there sit in small closed rooms our dragons will not eat in.
  Totals now: the four layouts 0.332 (65 main games, 335 against 673); all other layouts 0.510. New against 1900+ since the bar: 2 games (Trauma 7 against 0, Stripes 1 against 25); the bar needs 10.
  Re-count this hour: the four layouts 0.331 (67 main games, 340 against 686); all other layouts 0.510. New against 1900+ since the bar: 4 games, 13 against 38 (0.255); the bar needs 10.
  Totals now: the four layouts 0.345 (74 main games, 396 against 753); all other layouts 0.513. New against 1900+ since the bar: 6 games, 18 against 61 (0.228); the bar needs 10.
  This hour against all bands: 7 games, 56 against 67. Queen Of Spades 18 against 4 (vs 1814) and 17 against 15 (vs 1870), both won; 2 against 18 (vs 2014), won later by elimination; Tower Defense 6 against 6, 3 against 5, 4 against 7; Stripes 6 against 12 (won).
  Totals now: the four layouts 0.348 (80 main games, 423 against 793); all other layouts 0.515. New against 1900+ since the bar: 7 games, 19 against 83 (0.186); the bar needs 10.
  This hour: Trauma 7 against 1 and 8 against 2 (both won), Stripes 8 against 7 (won) and 1 against 22 (vs 1990, eliminated at r91), Tower Defense 2 against 3 (won) and 1 against 5 (lost).
  New games, run 0900 (bar F10_new_games, after battle 1265766, the four scarce 2-start layouts against 1900+; 10 needed): 11 games, our share of pearls by r50 0.199 (32 against 129). The line was 0.45: holds.
  New games, run 1000 (bar F10_new_games_2; 10 needed): 3 games on the four scarce layouts against 1900+: 37 pearls against 36 by r50. Too few to read. Totals main against 1900+: 0.285 on 54 games.
  New games, run 1100 (bar F10_new_games_2; 10 needed): 4 games on the four scarce layouts against 1900+: 37 pearls against 63 by r50 (0.37). Too few. This hour against all bands: 6 games, 10 pearls against 109 (Queen Of Spades three times, Stripes, Tower Defense, Trauma).
  First meal on these layouts (own count, work/h23_pass.py; seen after the F41 count, not under a bar): median rounds from the first pearl on the board to the first meal, ours against theirs, both codes:
  Queen Of Spades 23 against 10 (52 games), Stripes 20 against 10 (42), Trauma 32 against 19 (45), Tower Defense 17 against 20.5 (46). The other 2-start layouts: Maze 5 against 5, Trophy 6 against 7, weakhold 10 against 10.
  One Queen Of Spades opening traced at last (work/h4_trace.py, game 1298212 vs 1790): pearls appear from r4, 13 and 16 path steps from our two heads; our dragons walk for 50 rounds, never nearer than 5 steps to a pearl (mostly 10 to 25)
  with 20 to 30 pearls on the board, eat nothing, and are rammed at r52 and r54. Their second dragon is next to a pearl at r11 and their side has 9 dragons at r50.
  New games, run 1200 (bar F10_new_games_2, after battle 1289717; 10 needed): 7 games on the four scarce layouts against 1900+: our share of pearls by r50 is 0.344 (44 against 84). All main: 0.276 on 58 games.
  New games, run 1500 (bar F10_new_games_2, after battle 1289717; 10 needed, now met): 11 games on the four scarce layouts against 1900+: our share of pearls by r50 is 0.342 (53 against 102). The line was 0.45: holds. All main: 0.327 on 108 games.
  New games, run 1800 (bar F10_new_games_3, after battle 1316833; 10 needed): 7 games on the four scarce layouts against 1900+: our share of pearls by r50 is 0.224 (43 against 149). In line. All main, all bands: 0.323 on 121 games.
would be wrong if: (03:10, passed, recounted) pooled share on scarce layouts 0.45 or more; fewer than 3 scarce layouts under 0.45 in both codes; share elsewhere under 0.47.
  (new games) weakened if, once 10 new main games on these four layouts against 1900+ exist, our share by r50 is 0.45 or more. 1 so far.
inferred: This is no longer one thing. Tower Defense is far pearls (F7). Stripes is the pocket rule (F18). Queen Of Spades and Trauma are not explained.
not checked: Queen Of Spades (we eat 0 by r50 in some games; first split r31 against r12) and Trauma (splits level, share 0.20).
look at: data/online/ladder/1259377/M1259378.replay r0-60 (Queen Of Spades vs 2011: we eat 0 by r50, they 28; our first split r52, theirs r11);
  data/online/ladder/1240151/M1240153.replay r0-50 (Trauma vs 1985: 2 against 22).
smallest test: none of its own; F7 and F18 carry Tower Defense and Stripes. For Queen Of Spades, trace one opening first (work/h4_trace.py prints it).

### F18 On Stripes our dragons pass up the pearl behind a portal nine times in ten; counted per dragon turn they still go through portals 0.7 times as often as opponents, and going in is usually fatal
status: weakened (the count holds, verifier 04:43; its size and its use do not; my own follow-up bar failed this hour)      first seen: 7 Oct 04:07 KST   last tested: 7 Oct 05:09 KST
measured (own counts, work/h5_decline.py and work/h7_pocket.py; a chance = a dragon turn that starts with a pearl on a free tile next to its head; passed up = it eats nothing that turn):
  General claim "we pass up adjacent pearls more than opponents do in r0-100": FAILED. main 0.203 against their 0.243 (29,539 and 31,816 chances); v31 0.199 against 0.229. We pass up fewer.
  Narrower claim "it is the bot's pocket rule (POCKET_CAP 48, POCKET_DIV 2, POCKET_PENALTY 1000)": FAILED. Where that rule applies we pass up 0.337 against their 0.358 (main) and 0.327 against 0.364 (v31);
  without Stripes 0.27 against 0.39 in both codes. On Portals, where three quarters of the pearls are born in rooms of 4 tiles or fewer, we pass up 0.31 against 0.43.
  What is left is Stripes (24 by 12, 2 starting dragons of length 2, 86 to 88 percent of pearls born in kelp-closed rooms of 3 or 4 tiles that are entered only through a portal):
  r0-100, all chances: main 0.69 against 0.25 (366 and 447 chances, 9 games); v31 0.62 against 0.21 (978 and 1,144, 26 games). Opponents under 1900: 0.77 against 0.22 (main), 0.62 against 0.25 (v31); 1900+: 0.66 against 0.25, 0.62 against 0.16.
  r0-199, the pearl is one step away through a portal into such a room: main 0.906 against 0.395 (385 and 301 chances); v31 0.867 against 0.375 (1,175 and 856).
  The pearl is in such a room and no portal step is needed (the dragon is already inside): 0.06 against 0.11 and 0.05 against 0.13. So ours eat once inside; they do not go in.
  By length on Stripes (main): length 2 passes up 0.84 (theirs 0.33), length 3 0.64 (0.10), length 4 or more 0.29 (0.26).
  Results on Stripes: every game ends by elimination (35 of 35); we are the side eliminated in 7 of 9 main games and 17 of 26 v31 games; in the 7 lost main games pearls by r50 are 1 to 8 for us and 10 or more for them in 6.
  Verifier, 04:43 KST: every number reproduced (0.906 against 0.395 main, 0.867 against 0.375 v31; our rate higher in 8 of 9 and 23 of 25 games; both rating levels). Read with it, all three accepted:
  - the rooms are 1, 3 or 4 tiles and the dragon that takes the pearl is dead within 10 rounds in two cases of three on either side (ours 23 of 36, theirs 134 of 182), against 0.11 and 0.20 after passing up.
    Passing up is declining a dead end; the count does not show that taking pays;
  - per dragon it is less stark: 31 of our 60 dragons with such a chance took one at some point (theirs 158 of 178), and five waiting dragons supply 150 of our 385 chances;
  - it is a Stripes fact, not a portal fact: through portals elsewhere we pass up less than they do (0.40 against 0.56).
  New this hour, own count (work/h9_pass.py; bar from 04:21 KST): portal steps per non-queen dragon turn in r0-100. Stripes: main 78 steps in 1,900 turns against their 213 in 3,537 (ratio 0.68);
  v31 254 in 5,539 against 524 in 8,302 (0.73). Portals: 1.87 and 1.98 times as many as opponents. So our dragons do go through portals on Stripes, about 0.7 times as often.
  Results on Stripes now: main 10 games, 2 won, eliminated in 8 (new: vs 2140, queen rammed at r36, eliminated r136).
  New this hour, not re-counted: one Stripes game (vs 1873), won by elimination at r283 with 6 pearls against 12 by r50. Stripes on main: 11 games, 3 won.
would be wrong if: (04:07) our pass-up rate / theirs under 1.5 on main or v31, or above 1.25 on fewer than 60 percent of layouts. FAILED: 0.84 and 0.87; 4 of 18 and 4 of 19 layouts.
  (04:13) pocket bar: under 2 times theirs on pocket chances, or under 1.5 times without Stripes. FAILED: 0.94 and 0.90; 0.71 without Stripes.
  (04:21, counted 05:09) F18_portal_steps: wrong if on Stripes our portal steps per dragon turn are 0.5 or more of theirs in either code. FAILED: 0.68 and 0.73.
  The Stripes numbers were looked at after the first two failures; nothing about them was predicted.
inferred: We lose Stripes (2 of 10 on main, 9 of 26 on v31) and we are slower there to enter the pearl rooms, but the nine-in-ten figure overstates it: a few dragons waiting at a portal mouth pile up chances,
  and entering a 3 or 4 tile room kills the dragon two times in three for both sides. Opponents accept that trade (enter, eat, split, die) and we mostly do not. Whether accepting it wins Stripes is not shown.
  One layout cannot show a map property; see F23 for the other layout with pearl rooms behind portals, where the problem is the opposite one (our queen goes in).
not checked: which branch of score_portal_step() refuses the step (needs the bot run on the replay, or a local game with a print); why Portals differs (3 starting dragons of length 3; rooms of 1, 2 and 4 tiles).
look at: data/online/ladder/1254072/M1254072.replay r10-45 (Stripes vs 2030: our dragon 2 circles tiles 17,7 17,8 18,8 18,7 for 35 rounds; the west edge of 17,8 is a portal edge and a pearl sits one step behind it every time it passes;
  their dragon enters the matching room at r9, eats two, splits, and repeats at r30 and r43). work/h4_trace.py and work/h4_draw.py print the trace and the board.
smallest test: low priority. If the team wants it: local games on Stripes with a default-off switch that lets a non-queen dragon of length 2 or 3 take a portal whose exit tile holds a pearl when it can split inside
  (so the room trade is eat, split, lose one half). Pass mark to write first: our pearls by r50 on Stripes rise from 4 to at least 10 and eliminations against us fall below half.

### F8 The opponent is the one who rams in two thirds of head-on meetings
status: confirmed (verifier: holds); re-counted on all games this hour      first seen: 7 Oct 03:06 KST   last tested: 7 Oct 06:06 KST
measured (own count last hour, recounted exactly by the verifier): share of cross-team head-on meetings in which their dragon was the mover: main 0.657 (8,313 meetings, 210 games); band b 0.701; band c 0.630;
  half 1 0.639; half 2 0.671; v31 0.675 (16,491 meetings). Above 0.5 for 22 of 24 opponents (v31 40 of 43) and in 129 of 181 main games that are not level.
  Verifier: not a head-count effect (we have half the living dragons) and not our short dragons standing in the way (0.67 where both are longer than 2). The layout matters: 0.32 to 0.82;
  the five large layouts and Slithery Fight hold 61 percent of the meetings, all at 0.65 or more; on Prisoners Dilemma 1 and 2, Autarky, Devil and weakhold it is at or under one half.
  Cost, two bars written first, both FAILED last hour: we lose less length than they do (ratio 0.90, interval 0.86 to 0.94), and teams that ram more do not beat us more (rank correlation +0.01 main, -0.37 v31).
  Re-test this hour (own count, work/h9_pass.py, all 235 main games): their mover share 0.665 (9,460 meetings); on the 25 main games after battle 1265766 it is 0.720 (1,147 meetings).
  By band: main 1700-1899 0.721, 1900-2099 0.624, 2100+ 0.722 (15 games); v31 0.638, 0.708, 0.765.
  Place (bar from 04:21 KST, FAILED): on layouts with 1500 or more open tiles the meetings they start are within 2 tiles of a busy tile in 0.303 (main, 4,284 meetings) and 0.284 (v31, 7,756);
  the meetings we start in 0.307 (1,517) and 0.306 (2,614). Their rams are not aimed at the busy tiles.
  Re-count this hour (work/h9_pass.py, all 255 main games): 0.675 (10,457 meetings); bands 0.718, 0.636, 0.753; the 20 new games 0.771 (997 meetings).
  Not re-counted this hour (the h9 pass was not rerun).
would be wrong if: their mover share under 0.58 in any of band b, band c, half 1, half 2 or on v31; or above 0.5 for fewer than 70 percent of opponents. Passed, recounted.
inferred: Opponents take the one-for-one head-on far more readily than we do; main.cpp allows a ram only by a dragon of length 4 or less against a target of at least 5 parts or its own length plus 2
  (TRADE_TARGET_MIN_PARTS 5, TRADE_EVEN false, TRADE_MIN_UNITS 8, TRADE_LOCAL_EDGE 1). No count shows that this costs us games. The layouts where they ram most are the layouts of F20 and F11, so the
  rams may be how they clear our dragons off the busy tiles; that is a guess.
not checked: nothing further planned. Three bars about what the rams cost or aim at have now failed (length lost, teams that ram more, rams at busy tiles). The one place where rams do cost is the queen: F13 and F24.
look at: data/online/ladder/1256635/M1256637.replay r91-200 (Australia vs 1924: 88 meetings, they are the mover in 97 percent);
  data/online/ladder/1240862/M1240862.replay r34-100 (Slithery Fight vs 1814: 105 meetings, 91 percent, and we won).
smallest test: none.

### F15 Our "no action" deaths are feeder deaths and they work; this is not a fault
status: confirmed (verifier: holds)      first seen: 7 Oct 02:09 KST (as a note)   last tested: 7 Oct 03:43 KST (verifier); not re-counted on the 25 games since
measured (own count last hour, recounted exactly): main 5,895 deaths in 210 games, none before round 201; 92.8 percent within 8 tiles of one of our dragons at least twice as long; of 8,565 pearls dropped
  our side ate 80.4 percent within 15 rounds, the opponent 3.3 percent. Same in both rating bands. v31: 10,326 deaths; 93.0, 79.4 and 3.5 percent.
  Verifier: a rule and not a crash (every one is a plain no-action reply in the dragon's own turn, one of our heads within 3 tiles in all of them, no enemy head within 3 in any).
  Two limits it adds: we get back 0.445 of the length given up (a body drops one pearl per two segments); and it is no edge, opponents' own no-action deaths are eaten by their side at 0.84.
would be wrong if: fewer than 80 percent within 8 tiles of an own dragon twice as long; our side eats under 70 percent of the drop; the opponent eats more than 15 percent. Passed, recounted.
inferred: ready_to_die() in main.cpp doing what it was written to do. The team's question "deliberate or a fault" is answered: deliberate.
not checked: whether feeding is the right call in each game (it wins the both-queens-dead games: 73 of 117 on main).
look at: data/online/ladder/1246505/M1246508.replay r300-499 (Maze vs 1776: 93 feeder deaths after r300, our longest ends at 85 against 29, won).
smallest test: none needed.

### F16 With the same number of dragons, more pearls are born beside their dragons than beside ours
status: candidate (the same thing as F20 seen from the pearls; its proposed cause is refuted)      first seen: 7 Oct 03:17 KST   last tested: 7 Oct 04:10 KST
measured (own count, work/h3_reach2.py last hour, work/h4_pass.py this hour): natural pearls born when the sides are within 10 percent in dragons alive, within 6 tiles of their heads only / of ours only.
  Last hour: main 1.37, v31 1.35, carried by Around UNSW (1.72, 1.67) and Slithery Fight (1.44, 1.55); other layouts 0.74 to 1.27.
  This hour, the test of last hour's guess that our feeding from round 200 opens it. By hundred rounds on those two layouts: main r0-99 1.26, r100-199 1.71, r200-299 1.55, r300-399 1.59;
  v31 1.10, 1.67, 2.04, 2.03. The surplus is already there in r100-199, before any feeder death (none happens before r201).
would be wrong if: (03:19, passed) ratio under 1.25 in any of main b, main c, v31 b, v31 c.
  (03:24, counted 04:10) feed-cap bar: the ratio in r200-299 is less than 0.15 above r100-199. FAILED on main (1.55 against 1.71); on v31 it rises but from 1.67, not from under 1.25.
inferred: Feeding at round 200 (FEED_CAP_ROUND, FEED_CAP_UNITS) is not the cause. The gap opens between r100 and r200 on the two layouts where both sides have 50 to 60 dragons. See F20.
not checked: nothing further planned under this number.
look at: as F20.
smallest test: none of its own; see F20. FEED_CAP_UNITS 0 is not supported as a test by this count.

### F4 Teams rated 2100+ are ahead of us by round 100 because they eat more, not because they split earlier or kill more of ours
status: candidate (the bar on the first 10 new main games passed narrowly: behind at r100 in 6; 53 of 70 in all; nothing of its own to test)      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 18:20 KST (rows.jsonl, new games)
measured: v31, 48 games against 2100+: dragons alive at r100 24.0 against 30.9; deaths in r0-100 40.0 ours against 42.0 theirs; splits by r100 59.3 against 68.2; pearls in r0-100 134 against 174.
  main, 9 games: alive 23.7 against 41.0, deaths 36.6 against 45.6, pearls 125 against 212. Against bands b and c the same numbers are level. 5th split round differs by 1 (F4b failed last hour).
  By layout (v31, share of pearls by r100 against 2100+): Stripes 0.07, Tower Defense 0.08, Trauma 0.18, Australia 0.27, Schooltime 2 0.27, Queen Of Spades 0.31, Around UNSW 0.36, Islands 0.39; level elsewhere.
  main has still 10 games against 2100+ (1 won, 2 battles lost). Nothing new this hour.
  New this hour: lost 0-5 to a 2140 team. Behind in total length at r100 in 3 of the 5 (Stripes 2 against 39, Schooltime 2 31 against 81, Around UNSW 147 against 227), level on weakhold (30 against 30), ahead on Portals (40 against 23).
  main against 2100+ now: 1 won of 15, 0 of 3 battles; dragons alive at r100 20.9 against 33.1; pearls in r0-100 110 against 172.
  How those 15 ended: only their queen alive in 8 (6 on the queen rule, 2 eliminations), both queens dead 6, both alive 1. Our queen was alive at the end in none. See F24.
  F20 (heads at busy tiles) does not grow with rating, so it is not part of what the top teams add.
  New this hour: the first battle won against a 2100+ team (3-2 against a 2111 team: Trophy and Queen Of Spades by elimination, Maze on longest dragon; lost Around UNSW on the queen rule and Schooltime 1 on longest dragon).
  The bar on 10 new games held narrowly: behind at r100 in 6, level in 1, ahead in 3 (the wrong-if line was 5 or fewer); 3 of the 10 won.
  main against 2100+ now: 4 won of 20, 1 of 4 battles; dragons alive at r100 23.9 against 32.1; pearls in r0-100 111 against 163. Endings on free layouts (17 games): only their queen alive 9, both dead 7, only ours 1.
  No game against a 2100+ team this hour. main against 2100+: 4 won of 20, 1 of 4 battles. F31 applies to every band alike (pearl ratio at round 150 on big layouts: 0.77, 0.76, 0.79 by band), so it is not something the top teams add.
  No game against a 2100+ team this hour either. main against 2100+: 4 won of 20, 1 of 4 battles.
  Run 0900: lost 0-5 to a 2105 team (and 0-5 to a 2067 team). The bar is complete: in the 10 main games against 2100+ since it was set we were behind at r100 in 7 (this hour weakhold 23 against 24, Portals 36 against 60, Default 31 against 42, Schooltime 1 16 against 57; ahead on Slithery Fight 174 against 164). The line was 5 or fewer: holds.
  main against 2100+ now: 4 won of 25, 1 of 5 battles, four opponents. Dragons alive at r100 23.4 against 31.0; pearls in r0-100 120 against 160; behind in total length at r100 in 18 of 24. Endings on free layouts (20 games): only their queen alive 10, both dead 9, only ours 1.
  In the lone-queen count of this hour (F39) the top band looks like the others; in the narrow-tile count (F38) too. Nothing new that only the top band does.
  Run 1000: no game against 2100+ this hour. main 4 won of 25 against 2100+. Bar F4_2 (next 10 games) waits.
  New games, run 1200 (bar F4_2, saved in run 1000; 10 main games against 2100+ after battle 1289717, now met): behind in total length at r100 in 8 of 10 (two of the 8 are games in which we were wiped out before r100). The line was 5 or fewer: holds.
  The two battles: lost 1-4 against 2474, won 3-2 against 2195, the first battle won against a 2100+ team (main is now 8 games of 35 and 2 battles of 7 there).
  Against 2474: wiped out at r93 (Devil), r99 (Trophy) and r109 (Prisoners Dilemma 1); total length at r50 was 9 against 26, 12 against 54 and 3 against 34. Slithery Fight wiped out at r441. The one win is Maze on longest dragon, 25 against 21, with 591 pearls against 2,463; their queen died at r489 with no action sent.
  Against 2195: Devil won by wiping them out at r125 (77 against 3 at r100); Schooltime 1 and Slithery Fight won on longest dragon with much less total length (44 against 295; 165 against 319). Lost Prisoners Dilemma 2 (r191) and Stripes (r213) by elimination.
  Seen after these games, not under a bar: wiped out by r125, main: 4 of 145 games against 1700-1899, 6 of 185 against 1900-2099, 6 of 35 against 2100+ (three opponents); we do it to them in 8, 10 and 1. v31: 1 of 210, 10 of 135, 4 of 50.
  So against 2100+ one game in six is over by round 125. All six are on layouts of 1200 cells or fewer. A lead for next hour (bar F44).
  New games, run 1500 (bar F4_3, after battle 1302921; the first 10 main games against 2100+): behind in total length at r100 in 8 of 10. The line was 5 or fewer: holds. All 20 new games against 2100+ (four battles against teams rated 2421, 2127, 2425, 2309; all four lost, 5 games won): behind in 16.
  All main against 2100+: behind at r100 in 43 of 55 (0.78); against 1900-2099 102 of 200; against 1700-1899 70 of 170. Against 2100+ we win 6 of the 43 in which we are behind and 7 of the 12 in which we are not. main is now 13 won of 55 games and 2 of 11 battles against 2100+.
  What the gap is made of on small layouts, new this hour: F44 (wiped out by round 125 in 7 of 32) and F7 (on 2-dragon-start layouts a 2100+ team is still under 7 dragons at r100 in 2 of 19 games, a 1700-1899 team in 35 of 72; we are in 10 of 19 and 29 of 72).
  New games, run 1800 (bar F4_4, after battle 1316833; the first 10 main games against 2100+): behind in total length at r100 in 6 of 10. The line was 5 or fewer: holds, narrowly. All 15 new games against 2100+ (three battles against teams rated 2175, 2180 and 2408; all lost, 4 games won): behind in 10. All main: 53 of 70.
  How games against each band end (rows.jsonl, run 1800; share of games against 1700-1899, 1900-2099, 2100+). main: wiped out in any round 0.10, 0.16, 0.30 (19 of 190, 33 of 210, 21 of 70); lost with both queens dead 0.15, 0.14, 0.20; lost with only their queen alive 0.09, 0.12, 0.20.
  v31: wiped out 0.16, 0.21, 0.22; both queens dead 0.14, 0.19, 0.32; only their queen 0.10, 0.12, 0.20. So on main the top band's extra losses are mostly wipe-outs; on v31 they were mostly both-queens-dead endings.
would be wrong if: in the next 10 main games against 2100+ we are behind at r100 in 5 or fewer. 5 arrived: behind in 3, level in 1, ahead in 1. Not decided.
inferred: The top teams are the strongest case of F7, F18, F10 (the 2-start openings) and of F11 and F20 (large layouts), not a separate thing. On large layouts our r101-300 share falls with rating: 0.38, 0.31, 0.26 (main).
not checked: the F20 count has not been split by opponent rating; it should be (bar for next hour in state.json).
look at: data/online/ladder/1249035/M1249035.replay r0-100 (Around UNSW vs 2382: pearls 141 against 392 by r100).
smallest test: none of its own.

### F6 On corridor-heavy layouts with slow pearls we are behind at round 100 in four games out of five
status: weakened      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 04:03 KST (1 new game)
measured: The group is Maze and Tower Defense only. main behind in total length at r100 in 26 of 31 games last hour; this hour one more Maze game (48 against 86 at r100, won). v31 31 of 46.
  The two layouts behave differently: on Maze our pearl share by r50 is 0.50 and we pass up fewer adjacent pearls than opponents (0.09 against 0.17); Tower Defense is F7.
would be wrong if: (first hour, narrow pass on v31) the share there is under 0.60 or less than 20 points above the other layouts.
inferred: Not a map property. It is "Tower Defense, see F7". Moved to weakened because no second layout behaves like Tower Defense.
not checked: nothing further planned.
look at: data/online/ladder/1241400/M1241402.replay r0-100 (Tower Defense vs 1934).
smallest test: none; covered by F7.

### F3 Our queen ends boxed in (no safe step) more often than theirs
status: candidate (it has held in every block of new games; the pooled margin is beyond chance, each block alone is not)      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 11:12 KST (rows.jsonl, new games)
measured: Queen deaths by wall or own body on free layouts, main: ours 47, theirs 25 in 193 games. The verifier showed last hour that these are queens with no safe step (trapped), 49 against 32 whatever they then hit,
  and that 13 of the 19 excess games fell in one hour. New games since the bar: 25, ours 8, theirs 5.
  Totals now: 48 against 26 in 201 main games on free layouts; since the bar 33 games, 9 against 6. Seven of our 48 are Portals, where it is a different thing (F23): without Portals 41 against 24.
  The same surplus shows up in which queen dies first (F21, refuted as a general claim): when ours dies first it is by wall or own body in 36 of 105 games, theirs in 13 of 73.
  Re-test this hour: 49 new main games on free layouts since the bar (40 needed): ours 13, theirs 9. Ours is above theirs, so it is not refuted; the margin is inside chance. Totals 52 against 29 in 217 games; without Portals 44 against 26.
  Re-count this hour: 73 new main games on free layouts since the bar: ours 19, theirs 10 (z about 1.9). Totals 58 against 30 in 241 games (z about 3.3). This hour alone 6 against 1: wall on Maze r88, Tower Defense r132 and Islands r102; own body on Tower Defense r358, Stripes r99 and Maze r118.
  It has now held in every block of new games (8 against 5, 9 against 6, 13 against 9, 19 against 10), so the earlier worry that one hour carried it is weaker. Moved back from weakened to candidate; not queued, the verifier's reading (a boxed-in queen, about 1.5 to 1) stands.
  Re-count this hour: 61 against 30 in 255 main games on free layouts. Since the first bar 87 games: 22 against 10. Third bar (after battle 1281566; 40 needed): 14 games, ours 3 (own body on weakhold r156, Stripes r131, Prisoners Dilemma 2 r134), theirs 0.
  New this hour (F37): the surplus has a window. In r101-200 it is 21 against 1 on main and 30 against 11 on v31 (games reaching r200, queens alive at r100); in every other window the two sides are level. Maze holds 8 of the 21 and 11 of the 30.
  New games, run 0900 (bar F3_3, after battle 1281566; 40 needed): 32 main games on free layouts, queen deaths by wall or own body 7 against 2. Totals main: 65 against 32 in 273 games. Where and how: F38 (60 of the 65 start on a narrow tile).
  New games, run 1000 (bar F3_3, after battle 1281566; 40 needed, now met): 48 main games on free layouts; queen deaths by wall or own body ours 10, theirs 3. Not refuted; the fourth block of new games in the same direction.
  Totals main: 68 against 33 in 289 games on free layouts. F37 (the window) and F38 (the tiles) are the confirmed form of this finding.
  New games, run 1100: 18 main games on free layouts; queen deaths by wall or own body ours 2, theirs 1. Totals main: 70 against 34 in 307 games.
would be wrong if: moves to refuted if, once 40 new main games on free layouts exist, ours is not above theirs. 33 so far: 9 against 6.
inferred: A modest difference (about 1.5 to 1) in how often the queen gets boxed in. The usable detail stays: a trapped queen of theirs more often rams a head; ours takes the wall.
not checked: what boxed her in.
look at: data/online/ladder/1233593/M1233594.replay r172 (Maze, wall, length 2, lost).
smallest test: no change yet.

### F2 After head-on meetings the opponent eats more of the dropped pearls than we do
status: weakened      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 03:05 KST (not re-counted this hour)
measured: main, 210 games: share 0.399 of head-on drops eaten within 15 rounds. The verifier showed 0.40 is also our share of all pearls in those games, and that the mover's side takes the drop.
would be wrong if: share 0.47 or more in any of the four slices; band b reaches 0.504 in the verifier's interval.
inferred: Not a finding of its own; it is F8 seen through the pearls.
not checked: nothing further planned.
look at: data/online/ladder/1256635/M1256637.replay (Australia vs 1924).
smallest test: none.

### F1 Being behind in total length at round 100 means the game is mostly lost
status: weakened      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 10:05 KST (rows.jsonl, new games), narrow claim only
measured: main against 1900+: 25 won of 79 games in which we were behind at r100. New since the bar: 7 such games, 3 won (this hour: Around UNSW and Maze against 2032 were both won from behind).
  Against 1700-1899 the first-hour bar failed (13 of 24 won from behind).
  Totals now: 25 won of 82. New since the bar: 10 such games, 3 won. Counted this hour for F22: we win 24 of the 81 main games in which we trail by 20 percent or more at r200.
  Re-count this hour: 27 won of 87; new since the bar 15 games, 5 won (20 needed).
  Re-count this hour: 27 won of 89; new since the bar 17 games, 5 won (20 needed).
  No change this hour: 27 won of 89; new since the bar 17 games, 5 won (20 needed).
  Run 0900, bar F1b (the narrow claim; 20 games needed): 28 main games against 1900+ in which we were behind in total length at r100, 7 won (0.25). The line was 0.45: the narrow claim holds. The general claim stays weakened.
  Run 1000: behind at r100 against 1900+ in 7 new games, 3 won (Trauma, Slithery Fight, Schooltime 2, all at round 500). Since bar F1b: 35 games, 10 won.
would be wrong if: against 1900+ we win 0.45 or more of games behind at r100, once 20 such new games exist. 10 so far, 3 won.
inferred: An early deficit against 1900+ teams is recovered in about a third of games; when it is, both queens are usually dead and feeding decides.
not checked: whether total length is the right yardstick.
look at: data/online/ladder/1267969/M1267971.replay (Maze vs 2032, new: 48 against 86 at r100, won on longest dragon).
smallest test: none.

### F43 Their queens grow long and that keeps them alive
status: refuted (line b failed on both codes; line a between the lines)      first seen: 7 Oct 15:42 KST run 20261007-1500   last tested: 7 Oct 15:42 KST (rows.jsonl)
measured: rows.jsonl, free layouts, games that reached r400; queens alive at r300. Long = 10 or more at r300, short = 4 or less.
  (a) Their queens alive at r300 are long in 25 of 107 (main, 0.23) and 20 of 87 (v31, 0.23). Ours in 3 of 73 and 0 of 45. So theirs do grow more often than ours; I claimed 30 percent for theirs.
  (b) Alive at the end: a long queen of theirs 16 of 25 (main) and 12 of 20 (v31); a short one 50 of 75 and 32 of 50. Long minus short: minus 3 and minus 4 points. Ours: short 24 of 50 and 14 of 31; 5 to 9 long 13 of 20 and 9 of 14.
  (c) Long share of their queens against 1900+ minus against 1700-1899: main 14 of 66 against 11 of 41 (minus 6 points); v31 13 of 42 against 7 of 44 (plus 15).
would be wrong if: (F43, saved 12:42 before the count) (a) theirs under 20 percent or ours 20 percent or more; (b) the gap under 5 points on main or on v31; (c) under 5 points on both codes.
  (a) not wrong, claim not met (0.23). (b) FAILED on both codes. (c) not wrong by the letter (v31), reversed on main: no rating effect shown.
inferred: with F36 this closes the idea twice: a longer queen is not a safer queen, for them or for us. Growing our queen is not a test worth a slot. F42 is about nobody going to their queen, not about her size.
not checked: queens of 5 to 9; length earlier than r300.
look at: none.
smallest test: none.
### F41 On 2-dragon-start layouts we take twice as long as the opponents to the first meal when no pearl is near, because our dragons walk straight on when they see nothing
status: refuted (both bars failed; the second came out reversed)      first seen: 7 Oct 11:06 KST run 20261007-1100   last tested: 7 Oct 11:09 KST
measured: own count, work/h23_pass.py (all 325 main and v31 games on the seven layouts where each team starts with 2 dragons, raw rounds 0-100, 0 errors).
  T0 = the first raw round in which a dragon turn starts with a pearl on the board (one turn finer than the wording of the bar; the same for both sides). Far = no pearl within 7 path steps (kelp and portals respected, dragons ignored) of any head of that side at T0.
  Delay = raw round of the side's first meal minus T0; no meal by r100 counts as 101 minus T0.
  Both sides far (283 of the 325 games): median delay ours 14 against theirs 12 on main (133 games, 1.17 times); 13 against 10 on v31 (150 games, 1.30 times). Without Tower Defense, both codes: 12 against 10 (238 games, 1.2 times). I had claimed twice; the line was 1.3.
  We are the later side in 170 of those 283 games and the earlier one in 78: later more often than not, by two to four rounds at the median. No meal by r50: ours 18 games, theirs 9. Pearls by r50 in those games: 4,139 against 4,721. We won 142 of the 283.
  Both sides near (38 games): 4 against 4.5 rounds; pearls by r50 1,194 against 1,143; 24 won.
  By layout (seen after the count), median delay ours against theirs, both codes: Queen Of Spades 23 against 10; Stripes 20 against 10; Trauma 32 against 19; Tower Defense 17 against 20.5; weakhold 10 against 10; Trophy 6 against 7; Maze 5 against 5.
  Straight steps (same pass, raw rounds 1-50). Turns that start with no pearl inside the 7 by 7 square round the head, in which the dragon moves by a plain step and its step before was plain too.
  Our dragons keep their direction in 0.462 of such turns (7,655 of 16,556) and theirs in 0.562 (9,022 of 16,061) on main; 0.450 (7,371 of 16,372) against 0.614 (10,620 of 17,310) on v31. Ratio 0.82 and 0.73; I had claimed 1.2 or more.
  Ours is the lower one on all seven layouts (Tower Defense 0.38 against 0.60, weakhold 0.42 against 0.59, Trophy 0.40 against 0.55, Maze 0.43 against 0.53, Trauma 0.55 against 0.68, Queen Of Spades 0.54 against 0.63).
  A dragon starts a turn with no pearl in view in 0.49 of turns (ours) and 0.48 (theirs) on main, 0.45 and 0.46 on v31: the two sides see pearls equally often.
would be wrong if: (F41_first_meal, saved 11:06 before the pass existed; seen before it: one traced opening, Queen Of Spades vs 1790, the curves of five losses of this hour and the F7 and F10 blocks)
  (a) both sides far: our median delay under 1.3 times theirs on main or on v31. FAILED on main (1.17); v31 sits on the line (1.30). (b) without Tower Defense, both codes pooled, under 1.3. FAILED (1.2). (c) both sides near: ours 1.5 times theirs or more. Not crossed (0.9).
  (F41_straight, saved 11:06) our share of straight turns under 1.1 times theirs on main or v31. FAILED, reversed: 0.82 and 0.73.
inferred: What this hour's four losses on small 2-start layouts have in common is not a late first meal and not straight-line walking. The traced game is not typical: over all games our dragons turn more often than the opponents' dragons when they see nothing.
  That reversed number is a lead, not a finding (seen after the count). A dragon that keeps its direction brings new tiles into view on every step; one that turns about every second step looks again at ground it has seen.
  It would fit F7 (on Tower Defense both sides see a pearl equally rarely and theirs get next to one sixteen times as often). The three layouts where our first meal is about twice as late are three of the four F10 layouts; also seen after the count.
not checked: whether straighter walking is why their dragons reach pearls sooner (bar F7_sweep in state.json for next hour: new tiles brought into view per blind step); what our dragons steer by when they turn; the opponents are a mix of bots.
look at: data/online/ladder/1298211/M1298212.replay r0-54 (Queen Of Spades vs 1790: pearls from r4, 13 and 16 path steps away; we eat nothing in 54 rounds and are wiped out);
  data/online/ladder/1298211/M1298211.replay r0-200 (Tower Defense vs 1790: first meal at r20, then 8 pearls by r200 against 165).
smallest test: none of its own. The test of F7 stands (EXPLORE_GAIN above 0 while we have 3 or fewer dragons and no pearl in sight). Count first: bar F7_sweep.

### F40 On big layouts the leader phase costs games when it starts before our board is full (under 55 dragons at round 150)
status: refuted (my bar failed on main and on v31)      first seen: 7 Oct 10:09 KST run 20261007-1000   last tested: 7 Oct 10:10 KST
measured: rows.jsonl, layouts above 1200 cells, games that reached r300: main 104 of 105, v31 118 of 119. Split by our dragons alive at r150.
  main: under 55: 35 games, 5 won; our count changes by a median of minus 9 by r300, theirs by plus 3. 55 or more: 69 games, 35 won; ours minus 6, theirs plus 1. v31: under 55: 46 games, 11 won, minus 9 and plus 1. 55 or more: 72 games, 37 won, minus 6 and plus 2.
  Under 55 is mostly already behind: our count at r150 is under 0.9 of theirs in 26 of the 35 main games (1 won) and 44 of the 46 v31 games (10 won). With a count at least 0.9 of theirs: under 55, 9 games, 4 won (main; v31 2 games); 55 or more, 67 games, 33 won (v31 71, 37 won).
  Finer, ours at r150, games and wins, main: 0 to 29: 19 and 4; 30 to 44: 14 and 1; 45 to 54: 2 and 0; 55 to 59: 15 and 4; 60 or more: 54 and 31. v31: 16 and 0; 15 and 5; 15 and 6; 12 and 4; 60 and 33.
  Inside layouts. Australia: under 55 1 won of 10, 55 or more 3 of 11 (main); 2 of 14 and 7 of 13 (v31). Islands: 0 of 8 and 0 of 6 (main); 0 of 9 and 1 of 8 (v31).
  On Islands with 55 or more at r150 our count still falls by a median of 44 (main) and 21 (v31) by r300 while theirs rises by 17 and 16.
  Per game on Islands in r101-300 (main, 15 games): our deaths 112 (head-on 64, wall 20), theirs 202 (head-on 71, wall 63); pearls eaten 255 against 777. v31 (17 games): deaths 141 against 197; pearls 338 against 787.
would be wrong if: (saved 10:09 before any per-game count; the per-layout means had been seen) on main or v31: among games with our count at r150 at least 0.9 of theirs the under-55 group wins 0.7 or more as often as the 55-plus group (10 games a cell needed);
  or the median change of our count from r150 to r300 in the under-55 group is above minus 5; or the median change in the 55-plus group is minus 5 or lower too. FAILED on the third clause on both codes (minus 6 and minus 6).
  The first clause has too few games (9 on main, 4 won, beside 33 of 67: no sign of an effect).
inferred: A full board at round 150 does not protect us. The count falls after round 150 either way, by about the same amount, and theirs does not. That is F31 again, not a new condition for it. Games with few dragons at r150 are lost because they were lost already.
  What is left is one layout. On Islands we have not won a main game that reached r300 (0 of 14; v31 1 of 17), full board or not. Their dragons die nearly twice as often as ours there and they eat three times as much, so it is eating, not dying (F11, F20, F26, F31).
not checked: making the leader phase wait for a dragon count is not ruled out as a change; only the claim that the cost sits in the under-55 games is. Islands is one layout (56 by 40, 12 portals, most pearls from fast tiles); Slithery Fight has as large a fast share and is won half the time.
look at: data/online/ladder/1293799/M1293799.replay r150-359 (Islands vs 2061: 45 against 46 dragons at r100, 44 against 61 at r150, 29 against 62 at r200, 5 against 61 at r300, wiped out at r359);
  data/online/ladder/1280772/M1280776.replay r150-300 (Islands vs 1873: 61 against 19 at r150, 42 against 62 at r300, lost).
smallest test: none of its own; the F31 test (LEADER_GROW_ROUND_BIG) covers it. Islands is the layout to run that test on first.

### F29 When both queens are dead at the end we lose on large layouts and win elsewhere
status: refuted as a property of size (bar failed on v31); what is left is two layouts, Australia and Islands      first seen: 7 Oct 07:03 KST run 20261007-0700   last tested: 7 Oct 07:04 KST
measured: rows.jsonl, free layouts, games with both queens dead that reached r499 (the longest dragon decides).
  Large free layouts (Around UNSW, Australia, Islands): main 13 won of 34 (0.38), v31 22 of 48 (0.46). Other free layouts: main 36 of 47 (0.77), v31 41 of 84 (0.49).
  By layout, main then v31: Around UNSW 9 of 11 and 14 of 19; Australia 4 of 14 and 7 of 20; Islands 0 of 9 and 1 of 9.
  In the lost large games (21 main, 26 v31), medians ours against theirs: dragons alive at r300 25 against 62 and 33 against 63; at r400 16 against 56 and 22 against 61; longest dragon at r300 11 against 20 and 11 against 19;
  final longest 21 against 46 and 21 against 51; pearls in r301-500 4,928 against 16,123 and 5,716 against 21,650. Our dragons at r400 are under half of theirs in 13 of 21 and 15 of 26.
  In the won large games: alive at r400 55 against 51 and 56 against 43; final longest 56 against 33 and 49 against 32.
would be wrong if: (07:03, before the count) (a) we win 0.45 or more of such games on large free layouts on main or v31, or the rate is less than 15 points below the other free layouts. FAILED on v31 (0.46 against 0.49).
  (b) in the lost large games our dragons at r400 are under half of theirs in under 40 percent. Not crossed: 62 and 58 percent. (c) only one of the three layouts under 0.45. Not crossed: two are.
inferred: Not a property of size. On Australia and Islands we lose the longest-dragon ending (12 won of 52, both codes); on Around UNSW we win it (23 of 30). The lost games are lost before the late feeding:
  at r300 they have 62 dragons to our 25 to 33 and the longer dragon. F31 shows when the dragon count turns on these layouts: round 151.
  Added 08:12 (F32): on big layouts this ending is decided by who has the longer leader at r300 (right in 29 of 34 and 37 of 44), not by total length. On Australia and Islands we are the side with the shorter leader at r300.
not checked: what separates Australia and Islands from Around UNSW. Three layouts cannot show a property (fast-tile share 0.52 and 0.84 against 0.31; wall share 0.08 and 0.23 against 0.10).
look at: data/online/ladder/1279530/M1279533.replay r150-499 (Australia vs 1870); data/online/ladder/1280772/M1280776.replay r200-499 (Islands vs 1873: total length 137 each at the end, longest 25 against 46).
smallest test: none of its own; see F31.

### F30 On large layouts our dragons leave adjacent pearls because an enemy head is near (the threat rule)
status: refuted (two of three bars failed; the excess is real but sits where no enemy is near; it led to F31)      first seen: 7 Oct 07:03 KST run 20261007-0700   last tested: 7 Oct 07:04 KST
measured (work/h5-shard files, 635 games up to battle 1270027; turns of non-queen dragons that start with a free pearl one step away, raw rounds 101-199; left = the dragon eats nothing that turn):
  Large layouts, all such turns: ours left 0.325 of 13,540, theirs 0.232 of 20,016 (main); 0.327 of 27,408 against 0.228 of 38,451 (v31).
  No enemy head within 2 tiles of the pearl: ours 0.318, theirs 0.226 (main); 0.323 and 0.221 (v31). An enemy head within 2: 0.397 against 0.325; 0.370 against 0.324.
  Pearl tile with two or more free exits: 0.222 against 0.123 (main), 0.243 against 0.113 (v31); one exit 0.34 against 0.23; dead end 0.66 against 0.64 (equal).
  Other layouts, r101-199: ours 0.225, theirs 0.252 (main); 0.208 and 0.249 (v31). Large layouts in r0-100 with no enemy near: 0.235 against 0.226; 0.238 against 0.224.
  By layout with no enemy near, ours minus theirs: positive on all six layouts above 1200 cells in both codes (main +0.05 to +0.15, v31 +0.07 to +0.16); between -0.11 and +0.03 on every layout of 1200 cells or fewer on main.
would be wrong if: (07:03, before the count) (a) our rate under 1.25 times theirs. Passed: 1.40 and 1.43 times. (b) with no enemy near, ours more than 3 points above theirs. FAILED: 9 and 10 points.
  (c) with an enemy near, ours less than 8 points above theirs. FAILED: 7 and 5 points.
inferred: The threat fields (SMALL_THREAT_MULT, PENALTY_HEAD_RACE) are not why we leave pearls on large layouts. The excess starts after round 100, only above 1200 cells, on open tiles with nobody near.
  That pattern is a rule of our own bot; F31 finds its round.
not checked: the h5 shards stop at battle 1270027.
look at: none needed.
smallest test: none; see F31.

### F32 In the both-queens-dead ending, more total length at round 300 beats a longer leader at round 300
status: refuted (my bar failed; on big layouts it is the other way round, which speaks for the leader phase)      first seen: 7 Oct 08:02 KST run 20261007-0800   last tested: 7 Oct 15:42 KST (rows.jsonl, new games)
measured: rows.jsonl, free layouts, both queens dead, round 500 reached. Games in which the two leads at r300 point to different sides: main 19, the side with more total length wins 6; v31 32, wins 20.
  By layout class, both codes: big layouts 5 of 20; other layouts 21 of 31. All non-tied games: on big layouts the longer leader at r300 wins 29 of 34 (main) and 37 of 44 (v31), more total length wins 26 of 36 and 33 of 48.
  On other layouts the longer leader wins 24 of 34 and 29 of 60, more total length 29 of 47 and 57 of 82.
  When we were the side with the longer leader and less total length on big layouts we won 7 of 10 (main) and 8 of 10 (v31); 13 of those 20 games are Around UNSW.
  By round on main big layouts (36 games), our leader ahead won-lost / behind won-lost: r150 6-8 / 7-13; r200 5-9 / 7-14; r300 11-4 / 1-18; r400 9-1 / 4-22.
  New games (bar F32_new, met in run 1100): 11 both-queens-dead non-tied main games on big layouts since battle 1285561; the longer leader at r300 won 9 (all main games: 47 of 55). The claim of this block was the reverse; it stays refuted.
  New games, run 1200 (bar F32_new_2, after battle 1298211; 10 needed): 2 both-queens-dead non-tied main games on big layouts; the longer leader at r300 won 2. All main: 49 of 57.
  New games, run 1500 (bar F32_new_2, after battle 1298211; 10 needed, now met): 14 both-queens-dead non-tied main games on big layouts; the longer leader at r300 won 12. The line was 6 or fewer: F32 stays refuted. All main: 59 of 69.
would be wrong if: (08:02, before the count; the verifier's F31 cost figures had been seen) among disagreement games the side ahead in total length wins under 55 percent on main or v31 (20 games needed in a code), or under 50 percent on big layouts or on the other layouts, both codes pooled.
  FAILED on big layouts (5 of 20). v31 alone passed (0.625); main had 19 games, one short, at 6 of 19.
inferred: On big layouts the leader at r300 is the currency of the both-queens-dead ending, and the leader phase earns it when it works (Around UNSW). On smaller layouts, where our leader phase has not started by r300, total length is the better sign (v31).
  This is the first count that shows a return on the leader phase. It does not say that round 150 is the right start: at r150 and r200 a longer leader predicts nothing.
not checked: whether a later start would give a longer or a shorter leader at r300 (local games; see F31).
look at: none needed.
smallest test: none; it sets the pass mark for the F31 test.

### F33 Opponents whose dragons die by no action instead of on walls beat us more
status: refuted      first seen: 7 Oct 08:05 KST run 20261007-0800   last tested: 7 Oct 08:06 KST
measured: rows.jsonl, per battle: their no-action deaths in r0-100 divided by their deaths other than head-on in r0-100. The kinds are real: the share is 0.0 to 0.2 in 121 battles and 0.7 to 1.0 in 19, nothing between.
  Our wins against the no-action kind and against the rest: v31 1700-1899 13 of 20 against 108 of 190; v31 1900-2099 14 of 30 against 47 of 105. main 9 of 15 against 66 of 100 and 10 of 15 against 73 of 140 (cells too small to count).
would be wrong if: (08:05, before the count; one opponent of each kind had been seen this hour) in any cell with 20 games of each kind our win rate against the no-action kind is less than 10 points below the rest. FAILED in both cells that count (8 points above, 2 points above).
inferred: How an opponent gets rid of its dragons (no action, wall, own body) marks a family of bots but not a stronger one. Our own dragons die on walls 13 times a game in r0-100 on main, 5 times on their own body, 6 times in head-on meetings.
not checked: nothing further.
look at: none needed.
smallest test: none.

### F36 A queen that has grown by round 200 lives longer
status: refuted      first seen: 7 Oct 08:10 KST run 20261007-0800   last tested: 7 Oct 08:11 KST
measured: rows.jsonl, full games on free layouts, their queens alive at r200, alive at the end by length at r200: length 5 or more 12 of 25 (main) and 18 of 36 (v31); length 3 or less 32 of 58 and 29 of 65.
  With their side behind in total length at r200, both codes: 5 of 15 against 25 of 51. Our queens alive at r200 are length 3 or less in 61 of 64 and 68 of 70 games (she splits until QUEEN_SPLIT_ROUND 200), so only their queens can be compared.
would be wrong if: (08:10, before the count) the difference is under 10 points on main or v31, or under 10 points with their side behind. FAILED: minus 7 points on main, plus 5 on v31, minus 16 when behind.
inferred: Letting the queen grow earlier (a lower QUEEN_SPLIT_ROUND, a QUEEN_KEEP above 0) is not supported by the ladder as a way to keep her alive. This agrees with the failed bar F13b of run 0300.
not checked: queens of length 10 or more (too few).
look at: none needed.
smallest test: none.

### F27 With their queen one step away our dragons take the ram less often than theirs do
status: refuted (bar failed on v31; main shows no difference)      first seen: 7 Oct 06:09 KST run 20261007-0600   last tested: 7 Oct 06:16 KST
measured (own count, work/h11_pass.py, 665 games; chance = a non-queen dragon starts its turn with the living enemy queen's head one open-edge or portal step away; free layouts):
  own queen of the acting side alive: v31 ours take the ram in 59 of 67 chances (0.88), theirs in 51 of 66 (0.77); main 37 of 39 and 30 of 31.
  Own queen dead: ours 31 of 32 (v31) and 27 of 31 (main); theirs 31 of 91 and 14 of 22. Opponents' dragons often leave our lone queen alone when one step away (on v31 she is alive 3 rounds later in 49 of 58 such cases).
  Chances are rare: 67 and 66 in 362 v31 games. About half of all rams on a queen start from farther than one step (F24, paid sprints).
would be wrong if: (06:09, before the count) with the own queen alive our take rate is 0.7 or more of theirs on main or v31 (100 chances a side needed; main has 39 and 31). FAILED on v31: 1.14 times.
inferred: We do not hold back from the queen ram. QUEEN_HUNT false does not show up as missed one-step rams.
not checked: chances within sprint reach (2 or 3 steps), which is where the top band's rams on our queen come from.
look at: none needed.
smallest test: none.

### F21 Our queen is the first of the two to die more often than theirs, in every slice
status: refuted as a general claim (two of three bars failed); its rating part passed and is kept as F24      first seen: 7 Oct 05:04 KST run 20261007-0500   last tested: 7 Oct 05:05 KST
measured: rows.jsonl, free layouts, games in which one queen died strictly before the other. Ours first: main 105 against 73 (0.590); 1700-1899 0.621; 1900-2099 0.551; half 1 0.500 (37 against 37);
  half 2 0.654; 2100+ 10 against 3. v31 182 against 159 (0.534): 1700-1899 0.492, 1900-2099 0.586, 2100+ 0.675. We win 46 of 105 (main) and 73 of 182 (v31) when ours dies first; 51 of 73 and 92 of 159 when theirs does.
  What the surplus is made of (main): wall or own body 36 against 13; standing victim of a ram 60 against 49. By layout it runs from Portals 8 against 1 (v31 27 against 0, see F23), Devil 13 against 2,
  Australia 10 against 2 to Queen Of Spades 6 against 10 and Default 5 against 9.
would be wrong if: (05:04) (a) ours first in under 0.53 in any of main 1700-1899, main 1900-2099, half 1, half 2, or v31 pooled: FAILED in half 1 (0.500). (b) v31 2100+ less than 10 points above 1700-1899: passed (18 points).
  (c) we win 0.40 or more of ours-first games: FAILED (0.44 main, 0.40 v31).
inferred: Not a universal weak point: against teams under 1900 the two queens die first about equally often, and losing the queen first still leaves us four games in ten. What is real in it is the rating slope (F24),
  the boxed-in deaths (F3) and one layout (F23).
not checked: nothing further under this number.
look at: none needed.
smallest test: none.

### F22 We throw away leads more often than opponents do
status: refuted (reversed on main)      first seen: 7 Oct 05:04 KST run 20261007-0500   last tested: 7 Oct 05:06 KST
measured: rows.jsonl, free layouts, lead = total length at least 1.2 times the other side at raw round 200. main: we lead in 57 games and lose 9 (0.16); they lead in 81 and lose 24 (0.30).
  v31: we lose 23 of 100 (0.23); they lose 26 of 132 (0.20). At r100 and r300 the same picture (main 8 of 73 and 5 of 32 against 21 of 77 and 23 of 80).
  Of our 9 lost leads on main, 5 ended with only their queen alive; by layout the 9 are weakhold 3, Portals 2, Maze 2, Islands 1, Australia 1.
would be wrong if: (05:04) (our loss rate when we lead) minus (their loss rate when they lead) under 5 points on main or v31. FAILED: -14 points on main, +3 on v31.
inferred: A lead at round 200 is kept five times in six. The two new games that prompted this (most of the pearls eaten, lost on the queen rule) are the exception, and their mechanism is the queen (F23, F24), not a habit of losing leads.
not checked: leads measured in pearls or dragons instead of total length.
look at: none needed.
smallest test: none.

### F17 When both queens are alive at round 500 ours is the shorter one and we lose
status: refuted      first seen: 7 Oct 04:02 KST run 20261007-0400   last tested: 7 Oct 04:04 KST
measured: Free layouts, both queens alive at the end: main 18 games, we win 12, our queen is the longer one in 12 (median length 36 against 21). v31 15 games, 11 won, ours longer in 11.
  And it is one layout: Trauma holds 16 of the 18 and 13 of the 15.
would be wrong if: we win 45 percent or more of these games, or our queen is the longer one in 45 percent or more, on main or v31; or one layout holds more than half. All three failed the claim.
inferred: On Trauma both queens usually live to the end and ours is usually longer. No weak point here. How main games end on free layouts (193): both queens dead 117 (73 won), only theirs alive 33 (0 won),
  only ours 25 (25 won), both alive 18 (12 won).
not checked: why queens survive on Trauma.
look at: none needed.
smallest test: none.

### F19 On large layouts our dragons are more bunched than theirs, and theirs push further into our half
status: refuted (both parts; the first came out reversed and led to F20)      first seen: 7 Oct 04:11 KST run 20261007-0400   last tested: 7 Oct 04:13 KST
measured (own count, work/h6_spread.py; snapshots every 25 rounds from r100 to r300 with dragon counts within 10 percent):
  a) median distance from a head to the nearest friendly head: ours is the smaller in 12 of 78 non-tied snapshots on main large layouts and 18 of 122 on v31. Slithery Fight 8 of 36 and 12 of 49. Theirs are the bunched ones.
  b) share of heads nearer to the enemy queen's spawn than to their own: ours 0.294, theirs 0.292 (main); 0.301 and 0.300 (v31).
would be wrong if: a) ours smaller in under 55 percent of non-tied snapshots; b) their share minus ours under 5 points. Both failed.
inferred: We are not clumped and they do not out-expand us. They are clumped, at the busy tiles (F20).
not checked: most balanced snapshots are Around UNSW.
look at: none needed.
smallest test: none.

### F9 Their rams kill our queen more often than our rams kill theirs
status: refuted      first seen: 7 Oct 03:04 KST   last tested: 7 Oct 04:08 KST
measured: Last hour: games with our queen rammed 83, theirs 89 (main, free layouts); v31 172 and 167. This hour's own count agrees: rams on our queen 87, on theirs 93 (main); 171 and 164 (v31).
  Added 05:11 KST: even when pooled, not even by opponent rating. See F24.
would be wrong if: the ratio is under 1.3 in any main slice or on v31. Failed everywhere on main.
inferred: Queen rams are even between the sides. What survives is in F13.
not checked: 2100+ teams look different but that is 53 games.
look at: none needed.
smallest test: none.

### F12 When only their queen is alive at round 300 we almost never turn the game round
status: refuted      first seen: 7 Oct 03:11 KST   last tested: 7 Oct 03:12 KST
measured: main: only their queen alive at r300 in 29 games; she dies later in 11; we win 8. v31: 69 games, 28, 15.
would be wrong if: she dies later in 20 percent or more, or we win 15 percent or more. Failed.
inferred: The revenge hunt plus feeding does turn a quarter of these games.
not checked: the games where she lived.
look at: data/online/ladder/1263705/M1263706.replay r276-499 (Maze vs 2022).
smallest test: none.

### F14 The common root of F10 and F11 is reach: pearls born far from both sides go to the opponent
status: refuted      first seen: 7 Oct 03:13 KST   last tested: 7 Oct 03:17 KST
measured: pearls born 7 or more tiles from both sides at balanced moments: our share 0.495 on main and on v31. Tower Defense alone 0.10.
would be wrong if: our share of far-for-both pearls is 0.45 or more. Failed.
inferred: Our dragons fetch far pearls as well as opponents do, except on Tower Defense. A general "pull from farther" change is not supported.
not checked: straight-line distance, not path.
look at: none needed.
smallest test: none.

### F5 In rounds 0-100 our dragons die on walls more often than theirs
status: refuted      first seen: 7 Oct 02:09 KST run   last tested: 7 Oct 03:10 KST
measured: ratio 1.12 against band c teams and higher on only 11 of 18 layouts; both first-hour bars failed.
would be wrong if: ratio under 1.15 in any main slice. Failed in band c.
inferred: Early wall deaths are normal play for both sides.
not checked: what the wall deaths are.
look at: none needed.
smallest test: none.

## Notes that are not findings
- How main games end on free layouts (255): both queens dead 152 (95 won), only theirs alive 45 (0 won), only ours 38 (38 won), both alive 20 (14 won).
  Eliminations against us: 36 of 295 main games; by us 76. Full games only (143): both dead 83 (49 won), only theirs 32, only ours 8, both alive 20 (14 won).
- main.cpp facts used above: a dragon sees 3 tiles (VISION_RADIUS 3); no memory of tiles where pearls reappear; EXPLORE_GAIN 0.0; QUEEN_DEFEND_RADIUS and QUEEN_GUARD_CELLS 0; QUEEN_NO_PORTAL true (a low score, not a rejection);
  QUEEN_HUNT false, the queen hunt (qh_) starts when our own queen is dead and the round is 100 or more. New this hour: AGGRESSIVE_MAX_CELLS 1200, LEADER_GROW_ROUND 300, LEADER_GROW_ROUND_BIG 150, LEADER_PEARL_RADIUS 9,
  ZONE_PEARL_PENALTY 600, SPLIT_MIN_LENGTH 4, SPLIT_SOFT_LIMIT 60, SONAR_STALE 25 (F31).
- In 252 of 253 rams on our queen the ram came in the same round as her last move: she had moved first, and the rammer started from where it stood when she chose her step.
- Our queen is 2 long (median) when she is rammed, in every band; a queen of length 2 has one step a turn and nothing to pay with.
- Earlier team counts read as leads (run 0600), set beside the ladder:
  data/local/hunter38/deaths/summary.md says that in 26 of 33 head-on queen deaths she "had a safe move"; that is measured at the start of the rammer's turn, when she can no longer move.
  Measured at her own last turn with the full-reach rule, the ladder gives a safe step in 18 of 95 rams on main and 76 of 170 on v31. The ladder does not support "she usually had a safe move" for main.
  data/online/smoke/bbb-analysis-3/summary.md (one opponent) lists the rammer 2 to 6 tiles from our queen at round start in most rams. The ladder agrees on v31 (paid sprints, F24); on main it is not shown.
  data/online/smoke/drop-analysis/summary.md (one opponent): they eat 59 percent of the pearls our dragons drop in head-ons. On the ladder this is F2: our share is 0.40, and it is our share of all pearls, not a head-on fact.
  data/online/smoke/fountain-analysis-2/summary.md (one opponent; heads near fast tiles 7.9 against 24.2 in r101-200 on Around UNSW and Australia): the ladder has it as F20 at equal dragon counts, and F31 now adds that our eating falls at round 151 on exactly those layouts.
- Not re-counted on the new games this hour (no earlier replay pass was rerun): F8, F20, F26, F28, the F13 lone-queen ram counts, the F24 sprint counts, F15, F2, F16, F18. The work/h10-shard files used for F34 and F35 stop at battle 1276407 (665 games).
- main.cpp facts read this hour: the queen splits like any dragon until round QUEEN_SPLIT_ROUND 200 (QUEEN_KEEP 0, QUEEN_SPLIT_CLEAR 0), so she is 2 or 3 long until then; a queen-guard mode exists (queen_guard(): QG_GUARD_RADIUS 5, QG_THREAT_MULT 6.0, QG_SPLIT_CLEAR 6)
  and is off because QUEEN_GUARD_CELLS is 0; is_queen() is true only above QUEEN_MIN_CELLS 600 cells or with a closed home.
- Question 3 (versions): not attempted. main and v31 were played in different hours against different opponents, and every main game is from 6 Oct and the first hours of 7 Oct KST.
- Tooling: the guard compares write paths as text, and the on-disk path of this repository has its Korean folder name in decomposed form; write through a Python heredoc with the path given as backslash-u escapes (see state.json, tooling notes).
  New this hour: a background command is stopped after 10 minutes unless it is started with a longer limit. The reruns of work/h4_pass.py and work/h12_pass.py were cut that way, so h4-shard0 to 3 and h12-shard1 to 3 now miss their newest 2 to 19 games each
  (h12-shard0 is whole). The first h13 and h14 passes were cut too; their main-game parts were redone as h13m and h14m. Coverage is stated wherever these files are used.
- Run 1000, main.cpp facts read: the hunt (qh_watch): a hunter is 4 long or less (QH_MAX_LEN) and not the leader, with a report no older than QH_FRESH 20 rounds and newer than its last miss; with our queen alive only the first finder hunts,
  with her dead (from round QH_REVENGE_ROUND 100) every such dragon does; qh_reach() tests for a walk and has no distance limit. View is the 7 by 7 square round the head (helper.hpp, VISION_RADIUS 3).
- Run 1000, coverage: work/h20 and work/h21 shards cover all 745 main and v31 games up to battle 1293952. work/h18 and work/h19 were not rerun (they stop at battle 1289717), so the bars F38_new_games and F39_new_games were not counted.
- Run 1000, wins by layout on main (games, won): Islands 15, 0; Australia 21, 4; Schooltime 1 15, 4; Stripes 15, 4; Tower Defense 23, 7; Portals 13, 7; Slithery Fight 21, 11; weakhold 20, 11; Around UNSW 23, 13; Trauma 27, 16; Trophy 15, 10; Default 21, 15;
  Queen Of Spades 23, 17; Maze 24, 18; Schooltime 2 10, 8; Prisoners Dilemma 1 and 2 13, 10; Devil 17, 15; Autarky 19, 18. Eliminations against us: 42 of 335 (Stripes 11, Tower Defense 6, Queen Of Spades 6, Trophy 5, Default 4, Islands 4).
- Run 1100, coverage: work/h22 shards (sight, narrow-tile turns, stays, the 6-step flag) cover all 765 main and v31 games up to battle 1298211 and take the place of h18, h19, h20 and h21 for the new-games bars. work/h23 shards cover the 325 games on 2-start layouts, rounds 0-100.
- Run 1100, wins by layout on main (games, won): Islands 15, 0; Australia 24, 4; Stripes 16, 4; Tower Defense 24, 7; Schooltime 1 and 2 25, 12; Portals 14, 7; Around UNSW 23, 13; Slithery Fight 23, 13; weakhold 21, 12; Trauma 28, 17; Trophy 17, 11;
  Default 21, 15; Maze 25, 18; Queen Of Spades 26, 19; Prisoners Dilemma 1 and 2 15, 11; Devil 17, 15; Autarky 21, 20. Eliminations against us: 47 of 355 (Stripes 12, Queen Of Spades 7, Tower Defense 6, Trophy 6, Default 4, Islands 4); by us 90.
  We were wiped out before round 150 in 16 main games: Stripes 5, Trophy 4, Prisoners Dilemma 3, Queen Of Spades 3, Devil 1.
- Run 1100, main.cpp facts read: QUEEN_QUIET_ROUND 100 sets queen_game for a queen that has met no enemy by round 100; queen_game moves feed_round to QUEEN_GAME_FEED_ROUND 300 and gates QUEEN_LEAD_BONUS in leader_priority(). Not traced further.
- Run 1800, coverage: work/h26 shards (654 main and v31 games: head-on meetings in r0-60 on every layout of 1200 cells or fewer; the body-sight count on the 108 full games with one queen alive on free layouts) and work/h27 shards (the same 108 games, sight by her head) reach battle 1327312.
  work/h25 was not rerun, so the bars F38_long_new and F39_new_games_3 were not counted this hour.
- Run 1800, main.cpp facts read: lines 1477 to 1486: qh_pos, qh_round and qh_in_view are set only when the enemy queen's HEAD is the part in view; her body in view sets only qh_foe_id. Lines 2054 to 2113: qh_reach() floods from her last cell and from the hunter and has no distance limit.
  Lines 2116 to 2153: the sighting travels by sonar ping and a newer one replaces an older one.
- Run 1800, wins by layout on main (games, won): Islands 23, 0; Stripes 24, 4; Australia 33, 7; Tower Defense 31, 8; Portals 23, 11; Around UNSW 30, 15; Slithery Fight 36, 18; Schooltime 1 and 2 32, 18; Trophy 23, 14; weakhold 27, 17; Trauma 34, 22; Maze 34, 22;
  Prisoners Dilemma 1 and 2 24, 16; Default 30, 21; Queen Of Spades 33, 24; Devil 23, 19; Autarky 25, 23. Eliminations against us: 74 of 485; by us 112.
- Run 1800: the team's own notes under losses/ (plan.md of 13:30, early-growth.md, queen-ring.md of 16:42) were read as leads. Change 2 of plan.md (keep a sighting long enough to arrive) is what the F42 sight counts of this hour speak to; its buckets E1 and E2 are F44 and F45 here.
