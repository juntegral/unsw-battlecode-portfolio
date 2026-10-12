# v1 local report: v1fix (exp/v1/v1fix-a-px4) vs v1final (exp/v1/v1final-a-px4)

Paired games (same key): 6. v1fix games 6, v1final games 20. Opponents: proxy4 (local mimics; sanity only, not a filter).

## 1. Five diagnostic indicators (EVAL.md §2) and outcome, paired games

| cell | bot | games | wins | r100 heads us / opp | r250 heads | natural intake us / opp (ratio) | line sac. pearls r300-499 (full games) | final longest us / opp | eliminated |
|---|---|---:|---:|---|---:|---|---|---|---|
| all maps | v1fix | 6 | 1 | 24.0 / 40.5 | 26.0 | 277.0 / 871.0 (32%) | 2.8 (6) | 20.3 / 34.0 | 0% (0/6) |
| all maps | v1final | 6 | 1 | 23.0 / 42.0 | 13.0 | 137.3 / 989.5 (14%) | 2.5 (6) | 24.7 / 41.3 | 0% (0/6) |
| swarm | v1fix | 6 | 1 | 24.0 / 40.5 | 26.0 | 277.0 / 871.0 (32%) | 2.8 (6) | 20.3 / 34.0 | 0% (0/6) |
| swarm | v1final | 6 | 1 | 23.0 / 42.0 | 13.0 | 137.3 / 989.5 (14%) | 2.5 (6) | 24.7 / 41.3 | 0% (0/6) |
| swarm · r500 | v1fix | 4 | 0 | 29.0 / 53.3 | 33.0 | 330.8 / 1201.0 (28%) | 4.3 (4) | 22.8 / 39.3 | 0% (0/4) |
| swarm · r500 | v1final | 4 | 1 | 26.5 / 56.0 | 16.3 | 165.5 / 1351.3 (12%) | 3.8 (4) | 28.0 / 45.5 | 0% (0/4) |
| swarm · elim | v1fix | 2 | 1 | 14.0 / 15.0 | 12.0 | 169.5 / 211.0 (80%) | 0.0 (2) | 15.5 / 23.5 | 0% (0/2) |
| swarm · elim | v1final | 2 | 0 | 16.0 / 14.0 | 6.5 | 81.0 / 266.0 (30%) | 0.0 (2) | 18.0 / 33.0 | 0% (0/2) |

## 2. Safety side effects (our deaths per game by cause, mass ledger; team longest >= 8 lost to an enemy head from r340)

| cell | bot | trapped | rammed (by enemy) | ram (we moved into a head) | ally head-on | sacrifice | longest lost from r340 |
|---|---|---:|---:|---:|---:|---:|---|
| all maps | v1fix | 41.8 | 21.0 | 7.7 | 3.3 | 19.8 | 50% (3/6) |
| all maps | v1final | 20.8 | 11.7 | 3.8 | 2.0 | 9.5 | 17% (1/6) |
| swarm | v1fix | 41.8 | 21.0 | 7.7 | 3.3 | 19.8 | 50% (3/6) |
| swarm | v1final | 20.8 | 11.7 | 3.8 | 2.0 | 9.5 | 17% (1/6) |
| swarm · r500 | v1fix | 49.8 | 24.0 | 9.0 | 2.0 | 27.0 | 50% (2/4) |
| swarm · r500 | v1final | 25.8 | 11.5 | 3.5 | 1.5 | 14.3 | 0% (0/4) |
| swarm · elim | v1fix | 26.0 | 15.0 | 5.0 | 6.0 | 5.5 | 50% (1/2) |
| swarm · elim | v1final | 11.0 | 12.0 | 4.5 | 3.0 | 0.0 | 50% (1/2) |

## 2b. The chain, link by link (paired games; per game means)

Heads r50 / r100 -> natural intake -> pieces born r100-430 (children <= 3 long; all births) -> our sacrifices (all; from r300) -> their drops from r300 -> line sacrifice pearls r300-499 (full games) and line share of those drops -> final longest.

| cell | bot | heads r50 · r100 | natural intake | pieces born r100-430 (births) | sacrifices (r300+) | sac. drops r300+ | line sac. pearls | line share | final longest | sf main · late feeds |
|---|---|---|---:|---|---|---:|---:|---:|---:|---|
| all maps | v1fix | 16.5 · 24.0 | 277.0 | 58.0 (68.2) | 19.8 (13.8) | 26.2 | 2.8 | 11% | 20.3 | 15.0 · 4.3 |
| all maps | v1final | 15.8 · 23.0 | 137.3 | 12.2 (18.0) | 9.5 (5.5) | 11.2 | 2.5 | 22% | 24.7 | 9.0 · 0.5 |
| swarm | v1fix | 16.5 · 24.0 | 277.0 | 58.0 (68.2) | 19.8 (13.8) | 26.2 | 2.8 | 11% | 20.3 | 15.0 · 4.3 |
| swarm | v1final | 15.8 · 23.0 | 137.3 | 12.2 (18.0) | 9.5 (5.5) | 11.2 | 2.5 | 22% | 24.7 | 9.0 · 0.5 |
| swarm · r500 | v1fix | 20.8 · 29.0 | 330.8 | 65.5 (78.8) | 27.0 (18.3) | 34.3 | 4.3 | 12% | 22.8 | 20.3 · 6.5 |
| swarm · r500 | v1final | 20.0 · 26.5 | 165.5 | 13.5 (20.8) | 14.3 (8.3) | 16.8 | 3.8 | 22% | 28.0 | 13.5 · 0.8 |
| swarm · elim | v1fix | 8.0 · 14.0 | 169.5 | 43.0 (47.0) | 5.5 (5.0) | 10.0 | 0.0 | 0% | 15.5 | 4.5 · 0.0 |
| swarm · elim | v1final | 7.5 · 16.0 | 81.0 | 9.5 (12.5) | 0.0 (0.0) | 0.0 | 0.0 | – | 18.0 | 0.0 · 0.0 |

