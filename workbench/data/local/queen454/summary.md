aAah (team 454; no nAah in the full leaderboard): 60 games, sides {'B': 30, 'A': 30}; 2026-10-04 12:38 to 2026-10-07 03:02 UTC.
Ours, meow (1119), same-code versions 44/47: 370 games, sides {'A': 230, 'B': 140}; 2026-10-06 10:18 to 2026-10-07 02:55 UTC.
#38 attempt 2: 16 paired games per arm (off → on), local replays created 6–7 Oct 2026 KST; comparison opponent is a local bot.

All distances are wrapped Manhattan tile distances unless stated. Rounds are 1–500; raw replay rounds are 0–499. n means games, steps, samples or windows as named.
Ground = fraction of tiles with an open edge closest by legal walking distance to friendly heads; walls/portals respected, bodies ignored, ties half, unreachable by both unclaimed.
Behind = at least one teammate nearer to the enemy head nearest the queen; sampled every 10 completed rounds while she lives. Centre uses the circular mean of friendly heads.
A small loop needs a closed path through ≥4 distinct tiles within a trailing 8-round box; loop 3 includes loop 2. Stationary queens do not count. First 7 rounds excluded.
Travel windows are complete, non-overlapping 50-round blocks with a living queen. Box = smallest wrapped width × height. Early-ended games are absent from later checkpoints; dead queens count as length 0.

| Number | aAah | Ours v44/47 | #38 off → on |
|---|---|---|---|
| Alive at end / games | 55.0% (33/60) | 26.8% (99/370) | 25.0% (4/16) → 25.0% (4/16) |
| Death round, mean / deaths | 181.0 (n=27) | 156.6 (n=271) | 97.6 (n=12) → 141.1 (n=12) |
| Deaths: enemy head / wall / own body / no action / other | 21/0/5/0/1 (n=27) | 177/47/28/1/18 (n=271) | 10/2/0/0/0 (n=12) → 11/0/1/0/0 (n=12) |
| Visible-enemy steps: closer / farther | 33.5/62.6% (n=3551) | 32.4/61.8% (n=20823) | 27.6/70.0% (n=540) → 18.8/78.5% (n=536) |
| Queen kills / head-on hits (queen moving) | 2 / 21 (2); n=60 games | 17 / 177 (11); n=370 games | 2 / 10 (2); n=16 games → 4 / 11 (4); n=16 games |
| Before kills: first closer queen / enemy / neither | 1/1/0 (n=2) | 10/7/0 (n=17) | 0/2/0 (n=2) → 0/4/0 (n=4) |
| Before deaths: first closer queen / enemy / neither | 14/13/0 (n=27) | 147/116/8 (n=271) | 7/5/0 (n=12) → 2/10/0 (n=12) |
| At least one teammate ahead / samples | 63.8% (930/1457) | 49.9% (3939/7886) | 38.6% (119/308) → 53.3% (194/364) |
| Teammates ahead, mean / samples | 4.7 (n=1457) | 2.4 (n=7886) | 1.1 (n=308) → 1.8 (n=364) |
| Distance to centre / nearest teammate / start, means | 14.1 (n=1456) / 4.4 (n=1451) / 12.8 (n=1458) | 13.4 (n=7871) / 5.8 (n=7752) / 10.4 (n=7887) | 14.5 (n=307) / 7.2 (n=308) / 11.0 (n=308) → 11.5 (n=364) / 5.3 (n=364) / 7.6 (n=364) |
| Unique tiles / net displacement per 50 rounds, means | 33.2 (n=273) / 9.8 (n=273) | 34.2 (n=1455) / 9.2 (n=1455) | 49.1 (n=57) / 10.8 (n=57) → 12.8 (n=68) / 5.1 (n=68) |
| 50-round box, mean width × height / windows | 10.0 × 9.3 (n=273) | 9.3 × 10.0 (n=1455) | 10.5 × 14.8 (n=57) → 4.6 × 4.9 (n=68) |
| Loop 2×2 / ≤3×3 / eligible living rounds | 12.1% (1738/14361) / 24.6% (3526/14361) | 19.6% (15191/77645) / 28.7% (22287/77645) | 0.5% (15/3047) / 4.6% (139/3047) → 68.8% (2454/3569) / 75.3% (2688/3569) |
| Ground r100 / 200 / 300 / 400, means | 55.9% (n=57); 59.4% (n=39); 56.4% (n=31); 61.7% (n=28) | 52.6% (n=349); 51.1% (n=299); 45.5% (n=257); 44.3% (n=241) | 49.9% (n=16); 49.9% (n=16); 49.9% (n=14); 49.9% (n=14) → 50.1% (n=16); 48.5% (n=16); 49.2% (n=16); 53.8% (n=13) |
| Queen length r100 / 200 / 300 / 400 / 500, means | 2.0 (n=57); 2.6 (n=39); 2.6 (n=31); 1.4 (n=28); 1.2 (n=26) | 1.9 (n=349); 1.4 (n=299); 1.5 (n=257); 5.2 (n=241); 6.1 (n=225) | 1.4 (n=16); 0.6 (n=16); 1.4 (n=14); 7.5 (n=14); 11.5 (n=14) → 1.6 (n=16); 0.9 (n=16); 0.6 (n=16); 0.6 (n=13); 0.8 (n=13) |
| Pearls eaten / splits after r200, mean per game | 9.9 (n=60) / 0.8 (n=60) | 10.5 (n=370) / 0.7 (n=370) | 12.2 (n=16) / 0.1 (n=16) → 0.7 (n=16) / 0.1 (n=16) |
| Queen-rule endings; mean own : opposing length | 12/60; 1.9 : 15.1 | 83/370; 15.1 : 21.5 | 4/16; 40.2 : 40.2 → 4/16; 2.8 : 25.8 |
| Phase × area: games; closer/farther; behind; loop ≤3×3 | | | |
| 1-100; <=600 tiles | 22; 33.8/60.3% (n=473); 55.7% (108/194); 16.4% (298/1817) | 110; 39.0/57.0% (n=1697); 45.5% (373/819); 28.8% (2204/7665) | 4; 24.2/75.8% (n=33); 51.5% (17/33); 9.8% (31/316) → 4; 14.3/85.7% (n=21); 24.1% (7/29); 67.0% (179/267) |
| 101-300; <=600 tiles | 22; 34.8/60.6% (n=687); 56.0% (70/125); 20.1% (264/1314) | 110; 31.3/64.0% (n=1927); 39.6% (218/550); 37.6% (2126/5648) | 4; 58.3/41.7% (n=12); 100.0% (3/3); 0.0% (0/48) → 4; 35.6/61.6% (n=73); 60.0% (18/30); 55.4% (168/303) |
| 301-500; <=600 tiles | 22; 41.4/53.9% (n=191); 83.3% (40/48); 20.7% (101/488) | 110; 35.8/59.9% (n=812); 41.1% (60/146); 20.3% (310/1524) | 4; NA/NA% (n=0); NA (n=0); NA (n=0) → 4; 50.0/50.0% (n=6); 75.0% (15/20); 78.0% (156/200) |
| 1-100; >600 tiles | 38; 27.6/69.5% (n=653); 55.4% (201/363); 17.7% (601/3395) | 260; 24.5/72.4% (n=3829); 55.0% (1307/2377); 18.3% (4070/22232) | 12; 19.3/78.2% (n=243); 42.1% (45/107); 3.9% (39/1011) → 12; 17.4/80.2% (n=172); 53.3% (57/107); 75.7% (753/995) |
| 101-300; >600 tiles | 38; 33.6/63.0% (n=1176); 68.2% (322/472); 26.0% (1242/4770) | 260; 33.7/60.4% (n=7378); 54.7% (1416/2587); 29.8% (7862/26390) | 12; 28.4/68.0% (n=169); 34.1% (29/85); 7.2% (63/872) → 12; 14.3/83.2% (n=238); 41.4% (48/116); 77.4% (916/1183) |
| 301-500; >600 tiles | 38; 37.2/60.4% (n=371); 74.1% (189/255); 39.6% (1020/2577) | 260; 34.2/57.1% (n=5180); 40.2% (565/1407); 40.3% (5715/14186) | 12; 47.0/51.8% (n=83); 31.2% (25/80); 0.8% (6/800) → 12; 19.2/73.1% (n=26); 79.0% (49/62); 83.1% (516/621) |

