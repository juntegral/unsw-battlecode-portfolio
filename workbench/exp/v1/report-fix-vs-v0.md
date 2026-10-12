# v1 local report: v1fix (exp/v1/v1fix-a-px4) vs v0t (exp/v1/v0t-a-px4)

Paired games (same key): 6. v1fix games 6, v0t games 60. Opponents: proxy4 (local mimics; sanity only, not a filter).

## 1. Five diagnostic indicators (EVAL.md §2) and outcome, paired games

| cell | bot | games | wins | r100 heads us / opp | r250 heads | natural intake us / opp (ratio) | line sac. pearls r300-499 (full games) | final longest us / opp | eliminated |
|---|---|---:|---:|---|---:|---|---|---|---|
| all maps | v1fix | 6 | 1 | 24.0 / 40.5 | 26.0 | 277.0 / 871.0 (32%) | 2.8 (6) | 20.3 / 34.0 | 0% (0/6) |
| all maps | v0t | 6 | 3 | 17.8 / 40.2 | 17.0 | 160.2 / 938.2 (17%) | 4.2 (6) | 28.3 / 33.2 | 0% (0/6) |
| swarm | v1fix | 6 | 1 | 24.0 / 40.5 | 26.0 | 277.0 / 871.0 (32%) | 2.8 (6) | 20.3 / 34.0 | 0% (0/6) |
| swarm | v0t | 6 | 3 | 17.8 / 40.2 | 17.0 | 160.2 / 938.2 (17%) | 4.2 (6) | 28.3 / 33.2 | 0% (0/6) |
| swarm · r500 | v1fix | 4 | 0 | 29.0 / 53.3 | 33.0 | 330.8 / 1201.0 (28%) | 4.3 (4) | 22.8 / 39.3 | 0% (0/4) |
| swarm · r500 | v0t | 4 | 2 | 17.3 / 53.8 | 16.0 | 154.0 / 1299.8 (12%) | 4.0 (4) | 32.3 / 38.5 | 0% (0/4) |
| swarm · elim | v1fix | 2 | 1 | 14.0 / 15.0 | 12.0 | 169.5 / 211.0 (80%) | 0.0 (2) | 15.5 / 23.5 | 0% (0/2) |
| swarm · elim | v0t | 2 | 1 | 19.0 / 13.0 | 19.0 | 172.5 / 215.0 (80%) | 4.5 (2) | 20.5 / 22.5 | 0% (0/2) |

## 2. Safety side effects (our deaths per game by cause, mass ledger; team longest >= 8 lost to an enemy head from r340)

| cell | bot | trapped | rammed (by enemy) | ram (we moved into a head) | ally head-on | sacrifice | longest lost from r340 |
|---|---|---:|---:|---:|---:|---:|---|
| all maps | v1fix | 41.8 | 21.0 | 7.7 | 3.3 | 19.8 | 50% (3/6) |
| all maps | v0t | 19.7 | 13.7 | 6.0 | 5.0 | 7.7 | 0% (0/6) |
| swarm | v1fix | 41.8 | 21.0 | 7.7 | 3.3 | 19.8 | 50% (3/6) |
| swarm | v0t | 19.7 | 13.7 | 6.0 | 5.0 | 7.7 | 0% (0/6) |
| swarm · r500 | v1fix | 49.8 | 24.0 | 9.0 | 2.0 | 27.0 | 50% (2/4) |
| swarm · r500 | v0t | 14.8 | 12.8 | 6.0 | 1.0 | 9.3 | 0% (0/4) |
| swarm · elim | v1fix | 26.0 | 15.0 | 5.0 | 6.0 | 5.5 | 50% (1/2) |
| swarm · elim | v0t | 29.5 | 15.5 | 6.0 | 13.0 | 4.5 | 0% (0/2) |

## 2b. The chain, link by link (paired games; per game means)

Heads r50 / r100 -> natural intake -> pieces born r100-430 (children <= 3 long; all births) -> our sacrifices (all; from r300) -> their drops from r300 -> line sacrifice pearls r300-499 (full games) and line share of those drops -> final longest.

| cell | bot | heads r50 · r100 | natural intake | pieces born r100-430 (births) | sacrifices (r300+) | sac. drops r300+ | line sac. pearls | line share | final longest | sf main · late feeds |
|---|---|---|---:|---|---|---:|---:|---:|---:|---|
| all maps | v1fix | 16.5 · 24.0 | 277.0 | 58.0 (68.2) | 19.8 (13.8) | 26.2 | 2.8 | 11% | 20.3 | 15.0 · 4.3 |
| all maps | v0t | 8.8 · 17.8 | 160.2 | 28.0 (30.3) | 7.7 (7.7) | 14.8 | 4.2 | 28% | 28.3 | 0.0 · 0.0 |
| swarm | v1fix | 16.5 · 24.0 | 277.0 | 58.0 (68.2) | 19.8 (13.8) | 26.2 | 2.8 | 11% | 20.3 | 15.0 · 4.3 |
| swarm | v0t | 8.8 · 17.8 | 160.2 | 28.0 (30.3) | 7.7 (7.7) | 14.8 | 4.2 | 28% | 28.3 | 0.0 · 0.0 |
| swarm · r500 | v1fix | 20.8 · 29.0 | 330.8 | 65.5 (78.8) | 27.0 (18.3) | 34.3 | 4.3 | 12% | 22.8 | 20.3 · 6.5 |
| swarm · r500 | v0t | 10.0 · 17.3 | 154.0 | 18.3 (20.8) | 9.3 (9.3) | 17.3 | 4.0 | 23% | 32.3 | 0.0 · 0.0 |
| swarm · elim | v1fix | 8.0 · 14.0 | 169.5 | 43.0 (47.0) | 5.5 (5.0) | 10.0 | 0.0 | 0% | 15.5 | 4.5 · 0.0 |
| swarm · elim | v0t | 6.5 · 19.0 | 172.5 | 47.5 (49.5) | 4.5 (4.5) | 10.0 | 4.5 | 45% | 20.5 | 0.0 · 0.0 |