## 2c. Target overlap (research transfer 1): target-labelled turns (v1 " sd", v0 " F") whose target another of our dragons also targets that round

| family | bot | target turns / game | same tile | within 3 |
|---|---|---:|---:|---:|
| swarm | v1fix | 4314.8 | 9.8% | 46.1% |
| swarm | v1final | 525.8 | 18.4% | 49.7% |

## 3. Belief accuracy (tag " bl<len>@x,y k<0|1>" every 5 rounds vs the true longest other living ally at that turn start)

| cell | bot | tagged turns | king verdict right | truly longest: says king | not longest: says not king | length within 1 | position within 3 | believes longer than true (+2) | believes shorter (-2) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all maps · all turns | v1fix | 12023 | 91% (10910/12023) | 61% (558/922) | 93% (10352/11101) | 37% (4392/12023) | 20% (2361/12023) | 9% (1057/12023) | 55% (6574/12023) |
| all maps · all turns | v1final | 6828 | 87% (5946/6828) | 59% (600/1017) | 92% (5346/5811) | 53% (3587/6828) | 32% (2204/6808) | 12% (839/6828) | 35% (2402/6828) |
| all maps · r300+ | v1fix | 4130 | 90% (3714/4130) | 90% (266/297) | 90% (3448/3833) | 34% (1410/4130) | 20% (816/4130) | 5% (189/4130) | 61% (2531/4130) |
| all maps · r300+ | v1final | 1220 | 85% (1042/1220) | 90% (242/269) | 84% (800/951) | 53% (642/1220) | 30% (361/1200) | 3% (35/1220) | 45% (543/1220) |
| all maps · our length >= 8 | v1fix | 758 | 75% (570/758) | 98% (396/406) | 49% (174/352) | 41% (308/758) | 23% (172/758) | 4% (33/758) | 55% (417/758) |
| all maps · our length >= 8 | v1final | 421 | 88% (369/421) | 99% (270/273) | 67% (99/148) | 64% (269/421) | 40% (167/421) | 6% (25/421) | 30% (127/421) |
| swarm · all turns | v1fix | 12023 | 91% (10910/12023) | 61% (558/922) | 93% (10352/11101) | 37% (4392/12023) | 20% (2361/12023) | 9% (1057/12023) | 55% (6574/12023) |
| swarm · all turns | v1final | 6828 | 87% (5946/6828) | 59% (600/1017) | 92% (5346/5811) | 53% (3587/6828) | 32% (2204/6808) | 12% (839/6828) | 35% (2402/6828) |
| swarm · r300+ | v1fix | 4130 | 90% (3714/4130) | 90% (266/297) | 90% (3448/3833) | 34% (1410/4130) | 20% (816/4130) | 5% (189/4130) | 61% (2531/4130) |
| swarm · r300+ | v1final | 1220 | 85% (1042/1220) | 90% (242/269) | 84% (800/951) | 53% (642/1220) | 30% (361/1200) | 3% (35/1220) | 45% (543/1220) |
| swarm · our length >= 8 | v1fix | 758 | 75% (570/758) | 98% (396/406) | 49% (174/352) | 41% (308/758) | 23% (172/758) | 4% (33/758) | 55% (417/758) |
| swarm · our length >= 8 | v1final | 421 | 88% (369/421) | 99% (270/273) | 67% (99/148) | 64% (269/421) | 40% (167/421) | 6% (25/421) | 30% (127/421) |

## 4. Tags per game (our indicator labels), paired games

| family | bot | cl | conv | escape-split | feed | grab | no-exit | no-exit s | sc | scx | sd | sf | sk | sq | sr | src | srn | srx | sx | sxc | sxx | tg | tgx |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| swarm | v1fix | 927.3 | 15.0 | 24.7 | 19.3 | 286.8 | 41.2 | 4.7 | 46.0 | 32.7 | 4314.8 | 19.3 | 772.2 | 3.0 | 48.8 | 26.3 | 369.5 | 12.0 | 25.3 | 33.2 | 5.8 | 452.8 | 351.2 |
| swarm | v1final | 475.3 | 9.0 | 15.2 | 9.5 | 163.3 | 20.2 | 1.3 | 25.2 | 22.8 | 525.8 | 9.5 | 461.2 | 2.8 | 8.0 | 5.8 | 497.8 | 0.8 | 23.3 | 26.5 | 4.7 | 261.8 | 172.8 |

sf recipients (v1fix, swarm maps): 116 feeds; recipient length 3-4: 6% (7/116), 5-7: 12% (14/116), 8-15: 59% (68/116), 16+: 23% (27/116).

## 5. Per map (paired): wins, r100 heads, natural intake, final longest, eliminated

| map | v1fix W · u100 · nat · longest · elim | v1final W · u100 · nat · longest · elim |
|---|---|---|
| default | 1/2 · 14.0 · 169.5 · 15.5 · 0 | 0/2 · 16.0 · 81.0 · 18.0 · 0 |
| schooltime | 0/2 · 22.5 · 464.0 · 22.5 · 0 | 0/2 · 15.5 · 141.0 · 21.0 · 0 |
| slithery_fight | 0/2 · 35.5 · 197.5 · 23.0 · 0 | 1/2 · 37.5 · 190.0 · 35.0 · 0 |
