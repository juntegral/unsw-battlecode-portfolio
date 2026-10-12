# Analyst: unseen

Read `data/codex/astra/ASTRA-COMMON.md` first; your name is `unseen`.

Question: the qualifier (today) is a best of seven on maps nobody has seen. What in our live bot can break or go blind on a map
that differs from the 15 ladder maps? This is a code audit against the engine's real limits, not a replay count.
Sources: bot `data/online/smoke/one5-bot/main.cpp` (+ `helper.hpp`, `sonar_codec.hpp`); engine and rules `~/meow-redteam/engine*`,
`~/meow-redteam/README.md`, `~/meow-redteam/docs/`; maps `~/meow-redteam/maps/{ladder,dev,eval}/*.map` and the ladder map list
`data/analysis/ladder/maps.json`.
1. From the engine: the legal range of a map (width, height, cells, torus or not, symmetry kinds, portals, kelp walls on edges,
   pearl tiles and their timers, number and length of starting dragons, where the queen starts, round limit, time and memory
   limits per turn). Then the range actually covered by the 15 ladder maps. The gap between the two is what an unseen map can be.
2. Every assumption in the bot that is narrower than the engine allows, with lines: fixed array sizes, bit packing of cell indexes
   (for example `& 0xFFF` near line 1793 packs 12 bits = 4096 cells: what happens at 4097 or with width over 64?), size thresholds
   (600, 1200 cells and any other constant compared with cells, width or height), symmetry inference (`fill_from_mirror`,
   `sym_fixed`: what if the map has another symmetry or none, or the guess is wrong), portal handling, sonar codec ranges,
   anything keyed to a start layout (queen length 4, two dragons), per-turn time on the largest legal map with the unit cap reached.
   For each: what goes wrong (crash, illegal action, silent wrong behaviour, timeout), how likely, and the smallest fix.
3. Write test maps that hit each risk into `data/codex/astra/unseen/maps/` in the engine's map format (copy the format from the
   existing maps exactly; check each file loads with the engine's own map loader if you can run it; say so if you cannot).
   The lead will play the live bot on them. Name them `un_<risk>_<n>.map`.
4. Report: the risks ranked by (chance on an unseen map) x (damage), each with its test map and its fix. Fixes that are one or two
   lines and cannot change play on the 15 known maps go first.
