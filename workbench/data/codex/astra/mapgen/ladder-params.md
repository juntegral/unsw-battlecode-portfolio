# Ladder parameters

The current 15-name roster is read from `data/online/smoke/one5-w1.json` (offline). `maps.json` contains 19 historical variants; Autarky and Prisoners Dilemma are absent from this roster. Schooltime has two historical variants; the first stored variant is tabulated.

Source preference: the 9 files in `~/meow-redteam/maps/ladder` (8 distinct names), then installed engine 1.2.7 bundled maps. Each row links its actual source below. Ladder reconstructions may have estimated pearl timers; bundled maps supply exact local configuration, not verified current server timers.

Cells = width × height; kelp share = closed canonical torus edges / (2 × cells); portals = pairs; timers = min..max:number of bearing tiles; starts list lengths in queen-first order per side. Distance is minimum traversable head-to-head steps including portal routing; queen torus distance is also shown. Neither distance counts starting bodies as obstacles. None means the starts are disconnected. The additional historical column quotes maps.json bearing counts and queen torus distance; it is not substituted for the local map configuration.

| Name | W | H | Cells | Symmetry | Kelp share | Portal pairs | Bearing tiles / timers | Starts A / B | Start distance / queen torus | maps.json bearing / queen distance |
|---|---:|---:|---:|---|---:|---:|---|---|---|---|
| weakhold | 40 | 15 | 600 | xy | 0.254167 | 0 | 76; 1..1:22; 1..100:24; 1..250:2; 1..500:28 | [4, 4] / [4, 4] | 73 / 12 | 76 / 12 |
| Australia | 64 | 64 | 4096 | xy | 0.079102 | 4 | 338; 1..10:36; 1..200:62; 1..2000:112; 100..500:22; 40..200:104; 8..30:2 | [4, 4, 2, 2, 2, 2, 3, 4, 3] / [4, 4, 2, 2, 2, 2, 3, 4, 3] | 12 / 40 | 338 / 40 |
| Islands | 56 | 40 | 2240 | y | 0.226339 | 12 | 330; 1..1:20; 1..10:8; 1..200:58; 1..2559:244 | [3, 3, 2, 2, 2] / [3, 3, 2, 2, 2] | 5 / 21 | 330 / 21 |
| Maze | 48 | 24 | 1152 | xy | 0.269097 | 16 | 350; 1..1:30; 1..100:2; 1..1000:52; 1..200:198; 1..500:20; 10..30:20; 250..500:28 | [4, 4] / [4, 4] | 43 / 16 | 350 / 16 |
| Stripes | 24 | 12 | 288 | xy | 0.267361 | 8 | 70; 1..1:12; 1..10:16; 1..500:42 | [2, 2] / [2, 2] | 14 / 8 | 70 / 8 |
| Tower Defense | 32 | 16 | 512 | xy | 0.285156 | 0 | 150; 1..1:4; 1..100:60; 1..500:48; 250..500:16; 400..500:22 | [2, 2] / [2, 2] | 72 / 18 | 150 / 18 |
| Around UNSW | 64 | 64 | 4096 | xy | 0.104736 | 4 | 288; 1..1:22; 1..10:8; 1..100:52; 1..1000:82; 1..30:28; 1..500:26; 10..30:34; 250..500:36 | [4, 4, 2, 2, 2, 2, 3, 4, 3, 10] / [4, 4, 2, 2, 2, 2, 3, 4, 3, 10] | 29 / 44 | 290 / 44 |
| Default | 32 | 32 | 1024 | xy | 0.107422 | 12 | 1024; 1..255:58; 1..3849:762; 1..385:76; 1..769:128 | [4, 4, 4, 4] / [4, 4, 4, 4] | 6 / 2 | 1021 / 2 |
| Queen Of Spades | 25 | 35 | 875 | xy | 0.169143 | 2 | 442; 1..1000:410; 1..50:32 | [3, 3] / [3, 3] | 24 / 23 | 472 / 23 |
| Schooltime | 60 | 40 | 2400 | y | 0.192708 | 12 | 178; 20..200:158; 20..50:18; 20..80:2 | [4, 4, 4] / [4, 4, 4] | 13 / 7 | 178 / 7 |
| Trophy | 25 | 25 | 625 | y | 0.073600 | 1 | 547; 1..100:47; 1..1000:489; 5..30:11 | [3, 3] / [3, 3] | 9 / 9 | 547 / 9 |
| Devil | 32 | 16 | 512 | y | 0.238281 | 0 | 174; 1..1:18; 1..150:16; 1..30:12; 1..300:64; 1..600:64 | [4, 4, 4] / [4, 4, 4] | 31 / 7 | 176 / 7 |
| Trauma | 48 | 24 | 1152 | xy | 0.244792 | 6 | 142; 1..1:12; 1..200:130 | [4, 4] / [4, 4] | 98 / 16 | 142 / 16 |
| Portals | 32 | 16 | 512 | xy | 0.279297 | 20 | 104; 1..1:8; 1..10:96 | [3, 3, 3] / [3, 3, 3] | None / 6 | 104 / 6 |
| Slithery Fight | 63 | 27 | 1701 | xy | 0.151088 | 2 | 497; 1..1:18; 1..10:32; 1..20:2; 1..5:58; 1..500:43; 1..755:306; 100..300:12; 100..500:26 | [25, 7, 4, 2, 5, 2, 2] / [25, 7, 4, 2, 5, 2, 2] | 4 / 16 | 497 / 16 |

