# The same scoreboard for local games of any build

`data/analysis/ladder/dossier/target/scoreboard.md` and `scoreboard.json` (yours, `work/tg_*.py`, built on the
fingerprint rates of `work/fp_*.py` and the per-game counter `dossier/count_dossier.py`) put our ladder bot (O)
beside the rank-1 team (R). I need the same rates for local games of my test builds, so that a change can be
judged by which lines of the scoreboard it moves.

Local replays: `~/meow-redteam/solo/runs/<arm>/<map>-seed<S>-side<K>/game.replay` (+ result.json);
`side<K>` is OUR side (the arm); the other side is a fixed local opponent. Reader for this format:
`data/analysis/ladder/dossier/local/replay_format.py` (yours). Layout names: `sqheld_*` are held-out generated maps;
`ladder_<slug>_1` are copies of ladder layouts (islands, australia, schooltime_1, schooltime_2, around_unsw,
portals, tower_defense, stripes, slithery_fight).

## Deliverable: `data/analysis/ladder/dossier/local/scoreboard.py`
`python3 scoreboard.py <arm> [<arm> ...] [--maps <substring>]` prints, for the games ALL the named arms played
(same map, seed and side), one line per behaviour rate and window, the same rates and windows as the table in
target/scoreboard.md and in the same order: the rank-1 value R (shared-layout column from scoreboard.json), our
ladder value O, then one column per arm (the arm's own side in its local games, pooled numerator over
denominator), and for each arm after the first the change against the first arm. Mark with `*` the lines where
an arm moved towards R by a tenth of the O-to-R gap or more, and with `!` where it moved away by as much.
Then three context lines per arm: games, wins, pearls eaten a game, dragons alive at r100/r300, longest at the end.
Keep the per-game rows cached in `local/scoreboard-rows.jsonl` (keyed by replay path, size and mtime) so a rerun
only counts new games; the cache must survive new arms and new games without a full recount.
The rate definitions must be the fingerprint ones, ported not reinvented; list at the end of the output any rate
you could not port to the local format.
Test it on `m2base m2all4` and on `m2base m2lg`, and write the first output to `local/scoreboard-first.txt`.
Write only under `data/analysis/ladder/dossier/local/`. No games, no network. Last step:
`data/analysis/ladder/dossier/local/scoreboard-done.txt` (one line).
