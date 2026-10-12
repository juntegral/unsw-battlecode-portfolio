# v1 local report: v1fix (exp/v1/v1fix-a-px4) vs v1pre (exp/v1/v1-a-px4)

Paired games (same key): 6. v1fix games 6, v1pre games 60. Opponents: proxy4 (local mimics; sanity only, not a filter).

## 1. Five diagnostic indicators (EVAL.md §2) and outcome, paired games

| cell | bot | games | wins | r100 heads us / opp | r250 heads | natural intake us / opp (ratio) | line sac. pearls r300-499 (full games) | final longest us / opp | eliminated |
|---|---|---:|---:|---|---:|---|---|---|---|
| all maps | v1fix | 6 | 1 | 24.0 / 40.5 | 26.0 | 277.0 / 871.0 (32%) | 2.8 (6) | 20.3 / 34.0 | 0% (0/6) |
| all maps | v1pre | 6 | 2 | 21.2 / 38.2 | 24.8 | 357.0 / 878.0 (41%) | 9.0 (6) | 27.3 / 33.7 | 0% (0/6) |
| swarm | v1fix | 6 | 1 | 24.0 / 40.5 | 26.0 | 277.0 / 871.0 (32%) | 2.8 (6) | 20.3 / 34.0 | 0% (0/6) |
| swarm | v1pre | 6 | 2 | 21.2 / 38.2 | 24.8 | 357.0 / 878.0 (41%) | 9.0 (6) | 27.3 / 33.7 | 0% (0/6) |
| swarm · r500 | v1fix | 4 | 0 | 29.0 / 53.3 | 33.0 | 330.8 / 1201.0 (28%) | 4.3 (4) | 22.8 / 39.3 | 0% (0/4) |
| swarm · r500 | v1pre | 4 | 2 | 26.5 / 51.3 | 29.8 | 474.3 / 1195.8 (40%) | 12.5 (4) | 36.8 / 36.5 | 0% (0/4) |
| swarm · elim | v1fix | 2 | 1 | 14.0 / 15.0 | 12.0 | 169.5 / 211.0 (80%) | 0.0 (2) | 15.5 / 23.5 | 0% (0/2) |
| swarm · elim | v1pre | 2 | 0 | 10.5 / 12.0 | 15.0 | 122.5 / 242.5 (51%) | 2.0 (2) | 8.5 / 28.0 | 0% (0/2) |

## 2. Safety side effects (our deaths per game by cause, mass ledger; team longest >= 8 lost to an enemy head from r340)

| cell | bot | trapped | rammed (by enemy) | ram (we moved into a head) | ally head-on | sacrifice | longest lost from r340 |
|---|---|---:|---:|---:|---:|---:|---|
| all maps | v1fix | 41.8 | 21.0 | 7.7 | 3.3 | 19.8 | 50% (3/6) |
| all maps | v1pre | 76.5 | 21.3 | 6.7 | 5.3 | 53.5 | 17% (1/6) |
| swarm | v1fix | 41.8 | 21.0 | 7.7 | 3.3 | 19.8 | 50% (3/6) |
| swarm | v1pre | 76.5 | 21.3 | 6.7 | 5.3 | 53.5 | 17% (1/6) |
| swarm · r500 | v1fix | 49.8 | 24.0 | 9.0 | 2.0 | 27.0 | 50% (2/4) |
| swarm · r500 | v1pre | 101.8 | 23.5 | 7.3 | 3.0 | 74.8 | 25% (1/4) |
| swarm · elim | v1fix | 26.0 | 15.0 | 5.0 | 6.0 | 5.5 | 50% (1/2) |
| swarm · elim | v1pre | 26.0 | 17.0 | 5.5 | 10.0 | 11.0 | 0% (0/2) |

## 2b. The chain, link by link (paired games; per game means)

Heads r50 / r100 -> natural intake -> pieces born r100-430 (children <= 3 long; all births) -> our sacrifices (all; from r300) -> their drops from r300 -> line sacrifice pearls r300-499 (full games) and line share of those drops -> final longest.

| cell | bot | heads r50 · r100 | natural intake | pieces born r100-430 (births) | sacrifices (r300+) | sac. drops r300+ | line sac. pearls | line share | final longest | sf main · late feeds |
|---|---|---|---:|---|---|---:|---:|---:|---:|---|
| all maps | v1fix | 16.5 · 24.0 | 277.0 | 58.0 (68.2) | 19.8 (13.8) | 26.2 | 2.8 | 11% | 20.3 | 15.0 · 4.3 |
| all maps | v1pre | 15.2 · 21.2 | 357.0 | 115.7 (131.5) | 53.5 (53.3) | 87.3 | 9.0 | 10% | 27.3 | 50.8 · 0.0 |
| swarm | v1fix | 16.5 · 24.0 | 277.0 | 58.0 (68.2) | 19.8 (13.8) | 26.2 | 2.8 | 11% | 20.3 | 15.0 · 4.3 |
| swarm | v1pre | 15.2 · 21.2 | 357.0 | 115.7 (131.5) | 53.5 (53.3) | 87.3 | 9.0 | 10% | 27.3 | 50.8 · 0.0 |
| swarm · r500 | v1fix | 20.8 · 29.0 | 330.8 | 65.5 (78.8) | 27.0 (18.3) | 34.3 | 4.3 | 12% | 22.8 | 20.3 · 6.5 |
| swarm · r500 | v1pre | 18.8 · 26.5 | 474.3 | 143.3 (167.0) | 74.8 (74.5) | 123.8 | 12.5 | 10% | 36.8 | 71.3 · 0.0 |
| swarm · elim | v1fix | 8.0 · 14.0 | 169.5 | 43.0 (47.0) | 5.5 (5.0) | 10.0 | 0.0 | 0% | 15.5 | 4.5 · 0.0 |
| swarm · elim | v1pre | 8.0 · 10.5 | 122.5 | 60.5 (60.5) | 11.0 (11.0) | 14.5 | 2.0 | 14% | 8.5 | 10.0 · 0.0 |

