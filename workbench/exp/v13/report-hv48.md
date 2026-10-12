# v1 local report: v1.3-HV (exp/v13/hv-a, exp/v13/hv-b, exp/v13/hv-a34, exp/v13/hv-b34) vs v1.2 (exp/v11/v11bc-a-px4, exp/v11/v11bc-b-px4, exp/v13/base-a, exp/v13/base-b, exp/v13/base-a34, exp/v13/base-b34)

Paired games (same key): 48. v1.3-HV games 48, v1.2 games 88. Opponents: proxy4 (local mimics; sanity only, not a filter).

## 1. Five diagnostic indicators (EVAL.md §2) and outcome, paired games

| cell | bot | games | wins | r100 heads us / opp | r250 heads | natural intake us / opp (ratio) | line sac. pearls r300-499 (full games) | final longest us / opp | eliminated |
|---|---|---:|---:|---|---:|---|---|---|---|
| all maps | v1.3-HV | 48 | 7 | 29.0 / 43.0 | 25.3 | 277.4 / 1174.5 (24%) | 8.7 (48) | 23.6 / 32.3 | 0% (0/48) |
| all maps | v1.2 | 48 | 4 | 24.3 / 43.8 | 22.1 | 158.5 / 1161.1 (14%) | 6.0 (48) | 19.3 / 32.4 | 0% (0/48) |
| swarm | v1.3-HV | 48 | 7 | 29.0 / 43.0 | 25.3 | 277.4 / 1174.5 (24%) | 8.7 (48) | 23.6 / 32.3 | 0% (0/48) |
| swarm | v1.2 | 48 | 4 | 24.3 / 43.8 | 22.1 | 158.5 / 1161.1 (14%) | 6.0 (48) | 19.3 / 32.4 | 0% (0/48) |
| swarm · r500 | v1.3-HV | 48 | 7 | 29.0 / 43.0 | 25.3 | 277.4 / 1174.5 (24%) | 8.7 (48) | 23.6 / 32.3 | 0% (0/48) |
| swarm · r500 | v1.2 | 48 | 4 | 24.3 / 43.8 | 22.1 | 158.5 / 1161.1 (14%) | 6.0 (48) | 19.3 / 32.4 | 0% (0/48) |

## 2. Safety side effects (our deaths per game by cause, mass ledger; team longest >= 8 lost to an enemy head from r340)

| cell | bot | trapped | rammed (by enemy) | ram (we moved into a head) | ally head-on | sacrifice | longest lost from r340 |
|---|---|---:|---:|---:|---:|---:|---|
| all maps | v1.3-HV | 119.3 | 17.0 | 5.0 | 3.0 | 21.8 | 6% (3/48) |
| all maps | v1.2 | 31.9 | 14.4 | 4.6 | 1.5 | 17.4 | 15% (7/48) |
| swarm | v1.3-HV | 119.3 | 17.0 | 5.0 | 3.0 | 21.8 | 6% (3/48) |
| swarm | v1.2 | 31.9 | 14.4 | 4.6 | 1.5 | 17.4 | 15% (7/48) |
| swarm · r500 | v1.3-HV | 119.3 | 17.0 | 5.0 | 3.0 | 21.8 | 6% (3/48) |
| swarm · r500 | v1.2 | 31.9 | 14.4 | 4.6 | 1.5 | 17.4 | 15% (7/48) |

## 2b. The chain, link by link (paired games; per game means)

Heads r50 / r100 -> natural intake -> pieces born r100-430 (children <= 3 long; all births) -> our sacrifices (all; from r300) -> their drops from r300 -> line sacrifice pearls r300-499 (full games) and line share of those drops -> final longest.

| cell | bot | heads r50 · r100 | natural intake | pieces born r100-430 (births) | sacrifices (r300+) | sac. drops r300+ | line sac. pearls | line share | final longest | sf main · late feeds |
|---|---|---|---:|---|---|---:|---:|---:|---:|---|
| all maps | v1.3-HV | 24.7 · 29.0 | 277.4 | 69.5 (82.9) | 21.8 (14.6) | 25.6 | 8.7 | 34% | 23.6 | 18.3 · 3.6 |
| all maps | v1.2 | 19.8 · 24.3 | 158.5 | 30.4 (37.8) | 17.4 (11.6) | 19.4 | 6.0 | 31% | 19.3 | 14.0 · 3.5 |
| swarm | v1.3-HV | 24.7 · 29.0 | 277.4 | 69.5 (82.9) | 21.8 (14.6) | 25.6 | 8.7 | 34% | 23.6 | 18.3 · 3.6 |
| swarm | v1.2 | 19.8 · 24.3 | 158.5 | 30.4 (37.8) | 17.4 (11.6) | 19.4 | 6.0 | 31% | 19.3 | 14.0 · 3.5 |
| swarm · r500 | v1.3-HV | 24.7 · 29.0 | 277.4 | 69.5 (82.9) | 21.8 (14.6) | 25.6 | 8.7 | 34% | 23.6 | 18.3 · 3.6 |
| swarm · r500 | v1.2 | 19.8 · 24.3 | 158.5 | 30.4 (37.8) | 17.4 (11.6) | 19.4 | 6.0 | 31% | 19.3 | 14.0 · 3.5 |

## 2c. Target overlap (research transfer 1): target-labelled turns (v1 " sd", v0 " F") whose target another of our dragons also targets that round

