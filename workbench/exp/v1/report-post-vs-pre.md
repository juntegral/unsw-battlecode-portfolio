# v1 local report: v1post (exp/v1/v1post-a-px4, exp/v1/v1post-b-px4) vs v1pre (exp/v1/v1-a-px4, exp/v1/v1-b-px4)

Paired games (same key): 56. v1post games 56, v1pre games 120. Opponents: proxy4 (local mimics; sanity only, not a filter).

## 1. Five diagnostic indicators (EVAL.md §2) and outcome, paired games

| cell | bot | games | wins | r100 heads us / opp | r250 heads | natural intake us / opp (ratio) | line sac. pearls r300-499 (full games) | final longest us / opp | eliminated |
|---|---|---:|---:|---|---:|---|---|---|---|
| all maps | v1post | 56 | 5 | 12.5 / 26.9 | 11.9 | 113.8 / 551.7 (21%) | 4.5 (45) | 13.9 / 24.4 | 20% (11/56) |
| all maps | v1pre | 56 | 8 | 12.3 / 26.4 | 12.0 | 133.5 / 549.8 (24%) | 4.9 (45) | 14.6 / 23.0 | 20% (11/56) |
| swarm | v1post | 56 | 5 | 12.5 / 26.9 | 11.9 | 113.8 / 551.7 (21%) | 4.5 (45) | 13.9 / 24.4 | 20% (11/56) |
| swarm | v1pre | 56 | 8 | 12.3 / 26.4 | 12.0 | 133.5 / 549.8 (24%) | 4.9 (45) | 14.6 / 23.0 | 20% (11/56) |
| swarm · r500 | v1post | 24 | 4 | 18.1 / 32.3 | 20.8 | 181.7 / 861.0 (21%) | 6.1 (24) | 22.2 / 32.0 | 0% (0/24) |
| swarm · r500 | v1pre | 24 | 6 | 17.4 / 31.8 | 20.7 | 219.0 / 855.2 (26%) | 7.3 (24) | 24.3 / 28.7 | 0% (0/24) |
| swarm · elim | v1post | 32 | 1 | 8.3 / 23.0 | 5.2 | 62.8 / 319.7 (20%) | 2.7 (21) | 7.6 / 18.8 | 34% (11/32) |
| swarm · elim | v1pre | 32 | 2 | 8.4 / 22.4 | 5.6 | 69.3 / 320.7 (22%) | 2.2 (21) | 7.3 / 18.7 | 34% (11/32) |

## 2. Safety side effects (our deaths per game by cause, mass ledger; team longest >= 8 lost to an enemy head from r340)

| cell | bot | trapped | rammed (by enemy) | ram (we moved into a head) | ally head-on | sacrifice | longest lost from r340 |
|---|---|---:|---:|---:|---:|---:|---|
| all maps | v1post | 17.8 | 14.1 | 3.0 | 1.3 | 16.4 | 9% (4/47) |
| all maps | v1pre | 21.3 | 14.2 | 3.1 | 1.9 | 19.6 | 9% (4/47) |
| swarm | v1post | 17.8 | 14.1 | 3.0 | 1.3 | 16.4 | 9% (4/47) |
| swarm | v1pre | 21.3 | 14.2 | 3.1 | 1.9 | 19.6 | 9% (4/47) |
| swarm · r500 | v1post | 30.3 | 17.1 | 4.3 | 1.8 | 32.9 | 0% (0/24) |
| swarm · r500 | v1pre | 36.2 | 16.8 | 4.3 | 2.6 | 38.8 | 13% (3/24) |
| swarm · elim | v1post | 8.5 | 11.8 | 2.1 | 0.9 | 4.1 | 17% (4/23) |
| swarm · elim | v1pre | 10.2 | 12.3 | 2.2 | 1.3 | 5.2 | 4% (1/23) |

## 2b. The chain, link by link (paired games; per game means)

Heads r50 / r100 -> natural intake -> pieces born r100-430 (children <= 3 long; all births) -> our sacrifices (all; from r300) -> their drops from r300 -> line sacrifice pearls r300-499 (full games) and line share of those drops -> final longest.

