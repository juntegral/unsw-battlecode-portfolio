# Card 48 v1: 15 old + 15 new online games

Raw rounds; snapshots after the named round. Unreached state markers are null, and means use reached games (n shown); dead queens are 0. Cumulative pearls/splits include every game through the marker or its earlier end. Means rounded to two decimals.
Late-death context (r300 onward): collision dragon, otherwise nearest head by traversable path including portals; all nearest ties retained, yes if any is our longest (length ties count). Lengths are immediately before the death; paired head-on deaths are treated together.

## A. Set totals and means

| Set | Games | W/L/D | Endings: elimination / longer queen / longest dragon / total length / draw | Mean last round |
|---|---:|---|---|---:|
| old | 15 | 7/8/0 | 4 / 9 / 2 / 0 / 0 | 403.53 |
| new | 15 | 4/11/0 | 4 / 7 / 4 / 0 / 0 | 417.80 |

| Set / side | Queen alive end mean | Queen death round / length means (n) | Late death: own-longest yes / n; candidate length mean | Queen length r100 / r200 / r300 / r400 / end | Longest r300 / r400 / end | Alive r300 / r400 / end | Total end | Pearls ≤r100 / ≤r300 | Splits ≤r100 | Queen split turns |
|---|---:|---|---|---|---|---|---:|---|---:|---:|
| old / us | 0.13 | 122.85 (n=13) / 2.77 (n=13) | 0/1; 2.00 | 1.00 (n=15) / 1.00 (n=11) / 0.82 (n=11) / 3.55 (n=11) / 3.73 | 10.36 (n=11) / 19.27 (n=11) / 32.07 | 37.00 (n=11) / 33.45 (n=11) / 22.40 | 110.00 | 125.00 (n=15) / 436.13 (n=15) | 53.80 | 3.13 |
| old / them | 0.60 | 168.17 (n=6) / 5.00 (n=6) | 0/1; 3.00 | 2.13 (n=15) / 2.64 (n=11) / 2.55 (n=11) / 7.45 (n=11) / 13.67 | 6.73 (n=11) / 12.91 (n=11) / 21.73 | 44.00 (n=11) / 41.45 (n=11) / 15.20 | 85.60 | 123.87 (n=15) / 531.67 (n=15) | 44.60 | 6.33 |
| new / us | 0.27 | 131.18 (n=11) / 2.36 (n=11) | 0/0; — | 2.00 (n=15) / 0.83 (n=12) / 0.67 (n=12) / 2.91 (n=11) / 3.67 | 8.92 (n=12) / 15.36 (n=11) / 23.53 | 28.50 (n=12) / 23.18 (n=11) / 15.87 | 78.80 | 114.13 (n=15) / 426.27 (n=15) | 49.93 | 4.33 |
| new / them | 0.53 | 148.71 (n=7) / 2.14 (n=7) | 0/1; 5.00 | 1.80 (n=15) / 2.08 (n=12) / 2.00 (n=12) / 4.82 (n=11) / 7.20 | 6.17 (n=12) / 10.82 (n=11) / 19.93 | 40.67 (n=12) / 41.09 (n=11) / 24.67 | 115.53 | 108.93 (n=15) / 470.40 (n=15) | 41.00 | 6.47 |

## B. Queen deaths (counts)

| Cause or round band | Ours old | Ours new | Theirs old | Theirs new |
|---|---:|---:|---:|---:|
| head-on mover | 2 | 1 | 0 | 2 |
| head-on hit | 8 | 6 | 5 | 4 |
| wall | 1 | 3 | 1 | 1 |
| own body | 2 | 0 | 0 | 0 |
| another body | 0 | 1 | 0 | 0 |
| no action | 0 | 0 | 0 | 0 |
| unpaid sprint | 0 | 0 | 0 | 0 |
| illegal split | 0 | 0 | 0 | 0 |
| timeout | 0 | 0 | 0 | 0 |
| 0–100 | 9 | 3 | 2 | 4 |
| 101–300 | 3 | 8 | 3 | 2 |
| 301–499 | 1 | 0 | 1 | 1 |

## C. Per map (our side; old → new)

| Map | Result | Queen end/death | Longest end | Alive r400 |
|---|---|---|---|---|
| weakhold | loss → loss | r66 own body → r105 head-on hit | 2 → 10 | 8 → 12 |
| Australia | loss → loss | r91 head-on hit → r113 wall | 43 → 21 | 33 → 9 |
| Islands | loss → loss | r170 head-on hit → r139 head-on hit | 86 → 18 | 54 → 11 |
| Maze | loss → loss | r90 head-on hit → r155 another body | 26 → 70 | 47 → 55 |
| Stripes | win → loss | r89 own body → r84 head-on hit | 3 → 0 | unreached → unreached |
| Tower Defense | loss → loss | r320 head-on hit → r204 wall | 20 → 13 | 2 → 4 |
| Around UNSW | loss → loss | r139 head-on hit → r72 head-on mover | 20 → 53 | 35 → 54 |
| Default | win → loss | r89 head-on hit → r109 head-on hit | 43 → 0 | 53 → unreached |
| Queen Of Spades | win → win | r64 head-on mover → r64 head-on hit | 4 → 35 | unreached → 18 |
| Schooltime | win → loss | alive L3 → alive L3 | 101 → 4 | 55 → 2 |
| Trophy | win → win | r62 head-on mover → alive L3 | 4 → 3 | unreached → unreached |
| Devil | win → win | r78 head-on hit → alive L3 | 4 → 4 | unreached → unreached |
| Trauma | win → win | alive L53 → alive L46 | 53 → 46 | 9 → 10 |
| Portals | loss → loss | r40 wall → r115 wall | 20 → 42 | 20 → 25 |
| Slithery Fight | loss → loss | r299 head-on hit → r283 head-on hit | 52 → 34 | 52 → 55 |

## D. Count differences

Neither set records a late queen death into our longest dragon: old has one death from r300 onward (Tower Defense r320, hit by an enemy L2), new has none. Our queens alive at the end rose from 2/15 to 4/15 (two games), theirs fell from 9/15 to 8/15 (one game), and our queen deaths at r0–100 fell from 9 to 3 while deaths at r101–300 rose from 3 to 8. Results stayed the same on 12 maps; Stripes, Default and Schooltime changed from win to loss, with no loss-to-win changes; elimination endings stayed at 4/15, while longest-dragon endings rose from 2 to 4 and longer-queen endings fell from 9 to 7 (two games each). Our per-game means changed from 125.00 to 114.13 pearls by r100, 436.13 to 426.27 by r300, 53.80 to 49.93 splits by r100, 3.13 to 4.33 queen split turns, and 32.07 to 23.53 longest length at the end.
