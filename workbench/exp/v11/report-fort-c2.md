# v1 local report: v1.1 C2 (exp/v11/v11c-fort) vs v1.1 noC2 (exp/v11/v11-fort)

Paired games (same key): 14. v1.1 C2 games 14, v1.1 noC2 games 14. Opponents: proxy4 (local mimics; sanity only, not a filter).

## 1. Five diagnostic indicators (EVAL.md §2) and outcome, paired games

| cell | bot | games | wins | r100 heads us / opp | r250 heads | natural intake us / opp (ratio) | line sac. pearls r300-499 (full games) | final longest us / opp | eliminated |
|---|---|---:|---:|---|---:|---|---|---|---|
| all maps | v1.1 C2 | 14 | 10 | 6.8 / 20.0 | 6.9 | 266.1 / 336.2 (79%) | 12.9 (13) | 38.1 / 24.2 | 7% (1/14) |
| all maps | v1.1 noC2 | 14 | 10 | 6.8 / 20.0 | 7.4 | 263.6 / 332.9 (79%) | 11.4 (14) | 39.9 / 29.1 | 0% (0/14) |
| fortress | v1.1 C2 | 14 | 10 | 6.8 / 20.0 | 6.9 | 266.1 / 336.2 (79%) | 12.9 (13) | 38.1 / 24.2 | 7% (1/14) |
| fortress | v1.1 noC2 | 14 | 10 | 6.8 / 20.0 | 7.4 | 263.6 / 332.9 (79%) | 11.4 (14) | 39.9 / 29.1 | 0% (0/14) |
| fortress · r500 | v1.1 C2 | 8 | 7 | 8.9 / 27.9 | 8.6 | 292.6 / 426.9 (69%) | 18.6 (8) | 52.6 / 28.3 | 0% (0/8) |
| fortress · r500 | v1.1 noC2 | 8 | 8 | 8.9 / 27.9 | 9.4 | 278.3 / 436.6 (64%) | 16.4 (8) | 53.1 / 30.5 | 0% (0/8) |
| fortress · elim (PD) | v1.1 C2 | 6 | 3 | 4.0 / 9.5 | 4.5 | 230.7 / 215.3 (107%) | 3.8 (5) | 18.8 / 18.8 | 17% (1/6) |
| fortress · elim (PD) | v1.1 noC2 | 6 | 2 | 4.0 / 9.5 | 4.7 | 244.0 / 194.5 (125%) | 4.8 (6) | 22.3 / 27.2 | 0% (0/6) |

## 2. Safety side effects (our deaths per game by cause, mass ledger; team longest >= 8 lost to an enemy head from r340)

| cell | bot | trapped | rammed (by enemy) | ram (we moved into a head) | ally head-on | sacrifice | longest lost from r340 |
|---|---|---:|---:|---:|---:|---:|---|
| all maps | v1.1 C2 | 185.7 | 1.6 | 0.0 | 2.6 | 8.9 | 0% (0/14) |
| all maps | v1.1 noC2 | 190.6 | 1.4 | 0.0 | 1.7 | 8.3 | 0% (0/14) |
| fortress | v1.1 C2 | 185.7 | 1.6 | 0.0 | 2.6 | 8.9 | 0% (0/14) |
| fortress | v1.1 noC2 | 190.6 | 1.4 | 0.0 | 1.7 | 8.3 | 0% (0/14) |

## 2b. The chain, link by link (paired games; per game means)

Heads r50 / r100 -> natural intake -> pieces born r100-430 (children <= 3 long; all births) -> our sacrifices (all; from r300) -> their drops from r300 -> line sacrifice pearls r300-499 (full games) and line share of those drops -> final longest.

| cell | bot | heads r50 · r100 | natural intake | pieces born r100-430 (births) | sacrifices (r300+) | sac. drops r300+ | line sac. pearls | line share | final longest | sf main · late feeds |
|---|---|---|---:|---|---|---:|---:|---:|---:|---|
| all maps | v1.1 C2 | 5.9 · 6.8 | 266.1 | 11.1 (136.4) | 8.9 (8.8) | 27.4 | 12.9 | 46% | 38.1 | 0.0 · 0.0 |
| all maps | v1.1 noC2 | 5.9 · 6.8 | 263.6 | 10.3 (137.4) | 8.3 (8.2) | 24.1 | 11.4 | 47% | 39.9 | 0.0 · 0.0 |
| fortress | v1.1 C2 | 5.9 · 6.8 | 266.1 | 11.1 (136.4) | 8.9 (8.8) | 27.4 | 12.9 | 46% | 38.1 | 0.0 · 0.0 |
| fortress | v1.1 noC2 | 5.9 · 6.8 | 263.6 | 10.3 (137.4) | 8.3 (8.2) | 24.1 | 11.4 | 47% | 39.9 | 0.0 · 0.0 |

## 2c. Target overlap (research transfer 1): target-labelled turns (v1 " sd", v0 " F") whose target another of our dragons also targets that round

