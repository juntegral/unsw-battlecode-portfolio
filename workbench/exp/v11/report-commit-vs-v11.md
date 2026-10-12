# v1 local report: commit (exp/v11/cm-a-px4, exp/v11/cm-b-px4, exp/v11/cm-a2-px4, exp/v11/cm-b1-px4, exp/v11/cm-a3-px4) vs v1.1 (exp/v11/v11-a-px4, exp/v11/v11-b-px4, exp/v11/v11-a2-px4, exp/v11/v11-b1-px4, exp/v11/v11-a3-px4)

Paired games (same key): 112. commit games 112, v1.1 games 112. Opponents: proxy4 (local mimics; sanity only, not a filter).

## 1. Five diagnostic indicators (EVAL.md §2) and outcome, paired games

| cell | bot | games | wins | r100 heads us / opp | r250 heads | natural intake us / opp (ratio) | line sac. pearls r300-499 (full games) | final longest us / opp | eliminated |
|---|---|---:|---:|---|---:|---|---|---|---|
| all maps | commit | 112 | 20 | 13.8 / 26.4 | 13.3 | 141.4 / 528.3 (27%) | 4.1 (93) | 16.9 / 24.8 | 17% (19/112) |
| all maps | v1.1 | 112 | 17 | 13.1 / 26.3 | 12.0 | 126.0 / 537.9 (23%) | 3.3 (92) | 14.3 / 23.2 | 18% (20/112) |
| swarm | commit | 112 | 20 | 13.8 / 26.4 | 13.3 | 141.4 / 528.3 (27%) | 4.1 (93) | 16.9 / 24.8 | 17% (19/112) |
| swarm | v1.1 | 112 | 17 | 13.1 / 26.3 | 12.0 | 126.0 / 537.9 (23%) | 3.3 (92) | 14.3 / 23.2 | 18% (20/112) |
| swarm · r500 | commit | 48 | 14 | 19.5 / 31.9 | 21.9 | 223.9 / 814.5 (27%) | 6.4 (48) | 28.0 / 31.9 | 0% (0/48) |
| swarm · r500 | v1.1 | 48 | 9 | 18.1 / 32.3 | 19.5 | 188.2 / 848.2 (22%) | 4.7 (48) | 22.1 / 29.3 | 0% (0/48) |
| swarm · elim | commit | 64 | 6 | 9.5 / 22.3 | 6.8 | 79.6 / 313.6 (25%) | 1.7 (45) | 8.6 / 19.5 | 30% (19/64) |
| swarm · elim | v1.1 | 64 | 8 | 9.4 / 21.8 | 6.3 | 79.4 / 305.1 (26%) | 1.7 (44) | 8.5 / 18.6 | 31% (20/64) |

## 2. Safety side effects (our deaths per game by cause, mass ledger; team longest >= 8 lost to an enemy head from r340)

| cell | bot | trapped | rammed (by enemy) | ram (we moved into a head) | ally head-on | sacrifice | longest lost from r340 |
|---|---|---:|---:|---:|---:|---:|---|
| all maps | commit | 21.2 | 13.5 | 3.8 | 1.5 | 10.1 | 9% (9/95) |
| all maps | v1.1 | 18.6 | 12.7 | 3.8 | 1.7 | 8.5 | 10% (9/92) |
| swarm | commit | 21.2 | 13.5 | 3.8 | 1.5 | 10.1 | 9% (9/95) |
| swarm | v1.1 | 18.6 | 12.7 | 3.8 | 1.7 | 8.5 | 10% (9/92) |
| swarm · r500 | commit | 35.0 | 14.9 | 5.0 | 1.3 | 19.8 | 6% (3/48) |
| swarm · r500 | v1.1 | 27.5 | 13.7 | 5.1 | 1.3 | 16.3 | 8% (4/48) |
| swarm · elim | commit | 10.8 | 12.4 | 2.8 | 1.7 | 2.8 | 13% (6/47) |
| swarm · elim | v1.1 | 11.9 | 12.0 | 2.8 | 2.0 | 2.6 | 11% (5/44) |

## 2b. The chain, link by link (paired games; per game means)

Heads r50 / r100 -> natural intake -> pieces born r100-430 (children <= 3 long; all births) -> our sacrifices (all; from r300) -> their drops from r300 -> line sacrifice pearls r300-499 (full games) and line share of those drops -> final longest.