## 2c. Target overlap (research transfer 1): target-labelled turns (v1 " sd", v0 " F") whose target another of our dragons also targets that round

| family | bot | target turns / game | same tile | within 3 |
|---|---|---:|---:|---:|
| swarm | v1fix | 4314.8 | 9.8% | 46.1% |
| swarm | v1pre | 8066.7 | 28.2% | 71.7% |

## 3. Belief accuracy (tag " bl<len>@x,y k<0|1>" every 5 rounds vs the true longest other living ally at that turn start)

| cell | bot | tagged turns | king verdict right | truly longest: says king | not longest: says not king | length within 1 | position within 3 | believes longer than true (+2) | believes shorter (-2) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all maps · all turns | v1fix | 12023 | 91% (10910/12023) | 61% (558/922) | 93% (10352/11101) | 37% (4392/12023) | 20% (2361/12023) | 9% (1057/12023) | 55% (6574/12023) |
| all maps · all turns | v1pre | 12368 | 86% (10686/12368) | 37% (454/1233) | 92% (10232/11135) | 46% (5671/12368) | 22% (2759/12368) | 13% (1624/12368) | 41% (5073/12368) |
| all maps · r300+ | v1fix | 4130 | 90% (3714/4130) | 90% (266/297) | 90% (3448/3833) | 34% (1410/4130) | 20% (816/4130) | 5% (189/4130) | 61% (2531/4130) |
| all maps · r300+ | v1pre | 4926 | 86% (4255/4926) | 60% (198/331) | 88% (4057/4595) | 32% (1591/4926) | 16% (811/4926) | 8% (398/4926) | 60% (2937/4926) |
| all maps · our length >= 8 | v1fix | 758 | 75% (570/758) | 98% (396/406) | 49% (174/352) | 41% (308/758) | 23% (172/758) | 4% (33/758) | 55% (417/758) |
| all maps · our length >= 8 | v1pre | 706 | 64% (453/706) | 97% (239/246) | 47% (214/460) | 23% (164/706) | 11% (80/706) | 5% (32/706) | 72% (510/706) |
| swarm · all turns | v1fix | 12023 | 91% (10910/12023) | 61% (558/922) | 93% (10352/11101) | 37% (4392/12023) | 20% (2361/12023) | 9% (1057/12023) | 55% (6574/12023) |
| swarm · all turns | v1pre | 12368 | 86% (10686/12368) | 37% (454/1233) | 92% (10232/11135) | 46% (5671/12368) | 22% (2759/12368) | 13% (1624/12368) | 41% (5073/12368) |
| swarm · r300+ | v1fix | 4130 | 90% (3714/4130) | 90% (266/297) | 90% (3448/3833) | 34% (1410/4130) | 20% (816/4130) | 5% (189/4130) | 61% (2531/4130) |
| swarm · r300+ | v1pre | 4926 | 86% (4255/4926) | 60% (198/331) | 88% (4057/4595) | 32% (1591/4926) | 16% (811/4926) | 8% (398/4926) | 60% (2937/4926) |
| swarm · our length >= 8 | v1fix | 758 | 75% (570/758) | 98% (396/406) | 49% (174/352) | 41% (308/758) | 23% (172/758) | 4% (33/758) | 55% (417/758) |
| swarm · our length >= 8 | v1pre | 706 | 64% (453/706) | 97% (239/246) | 47% (214/460) | 23% (164/706) | 11% (80/706) | 5% (32/706) | 72% (510/706) |

## 4. Tags per game (our indicator labels), paired games

| family | bot | cl | conv | escape-split | feed | frag | grab | no-exit | no-exit s | sc | scx | sd | sf | sk | sq | sr | src | srn | srx | sx | sxc | sxx | tg | tgx |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| swarm | v1fix | 927.3 | 15.0 | 24.7 | 19.3 | 0.0 | 286.8 | 41.2 | 4.7 | 46.0 | 32.7 | 4314.8 | 19.3 | 772.2 | 3.0 | 48.8 | 26.3 | 369.5 | 12.0 | 25.3 | 33.2 | 5.8 | 452.8 | 351.2 |
| swarm | v1pre | 1499.0 | 50.8 | 48.2 | 53.7 | 2.0 | 537.7 | 75.7 | 7.7 | 78.7 | 66.0 | 8066.7 | 50.8 | 599.8 | 9.7 | 93.5 | 90.8 | 77.0 | 29.3 | 22.8 | 40.0 | 5.0 | 401.8 | 311.0 |

sf recipients (v1fix, swarm maps): 116 feeds; recipient length 3-4: 6% (7/116), 5-7: 12% (14/116), 8-15: 59% (68/116), 16+: 23% (27/116).

## 5. Per map (paired): wins, r100 heads, natural intake, final longest, eliminated

| map | v1fix W · u100 · nat · longest · elim | v1pre W · u100 · nat · longest · elim |
|---|---|---|
| default | 1/2 · 14.0 · 169.5 · 15.5 · 0 | 0/2 · 10.5 · 122.5 · 8.5 · 0 |
| schooltime | 0/2 · 22.5 · 464.0 · 22.5 · 0 | 2/2 · 21.0 · 772.5 · 50.0 · 0 |
| slithery_fight | 0/2 · 35.5 · 197.5 · 23.0 · 0 | 0/2 · 32.0 · 176.0 · 23.5 · 0 |
