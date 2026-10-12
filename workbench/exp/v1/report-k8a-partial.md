# v1 local report: k8 (exp/v1/k8-a-px4) vs v1post (exp/v1/v1post-a-px4)

Paired games (same key): 28. k8 games 28, v1post games 28. Opponents: proxy4 (local mimics; sanity only, not a filter).

## 1. Five diagnostic indicators (EVAL.md §2) and outcome, paired games

| cell | bot | games | wins | r100 heads us / opp | r250 heads | natural intake us / opp (ratio) | line sac. pearls r300-499 (full games) | final longest us / opp | eliminated |
|---|---|---:|---:|---|---:|---|---|---|---|
| all maps | k8 | 28 | 6 | 13.3 / 29.4 | 13.3 | 152.1 / 611.4 (25%) | 4.2 (23) | 19.3 / 26.0 | 18% (5/28) |
| all maps | v1post | 28 | 4 | 13.3 / 29.4 | 13.3 | 139.2 / 612.0 (23%) | 4.4 (23) | 18.1 / 28.3 | 18% (5/28) |
| swarm | k8 | 28 | 6 | 13.3 / 29.4 | 13.3 | 152.1 / 611.4 (25%) | 4.2 (23) | 19.3 / 26.0 | 18% (5/28) |
| swarm | v1post | 28 | 4 | 13.3 / 29.4 | 13.3 | 139.2 / 612.0 (23%) | 4.4 (23) | 18.1 / 28.3 | 18% (5/28) |
| swarm · r500 | k8 | 12 | 4 | 20.2 / 37.0 | 22.5 | 250.4 / 1001.9 (25%) | 6.6 (12) | 32.8 / 34.6 | 0% (0/12) |
| swarm · r500 | v1post | 12 | 3 | 20.2 / 37.0 | 22.5 | 226.2 / 1000.3 (23%) | 5.3 (12) | 30.0 / 38.1 | 0% (0/12) |
| swarm · elim | k8 | 16 | 2 | 8.1 / 23.6 | 6.3 | 78.4 / 318.6 (25%) | 1.5 (11) | 9.1 / 19.6 | 31% (5/16) |
| swarm · elim | v1post | 16 | 1 | 8.1 / 23.6 | 6.3 | 74.0 / 320.8 (23%) | 3.5 (11) | 9.2 / 21.0 | 31% (5/16) |

## 2. Safety side effects (our deaths per game by cause, mass ledger; team longest >= 8 lost to an enemy head from r340)

| cell | bot | trapped | rammed (by enemy) | ram (we moved into a head) | ally head-on | sacrifice | longest lost from r340 |
|---|---|---:|---:|---:|---:|---:|---|
| all maps | k8 | 27.0 | 17.0 | 3.8 | 1.9 | 9.1 | 8% (2/24) |
| all maps | v1post | 22.5 | 16.3 | 3.2 | 1.5 | 19.3 | 8% (2/24) |
| swarm | k8 | 27.0 | 17.0 | 3.8 | 1.9 | 9.1 | 8% (2/24) |
| swarm | v1post | 22.5 | 16.3 | 3.2 | 1.5 | 19.3 | 8% (2/24) |
| swarm · r500 | k8 | 45.4 | 22.3 | 6.0 | 1.7 | 17.9 | 0% (0/12) |
| swarm · r500 | v1post | 36.9 | 21.3 | 5.1 | 1.3 | 38.4 | 0% (0/12) |
| swarm · elim | k8 | 13.3 | 13.1 | 2.1 | 2.0 | 2.4 | 17% (2/12) |
| swarm · elim | v1post | 11.8 | 12.6 | 1.8 | 1.6 | 4.9 | 17% (2/12) |

## 2b. The chain, link by link (paired games; per game means)

Heads r50 / r100 -> natural intake -> pieces born r100-430 (children <= 3 long; all births) -> our sacrifices (all; from r300) -> their drops from r300 -> line sacrifice pearls r300-499 (full games) and line share of those drops -> final longest.

