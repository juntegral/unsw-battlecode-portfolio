# Add the "stands on a tile that is about to spawn" counts to the local tools

`data/analysis/ladder/dossier/diag-spawn.md` (read sections 2, 4 and "Expected signal") measures on ladder replays,
with `dossier/work/sp_tick.py` and `sp_tickagg.py`, how often a dragon steps onto an empty tile just before it
would spawn a pearl, which stops the pearl. I need the same counts on local replays of my test builds:
`~/meow-redteam/solo/runs/<arm>/<map>-seed<S>-side<K>/game.replay` (`side<K>` is our side; reader
`data/analysis/ladder/dossier/local/replay_format.py`). Local maps carry their true spawn intervals in the `.map`
files under `~/meow-redteam/maps/` (TILE min max), and the engine semantics are in
`data/analysis/ladder/dossier/local/maps2/semantics.json`; unlike the ladder you may be able to read the real
countdown of every tile from the replay or reconstruct it exactly. Use the exact countdown where the local replay
gives it; otherwise port the mirror-tile method. Say which you used.

## Deliverable: `data/analysis/ladder/dossier/local/spawn.py <armA> <armB> [--maps <substring>]`
For the games both arms played (same map, seed, side), per arm, our side (and the opponent's side as context):
1. head beside an empty tile whose countdown is 1: cases, and the share where the dragon steps onto that tile;
   the same at countdown 2;
2. spawn attempts that failed because a body of the side lay on the tile: a game; split into "the head stepped
   onto the empty tile within the last L rounds" and "a body segment behind it"; per 100 pearls born;
3. from 2 steps away with 2 rounds to go: share where the pearl is born;
4. natural pearls born a game, natural pearls the side eats a game (rounds 0-100, 101-300, whole game), share of
   births eaten in the birth round, wait from birth to eating;
5. context: wins, dragons alive at r100 and r300, our deaths by wall, own body and another body per 1,000 dragon
   turns (rounds 0-300), longest at the end.
Then paired differences armB minus armA for the lines of 1 to 5. 30 lines of output or fewer. Cache per-game rows
in `local/spawn-rows.jsonl` (keyed by replay path, size, mtime) so reruns only count new games.
Test on `m2base m2all4` now (both exist) and write that output to `local/spawn-first.txt`.
Write only under `data/analysis/ladder/dossier/local/`. No games, no network. Last step:
`data/analysis/ladder/dossier/local/spawn-done.txt` (one line).