| cell | bot | heads r50 · r100 | natural intake | pieces born r100-430 (births) | sacrifices (r300+) | sac. drops r300+ | line sac. pearls | line share | final longest | sf main · late feeds |
|---|---|---|---:|---|---|---:|---:|---:|---:|---|
| all maps | commit | 9.6 · 13.8 | 141.4 | 28.2 (33.8) | 10.1 (7.9) | 14.7 | 4.1 | 23% | 16.9 | 7.2 · 2.8 |
| all maps | v1.1 | 9.7 · 13.1 | 126.0 | 26.5 (29.6) | 8.5 (7.0) | 13.3 | 3.3 | 20% | 14.3 | 4.9 · 3.4 |
| swarm | commit | 9.6 · 13.8 | 141.4 | 28.2 (33.8) | 10.1 (7.9) | 14.7 | 4.1 | 23% | 16.9 | 7.2 · 2.8 |
| swarm | v1.1 | 9.7 · 13.1 | 126.0 | 26.5 (29.6) | 8.5 (7.0) | 13.3 | 3.3 | 20% | 14.3 | 4.9 · 3.4 |
| swarm · r500 | commit | 13.3 · 19.5 | 223.9 | 41.3 (53.5) | 19.8 (14.7) | 27.5 | 6.4 | 23% | 28.0 | 15.6 · 4.2 |
| swarm · r500 | v1.1 | 13.8 · 18.1 | 188.2 | 38.0 (43.1) | 16.3 (13.0) | 24.8 | 4.7 | 19% | 22.1 | 10.4 · 5.9 |
| swarm · elim | commit | 6.8 · 9.5 | 79.6 | 18.4 (19.0) | 2.8 (2.8) | 5.1 | 1.7 | 24% | 8.6 | 0.9 · 1.8 |
| swarm · elim | v1.1 | 6.7 · 9.4 | 79.4 | 17.9 (19.4) | 2.6 (2.4) | 4.6 | 1.7 | 25% | 8.5 | 0.9 · 1.5 |

## 2c. Target overlap (research transfer 1): target-labelled turns (v1 " sd", v0 " F") whose target another of our dragons also targets that round

| family | bot | target turns / game | same tile | within 3 |
|---|---|---:|---:|---:|
| swarm | commit | 2719.7 | 8.9% | 40.9% |
| swarm | v1.1 | 2493.8 | 9.8% | 42.3% |

## 3. Belief accuracy (tag " bl<len>@x,y k<0|1>" every 5 rounds vs the true longest other living ally at that turn start)

| cell | bot | tagged turns | king verdict right | truly longest: says king | not longest: says not king | length within 1 | position within 3 | believes longer than true (+2) | believes shorter (-2) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all maps · all turns | commit | 123288 | 84% (103450/123288) | 51% (9637/18899) | 90% (93813/104389) | 51% (62351/123288) | 26% (32058/123153) | 8% (9884/123288) | 41% (51053/123288) |
| all maps · all turns | v1.1 | 118441 | 84% (99009/118441) | 49% (9831/20094) | 91% (89178/98347) | 59% (69372/118441) | 30% (35353/118220) | 10% (11406/118441) | 32% (37663/118441) |
| all maps · r300+ | commit | 43256 | 84% (36325/43256) | 68% (3781/5530) | 86% (32544/37726) | 43% (18748/43256) | 23% (10025/43201) | 4% (1857/43256) | 52% (22651/43256) |
| all maps · r300+ | v1.1 | 42983 | 85% (36427/42983) | 63% (3757/6010) | 88% (32670/36973) | 52% (22347/42983) | 27% (11718/42871) | 6% (2560/42983) | 42% (18076/42983) |
| all maps · our length >= 8 | commit | 6981 | 76% (5272/6981) | 99% (3208/3251) | 55% (2064/3730) | 36% (2513/6981) | 21% (1475/6975) | 4% (289/6981) | 60% (4179/6981) |
| all maps · our length >= 8 | v1.1 | 4387 | 77% (3384/4387) | 99% (2444/2479) | 49% (940/1908) | 42% (1830/4387) | 25% (1076/4384) | 5% (214/4387) | 53% (2343/4387) |
| swarm · all turns | commit | 123288 | 84% (103450/123288) | 51% (9637/18899) | 90% (93813/104389) | 51% (62351/123288) | 26% (32058/123153) | 8% (9884/123288) | 41% (51053/123288) |
| swarm · all turns | v1.1 | 118441 | 84% (99009/118441) | 49% (9831/20094) | 91% (89178/98347) | 59% (69372/118441) | 30% (35353/118220) | 10% (11406/118441) | 32% (37663/118441) |
| swarm · r300+ | commit | 43256 | 84% (36325/43256) | 68% (3781/5530) | 86% (32544/37726) | 43% (18748/43256) | 23% (10025/43201) | 4% (1857/43256) | 52% (22651/43256) |
| swarm · r300+ | v1.1 | 42983 | 85% (36427/42983) | 63% (3757/6010) | 88% (32670/36973) | 52% (22347/42983) | 27% (11718/42871) | 6% (2560/42983) | 42% (18076/42983) |
| swarm · our length >= 8 | commit | 6981 | 76% (5272/6981) | 99% (3208/3251) | 55% (2064/3730) | 36% (2513/6981) | 21% (1475/6975) | 4% (289/6981) | 60% (4179/6981) |
| swarm · our length >= 8 | v1.1 | 4387 | 77% (3384/4387) | 99% (2444/2479) | 49% (940/1908) | 42% (1830/4387) | 25% (1076/4384) | 5% (214/4387) | 53% (2343/4387) |

