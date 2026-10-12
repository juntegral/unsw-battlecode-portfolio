# Rank-1 behaviour scoreboard

Vibing++ (306): 597 games / 1194 side rows, 19 layouts; 380 wins, 217 losses, 0 draws. Selected by team ID from 1874 replays; excluded 1277 other-team games. Completed UTC: 2026-10-04T12:49:29.107Z to 2026-10-04T19:26:26.707Z. Opponents: 21 distinct; 13 rated 2100+ in at least one sampled game, across 448 games; missing ratings: 0.
Layouts (games): Around UNSW #1: 31; Australia #1: 43; Autarky #1: 34; Default #1: 33; Devil #1: 43; Islands #1: 34; Maze #1: 32; Portals #1: 33; Prisoners Dilemma #1: 20; Prisoners Dilemma #2: 15; Queen Of Spades #1: 26; Schooltime #1: 24; Schooltime #2: 14; Slithery Fight #1: 32; Stripes #1: 30; Tower Defense #1: 38; Trauma #1: 38; Trophy #1: 42; weakhold #1: 35.
O = ours (500 games); R = rank-1; RO = its opponents; E = our ladder opponents rated 2100+ (70 games). Shared O/R: equal-weight means over 19 matching layouts (size, edges, starting dragons; colour swaps equivalent). Shared means use the same valid layouts for both bots per rate; higher excludes ties/missing. Gap = (R−O)/max(|R|,|O|) on shared means (zero/zero = 0). NA means no denominator.
Unchanged fingerprint definitions; pooled numerator/denominator rates, inclusive windows, percentages 0–100; full 20-round blocks only. Harvest follows birth cohorts to game end; wait/death/contact means are conditional; incidence uses original follow-up eligibility. Consistency: pooled/shared directions agree and ≥ceil(15×valid layouts/19) layout signs agree; descriptive counts, no uncertainty test. The 12 gaps below are largest among consistent behaviour rates. First 30 rows reproduce the fingerprint ranked table; extra rows have ≥25% absolute pooled or shared gap. Every rate and denominator is in scoreboard.json.