| family | bot | target turns / game | same tile | within 3 |
|---|---|---:|---:|---:|
| swarm | v1.3-HV | 2465.9 | 9.2% | 48.4% |
| swarm | v1.2 | 3237.3 | 10.6% | 54.0% |

## 3. Belief accuracy (tag " bl<len>@x,y k<0|1>" every 5 rounds vs the true longest other living ally at that turn start)

| cell | bot | tagged turns | king verdict right | truly longest: says king | not longest: says not king | length within 1 | position within 3 | believes longer than true (+2) | believes shorter (-2) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all maps · all turns | v1.3-HV | 92482 | 94% (86981/92482) | 64% (4072/6338) | 96% (82909/86144) | 47% (43840/92482) | 27% (25420/92482) | 25% (23553/92482) | 27% (25089/92482) |
| all maps · all turns | v1.2 | 80587 | 91% (73036/80587) | 55% (4061/7404) | 94% (68975/73183) | 46% (37387/80587) | 26% (21125/80587) | 25% (20005/80587) | 29% (23195/80587) |
| all maps · r300+ | v1.3-HV | 24125 | 93% (22437/24125) | 86% (1861/2170) | 94% (20576/21955) | 53% (12684/24125) | 31% (7429/24125) | 8% (1935/24125) | 39% (9506/24125) |
| all maps · r300+ | v1.2 | 22262 | 89% (19796/22262) | 79% (1904/2412) | 90% (17892/19850) | 51% (11402/22262) | 28% (6125/22262) | 10% (2201/22262) | 39% (8659/22262) |
| all maps · our length >= 8 | v1.3-HV | 4784 | 86% (4122/4784) | 94% (2545/2717) | 76% (1577/2067) | 56% (2689/4784) | 36% (1733/4784) | 10% (470/4784) | 34% (1625/4784) |
| all maps · our length >= 8 | v1.2 | 4136 | 81% (3334/4136) | 95% (2321/2451) | 60% (1013/1685) | 49% (2036/4136) | 30% (1229/4136) | 10% (412/4136) | 41% (1688/4136) |
| swarm · all turns | v1.3-HV | 92482 | 94% (86981/92482) | 64% (4072/6338) | 96% (82909/86144) | 47% (43840/92482) | 27% (25420/92482) | 25% (23553/92482) | 27% (25089/92482) |
| swarm · all turns | v1.2 | 80587 | 91% (73036/80587) | 55% (4061/7404) | 94% (68975/73183) | 46% (37387/80587) | 26% (21125/80587) | 25% (20005/80587) | 29% (23195/80587) |
| swarm · r300+ | v1.3-HV | 24125 | 93% (22437/24125) | 86% (1861/2170) | 94% (20576/21955) | 53% (12684/24125) | 31% (7429/24125) | 8% (1935/24125) | 39% (9506/24125) |
| swarm · r300+ | v1.2 | 22262 | 89% (19796/22262) | 79% (1904/2412) | 90% (17892/19850) | 51% (11402/22262) | 28% (6125/22262) | 10% (2201/22262) | 39% (8659/22262) |
| swarm · our length >= 8 | v1.3-HV | 4784 | 86% (4122/4784) | 94% (2545/2717) | 76% (1577/2067) | 56% (2689/4784) | 36% (1733/4784) | 10% (470/4784) | 34% (1625/4784) |
| swarm · our length >= 8 | v1.2 | 4136 | 81% (3334/4136) | 95% (2321/2451) | 60% (1013/1685) | 49% (2036/4136) | 30% (1229/4136) | 10% (412/4136) | 41% (1688/4136) |

## 4. Tags per game (our indicator labels), paired games

| family | bot | cl | conv | escape-split | feed | grab | no-exit | no-exit s | pocket-eat | sc | scx | sd | sf | sk | sq | sr | src | srn | srx | sx | sxc | sxx | tg | tgx |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| swarm | v1.3-HV | 687.8 | 18.3 | 43.6 | 21.9 | 336.4 | 117.9 | 6.4 | 0.1 | 43.1 | 55.8 | 2465.9 | 21.9 | 491.4 | 5.1 | 31.1 | 37.2 | 585.3 | 4.3 | 35.0 | 59.9 | 9.1 | 264.0 | 193.1 |
| swarm | v1.2 | 536.7 | 14.0 | 21.1 | 17.5 | 203.8 | 31.3 | 2.1 | 0.1 | 30.6 | 41.4 | 3237.3 | 17.5 | 576.5 | 4.7 | 24.6 | 28.4 | 374.2 | 4.0 | 23.8 | 40.5 | 5.9 | 248.4 | 183.0 |

sf recipients (v1.3-HV, swarm maps): 1052 feeds; recipient length 3-4: 7% (76/1052), 5-7: 5% (54/1052), 8-15: 57% (597/1052), 16+: 31% (325/1052).

## 5. Per map (paired): wins, r100 heads, natural intake, final longest, eliminated

| map | v1.3-HV W · u100 · nat · longest · elim | v1.2 W · u100 · nat · longest · elim |
|---|---|---|
| slithery_fight | 2/16 · 43.9 · 387.6 · 30.1 · 0 | 3/16 · 39.2 · 205.3 · 26.3 · 0 |
| slithery_fight_b | 1/16 · 35.9 · 342.4 · 23.6 · 0 | 0/16 · 27.8 · 195.7 · 18.5 · 0 |
| trauma | 4/16 · 7.1 · 102.3 · 17.1 · 0 | 1/16 · 5.8 · 74.5 · 13.2 · 0 |
