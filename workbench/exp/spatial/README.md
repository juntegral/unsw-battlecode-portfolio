# Spatial occupancy study

The frozen game-key manifest is committed as `population.keys.json`. Full metadata and per-game evidence are in `cache/population.json` and `cache/games.jsonl`.
The cache is ignored by Git; do not replace it with a sample. Rows are append-only and versioned;
all readers deduplicate by game key, retaining the latest row. `schemaVersion: 2` adds tile-level
counts and sustained stays near pocket mouths.

Primary extraction uses `mass_ledger.perGame` hooks. The independent `recount.js` follows replay
head/tail updates and `tileChange` under the current actor. `recount_park.js` separately checks
the sustained-stay metric. The only common reconstruction dependency is the validated binary
decoder. Check `verification.json` and `park-verification.json` before interpreting output.

`tables.json` is the machine interface. Its `definitions` specify denominators and orientation.
Arrays have five frontier bins plus an explicit sixth bin for tiles unreachable from both starts.
Checkpoint N is conditional on the game reaching that round. Fountain groups overlap: never
sum their yield, intake or staffing as though they were a disjoint partition.

Each map/layout has:

- `classes`: elite winners/losers, all our version families, individual sets, and local families;
  raw counts, exposure, phase/checkpoint shares, intake/death rates, holds, staffing and sd targets.
- `groups`: unique radius-3 fountain sets, observed yield, coordinates, f, pocket flags and holds.
- `pocketFountains`, `pockets`: individual harvesting counts, pearl presence, entrances and topology.
- `spawnTiles`, `spawnTileCounts`: all natural spawn tiles, including slow supply on maps with no fountains.
- `safeSpawnCandidateGroups`: safe radius-3 supply candidates weighted by observed respawns/round.
- `recommendedHeadAllocation`, `targetRules`: observational implementation hypotheses, not tested bot results.

`node eval/spatial_report.js <set name/dir or local exp dir>` is read-only and recomputes directly.
The original Slithery diagnostic is reproduced with:

```sh
node eval/spatial_report.js exp/v1/v1-a-px4/games/proxy4_king_slithery_fight_A_1
```

The Korean report is `research/observations/spatial-occupancy.md`. Reproduction commands are there.
Run `node exp/spatial/summary.js` only after checks and report validation; `SUMMARY.txt` is written last.
