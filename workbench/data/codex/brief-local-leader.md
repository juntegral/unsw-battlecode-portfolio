# Add leader-death counts to the local counter

`data/analysis/ladder/dossier/local/count_local.py` (yours) counts local replays under
`~/meow-redteam/solo/runs/<arm>/<map>-seed<S>-side<K>/`. Add, per game and per side, without
changing any existing field (rows are cached by signature: make sure old rows are recounted once so the new fields
exist everywhere):
- `leader_deaths_301_499`: deaths in rounds 301-499 of a dragon that was its side's longest at the start of that
  turn and at least 15 long; `leader_deaths_rammed_301_499`: those where an enemy head moved into its head;
  `leader_death_rounds` and `leader_death_lengths` (lists); `leader_death_allies5`: for each, the number of own
  heads within 5 tiles (wrap-aware Manhattan) at that moment.
- `longest_r450`; `longest_peak_301_499` (the largest length any dragon of the side had in rounds 301-499) and
  `longest_kept_share` = longest at the end / that peak.
- `leader_pearls_301_499`: pearls eaten in rounds 301-499 by whichever dragon was the side's longest at the start
  of each of its turns.
- `leader_turns_enemy3_301_499`: turns in 301-499 of the side's longest dragon (15 or more) that start with an
  enemy head of 9 or less within 3 tiles; and how many of those turns it moved more than one tile.
Definitions follow `data/analysis/ladder/dossier/work/fd_ram.py` and `fd_esc.py` (ladder versions); port, do not
reinvent, and note any difference at the end of table.md.
Also add a small script `data/analysis/ladder/dossier/local/leader.py <armA> <armB> [map-substring]` that prints,
for the games both arms played (same map, seed, side): games, wins, and the means of the new fields for each arm,
plus the paired difference of longest at the end and of wins. 20 lines of output or fewer.
Write only under `data/analysis/ladder/dossier/local/`. No games, no network. Last step: write
`data/analysis/ladder/dossier/local/leader-done.txt` (one line).
