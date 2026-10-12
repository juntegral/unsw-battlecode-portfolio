# v1 local report: v1 online (w1+w2) (exp/online-eval/v1-w12) vs stack11 online (bench 1-3) (exp/online-eval/bench-s11)

Paired games (same key): 140. v1 online (w1+w2) games 140, stack11 online (bench 1-3) games 210. Opponents: proxy4 (local mimics; sanity only, not a filter).

## 1. Five diagnostic indicators (EVAL.md §2) and outcome, paired games

| cell | bot | games | wins | r100 heads us / opp | r250 heads | natural intake us / opp (ratio) | line sac. pearls r300-499 (full games) | final longest us / opp | eliminated |
|---|---|---:|---:|---|---:|---|---|---|---|
| all maps | v1 online (w1+w2) | 140 | 28 | 11.7 / 30.7 | 10.1 | 169.4 / 512.0 (33%) | 8.8 (89) | 18.7 / 30.1 | 36% (51/140) |
| all maps | stack11 online (bench 1-3) | 140 | 17 | 9.5 / 31.1 | 9.9 | 152.4 / 492.1 (31%) | 8.1 (84) | 13.5 / 28.2 | 40% (56/140) |
| fortress | v1 online (w1+w2) | 42 | 20 | 6.6 / 24.2 | 7.8 | 271.9 / 383.9 (71%) | 13.4 (39) | 39.0 / 41.5 | 7% (3/42) |
| fortress | stack11 online (bench 1-3) | 42 | 16 | 8.6 / 23.2 | 13.3 | 291.8 / 394.3 (74%) | 12.5 (40) | 28.5 / 37.9 | 5% (2/42) |
| swarm | v1 online (w1+w2) | 98 | 8 | 13.9 / 33.5 | 11.1 | 125.4 / 566.9 (22%) | 5.3 (50) | 9.9 / 25.1 | 49% (48/98) |
| swarm | stack11 online (bench 1-3) | 98 | 1 | 9.9 / 34.4 | 8.5 | 92.7 / 534.1 (17%) | 4.2 (44) | 7.1 / 24.0 | 55% (54/98) |
| swarm · r500 | v1 online (w1+w2) | 42 | 7 | 21.2 / 39.0 | 22.5 | 232.5 / 936.5 (25%) | 6.8 (37) | 20.0 / 43.4 | 12% (5/42) |
| swarm · r500 | stack11 online (bench 1-3) | 42 | 1 | 13.7 / 38.2 | 17.5 | 173.0 / 861.2 (20%) | 5.5 (32) | 14.1 / 40.6 | 24% (10/42) |
| swarm · elim | v1 online (w1+w2) | 56 | 1 | 8.4 / 29.4 | 2.6 | 45.0 / 289.7 (16%) | 1.0 (13) | 2.4 / 11.5 | 77% (43/56) |
| swarm · elim | stack11 online (bench 1-3) | 56 | 0 | 7.0 / 31.6 | 1.7 | 32.4 / 288.7 (11%) | 0.8 (12) | 1.8 / 11.5 | 79% (44/56) |
| fortress · r500 | v1 online (w1+w2) | 28 | 16 | 8.0 / 29.0 | 8.9 | 289.5 / 463.0 (63%) | 16.5 (28) | 49.5 / 46.6 | 0% (0/28) |
| fortress · r500 | stack11 online (bench 1-3) | 28 | 12 | 11.0 / 27.0 | 15.4 | 315.8 / 474.5 (67%) | 15.1 (28) | 34.5 / 41.2 | 0% (0/28) |
| fortress · elim (PD) | v1 online (w1+w2) | 14 | 4 | 3.8 / 14.4 | 5.7 | 236.9 / 225.8 (105%) | 5.5 (11) | 18.1 / 31.4 | 21% (3/14) |
| fortress · elim (PD) | stack11 online (bench 1-3) | 14 | 4 | 3.6 / 15.6 | 9.1 | 243.9 / 233.7 (104%) | 6.3 (12) | 16.4 / 31.2 | 14% (2/14) |

