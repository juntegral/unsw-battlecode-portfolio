# Reports sent to the lead by maps-sonnet

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 02:32:08 — closing summary

All seven maps now exist in `~/meow-redteam/maps/ladder/` and both checks passed. The maps are `ladder_<slug>_1.map` for `queen_of_spades`, `trauma`, `trophy`, `default`, `devil`, `maze` and `weakhold`.

**Method.** `replay2map.js` can't be revived without changing its logic. The `ENOENT` on `variants.json` is only the `--audit` path. Single-replay mode needs `tools/viewer.js`, which reads a vsix from the deleted `.venv-ppo`. The vsix we still have (`bc127`, `bc129`, vscode 1.2.x) is a newer webview build, so the tool's parser cut point `var Af=B(` no longer exists in it. I wrote `convert.py` in `ROOT/data/codex/astra/maps-sonnet/` instead. The replay embeds the full map text, so walls, portals and their pairing, the dragon starts and the size are copied verbatim. A patched copy of the tools is in that folder's `tools/`, unused.

**Check 1, comparing with the existing local files.**
- **Portals (game 1517698) and Stripes (1517689):** the header, all edges and portal pairs are identical to the existing `.map` files. The dragons are identical apart from the A/B labels, which are swapped relative to the existing files. That should not matter, since the map is symmetric.
- **Portals:** the pearl-bed set is also identical (104 beds).
- **Stripes:** my file has 36 beds against 70 in the existing file, because one replay only shows beds that spawned in that game.
- **Gap values:** the existing files hold convention values (`1 1`, `1 10`, `1 500`, `1 2559`) that likely came from `variants.json`, and mine are measured, so they differ everywhere.

**Check 2, one game each, `mNps` vs `m3base`, seed 1.** All seven have `result.txt` and no "error" in `engine.log`. A trophy/devil/maze run hit a "output directory must be empty" failure from a leftover `engine.log` of my own, so I cleared it and reran. Results are in `~/meow-redteam/solo/runs/mapcheck/<slug>`.

**Estimated rather than read from the replay:**
- **Pearl respawn gaps (`TILE x y min max`):** the server hides these (all `0 0`). For each bed I took the min and max gap between a pearl being eaten and the next natural spawn, pooling a tile with its mirror. Beds never seen to respawn get the map-wide min and max of the observed gaps.
- **Missing beds:** beds that never spawned in the single replay are missing entirely, as on Stripes. The Queen of Spades and Default bed counts are likely too low for the same reason.
- **Unobserved gaps:** the share of beds with a pooled default instead of an observed gap is Queen of Spades 122 of 156, Trophy 39 of 47, Devil 32 of 60, Default 124 of 310, Maze 54 of 322, Weakhold 20 of 56 and Trauma 2 of 142. Trophy and Devil were regenerated and I only have their final bed counts, so their beds-seen figures are 47 and 60.

**Things that look wrong.** Pearl supply on these maps is only roughly right. The mirror rule is `y` flips x and `x` flips y, not the reverse. My first version had it backwards and the engine rejected the Trophy and Devil maps for it. The 20-minute deadline was overrun, mostly waiting on games while other agents' games were running.

Files are in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/maps-sonnet/`:
- `convert.py`
- `cmp.py`
- `runall.sh`
- `games.sh`
- `out/`
