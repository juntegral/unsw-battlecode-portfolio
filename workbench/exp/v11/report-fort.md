# v1 local report: v1.1 (exp/v11/v11-fort) vs v1 (exp/v11/v1-fort)

Paired games (same key): 14. v1.1 games 14, v1 games 14. Opponents: proxy4 (local mimics; sanity only, not a filter).

## 1. Five diagnostic indicators (EVAL.md §2) and outcome, paired games

| cell | bot | games | wins | r100 heads us / opp | r250 heads | natural intake us / opp (ratio) | line sac. pearls r300-499 (full games) | final longest us / opp | eliminated |
|---|---|---:|---:|---|---:|---|---|---|---|
| all maps | v1.1 | 14 | 10 | 6.8 / 20.0 | 7.4 | 263.6 / 332.9 (79%) | 11.4 (14) | 39.9 / 29.1 | 0% (0/14) |
| all maps | v1 | 14 | 9 | 6.6 / 20.7 | 7.5 | 264.4 / 337.8 (78%) | 14.1 (12) | 38.7 / 28.3 | 14% (2/14) |
| fortress | v1.1 | 14 | 10 | 6.8 / 20.0 | 7.4 | 263.6 / 332.9 (79%) | 11.4 (14) | 39.9 / 29.1 | 0% (0/14) |
| fortress | v1 | 14 | 9 | 6.6 / 20.7 | 7.5 | 264.4 / 337.8 (78%) | 14.1 (12) | 38.7 / 28.3 | 14% (2/14) |
| fortress · r500 | v1.1 | 8 | 8 | 8.9 / 27.9 | 9.4 | 278.3 / 436.6 (64%) | 16.4 (8) | 53.1 / 30.5 | 0% (0/8) |
| fortress · r500 | v1 | 8 | 7 | 8.6 / 29.1 | 10.0 | 290.1 / 428.0 (68%) | 19.8 (8) | 57.0 / 37.0 | 0% (0/8) |
| fortress · elim (PD) | v1.1 | 6 | 2 | 4.0 / 9.5 | 4.7 | 244.0 / 194.5 (125%) | 4.8 (6) | 22.3 / 27.2 | 0% (0/6) |
| fortress · elim (PD) | v1 | 6 | 2 | 4.0 / 9.5 | 4.2 | 230.0 / 217.5 (106%) | 2.8 (4) | 14.3 / 16.7 | 33% (2/6) |

## 2. Safety side effects (our deaths per game by cause, mass ledger; team longest >= 8 lost to an enemy head from r340)

| cell | bot | trapped | rammed (by enemy) | ram (we moved into a head) | ally head-on | sacrifice | longest lost from r340 |
|---|---|---:|---:|---:|---:|---:|---|
| all maps | v1.1 | 190.6 | 1.4 | 0.0 | 1.7 | 8.3 | 0% (0/14) |
| all maps | v1 | 188.4 | 1.4 | 0.1 | 1.1 | 9.0 | 14% (2/14) |
| fortress | v1.1 | 190.6 | 1.4 | 0.0 | 1.7 | 8.3 | 0% (0/14) |
| fortress | v1 | 188.4 | 1.4 | 0.1 | 1.1 | 9.0 | 14% (2/14) |

## 2b. The chain, link by link (paired games; per game means)

Heads r50 / r100 -> natural intake -> pieces born r100-430 (children <= 3 long; all births) -> our sacrifices (all; from r300) -> their drops from r300 -> line sacrifice pearls r300-499 (full games) and line share of those drops -> final longest.

| cell | bot | heads r50 · r100 | natural intake | pieces born r100-430 (births) | sacrifices (r300+) | sac. drops r300+ | line sac. pearls | line share | final longest | sf main · late feeds |
|---|---|---|---:|---|---|---:|---:|---:|---:|---|
| all maps | v1.1 | 5.9 · 6.8 | 263.6 | 10.3 (137.4) | 8.3 (8.2) | 24.1 | 11.4 | 47% | 39.9 | 0.0 · 0.0 |
| all maps | v1 | 5.9 · 6.6 | 264.4 | 9.8 (137.9) | 9.0 (8.9) | 27.0 | 14.1 | 48% | 38.7 | 0.0 · 0.0 |
| fortress | v1.1 | 5.9 · 6.8 | 263.6 | 10.3 (137.4) | 8.3 (8.2) | 24.1 | 11.4 | 47% | 39.9 | 0.0 · 0.0 |
| fortress | v1 | 5.9 · 6.6 | 264.4 | 9.8 (137.9) | 9.0 (8.9) | 27.0 | 14.1 | 48% | 38.7 | 0.0 · 0.0 |

## 2c. Target overlap (research transfer 1): target-labelled turns (v1 " sd", v0 " F") whose target another of our dragons also targets that round