| cell | bot | heads r50 · r100 | natural intake | pieces born r100-430 (births) | sacrifices (r300+) | sac. drops r300+ | line sac. pearls | line share | final longest | sf main · late feeds |
|---|---|---|---:|---|---|---:|---:|---:|---:|---|
| all maps | k8 | 10.0 · 13.3 | 152.1 | 37.0 (41.0) | 9.1 (9.1) | 18.0 | 4.2 | 19% | 19.3 | 4.5 · 4.6 |
| all maps | v1post | 10.0 · 13.3 | 139.2 | 41.0 (45.0) | 19.3 (19.3) | 28.1 | 4.4 | 13% | 18.1 | 18.5 · 0.6 |
| swarm | k8 | 10.0 · 13.3 | 152.1 | 37.0 (41.0) | 9.1 (9.1) | 18.0 | 4.2 | 19% | 19.3 | 4.5 · 4.6 |
| swarm | v1post | 10.0 · 13.3 | 139.2 | 41.0 (45.0) | 19.3 (19.3) | 28.1 | 4.4 | 13% | 18.1 | 18.5 · 0.6 |
| swarm · r500 | k8 | 13.7 · 20.2 | 250.4 | 61.9 (68.8) | 17.9 (17.9) | 34.8 | 6.6 | 19% | 32.8 | 9.2 · 8.9 |
| swarm · r500 | v1post | 13.7 · 20.2 | 226.2 | 71.4 (78.3) | 38.4 (38.4) | 54.3 | 5.3 | 10% | 30.0 | 37.3 · 1.0 |
| swarm · elim | k8 | 7.3 · 8.1 | 78.4 | 18.3 (20.1) | 2.4 (2.4) | 5.5 | 1.5 | 19% | 9.1 | 1.1 · 1.4 |
| swarm · elim | v1post | 7.3 · 8.1 | 74.0 | 18.3 (20.1) | 4.9 (4.9) | 8.4 | 3.5 | 29% | 9.2 | 4.5 · 0.4 |

## 2c. Target overlap (research transfer 1): target-labelled turns (v1 " sd", v0 " F") whose target another of our dragons also targets that round

| family | bot | target turns / game | same tile | within 3 |
|---|---|---:|---:|---:|
| swarm | k8 | 4391.5 | 17.8% | 56.7% |
| swarm | v1post | 4391.5 | 17.8% | 56.7% |

## 3. Belief accuracy (tag " bl<len>@x,y k<0|1>" every 5 rounds vs the true longest other living ally at that turn start)

| cell | bot | tagged turns | king verdict right | truly longest: says king | not longest: says not king | length within 1 | position within 3 | believes longer than true (+2) | believes shorter (-2) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all maps · all turns | k8 | 34300 | 86% (29365/34300) | 43% (2141/5024) | 93% (27224/29276) | 54% (18588/34300) | 30% (10258/34147) | 14% (4892/34300) | 32% (10820/34300) |
| all maps · all turns | v1post | 30718 | 84% (25880/30718) | 43% (2177/5021) | 92% (23703/25697) | 55% (17033/30718) | 30% (9252/30552) | 15% (4509/30718) | 30% (9176/30718) |
| all maps · r300+ | k8 | 14522 | 89% (12857/14522) | 60% (863/1443) | 92% (11994/13079) | 48% (6978/14522) | 29% (4140/14418) | 10% (1503/14522) | 42% (6041/14522) |
| all maps · r300+ | v1post | 10940 | 86% (9372/10940) | 62% (899/1440) | 89% (8473/9500) | 50% (5423/10940) | 29% (3134/10823) | 10% (1120/10940) | 40% (4397/10940) |
| all maps · our length >= 8 | k8 | 1190 | 80% (953/1190) | 99% (606/614) | 60% (347/576) | 48% (571/1190) | 30% (354/1185) | 4% (50/1190) | 48% (569/1190) |
| all maps · our length >= 8 | v1post | 1205 | 79% (948/1205) | 99% (621/630) | 57% (327/575) | 48% (574/1205) | 28% (335/1190) | 5% (59/1205) | 47% (572/1205) |
| swarm · all turns | k8 | 34300 | 86% (29365/34300) | 43% (2141/5024) | 93% (27224/29276) | 54% (18588/34300) | 30% (10258/34147) | 14% (4892/34300) | 32% (10820/34300) |
| swarm · all turns | v1post | 30718 | 84% (25880/30718) | 43% (2177/5021) | 92% (23703/25697) | 55% (17033/30718) | 30% (9252/30552) | 15% (4509/30718) | 30% (9176/30718) |
| swarm · r300+ | k8 | 14522 | 89% (12857/14522) | 60% (863/1443) | 92% (11994/13079) | 48% (6978/14522) | 29% (4140/14418) | 10% (1503/14522) | 42% (6041/14522) |
| swarm · r300+ | v1post | 10940 | 86% (9372/10940) | 62% (899/1440) | 89% (8473/9500) | 50% (5423/10940) | 29% (3134/10823) | 10% (1120/10940) | 40% (4397/10940) |
| swarm · our length >= 8 | k8 | 1190 | 80% (953/1190) | 99% (606/614) | 60% (347/576) | 48% (571/1190) | 30% (354/1185) | 4% (50/1190) | 48% (569/1190) |
| swarm · our length >= 8 | v1post | 1205 | 79% (948/1205) | 99% (621/630) | 57% (327/575) | 48% (574/1205) | 28% (335/1190) | 5% (59/1205) | 47% (572/1205) |

