# v1 local report: v1post (exp/v1/v1post-a-px4, exp/v1/v1post-b-px4) vs v0t (exp/v1/v0t-a-px4, exp/v1/v0t-b-px4)

Paired games (same key): 56. v1post games 56, v0t games 120. Opponents: proxy4 (local mimics; sanity only, not a filter).

## 1. Five diagnostic indicators (EVAL.md §2) and outcome, paired games

| cell | bot | games | wins | r100 heads us / opp | r250 heads | natural intake us / opp (ratio) | line sac. pearls r300-499 (full games) | final longest us / opp | eliminated |
|---|---|---:|---:|---|---:|---|---|---|---|
| all maps | v1post | 56 | 5 | 12.5 / 26.9 | 11.9 | 113.8 / 551.7 (21%) | 4.5 (45) | 13.9 / 24.4 | 20% (11/56) |
| all maps | v0t | 56 | 9 | 9.1 / 27.9 | 9.4 | 89.0 / 550.5 (16%) | 5.2 (43) | 15.6 / 24.7 | 21% (12/56) |
| swarm | v1post | 56 | 5 | 12.5 / 26.9 | 11.9 | 113.8 / 551.7 (21%) | 4.5 (45) | 13.9 / 24.4 | 20% (11/56) |
| swarm | v0t | 56 | 9 | 9.1 / 27.9 | 9.4 | 89.0 / 550.5 (16%) | 5.2 (43) | 15.6 / 24.7 | 21% (12/56) |
| swarm · r500 | v1post | 24 | 4 | 18.1 / 32.3 | 20.8 | 181.7 / 861.0 (21%) | 6.1 (24) | 22.2 / 32.0 | 0% (0/24) |
| swarm · r500 | v0t | 24 | 4 | 11.1 / 33.2 | 13.3 | 116.4 / 865.5 (13%) | 6.4 (24) | 24.3 / 32.8 | 0% (0/24) |
| swarm · elim | v1post | 32 | 1 | 8.3 / 23.0 | 5.2 | 62.8 / 319.7 (20%) | 2.7 (21) | 7.6 / 18.8 | 34% (11/32) |
| swarm · elim | v0t | 32 | 5 | 7.5 / 23.9 | 6.4 | 68.5 / 314.3 (22%) | 3.6 (19) | 9.1 / 18.7 | 38% (12/32) |

## 2. Safety side effects (our deaths per game by cause, mass ledger; team longest >= 8 lost to an enemy head from r340)

| cell | bot | trapped | rammed (by enemy) | ram (we moved into a head) | ally head-on | sacrifice | longest lost from r340 |
|---|---|---:|---:|---:|---:|---:|---|
| all maps | v1post | 17.8 | 14.1 | 3.0 | 1.3 | 16.4 | 9% (4/47) |
| all maps | v0t | 13.2 | 10.3 | 2.5 | 1.2 | 4.0 | 11% (5/46) |
| swarm | v1post | 17.8 | 14.1 | 3.0 | 1.3 | 16.4 | 9% (4/47) |
| swarm | v0t | 13.2 | 10.3 | 2.5 | 1.2 | 4.0 | 11% (5/46) |
| swarm · r500 | v1post | 30.3 | 17.1 | 4.3 | 1.8 | 32.9 | 0% (0/24) |
| swarm · r500 | v0t | 17.4 | 9.8 | 2.5 | 1.0 | 6.9 | 13% (3/24) |
| swarm · elim | v1post | 8.5 | 11.8 | 2.1 | 0.9 | 4.1 | 17% (4/23) |
| swarm · elim | v0t | 10.1 | 10.7 | 2.5 | 1.3 | 1.9 | 9% (2/22) |

## 2b. The chain, link by link (paired games; per game means)

Heads r50 / r100 -> natural intake -> pieces born r100-430 (children <= 3 long; all births) -> our sacrifices (all; from r300) -> their drops from r300 -> line sacrifice pearls r300-499 (full games) and line share of those drops -> final longest.