| family | bot | target turns / game | same tile | within 3 |
|---|---|---:|---:|---:|
| fortress | v1.1 | 262.6 | 9.3% | 16.0% |
| fortress | v1 | 254.1 | 7.2% | 15.0% |

## 3. Belief accuracy (tag " bl<len>@x,y k<0|1>" every 5 rounds vs the true longest other living ally at that turn start)

| cell | bot | tagged turns | king verdict right | truly longest: says king | not longest: says not king | length within 1 | position within 3 | believes longer than true (+2) | believes shorter (-2) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all maps · all turns | v1.1 | 7333 | 79% (5791/7333) | 99% (1371/1387) | 74% (4420/5946) | 29% (2134/7333) | 26% (1926/7331) | 2% (167/7333) | 69% (5032/7333) |
| all maps · all turns | v1 | 7319 | 78% (5682/7319) | 99% (1374/1394) | 73% (4308/5925) | 26% (1881/7319) | 24% (1743/7319) | 2% (175/7319) | 72% (5263/7319) |
| all maps · r300+ | v1.1 | 2212 | 84% (1867/2212) | 99% (536/539) | 80% (1331/1673) | 40% (889/2212) | 35% (783/2210) | 4% (91/2212) | 56% (1232/2212) |
| all maps · r300+ | v1 | 2220 | 85% (1896/2220) | 98% (527/538) | 81% (1369/1682) | 41% (916/2220) | 35% (768/2220) | 6% (123/2220) | 53% (1181/2220) |
| all maps · our length >= 8 | v1.1 | 2753 | 71% (1951/2753) | 99% (1299/1308) | 45% (652/1445) | 35% (959/2753) | 30% (822/2751) | 3% (92/2753) | 62% (1702/2753) |
| all maps · our length >= 8 | v1 | 2801 | 70% (1952/2801) | 99% (1295/1306) | 44% (657/1495) | 34% (939/2801) | 28% (787/2801) | 4% (102/2801) | 63% (1760/2801) |
| fortress · all turns | v1.1 | 7333 | 79% (5791/7333) | 99% (1371/1387) | 74% (4420/5946) | 29% (2134/7333) | 26% (1926/7331) | 2% (167/7333) | 69% (5032/7333) |
| fortress · all turns | v1 | 7319 | 78% (5682/7319) | 99% (1374/1394) | 73% (4308/5925) | 26% (1881/7319) | 24% (1743/7319) | 2% (175/7319) | 72% (5263/7319) |
| fortress · r300+ | v1.1 | 2212 | 84% (1867/2212) | 99% (536/539) | 80% (1331/1673) | 40% (889/2212) | 35% (783/2210) | 4% (91/2212) | 56% (1232/2212) |
| fortress · r300+ | v1 | 2220 | 85% (1896/2220) | 98% (527/538) | 81% (1369/1682) | 41% (916/2220) | 35% (768/2220) | 6% (123/2220) | 53% (1181/2220) |
| fortress · our length >= 8 | v1.1 | 2753 | 71% (1951/2753) | 99% (1299/1308) | 45% (652/1445) | 35% (959/2753) | 30% (822/2751) | 3% (92/2753) | 62% (1702/2753) |
| fortress · our length >= 8 | v1 | 2801 | 70% (1952/2801) | 99% (1295/1306) | 44% (657/1495) | 34% (939/2801) | 28% (787/2801) | 4% (102/2801) | 63% (1760/2801) |

## 4. Tags per game (our indicator labels), paired games

| family | bot | cl | conv | csplit | escape-split | feed | frag | gh | grab | kx | lsplit | no-exit | no-exit s | pocket-eat | tg | tgx |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fortress | v1.1 | 124.1 | 4.1 | 3.5 | 191.7 | 8.2 | 4.0 | 13.3 | 76.7 | 11.1 | 0.8 | 189.7 | 0.8 | 23.9 | 25.0 | 21.9 |
| fortress | v1 | 120.2 | 4.4 | 3.4 | 191.0 | 9.0 | 2.8 | 13.2 | 81.9 | 11.4 | 0.6 | 187.4 | 0.8 | 23.9 | 25.9 | 21.4 |

## 5. Per map (paired): wins, r100 heads, natural intake, final longest, eliminated

| map | v1.1 W · u100 · nat · longest · elim | v1 W · u100 · nat · longest · elim |
|---|---|---|
| autarky | 4/4 · 5.5 · 341.8 · 64.5 · 0 | 4/4 · 5.5 · 340.8 · 68.8 · 0 |
| portals | 4/4 · 12.3 · 214.8 · 41.8 · 0 | 3/4 · 11.8 · 239.5 · 45.3 · 0 |
| prisoners_dilemma | 2/4 · 4.0 · 280.5 · 27.0 · 0 | 2/4 · 4.0 · 259.5 · 15.0 · 2 |
| prisoners_dilemma_10 | 0/2 · 4.0 · 171.0 · 13.0 · 0 | 0/2 · 4.0 · 171.0 · 13.0 · 0 |
