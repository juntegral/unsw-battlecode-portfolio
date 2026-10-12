# System report: v1 local (proxy4, swarm maps, a+b, 56 games)

- Sets: `local-v1post-a-px4`, `local-v1post-b-px4`
- Compared with (--vs): v0 tagged local (proxy4, a+b): `local-v0t-a-px4`, `local-v0t-b-px4`
- Games: top 6 56, DEV 545 0 (other opponents skipped: 0)
- Tool: `eval/system_report.js` (definitions in its header and `eval/README.md`), generated 2026-10-01 03:41:38 KST

## 1. Outcome

### Top 6 (306, 70, 20, 801, 264, 46)

| | games | W | D | L | E (we eliminated) | they eliminated | final longest ours / theirs |
|---|---|---|---|---|---|---|---|
| **all** | 56 | 5 (8.9%, 3.9%–19.3%) | 1 (1.8%, 0.3%–9.4%) | 50 (89.3%, 78.5%–95.0%) | 11 (19.6%, 11.3%–31.8%) | 0 | 13.9 / 24.4 |
| swarm maps (the other seven) | 56 | 5 (8.9%, 3.9%–19.3%) | 1 (1.8%, 0.3%–9.4%) | 50 (89.3%, 78.5%–95.0%) | 11 (19.6%, 11.3%–31.8%) | 0 | 13.9 / 24.4 |

By map:

| | games | W | D | L | E (we eliminated) | they eliminated | final longest ours / theirs |
|---|---|---|---|---|---|---|---|
| Trauma (swarm, r500) | 8 | 1 (12.5%, 2.2%–47.1%) | 1 (12.5%, 2.2%–47.1%) | 6 (75.0%, 40.9%–92.9%) | 0 (0.0%, 0.0%–32.4%) | 0 | 12.8 / 18.9 |
| Slithery Fight (swarm, r500) | 8 | 0 (0.0%, 0.0%–32.4%) | 0 (0.0%, 0.0%–32.4%) | 8 (100.0%, 67.6%–100.0%) | 0 (0.0%, 0.0%–32.4%) | 0 | 16.9 / 37.6 |
| Schooltime (swarm, r500) | 8 | 3 (37.5%, 13.7%–69.4%) | 0 (0.0%, 0.0%–32.4%) | 5 (62.5%, 30.6%–86.3%) | 0 (0.0%, 0.0%–32.4%) | 0 | 37.0 / 39.4 |
| Default (swarm, elim) | 8 | 0 (0.0%, 0.0%–32.4%) | 0 (0.0%, 0.0%–32.4%) | 8 (100.0%, 67.6%–100.0%) | 2 (25.0%, 7.1%–59.1%) | 0 | 9.6 / 23.8 |
| Devil (swarm, elim) | 8 | 0 (0.0%, 0.0%–32.4%) | 0 (0.0%, 0.0%–32.4%) | 8 (100.0%, 67.6%–100.0%) | 1 (12.5%, 2.2%–47.1%) | 0 | 10.4 / 31.8 |
| Queen Of Spades (swarm, elim) | 8 | 1 (12.5%, 2.2%–47.1%) | 0 (0.0%, 0.0%–32.4%) | 7 (87.5%, 52.9%–97.8%) | 0 (0.0%, 0.0%–32.4%) | 0 | 10.5 / 15.3 |
| Trophy (swarm, elim) | 8 | 0 (0.0%, 0.0%–32.4%) | 0 (0.0%, 0.0%–32.4%) | 8 (100.0%, 67.6%–100.0%) | 8 (100.0%, 67.6%–100.0%) | 0 | 0.0 / 4.4 |

By opponent:

| | games | W | D | L | E (we eliminated) | they eliminated | final longest ours / theirs |
|---|---|---|---|---|---|---|---|
| 306 proxy4_king | 28 | 1 (3.6%, 0.6%–17.7%) | 0 (0.0%, 0.0%–12.1%) | 27 (96.4%, 82.3%–99.4%) | 4 (14.3%, 5.7%–31.5%) | 0 | 13.6 / 27.0 |
| 20 proxy4_elim | 28 | 4 (14.3%, 5.7%–31.5%) | 1 (3.6%, 0.6%–17.7%) | 23 (82.1%, 64.4%–92.1%) | 7 (25.0%, 12.7%–43.4%) | 0 | 14.1 / 21.9 |

### DEV 545 (apart)

| | games | W | D | L | E (we eliminated) | they eliminated | final longest ours / theirs |
|---|---|---|---|---|---|---|---|
| **all** | 0 | – | – | – | – | 0 | – / – |

### Against v0 tagged local (proxy4, a+b)

- v0 tagged local (proxy4, a+b): top 6 27 (22.5%, 15.9%–30.8%) of 120; fortress 17 (47.2%, 32.0%–63.0%); swarm 10 (11.9%, 6.6%–20.5%); DEV –

| | this pool | vs pool | difference (95% CI) | p one-sided: this > vs | p one-sided: this < vs |
|---|---|---|---|---|---|
| top 6, all maps | 5/56 (8.9%) | 27/120 (22.5%) | -13.6 pp (-23.3 … -1.3) | 0.994 | 0.021 |
| top 6, swarm maps (goal: this > vs) | 5/56 (8.9%) | 10/84 (11.9%) | -3.0 pp (-13.0 … 8.6) | 0.797 | 0.396 |
| DEV 545 | 0/0 (–) | 0/0 (–) | – | 1.000 | 1.000 |
| we eliminated, top 7 (lower is better) | 11/56 (19.6%) | 18/120 (15.0%) | 4.6 pp (-6.5 … 17.9) | – | 0.839 |

### Power (one-sided Fisher exact, α = 0.05, against v0 tagged local (proxy4, a+b): 27/120 = 22.5%)

