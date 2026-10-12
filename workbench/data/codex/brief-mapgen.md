# Worker: mapgen

Read `data/codex/astra/ASTRA-COMMON.md` (sections Game, Data, Rules) first; your name is `mapgen`; write only under
`data/codex/astra/mapgen/`.

Task: the qualifier is played on unseen maps. Build a set of 64 new maps so the lead can play the live bot on ground it has never
been tuned on. No analysis, no card.
1. Learn the format and the legal ranges from `~/meow-redteam/maps/{ladder,dev,eval}/*.map` and the engine's map loader under
   `~/meow-redteam/engine*`. Tabulate the 15 ladder maps (`maps/ladder` and `data/analysis/ladder/maps.json`): width, height,
   cells, symmetry, share of kelp, portals, pearl tiles and their timers, starting dragons per side with lengths, distance
   between the two sides' starts. Write the table to `ladder-params.md`.
2. Write `gen.py` (seeded, deterministic) and generate into `maps/` 64 maps named `gx_<family>_<size>_<seed>.map`:
   8 families x 8 maps. Families: open field, rooms with doors, long corridors and dead ends, islands joined by portals, a ring
   or donut, diagonal or rotational symmetry (if the engine allows it), pearl-poor (few bearing tiles, long timers), pearl-rich.
   Within each family spread sizes from the smallest legal map to the largest legal one including non-square shapes (wide, tall),
   and vary the start: both start layouts seen on the ladder (a 4-long queen alone; two dragons) plus any other legal start the
   ladder uses. Half of the maps inside the ladder's parameter range, half outside it but legal.
3. Validate every map: it loads with the engine's loader, both sides are mirror images under the stated symmetry, every start can
   reach a pearl tile, no start is boxed in. Write `maps/INDEX.tsv` (name, family, w, h, cells, symmetry, portals, bearing tiles,
   start layout, inside/outside ladder range) and `done.txt` with what you could not validate.
You cannot play games on this machine; do not try.