## Sources

- weakhold: `~/meow-redteam/engine/venv/lib/python3.13/site-packages/unswbc/templates/maps/weakhold.map`
- Australia: `~/meow-redteam/maps/ladder/ladder_australia_1.map`
- Islands: `~/meow-redteam/maps/ladder/ladder_islands_1.map`
- Maze: `~/meow-redteam/engine/venv/lib/python3.13/site-packages/unswbc/templates/maps/maze.map`
- Stripes: `~/meow-redteam/maps/ladder/ladder_stripes_1.map`
- Tower Defense: `~/meow-redteam/maps/ladder/ladder_tower_defense_1.map`
- Around UNSW: `~/meow-redteam/maps/ladder/ladder_around_unsw_1.map`
- Default: `~/meow-redteam/engine/venv/lib/python3.13/site-packages/unswbc/templates/maps/default.map`
- Queen Of Spades: `~/meow-redteam/engine/venv/lib/python3.13/site-packages/unswbc/templates/maps/queen_of_spades.map`
- Schooltime: `~/meow-redteam/maps/ladder/ladder_schooltime_1.map`
- Trophy: `~/meow-redteam/engine/venv/lib/python3.13/site-packages/unswbc/templates/maps/trophy.map`
- Devil: `~/meow-redteam/engine/venv/lib/python3.13/site-packages/unswbc/templates/maps/devil.map`
- Trauma: `~/meow-redteam/engine/venv/lib/python3.13/site-packages/unswbc/templates/maps/trauma.map`
- Portals: `~/meow-redteam/maps/ladder/ladder_portals_1.map`
- Slithery Fight: `~/meow-redteam/maps/ladder/ladder_slithery_fight_1.map`

## Measured envelope

```json
{
  "w": [
    24,
    64
  ],
  "h": [
    12,
    64
  ],
  "cells": [
    288,
    4096
  ],
  "kelp": [
    0.0736,
    0.28515625
  ],
  "portals": [
    0,
    20
  ],
  "bearing_share": [
    0.0703125,
    1.0
  ],
  "start_distance": [
    4,
    98
  ],
  "timer_lo": [
    1,
    400
  ],
  "timer_hi": [
    1,
    3849
  ],
  "start_lengths": [
    2,
    3,
    4,
    5,
    7,
    10,
    25
  ],
  "start_count": [
    2,
    10
  ]
}
```

`inside` means every numeric dimension above is within its marginal ladder bounds; start lengths belong to the observed set. It does not mean the joint geometry occurred on the ladder. `outside` means at least one dimension is outside. Symmetries x, y, xy are all observed.

The brief additionally requests a lone length-4 queen. This layout is legal but is not present among these 15 local ladder configurations; it is included as outside-range coverage.

## Loader rules

Installed engine: `~/meow-redteam/engine/venv/.../unswbc/engine.py` and `unswbc_engine.wasm` (1.2.7). The wheel exposes `ubc_run`, not a separate parse function. `loader_check.py` aborts at the first spawn callback, after loading and before any turn/reply. No bot process exists.

Loader dimension probes establish each side in 7..256 inclusive; 6 is rejected with “map must be at least 7x7”, 257 with “map must be at most 256x256”. SYMMETRY accepts x (top/bottom), y (left/right), xy (180-degree rotation); diagonal declarations are unsupported. EDGE kind 0=open, 1=kelp, 2=paired portal; EDGE indices use alternating horizontal/vertical rows of width W+1, with torus aliases. TILE records contain coordinates and positive ordered respawn bounds or 0 0. DRAGON teams alternate, segments are head-first, minimum length 2. Generator writes all tiles, non-open canonical edges, all dragons, and END. Generated timer/length values are validated by the loader rather than assumed to be exhaustive engine limits.