## 4. Tags per game (our indicator labels), paired games

| family | bot | cl | conv | escape-split | feed | grab | no-exit | no-exit s | pocket-eat | sc | scx | sd | sf | sk | sq | sr | src | srn | srx | sx | sxc | sxx | tg | tgx |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| swarm | commit | 459.5 | 7.2 | 15.4 | 10.0 | 132.9 | 20.8 | 2.5 | 0.1 | 21.2 | 19.8 | 2719.7 | 10.0 | 461.8 | 2.3 | 23.6 | 27.1 | 183.7 | 5.0 | 13.3 | 25.6 | 3.1 | 214.7 | 185.0 |
| swarm | v1.1 | 443.3 | 4.9 | 12.0 | 8.4 | 132.7 | 18.2 | 2.4 | 0.1 | 17.1 | 14.0 | 2493.8 | 8.4 | 393.5 | 1.7 | 22.6 | 25.9 | 186.5 | 4.5 | 12.8 | 22.9 | 2.7 | 219.4 | 181.1 |

sf recipients (commit, swarm maps): 1125 feeds; recipient length 3-4: 13% (143/1125), 5-7: 11% (121/1125), 8-15: 45% (505/1125), 16+: 32% (356/1125).

## 5. Per map (paired): wins, r100 heads, natural intake, final longest, eliminated

| map | commit W · u100 · nat · longest · elim | v1.1 W · u100 · nat · longest · elim |
|---|---|---|
| default | 4/16 · 12.1 · 132.5 · 12.8 · 1 | 4/16 · 13.0 · 147.6 · 13.9 · 0 |
| devil | 0/8 · 8.8 · 68.9 · 13.0 · 0 | 0/8 · 8.6 · 48.1 · 6.4 · 2 |
| devil_b | 0/8 · 9.1 · 59.1 · 6.8 · 2 | 0/8 · 11.1 · 87.4 · 11.8 · 0 |
| queen_of_spades | 2/8 · 4.5 · 100.9 · 16.3 · 0 | 2/8 · 3.1 · 70.3 · 10.6 · 2 |
| queen_of_spades_b | 0/8 · 6.1 · 80.0 · 7.4 · 0 | 2/8 · 4.0 · 67.1 · 11.6 · 0 |
| schooltime | 7/8 · 26.1 · 669.9 · 68.8 · 0 | 5/8 · 22.1 · 511.0 · 58.9 · 0 |
| schooltime_b | 2/8 · 9.5 · 117.3 · 22.4 · 0 | 0/8 · 9.3 · 91.5 · 10.1 · 0 |
| slithery_fight | 0/8 · 41.8 · 203.3 · 22.3 · 0 | 2/8 · 38.8 · 188.8 · 23.4 · 0 |
| slithery_fight_b | 1/8 · 27.8 · 199.8 · 24.0 · 0 | 0/8 · 26.5 · 192.9 · 14.5 · 0 |
| trauma | 4/16 · 5.8 · 76.6 · 15.4 · 0 | 2/16 · 6.0 · 72.6 · 12.9 · 0 |
| trophy | 0/16 · 11.7 · 31.4 · 0.0 · 16 | 0/16 · 11.1 · 33.6 · 0.0 · 16 |