## 2. Safety side effects (our deaths per game by cause, mass ledger; team longest >= 8 lost to an enemy head from r340)

| cell | bot | trapped | rammed (by enemy) | ram (we moved into a head) | ally head-on | sacrifice | longest lost from r340 |
|---|---|---:|---:|---:|---:|---:|---|
| all maps | v1 online (w1+w2) | 76.1 | 10.8 | 2.5 | 1.1 | 8.9 | 11% (11/96) |
| all maps | stack11 online (bench 1-3) | 77.4 | 9.2 | 1.8 | 1.5 | 6.7 | 18% (17/94) |
| fortress | v1 online (w1+w2) | 186.1 | 1.4 | 0.1 | 2.0 | 9.9 | 5% (2/42) |
| fortress | stack11 online (bench 1-3) | 202.0 | 1.8 | 0.0 | 3.6 | 12.6 | 5% (2/42) |
| swarm | v1 online (w1+w2) | 29.0 | 14.8 | 3.5 | 0.8 | 8.5 | 17% (9/54) |
| swarm | stack11 online (bench 1-3) | 24.0 | 12.3 | 2.6 | 0.6 | 4.1 | 29% (15/52) |
| swarm · r500 | v1 online (w1+w2) | 57.8 | 18.2 | 5.7 | 1.3 | 19.2 | 24% (9/37) |
| swarm · r500 | stack11 online (bench 1-3) | 48.1 | 15.3 | 4.5 | 1.0 | 9.4 | 36% (13/36) |
| swarm · elim | v1 online (w1+w2) | 7.4 | 12.3 | 1.8 | 0.3 | 0.4 | 0% (0/17) |
| swarm · elim | stack11 online (bench 1-3) | 5.9 | 10.0 | 1.2 | 0.3 | 0.1 | 13% (2/16) |

## 2b. The chain, link by link (paired games; per game means)

Heads r50 / r100 -> natural intake -> pieces born r100-430 (children <= 3 long; all births) -> our sacrifices (all; from r300) -> their drops from r300 -> line sacrifice pearls r300-499 (full games) and line share of those drops -> final longest.

| cell | bot | heads r50 · r100 | natural intake | pieces born r100-430 (births) | sacrifices (r300+) | sac. drops r300+ | line sac. pearls | line share | final longest | sf main · late feeds |
|---|---|---|---:|---|---|---:|---:|---:|---:|---|
| all maps | v1 online (w1+w2) | 9.1 · 11.7 | 169.4 | 23.9 (67.1) | 8.9 (7.4) | 16.6 | 8.8 | 34% | 18.7 | 4.8 · 1.1 |
| all maps | stack11 online (bench 1-3) | 7.1 · 9.5 | 152.4 | 22.5 (66.1) | 6.7 (6.6) | 14.2 | 8.1 | 35% | 13.5 | 0.0 · 0.0 |
| fortress | v1 online (w1+w2) | 6.2 · 6.6 | 271.9 | 12.9 (139.3) | 9.9 (9.8) | 27.7 | 13.4 | 46% | 39.0 | 0.0 · 0.0 |
| fortress | stack11 online (bench 1-3) | 6.1 · 8.6 | 291.8 | 21.7 (154.6) | 12.6 (12.5) | 28.0 | 12.5 | 44% | 28.5 | 0.0 · 0.0 |
| swarm | v1 online (w1+w2) | 10.3 · 13.9 | 125.4 | 28.6 (36.2) | 8.5 (6.3) | 11.8 | 5.3 | 23% | 9.9 | 6.9 · 1.6 |
| swarm | stack11 online (bench 1-3) | 7.5 · 9.9 | 92.7 | 22.8 (28.2) | 4.1 (4.1) | 8.4 | 4.2 | 23% | 7.1 | 0.0 · 0.0 |
| swarm · r500 | v1 online (w1+w2) | 14.4 · 21.2 | 232.5 | 55.7 (72.5) | 19.2 (14.3) | 26.7 | 6.8 | 22% | 20.0 | 16.0 · 3.3 |
| swarm · r500 | stack11 online (bench 1-3) | 8.5 · 13.7 | 173.0 | 46.6 (59.0) | 9.4 (9.4) | 19.2 | 5.5 | 22% | 14.1 | 0.0 · 0.0 |
| swarm · elim | v1 online (w1+w2) | 7.2 · 8.4 | 45.0 | 8.4 (8.9) | 0.4 (0.4) | 0.6 | 1.0 | 42% | 2.4 | 0.1 · 0.3 |
| swarm · elim | stack11 online (bench 1-3) | 6.7 · 7.0 | 32.4 | 4.9 (5.1) | 0.1 (0.1) | 0.2 | 0.8 | 82% | 1.8 | 0.0 · 0.0 |