## 2c. Target overlap (research transfer 1): target-labelled turns (v1 " sd", v0 " F") whose target another of our dragons also targets that round

| family | bot | target turns / game | same tile | within 3 |
|---|---|---:|---:|---:|
| swarm | v1fix | 4314.8 | 9.8% | 46.1% |
| swarm | v0t | 244.5 | 20.9% | 33.5% |

## 3. Belief accuracy (tag " bl<len>@x,y k<0|1>" every 5 rounds vs the true longest other living ally at that turn start)

| cell | bot | tagged turns | king verdict right | truly longest: says king | not longest: says not king | length within 1 | position within 3 | believes longer than true (+2) | believes shorter (-2) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all maps · all turns | v1fix | 12023 | 91% (10910/12023) | 61% (558/922) | 93% (10352/11101) | 37% (4392/12023) | 20% (2361/12023) | 9% (1057/12023) | 55% (6574/12023) |
| all maps · all turns | v0t | 7762 | 86% (6674/7762) | 30% (338/1135) | 96% (6336/6627) | 52% (4043/7762) | 21% (1666/7762) | 15% (1163/7762) | 33% (2556/7762) |
| all maps · r300+ | v1fix | 4130 | 90% (3714/4130) | 90% (266/297) | 90% (3448/3833) | 34% (1410/4130) | 20% (816/4130) | 5% (189/4130) | 61% (2531/4130) |
| all maps · r300+ | v0t | 2373 | 88% (2079/2373) | 66% (195/295) | 91% (1884/2078) | 44% (1051/2373) | 21% (490/2373) | 14% (334/2373) | 42% (988/2373) |
| all maps · our length >= 8 | v1fix | 758 | 75% (570/758) | 98% (396/406) | 49% (174/352) | 41% (308/758) | 23% (172/758) | 4% (33/758) | 55% (417/758) |
| all maps · our length >= 8 | v0t | 511 | 62% (315/511) | 68% (218/322) | 51% (97/189) | 17% (88/511) | 14% (69/511) | 46% (235/511) | 37% (188/511) |
| swarm · all turns | v1fix | 12023 | 91% (10910/12023) | 61% (558/922) | 93% (10352/11101) | 37% (4392/12023) | 20% (2361/12023) | 9% (1057/12023) | 55% (6574/12023) |
| swarm · all turns | v0t | 7762 | 86% (6674/7762) | 30% (338/1135) | 96% (6336/6627) | 52% (4043/7762) | 21% (1666/7762) | 15% (1163/7762) | 33% (2556/7762) |
| swarm · r300+ | v1fix | 4130 | 90% (3714/4130) | 90% (266/297) | 90% (3448/3833) | 34% (1410/4130) | 20% (816/4130) | 5% (189/4130) | 61% (2531/4130) |
| swarm · r300+ | v0t | 2373 | 88% (2079/2373) | 66% (195/295) | 91% (1884/2078) | 44% (1051/2373) | 21% (490/2373) | 14% (334/2373) | 42% (988/2373) |
| swarm · our length >= 8 | v1fix | 758 | 75% (570/758) | 98% (396/406) | 49% (174/352) | 41% (308/758) | 23% (172/758) | 4% (33/758) | 55% (417/758) |
| swarm · our length >= 8 | v0t | 511 | 62% (315/511) | 68% (218/322) | 51% (97/189) | 17% (88/511) | 14% (69/511) | 46% (235/511) | 37% (188/511) |

## 4. Tags per game (our indicator labels), paired games

| family | bot | cl | conv | csplit | escape-split | feed | floor | frag | gh | grab | kx | lsplit | no-exit | no-exit s | sc | scx | sd | sf | sk | sq | sr | src | srn | srx | sx | sxc | sxx | tg | tgx |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| swarm | v1fix | 927.3 | 15.0 | 0.0 | 24.7 | 19.3 | 0.0 | 0.0 | 0.0 | 286.8 | 0.0 | 0.0 | 41.2 | 4.7 | 46.0 | 32.7 | 4314.8 | 19.3 | 772.2 | 3.0 | 48.8 | 26.3 | 369.5 | 12.0 | 25.3 | 33.2 | 5.8 | 452.8 | 351.2 |
| swarm | v0t | 820.0 | 4.3 | 32.0 | 10.0 | 7.8 | 0.2 | 0.7 | 24.3 | 173.3 | 44.0 | 10.3 | 18.3 | 1.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 331.2 | 280.0 |

sf recipients (v1fix, swarm maps): 116 feeds; recipient length 3-4: 6% (7/116), 5-7: 12% (14/116), 8-15: 59% (68/116), 16+: 23% (27/116).

## 5. Per map (paired): wins, r100 heads, natural intake, final longest, eliminated

| map | v1fix W · u100 · nat · longest · elim | v0t W · u100 · nat · longest · elim |
|---|---|---|
| default | 1/2 · 14.0 · 169.5 · 15.5 · 0 | 1/2 · 19.0 · 172.5 · 20.5 · 0 |
| schooltime | 0/2 · 22.5 · 464.0 · 22.5 · 0 | 1/2 · 15.5 · 194.0 · 30.0 · 0 |
| slithery_fight | 0/2 · 35.5 · 197.5 · 23.0 · 0 | 1/2 · 19.0 · 114.0 · 34.5 · 0 |