| cell | bot | heads r50 · r100 | natural intake | pieces born r100-430 (births) | sacrifices (r300+) | sac. drops r300+ | line sac. pearls | line share | final longest | sf main · late feeds |
|---|---|---|---:|---|---|---:|---:|---:|---:|---|
| all maps | v1post | 9.3 · 12.5 | 113.8 | 33.6 (36.5) | 16.4 (16.4) | 23.5 | 4.5 | 15% | 13.9 | 15.9 · 0.4 |
| all maps | v1pre | 9.4 · 12.3 | 133.5 | 40.6 (44.0) | 19.6 (19.5) | 28.9 | 4.9 | 14% | 14.6 | 18.8 · 0.0 |
| swarm | v1post | 9.3 · 12.5 | 113.8 | 33.6 (36.5) | 16.4 (16.4) | 23.5 | 4.5 | 15% | 13.9 | 15.9 · 0.4 |
| swarm | v1pre | 9.4 · 12.3 | 133.5 | 40.6 (44.0) | 19.6 (19.5) | 28.9 | 4.9 | 14% | 14.6 | 18.8 · 0.0 |
| swarm · r500 | v1post | 13.1 · 18.1 | 181.7 | 59.0 (64.4) | 32.9 (32.9) | 46.2 | 6.1 | 13% | 22.2 | 32.1 · 0.8 |
| swarm · r500 | v1pre | 13.1 · 17.4 | 219.0 | 69.6 (77.1) | 38.8 (38.7) | 57.2 | 7.3 | 13% | 24.3 | 37.4 · 0.0 |
| swarm · elim | v1post | 6.4 · 8.3 | 62.8 | 14.5 (15.6) | 4.1 (4.1) | 6.4 | 2.7 | 27% | 7.6 | 3.8 · 0.2 |
| swarm · elim | v1pre | 6.5 · 8.4 | 69.3 | 18.9 (19.2) | 5.2 (5.2) | 7.7 | 2.2 | 19% | 7.3 | 4.8 · 0.0 |

## 2c. Target overlap (research transfer 1): target-labelled turns (v1 " sd", v0 " F") whose target another of our dragons also targets that round

| family | bot | target turns / game | same tile | within 3 |
|---|---|---:|---:|---:|
| swarm | v1post | 4084.0 | 17.5% | 55.4% |
| swarm | v1pre | 4088.2 | 25.0% | 67.5% |

## 3. Belief accuracy (tag " bl<len>@x,y k<0|1>" every 5 rounds vs the true longest other living ally at that turn start)

| cell | bot | tagged turns | king verdict right | truly longest: says king | not longest: says not king | length within 1 | position within 3 | believes longer than true (+2) | believes shorter (-2) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all maps · all turns | v1post | 56374 | 82% (46099/56374) | 40% (4395/10856) | 92% (41704/45518) | 60% (33564/56374) | 32% (17836/56078) | 16% (8749/56374) | 25% (14061/56374) |
| all maps · all turns | v1pre | 57931 | 82% (47291/57931) | 41% (4273/10535) | 91% (43018/47396) | 57% (32871/57931) | 30% (17066/57760) | 13% (7654/57931) | 30% (17406/57931) |
| all maps · r300+ | v1post | 19234 | 83% (15987/19234) | 56% (1785/3165) | 88% (14202/16069) | 56% (10686/19234) | 29% (5541/19045) | 10% (1912/19234) | 35% (6636/19234) |
| all maps · r300+ | v1pre | 20611 | 83% (17206/20611) | 62% (1842/2953) | 87% (15364/17658) | 50% (10217/20611) | 26% (5407/20527) | 6% (1313/20611) | 44% (9081/20611) |
| all maps · our length >= 8 | v1post | 1719 | 80% (1377/1719) | 99% (973/986) | 55% (404/733) | 50% (857/1719) | 31% (526/1704) | 4% (73/1719) | 46% (789/1719) |
| all maps · our length >= 8 | v1pre | 1995 | 76% (1526/1995) | 99% (1202/1212) | 41% (324/783) | 43% (862/1995) | 21% (415/1972) | 5% (90/1995) | 52% (1043/1995) |
| swarm · all turns | v1post | 56374 | 82% (46099/56374) | 40% (4395/10856) | 92% (41704/45518) | 60% (33564/56374) | 32% (17836/56078) | 16% (8749/56374) | 25% (14061/56374) |
| swarm · all turns | v1pre | 57931 | 82% (47291/57931) | 41% (4273/10535) | 91% (43018/47396) | 57% (32871/57931) | 30% (17066/57760) | 13% (7654/57931) | 30% (17406/57931) |
| swarm · r300+ | v1post | 19234 | 83% (15987/19234) | 56% (1785/3165) | 88% (14202/16069) | 56% (10686/19234) | 29% (5541/19045) | 10% (1912/19234) | 35% (6636/19234) |
| swarm · r300+ | v1pre | 20611 | 83% (17206/20611) | 62% (1842/2953) | 87% (15364/17658) | 50% (10217/20611) | 26% (5407/20527) | 6% (1313/20611) | 44% (9081/20611) |
| swarm · our length >= 8 | v1post | 1719 | 80% (1377/1719) | 99% (973/986) | 55% (404/733) | 50% (857/1719) | 31% (526/1704) | 4% (73/1719) | 46% (789/1719) |
| swarm · our length >= 8 | v1pre | 1995 | 76% (1526/1995) | 99% (1202/1212) | 41% (324/783) | 43% (862/1995) | 21% (415/1972) | 5% (90/1995) | 52% (1043/1995) |