## 2c. Target overlap (research transfer 1): target-labelled turns (v1 " sd", v0 " F") whose target another of our dragons also targets that round

| family | bot | target turns / game | same tile | within 3 |
|---|---|---:|---:|---:|
| fortress | v1 online (w1+w2) | 317.3 | 9.9% | 21.2% |
| fortress | stack11 online (bench 1-3) | 343.6 | 9.9% | 19.3% |
| swarm | v1 online (w1+w2) | 2152.8 | 11.7% | 48.3% |
| swarm | stack11 online (bench 1-3) | 121.6 | 13.8% | 27.4% |

## 3. Belief accuracy (tag " bl<len>@x,y k<0|1>" every 5 rounds vs the true longest other living ally at that turn start)

| cell | bot | tagged turns | king verdict right | truly longest: says king | not longest: says not king | length within 1 | position within 3 | believes longer than true (+2) | believes shorter (-2) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all maps · all turns | v1 online (w1+w2) | 114951 | 84% (96915/114951) | 61% (10791/17760) | 89% (86124/97191) | 46% (52620/114951) | 27% (31304/114580) | 9% (10079/114951) | 45% (52252/114951) |
| all maps · r300+ | v1 online (w1+w2) | 33229 | 86% (28623/33229) | 75% (3848/5120) | 88% (24775/28109) | 40% (13303/33229) | 26% (8608/33023) | 6% (1965/33229) | 54% (17961/33229) |
| all maps · our length >= 8 | v1 online (w1+w2) | 12790 | 69% (8785/12790) | 99% (5544/5626) | 45% (3241/7164) | 31% (3974/12790) | 23% (2952/12756) | 4% (518/12790) | 65% (8298/12790) |
| fortress · all turns | v1 online (w1+w2) | 23752 | 78% (18558/23752) | 92% (4163/4543) | 75% (14395/19209) | 24% (5808/23752) | 24% (5782/23721) | 4% (836/23752) | 72% (17108/23752) |
| fortress · r300+ | v1 online (w1+w2) | 7524 | 86% (6497/7524) | 91% (1633/1793) | 85% (4864/5731) | 37% (2783/7524) | 35% (2604/7493) | 7% (520/7524) | 56% (4221/7524) |
| fortress · our length >= 8 | v1 online (w1+w2) | 8587 | 67% (5763/8587) | 99% (3784/3818) | 41% (1979/4769) | 30% (2545/8587) | 24% (2079/8560) | 3% (285/8587) | 67% (5757/8587) |
| swarm · all turns | v1 online (w1+w2) | 91199 | 86% (78357/91199) | 50% (6628/13217) | 92% (71729/77982) | 51% (46812/91199) | 28% (25522/90859) | 10% (9243/91199) | 39% (35144/91199) |
| swarm · r300+ | v1 online (w1+w2) | 25705 | 86% (22126/25705) | 67% (2215/3327) | 89% (19911/22378) | 41% (10520/25705) | 24% (6004/25530) | 6% (1445/25705) | 53% (13740/25705) |
| swarm · our length >= 8 | v1 online (w1+w2) | 4203 | 72% (3022/4203) | 97% (1760/1808) | 53% (1262/2395) | 34% (1429/4203) | 21% (873/4196) | 6% (233/4203) | 60% (2541/4203) |

