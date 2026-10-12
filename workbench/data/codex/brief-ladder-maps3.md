# Three more ladder layouts as local maps, same method as before

You already did this for six layouts: read `data/analysis/ladder/dossier/local/maps/README.md` (extraction and
structure check) and `data/analysis/ladder/dossier/local/maps2/README.md` (pearl spawn intervals restored from
observed births), and reuse those scripts (`local/maps/verify_maps.py`, `local/maps2/*.py`). Do not redo the engine
semantics work; it is in `local/maps2/semantics.json`.

## Job
Produce, with exactly the same two steps and the same checks, maps for these ladder layouts:
Stripes #1, Portals #1, Tower Defense #1 (names as in `data/analysis/ladder/maps.json` and
`dossier/per-game.jsonl`). Use every ladder replay of each layout you can find under `data/online/`.
Write `data/analysis/ladder/dossier/local/maps3/ladder_<slug>.map` (structure exact, TILE intervals restored).
Stripes matters most: 86 percent of its pearls are born in small rooms behind portals (rooms of 1, 3 and 4 tiles),
so check those room tiles by hand in the output and list their intervals in the README.

## Output
`data/analysis/ladder/dossier/local/maps3/README.md` (30 lines or fewer): per map the size, dragons a side, the
interval classes with tile counts, the structure check against two replays, and the same calibrated birth check as
maps2 (ratio local / ladder for rounds 0-100 and 101-300, say plainly where it is outside 15 percent). For Stripes
also a small table: each portal room (tiles, loop or dead end) with the interval of its tiles.
Then `maps3/done.txt` (one line) as the very last step. Write only under
`data/analysis/ladder/dossier/local/maps3/`. No network, no posts.
