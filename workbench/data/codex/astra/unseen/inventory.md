[M] Live 15-map list: `data/online/smoke/one5-w1.json`; `maps.json` has 19 historical name/version entries, so using all 19 as the current ladder is wrong.
[M] Exact initializer data below comes from local ladder files, plus installed engine templates where a ladder copy is absent. The replay index dragon count is per side; its pearl-bed counts sometimes differ from local initializers. Both sources are retained in JSON.

| Map | Size/cells | Sym | Starters A/B | Queen lengths | All start lengths | Pearl beds; gap min/max | Portal pairs; max ID | Seam kelp |
|---|---|---|---|---|---|---|---|---|
| weakhold | 40×15 / 600 | xy | [2, 2] | [4, 4] | [4, 4] | 76; [1, 500] | 0; — | 55 |
| Australia | 64×64 / 4096 | xy | [9, 9] | [4, 4] | [2, 4] | 338; [1, 2000] | 4; 3 | 12 |
| Islands | 56×40 / 2240 | y | [5, 5] | [3, 3] | [2, 3] | 330; [1, 2559] | 12; 11 | 3 |
| Maze | 48×24 / 1152 | xy | [2, 2] | [4, 4] | [4, 4] | 350; [1, 1000] | 16; 15 | 72 |
| Stripes | 24×12 / 288 | xy | [2, 2] | [2, 2] | [2, 2] | 70; [1, 500] | 8; 7 | 22 |
| Tower Defense | 32×16 / 512 | xy | [2, 2] | [2, 2] | [2, 2] | 150; [1, 500] | 0; — | 38 |
| Around UNSW | 64×64 / 4096 | xy | [10, 10] | [4, 4] | [2, 10] | 288; [1, 1000] | 4; 3 | 10 |
| Default | 32×32 / 1024 | xy | [4, 4] | [4, 4] | [4, 4] | 1024; [1, 3849] | 12; 11 | 4 |
| Queen Of Spades | 25×35 / 875 | xy | [2, 2] | [3, 3] | [3, 3] | 442; [1, 1000] | 2; 1 | 0 |
| Schooltime | 60×40 / 2400 | y | [3, 3] | [4, 4] | [4, 4] | 326; [1, 200] | 12; 11 | 60 |
| Trophy | 25×25 / 625 | y | [2, 2] | [3, 3] | [3, 3] | 547; [1, 1000] | 1; 0 | 0 |
| Devil | 32×16 / 512 | y | [3, 3] | [4, 4] | [4, 4] | 174; [1, 600] | 0; — | 40 |
| Trauma | 48×24 / 1152 | xy | [2, 2] | [4, 4] | [4, 4] | 142; [1, 200] | 6; 5 | 72 |
| Portals | 32×16 / 512 | xy | [3, 3] | [3, 3] | [3, 3] | 104; [1, 10] | 20; 19 | 48 |
| Slithery Fight | 63×27 / 1701 | xy | [7, 7] | [25, 25] | [2, 25] | 497; [1, 755] | 2; 1 | 90 |

[M] Local ladder ranges: {'width': [24, 64], 'height': [12, 64], 'cells': [288, 4096], 'queen_distance': [2, 44]}

[M] Read-only held-out geometry: {'maps': 24, 'width': [16, 63], 'height': [10, 59], 'cells': [170, 3477]}

[M] Every inventoried ladder/held-out file has unit limit 64 and declared x/y/xy symmetry; no tested local ladder portal ID reaches 2*cells.