| cell | bot | heads r50 · r100 | natural intake | pieces born r100-430 (births) | sacrifices (r300+) | sac. drops r300+ | line sac. pearls | line share | final longest | sf main · late feeds |
|---|---|---|---:|---|---|---:|---:|---:|---:|---|
| all maps | v1post | 9.3 · 12.5 | 113.8 | 33.6 (36.5) | 16.4 (16.4) | 23.5 | 4.5 | 15% | 13.9 | 15.9 · 0.4 |
| all maps | v0t | 7.2 · 9.1 | 89.0 | 16.5 (19.3) | 4.0 (4.0) | 8.6 | 5.2 | 46% | 15.6 | 0.0 · 0.0 |
| swarm | v1post | 9.3 · 12.5 | 113.8 | 33.6 (36.5) | 16.4 (16.4) | 23.5 | 4.5 | 15% | 13.9 | 15.9 · 0.4 |
| swarm | v0t | 7.2 · 9.1 | 89.0 | 16.5 (19.3) | 4.0 (4.0) | 8.6 | 5.2 | 46% | 15.6 | 0.0 · 0.0 |
| swarm · r500 | v1post | 13.1 · 18.1 | 181.7 | 59.0 (64.4) | 32.9 (32.9) | 46.2 | 6.1 | 13% | 22.2 | 32.1 · 0.8 |
| swarm · r500 | v0t | 7.9 · 11.1 | 116.4 | 19.6 (24.5) | 6.9 (6.9) | 13.8 | 6.4 | 46% | 24.3 | 0.0 · 0.0 |
| swarm · elim | v1post | 6.4 · 8.3 | 62.8 | 14.5 (15.6) | 4.1 (4.1) | 6.4 | 2.7 | 27% | 7.6 | 3.8 · 0.2 |
| swarm · elim | v0t | 6.7 · 7.5 | 68.5 | 14.2 (15.3) | 1.9 (1.9) | 4.7 | 3.6 | 46% | 9.1 | 0.0 · 0.0 |

## 2c. Target overlap (research transfer 1): target-labelled turns (v1 " sd", v0 " F") whose target another of our dragons also targets that round

| family | bot | target turns / game | same tile | within 3 |
|---|---|---:|---:|---:|
| swarm | v1post | 4084.0 | 17.5% | 55.4% |
| swarm | v0t | 117.6 | 18.1% | 30.6% |

## 3. Belief accuracy (tag " bl<len>@x,y k<0|1>" every 5 rounds vs the true longest other living ally at that turn start)

| cell | bot | tagged turns | king verdict right | truly longest: says king | not longest: says not king | length within 1 | position within 3 | believes longer than true (+2) | believes shorter (-2) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all maps · all turns | v1post | 56374 | 82% (46099/56374) | 40% (4395/10856) | 92% (41704/45518) | 60% (33564/56374) | 32% (17836/56078) | 16% (8749/56374) | 25% (14061/56374) |
| all maps · all turns | v0t | 41391 | 79% (32869/41391) | 23% (2218/9560) | 96% (30651/31831) | 49% (20085/41391) | 25% (10510/41268) | 24% (9850/41391) | 28% (11456/41391) |
| all maps · r300+ | v1post | 19234 | 83% (15987/19234) | 56% (1785/3165) | 88% (14202/16069) | 56% (10686/19234) | 29% (5541/19045) | 10% (1912/19234) | 35% (6636/19234) |
| all maps · r300+ | v0t | 12823 | 84% (10750/12823) | 42% (1091/2608) | 95% (9659/10215) | 43% (5475/12823) | 23% (2994/12764) | 29% (3657/12823) | 29% (3691/12823) |
| all maps · our length >= 8 | v1post | 1719 | 80% (1377/1719) | 99% (973/986) | 55% (404/733) | 50% (857/1719) | 31% (526/1704) | 4% (73/1719) | 46% (789/1719) |
| all maps · our length >= 8 | v0t | 2209 | 67% (1486/2209) | 75% (1182/1581) | 48% (304/628) | 26% (575/2209) | 15% (336/2203) | 41% (901/2209) | 33% (733/2209) |
| swarm · all turns | v1post | 56374 | 82% (46099/56374) | 40% (4395/10856) | 92% (41704/45518) | 60% (33564/56374) | 32% (17836/56078) | 16% (8749/56374) | 25% (14061/56374) |
| swarm · all turns | v0t | 41391 | 79% (32869/41391) | 23% (2218/9560) | 96% (30651/31831) | 49% (20085/41391) | 25% (10510/41268) | 24% (9850/41391) | 28% (11456/41391) |
| swarm · r300+ | v1post | 19234 | 83% (15987/19234) | 56% (1785/3165) | 88% (14202/16069) | 56% (10686/19234) | 29% (5541/19045) | 10% (1912/19234) | 35% (6636/19234) |
| swarm · r300+ | v0t | 12823 | 84% (10750/12823) | 42% (1091/2608) | 95% (9659/10215) | 43% (5475/12823) | 23% (2994/12764) | 29% (3657/12823) | 29% (3691/12823) |
| swarm · our length >= 8 | v1post | 1719 | 80% (1377/1719) | 99% (973/986) | 55% (404/733) | 50% (857/1719) | 31% (526/1704) | 4% (73/1719) | 46% (789/1719) |
| swarm · our length >= 8 | v0t | 2209 | 67% (1486/2209) | 75% (1182/1581) | 48% (304/628) | 26% (575/2209) | 15% (336/2203) | 41% (901/2209) | 33% (733/2209) |

