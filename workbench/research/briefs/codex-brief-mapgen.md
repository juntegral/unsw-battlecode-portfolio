# Codex brief: generate rule-valid unseen maps as a test bed for mechanism checks (W8)

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. Read first:
- `AGENTS.md`, especially §2 and §4 step 7: local games are mechanism checks, never win-rate verdicts.
- `docs/WORKQUEUE.md`, task W8.
- The map rules in `rules/ALL.md`:
  - "# Game Map", around line 188: size 10–64, symmetry, pearls and spawns, portal constraints around line 292;
  - "## unswbc maps", around line 694;
  - "# Map Files", around line 1298: the `.map` format with `MAP`, `MAP_NAME`, `SYMMETRY`, `TILE`, `EDGE` and `DRAGON`.
- The existing maps:
  - `maps/online-20260927/`: the 10 online maps;
  - `maps/bundled/`: 13 maps; `dilemma.map` is identical to Prisoners Dilemma;
  - `maps/server-b/`;
  - `maps/variants/`, with its README.

## Why
The qualifier is played on unseen maps. Our only unseen test maps are five bundled ones: arena, big_empty, Colosseum, default_small and stronghold. Every runtime rule we build risks being fitted to them, so we need a wider test bed of rule-valid maps with varied geometry.

The test bed is for **mechanism checks**:
- Does a runtime rule fire in the situations it was designed for?
- Does it produce the intended board state?
- Does anything break (errors, timeouts, misrecognition)?

It is **not** for win-rate evaluation. Do not produce win/loss tables.

stronghold shows what the organisers do. It is Trauma edited: the same size, symmetry and start dragons, with 684 of 1152 tiles equal. Maps like that are the hardest case for our map recognition (W2), so the test bed must include them.

## Steps
1. **Census of the existing maps.** Cover every directory above and mark duplicates. For each map, record:
   - width, height, area, aspect and `SYMMETRY`;
   - kelp-edge density, the corridor-width distribution, dead ends, 2-core size and pocket tiles (reuse `exp/pocket/` or `exp/general/`);
   - portal pairs;
   - spawn tiles: their share of all tiles, the gap distribution, and fountains (mean gap ≤ 12, as in our `isFountain`);
   - centre supply share and pocket supply share, as defined in `research/observations/general-principles.md`;
   - start dragons per team, their lengths, and the start distance between teams.

   The census sets the realistic envelope.
2. **Generator: `tools/mapgen/mapgen.js`.** Node, no dependencies, deterministic by seed.
   - Build one half (the fundamental domain) and complete it by the declared symmetry, so tiles (gaps), edges (kelp, portals) and start dragons are all symmetric.
   - Respect every format constraint: bounds, the edge-row layout, portal pairs with equal orientation, dragon segments adjacent and non-overlapping, length ≥ 2.
   - Keep the open tiles connected, so both teams can reach each other.
3. **Families: about 30–35 maps**, named `gen_<family>_<nn>` (in `MAP_NAME` too).
   - **S, small (10–20 per side), about 6:** open; light kelp; maze-like; central fountain cluster; edge fountains; crowded starts.
   - **M, medium (24–40), about 8:** rooms and corridors; pocket-rich (dead ends with fountains); 2–4 portal pairs; centre-heavy vs edge-heavy supply; long thin corridors.
   - **L, large (48–64), about 6:** open and sparse (like big_empty); maze-like; starts far apart; many start dragons; portals across the map.
   - **R, extreme aspect, 2:** for example 64×12 and 14×56.
   - **X, recognition traps:**
     - One per known online map layout: the same size, `SYMMETRY` and start dragons. Keep the area within about 6 tiles of each start identical and regenerate the rest, changing at least 40% of edges and spawn tiles.
     - Three more with the same size as a known map but different starts.

   Mark which maps are inside the census envelope and which are stress cases outside it.
4. **Validation.**
   - **Static:** `tools/mapgen/validate.js` re-parses every map and checks:
     - every format constraint;
     - the symmetry of tiles, edges and dragons;
     - connectivity.

     Run it on the existing maps too; they must pass.
   - **Engine smoke test:** one game per generated map with the official runner.
     - Launch games the same way `exp/v14/runq14.js` does (`tools/unswbc run <map> <botA> <botB> --sandbox --seed 1 ...`).
     - Use `versions/v1.6/bot` as A against `bots/proxy4_king` as B. For family X, also run with our bot on side B (proxy as A).
     - Record per game:
       - whether the map loaded and the game finished;
       - any error or timeout of our bot;
       - the maximum CPU per turn, if available;
       - which known map our bot recognised, if any, on each side. `exp/gen/genreport.js` shows how recognition and engine labels are read from replays.
     - No win/loss columns.
5. **Test-bed manifest.**
   - Write `maps/generated/MANIFEST.md` (in Korean) and `maps/generated/manifest.json`. For each map give:
     - its family, size and symmetry;
     - the census metrics;
     - what it exercises: small-map survival (W7), pockets and pocket harvest, portals, wide-map conversion (v1.6h), recognition traps (W2), or the runtime map model (W3).
   - Document how to run the queue tools (`exp/v14/runq14.js`, `tools/eval.js`) on `maps/generated/` without editing them. If a change would be needed, write a wrapper in `tools/mapgen/` instead.

## Deliverables
- `exp/mapgen/census.json`, written first.
- `tools/mapgen/mapgen.js`, `tools/mapgen/validate.js` and `tools/mapgen/README.md`.
- `maps/generated/*.map`, `maps/generated/MANIFEST.md` and `maps/generated/manifest.json`.
- `exp/mapgen/smoke.jsonl`.
- `research/observations/mapgen.md`, in Korean, containing:
  - the census table;
  - the generator design and the families;
  - the validation results, with game ids for any error, timeout or misrecognition of our bot;
  - the limitations.
- `exp/mapgen/SUMMARY.txt`, written last (12 lines).

## Rules
- **Write scope:** `tools/mapgen/**`, `maps/generated/**`, `exp/mapgen/**` and `research/observations/mapgen.md`.
  - Do not modify `tools/eval.js`, `exp/v14/**`, `versions/**` or `bots/**`.
  - Do not commit; the coordinator commits.
- Do not read the sources in `bots/`; run them only.
- No network and no uploads.
- **Local games are for the smoke test only:**
  - one game at a time;
  - start a game only while `pgrep -f "unswbc-clean.py run" | wc -l` is below 6 and at least 21 GB of disk is free;
  - run games with `nice -n 10`.
- At most 2 worker processes.
- **Targets:** the census, the generator and the first 10 validated maps by 16:30 KST; everything by 18:30 KST.