All requested numbers, including deaths, lengths, ground, travel and five-round approach credits, are also split by phase × area in strata.json; rows.json retains each game and encounter.
Visible-enemy steps include executed steps and the attempted fatal step, comparing the same visible enemy-head set before/after. Walls are not traversed. Closer is movement, not intent.
Before-kill/death counts use the previous five completed rounds and the first positive distance reduction against that specific head. Queen kills include her rams and enemies hitting her body; mutual head hits are separate.
For wall/self/no-action deaths, the paired head is the nearest remaining enemy (not a claimed cause). Positive/negative net approach credits and the exact pairs are in rows.json.

Measured
(a) ‘Their queen does not engage first’: not established. aAah closer/farther steps are 33.5/62.6% (n=3551); she is the moving head in 2/21 head-on hits. These measure actions, not intent.
(b) ‘Mostly among or behind teammates’: supported by the stated position proxy in 63.8% (930/1457) of samples; ours 49.9% (3939/7886). This is relative to one nearest enemy, not a battle line.
(c) ‘She does not circle’: not literally true; aAah spends 24.6% (3526/14361) of eligible living rounds in a ≤3×3 loop, versus ours 28.7% (22287/77645) and #38 on 75.3% (2688/3569).
(d) ‘Our circling queen holds less ground’: paired #38 on-minus-off changes at r100/200/300/400 are 0.2 percentage points (8 lower/16 pairs); -1.4 percentage points (13 lower/16 pairs); 3.3 percentage points (7 lower/14 pairs); 9.5 percentage points (5 lower/12 pairs). This small local sample cannot establish a general causal effect.

Read, not tested
The observations can motivate testing queen placement behind active teammates; they do not identify an opponent policy or prove a survival benefit.
Queen movement and team ground can share causes: teammate population, opponent pressure, map geometry, and the survival of either queen.

Limits
aAah: 60 games from 8 series, recent and clustered; ours 370 from 74 series. Games within a series are not independent.
Opponent ratings (mean/min/max; ≥2000 games): aAah 2346.0/2080/2487; 60/60; ours 1936.9/1664/2474; 100/370. This is not a matched ladder comparison.
aAah submission IDs are hidden in public replays/API, so version changes could not be identified. Our v44/v47 labels come from the existing ladder ledger. #38 attempt 2 is a separate local experiment.
True replay positions include enemies/teammates outside the queen’s view; only the initiative filter uses her 7×7 view. Geometric distances ignore walls; ground walking distances do not.
Loops larger than 3×3 or with interruptions can be missed; centre can be undefined for a perfectly balanced wrap-around distribution. Ground is a head-distance proxy, not possession or reachable moves through bodies.
All final body counts/lengths were checked against replay result fields; our 370 queen outcomes, death rounds, pearls and split totals match the existing ladder ledger. No games were run or requested; no submission or post was made.