## 4. Tags per game (our indicator labels), paired games

| family | bot | bsp | cl | conv | csplit | escape-split | feed | floor | frag | gh | grab | kcap | kx | lsplit | no-exit | no-exit s | pocket-eat | sc | scx | sd | sf | sk | sq | sr | src | srn | srx | sx | sxc | sxx | tg | tgx |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| swarm | v1post | 0.0 | 601.3 | 15.9 | 0.0 | 10.1 | 16.4 | 0.0 | 0.0 | 0.0 | 143.4 | 0.0 | 0.0 | 0.0 | 17.5 | 2.0 | 0.1 | 14.3 | 13.9 | 4084.0 | 16.4 | 253.9 | 2.7 | 30.1 | 50.9 | 59.0 | 8.6 | 12.5 | 26.1 | 2.6 | 204.7 | 167.4 |
| swarm | v0t | 0.6 | 405.3 | 1.8 | 17.1 | 7.7 | 4.0 | 0.5 | 0.3 | 12.2 | 82.6 | 0.0 | 14.4 | 4.7 | 12.7 | 1.6 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 177.5 | 135.7 |

sf recipients (v1post, swarm maps): 918 feeds; recipient length 3-4: 82% (749/918), 5-7: 9% (79/918), 8-15: 8% (70/918), 16+: 2% (20/918).

## 5. Per map (paired): wins, r100 heads, natural intake, final longest, eliminated

| map | v1post W · u100 · nat · longest · elim | v0t W · u100 · nat · longest · elim |
|---|---|---|
| default | 0/8 · 9.0 · 72.9 · 9.6 · 2 | 3/8 · 12.3 · 124.9 · 17.1 · 1 |
| devil | 0/4 · 9.8 · 52.3 · 14.3 · 0 | 0/4 · 7.0 · 56.0 · 12.0 · 0 |
| devil_b | 0/4 · 8.0 · 52.5 · 6.5 · 1 | 0/4 · 6.3 · 53.0 · 7.8 · 1 |
| queen_of_spades | 1/4 · 4.8 · 125.5 · 10.5 · 0 | 2/4 · 4.5 · 91.5 · 15.8 · 0 |
| queen_of_spades_b | 0/4 · 5.0 · 70.5 · 10.5 · 0 | 0/4 · 4.5 · 42.0 · 3.3 · 2 |
| schooltime | 3/4 · 18.8 · 407.8 · 61.8 · 0 | 2/4 · 14.8 · 225.5 · 49.0 · 0 |
| schooltime_b | 0/4 · 9.8 · 90.5 · 12.3 · 0 | 0/4 · 9.0 · 57.3 · 11.5 · 0 |
| slithery_fight | 0/4 · 36.0 · 191.0 · 17.5 · 0 | 1/4 · 16.8 · 116.8 · 32.5 · 0 |
| slithery_fight_b | 0/4 · 30.3 · 224.8 · 16.3 · 0 | 1/4 · 13.0 · 138.0 · 22.0 · 0 |
| trauma | 1/8 · 7.0 · 88.1 · 12.8 · 0 | 0/8 · 6.5 · 80.4 · 15.5 · 0 |
| trophy | 0/8 · 10.3 · 28.1 · 0.0 · 8 | 0/8 · 6.8 · 27.8 · 0.0 · 8 |