| Rate (unit) | Window | O | R | RO | E | Shared O | Shared R | R higher/valid | Gap |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Death: no action (/1k turns) | 0-100 | 0.000 | 0.000 | 3.892 | 5.475 | 0.000 | 0.000 | 0/19 | +0.0% |
| Same-team head-on meetings (/1k turns) | 101-300 | 0.107 | 0.314 | 0.314 | 0.336 | 0.118 | 0.292 | 12/19 | +59.7% |
| Death: head-on mover (/1k turns) | 101-300 | 1.456 | 4.087 | 3.213 | 2.443 | 1.991 | 4.189 | 17/19 | +52.5% |
| Head-on meetings started (/1k turns) | 101-300 | 1.456 | 4.087 | 3.213 | 2.443 | 1.991 | 4.189 | 17/19 | +52.5% |
| Death: head-on mover (/1k turns) | 0-100 | 1.510 | 4.014 | 2.628 | 2.853 | 2.186 | 4.272 | 17/19 | +48.8% |
| Head-on meetings started (/1k turns) | 0-100 | 1.510 | 4.014 | 2.628 | 2.853 | 2.186 | 4.272 | 17/19 | +48.8% |
| Portal steps (/1k turns) | game | 11.891 | 11.628 | 8.377 | 10.304 | 15.097 | 14.938 | 8/19 | -1.1% |
| Repeated-spawn tile nearby (%) | 101-300 | 24.242 | 36.327 | 33.642 | 35.551 | 25.266 | 35.478 | 18/19 | +28.8% |
| Blind direction kept (%) | 0-100 | 39.031 | 50.315 | 50.497 | 49.826 | 40.408 | 48.895 | 18/19 | +17.4% |
| Blind direction kept (%) | 101-300 | 37.382 | 49.099 | 46.189 | 46.570 | 37.413 | 47.895 | 18/19 | +21.9% |
| Splits per eaten pearl (/pearl) | game | 0.366 | 0.331 | 0.335 | 0.293 | 0.382 | 0.362 | 4/19 | -5.2% |
| Splits per eaten pearl (/pearl) | 101-300 | 0.376 | 0.346 | 0.349 | 0.291 | 0.387 | 0.373 | 5/19 | -3.5% |
| Repeated-spawn tile nearby (%) | 0-100 | 15.740 | 21.610 | 18.053 | 20.866 | 13.456 | 19.176 | 18/19 | +29.8% |
| Blind turns (%) | 101-300 | 49.968 | 42.256 | 45.239 | 41.662 | 48.288 | 40.793 | 3/19 | -15.5% |
| Blind re-tread (%) | 101-300 | 17.566 | 10.264 | 15.960 | 16.011 | 19.702 | 11.215 | 1/19 | -43.1% |
| Blind tiles visited per 20-round dragon block (tiles/block) | 101-300 | 11.441 | 9.758 | 10.012 | 10.343 | 10.157 | 8.852 | 2/19 | -12.9% |
| All deaths (/1k turns) | game | 20.804 | 27.222 | 23.547 | 25.307 | 20.065 | 27.789 | 18/19 | +27.8% |
| Split frequency (/1k turns) | game | 22.245 | 28.634 | 24.481 | 26.773 | 22.661 | 30.580 | 17/19 | +25.9% |
| Blind successful movement (%) | 101-300 | 98.530 | 97.547 | 98.063 | 97.697 | 98.431 | 97.490 | 1/19 | -1.0% |
| Death: illegal split (/1k turns) | 0-100 | 0.000 | 19.794 | 0.012 | 0.000 | 0.000 | 18.111 | 19/19 | +100.0% |
| Death: illegal split (/1k turns) | 101-300 | 0.000 | 18.494 | 0.006 | 0.000 | 0.000 | 18.792 | 19/19 | +100.0% |
| Death: timeout (/1k turns) | 101-300 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0/19 | +0.0% |
| Death: unpaid sprint (/1k turns) | 101-300 | 0.000 | 0.000 | 0.003 | 0.002 | 0.000 | 0.000 | 0/19 | +0.0% |
| Queen death: illegal split (%) | 101-300 | 0.000 | 12.262 | 0.000 | 0.000 | 0.000 | 17.739 | 12/19 | +100.0% |
| Queen death: no action (%) | 0-100 | 0.000 | 0.000 | 0.508 | 1.471 | 0.000 | 0.000 | 0/19 | +0.0% |
| Queen death: head-on mover (%) | 0-100 | 0.818 | 2.721 | 1.861 | 7.353 | 0.747 | 2.454 | 7/19 | +69.6% |
| Queen death: wall (%) | 101-300 | 12.141 | 0.000 | 1.256 | 2.564 | 19.733 | 0.000 | 0/19 | -100.0% |
| Same-team head-on meetings (/1k turns) | 0-100 | 0.098 | 0.222 | 0.259 | 0.296 | 0.079 | 0.228 | 11/19 | +65.2% |
| Queen death: own body (%) | 0-100 | 2.658 | 0.000 | 1.184 | 2.941 | 2.809 | 0.000 | 0/19 | -100.0% |
| Death: no action (/1k turns) | 101-300 | 1.150 | 0.000 | 3.808 | 7.978 | 0.639 | 0.000 | 0/19 | -100.0% |
| Death: wall (/1k turns) | 0-100 | 10.081 | 0.000 | 2.902 | 3.785 | 8.315 | 0.000 | 0/19 | -100.0% |
| Death: wall (/1k turns) | 101-300 | 7.482 | 0.000 | 2.761 | 3.428 | 7.273 | 0.000 | 0/19 | -100.0% |
| Queen death: illegal split (%) | 0-100 | 0.000 | 10.884 | 0.000 | 0.000 | 0.000 | 11.063 | 10/19 | +100.0% |
| Queen death: own body (%) | 101-300 | 6.709 | 0.000 | 2.764 | 2.564 | 7.316 | 0.000 | 0/19 | -100.0% |
| Queen death: wall (%) | 0-100 | 6.544 | 0.000 | 1.523 | 2.941 | 6.919 | 0.000 | 0/19 | -100.0% |
| Death: own body (/1k turns) | 0-100 | 3.800 | 0.005 | 5.359 | 4.940 | 3.153 | 0.005 | 0/19 | -99.8% |
| Death: own body (/1k turns) | 101-300 | 3.514 | 0.007 | 5.390 | 5.326 | 3.436 | 0.008 | 0/19 | -99.8% |
| First contact in window (%) | 101-300 | 4.400 | 0.335 | 0.335 | 2.857 | 3.659 | 0.277 | 0/19 | -92.4% |
| Queen death: another body (%) | 0-100 | 2.249 | 0.340 | 0.338 | 1.471 | 2.589 | 0.291 | 2/19 | -88.8% |
| Death: another body (/1k turns) | 0-100 | 2.815 | 0.272 | 1.605 | 1.936 | 1.889 | 0.298 | 0/19 | -84.2% |
| Death: another body (/1k turns) | 101-300 | 2.683 | 0.493 | 2.299 | 2.932 | 2.465 | 0.479 | 0/19 | -80.6% |
| Queen death: another body (%) | 101-300 | 3.514 | 0.272 | 0.503 | 0.000 | 2.742 | 0.658 | 1/19 | -76.0% |
| Blind re-tread (%) | 0-100 | 16.257 | 9.536 | 13.490 | 13.160 | 17.841 | 10.431 | 2/19 | -41.5% |
| First contact round (rounds/contact) | game | 22.172 | 12.608 | 12.941 | 18.257 | 19.895 | 12.485 | 4/19 | -37.2% |
| Birth-cohort wait until eaten (rounds/eaten) | 101-300 | 8.502 | 5.239 | 5.900 | 6.584 | 8.660 | 5.505 | 1/19 | -36.4% |
| Birth-cohort wait until eaten (rounds/eaten) | 0-100 | 17.464 | 13.281 | 13.255 | 12.701 | 26.550 | 17.058 | 3/19 | -35.8% |
| First contact round (rounds/contact) | 0-100 | 17.192 | 12.296 | 12.634 | 15.015 | 17.837 | 12.276 | 5/19 | -31.2% |
| Adjacent pearl missed (%) | 101-300 | 28.834 | 21.690 | 23.337 | 24.497 | 26.872 | 19.331 | 4/19 | -28.1% |
| Cross-team head-on involvement (/1k turns) | 0-100 | 4.025 | 6.196 | 6.107 | 3.387 | 4.738 | 6.579 | 16/19 | +28.0% |
| Dead-drop birth-cohort harvest (%) | 101-300 | 39.946 | 55.821 | 43.127 | 64.095 | 40.646 | 55.885 | 15/19 | +27.3% |
| Split frequency (/1k turns) | 101-300 | 20.805 | 28.019 | 22.979 | 24.349 | 21.072 | 28.904 | 17/19 | +27.1% |
| Portal-required birth-cohort harvest (%) | 0-100 | 55.988 | 60.546 | 49.113 | 67.988 | 47.999 | 64.643 | 10/13 | +25.7% |
| Birth-cohort harvest (%) | 101-300 | 40.495 | 56.270 | 42.823 | 65.877 | 42.377 | 56.496 | 15/19 | +25.0% |
| Natural birth-cohort harvest (%) | 101-300 | 40.984 | 56.693 | 42.537 | 67.384 | 43.548 | 57.070 | 15/19 | +23.7% |
| Cross-team head-on involvement (/1k turns) | 101-300 | 4.469 | 6.492 | 6.921 | 2.967 | 5.061 | 6.570 | 15/19 | +23.0% |
| Queen dies in window (%) | 101-300 | 57.188 | 41.962 | 49.749 | 28.205 | 67.634 | 53.334 | 3/19 | -21.1% |
| Queen death: head-on mover (%) | 101-300 | 2.556 | 1.362 | 2.261 | 10.256 | 1.790 | 2.111 | 4/19 | +15.2% |

