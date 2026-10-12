# v1 local report: v1.3-HV (exp/v13/hv-a, exp/v13/hv-b) vs v1.2 (exp/v11/v11bc-a-px4, exp/v11/v11bc-b-px4, exp/v13/base-a, exp/v13/base-b)

Paired games (same key): 24. v1.3-HV games 24, v1.2 games 64. Opponents: proxy4 (local mimics; sanity only, not a filter).

## 1. Five diagnostic indicators (EVAL.md §2) and outcome, paired games

| cell | bot | games | wins | r100 heads us / opp | r250 heads | natural intake us / opp (ratio) | line sac. pearls r300-499 (full games) | final longest us / opp | eliminated |
|---|---|---:|---:|---|---:|---|---|---|---|
| all maps | v1.3-HV | 24 | 3 | 30.2 / 42.9 | 27.4 | 293.5 / 1182.3 (25%) | 9.6 (24) | 25.7 / 32.3 | 0% (0/24) |
| all maps | v1.2 | 24 | 1 | 24.3 / 44.5 | 22.1 | 160.9 / 1156.7 (14%) | 5.5 (24) | 19.3 / 33.5 | 0% (0/24) |
| swarm | v1.3-HV | 24 | 3 | 30.2 / 42.9 | 27.4 | 293.5 / 1182.3 (25%) | 9.6 (24) | 25.7 / 32.3 | 0% (0/24) |
| swarm | v1.2 | 24 | 1 | 24.3 / 44.5 | 22.1 | 160.9 / 1156.7 (14%) | 5.5 (24) | 19.3 / 33.5 | 0% (0/24) |
| swarm · r500 | v1.3-HV | 24 | 3 | 30.2 / 42.9 | 27.4 | 293.5 / 1182.3 (25%) | 9.6 (24) | 25.7 / 32.3 | 0% (0/24) |
| swarm · r500 | v1.2 | 24 | 1 | 24.3 / 44.5 | 22.1 | 160.9 / 1156.7 (14%) | 5.5 (24) | 19.3 / 33.5 | 0% (0/24) |

## 2. Safety side effects (our deaths per game by cause, mass ledger; team longest >= 8 lost to an enemy head from r340)

| cell | bot | trapped | rammed (by enemy) | ram (we moved into a head) | ally head-on | sacrifice | longest lost from r340 |
|---|---|---:|---:|---:|---:|---:|---|
| all maps | v1.3-HV | 127.0 | 17.1 | 5.5 | 3.4 | 24.5 | 8% (2/24) |
| all maps | v1.2 | 32.5 | 14.8 | 4.7 | 1.3 | 17.0 | 21% (5/24) |
| swarm | v1.3-HV | 127.0 | 17.1 | 5.5 | 3.4 | 24.5 | 8% (2/24) |
| swarm | v1.2 | 32.5 | 14.8 | 4.7 | 1.3 | 17.0 | 21% (5/24) |
| swarm · r500 | v1.3-HV | 127.0 | 17.1 | 5.5 | 3.4 | 24.5 | 8% (2/24) |
| swarm · r500 | v1.2 | 32.5 | 14.8 | 4.7 | 1.3 | 17.0 | 21% (5/24) |

## 2b. The chain, link by link (paired games; per game means)

Heads r50 / r100 -> natural intake -> pieces born r100-430 (children <= 3 long; all births) -> our sacrifices (all; from r300) -> their drops from r300 -> line sacrifice pearls r300-499 (full games) and line share of those drops -> final longest.

| cell | bot | heads r50 · r100 | natural intake | pieces born r100-430 (births) | sacrifices (r300+) | sac. drops r300+ | line sac. pearls | line share | final longest | sf main · late feeds |
|---|---|---|---:|---|---|---:|---:|---:|---:|---|
| all maps | v1.3-HV | 25.2 · 30.2 | 293.5 | 77.1 (93.5) | 24.5 (16.9) | 29.4 | 9.6 | 33% | 25.7 | 20.7 · 4.0 |
| all maps | v1.2 | 20.1 · 24.3 | 160.9 | 29.7 (38.1) | 17.0 (10.6) | 18.5 | 5.5 | 30% | 19.3 | 13.5 · 3.6 |
| swarm | v1.3-HV | 25.2 · 30.2 | 293.5 | 77.1 (93.5) | 24.5 (16.9) | 29.4 | 9.6 | 33% | 25.7 | 20.7 · 4.0 |
| swarm | v1.2 | 20.1 · 24.3 | 160.9 | 29.7 (38.1) | 17.0 (10.6) | 18.5 | 5.5 | 30% | 19.3 | 13.5 · 3.6 |
| swarm · r500 | v1.3-HV | 25.2 · 30.2 | 293.5 | 77.1 (93.5) | 24.5 (16.9) | 29.4 | 9.6 | 33% | 25.7 | 20.7 · 4.0 |
| swarm · r500 | v1.2 | 20.1 · 24.3 | 160.9 | 29.7 (38.1) | 17.0 (10.6) | 18.5 | 5.5 | 30% | 19.3 | 13.5 · 3.6 |

## 2c. Target overlap (research transfer 1): target-labelled turns (v1 " sd", v0 " F") whose target another of our dragons also targets that round

| family | bot | target turns / game | same tile | within 3 |
|---|---|---:|---:|---:|
| swarm | v1.3-HV | 2545.1 | 9.4% | 49.4% |
| swarm | v1.2 | 3237.9 | 10.7% | 54.4% |