## 4. Tags per game (our indicator labels), paired games

| family | bot | bsp | cl | conv | escape-split | feed | floor | frag | grab | kcap | no-exit | no-exit s | pocket-eat | sc | scx | sd | sf | sk | sq | sr | src | srn | srx | sx | sxc | sxx | tg | tgx |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| swarm | v1post | 0.0 | 601.3 | 15.9 | 10.1 | 16.4 | 0.0 | 0.0 | 143.4 | 0.0 | 17.5 | 2.0 | 0.1 | 14.3 | 13.9 | 4084.0 | 16.4 | 253.9 | 2.7 | 30.1 | 50.9 | 59.0 | 8.6 | 12.5 | 26.1 | 2.6 | 204.7 | 167.4 |
| swarm | v1pre | 0.9 | 640.1 | 18.8 | 11.9 | 19.6 | 0.6 | 0.5 | 168.8 | 0.0 | 20.9 | 2.6 | 0.0 | 19.9 | 17.1 | 4088.2 | 18.8 | 297.5 | 2.9 | 34.8 | 55.3 | 48.7 | 8.8 | 11.8 | 23.3 | 2.8 | 214.9 | 176.5 |

sf recipients (v1post, swarm maps): 918 feeds; recipient length 3-4: 82% (749/918), 5-7: 9% (79/918), 8-15: 8% (70/918), 16+: 2% (20/918).

## 5. Per map (paired): wins, r100 heads, natural intake, final longest, eliminated

| map | v1post W · u100 · nat · longest · elim | v1pre W · u100 · nat · longest · elim |
|---|---|---|
| default | 0/8 · 9.0 · 72.9 · 9.6 · 2 | 1/8 · 11.9 · 105.9 · 9.8 · 2 |
| devil | 0/4 · 9.8 · 52.3 · 14.3 · 0 | 0/4 · 7.0 · 59.5 · 9.5 · 0 |
| devil_b | 0/4 · 8.0 · 52.5 · 6.5 · 1 | 0/4 · 8.5 · 64.8 · 10.0 · 0 |
| queen_of_spades | 1/4 · 4.8 · 125.5 · 10.5 · 0 | 0/4 · 4.8 · 89.8 · 9.5 · 1 |
| queen_of_spades_b | 0/4 · 5.0 · 70.5 · 10.5 · 0 | 1/4 · 4.8 · 67.0 · 9.5 · 0 |
| schooltime | 3/4 · 18.8 · 407.8 · 61.8 · 0 | 4/4 · 21.0 · 599.3 · 61.3 · 0 |
| schooltime_b | 0/4 · 9.8 · 90.5 · 12.3 · 0 | 1/4 · 10.5 · 162.5 · 16.8 · 0 |
| slithery_fight | 0/4 · 36.0 · 191.0 · 17.5 · 0 | 0/4 · 34.3 · 188.5 · 22.8 · 0 |
| slithery_fight_b | 0/4 · 30.3 · 224.8 · 16.3 · 0 | 0/4 · 26.0 · 205.8 · 15.3 · 0 |
| trauma | 1/8 · 7.0 · 88.1 · 12.8 · 0 | 1/8 · 6.4 · 78.9 · 14.9 · 0 |
| trophy | 0/8 · 10.3 · 28.1 · 0.0 · 8 | 0/8 · 9.3 · 31.0 · 0.0 · 8 |
