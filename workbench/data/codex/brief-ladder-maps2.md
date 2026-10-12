# Fix the six ladder maps: they have no pearl spawning

`data/analysis/ladder/dossier/local/maps/ladder_*.map` (your earlier output, see its README.md) carry `TILE x y 0 0`
on every tile, because ladder replays store 0 0 there. Played locally, no pearl ever appears: games on them are
useless. The real layouts spawn pearls on fixed tiles (`data/analysis/ladder/maps.json` counts `pearl_tiles` and
`fast_tiles` per layout from observed births; the dossier scripts `dossier/count_dossier.py` and
`dossier/work/isl_map.py` identify natural births in ladder replays).

## Job
1. Learn exactly what the two TILE numbers mean to the engine (min and max of the spawn interval: counted from
   what event, in rounds, inclusive or not, what happens while a pearl or a body is on the tile, when the first
   pearl comes). Sources: the engine in `~/meow-redteam/engine/` (python venv, the unswbc package
   and its WASM), `~/meow-redteam/docs/`, and the working maps in
   `~/meow-redteam/maps/dev/` whose TILE values are known. If the docs do not say, measure it:
   the venv python may load a known map and step the engine with no-op replies (as your verify_maps.py did).
2. For each of the six layouts, from EVERY ladder replay of that layout under `data/online/` (the 500 main games in
   `dossier/per-game.jsonl` and any others you find), estimate per tile the (min, max) the server uses, using the
   engine semantics from step 1 (gaps between the tile becoming free and the next natural birth, first-birth
   rounds, and so on). Use the symmetry of the layout to pool mirrored tiles. Tiles with no natural birth in any
   game stay 0 0. The known maps use a small set of values (for example 1 200, 1 300, 5 30, 1 150, 1 60): say whether
   the estimates fall on such a small set and snap to it only if the data clearly does.
3. Write the corrected maps to `data/analysis/ladder/dossier/local/maps2/ladder_<slug>.map` (everything else
   byte-identical to the maps in `maps/`).

## Check (required)
For each layout, with the venv engine and no-op bots (nobody moves, so nothing is eaten; if no-op bots die at once,
use a reply that keeps them alive or say what you did): the number of natural births per tile class in rounds
0-100 and 101-300 on your map, against the same count in the ladder replays restricted to tiles/rounds that are
comparable (say exactly how you made them comparable). Also total natural births per game in rounds 0-100.
Report ratio local / ladder per layout; it should be within 15 percent, and say so plainly where it is not.

## Output
`data/analysis/ladder/dossier/local/maps2/README.md` (40 lines or fewer): the engine semantics you established,
per layout the value classes with tile counts, and the check table. Then `maps2/done.txt` (one line) as the very
last step. Write only under `data/analysis/ladder/dossier/local/maps2/`. No network, no posts.