## 4. Tags per game (our indicator labels), paired games

| family | bot | bsp | cl | conv | csplit | escape-split | feed | floor | frag | gh | grab | kcap | kx | lsplit | no-exit | no-exit s | pocket-eat | sc | scx | sd | sf | sk | sq | sr | src | srn | srx | sx | sxc | sxx | tg | tgx |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fortress | v1 online (w1+w2) | 0.0 | 146.9 | 4.5 | 4.3 | 187.7 | 9.8 | 0.0 | 4.4 | 15.4 | 96.0 | 0.0 | 19.5 | 0.7 | 184.3 | 1.3 | 20.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 18.8 | 11.1 |
| fortress | stack11 online (bench 1-3) | 0.0 | 367.9 | 6.1 | 12.9 | 200.8 | 12.6 | 0.0 | 1.2 | 78.6 | 139.5 | 0.0 | 5.9 | 4.1 | 200.0 | 2.3 | 24.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 22.4 | 18.9 |
| swarm | v1 online (w1+w2) | 0.0 | 493.2 | 6.9 | 0.0 | 21.2 | 8.5 | 0.0 | 0.0 | 0.0 | 163.1 | 0.0 | 0.0 | 0.0 | 28.7 | 3.4 | 0.1 | 28.8 | 27.3 | 2152.8 | 8.5 | 299.9 | 3.5 | 20.4 | 22.3 | 242.6 | 4.4 | 14.6 | 27.8 | 3.5 | 150.0 | 127.7 |
| swarm | stack11 online (bench 1-3) | 0.9 | 502.8 | 1.9 | 19.5 | 15.3 | 4.1 | 0.4 | 0.8 | 16.3 | 121.6 | 0.2 | 12.0 | 5.1 | 23.6 | 2.9 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 139.1 | 114.2 |

sf recipients (v1 online (w1+w2), swarm maps): 830 feeds; recipient length 3-4: 7% (62/830), 5-7: 6% (53/830), 8-15: 55% (454/830), 16+: 31% (261/830).

## 5. Per map (paired): wins, r100 heads, natural intake, final longest, eliminated

| map | v1 online (w1+w2) W · u100 · nat · longest · elim | stack11 online (bench 1-3) W · u100 · nat · longest · elim |
|---|---|---|
| autarky | 9/14 · 5.3 · 339.0 · 60.6 · 0 | 5/14 · 10.5 · 354.4 · 42.1 · 0 |
| default | 0/14 · 10.7 · 59.4 · 5.1 · 9 | 0/14 · 9.2 · 41.7 · 5.3 · 8 |
| devil | 0/14 · 9.5 · 48.4 · 1.7 · 10 | 0/14 · 6.1 · 25.7 · 0.5 · 11 |
| portals | 7/14 · 10.8 · 239.9 · 38.3 · 0 | 7/14 · 11.6 · 277.1 · 26.9 · 0 |
| prisoners_dilemma | 4/14 · 3.8 · 236.9 · 18.1 · 3 | 4/14 · 3.6 · 243.9 · 16.4 · 2 |
| queen_of_spades | 1/14 · 5.6 · 33.6 · 2.6 · 10 | 0/14 · 4.9 · 24.1 · 1.4 · 11 |
| schooltime | 1/14 · 13.2 · 175.9 · 18.5 · 5 | 0/14 · 11.1 · 140.1 · 13.1 · 8 |
| slithery_fight | 3/14 · 43.1 · 442.8 · 29.4 · 0 | 0/14 · 23.6 · 287.3 · 16.9 · 2 |
| trauma | 3/14 · 7.3 · 78.9 · 12.1 · 0 | 1/14 · 6.4 · 91.7 · 12.4 · 0 |
| trophy | 0/14 · 7.9 · 38.8 · 0.0 · 14 | 0/14 · 7.8 · 38.1 · 0.0 · 14 |
