# Card 47 third build: 45 online games, 7 Oct 2026

Each set has 15 maps against Big Bobs Bots (946); our side is read from team 1119 in each game. These are unpaired games: build effects and opponent variation/luck are mixed.
Definitions reuse card_47_check.py: room ≤31, no portal, one gate; wasted = <2 growth-counted pearls then split/died inside; charged uses its 25-round pearl-count proxy, not bot-state inspection; enemy near = wrapped 3-tile square. Ray hits proxy hearing; receptions count first dragon/end pairs; babies born on a named tile are excluded. Alive checkpoints after an early finish carry the final state; safe move means a non-kelp step to an unoccupied tile, including portals; no action includes explicit suicide.
## A. Job (totals unless labelled)

| Measure | new | main48 | main47 |
|---|---:|---:|---:|
| Dragon turns | 136501 | 145643 | 173836 |
| Dead-end stays / with alert (incl. split ping) | 557 / 529 | 438 / 0 | 484 / 0 |
| Inside turns / alerted; non-split alerts / own-end split pings | 2020 / 1811; 1347 / 495 | 1812 / 0; 0 / 0 | 1988 / 0; 0 / 0 |
| End packets / true; end rays / teammate hits | 3901 / 3901; 15332 / 3277 | 0 / 0; 0 / 0 | 0 / 0; 0 / 0 |
| Passed on: relay turns / relay rays heard | 1113 / 1301 | 0 / 0 | 0 / 0 |
| First dead-end receptions (dragon/end pairs) | 1568 | 0 | 0 |
| told arrivals / entered / share | 646 / 150 / 23.2% | 0 / 0 / — | 0 / 0 / — |
| untold arrivals / entered / share | 2944 / 284 / 9.6% | 3534 / 378 / 10.7% | 4322 / 421 / 9.7% |
| told-charged arrivals / entered / share | 495 / 57 / 11.5% | 0 / 0 / — | 0 / 0 / — |
| Charged entries with enemy head within 3 | 7 | 0 | 0 |
| Wasted stays / per 1,000 dragon turns | 85 / 0.623 | 110 / 0.755 | 144 / 0.828 |
| Pearls eaten on stays / length lost at deaths inside | 1434 / 1157 | 1193 / 938 | 1314 / 1027 |
| Trapped mother splits / those naming refill tiles | 414 / 144 | 320 / 0 | 342 / 0 |
| Refill tiles named at split / split+resends / told to babies | 234 / 234 / 162 | 0 / 0 / 0 | 0 / 0 / 0 |
| Babies told / reached ≤30 rounds / pearls there | 102 / 4 / 7 | 0 / 0 / 0 | 0 / 0 / 0 |
| Refill message turns from trapped mothers / all; unflagged tiles | 144 / 144; 0 | 0 / 0; 0 | 0 / 0; 0 |
## B. Downsides (per-game means; death cells = mean / pooled per 1,000 turns)

| Measure | new | main48 | main47 |
|---|---:|---:|---:|
| Results W/D/L (counts) | 5/0/10 | 4/0/11 | 7/0/8 |
| Endings elimination / round limit (counts) | 5 / 10 | 4 / 11 | 4 / 11 |
| Pearls by r100 / r300 | 107.07 / 362.40 | 114.13 / 426.27 | 125.00 / 436.13 |
| Alive at r100 / r200 / r300 | 23.13 / 30.60 / 26.60 | 24.13 / 32.27 / 29.93 | 26.73 / 33.80 / 33.93 |
| Death: wall | 63.93 / 7.026 | 71.93 / 7.409 | 73.73 / 6.362 |
| Death: own body | 27.07 / 2.974 | 34.73 / 3.577 | 37.27 / 3.216 |
| Death: another body | 27.73 / 3.048 | 26.47 / 2.726 | 37.87 / 3.267 |
| Death: head-on mover | 12.40 / 1.363 | 12.93 / 1.332 | 13.20 / 1.139 |
| Death: head-on hit | 37.40 / 4.110 | 37.13 / 3.824 | 40.20 / 3.469 |
| Death: no action | 20.60 / 2.264 | 25.93 / 2.671 | 33.33 / 2.876 |
| Deaths: timeout; unpaid sprint; illegal split | 0.00 / 0.000; 0.00 / 0.000; 0.00 / 0.000 | 0.00 / 0.000; 0.00 / 0.000; 0.00 / 0.000 | 0.00 / 0.000; 0.00 / 0.000; 0.00 / 0.000 |
| Timeout turns / no-action turns / either with safe move | 0.00 / 20.60 / 19.47 | 0.00 / 25.93 / 24.53 | 0.00 / 33.33 / 32.33 |
| Sonar rays: leader / new kind | 33152.87 / 1022.13 | 35315.67 / 0.00 | 41370.00 / 0.00 |
| Other rays: mouth / queen / other / unreadable | 1346.47 / 271.87 / 0.00 / 0.00 | 1173.93 / 1660.53 / 0.00 / 0.00 | 1823.33 / 2381.33 / 0.00 / 0.00 |
| Queen alive at end (mean indicator) / longest at end | 0.200 / 23.33 | 0.267 / 23.53 | 0.133 / 32.07 |
## C. Per map (new / main48)

