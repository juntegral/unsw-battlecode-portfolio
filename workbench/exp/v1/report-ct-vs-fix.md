# v1 local report: v1ct (exp/v1/v1ct-a-px4) vs v1fix (exp/v1/v1fix-a-px4)

Paired games (same key): 6. v1ct games 6, v1fix games 6. Opponents: proxy4 (local mimics; sanity only, not a filter).

## 1. Five diagnostic indicators (EVAL.md §2) and outcome, paired games

| cell | bot | games | wins | r100 heads us / opp | r250 heads | natural intake us / opp (ratio) | line sac. pearls r300-499 (full games) | final longest us / opp | eliminated |
|---|---|---:|---:|---|---:|---|---|---|---|
| all maps | v1ct | 6 | 1 | 23.3 / 38.5 | 27.5 | 332.7 / 806.3 (41%) | 6.3 (6) | 27.0 / 40.2 | 0% (0/6) |
| all maps | v1fix | 6 | 1 | 24.0 / 40.5 | 26.0 | 277.0 / 871.0 (32%) | 2.8 (6) | 20.3 / 34.0 | 0% (0/6) |
| swarm | v1ct | 6 | 1 | 23.3 / 38.5 | 27.5 | 332.7 / 806.3 (41%) | 6.3 (6) | 27.0 / 40.2 | 0% (0/6) |
| swarm | v1fix | 6 | 1 | 24.0 / 40.5 | 26.0 | 277.0 / 871.0 (32%) | 2.8 (6) | 20.3 / 34.0 | 0% (0/6) |
| swarm · r500 | v1ct | 4 | 1 | 29.0 / 50.5 | 35.3 | 427.0 / 1092.3 (39%) | 7.8 (4) | 33.3 / 43.8 | 0% (0/4) |
| swarm · r500 | v1fix | 4 | 0 | 29.0 / 53.3 | 33.0 | 330.8 / 1201.0 (28%) | 4.3 (4) | 22.8 / 39.3 | 0% (0/4) |
| swarm · elim | v1ct | 2 | 0 | 12.0 / 14.5 | 12.0 | 144.0 / 234.5 (61%) | 3.5 (2) | 14.5 / 33.0 | 0% (0/2) |
| swarm · elim | v1fix | 2 | 1 | 14.0 / 15.0 | 12.0 | 169.5 / 211.0 (80%) | 0.0 (2) | 15.5 / 23.5 | 0% (0/2) |

## 2. Safety side effects (our deaths per game by cause, mass ledger; team longest >= 8 lost to an enemy head from r340)

| cell | bot | trapped | rammed (by enemy) | ram (we moved into a head) | ally head-on | sacrifice | longest lost from r340 |
|---|---|---:|---:|---:|---:|---:|---|
| all maps | v1ct | 43.5 | 23.8 | 8.7 | 4.3 | 25.2 | 33% (2/6) |
| all maps | v1fix | 41.8 | 21.0 | 7.7 | 3.3 | 19.8 | 50% (3/6) |
| swarm | v1ct | 43.5 | 23.8 | 8.7 | 4.3 | 25.2 | 33% (2/6) |
| swarm | v1fix | 41.8 | 21.0 | 7.7 | 3.3 | 19.8 | 50% (3/6) |
| swarm · r500 | v1ct | 56.8 | 28.0 | 8.5 | 3.0 | 35.5 | 25% (1/4) |
| swarm · r500 | v1fix | 49.8 | 24.0 | 9.0 | 2.0 | 27.0 | 50% (2/4) |
| swarm · elim | v1ct | 17.0 | 15.5 | 9.0 | 7.0 | 4.5 | 50% (1/2) |
| swarm · elim | v1fix | 26.0 | 15.0 | 5.0 | 6.0 | 5.5 | 50% (1/2) |

## 2b. The chain, link by link (paired games; per game means)

Heads r50 / r100 -> natural intake -> pieces born r100-430 (children <= 3 long; all births) -> our sacrifices (all; from r300) -> their drops from r300 -> line sacrifice pearls r300-499 (full games) and line share of those drops -> final longest.

| cell | bot | heads r50 · r100 | natural intake | pieces born r100-430 (births) | sacrifices (r300+) | sac. drops r300+ | line sac. pearls | line share | final longest | sf main · late feeds |
|---|---|---|---:|---|---|---:|---:|---:|---:|---|
| all maps | v1ct | 16.3 · 23.3 | 332.7 | 64.7 (73.8) | 25.2 (19.7) | 38.3 | 6.3 | 17% | 27.0 | 20.3 · 5.3 |
| all maps | v1fix | 16.5 · 24.0 | 277.0 | 58.0 (68.2) | 19.8 (13.8) | 26.2 | 2.8 | 11% | 20.3 | 15.0 · 4.3 |
| swarm | v1ct | 16.3 · 23.3 | 332.7 | 64.7 (73.8) | 25.2 (19.7) | 38.3 | 6.3 | 17% | 27.0 | 20.3 · 5.3 |
| swarm | v1fix | 16.5 · 24.0 | 277.0 | 58.0 (68.2) | 19.8 (13.8) | 26.2 | 2.8 | 11% | 20.3 | 15.0 · 4.3 |
| swarm · r500 | v1ct | 21.0 · 29.0 | 427.0 | 77.5 (90.3) | 35.5 (27.3) | 53.0 | 7.8 | 15% | 33.3 | 29.0 · 7.3 |
| swarm · r500 | v1fix | 20.8 · 29.0 | 330.8 | 65.5 (78.8) | 27.0 (18.3) | 34.3 | 4.3 | 12% | 22.8 | 20.3 · 6.5 |
| swarm · elim | v1ct | 7.0 · 12.0 | 144.0 | 39.0 (41.0) | 4.5 (4.5) | 9.0 | 3.5 | 39% | 14.5 | 3.0 · 1.5 |
| swarm · elim | v1fix | 8.0 · 14.0 | 169.5 | 43.0 (47.0) | 5.5 (5.0) | 10.0 | 0.0 | 0% | 15.5 | 4.5 · 0.0 |

