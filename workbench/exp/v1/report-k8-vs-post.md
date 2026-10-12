# v1 local report: k8 (exp/v1/k8-a-px4, exp/v1/k8-b-px4) vs v1post (exp/v1/v1post-a-px4, exp/v1/v1post-b-px4)

Paired games (same key): 56. k8 games 56, v1post games 56. Opponents: proxy4 (local mimics; sanity only, not a filter).

## 1. Five diagnostic indicators (EVAL.md §2) and outcome, paired games

| cell | bot | games | wins | r100 heads us / opp | r250 heads | natural intake us / opp (ratio) | line sac. pearls r300-499 (full games) | final longest us / opp | eliminated |
|---|---|---:|---:|---|---:|---|---|---|---|
| all maps | k8 | 56 | 8 | 12.5 / 26.9 | 11.9 | 122.8 / 546.8 (22%) | 3.4 (46) | 14.6 / 23.5 | 18% (10/56) |
| all maps | v1post | 56 | 5 | 12.5 / 26.9 | 11.9 | 113.8 / 551.7 (21%) | 4.5 (45) | 13.9 / 24.4 | 20% (11/56) |
| swarm | k8 | 56 | 8 | 12.5 / 26.9 | 11.9 | 122.8 / 546.8 (22%) | 3.4 (46) | 14.6 / 23.5 | 18% (10/56) |
| swarm | v1post | 56 | 5 | 12.5 / 26.9 | 11.9 | 113.8 / 551.7 (21%) | 4.5 (45) | 13.9 / 24.4 | 20% (11/56) |
| swarm · r500 | k8 | 24 | 6 | 18.1 / 32.3 | 20.8 | 197.2 / 852.4 (23%) | 5.3 (24) | 23.5 / 30.3 | 0% (0/24) |
| swarm · r500 | v1post | 24 | 4 | 18.1 / 32.3 | 20.8 | 181.7 / 861.0 (21%) | 6.1 (24) | 22.2 / 32.0 | 0% (0/24) |
| swarm · elim | k8 | 32 | 2 | 8.3 / 23.0 | 5.2 | 67.0 / 317.7 (21%) | 1.4 (22) | 7.8 / 18.4 | 31% (10/32) |
| swarm · elim | v1post | 32 | 1 | 8.3 / 23.0 | 5.2 | 62.8 / 319.7 (20%) | 2.7 (21) | 7.6 / 18.8 | 34% (11/32) |

## 2. Safety side effects (our deaths per game by cause, mass ledger; team longest >= 8 lost to an enemy head from r340)

| cell | bot | trapped | rammed (by enemy) | ram (we moved into a head) | ally head-on | sacrifice | longest lost from r340 |
|---|---|---:|---:|---:|---:|---:|---|
| all maps | k8 | 21.7 | 14.6 | 3.5 | 1.6 | 7.3 | 9% (4/47) |
| all maps | v1post | 17.8 | 14.1 | 3.0 | 1.3 | 16.4 | 9% (4/47) |
| swarm | k8 | 21.7 | 14.6 | 3.5 | 1.6 | 7.3 | 9% (4/47) |
| swarm | v1post | 17.8 | 14.1 | 3.0 | 1.3 | 16.4 | 9% (4/47) |
| swarm · r500 | k8 | 37.6 | 17.8 | 5.2 | 2.2 | 14.5 | 0% (0/24) |
| swarm · r500 | v1post | 30.3 | 17.1 | 4.3 | 1.8 | 32.9 | 0% (0/24) |
| swarm · elim | k8 | 9.8 | 12.2 | 2.3 | 1.2 | 1.8 | 17% (4/23) |
| swarm · elim | v1post | 8.5 | 11.8 | 2.1 | 0.9 | 4.1 | 17% (4/23) |

## 2b. The chain, link by link (paired games; per game means)

Heads r50 / r100 -> natural intake -> pieces born r100-430 (children <= 3 long; all births) -> our sacrifices (all; from r300) -> their drops from r300 -> line sacrifice pearls r300-499 (full games) and line share of those drops -> final longest.

