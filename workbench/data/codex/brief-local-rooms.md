# Count room behaviour in local replays on the layouts with small portal rooms

Arms of our bot (base, pl, hp, plhp, and any other folder that has such games) play an opponent on
`ladder_stripes_1` and `ladder_portals_1`. Replays:
`~/meow-redteam/solo/runs/<arm>/ladder_<slug>-seed<S>-side<K>/game.replay` (+ result.json);
`side<K>` is OUR side. Games are still being played: count whatever exists, cheap to rerun.
Local replay parsing: reuse `data/analysis/ladder/dossier/local/replay_format.py` and `count_local.py` (yours).
Room geometry of Stripes: `data/analysis/ladder/dossier/local/maps3/stripes-rooms.json` and its README. For Portals
derive the rooms the same way (kelp-closed room under 48 tiles; "loop" = a portal edge inside the room that leads
out; "dead end" = its only portal edge is on its border).
Definitions to copy exactly from the ladder scripts in `data/analysis/ladder/dossier/work/`: `st_known.py`
(door chances and whether the step was taken), `st_rooms.py` (visits, pearls a visit, left alive, split with the
child outside), `st_open.py` (first round at a door, first step in), `st_pergame.py` (pearls by area). Port them
to the local format; say where you could not.

## Deliverable
`data/analysis/ladder/dossier/local/count_rooms.py` (no arguments), writing `rooms-rows.jsonl` and
`rooms-table.md` (70 lines or fewer) next to itself. Per layout, one row per arm (game means, ours / theirs):
1. games, won; pearls eaten by r50 and by r100; dragons and total length at r100 (or at the end if earlier).
2. loop rooms: door chances with a pearl on the entry tile and the far side already seen, for length 2 and for
   length 3: taken / chances; visits a game; share that left alive; pearls a visit; pearls eaten in loop rooms by r100.
3. dead-end rooms of 3 tiles: door chances with a pearl on the entry tile: taken / chances; visits a game; pearls
   a visit; visits that split a child with its head outside; net length a visit (pearls eaten minus length that
   died inside); pearls eaten in them by r100. Dead-end rooms of 1 tile: visits a game and net length.
4. first round one of ours steps into a room that holds a pearl (median over games; games with none by r60).
5. our deaths inside rooms by cause.
Then, paired against base (same layout, seed, side): for each other arm the number of pairs whose game differs at
all, and the mean paired difference of pearls by r100, dragons at r100, loop-room visits, dead-end 3-tile visits,
and wins.
Write only under `data/analysis/ladder/dossier/local/`. No games, no network, no posts. Last step:
`data/analysis/ladder/dossier/local/rooms-done.txt` (one line).