## 2c. Target overlap (research transfer 1): target-labelled turns (v1 " sd", v0 " F") whose target another of our dragons also targets that round

| family | bot | target turns / game | same tile | within 3 |
|---|---|---:|---:|---:|
| swarm | v1ct | 4391.2 | 12.4% | 48.1% |
| swarm | v1fix | 4314.8 | 9.8% | 46.1% |

## 3. Belief accuracy (tag " bl<len>@x,y k<0|1>" every 5 rounds vs the true longest other living ally at that turn start)

| cell | bot | tagged turns | king verdict right | truly longest: says king | not longest: says not king | length within 1 | position within 3 | believes longer than true (+2) | believes shorter (-2) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all maps · all turns | v1ct | 12803 | 90% (11538/12803) | 59% (508/867) | 92% (11030/11936) | 36% (4629/12803) | 19% (2473/12803) | 9% (1134/12803) | 55% (7040/12803) |
| all maps · all turns | v1fix | 12023 | 91% (10910/12023) | 61% (558/922) | 93% (10352/11101) | 37% (4392/12023) | 20% (2361/12023) | 9% (1057/12023) | 55% (6574/12023) |
| all maps · r300+ | v1ct | 4740 | 89% (4218/4740) | 84% (220/261) | 89% (3998/4479) | 31% (1474/4740) | 19% (882/4740) | 5% (241/4740) | 64% (3025/4740) |
| all maps · r300+ | v1fix | 4130 | 90% (3714/4130) | 90% (266/297) | 90% (3448/3833) | 34% (1410/4130) | 20% (816/4130) | 5% (189/4130) | 61% (2531/4130) |
| all maps · our length >= 8 | v1ct | 827 | 68% (564/827) | 96% (356/370) | 46% (208/457) | 35% (293/827) | 19% (157/827) | 3% (24/827) | 62% (510/827) |
| all maps · our length >= 8 | v1fix | 758 | 75% (570/758) | 98% (396/406) | 49% (174/352) | 41% (308/758) | 23% (172/758) | 4% (33/758) | 55% (417/758) |
| swarm · all turns | v1ct | 12803 | 90% (11538/12803) | 59% (508/867) | 92% (11030/11936) | 36% (4629/12803) | 19% (2473/12803) | 9% (1134/12803) | 55% (7040/12803) |
| swarm · all turns | v1fix | 12023 | 91% (10910/12023) | 61% (558/922) | 93% (10352/11101) | 37% (4392/12023) | 20% (2361/12023) | 9% (1057/12023) | 55% (6574/12023) |
| swarm · r300+ | v1ct | 4740 | 89% (4218/4740) | 84% (220/261) | 89% (3998/4479) | 31% (1474/4740) | 19% (882/4740) | 5% (241/4740) | 64% (3025/4740) |
| swarm · r300+ | v1fix | 4130 | 90% (3714/4130) | 90% (266/297) | 90% (3448/3833) | 34% (1410/4130) | 20% (816/4130) | 5% (189/4130) | 61% (2531/4130) |
| swarm · our length >= 8 | v1ct | 827 | 68% (564/827) | 96% (356/370) | 46% (208/457) | 35% (293/827) | 19% (157/827) | 3% (24/827) | 62% (510/827) |
| swarm · our length >= 8 | v1fix | 758 | 75% (570/758) | 98% (396/406) | 49% (174/352) | 41% (308/758) | 23% (172/758) | 4% (33/758) | 55% (417/758) |

## 4. Tags per game (our indicator labels), paired games

| family | bot | cl | conv | escape-split | feed | grab | no-exit | no-exit s | sc | scx | sd | sf | sk | sq | sr | src | srn | srx | sx | sxc | sxx | tg | tgx |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| swarm | v1ct | 1082.0 | 20.3 | 31.0 | 25.7 | 355.3 | 42.0 | 3.3 | 60.7 | 51.0 | 4391.2 | 25.7 | 805.3 | 6.7 | 56.0 | 29.5 | 362.7 | 15.8 | 24.7 | 43.0 | 7.3 | 417.8 | 310.3 |
| swarm | v1fix | 927.3 | 15.0 | 24.7 | 19.3 | 286.8 | 41.2 | 4.7 | 46.0 | 32.7 | 4314.8 | 19.3 | 772.2 | 3.0 | 48.8 | 26.3 | 369.5 | 12.0 | 25.3 | 33.2 | 5.8 | 452.8 | 351.2 |

sf recipients (v1ct, swarm maps): 154 feeds; recipient length 3-4: 7% (11/154), 5-7: 7% (11/154), 8-15: 53% (82/154), 16+: 32% (50/154).

## 5. Per map (paired): wins, r100 heads, natural intake, final longest, eliminated

| map | v1ct W · u100 · nat · longest · elim | v1fix W · u100 · nat · longest · elim |
|---|---|---|
| default | 0/2 · 12.0 · 144.0 · 14.5 · 0 | 1/2 · 14.0 · 169.5 · 15.5 · 0 |
| schooltime | 1/2 · 23.0 · 606.0 · 39.5 · 0 | 0/2 · 22.5 · 464.0 · 22.5 · 0 |
| slithery_fight | 0/2 · 35.0 · 248.0 · 27.0 · 0 | 0/2 · 35.5 · 197.5 · 23.0 · 0 |