| cell | bot | heads r50 · r100 | natural intake | pieces born r100-430 (births) | sacrifices (r300+) | sac. drops r300+ | line sac. pearls | line share | final longest | sf main · late feeds |
|---|---|---|---:|---|---|---:|---:|---:|---:|---|
| all maps | k8 | 9.3 · 12.5 | 122.8 | 30.3 (33.2) | 7.3 (7.2) | 13.9 | 3.4 | 20% | 14.6 | 2.8 · 4.5 |
| all maps | v1post | 9.3 · 12.5 | 113.8 | 33.6 (36.5) | 16.4 (16.4) | 23.5 | 4.5 | 15% | 13.9 | 15.9 · 0.4 |
| swarm | k8 | 9.3 · 12.5 | 122.8 | 30.3 (33.2) | 7.3 (7.2) | 13.9 | 3.4 | 20% | 14.6 | 2.8 · 4.5 |
| swarm | v1post | 9.3 · 12.5 | 113.8 | 33.6 (36.5) | 16.4 (16.4) | 23.5 | 4.5 | 15% | 13.9 | 15.9 · 0.4 |
| swarm · r500 | k8 | 13.1 · 18.1 | 197.2 | 51.2 (56.5) | 14.5 (14.4) | 27.2 | 5.3 | 20% | 23.5 | 5.6 · 8.9 |
| swarm · r500 | v1post | 13.1 · 18.1 | 181.7 | 59.0 (64.4) | 32.9 (32.9) | 46.2 | 6.1 | 13% | 22.2 | 32.1 · 0.8 |
| swarm · elim | k8 | 6.4 · 8.3 | 67.0 | 14.6 (15.7) | 1.8 (1.8) | 3.8 | 1.4 | 24% | 7.8 | 0.7 · 1.2 |
| swarm · elim | v1post | 6.4 · 8.3 | 62.8 | 14.5 (15.6) | 4.1 (4.1) | 6.4 | 2.7 | 27% | 7.6 | 3.8 · 0.2 |

## 2c. Target overlap (research transfer 1): target-labelled turns (v1 " sd", v0 " F") whose target another of our dragons also targets that round

| family | bot | target turns / game | same tile | within 3 |
|---|---|---:|---:|---:|
| swarm | k8 | 4084.0 | 17.5% | 55.4% |
| swarm | v1post | 4084.0 | 17.5% | 55.4% |

## 3. Belief accuracy (tag " bl<len>@x,y k<0|1>" every 5 rounds vs the true longest other living ally at that turn start)

| cell | bot | tagged turns | king verdict right | truly longest: says king | not longest: says not king | length within 1 | position within 3 | believes longer than true (+2) | believes shorter (-2) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all maps · all turns | k8 | 62992 | 83% (52552/62992) | 40% (4391/11019) | 93% (48161/51973) | 59% (37175/62992) | 32% (20003/62707) | 15% (9424/62992) | 26% (16393/62992) |
| all maps · all turns | v1post | 56374 | 82% (46099/56374) | 40% (4395/10856) | 92% (41704/45518) | 60% (33564/56374) | 32% (17836/56078) | 16% (8749/56374) | 25% (14061/56374) |
| all maps · r300+ | k8 | 25852 | 87% (22440/25852) | 54% (1781/3328) | 92% (20659/22524) | 55% (14297/25852) | 30% (7708/25674) | 10% (2587/25852) | 35% (8968/25852) |
| all maps · r300+ | v1post | 19234 | 83% (15987/19234) | 56% (1785/3165) | 88% (14202/16069) | 56% (10686/19234) | 29% (5541/19045) | 10% (1912/19234) | 35% (6636/19234) |
| all maps · our length >= 8 | k8 | 1516 | 83% (1251/1516) | 99% (873/883) | 60% (378/633) | 51% (779/1516) | 32% (479/1511) | 4% (63/1516) | 44% (674/1516) |
| all maps · our length >= 8 | v1post | 1719 | 80% (1377/1719) | 99% (973/986) | 55% (404/733) | 50% (857/1719) | 31% (526/1704) | 4% (73/1719) | 46% (789/1719) |
| swarm · all turns | k8 | 62992 | 83% (52552/62992) | 40% (4391/11019) | 93% (48161/51973) | 59% (37175/62992) | 32% (20003/62707) | 15% (9424/62992) | 26% (16393/62992) |
| swarm · all turns | v1post | 56374 | 82% (46099/56374) | 40% (4395/10856) | 92% (41704/45518) | 60% (33564/56374) | 32% (17836/56078) | 16% (8749/56374) | 25% (14061/56374) |
| swarm · r300+ | k8 | 25852 | 87% (22440/25852) | 54% (1781/3328) | 92% (20659/22524) | 55% (14297/25852) | 30% (7708/25674) | 10% (2587/25852) | 35% (8968/25852) |
| swarm · r300+ | v1post | 19234 | 83% (15987/19234) | 56% (1785/3165) | 88% (14202/16069) | 56% (10686/19234) | 29% (5541/19045) | 10% (1912/19234) | 35% (6636/19234) |
| swarm · our length >= 8 | k8 | 1516 | 83% (1251/1516) | 99% (873/883) | 60% (378/633) | 51% (779/1516) | 32% (479/1511) | 4% (63/1516) | 44% (674/1516) |
| swarm · our length >= 8 | v1post | 1719 | 80% (1377/1719) | 99% (973/986) | 55% (404/733) | 50% (857/1719) | 31% (526/1704) | 4% (73/1719) | 46% (789/1719) |