| family | bot | target turns / game | same tile | within 3 |
|---|---|---:|---:|---:|
| fortress | v1.1 C2 | 269.8 | 7.5% | 13.4% |
| fortress | v1.1 noC2 | 262.6 | 9.3% | 16.0% |

## 3. Belief accuracy (tag " bl<len>@x,y k<0|1>" every 5 rounds vs the true longest other living ally at that turn start)

| cell | bot | tagged turns | king verdict right | truly longest: says king | not longest: says not king | length within 1 | position within 3 | believes longer than true (+2) | believes shorter (-2) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all maps · all turns | v1.1 C2 | 7450 | 81% (6015/7450) | 98% (1360/1387) | 77% (4655/6063) | 33% (2423/7450) | 27% (2008/7446) | 3% (219/7450) | 65% (4808/7450) |
| all maps · all turns | v1.1 noC2 | 7333 | 79% (5791/7333) | 99% (1371/1387) | 74% (4420/5946) | 29% (2134/7333) | 26% (1926/7331) | 2% (167/7333) | 69% (5032/7333) |
| all maps · r300+ | v1.1 C2 | 2399 | 88% (2116/2399) | 98% (532/544) | 85% (1584/1855) | 43% (1032/2399) | 36% (858/2395) | 6% (137/2399) | 51% (1230/2399) |
| all maps · r300+ | v1.1 noC2 | 2212 | 84% (1867/2212) | 99% (536/539) | 80% (1331/1673) | 40% (889/2212) | 35% (783/2210) | 4% (91/2212) | 56% (1232/2212) |
| all maps · our length >= 8 | v1.1 C2 | 2778 | 74% (2049/2778) | 98% (1278/1298) | 52% (771/1480) | 37% (1025/2778) | 29% (801/2777) | 4% (106/2778) | 59% (1647/2778) |
| all maps · our length >= 8 | v1.1 noC2 | 2753 | 71% (1951/2753) | 99% (1299/1308) | 45% (652/1445) | 35% (959/2753) | 30% (822/2751) | 3% (92/2753) | 62% (1702/2753) |
| fortress · all turns | v1.1 C2 | 7450 | 81% (6015/7450) | 98% (1360/1387) | 77% (4655/6063) | 33% (2423/7450) | 27% (2008/7446) | 3% (219/7450) | 65% (4808/7450) |
| fortress · all turns | v1.1 noC2 | 7333 | 79% (5791/7333) | 99% (1371/1387) | 74% (4420/5946) | 29% (2134/7333) | 26% (1926/7331) | 2% (167/7333) | 69% (5032/7333) |
| fortress · r300+ | v1.1 C2 | 2399 | 88% (2116/2399) | 98% (532/544) | 85% (1584/1855) | 43% (1032/2399) | 36% (858/2395) | 6% (137/2399) | 51% (1230/2399) |
| fortress · r300+ | v1.1 noC2 | 2212 | 84% (1867/2212) | 99% (536/539) | 80% (1331/1673) | 40% (889/2212) | 35% (783/2210) | 4% (91/2212) | 56% (1232/2212) |
| fortress · our length >= 8 | v1.1 C2 | 2778 | 74% (2049/2778) | 98% (1278/1298) | 52% (771/1480) | 37% (1025/2778) | 29% (801/2777) | 4% (106/2778) | 59% (1647/2778) |
| fortress · our length >= 8 | v1.1 noC2 | 2753 | 71% (1951/2753) | 99% (1299/1308) | 45% (652/1445) | 35% (959/2753) | 30% (822/2751) | 3% (92/2753) | 62% (1702/2753) |

## 4. Tags per game (our indicator labels), paired games

| family | bot | cl | conv | csplit | escape-split | feed | frag | gh | grab | kx | lsplit | no-exit | no-exit s | pocket-eat | tg | tgx |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fortress | v1.1 C2 | 137.5 | 3.1 | 4.0 | 187.3 | 8.7 | 5.2 | 16.9 | 75.5 | 10.6 | 0.4 | 184.6 | 0.8 | 24.1 | 27.9 | 22.7 |
| fortress | v1.1 noC2 | 124.1 | 4.1 | 3.5 | 191.7 | 8.2 | 4.0 | 13.3 | 76.7 | 11.1 | 0.8 | 189.7 | 0.8 | 23.9 | 25.0 | 21.9 |

## 5. Per map (paired): wins, r100 heads, natural intake, final longest, eliminated

| map | v1.1 C2 W · u100 · nat · longest · elim | v1.1 noC2 W · u100 · nat · longest · elim |
|---|---|---|
| autarky | 4/4 · 5.5 · 343.5 · 64.0 · 0 | 4/4 · 5.5 · 341.8 · 64.5 · 0 |
| portals | 3/4 · 12.3 · 241.8 · 41.3 · 0 | 4/4 · 12.3 · 214.8 · 41.8 · 0 |
| prisoners_dilemma | 3/4 · 4.0 · 260.5 · 21.8 · 1 | 2/4 · 4.0 · 280.5 · 27.0 · 0 |
| prisoners_dilemma_10 | 0/2 · 4.0 · 171.0 · 13.0 · 0 | 0/2 · 4.0 · 171.0 · 13.0 · 0 |