## Where we differ most from rank-1

- 0-100: A dragon of theirs dies after an illegal split more often than ours (+100.0%); fields: `ranges.0-100.deaths.illegal split`, `ranges.0-100.turns`.
- 101-300: A dragon of theirs dies after an illegal split more often than ours (+100.0%); fields: `ranges.101-300.deaths.illegal split`, `ranges.101-300.turns`.
- 0-100: A dragon of theirs dies by hitting a wall less often than ours (-100.0%); fields: `ranges.0-100.deaths.wall`, `ranges.0-100.turns`.
- 101-300: A dragon of theirs dies by hitting a wall less often than ours (-100.0%); fields: `ranges.101-300.deaths.wall`, `ranges.101-300.turns`.
- 0-100: A dragon of theirs dies by hitting its own body less often than ours (-99.8%); fields: `ranges.0-100.deaths.own body`, `ranges.0-100.turns`.
- 101-300: A dragon of theirs dies by hitting its own body less often than ours (-99.8%); fields: `ranges.101-300.deaths.own body`, `ranges.101-300.turns`.
- 0-100: A dragon of theirs dies by hitting another dragon’s body less often than ours (-84.2%); fields: `ranges.0-100.deaths.another body`, `ranges.0-100.turns`.
- 101-300: A dragon of theirs dies by hitting another dragon’s body less often than ours (-80.6%); fields: `ranges.101-300.deaths.another body`, `ranges.101-300.turns`.
- 101-300: A dragon of theirs initiates a head-on collision and dies more often than ours (+52.5%); fields: `ranges.101-300.deaths.head-on mover`, `ranges.101-300.turns`.
- 101-300: A dragon of theirs starts head-on meetings more often than ours (+52.5%); fields: `ranges.101-300.deaths.head-on mover`, `ranges.101-300.turns`.
- 0-100: A dragon of theirs initiates a head-on collision and dies more often than ours (+48.8%); fields: `ranges.0-100.deaths.head-on mover`, `ranges.0-100.turns`.
- 0-100: A dragon of theirs starts head-on meetings more often than ours (+48.8%); fields: `ranges.0-100.deaths.head-on mover`, `ranges.0-100.turns`.

## Where we already match

- 0-100 (|shared gap| <10%): Blind successful movement (-0.8%); Tiles visited per 20-round dragon block (-3.4%); Board seen by endpoint (+3.4%).
- 101-300 (|shared gap| <10%): Blind successful movement (-1.0%); Tiles visited per 20-round dragon block (-3.7%); Board seen by endpoint (+1.8%).
- game / r50 / r100 (|shared gap| <10%): Heads in enemy half [r100] (+4.6%); Portal steps [game] (-1.1%); Splits per eaten pearl [game] (-5.2%); Queen dies before game end [game] (-6.8%).

Re-run from the repository root: `nice -n 10 python3 -B data/analysis/ladder/dossier/work/tg_run.py`.