## 3. Belief accuracy (tag " bl<len>@x,y k<0|1>" every 5 rounds vs the true longest other living ally at that turn start)

| cell | bot | tagged turns | king verdict right | truly longest: says king | not longest: says not king | length within 1 | position within 3 | believes longer than true (+2) | believes shorter (-2) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all maps · all turns | v1.3-HV | 49053 | 94% (46217/49053) | 62% (1992/3190) | 96% (44225/45863) | 45% (22013/49053) | 25% (12399/49053) | 27% (13038/49053) | 29% (14002/49053) |
| all maps · all turns | v1.2 | 40378 | 91% (36543/40378) | 53% (1964/3716) | 94% (34579/36662) | 43% (17398/40378) | 24% (9859/40378) | 27% (10956/40378) | 30% (12024/40378) |
| all maps · r300+ | v1.3-HV | 13043 | 94% (12250/13043) | 91% (960/1060) | 94% (11290/11983) | 52% (6794/13043) | 31% (4053/13043) | 7% (913/13043) | 41% (5336/13043) |
| all maps · r300+ | v1.2 | 10916 | 88% (9658/10916) | 77% (927/1210) | 90% (8731/9706) | 49% (5334/10916) | 28% (3066/10916) | 10% (1136/10916) | 41% (4446/10916) |
| all maps · our length >= 8 | v1.3-HV | 2637 | 85% (2237/2637) | 92% (1273/1378) | 77% (964/1259) | 54% (1432/2637) | 36% (944/2637) | 10% (256/2637) | 36% (949/2637) |
| all maps · our length >= 8 | v1.2 | 2226 | 77% (1711/2226) | 93% (1101/1182) | 58% (610/1044) | 45% (1011/2226) | 28% (626/2226) | 10% (229/2226) | 44% (986/2226) |
| swarm · all turns | v1.3-HV | 49053 | 94% (46217/49053) | 62% (1992/3190) | 96% (44225/45863) | 45% (22013/49053) | 25% (12399/49053) | 27% (13038/49053) | 29% (14002/49053) |
| swarm · all turns | v1.2 | 40378 | 91% (36543/40378) | 53% (1964/3716) | 94% (34579/36662) | 43% (17398/40378) | 24% (9859/40378) | 27% (10956/40378) | 30% (12024/40378) |
| swarm · r300+ | v1.3-HV | 13043 | 94% (12250/13043) | 91% (960/1060) | 94% (11290/11983) | 52% (6794/13043) | 31% (4053/13043) | 7% (913/13043) | 41% (5336/13043) |
| swarm · r300+ | v1.2 | 10916 | 88% (9658/10916) | 77% (927/1210) | 90% (8731/9706) | 49% (5334/10916) | 28% (3066/10916) | 10% (1136/10916) | 41% (4446/10916) |
| swarm · our length >= 8 | v1.3-HV | 2637 | 85% (2237/2637) | 92% (1273/1378) | 77% (964/1259) | 54% (1432/2637) | 36% (944/2637) | 10% (256/2637) | 36% (949/2637) |
| swarm · our length >= 8 | v1.2 | 2226 | 77% (1711/2226) | 93% (1101/1182) | 58% (610/1044) | 45% (1011/2226) | 28% (626/2226) | 10% (229/2226) | 44% (986/2226) |

## 4. Tags per game (our indicator labels), paired games

| family | bot | cl | conv | escape-split | feed | grab | no-exit | no-exit s | pocket-eat | sc | scx | sd | sf | sk | sq | sr | src | srn | srx | sx | sxc | sxx | tg | tgx |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| swarm | v1.3-HV | 721.8 | 20.7 | 48.5 | 24.8 | 383.2 | 125.6 | 6.6 | 0.1 | 50.5 | 61.9 | 2545.1 | 24.8 | 504.6 | 5.8 | 34.6 | 41.3 | 664.9 | 5.2 | 36.3 | 59.8 | 9.9 | 252.5 | 187.2 |
| swarm | v1.2 | 518.0 | 13.5 | 22.1 | 17.1 | 203.5 | 31.8 | 2.1 | 0.1 | 29.6 | 43.0 | 3237.9 | 17.1 | 574.3 | 5.3 | 24.4 | 33.0 | 380.3 | 4.0 | 23.5 | 38.7 | 6.0 | 241.5 | 176.2 |

sf recipients (v1.3-HV, swarm maps): 594 feeds; recipient length 3-4: 6% (38/594), 5-7: 6% (37/594), 8-15: 56% (335/594), 16+: 31% (184/594).

## 5. Per map (paired): wins, r100 heads, natural intake, final longest, eliminated

| map | v1.3-HV W · u100 · nat · longest · elim | v1.2 W · u100 · nat · longest · elim |
|---|---|---|
| slithery_fight | 2/8 · 47.0 · 420.0 · 32.3 · 0 | 1/8 · 40.3 · 216.1 · 26.8 · 0 |
| slithery_fight_b | 1/8 · 36.4 · 360.0 · 27.4 · 0 | 0/8 · 26.6 · 189.3 · 18.0 · 0 |
| trauma | 0/8 · 7.3 · 100.4 · 17.4 · 0 | 0/8 · 6.0 · 77.4 · 13.1 · 0 |