| Map | Result | Pearls r100 | Wasted stays | Deaths in dead ends |
|---|---|---:|---:|---:|
| weakhold | W / L | 69 / 39 | 14 / 7 | 102 / 84 |
| Australia | L / L | 43 / 116 | 16 / 11 | 39 / 22 |
| Islands | L / L | 226 / 213 | 11 / 7 | 31 / 14 |
| Maze | L / L | 70 / 70 | 16 / 29 | 109 / 126 |
| Stripes | W / L | 40 / 9 | 0 / 0 | 21 / 0 |
| Tower Defense | L / L | 4 / 3 | 0 / 0 | 0 / 1 |
| Around UNSW | L / L | 160 / 169 | 1 / 7 | 30 / 55 |
| Default | L / L | 61 / 22 | 0 / 0 | 0 / 0 |
| Queen Of Spades | W / W | 41 / 45 | 6 / 11 | 6 / 11 |
| Schooltime | W / L | 139 / 19 | 3 / 3 | 7 / 2 |
| Trophy | W / W | 123 / 128 | 0 / 0 | 0 / 0 |
| Devil | L / W | 39 / 210 | 0 / 0 | 0 / 0 |
| Trauma | L / W | 5 / 19 | 6 / 2 | 35 / 37 |
| Portals | L / L | 54 / 257 | 0 / 4 | 1 / 34 |
| Slithery Fight | L / L | 532 / 393 | 12 / 29 | 149 / 42 |
## What the counts say

Alerts appear on 529 of 557 stays, all 3,901 dead-end packets describe real dead ends, 3,277 rays hit teammates, and 1,113 relay turns show passing on.
Charged dragons enter on 57 of 495 arrivals (11.5%), against 284 of 2,944 untold arrivals (9.6%), so lower entry by charged dragons does not show, while wasted stays per 1,000 turns are 0.623 versus 0.755 and 0.828 in the two earlier sets.
All 144 refill-message turns come from trapped splits, 102 told babies produce four reaches and seven pearls on named tiles, and one reach starts 13 tiles away, but the replay cannot establish the baby’s motive or whether nothing else was in reach.
Using |new − main48| > |main48 − main47| as the requested luck scale, the per-game measures beyond it are pearls by r300 (down 63.87 versus spread 9.87), alive at r200 (down 1.67 versus 1.53), wall deaths (down 8.00 versus 1.80), own-body deaths (down 7.67 versus 2.53), mover head-on deaths (down 0.53 versus 0.27), queen rays (down 1,388.67 versus 720.80), new-kind rays (up 1,022.13 versus zero), and elimination endings (five versus four and four, with round-limit endings falling from eleven to ten).
For pooled deaths per 1,000 turns, only own-body deaths (down 0.603 versus spread 0.362) and no-action deaths (down 0.407 versus 0.205) move beyond that scale.
Results, pearls by r100, alive at r100 and r300, queen survival, final longest, leader and mouth rays, no-action and safe-move failure turns, and all other listed death measures stay within the reference spread; unpaired opponent behavior prevents attributing these differences to the build.