| true top-6 win rate | 56 games ← this pool | 60 games (1 wave) | 120 games (2 waves) | 180 games (3 waves) | 240 games (4 waves) | 360 games (6 waves) |
|---|---|---|---|---|---|---|
| 12% | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 14% | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 17% | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 20% | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 |
| wins needed for p < 0.05 | 20 (35.7%) | 22 (36.7%) | 40 (33.3%) | 58 (32.2%) | 76 (31.7%) | 111 (30.8%) |

- EVAL.md §1 gives the same table against a fixed 9.0% without recording its method; against 81/900 this exact computation lands within about ±0.06 of it. The rule stays: judge a version on 3 pooled waves (180 top-6 games).

## 2. Diagnostic indicators (EVAL.md §2)

- Population: top 6 + DEV 545 games. Per game means; the intake ratio is ours ÷ theirs of the pool sums. Line sacrifice: games that reached r500 with a final king (n in brackets, ours / theirs). v1 targets (swarm maps): r100 heads ≥25, intake ratio ≥50%, line sacrifice ≥15, final longest ≥35, elimination ≤40% (elimination maps).

| cell | games (ledger) | r100 heads ours / theirs | natural intake ours / theirs (ratio) | line sacrifice pearls r300–499 ours / theirs (full games) | final longest ours / theirs | we eliminated |
|---|---|---|---|---|---|---|
| all maps | 56 (0) | – / – | – / – (–) | 4.5 / 13.9 (45 / 45) | – / – | 11 (19.6%, 11.3%–31.8%) |
| 500-round maps (r500) | 24 (0) | – / – | – / – (–) | 6.1 / 14.0 (24 / 24) | – / – | 0 (0.0%, 0.0%–13.8%) |
| elimination maps (elim) | 32 (0) | – / – | – / – (–) | 2.7 / 13.9 (21 / 21) | – / – | 11 (34.4%, 20.4%–51.7%) |
| swarm · r500 (Schooltime, Slithery Fight, Trauma) | 24 (0) | – / – | – / – (–) | 6.1 / 14.0 (24 / 24) | – / – | 0 (0.0%, 0.0%–13.8%) |
| swarm · elim (Default, Devil, Queen Of Spades, Trophy) | 32 (0) | – / – | – / – (–) | 2.7 / 13.9 (21 / 21) | – / – | 11 (34.4%, 20.4%–51.7%) |

v0 tagged local (proxy4, a+b):

| cell | games (ledger) | r100 heads ours / theirs | natural intake ours / theirs (ratio) | line sacrifice pearls r300–499 ours / theirs (full games) | final longest ours / theirs | we eliminated |
|---|---|---|---|---|---|---|
| all maps | 120 (0) | – / – | – / – (–) | 7.0 / 14.5 (101 / 101) | – / – | 18 (15.0%, 9.7%–22.5%) |
| 500-round maps (r500) | 60 (0) | – / – | – / – (–) | 9.7 / 15.9 (60 / 60) | – / – | 0 (0.0%, 0.0%–6.0%) |
| elimination maps (elim) | 60 (0) | – / – | – / – (–) | 3.0 / 12.5 (41 / 41) | – / – | 18 (30.0%, 19.9%–42.5%) |
| fortress · r500 (Autarky, Portals) | 24 (0) | – / – | – / – (–) | 15.4 / 18.1 (24 / 24) | – / – | 0 (0.0%, 0.0%–13.8%) |
| fortress · elim (Prisoners Dilemma) | 12 (0) | – / – | – / – (–) | 3.8 / 14.8 (12 / 12) | – / – | 0 (0.0%, 0.0%–24.2%) |
| swarm · r500 (Schooltime, Slithery Fight, Trauma) | 36 (0) | – / – | – / – (–) | 5.9 / 14.4 (36 / 36) | – / – | 0 (0.0%, 0.0%–9.6%) |
| swarm · elim (Default, Devil, Queen Of Spades, Trophy) | 48 (0) | – / – | – / – (–) | 2.7 / 11.6 (29 / 29) | – / – | 18 (37.5%, 25.2%–51.6%) |

## 3. Engine labels (" E=F" / " E=S")

| map | games | our turns E=F | E=S | unlabelled | E=S share |
|---|---|---|---|---|---|
| Trauma | 8 | 0 | 32590 | 0 | 100.0% |
| Slithery Fight | 8 | 0 | 111705 | 0 | 100.0% |
| Schooltime | 8 | 0 | 55523 | 0 | 100.0% |
| Default | 8 | 0 | 28197 | 0 | 100.0% |
| Devil | 8 | 36 | 14654 | 0 | 99.8% |
| Queen Of Spades | 8 | 0 | 35000 | 0 | 100.0% |
| Trophy | 8 | 0 | 9222 | 0 | 100.0% |
| **all** | 56 | 36 | 286891 | 0 | 100.0% |

## Sources and checks

| set | games (top 6 / DEV) | skipped | no replay | ledger | endgame (legacy cache / system-report cache / computed now) | ledger checks | endgame checks | E= labels |
|---|---|---|---|---|---|---|---|---|
| local-v1post-a-px4 | 28 (28 / 0) | 0 | 0 | 0 | 28 (0 / 0 / 28) | all 0 | all 0 | yes |
| local-v1post-b-px4 | 28 (28 / 0) | 0 | 0 | 0 | 28 (0 / 0 / 28) | all 0 | all 0 | yes |
| local-v0t-a-px4 | 60 (60 / 0) | 0 | 0 | 0 | 60 (0 / 60 / 0) | all 0 | all 0 | yes |
| local-v0t-b-px4 | 60 (60 / 0) | 0 | 0 | 0 | 60 (0 / 60 / 0) | all 0 | all 0 | yes |