## 4. Tags per game (our indicator labels), paired games

| family | bot | cl | conv | escape-split | feed | grab | no-exit | no-exit s | pocket-eat | sc | scx | sd | sf | sk | sq | sr | src | srn | srx | sx | sxc | sxx | tg | tgx |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| swarm | k8 | 685.2 | 2.8 | 12.1 | 7.3 | 139.9 | 21.3 | 2.7 | 0.2 | 17.1 | 16.0 | 4084.0 | 7.3 | 254.3 | 2.5 | 26.3 | 51.8 | 64.2 | 7.8 | 12.5 | 26.1 | 2.6 | 213.3 | 175.8 |
| swarm | v1post | 601.3 | 15.9 | 10.1 | 16.4 | 143.4 | 17.5 | 2.0 | 0.1 | 14.3 | 13.9 | 4084.0 | 16.4 | 253.9 | 2.7 | 30.1 | 50.9 | 59.0 | 8.6 | 12.5 | 26.1 | 2.6 | 204.7 | 167.4 |

sf recipients (k8, swarm maps): 408 feeds; recipient length 3-4: 31% (126/408), 5-7: 20% (82/408), 8-15: 31% (125/408), 16+: 18% (75/408).

## 5. Per map (paired): wins, r100 heads, natural intake, final longest, eliminated

| map | k8 W · u100 · nat · longest · elim | v1post W · u100 · nat · longest · elim |
|---|---|---|
| default | 1/8 · 9.0 · 82.0 · 12.0 · 1 | 0/8 · 9.0 · 72.9 · 9.6 · 2 |
| devil | 0/4 · 9.8 · 56.0 · 13.3 · 0 | 0/4 · 9.8 · 52.3 · 14.3 · 0 |
| devil_b | 0/4 · 8.0 · 51.5 · 5.8 · 1 | 0/4 · 8.0 · 52.5 · 6.5 · 1 |
| queen_of_spades | 1/4 · 4.8 · 135.3 · 12.5 · 0 | 1/4 · 4.8 · 125.5 · 10.5 · 0 |
| queen_of_spades_b | 0/4 · 5.0 · 73.3 · 7.0 · 0 | 0/4 · 5.0 · 70.5 · 10.5 · 0 |
| schooltime | 3/4 · 18.8 · 454.8 · 67.0 · 0 | 3/4 · 18.8 · 407.8 · 61.8 · 0 |
| schooltime_b | 1/4 · 9.8 · 96.8 · 15.8 · 0 | 0/4 · 9.8 · 90.5 · 12.3 · 0 |
| slithery_fight | 0/4 · 36.0 · 216.8 · 18.3 · 0 | 0/4 · 36.0 · 191.0 · 17.5 · 0 |
| slithery_fight_b | 0/4 · 30.3 · 239.0 · 17.3 · 0 | 0/4 · 30.3 · 224.8 · 16.3 · 0 |
| trauma | 2/8 · 7.0 · 87.9 · 11.5 · 0 | 1/8 · 7.0 · 88.1 · 12.8 · 0 |
| trophy | 0/8 · 10.3 · 28.1 · 0.0 · 8 | 0/8 · 10.3 · 28.1 · 0.0 · 8 |
