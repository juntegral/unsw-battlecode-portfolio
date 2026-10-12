# Codex brief: rebuild the 7 sprint-bracket maps from replays, validated on known maps (W5 / W8)

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. Read first:
- `AGENTS.md`.
- `docs/WORKQUEUE.md`, tasks W5 and W8.
- `rules/ALL.md` "# Map Files" (around line 1298), which defines the `.map` format.
- `tools/mapgen/lib.js`. It has the map model (`blank(W,H,symmetry,name)`, `tiles[k]=[minGap,maxGap]`, `edges[e]=[kind,portalId]` with e < W·H the north edge of tile k and e ≥ W·H the west edge, `dragons`), plus `parse`, `serialize`, `metrics`, `coreOf` and `graph`.
- `tools/mapgen/validate.js`.
- A first converter attempt: `/private/tmp/claude-501/-Users-jun-01--Project---------unsw-arena/ab529c8b-1bec-404e-b9b6-2b23c283b013/scratchpad/replay2map.js`.
  - It does **not** yet match the official files. On a Trophy replay it gets 625/625 tile gaps wrong (`pearlRespawn` gave [0,0] where the file has [1,1000]), 90 edge kinds wrong, and dragons unequal.

## Why
The qualifier is played on unseen custom maps. The sprint bracket (`node tools/online.js tournaments 1`) used 7 custom maps, each played once in every bo7 series: Australia (map id 29), Islands (30), Maze (31), Stripes (32), Tower Defense (33), Around UNSW (34) and weakhold (28).
- The server's `/maps` lists only the 10 active ladder maps, so these 7 exist only inside the replays.
- They are the best qualifier-like test maps we can get.
- The user saw they are structurally complex, with many 1-wide tunnels.

## Data
- `data/online/sprint-bracket/`: 224 games from 32 series, the round of 32 onward plus our own match.
  - Files: `M<gameId>.replay`, `game-<id>.json` (with `mapName`/`mapId`), `events-<id>.jsonl.gz`.
- Known-map replays for validation: `data/top/<battleId>/<gameId>.replay.gz` (see `data/top/index.jsonl`, field `map`).
- The official known map files are `maps/online-20260927/*.map` and `maps/server-b/*.map`. Layout variants a/b exist, so match each replay to the right file.

## Steps
1. **Build `tools/replay2map.js`.** It turns a replay's `match.map` (width, height, initialTiles, initialHEdges, initialVEdges, portals, initialDragons, pearlRespawn, symmetry, mapName) into a `.map` text.
   - Find the exact conventions:
     - edge index orientation (north/west vs south/east, wrap);
     - the meaning of `pearlRespawn`. If it isn't the spawn gap, recover `minGap`/`maxGap` from where the replay keeps them, for example the countdown events, or report that they are not recoverable;
     - dragon order;
     - portal ids.
2. **Validate on all 10 known maps (both layouts where they exist).**
   - Reconstruct from at least 2 replays per map and compare with the official file: tiles, edges, portals, dragons.
   - The known maps must match exactly. If spawn gaps truly can't be recovered from replays, say so, and give the rest exactly plus the best gap estimate with its method.
3. **Write the 7 custom maps** to `maps/sprint/<name>.map`. `MAP_NAME` is the original name.
   - Check that every game of the same map gives the same map.
   - Run `node tools/mapgen/validate.js maps/sprint`.
4. **Census of the 7 maps** with `lib.metrics`:
   - size, symmetry, kelp density;
   - 2-core size, off-core (dead-branch) share, number and length of 1-wide dead-end chains;
   - corridor widths;
   - portal pairs;
   - spawn and fountain shares;
   - start dragons;
   - side by side with the 20 existing maps and the generated families in `maps/generated/MANIFEST.md`.
5. **`maps/sprint/README.md`** (in Korean): for each map, which battle and game ids it came from, and the census row.

## Deliverables
- `tools/replay2map.js`
- `maps/sprint/*.map` and `maps/sprint/README.md`
- `exp/sprint-maps/validation.json`: per known map and replay, every field compared
- `exp/sprint-maps/census.json`
- `exp/sprint-maps/SUMMARY.txt`, written last (12 lines)

## Rules
- **Write scope:** `tools/replay2map.js`, `maps/sprint/**` and `exp/sprint-maps/**`. Do not commit.
- No network, no uploads, no games: the coordinator runs the smoke games afterwards.
- One worker process. This is a small job.
- **Target:** about 2 hours.