## 4. Tags per game (our indicator labels), paired games

| family | bot | cl | conv | escape-split | feed | grab | no-exit | no-exit s | pocket-eat | sc | scx | sd | sf | sk | sq | sr | src | srn | srx | sx | sxc | sxx | tg | tgx |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| swarm | k8 | 792.1 | 4.5 | 15.9 | 9.1 | 172.2 | 26.6 | 3.0 | 0.1 | 22.4 | 20.9 | 4391.5 | 9.1 | 292.4 | 3.3 | 32.0 | 53.0 | 75.7 | 10.1 | 14.1 | 31.1 | 3.1 | 212.4 | 181.0 |
| swarm | v1post | 696.5 | 18.5 | 13.0 | 19.2 | 177.9 | 22.3 | 2.2 | 0.1 | 18.4 | 18.0 | 4391.5 | 19.2 | 287.2 | 3.1 | 36.3 | 51.5 | 67.5 | 10.5 | 14.1 | 31.1 | 3.1 | 203.4 | 171.2 |

sf recipients (k8, swarm maps): 256 feeds; recipient length 3-4: 21% (53/256), 5-7: 18% (46/256), 8-15: 42% (107/256), 16+: 20% (50/256).

## 5. Per map (paired): wins, r100 heads, natural intake, final longest, eliminated

| map | k8 W · u100 · nat · longest · elim | v1post W · u100 · nat · longest · elim |
|---|---|---|
| default | 1/4 · 9.3 · 95.3 · 10.8 · 1 | 0/4 · 9.3 · 91.3 · 12.0 · 1 |
| devil | 0/4 · 9.8 · 56.0 · 13.3 · 0 | 0/4 · 9.8 · 52.3 · 14.3 · 0 |
| queen_of_spades | 1/4 · 4.8 · 135.3 · 12.5 · 0 | 1/4 · 4.8 · 125.5 · 10.5 · 0 |
| schooltime | 3/4 · 18.8 · 454.8 · 67.0 · 0 | 3/4 · 18.8 · 407.8 · 61.8 · 0 |
| slithery_fight | 0/4 · 36.0 · 216.8 · 18.3 · 0 | 0/4 · 36.0 · 191.0 · 17.5 · 0 |
| trauma | 1/4 · 5.8 · 79.8 · 13.3 · 0 | 0/4 · 5.8 · 79.8 · 10.8 · 0 |
| trophy | 0/4 · 8.5 · 27.0 · 0.0 · 4 | 0/4 · 8.5 · 27.0 · 0.0 · 4 |
