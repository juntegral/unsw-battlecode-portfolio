# Add the ram classes to the local counter

`data/analysis/ladder/dossier/local/count_local.py` (yours) counts local replays under
`~/meow-redteam/solo/runs/<arm>/<map>-seed<S>-side<K>/`. Add, per game and per side, without
changing existing fields (recount old rows once so the new fields exist everywhere), the classes that
`data/analysis/ladder/dossier/work/at_scan.py` and `at_more.py` define for ladder replays (read
`data/analysis/ladder/dossier/diag-attack.md`, "Terms" and section 2, for the words): for dragons of length 2 to 4
that are not the queen,
- chances and how many were taken, by target against own length (shorter; same to under twice; twice or more),
  by reach (free steps; paid), and by "outnumbered in view" yes or no;
- the "added" class of the card: the target shows at least twice the dragon's length in parts inside its 7 by 7
  view, is within sprint reach, and today's rule would refuse (outnumbered in view, or the round is past the feed
  round as at_scan reconstructs it): chances, taken;
- for every cross-team head-on a side starts on a head at least twice the mover's length: count, mover length,
  victim length, and the swing 15 rounds later (length the victim's side is down minus length the mover's side is
  down, drops eaten counted), summed per game; and whether the mover was its side's longest dragon or its queen;
- dragons alive at r200 and r300, longest at r300 and at the end (already there: keep the same names).
Port the definitions, do not reinvent; note differences at the end of table.md.
Also `data/analysis/ladder/dossier/local/rams.py <armA> <armB> [map-substring]`: for the games both arms played
(same map, seed, side) print games, wins, and for each arm the means of: added-class chances and take rate (pooled),
rams on a head twice the mover's length a game, their swing a meeting, all head-ons started a game, net length from
meetings, dragons alive at r300, longest at the end; plus paired differences of the last three. 20 lines or fewer.
Write only under `data/analysis/ladder/dossier/local/`. No games, no network. Last step:
`data/analysis/ladder/dossier/local/rams-done.txt` (one line).
